import os
from schema import Schema, And, Or, Use, Optional
from werewolf_python import *


class WerewolfModeler:
    def __init__(self, gams_sysdir, scn, data_dir):
        if os.path.isabs(gams_sysdir) == False:
            raise Exception(
                "must enter in full (absolute) path to GAMS sysdir directory"
            )

        if os.path.isabs(data_dir) == False:
            raise Exception(
                "must enter in full (absolute) path to 'data_dir' directory"
            )

        self.data = scn
        self.data_dir = data_dir

        # data schema
        schema = Schema(
            {
                "solve_seq": Or(Schema([str]), str),
                Optional("mode"): str,
                Optional("x_axis_title"): str,
                Optional("proj_year", default=2020): int,
                Optional("ev_factor", default=0): Or(int, float),
                Optional("almostsure", default=0): int,
                Optional("wind_scn", default=10): int,
                Optional("solar_scn", default=1): int,
                Optional("hydro_scn", default=1): int,
                Optional("frac", default=0): Schema([int, float]),
            }
        )

        for major_scenario in self.data.keys():
            if schema.is_valid(self.data[major_scenario]) == False:
                raise Exception(
                    f"input data for scenario '{major_scenario}' does not follow schema"
                )
            else:
                self.data[major_scenario] = schema.validate(self.data[major_scenario])

        #
        #
        # directory management
        self.gams_sysdir = gams_sysdir

        # create output directory if necessary
        if os.path.isdir(os.path.join(os.getcwd(), "output")) == False:
            os.mkdir(os.path.join(os.getcwd(), "output"))

        # scenario directory
        for major_scenario in self.data.keys():
            if (
                os.path.isdir(os.path.join(os.getcwd(), "output", major_scenario))
                == False
            ):
                os.mkdir(os.path.join(os.getcwd(), "output", major_scenario))

            if (
                os.path.isdir(
                    os.path.join(os.getcwd(), "output", major_scenario, "data_repo")
                )
                == False
            ):
                os.mkdir(
                    os.path.join(os.getcwd(), "output", major_scenario, "data_repo")
                )

            if (
                os.path.isdir(
                    os.path.join(os.getcwd(), "output", major_scenario, "ldc_curves")
                )
                == False
            ):
                os.mkdir(
                    os.path.join(os.getcwd(), "output", major_scenario, "ldc_curves")
                )

            if (
                os.path.isdir(
                    os.path.join(os.getcwd(), "output", major_scenario, "summary_maps")
                )
                == False
            ):
                os.mkdir(
                    os.path.join(os.getcwd(), "output", major_scenario, "summary_maps")
                )

            if (
                os.path.isdir(
                    os.path.join(os.getcwd(), "output", major_scenario, "summary_plots")
                )
                == False
            ):
                os.mkdir(
                    os.path.join(os.getcwd(), "output", major_scenario, "summary_plots")
                )

            if (
                os.path.isdir(
                    os.path.join(os.getcwd(), "output", major_scenario, "lst")
                )
                == False
            ):
                os.mkdir(os.path.join(os.getcwd(), "output", major_scenario, "lst"))

        self.sequences = {
            "all": [
                self.run_werewolf_1,
                self.run_create_network,
                self.run_create_ldcs,
                self.run_werewolf_2,
                self.run_werewolf_3,
                self.run_make_geojson,
                self.run_map_model_network,
                self.run_map_built_capacity,
                self.run_map_built_capacity_cntlreg,
                self.run_map_generation,
                self.run_map_generation_cntlreg,
                self.run_map_total_capacity,
                self.run_plot_carbon_emissions,
                self.run_plot_generation,
                self.run_plot_capacity,
                self.run_plot_transmission_exim,
                self.run_plot_costs,
            ],
            "run_1_2": [
                self.run_werewolf_1,
                self.run_create_network,
                self.run_create_ldcs,
                self.run_werewolf_2,
            ],
            "run_123": [
                self.run_werewolf_1,
                self.run_create_network,
                self.run_create_ldcs,
                self.run_werewolf_2,
                self.run_werewolf_3,
            ],
            "run_1": self.run_werewolf_1,
            "run_2": self.run_werewolf_2,
            "run_3": [
                self.run_werewolf_3,
                # self.run_make_geojson,
                # self.run_map_model_network,
                # self.run_map_built_capacity,
                # self.run_map_built_capacity_cntlreg,
                # self.run_map_generation,
                # self.run_map_generation_cntlreg,
                # self.run_map_total_capacity,
                # self.run_plot_carbon_emissions,
                # self.run_plot_generation,
                # self.run_plot_capacity,
                # self.run_plot_transmission_exim,
                # self.run_plot_costs,
            ],
            "all_maps": [
                self.run_make_geojson,
                self.run_map_model_network,
                self.run_map_built_capacity,
                self.run_map_built_capacity_cntlreg,
                self.run_map_generation,
                self.run_map_generation_cntlreg,
                self.run_map_total_capacity,
            ],
            "all_plots": [
                self.run_plot_carbon_emissions,
                self.run_plot_generation,
                self.run_plot_capacity,
                self.run_plot_transmission_exim,
                self.run_plot_costs,
            ],
            "map_network": self.run_map_model_network,
            "map_built": self.run_map_built_capacity,
            "map_built_cntlreg": self.run_map_built_capacity_cntlreg,
            "map_gen": self.run_map_generation,
            "map_gen_cntlreg": self.run_map_generation_cntlreg,
            "map_total_cap": self.run_map_total_capacity,
        }

        self.mode_flags = {
            "carbon_reduction": {
                ("2020_baseline", "co2redn"): 0,
                ("2020_baseline", "capredn"): 0,
                ("2020_baseline", "nrenergyredn"): 0,
                ("2020_baseline", "carbonleakage"): 1,
                ("proj_year_baseline", "co2redn"): 1,
                ("proj_year_baseline", "capredn"): 0,
                ("proj_year_baseline", "nrenergyredn"): 0,
                ("proj_year_baseline", "carbonleakage"): 1,
                ("proj_year_scn", "co2redn"): 1,
                ("proj_year_scn", "capredn"): 0,
                ("proj_year_scn", "nrenergyredn"): 0,
                ("proj_year_scn", "carbonleakage"): 1,
            },
            "capacity_reduction": {
                ("2020_baseline", "co2redn"): 0,
                ("2020_baseline", "capredn"): 0,
                ("2020_baseline", "nrenergyredn"): 0,
                ("2020_baseline", "carbonleakage"): 1,
                ("proj_year_baseline", "co2redn"): 0,
                ("proj_year_baseline", "capredn"): 1,
                ("proj_year_baseline", "nrenergyredn"): 0,
                ("proj_year_baseline", "carbonleakage"): 1,
                ("proj_year_scn", "co2redn"): 0,
                ("proj_year_scn", "capredn"): 1,
                ("proj_year_scn", "nrenergyredn"): 0,
                ("proj_year_scn", "carbonleakage"): 0,
            },
            "limit_nonrenw": {
                ("2020_baseline", "co2redn"): 0,
                ("2020_baseline", "capredn"): 0,
                ("2020_baseline", "nrenergyredn"): 0,
                ("2020_baseline", "carbonleakage"): 1,
                ("proj_year_baseline", "co2redn"): 0,
                ("proj_year_baseline", "capredn"): 0,
                ("proj_year_baseline", "nrenergyredn"): 1,
                ("proj_year_baseline", "carbonleakage"): 1,
                ("proj_year_scn", "co2redn"): 0,
                ("proj_year_scn", "capredn"): 0,
                ("proj_year_scn", "nrenergyredn"): 1,
                ("proj_year_scn", "carbonleakage"): 0,
            },
            "no_policy": {
                ("2020_baseline", "co2redn"): 0,
                ("2020_baseline", "capredn"): 0,
                ("2020_baseline", "nrenergyredn"): 0,
                ("2020_baseline", "carbonleakage"): 1,
                ("proj_year_baseline", "co2redn"): 0,
                ("proj_year_baseline", "capredn"): 0,
                ("proj_year_baseline", "nrenergyredn"): 1,
                ("proj_year_baseline", "carbonleakage"): 1,
                ("proj_year_scn", "co2redn"): 0,
                ("proj_year_scn", "capredn"): 0,
                ("proj_year_scn", "nrenergyredn"): 0,
                ("proj_year_scn", "carbonleakage"): 1,
            },
        }

    def run_werewolf_1(self, major_scenario):
        print(f"RUNNING... werewolf_1_aggr.gms")
        rc = os.system(
            f"gams werewolf_1_aggr.gms r=disaggregated_data o={os.path.join(os.getcwd(),'output',major_scenario,'lst','werewolf_1_aggr.lst')} --ev_factor {self.data[major_scenario]['ev_factor']} --proj_year {self.data[major_scenario]['proj_year']} --output_gdx {os.path.join(os.getcwd(),'output',major_scenario,'data_repo','processed_werewolf_data.gdx')}"
        )
        if rc != 0:
            raise Exception("werewolf_1_aggr.gms did not finish correctly...")

    def run_werewolf_2(self, major_scenario):
        print(f"RUNNING... werewolf_2_declare.gms")
        rc = os.system(
            f"gams werewolf_2_declare.gms s=vre_models o={os.path.join(os.getcwd(),'output',major_scenario,'lst','werewolf_2_declare.lst')} --network_arcs {os.path.join(os.getcwd(),'output',major_scenario,'data_repo','network_arcs.gdx')} --ldc_fit {os.path.join(os.getcwd(),'output',major_scenario,'data_repo','ldc_fit.gdx')} --werewolf_data {os.path.join(os.getcwd(),'werewolf_data.gdx')} --processed_data {os.path.join(os.getcwd(),'output',major_scenario,'data_repo','processed_werewolf_data.gdx')} --almostsure {self.data[major_scenario]['almostsure']} --wind_scn {self.data[major_scenario]['wind_scn']} --solar_scn {self.data[major_scenario]['solar_scn']} --hydro_scn {self.data[major_scenario]['hydro_scn']}"
        )
        if rc != 0:
            raise Exception("werewolf_2_declare.gms did not finish correctly...")

    def run_werewolf_3(self, major_scenario):
        if self.data[major_scenario]["mode"] == "baseline_growth":
            demand_model = 1
            policy_model = 0
        else:
            demand_model = 0
            policy_model = 1

        data = {
            "r": {
                "type": "set",
                "elements": list(range(0, len(self.data[major_scenario]["frac"]))),
                "text": "scenario iteration",
            },
            "frac_r": {
                "type": "parameter",
                "domain": ["r"],
                "elements": {
                    str(n): i for n, i in enumerate(self.data[major_scenario]["frac"])
                },
            },
        }

        gdx = gmsxfr.GdxContainer(self.gams_sysdir)
        gdx.deep_validate(data)
        gdx.add_to_gdx(data, standardize_data=True, inplace=True, quality_checks=False)

        gdx.write_gdx(
            os.path.join(
                os.getcwd(), "output", major_scenario, "data_repo", "frac_gdx.gdx"
            ),
            compress=False,
        )

        print(f"RUNNING... werewolf_3_model.gms")
        rc = os.system(
            f"gams werewolf_3_model.gms r=vre_models --policy_model {policy_model} --demand_model {demand_model} o={os.path.join(os.getcwd(),'output',major_scenario,'lst','werewolf_3_model.lst')} --processed_data {os.path.join(os.getcwd(),'output',major_scenario,'data_repo','processed_werewolf_data.gdx')} --solve_mode {os.path.join(os.getcwd(),'output',major_scenario,'data_repo','solve_mode.gdx')} --final_results {os.path.join(os.getcwd(),'output',major_scenario,'data_repo','final_results.gdx')} --frac_gdx  {os.path.join(os.getcwd(),'output',major_scenario,'data_repo','frac_gdx.gdx')}"
        )
        if rc != 0:
            raise Exception("werewolf_3_model.gms did not finish correctly...")

    def run_create_network(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','create_network.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','create_network.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')}"
        )
        if rc != 0:
            raise Exception("create_network.py did not finish correctly...")

    def run_create_ldcs(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','create_ldcs.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','create_ldcs.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --ldc_curves {os.path.join(os.getcwd(),'output',major_scenario,'ldc_curves')}"
        )
        if rc != 0:
            raise Exception("create_ldcs.py did not finish correctly...")

    def run_make_geojson(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','make_geojson.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','make_geojson.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --data_dir {os.path.join(self.data_dir,'raw_data')}"
        )
        if rc != 0:
            raise Exception("make_geojson.py did not finish correctly...")

    def run_map_model_network(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','map_model_network.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','map_model_network.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --data_dir {os.path.join(self.data_dir,'raw_data')} --output {os.path.join(os.getcwd(),'output',major_scenario,'summary_maps')}"
        )
        if rc != 0:
            raise Exception("map_model_network.py did not finish correctly...")

    # "map_total_cap": self.run_map_total_capacity,

    def run_map_built_capacity_cntlreg(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','map_built_capacity_cntlreg.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','map_built_capacity_cntlreg.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --output {os.path.join(os.getcwd(),'output',major_scenario,'summary_maps')}"
        )
        if rc != 0:
            raise Exception("map_built_capacity_cntlreg.py did not finish correctly...")

    def run_map_built_capacity(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','map_built_capacity.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','map_built_capacity.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --output {os.path.join(os.getcwd(),'output',major_scenario,'summary_maps')}"
        )
        if rc != 0:
            raise Exception("map_built_capacity.py did not finish correctly...")

    def run_map_generation_cntlreg(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','map_generation_cntlreg.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','map_generation_cntlreg.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --output {os.path.join(os.getcwd(),'output',major_scenario,'summary_maps')}"
        )
        if rc != 0:
            raise Exception("map_generation_cntlreg.py did not finish correctly...")

    def run_map_generation(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','map_generation.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','map_generation.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --output {os.path.join(os.getcwd(),'output',major_scenario,'summary_maps')}"
        )
        if rc != 0:
            raise Exception("map_generation.py did not finish correctly...")

    def run_map_total_capacity(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','map_total_capacity.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','map_total_capacity.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --output {os.path.join(os.getcwd(),'output',major_scenario,'summary_maps')}"
        )
        if rc != 0:
            raise Exception("map_total_capacity.py did not finish correctly...")

    def run_plot_carbon_emissions(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','plot_carbon_emissions.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','plot_carbon_emissions.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --output {os.path.join(os.getcwd(),'output',major_scenario,'summary_plots')}"
        )
        if rc != 0:
            raise Exception("plot_carbon_emissions.py did not finish correctly...")

    def run_plot_generation(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','plot_generation.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','plot_generation.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --output {os.path.join(os.getcwd(),'output',major_scenario,'summary_plots')}"
        )
        if rc != 0:
            raise Exception("plot_generation.py did not finish correctly...")

    def run_plot_capacity(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','plot_capacity.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','plot_capacity.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --output {os.path.join(os.getcwd(),'output',major_scenario,'summary_plots')}"
        )
        if rc != 0:
            raise Exception("plot_capacity.py did not finish correctly...")

    def run_plot_transmission_exim(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','plot_transmission_exim.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','plot_transmission_exim.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --output {os.path.join(os.getcwd(),'output',major_scenario,'summary_plots')}"
        )
        if rc != 0:
            raise Exception("plot_transmission_exim.py did not finish correctly...")

    def run_plot_costs(self, major_scenario):
        print(
            f"RUNNING... {os.path.join(os.getcwd(),'werewolf_python','plot_costs.py')}"
        )
        rc = os.system(
            f"python {os.path.join(os.getcwd(),'werewolf_python','plot_costs.py')} --gams_sysdir {self.gams_sysdir} --data_repo {os.path.join(os.getcwd(),'output',major_scenario,'data_repo')} --output {os.path.join(os.getcwd(),'output',major_scenario,'summary_plots')}"
        )
        if rc != 0:
            raise Exception("plot_costs.py did not finish correctly...")

    def run_sequence(self):
        for major_scenario in scn.keys():

            # if "mode" in self.data[major_scenario].keys():
            data = {
                "mode": {
                    "type": "parameter",
                    "elements": self.mode_flags[self.data[major_scenario]["mode"]],
                },
                "x_title": {
                    "type": "set",
                    "elements": 1,
                    "text": self.data[major_scenario]["x_axis_title"],
                },
            }

            gdx = gmsxfr.GdxContainer(self.gams_sysdir)
            gdx.deep_validate(data)
            gdx.add_to_gdx(
                data, standardize_data=True, inplace=True, quality_checks=False
            )

            gdx.write_gdx(
                os.path.join(
                    os.getcwd(),
                    "output",
                    major_scenario,
                    "data_repo",
                    "solve_mode.gdx",
                ),
                compress=False,
            )

            if isinstance(self.data[major_scenario]["solve_seq"], str):
                self.data[major_scenario]["solve_seq"] = [
                    self.data[major_scenario]["solve_seq"]
                ]

            for i in self.data[major_scenario]["solve_seq"]:
                if callable(self.sequences[i]):
                    self.sequences[i](major_scenario)
                else:
                    for j in self.sequences[i]:
                        j(major_scenario)


if __name__ == "__main__":

    # schema = Schema(
    #     {
    #         "solve_seq": Or(Schema([str]), str),
    #         Optional("mode"): str,
    #         Optional("x_axis_title"): str,
    #         Optional("proj_year", default=2030): int,
    #         Optional("ev_factor", default=0): Or(int, float),
    #         Optional("almostsure", default=0): int,
    #         Optional("wind_scn", default=10): int,
    #         Optional("solar_scn", default=1): int,
    #         Optional("hydro_scn", default=1): int,
    #         Optional("frac", default=0): Schema([int, float]),
    #     }
    # )

    scn = {
        # "scenario_label_1": {
        #     "solve_seq": "run_1_2",
        #     "proj_year": 2020,
        #     "mode": "carbon_reduction",
        #     "frac": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
        #     "x_axis_title": "Carbon Reduction (% from baseline)",
        # },
        "scenario_label_1": {
            "solve_seq": "run_123",
            "proj_year": 2020,
            "mode": "carbon_reduction",
            "frac": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            "x_axis_title": "Carbon Reduction (% from baseline)",
        },
        # "baseline_scenario": {
        #     "solve_seq": "all",
        #     "mode": "baseline_growth",
        #     "frac": list(range(2020, 2031)),
        #     "x_axis_title": "Year",
        # },
    }

    ww = WerewolfModeler(
        gams_sysdir="/Applications/GAMS30.3/Resources/sysdir",
        data_dir="/Users/adam/Projects/werewolf/gams/werewolf/data/epa_needs_093019",
        scn=scn,
    )

    ww.run_sequence()
