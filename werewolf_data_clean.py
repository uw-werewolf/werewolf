import os
import pandas as pd
import werewolf_data as wd

if __name__ == "__main__":

    # Load Data
    data_dir = os.path.join(os.getcwd(), "data", "wi_psc", "raw_data")
    w1 = wd.WerewolfLoader(data_dir=data_dir, version="wi_psc")

    # # create notation (no cnty notation right now, first clean things up)
    # wdl.add_notation["state.abbv"] = set(wdl.data.reeds_regions["state.abbv"])
    # wdl.add_notation["state.fullname"] = set(wdl.data.reeds_regions["state.fullname"])
    # wdl.add_notation["fips.full"] = set(wdl.data.reeds_regions["fips.full"])
    # wdl.add_notation["fips.cnty"] = set(wdl.data.reeds_regions["fips.cnty"])
    # wdl.add_notation["fips.state"] = set(wdl.data.reeds_regions["fips.state"])
    # wdl.add_notation["region.reeds.reg"] = set(
    #     wdl.data.reeds_regions["region.reeds.reg"]
    # )
    # wdl.add_notation["region.reeds.ba"] = set(wdl.data.reeds_regions["region.reeds.ba"])
    # wdl.add_notation["unique_id_final"] = set(wdl.data.epa_needs["unique_id_final"])
    # wdl.add_notation["plant_type"] = set(wdl.data.epa_needs["plant_type"])
    # wdl.add_notation["hour"] = set(wdl.data.ldc["hour"])
    # wdl.add_notation["region.epa.ipm"] = set(wdl.data.epa_needs["region.epa.ipm"]) - {
    #     "CN_AB",
    #     "CN_NF",
    #     "CN_PQ",
    #     "CN_NL",
    #     "CN_NB",
    #     "CN_SK",
    #     "CN_BC",
    #     "CN_MB",
    #     "CN_NS",
    #     "CN_PE",
    #     "CN_ON",
    # }
    # wdl.test_notation()
    #
    # # clean up
    # wdl.bulk_replace(
    #     {
    #         "NY_Z_G-I": "NY_Z_G_I",
    #         "Solar": "Solar_PV",
    #         "Wind": "Onshore_Wind",
    #         "Combined Cycle": "Combined_Cycle",
    #     }
    # )
    # wdl.test_notation()
    # wdl.bulk_drop_rows()
    #
    # #
    # #
    # # now to deal with county names
    #
    # # map state.fullname to state.abbv
    # state_fullname_2_state_abbv = dict(
    #     zip(
    #         wdl.data.reeds_regions["state.fullname"],
    #         wdl.data.reeds_regions["state.abbv"],
    #     )
    # )
    #
    # wdl.bulk_map_column(
    #     from_col="state.fullname",
    #     to_col="state.abbv",
    #     mapping=state_fullname_2_state_abbv,
    # )
    #
    # wdl.test_notation()
    #
    # # join columns to match counties
    # # add cnty.fullname_state.abbv columns
    # wdl.data.reeds_regions["cnty.fullname_state.abbv"] = (
    #     wdl.data.reeds_regions["cnty.fullname"]
    #     + " County, "
    #     + wdl.data.reeds_regions["state.abbv"]
    # )
    #
    # wdl.data.epa_ipm_to_fips["cnty.fullname_state.abbv"] = (
    #     wdl.data.epa_ipm_to_fips["cnty.fullname"]
    #     + " County, "
    #     + wdl.data.epa_ipm_to_fips["state.abbv"]
    # )
    #
    # # create new notation
    # wdl.add_notation["cnty.fullname_state.abbv"] = set(
    #     wdl.data.reeds_regions["cnty.fullname_state.abbv"]
    # )
    #
    # wdl.test_notation()
    #
    # # clean up county names
    # wdl.data.epa_ipm_to_fips.replace(
    #     {
    #         "Alexandria City County, VA": "Alexandria County, VA",
    #         "Bristol City County, VA": "Bristol County, VA",
    #         "Chesapeake City County, VA": "Chesapeake County, VA",
    #         "Covington City County, VA": "Covington County, VA",
    #         "Danville City County, VA": "Danville County, VA",
    #         "DeSoto County, LA": "De Soto County, LA",
    #         "DeWitt County, IL": "De Witt County, IL",
    #         "Hampton City County, VA": "Hampton County, VA",
    #         "Hopewell City County, VA": "Hopewell County, VA",
    #         "LaSalle County, IL": "La Salle County, IL",
    #         "Lynchburg City County, VA": "Lynchburg County, VA",
    #         "Manassas City County, VA": "Manassas County, VA",
    #         "Miami Dade County, FL": "Miami-Dade County, FL",
    #         "Portsmouth City County, VA": "Portsmouth County, VA",
    #         "Prince Georges County, MD": "Prince George's County, MD",
    #         "Queen Annes County, MD": "Queen Anne's County, MD",
    #         "Salem City County, VA": "Salem County, VA",
    #         "St Bernard County, LA": "St. Bernard County, LA",
    #         "St Charles County, LA": "St. Charles County, LA",
    #         "St Charles County, MO": "St. Charles County, MO",
    #         "St Clair County, IL": "St. Clair County, IL",
    #         "St Clair County, MI": "St. Clair County, MI",
    #         "St Croix County, WI": "St. Croix County, WI",
    #         "St Francois County, MO": "St. Francois County, MO",
    #         "St James County, LA": "St. James County, LA",
    #         "St Joseph County, IN": "St. Joseph County, IN",
    #         "St Joseph County, MI": "St. Joseph County, MI",
    #         "St Lawrence County, NY": "St. Lawrence County, NY",
    #         "St Louis City County, MO": "St. Louis City County, MO",
    #         "St Louis County, MN": "St. Louis County, MN",
    #         "St Louis County, MO": "St. Louis County, MO",
    #         "St Lucie County, FL": "St. Lucie County, FL",
    #         "St Mary County, LA": "St. Mary County, LA",
    #         "Suffolk City County, VA": "Suffolk County, VA",
    #         "Virginia Beach City County, VA": "Virginia Beach County, VA",
    #     },
    #     inplace=True,
    # )
    #
    # wdl.test_notation()
    #
    # # merge colums for miso data
    # wdl.data.miso_gen["cnty.fullname_state.abbv"] = (
    #     wdl.data.miso_gen["cnty.fullname"] + ", " + wdl.data.miso_gen["state.abbv"]
    # )
    #
    # wdl.test_notation()
    #
    # wdl.data.miso_gen.replace(
    #     {
    #         "Grant County,Iowa County, WI": "Grant County, WI",
    #         "Greene County,Scott County, IL": "Greene County, IL",
    #         "Morgan County,Scott County, IL": "Morgan County, IL",
    #         "Morgan County,Sangamon County, IL": "Morgan County, IL",
    #         "Humboldt County,Kossuth County, IA": "Humboldt County, IA",
    #     },
    #     inplace=True,
    # )
    #
    # # 1. map state.fullname to state.abbv
    # cnty_fullname_state_abbv_2_fips_full = dict(
    #     zip(
    #         wdl.data.reeds_regions["cnty.fullname_state.abbv"],
    #         wdl.data.reeds_regions["fips.full"],
    #     )
    # )
    #
    # wdl.bulk_map_column(
    #     from_col="cnty.fullname_state.abbv",
    #     to_col="fips.full",
    #     mapping=cnty_fullname_state_abbv_2_fips_full,
    # )
    #
    # # to avoid confustion, get rid of all cnty.fullname columns
    # wdl.bulk_drop_columns(["cnty.fullname"])
    # wdl.test_notation()
    #
    # wdl.to_csv(output_dir=os.path.join(os.getcwd(), "standard_data"))
    #
    # #
    # #
    # #
    # # now we have to generate the GDX file
    # k = set()
    # k.update(wdl.data.epa_needs["plant_type"])
    # k.update(["Energy_Storage_slow", "Energy_Storage_med", "Energy_Storage_fast"])
    # k.update(wdl.data.reeds_wind_cap["tech.label"])
    # k.update(wdl.data.reeds_solar_cap["tech.label"])
    #
    # gen = set()
    # gen.update(wdl.data.epa_needs["plant_type"])
    # gen.remove("Energy_Storage")
    # gen.update(wdl.data.reeds_wind_cap["tech.label"])
    # gen.update(wdl.data.reeds_solar_cap["tech.label"])
    #
    # fossil = {
    #     "Coal_Steam",
    #     "Combined_Cycle",
    #     "Combustion_Turbine",
    #     "Fossil_Waste",
    #     "IGCC",
    #     "Landfill_Gas",
    #     "Municipal_Solid_Waste",
    #     "Non_Fossil_Waste",
    #     "OG_Steam",
    #     "Tires",
    # }
    #
    # hydro = {"Hydro", "Pumped_Storage"}
    #
    # geothermal = {"Geothermal"}
    #
    # nuclear = {"Nuclear"}
    #
    # store = {
    #     "Energy_Storage_fast",
    #     "Energy_Storage_med",
    #     "Energy_Storage_slow",
    #     "Pumped_Storage",
    # }
    #
    # energy_storage = {
    #     "Energy_Storage_fast",
    #     "Energy_Storage_med",
    #     "Energy_Storage_slow",
    # }
    #
    # renew = {
    #     "Energy_Storage_fast",
    #     "Energy_Storage_med",
    #     "Energy_Storage_slow",
    #     "Fuel_Cell",
    #     "Hydro",
    #     "Offshore_Wind",
    #     "Offshore_Wind_1",
    #     "Offshore_Wind_10",
    #     "Offshore_Wind_11",
    #     "Offshore_Wind_12",
    #     "Offshore_Wind_13",
    #     "Offshore_Wind_14",
    #     "Offshore_Wind_15",
    #     "Offshore_Wind_2",
    #     "Offshore_Wind_3",
    #     "Offshore_Wind_4",
    #     "Offshore_Wind_5",
    #     "Offshore_Wind_6",
    #     "Offshore_Wind_7",
    #     "Offshore_Wind_8",
    #     "Offshore_Wind_9",
    #     "Onshore_Wind",
    #     "Onshore_Wind_1",
    #     "Onshore_Wind_10",
    #     "Onshore_Wind_2",
    #     "Onshore_Wind_3",
    #     "Onshore_Wind_4",
    #     "Onshore_Wind_5",
    #     "Onshore_Wind_6",
    #     "Onshore_Wind_7",
    #     "Onshore_Wind_8",
    #     "Onshore_Wind_9",
    #     "Pumped_Storage",
    #     "SolarDistUtil_PV_1",
    #     "SolarDistUtil_PV_2",
    #     "SolarDistUtil_PV_3",
    #     "SolarDistUtil_PV_4",
    #     "SolarDistUtil_PV_5",
    #     "SolarDistUtil_PV_6",
    #     "SolarDistUtil_PV_7",
    #     "SolarUtil_PV_1",
    #     "SolarUtil_PV_2",
    #     "SolarUtil_PV_3",
    #     "SolarUtil_PV_4",
    #     "SolarUtil_PV_5",
    #     "SolarUtil_PV_6",
    #     "SolarUtil_PV_7",
    #     "Solar_PV",
    #     "Solar_Thermal",
    # }
    #
    # all_solar = {
    #     "SolarDistUtil_PV_1",
    #     "SolarDistUtil_PV_2",
    #     "SolarDistUtil_PV_3",
    #     "SolarDistUtil_PV_4",
    #     "SolarDistUtil_PV_5",
    #     "SolarDistUtil_PV_6",
    #     "SolarDistUtil_PV_7",
    #     "SolarUtil_PV_1",
    #     "SolarUtil_PV_2",
    #     "SolarUtil_PV_3",
    #     "SolarUtil_PV_4",
    #     "SolarUtil_PV_5",
    #     "SolarUtil_PV_6",
    #     "SolarUtil_PV_7",
    #     "Solar_PV",
    #     "Solar_Thermal",
    # }
    #
    # all_solar_PV = {
    #     "SolarDistUtil_PV_1",
    #     "SolarDistUtil_PV_2",
    #     "SolarDistUtil_PV_3",
    #     "SolarDistUtil_PV_4",
    #     "SolarDistUtil_PV_5",
    #     "SolarDistUtil_PV_6",
    #     "SolarDistUtil_PV_7",
    #     "SolarUtil_PV_1",
    #     "SolarUtil_PV_2",
    #     "SolarUtil_PV_3",
    #     "SolarUtil_PV_4",
    #     "SolarUtil_PV_5",
    #     "SolarUtil_PV_6",
    #     "SolarUtil_PV_7",
    #     "Solar_PV",
    # }
    #
    # all_distsolar_PV = {
    #     "SolarDistUtil_PV_1",
    #     "SolarDistUtil_PV_2",
    #     "SolarDistUtil_PV_3",
    #     "SolarDistUtil_PV_4",
    #     "SolarDistUtil_PV_5",
    #     "SolarDistUtil_PV_6",
    #     "SolarDistUtil_PV_7",
    # }
    #
    # all_utilsolar_PV = {
    #     "SolarUtil_PV_1",
    #     "SolarUtil_PV_2",
    #     "SolarUtil_PV_3",
    #     "SolarUtil_PV_4",
    #     "SolarUtil_PV_5",
    #     "SolarUtil_PV_6",
    #     "SolarUtil_PV_7",
    #     "Solar_PV",
    # }
    #
    # all_solar_therm = {"Solar_Thermal"}
    #
    # all_wind = {
    #     "Offshore_Wind",
    #     "Offshore_Wind_1",
    #     "Offshore_Wind_10",
    #     "Offshore_Wind_11",
    #     "Offshore_Wind_12",
    #     "Offshore_Wind_13",
    #     "Offshore_Wind_14",
    #     "Offshore_Wind_15",
    #     "Offshore_Wind_2",
    #     "Offshore_Wind_3",
    #     "Offshore_Wind_4",
    #     "Offshore_Wind_5",
    #     "Offshore_Wind_6",
    #     "Offshore_Wind_7",
    #     "Offshore_Wind_8",
    #     "Offshore_Wind_9",
    #     "Onshore_Wind",
    #     "Onshore_Wind_1",
    #     "Onshore_Wind_10",
    #     "Onshore_Wind_2",
    #     "Onshore_Wind_3",
    #     "Onshore_Wind_4",
    #     "Onshore_Wind_5",
    #     "Onshore_Wind_6",
    #     "Onshore_Wind_7",
    #     "Onshore_Wind_8",
    #     "Onshore_Wind_9",
    # }
    #
    # all_offwind = {
    #     "Offshore_Wind",
    #     "Offshore_Wind_1",
    #     "Offshore_Wind_10",
    #     "Offshore_Wind_11",
    #     "Offshore_Wind_12",
    #     "Offshore_Wind_13",
    #     "Offshore_Wind_14",
    #     "Offshore_Wind_15",
    #     "Offshore_Wind_2",
    #     "Offshore_Wind_3",
    #     "Offshore_Wind_4",
    #     "Offshore_Wind_5",
    #     "Offshore_Wind_6",
    #     "Offshore_Wind_7",
    #     "Offshore_Wind_8",
    #     "Offshore_Wind_9",
    # }
    #
    # all_onwind = {
    #     "Onshore_Wind",
    #     "Onshore_Wind_1",
    #     "Onshore_Wind_10",
    #     "Onshore_Wind_2",
    #     "Onshore_Wind_3",
    #     "Onshore_Wind_4",
    #     "Onshore_Wind_5",
    #     "Onshore_Wind_6",
    #     "Onshore_Wind_7",
    #     "Onshore_Wind_8",
    #     "Onshore_Wind_9",
    # }
    #
    # nrel_solar_PV = {
    #     "SolarDistUtil_PV_1",
    #     "SolarDistUtil_PV_2",
    #     "SolarDistUtil_PV_3",
    #     "SolarDistUtil_PV_4",
    #     "SolarDistUtil_PV_5",
    #     "SolarDistUtil_PV_6",
    #     "SolarDistUtil_PV_7",
    #     "SolarUtil_PV_1",
    #     "SolarUtil_PV_2",
    #     "SolarUtil_PV_3",
    #     "SolarUtil_PV_4",
    #     "SolarUtil_PV_5",
    #     "SolarUtil_PV_6",
    #     "SolarUtil_PV_7",
    # }
    #
    # nrel_offwind = {
    #     "Offshore_Wind_1",
    #     "Offshore_Wind_10",
    #     "Offshore_Wind_11",
    #     "Offshore_Wind_12",
    #     "Offshore_Wind_13",
    #     "Offshore_Wind_14",
    #     "Offshore_Wind_15",
    #     "Offshore_Wind_2",
    #     "Offshore_Wind_3",
    #     "Offshore_Wind_4",
    #     "Offshore_Wind_5",
    #     "Offshore_Wind_6",
    #     "Offshore_Wind_7",
    #     "Offshore_Wind_8",
    #     "Offshore_Wind_9",
    # }
    #
    # nrel_onwind = {
    #     "Onshore_Wind_1",
    #     "Onshore_Wind_10",
    #     "Onshore_Wind_2",
    #     "Onshore_Wind_3",
    #     "Onshore_Wind_4",
    #     "Onshore_Wind_5",
    #     "Onshore_Wind_6",
    #     "Onshore_Wind_7",
    #     "Onshore_Wind_8",
    #     "Onshore_Wind_9",
    # }
    #
    # agent = {
    #     "fossil_gen_agent",
    #     "renew_gen_agent",
    #     "transmission_agent",
    #     "demand_agent",
    # }
    #
    # prodn = {"fossil_gen_agent", "renew_gen_agent"}
    #
    # regions = set()
    # regions.update(wdl.add_notation["fips.full"])
    # regions.update(wdl.add_notation["state.abbv"])
    # regions.update(wdl.add_notation["region.reeds.reg"])
    # regions.update(wdl.add_notation["region.reeds.ba"])
    # regions.update(wdl.add_notation["region.epa.ipm"])
    #
    # reeds_region = set()
    # reeds_region.update(wdl.data.reeds_regions["region.reeds.reg"])
    #
    # reeds_balauth = set()
    # reeds_balauth.update(wdl.data.reeds_regions["region.reeds.ba"])
    #
    # fips = set()
    # fips.update(wdl.add_notation["fips.full"])
    #
    # ipm_regions = set()
    # ipm_regions.update(wdl.add_notation["region.epa.ipm"])
    #
    # offshore_fips = set()
    # offshore_fips.update(wdl.data.offshore["fips.full"])
    #
    # states = set()
    # states.update(wdl.add_notation["state.abbv"])
    #
    # uid = set()
    # uid.update(wdl.add_notation["unique_id_final"])
    #
    # hrs = set()
    # hrs.update(wdl.add_notation["hour"])
    #
    # epoch = set()
    # epoch.update(wdl.data.ldc["epoch"])
    #
    # cost_bin = {
    #     "value.cost.bin.1.usd_per_MW_per_year",
    #     "value.cost.bin.2.usd_per_MW_per_year",
    #     "value.cost.bin.3.usd_per_MW_per_year",
    #     "value.cost.bin.4.usd_per_MW_per_year",
    #     "value.cost.bin.5.usd_per_MW_per_year",
    # }
    #
    # #
    # #
    # # MAPS
    # time = set()
    # time.update(list(zip(wdl.data.ldc["epoch"], wdl.data.ldc["hour"])))
    #
    # map_fips_reeds_regions = set()
    # map_fips_reeds_regions.update(
    #     list(
    #         zip(
    #             wdl.data.reeds_regions["fips.full"],
    #             wdl.data.reeds_regions["region.reeds.reg"],
    #         )
    #     )
    # )
    #
    # map_fips_reeds_balauth = set()
    # map_fips_reeds_balauth.update(
    #     list(
    #         zip(
    #             wdl.data.reeds_regions["fips.full"],
    #             wdl.data.reeds_regions["region.reeds.ba"],
    #         )
    #     )
    # )
    #
    # map_fips_ipm = set()
    # map_fips_ipm.update(
    #     list(
    #         zip(
    #             wdl.data.epa_ipm_to_fips["fips.full"],
    #             wdl.data.epa_ipm_to_fips["region.epa.ipm"],
    #         )
    #     )
    # )
    #
    # map_fips_state = set()
    # map_fips_state.update(
    #     list(
    #         zip(
    #             wdl.data.epa_ipm_to_fips["fips.full"],
    #             wdl.data.epa_ipm_to_fips["state.abbv"],
    #         )
    #     )
    # )
    #
    # # MAPS -- locating generators to nodes
    # map_uid_fips = set()
    # map_uid_fips.update(
    #     list(
    #         zip(wdl.data.epa_needs["unique_id_final"], wdl.data.epa_needs["fips.full"],)
    #     )
    # )
    #
    # map_uid_ipm = set()
    # map_uid_ipm.update(
    #     list(
    #         zip(
    #             wdl.data.epa_needs["unique_id_final"],
    #             wdl.data.epa_needs["region.epa.ipm"],
    #         )
    #     )
    # )
    #
    # map_uid_type = set()
    # map_uid_type.update(
    #     list(
    #         zip(
    #             wdl.data.epa_needs["unique_id_final"], wdl.data.epa_needs["plant_type"],
    #         )
    #     )
    # )
    #
    # #
    # #
    # # PARAMETERS
    # ldc_raw = dict(
    #     zip(
    #         zip(
    #             wdl.data.ldc["epoch"],
    #             wdl.data.ldc["hour"],
    #             wdl.data.ldc["region.epa.ipm"],
    #         ),
    #         wdl.data.ldc["value.demand.MW"],
    #     )
    # )
    #
    # lat = dict(zip(wdl.data.latlng["fips.full"], wdl.data.latlng["lat"]))
    # lng = dict(zip(wdl.data.latlng["fips.full"], wdl.data.latlng["lng"]))
    #
    # cap = dict(
    #     zip(
    #         wdl.data.epa_needs["unique_id_final"],
    #         wdl.data.epa_needs["value.capacity.MW"],
    #     )
    # )
    #
    # hr = dict(
    #     zip(
    #         wdl.data.epa_needs["unique_id_final"],
    #         wdl.data.epa_needs["value.heat_rate.btu_per_kwh"],
    #     )
    # )
    #
    # pop = dict(
    #     zip(wdl.data.latlng["fips.full"], wdl.data.latlng["value.population.count"])
    # )
    #
    # miso_gen = dict(
    #     zip(
    #         zip(
    #             wdl.data.miso_gen["fips.full"],
    #             wdl.data.miso_gen["plant_type"],
    #             wdl.data.miso_gen["year_in_service"],
    #         ),
    #         wdl.data.miso_gen["value.capacity.MW"],
    #     )
    # )
    #
    # # VRE related parameters
    # nrel_wind_cf = dict(
    #     zip(
    #         zip(
    #             wdl.data.reeds_wind_cf["tech.label"],
    #             wdl.data.reeds_wind_cf["region.reeds.reg"],
    #             wdl.data.reeds_wind_cf["hour"],
    #         ),
    #         wdl.data.reeds_wind_cf["value.capacity_factor.unitless"],
    #     )
    # )
    #
    # nrel_wind_cap = pd.melt(
    #     wdl.data.reeds_wind_cap,
    #     id_vars=["region.reeds.reg", "tech.bin", "tech.label"],
    #     var_name="cost_bin",
    # )
    #
    # nrel_wind_cap = dict(
    #     zip(
    #         zip(
    #             nrel_wind_cap["tech.label"],
    #             nrel_wind_cap["region.reeds.reg"],
    #             nrel_wind_cap["cost_bin"],
    #         ),
    #         nrel_wind_cap["value"],
    #     )
    # )
    #
    # nrel_wind_cost = pd.melt(
    #     wdl.data.reeds_wind_costs,
    #     id_vars=["region.reeds.reg", "tech.bin", "tech.label"],
    #     var_name="cost_bin",
    # )
    #
    # nrel_wind_cost = dict(
    #     zip(
    #         zip(
    #             nrel_wind_cost["tech.label"],
    #             nrel_wind_cost["region.reeds.reg"],
    #             nrel_wind_cost["cost_bin"],
    #         ),
    #         nrel_wind_cost["value"],
    #     )
    # )
    #
    # nrel_solar_cf = dict(
    #     zip(
    #         zip(
    #             wdl.data.reeds_solar_cf["tech.label"],
    #             wdl.data.reeds_solar_cf["region.reeds.ba"],
    #             wdl.data.reeds_solar_cf["hour"],
    #         ),
    #         wdl.data.reeds_solar_cf["value.capacity_factor.unitless"],
    #     )
    # )
    #
    # nrel_solar_cap = pd.melt(
    #     wdl.data.reeds_solar_cap,
    #     id_vars=["region.reeds.ba", "tech.bin", "tech.label"],
    #     var_name="cost_bin",
    # )
    #
    # nrel_solar_cap = dict(
    #     zip(
    #         zip(
    #             nrel_solar_cap["tech.label"],
    #             nrel_solar_cap["region.reeds.ba"],
    #             nrel_solar_cap["cost_bin"],
    #         ),
    #         nrel_solar_cap["value"],
    #     )
    # )
    #
    # nrel_solar_cost = pd.melt(
    #     wdl.data.reeds_solar_costs,
    #     id_vars=["region.reeds.ba", "tech.bin", "tech.label"],
    #     var_name="cost_bin",
    # )
    #
    # nrel_solar_cost = dict(
    #     zip(
    #         zip(
    #             nrel_solar_cost["tech.label"],
    #             nrel_solar_cost["region.reeds.ba"],
    #             nrel_solar_cost["cost_bin"],
    #         ),
    #         nrel_solar_cost["value"],
    #     )
    # )
    #
    # #
    # #
    # # GDX data structure
    # data = {
    #     "a": {"type": "set", "elements": agent, "text": "model agent type"},
    #     "prodn": {
    #         "type": "set",
    #         "domain": ["a"],
    #         "domain_info": "regular",
    #         "elements": prodn,
    #         "text": "model agent type that generated electricity",
    #     },
    #     "k": {"type": "set", "elements": k, "text": "all technolgy types in the model"},
    #     "gen": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": gen,
    #         "text": "all electricty generation technolgy types in the model",
    #     },
    #     "fossil": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": fossil,
    #         "text": "fossil technolgoies",
    #     },
    #     "hydro": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": hydro,
    #         "text": "hyrdo technologies",
    #     },
    #     "geothermal": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": geothermal,
    #         "text": "geothermal technolgoies",
    #     },
    #     "all_wind": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": all_wind,
    #         "text": "all wind technolgoies",
    #     },
    #     "all_offwind": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": all_offwind,
    #         "text": "all offshore wind technolgoies",
    #     },
    #     "all_onwind": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": all_onwind,
    #         "text": "all onshore wind technolgoies",
    #     },
    #     "all_solar": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": all_solar,
    #         "text": "all solar technolgoies",
    #     },
    #     "all_solar_PV": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": all_solar_PV,
    #         "text": "all solar PV technolgoies",
    #     },
    #     "all_distsolar_PV": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": all_distsolar_PV,
    #         "text": "all distributed solar PV technolgoies",
    #     },
    #     "all_utilsolar_PV": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": all_utilsolar_PV,
    #         "text": "all utility scale solar PV technolgoies",
    #     },
    #     "all_solar_therm": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": all_solar_therm,
    #         "text": "all utility scale solar thermal technolgoies",
    #     },
    #     "nuclear": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": nuclear,
    #         "text": "nuclear technologies",
    #     },
    #     "store": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": store,
    #         "text": "storage technologies",
    #     },
    #     "battery": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": energy_storage,
    #         "text": "battery storage technologies",
    #     },
    #     "renew": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": renew,
    #         "text": "renewable technologies",
    #     },
    #     "nrel_offwind": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": nrel_offwind,
    #         "text": "offshore wind technologies from NREL",
    #     },
    #     "nrel_onwind": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": nrel_onwind,
    #         "text": "onshore wind technologies from NREL",
    #     },
    #     "nrel_solar_PV": {
    #         "type": "set",
    #         "domain": ["k"],
    #         "domain_info": "regular",
    #         "elements": nrel_solar_PV,
    #         "text": "solar PV technologies from NREL",
    #     },
    #     "reeds_regions": {
    #         "type": "set",
    #         "domain": ["regions"],
    #         "domain_info": "regular",
    #         "elements": reeds_region,
    #         "text": "NREL ReEDS regions",
    #     },
    #     "reeds_balauth": {
    #         "type": "set",
    #         "domain": ["regions"],
    #         "domain_info": "regular",
    #         "elements": reeds_balauth,
    #         "text": "NREL ReEDS balancing authority regions",
    #     },
    #     "uid": {
    #         "type": "set",
    #         "elements": uid,
    #         "text": "unique id numbers from EPA NEEDS database",
    #     },
    #     "regions": {"type": "set", "elements": regions, "text": "all regions"},
    #     "fips": {
    #         "type": "set",
    #         "domain": ["regions"],
    #         "domain_info": "regular",
    #         "elements": fips,
    #         "text": "all FIPS codes",
    #     },
    #     "offshore_fips": {
    #         "type": "set",
    #         "domain": ["regions"],
    #         "domain_info": "regular",
    #         "elements": offshore_fips,
    #         "text": "FIPS codes that have shoreline",
    #     },
    #     "ipm": {
    #         "type": "set",
    #         "domain": ["regions"],
    #         "domain_info": "regular",
    #         "elements": ipm_regions,
    #         "text": "all IPM codes",
    #     },
    #     "state": {
    #         "type": "set",
    #         "domain": ["regions"],
    #         "domain_info": "regular",
    #         "elements": states,
    #         "text": "all states",
    #     },
    #     "hrs": {"type": "set", "elements": hrs, "text": "hours in a year"},
    #     "epoch": {"type": "set", "elements": epoch, "text": "timestamp"},
    #     "time": {
    #         "type": "set",
    #         "domain": ["epoch", "hrs"],
    #         "domain_info": "regular",
    #         "elements": time,
    #         "text": "relationship between epoch and hrs",
    #     },
    #     "map_fips_reeds_regions": {
    #         "type": "set",
    #         "domain": ["regions", "regions"],
    #         "domain_info": "regular",
    #         "elements": map_fips_reeds_regions,
    #         "text": "map between FIPS5 codes and NREL ReEDS regions",
    #     },
    #     "map_fips_reeds_balauth": {
    #         "type": "set",
    #         "domain": ["regions", "regions"],
    #         "domain_info": "regular",
    #         "elements": map_fips_reeds_balauth,
    #         "text": "map between FIPS5 codes and NREL ReEDS balancing authority regions",
    #     },
    #     "map_fips_ipm": {
    #         "type": "set",
    #         "domain": ["regions", "regions"],
    #         "domain_info": "regular",
    #         "elements": map_fips_ipm,
    #         "text": "map between FIPS5 codes and IPM regions",
    #     },
    #     "map_fips_state": {
    #         "type": "set",
    #         "domain": ["regions", "regions"],
    #         "domain_info": "regular",
    #         "elements": map_fips_state,
    #         "text": "map between FIPS5 codes and State regions",
    #     },
    #     "map_uid_fips": {
    #         "type": "set",
    #         "domain": ["uid", "regions"],
    #         "domain_info": "regular",
    #         "elements": map_uid_fips,
    #         "text": "map between unit generator ID and FIPS5 codes",
    #     },
    #     "map_uid_ipm": {
    #         "type": "set",
    #         "domain": ["uid", "regions"],
    #         "domain_info": "regular",
    #         "elements": map_uid_ipm,
    #         "text": "map between unit generator ID and IPM region",
    #     },
    #     "map_uid_type": {
    #         "type": "set",
    #         "domain": ["uid", "k"],
    #         "domain_info": "regular",
    #         "elements": map_uid_type,
    #         "text": "map between unit generator ID and technolgy type",
    #     },
    #     "ldc_raw": {
    #         "type": "parameter",
    #         "domain": ["epoch", "hrs", "regions"],
    #         "domain_info": "regular",
    #         "elements": ldc_raw,
    #         "text": "raw load duration curves",
    #     },
    #     "lat": {
    #         "type": "parameter",
    #         "domain": ["regions"],
    #         "domain_info": "regular",
    #         "elements": lat,
    #         "text": "latitude",
    #     },
    #     "lng": {
    #         "type": "parameter",
    #         "domain": ["regions"],
    #         "domain_info": "regular",
    #         "elements": lng,
    #         "text": "longitude",
    #     },
    #     "cap": {
    #         "type": "parameter",
    #         "domain": ["uid"],
    #         "domain_info": "regular",
    #         "elements": cap,
    #         "text": "generation nameplate capacity (units: MW)",
    #     },
    #     "hr": {
    #         "type": "parameter",
    #         "domain": ["uid"],
    #         "domain_info": "regular",
    #         "elements": hr,
    #         "text": "generator efficiency (i.e., heat rate) (units: Btu/kWh)",
    #     },
    #     "population": {
    #         "type": "parameter",
    #         "domain": ["regions"],
    #         "domain_info": "regular",
    #         "elements": pop,
    #         "text": "population of a region (units: count)",
    #     },
    #     "miso_gen": {
    #         "type": "parameter",
    #         "domain": ["fips", "k", "*"],
    #         "domain_info": "relaxed",
    #         "elements": miso_gen,
    #         "text": "Projects listed in the MISO Generation Interconnection Queue",
    #     },
    #     "nrel_solar_cf": {
    #         "type": "parameter",
    #         "domain": ["k", "regions", "hrs"],
    #         "domain_info": "regular",
    #         "elements": nrel_solar_cf,
    #         "text": "solar capacity factor (units: unitless)",
    #     },
    #     "nrel_wind_cf": {
    #         "type": "parameter",
    #         "domain": ["k", "regions", "hrs"],
    #         "domain_info": "regular",
    #         "elements": nrel_wind_cf,
    #         "text": "wind capacity factor (units: unitless)",
    #     },
    #     "cost_bin": {"type": "set", "elements": cost_bin, "text": "cost bin"},
    #     "nrel_wind_cap": {
    #         "type": "parameter",
    #         "domain": ["k", "regions", "cost_bin"],
    #         "domain_info": "regular",
    #         "elements": nrel_wind_cap,
    #         "text": "wind potential capacity (units: MW)",
    #     },
    #     "nrel_wind_cost": {
    #         "type": "parameter",
    #         "domain": ["k", "regions", "cost_bin"],
    #         "domain_info": "regular",
    #         "elements": nrel_wind_cost,
    #         "text": "wind costs (units: $/MW/year)",
    #     },
    #     "nrel_solar_cap": {
    #         "type": "parameter",
    #         "domain": ["k", "regions", "cost_bin"],
    #         "domain_info": "regular",
    #         "elements": nrel_solar_cap,
    #         "text": "solar potential capacity (units: MW)",
    #     },
    #     "nrel_solar_cost": {
    #         "type": "parameter",
    #         "domain": ["k", "regions", "cost_bin"],
    #         "domain_info": "regular",
    #         "elements": nrel_solar_cost,
    #         "text": "solar costs (units: $/MW/year)",
    #     },
    # }
    #
    # #
    # #
    # # GDX creation
    # gdx = gmsxfr.GdxContainer("/Applications/GAMS30.3/Resources/sysdir")
    # gdx.validate(data)
    #
    # gdx.add_to_gdx(data, standardize_data=True, inplace=True, quality_checks=False)
    # gdx.write_gdx("werewolf_data_2.gdx", compress=True)
