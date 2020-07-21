import os
import pandas as pd
from werewolf_python import *
import pprint


class _werewolf_1_0:
    def __init__(self, data_dir):
        from werewolf_data.epa_needs_093019 import (
            read_reeds_regions,
            read_fips_region,
            read_needs_data,
            read_latlng,
            read_ldc,
            read_nrel_reeds_wind_cf,
            read_reeds_wind_cap,
            read_reeds_wind_costs,
            read_nrel_reeds_solar_cf,
            read_reeds_solar_cap,
            read_reeds_solar_costs,
            read_counties_with_shoreline,
            read_egrid,
        )

        # region data
        self.epa_ipm_to_fips = read_fips_region(data_dir)
        self.offshore = read_counties_with_shoreline(data_dir)
        self.reeds_regions = read_reeds_regions(data_dir)

        # read EPA NEEDS data
        self.epa_needs = read_needs_data(data_dir)
        self.latlng = read_latlng(data_dir)

        # read EPA IPM LDCs
        self.ldc = read_ldc(data_dir)

        # read NREL VRE data
        self.reeds_wind_cf = read_nrel_reeds_wind_cf(data_dir)
        self.reeds_wind_cap = read_reeds_wind_cap(data_dir)
        self.reeds_wind_costs = read_reeds_wind_costs(data_dir)

        self.reeds_solar_cf = read_nrel_reeds_solar_cf(data_dir)
        self.reeds_solar_cap = read_reeds_solar_cap(data_dir)
        self.reeds_solar_costs = read_reeds_solar_costs(data_dir)


class _werewolf_2_0:
    def __init__(self, data_dir):
        from werewolf_data.wi_psc import (
            read_fips_region,
            read_reeds_regions,
            read_needs_data,
            read_latlng,
            read_ldc,
            read_nrel_reeds_wind_cf,
            read_reeds_wind_cap,
            read_reeds_wind_costs,
            read_nrel_reeds_solar_cf,
            read_reeds_solar_cap,
            read_reeds_solar_costs,
            read_counties_with_shoreline,
            read_miso_gen_queue,
            read_egrid,
        )

        # region data
        self.epa_ipm_to_fips = read_fips_region(data_dir)
        self.offshore = read_counties_with_shoreline(data_dir)
        self.reeds_regions = read_reeds_regions(data_dir)

        # read EPA NEEDS data
        self.epa_needs = read_needs_data(data_dir)
        self.latlng = read_latlng(data_dir)

        # read MISO generation queue
        self.miso_gen = read_miso_gen_queue(data_dir)

        # read eGrid data
        self.egrid = read_egrid(data_dir)

        # read EPA IPM LDCs
        self.ldc = read_ldc(data_dir)

        # read NREL VRE data
        self.reeds_wind_cf = read_nrel_reeds_wind_cf(data_dir)
        self.reeds_wind_cap = read_reeds_wind_cap(data_dir)
        self.reeds_wind_costs = read_reeds_wind_costs(data_dir)

        self.reeds_solar_cf = read_nrel_reeds_solar_cf(data_dir)
        self.reeds_solar_cap = read_reeds_solar_cap(data_dir)
        self.reeds_solar_costs = read_reeds_solar_costs(data_dir)


class WerewolfData:

    _versions = {"epa_2019": _werewolf_1_0, "wi_psc": _werewolf_2_0}
    _data_dir = {"epa_2019": "epa_needs_093019", "wi_psc": "wi_psc"}

    def __init__(self, data_dir, version=None):
        if version is None:
            version = "werewolf_1_0"
        if version not in self._versions:
            raise ValueError(f"Unknown WEREWOLF version: {version}")

        self.version = version
        self.data_dir = os.path.abspath(os.path.join(data_dir, self._data_dir[version]))
        self.data = self._versions[version](self.data_dir)

        # standardize column names for all data
        self.__rename_columns__()

        # drop columns not in the minimal column set
        self.__drop_columns__()

        # harmonize all data types
        self.__col_dtypes__()

        # container for notation
        self.add_notation = {}

        # find all unique columns
        self.__all_cols__ = []
        for k, v in self.data.__dict__.items():
            self.__all_cols__.extend(v.columns.tolist())
        self.__all_cols__ = list(set(self.__all_cols__))
        self.__all_cols__.sort()

    def __rename_columns__(self):
        import werewolf_data.rename_cols as cols

        for k, v in self.data.__dict__.items():
            v.rename(columns=cols._rename_cols[self.version][k], inplace=True)

    def __drop_columns__(self):
        import werewolf_data.rename_cols as cols

        for k, v in self.data.__dict__.items():
            drop_me = set(v.columns) - set(cols._col_dtypes[self.version].keys())
            if not (not drop_me):
                print(f"dropping columns {drop_me} from {k}")
                v.drop(columns=drop_me, inplace=True)

    def __col_dtypes__(self):
        import werewolf_data.rename_cols as cols

        for k, v in self.data.__dict__.items():
            for i in v.columns.to_list():
                if i not in {"timestamp"}:
                    print(
                        f"converting '{i}' in '{k}' from '{v[i].dtype}' --> '{cols._col_dtypes[self.version][i]}'"
                    )
                    v[i] = v[i].map(cols._col_dtypes[self.version][i])
                else:
                    v[i] = pd.to_datetime(v[i], unit="s")
                    v[i] = v[i].map(str)

    def bulk_replace(self, convert):
        for k, v in self.data.__dict__.items():
            v.replace(convert, inplace=True)

    def bulk_drop_rows(self):
        for k, v in self.__to_drop__.items():
            for col, v2 in v.items():

                if v2 != []:
                    idx = self.data.__dict__[k][
                        self.data.__dict__[k][col].isin(v2) == True
                    ].index

                    print(f"dropping {len(idx)} rows from '{col}' in '{k}'")
                    self.data.__dict__[k].drop(idx, inplace=True)

        for k, v in self.data.__dict__.items():
            v.reset_index(drop=True, inplace=True)

    def test_notation(self):
        if self.add_notation == {}:
            raise Exception("notation is empty!")

        self.__to_drop__ = {}
        for k, v in self.data.__dict__.items():
            self.__to_drop__[k] = {}
            for i in v.columns:
                self.__to_drop__[k][i] = []

                if i in self.add_notation.keys():

                    data = set(v[i])
                    notation = self.add_notation[i]

                    diff_data = data - notation
                    diff_notation = notation - data

                    # if sets are equal
                    if data == notation:
                        print(f"valid dense data detected in '{i}' for '{k}'")

                    # if data is a subset of notation
                    elif data.issubset(notation) and data != notation:
                        print(f"valid sparse data detected in '{i}' for '{k}'")

                    # if data is a superset of notation
                    elif data.issuperset(notation) and data != notation:
                        self.__to_drop__[k][i].extend(diff_data)
                        print(
                            f"**** POTENTIAL DATA DROP (dense structure): {len(diff_data)} elements in '{i}' for '{k}'"
                        )
                        if len(diff_data) < 200:
                            print(f"**** in data: {diff_data}")
                        elif len(diff_data) > 200:
                            print("**** (too many to show)")

                    # if symmetric difference is not empty and the length of differences are ==
                    elif data.symmetric_difference(notation) != set() and len(
                        diff_notation
                    ) == len(diff_data):
                        print(
                            f"**** POTENTIAL 1:1 MAP: {len(diff_data)} elements in '{i}' for '{k}'"
                        )
                        if len(diff_data) < 200 and len(diff_notation) < 200:
                            print(f"**** in data: {diff_data}")
                            print(f"**** in notation: {diff_notation}")
                        elif len(diff_data) > 200:
                            print("**** (too many to show)")

                    # if the left and right differences are != and diff_notation not empty
                    elif (
                        len(diff_notation) != len(diff_data) and diff_notation != set()
                    ):
                        self.__to_drop__[k][i].extend(diff_data)
                        print(
                            f"**** POTENTIAL DATA DROP (sparse structure): {len(diff_data)} elements in '{i}' for '{k}'"
                        )
                        if len(diff_data) < 200:
                            print(f"in data: {diff_data}")
                        elif len(diff_data) > 200:
                            print("**** (too many to show)")

                    # totally disjoint
                    elif notation.isdisjoint(data):
                        print(f"**** DISJOINT: '{i}' for '{k}'")
                        if len(data) < 200 and len(notation) < 200:
                            print(f"in data: {set(v[i])}")
                            print(f"in notation: {notation}")
                        elif len(data) > 200 or len(notation) > 200:
                            print("**** (too many to show)")

                    else:
                        print(f"**** UNKNOWN ISSUE: '{i}' for '{k}'")

    def bulk_map_column(self, from_col, to_col, mapping):
        for k, v in self.data.__dict__.items():
            if from_col in v.columns:
                print(f"mapping column '{to_col}' in table '{k}'...")
                v[to_col] = v[from_col].map(mapping)

    def bulk_drop_columns(self, header):
        for i in header:
            for k, v in self.data.__dict__.items():
                if i in v.columns:
                    print(f"dropping column '{i}' from table '{k}'...")
                    v.drop(columns=i, inplace=True)

    def unique_columns(self):
        col = set()
        for k, v in self.data.__dict__.items():
            col.update(v.columns)
        return col

    def column_view(self):
        pp = pprint.PrettyPrinter(indent=2)
        cv = {}
        for k, v in self.data.__dict__.items():
            cv[k] = v.columns.tolist()
        return pp.pprint(cv)

    def needs_notation(self):
        return self.unique_columns() - set(self.add_notation.keys())

    def to_csv(self, output_dir=None):
        if output_dir == None:
            self.output_dir = os.path.join(os.getcwd(), "standard_data")
        else:
            self.output_dir = os.path.abspath(output_dir)

        if os.path.isdir(self.output_dir) == False:
            os.mkdir(self.output_dir)

        for k, v in self.data.__dict__.items():
            v.to_csv(os.path.join(self.output_dir, f"{k}.csv"))


if __name__ == "__main__":

    wdl = WerewolfData(data_dir=os.path.join(os.getcwd(), "data"), version="wi_psc")

    # aggregate NREL solar and wind data into regional, only, data
    # must aggreate across technology and cost bins

    #
    #
    # SOLAR DATA
    wdl.data.reeds_solar_cap["solar_type"] = wdl.data.reeds_solar_cap[
        "tech.label"
    ].str.split("_")
    wdl.data.reeds_solar_cap["solar_type"] = wdl.data.reeds_solar_cap["solar_type"].str[
        0
    ]

    w_cap = []
    for i in {"SolarUtil", "SolarDistUtil"}:

        df = wdl.data.reeds_solar_cap[
            wdl.data.reeds_solar_cap["solar_type"] == i
        ].copy()
        df.drop(columns=["tech.label", "solar_type"], inplace=True)
        df["total"] = df[
            [
                "value.cost.bin.1.MW",
                "value.cost.bin.2.MW",
                "value.cost.bin.3.MW",
                "value.cost.bin.4.MW",
                "value.cost.bin.5.MW",
            ]
        ].sum(axis=1)

        df = df.merge(
            df[["tech.bin", "region.reeds.ba", "total"]]
            .groupby("region.reeds.ba")
            .sum(),
            on="region.reeds.ba",
        ).copy()

        df["weight"] = df["total_x"] / df["total_y"]

        df["solar_type"] = i
        w_cap.append(df[["solar_type", "region.reeds.ba", "tech.bin", "weight"]])

    w_cap = pd.concat(w_cap, ignore_index=True)

    # capacity weighted capacity factor calculation
    solar_cf = wdl.data.reeds_solar_cf.copy()
    solar_cf["solar_type"] = solar_cf["tech.label"].str.split("_")
    solar_cf["solar_type"] = solar_cf["solar_type"].str[0]

    solar_cf = solar_cf.merge(w_cap, on=["solar_type", "tech.bin", "region.reeds.ba"])

    solar_cf["weighted_cf"] = (
        solar_cf["weight"] * solar_cf["value.capacity_factor.unitless"]
    )
    solar_cf = (
        solar_cf[["solar_type", "region.reeds.ba", "hour", "tech.bin", "weighted_cf"]]
        .groupby(["solar_type", "region.reeds.ba", "hour"])
        .sum()
    )
    solar_cf.reset_index(drop=False, inplace=True)

    # new weighting factor to find weighted costs
    w_cap = pd.melt(
        wdl.data.reeds_solar_cap[
            [
                "region.reeds.ba",
                "tech.bin",
                "solar_type",
                "value.cost.bin.1.MW",
                "value.cost.bin.2.MW",
                "value.cost.bin.3.MW",
                "value.cost.bin.4.MW",
                "value.cost.bin.5.MW",
            ]
        ],
        id_vars=["region.reeds.ba", "tech.bin", "solar_type"],
        var_name="cost.bin",
    )

    w_cap["cost.bin"] = w_cap["cost.bin"].str.split(".")
    w_cap["cost.bin"] = w_cap["cost.bin"].str[3]

    w_cap = w_cap.merge(
        w_cap.groupby(["solar_type", "region.reeds.ba"]).sum(),
        on=["region.reeds.ba", "solar_type"],
    ).copy()

    w_cap["weighted_cap"] = w_cap["value_x"] / w_cap["value_y"]
    w_cap = w_cap[
        ["solar_type", "region.reeds.ba", "tech.bin", "cost.bin", "weighted_cap"]
    ].copy()

    wdl.data.reeds_solar_costs["solar_type"] = wdl.data.reeds_solar_costs[
        "tech.label"
    ].str.split("_")

    wdl.data.reeds_solar_costs["solar_type"] = wdl.data.reeds_solar_costs[
        "solar_type"
    ].str[0]

    wdl.data.reeds_solar_costs = pd.melt(
        wdl.data.reeds_solar_costs[
            [
                "region.reeds.ba",
                "tech.bin",
                "solar_type",
                "value.cost.bin.1.usd_per_MW_per_year",
                "value.cost.bin.2.usd_per_MW_per_year",
                "value.cost.bin.3.usd_per_MW_per_year",
                "value.cost.bin.4.usd_per_MW_per_year",
                "value.cost.bin.5.usd_per_MW_per_year",
            ]
        ],
        id_vars=["region.reeds.ba", "tech.bin", "solar_type"],
        var_name="cost.bin",
    )

    wdl.data.reeds_solar_costs["cost.bin"] = wdl.data.reeds_solar_costs[
        "cost.bin"
    ].str.split(".")
    wdl.data.reeds_solar_costs["cost.bin"] = wdl.data.reeds_solar_costs["cost.bin"].str[
        3
    ]

    solar_costs = wdl.data.reeds_solar_costs.merge(
        w_cap, on=["solar_type", "region.reeds.ba", "tech.bin", "cost.bin"]
    )

    solar_costs["weighted_cost"] = solar_costs["value"] * solar_costs["weighted_cap"]

    solar_costs = (
        solar_costs[
            ["region.reeds.ba", "tech.bin", "solar_type", "cost.bin", "weighted_cost"]
        ]
        .groupby(["region.reeds.ba", "solar_type",])
        .sum()
        .copy()
    )

    solar_costs.reset_index(drop=False, inplace=True)

    # replace data in wdl
    wdl.data.reeds_solar_cf = solar_cf.copy()
    wdl.data.reeds_solar_costs = solar_costs.copy()

    wdl.data.reeds_solar_cap["value.MW"] = wdl.data.reeds_solar_cap[
        [
            "value.cost.bin.1.MW",
            "value.cost.bin.2.MW",
            "value.cost.bin.3.MW",
            "value.cost.bin.4.MW",
            "value.cost.bin.5.MW",
        ]
    ].sum(axis=1)

    wdl.data.reeds_solar_cap = (
        wdl.data.reeds_solar_cap[
            ["region.reeds.ba", "tech.bin", "solar_type", "value.MW"]
        ]
        .groupby(["solar_type", "region.reeds.ba"])
        .sum()
    )

    wdl.data.reeds_solar_cap.reset_index(drop=False, inplace=True)
    wdl.data.reeds_solar_cap.rename(columns={"solar_type": "tech.label"}, inplace=True)

    del solar_cf
    del solar_costs

    #
    #
    # WIND DATA
    wdl.data.reeds_wind_cap["wind_type"] = wdl.data.reeds_wind_cap[
        "tech.label"
    ].str.split("_")
    wdl.data.reeds_wind_cap["wind_type"] = wdl.data.reeds_wind_cap["wind_type"].str[0]

    w_cap = []
    for i in {"Offshore", "Onshore"}:

        df = wdl.data.reeds_wind_cap[wdl.data.reeds_wind_cap["wind_type"] == i].copy()
        df.drop(columns=["tech.label", "wind_type"], inplace=True)
        df["total"] = df[
            [
                "value.cost.bin.1.MW",
                "value.cost.bin.2.MW",
                "value.cost.bin.3.MW",
                "value.cost.bin.4.MW",
                "value.cost.bin.5.MW",
            ]
        ].sum(axis=1)

        df = df.merge(
            df[["tech.bin", "region.reeds.reg", "total"]]
            .groupby("region.reeds.reg")
            .sum(),
            on="region.reeds.reg",
        ).copy()

        df["weight"] = df["total_x"] / df["total_y"]

        df["wind_type"] = i
        w_cap.append(df[["wind_type", "region.reeds.reg", "tech.bin", "weight"]])

    w_cap = pd.concat(w_cap, ignore_index=True)

    # capacity weighted capacity factor calculation
    wind_cf = wdl.data.reeds_wind_cf.copy()
    wind_cf["wind_type"] = wind_cf["tech.label"].str.split("_")
    wind_cf["wind_type"] = wind_cf["wind_type"].str[0]

    wind_cf = wind_cf.merge(w_cap, on=["wind_type", "tech.bin", "region.reeds.reg"],)

    wind_cf["weighted_cf"] = (
        wind_cf["weight"] * wind_cf["value.capacity_factor.unitless"]
    )

    wind_cf = (
        wind_cf[["wind_type", "region.reeds.reg", "hour", "tech.bin", "weighted_cf"]]
        .groupby(["wind_type", "region.reeds.reg", "hour"])
        .sum()
    )
    wind_cf.reset_index(drop=False, inplace=True)

    # new weighting factor to find weighted costs
    w_cap = pd.melt(
        wdl.data.reeds_wind_cap[
            [
                "region.reeds.reg",
                "tech.bin",
                "wind_type",
                "value.cost.bin.1.MW",
                "value.cost.bin.2.MW",
                "value.cost.bin.3.MW",
                "value.cost.bin.4.MW",
                "value.cost.bin.5.MW",
            ]
        ],
        id_vars=["region.reeds.reg", "tech.bin", "wind_type"],
        var_name="cost.bin",
    )

    w_cap["cost.bin"] = w_cap["cost.bin"].str.split(".")
    w_cap["cost.bin"] = w_cap["cost.bin"].str[3]

    w_cap = w_cap.merge(
        w_cap.groupby(["wind_type", "region.reeds.reg"]).sum(),
        on=["region.reeds.reg", "wind_type"],
    ).copy()

    w_cap["weighted_cap"] = w_cap["value_x"] / w_cap["value_y"]
    w_cap = w_cap[
        ["wind_type", "region.reeds.reg", "tech.bin", "cost.bin", "weighted_cap"]
    ].copy()

    wdl.data.reeds_wind_costs["wind_type"] = wdl.data.reeds_wind_costs[
        "tech.label"
    ].str.split("_")

    wdl.data.reeds_wind_costs["wind_type"] = wdl.data.reeds_wind_costs["wind_type"].str[
        0
    ]

    wdl.data.reeds_wind_costs = pd.melt(
        wdl.data.reeds_wind_costs[
            [
                "region.reeds.reg",
                "tech.bin",
                "wind_type",
                "value.cost.bin.1.usd_per_MW_per_year",
                "value.cost.bin.2.usd_per_MW_per_year",
                "value.cost.bin.3.usd_per_MW_per_year",
                "value.cost.bin.4.usd_per_MW_per_year",
                "value.cost.bin.5.usd_per_MW_per_year",
            ]
        ],
        id_vars=["region.reeds.reg", "tech.bin", "wind_type"],
        var_name="cost.bin",
    )

    wdl.data.reeds_wind_costs["cost.bin"] = wdl.data.reeds_wind_costs[
        "cost.bin"
    ].str.split(".")
    wdl.data.reeds_wind_costs["cost.bin"] = wdl.data.reeds_wind_costs["cost.bin"].str[3]

    wind_costs = wdl.data.reeds_wind_costs.merge(
        w_cap, on=["wind_type", "region.reeds.reg", "tech.bin", "cost.bin"]
    )

    wind_costs["weighted_cost"] = wind_costs["value"] * wind_costs["weighted_cap"]

    wind_costs = (
        wind_costs[
            ["region.reeds.reg", "tech.bin", "wind_type", "cost.bin", "weighted_cost"]
        ]
        .groupby(["region.reeds.reg", "wind_type",])
        .sum()
        .copy()
    )

    wind_costs.reset_index(drop=False, inplace=True)

    # replace data in wdl
    wdl.data.reeds_wind_cf = wind_cf.copy()
    wdl.data.reeds_wind_costs = wind_costs.copy()

    wdl.data.reeds_wind_cap["value.MW"] = wdl.data.reeds_wind_cap[
        [
            "value.cost.bin.1.MW",
            "value.cost.bin.2.MW",
            "value.cost.bin.3.MW",
            "value.cost.bin.4.MW",
            "value.cost.bin.5.MW",
        ]
    ].sum(axis=1)

    wdl.data.reeds_wind_cap = (
        wdl.data.reeds_wind_cap[
            ["region.reeds.reg", "tech.bin", "wind_type", "value.MW"]
        ]
        .groupby(["wind_type", "region.reeds.reg"])
        .sum()
    )

    wdl.data.reeds_wind_cap.reset_index(drop=False, inplace=True)
    wdl.data.reeds_wind_cap.rename(columns={"wind_type": "tech.label"}, inplace=True)

    del wind_cf
    del wind_costs

    # create notation (no cnty notation right now, first clean things up)
    wdl.add_notation["state.abbv"] = set(wdl.data.reeds_regions["state.abbv"])
    wdl.add_notation["state.fullname"] = set(wdl.data.reeds_regions["state.fullname"])
    wdl.add_notation["fips.full"] = set(wdl.data.reeds_regions["fips.full"])
    wdl.add_notation["fips.cnty"] = set(wdl.data.reeds_regions["fips.cnty"])
    wdl.add_notation["fips.state"] = set(wdl.data.reeds_regions["fips.state"])
    wdl.add_notation["region.reeds.reg"] = set(
        wdl.data.reeds_regions["region.reeds.reg"]
    )
    wdl.add_notation["region.reeds.ba"] = set(wdl.data.reeds_regions["region.reeds.ba"])
    wdl.add_notation["unique_id_final"] = set(wdl.data.epa_needs["unique_id_final"])
    wdl.add_notation["plant_type"] = set(wdl.data.epa_needs["plant_type"])
    wdl.add_notation["hour"] = set(wdl.data.ldc["hour"])
    wdl.add_notation["region.epa.ipm"] = set(wdl.data.epa_needs["region.epa.ipm"]) - {
        "CN_AB",
        "CN_NF",
        "CN_PQ",
        "CN_NL",
        "CN_NB",
        "CN_SK",
        "CN_BC",
        "CN_MB",
        "CN_NS",
        "CN_PE",
        "CN_ON",
    }
    wdl.test_notation()

    # clean up
    wdl.bulk_replace(
        {
            "NY_Z_G-I": "NY_Z_G_I",
            "Solar": "Solar_PV",
            "Wind": "Onshore_Wind",
            "Combined Cycle": "Combined_Cycle",
            "Onshore": "Onshore_Wind",
            "Offshore": "Offshore_Wind",
        }
    )
    wdl.test_notation()
    wdl.bulk_drop_rows()

    #
    #
    # now to deal with county names

    # map state.fullname to state.abbv
    state_fullname_2_state_abbv = dict(
        zip(
            wdl.data.reeds_regions["state.fullname"],
            wdl.data.reeds_regions["state.abbv"],
        )
    )

    wdl.bulk_map_column(
        from_col="state.fullname",
        to_col="state.abbv",
        mapping=state_fullname_2_state_abbv,
    )

    wdl.test_notation()

    # join columns to match counties
    # add cnty.fullname_state.abbv columns
    wdl.data.reeds_regions["cnty.fullname_state.abbv"] = (
        wdl.data.reeds_regions["cnty.fullname"]
        + " County, "
        + wdl.data.reeds_regions["state.abbv"]
    )

    wdl.data.epa_ipm_to_fips["cnty.fullname_state.abbv"] = (
        wdl.data.epa_ipm_to_fips["cnty.fullname"]
        + " County, "
        + wdl.data.epa_ipm_to_fips["state.abbv"]
    )

    # create new notation
    wdl.add_notation["cnty.fullname_state.abbv"] = set(
        wdl.data.reeds_regions["cnty.fullname_state.abbv"]
    )

    wdl.test_notation()

    # clean up county names
    wdl.data.epa_ipm_to_fips.replace(
        {
            "Alexandria City County, VA": "Alexandria County, VA",
            "Bristol City County, VA": "Bristol County, VA",
            "Chesapeake City County, VA": "Chesapeake County, VA",
            "Covington City County, VA": "Covington County, VA",
            "Danville City County, VA": "Danville County, VA",
            "DeSoto County, LA": "De Soto County, LA",
            "DeWitt County, IL": "De Witt County, IL",
            "Hampton City County, VA": "Hampton County, VA",
            "Hopewell City County, VA": "Hopewell County, VA",
            "LaSalle County, IL": "La Salle County, IL",
            "Lynchburg City County, VA": "Lynchburg County, VA",
            "Manassas City County, VA": "Manassas County, VA",
            "Miami Dade County, FL": "Miami-Dade County, FL",
            "Portsmouth City County, VA": "Portsmouth County, VA",
            "Prince Georges County, MD": "Prince George's County, MD",
            "Queen Annes County, MD": "Queen Anne's County, MD",
            "Salem City County, VA": "Salem County, VA",
            "St Bernard County, LA": "St. Bernard County, LA",
            "St Charles County, LA": "St. Charles County, LA",
            "St Charles County, MO": "St. Charles County, MO",
            "St Clair County, IL": "St. Clair County, IL",
            "St Clair County, MI": "St. Clair County, MI",
            "St Croix County, WI": "St. Croix County, WI",
            "St Francois County, MO": "St. Francois County, MO",
            "St James County, LA": "St. James County, LA",
            "St Joseph County, IN": "St. Joseph County, IN",
            "St Joseph County, MI": "St. Joseph County, MI",
            "St Lawrence County, NY": "St. Lawrence County, NY",
            "St Louis City County, MO": "St. Louis City County, MO",
            "St Louis County, MN": "St. Louis County, MN",
            "St Louis County, MO": "St. Louis County, MO",
            "St Lucie County, FL": "St. Lucie County, FL",
            "St Mary County, LA": "St. Mary County, LA",
            "Suffolk City County, VA": "Suffolk County, VA",
            "Virginia Beach City County, VA": "Virginia Beach County, VA",
        },
        inplace=True,
    )

    wdl.test_notation()

    # merge colums for miso data
    wdl.data.miso_gen["cnty.fullname_state.abbv"] = (
        wdl.data.miso_gen["cnty.fullname"] + ", " + wdl.data.miso_gen["state.abbv"]
    )

    wdl.test_notation()

    wdl.data.miso_gen.replace(
        {
            "Grant County,Iowa County, WI": "Grant County, WI",
            "Greene County,Scott County, IL": "Greene County, IL",
            "Morgan County,Scott County, IL": "Morgan County, IL",
            "Morgan County,Sangamon County, IL": "Morgan County, IL",
            "Humboldt County,Kossuth County, IA": "Humboldt County, IA",
        },
        inplace=True,
    )

    # 1. map state.fullname to state.abbv
    cnty_fullname_state_abbv_2_fips_full = dict(
        zip(
            wdl.data.reeds_regions["cnty.fullname_state.abbv"],
            wdl.data.reeds_regions["fips.full"],
        )
    )

    wdl.bulk_map_column(
        from_col="cnty.fullname_state.abbv",
        to_col="fips.full",
        mapping=cnty_fullname_state_abbv_2_fips_full,
    )

    # to avoid confustion, get rid of all cnty.fullname columns
    wdl.bulk_drop_columns(["cnty.fullname"])
    wdl.test_notation()

    wdl.to_csv(output_dir=os.path.join(os.getcwd(), "standard_data"))

    #
    #
    #
    # now we have to generate the GDX file
    k = set()
    k.update(wdl.data.epa_needs["plant_type"])
    k.update(["Energy_Storage_slow", "Energy_Storage_med", "Energy_Storage_fast"])
    k.update(wdl.data.reeds_wind_cap["tech.label"])
    k.update(wdl.data.reeds_solar_cap["tech.label"])

    gen = set()
    gen.update(wdl.data.epa_needs["plant_type"])
    gen.remove("Energy_Storage")
    gen.update(wdl.data.reeds_wind_cap["tech.label"])
    gen.update(wdl.data.reeds_solar_cap["tech.label"])

    fossil = {
        "Coal_Steam",
        "Combined_Cycle",
        "Combustion_Turbine",
        "Fossil_Waste",
        "IGCC",
        "Landfill_Gas",
        "Municipal_Solid_Waste",
        "Non_Fossil_Waste",
        "OG_Steam",
        "Tires",
    }

    hydro = {"Hydro", "Pumped_Storage"}

    geothermal = {"Geothermal"}

    nuclear = {"Nuclear"}

    store = {
        "Energy_Storage_fast",
        "Energy_Storage_med",
        "Energy_Storage_slow",
        "Pumped_Storage",
    }

    energy_storage = {
        "Energy_Storage_fast",
        "Energy_Storage_med",
        "Energy_Storage_slow",
    }

    renew = {
        "Energy_Storage_fast",
        "Energy_Storage_med",
        "Energy_Storage_slow",
        "Fuel_Cell",
        "Hydro",
        "Offshore_Wind",
        "Onshore_Wind",
        "Pumped_Storage",
        "SolarDistUtil",
        "SolarUtil",
        "Solar_PV",
        "Solar_Thermal",
    }

    all_solar = {
        "SolarDistUtil",
        "SolarUtil",
        "Solar_PV",
        "Solar_Thermal",
    }

    all_solar_PV = {
        "SolarDistUtil",
        "SolarUtil",
        "Solar_PV",
    }

    all_distsolar_PV = {
        "SolarDistUtil",
    }

    all_utilsolar_PV = {
        "SolarUtil",
        "Solar_PV",
    }

    all_solar_therm = {"Solar_Thermal"}

    all_wind = {
        "Offshore_Wind",
        "Onshore_Wind",
    }

    all_offwind = {
        "Offshore_Wind",
    }

    all_onwind = {
        "Onshore_Wind",
    }

    nrel_solar = {"SolarDistUtil", "SolarUtil"}

    agent = {
        "fossil_gen_agent",
        "renew_gen_agent",
        "transmission_agent",
        "demand_agent",
    }

    prodn = {"fossil_gen_agent", "renew_gen_agent"}

    regions = set()
    regions.update(wdl.add_notation["fips.full"])
    regions.update(wdl.add_notation["state.abbv"])
    regions.update(wdl.add_notation["region.reeds.reg"])
    regions.update(wdl.add_notation["region.reeds.ba"])
    regions.update(wdl.add_notation["region.epa.ipm"])

    reeds_region = set()
    reeds_region.update(wdl.data.reeds_regions["region.reeds.reg"])

    reeds_balauth = set()
    reeds_balauth.update(wdl.data.reeds_regions["region.reeds.ba"])

    fips = set()
    fips.update(wdl.add_notation["fips.full"])

    ipm_regions = set()
    ipm_regions.update(wdl.add_notation["region.epa.ipm"])

    offshore_fips = set()
    offshore_fips.update(wdl.data.offshore["fips.full"])

    states = set()
    states.update(wdl.add_notation["state.abbv"])

    uid = set()
    uid.update(wdl.add_notation["unique_id_final"])

    hrs = set()
    hrs.update(wdl.add_notation["hour"])

    epoch = set()
    epoch.update(wdl.data.ldc["epoch"])

    #
    #
    # MAPS
    time = set()
    time.update(list(zip(wdl.data.ldc["epoch"], wdl.data.ldc["hour"])))

    map_fips_reeds_regions = set()
    map_fips_reeds_regions.update(
        list(
            zip(
                wdl.data.reeds_regions["fips.full"],
                wdl.data.reeds_regions["region.reeds.reg"],
            )
        )
    )

    map_fips_reeds_balauth = set()
    map_fips_reeds_balauth.update(
        list(
            zip(
                wdl.data.reeds_regions["fips.full"],
                wdl.data.reeds_regions["region.reeds.ba"],
            )
        )
    )

    map_fips_ipm = set()
    map_fips_ipm.update(
        list(
            zip(
                wdl.data.epa_ipm_to_fips["fips.full"],
                wdl.data.epa_ipm_to_fips["region.epa.ipm"],
            )
        )
    )

    map_fips_state = set()
    map_fips_state.update(
        list(
            zip(
                wdl.data.epa_ipm_to_fips["fips.full"],
                wdl.data.epa_ipm_to_fips["state.abbv"],
            )
        )
    )

    # MAPS -- locating generators to nodes
    map_uid_fips = set()
    map_uid_fips.update(
        list(
            zip(wdl.data.epa_needs["unique_id_final"], wdl.data.epa_needs["fips.full"],)
        )
    )

    map_uid_ipm = set()
    map_uid_ipm.update(
        list(
            zip(
                wdl.data.epa_needs["unique_id_final"],
                wdl.data.epa_needs["region.epa.ipm"],
            )
        )
    )

    map_uid_type = set()
    map_uid_type.update(
        list(
            zip(
                wdl.data.epa_needs["unique_id_final"], wdl.data.epa_needs["plant_type"],
            )
        )
    )

    #
    #
    # PARAMETERS
    ldc_raw = dict(
        zip(
            zip(
                wdl.data.ldc["epoch"],
                wdl.data.ldc["hour"],
                wdl.data.ldc["region.epa.ipm"],
            ),
            wdl.data.ldc["value.demand.MW"],
        )
    )

    lat = dict(zip(wdl.data.latlng["fips.full"], wdl.data.latlng["lat"]))
    lng = dict(zip(wdl.data.latlng["fips.full"], wdl.data.latlng["lng"]))

    cap = dict(
        zip(
            wdl.data.epa_needs["unique_id_final"],
            wdl.data.epa_needs["value.capacity.MW"],
        )
    )

    hr = dict(
        zip(
            wdl.data.epa_needs["unique_id_final"],
            wdl.data.epa_needs["value.heat_rate.btu_per_kwh"],
        )
    )

    pop = dict(
        zip(wdl.data.latlng["fips.full"], wdl.data.latlng["value.population.count"])
    )

    miso_gen = dict(
        zip(
            zip(
                wdl.data.miso_gen["fips.full"],
                wdl.data.miso_gen["plant_type"],
                wdl.data.miso_gen["year_in_service"],
            ),
            wdl.data.miso_gen["value.capacity.MW"],
        )
    )

    # VRE related parameters
    nrel_wind_cf = dict(
        zip(
            zip(
                wdl.data.reeds_wind_cf["wind_type"],
                wdl.data.reeds_wind_cf["region.reeds.reg"],
                wdl.data.reeds_wind_cf["hour"],
            ),
            wdl.data.reeds_wind_cf["weighted_cf"],
        )
    )

    nrel_wind_cap = dict(
        zip(
            zip(
                wdl.data.reeds_wind_cap["tech.label"],
                wdl.data.reeds_wind_cap["region.reeds.reg"],
            ),
            wdl.data.reeds_wind_cap["value.MW"],
        )
    )

    nrel_wind_cost = dict(
        zip(
            zip(
                wdl.data.reeds_wind_costs["wind_type"],
                wdl.data.reeds_wind_costs["region.reeds.reg"],
            ),
            wdl.data.reeds_wind_costs["weighted_cost"],
        )
    )

    nrel_solar_cf = dict(
        zip(
            zip(
                wdl.data.reeds_solar_cf["solar_type"],
                wdl.data.reeds_solar_cf["region.reeds.ba"],
                wdl.data.reeds_solar_cf["hour"],
            ),
            wdl.data.reeds_solar_cf["weighted_cf"],
        )
    )

    nrel_solar_cap = dict(
        zip(
            zip(
                wdl.data.reeds_solar_cap["tech.label"],
                wdl.data.reeds_solar_cap["region.reeds.ba"],
            ),
            wdl.data.reeds_solar_cap["value.MW"],
        )
    )

    nrel_solar_cost = dict(
        zip(
            zip(
                wdl.data.reeds_solar_costs["solar_type"],
                wdl.data.reeds_solar_costs["region.reeds.ba"],
            ),
            wdl.data.reeds_solar_costs["weighted_cost"],
        )
    )

    #
    #
    # GDX data structure
    data = {
        "a": {"type": "set", "elements": agent, "text": "model agent type"},
        "prodn": {
            "type": "set",
            "domain": ["a"],
            "domain_info": "regular",
            "elements": prodn,
            "text": "model agent type that generated electricity",
        },
        "k": {"type": "set", "elements": k, "text": "all technolgy types in the model"},
        "gen": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": gen,
            "text": "all electricty generation technolgy types in the model",
        },
        "fossil": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": fossil,
            "text": "fossil technolgoies",
        },
        "hydro": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": hydro,
            "text": "hyrdo technologies",
        },
        "geothermal": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": geothermal,
            "text": "geothermal technolgoies",
        },
        "all_wind": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": all_wind,
            "text": "all wind technolgoies",
        },
        "all_offwind": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": all_offwind,
            "text": "all offshore wind technolgoies",
        },
        "all_onwind": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": all_onwind,
            "text": "all onshore wind technolgoies",
        },
        "all_solar": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": all_solar,
            "text": "all solar technolgoies",
        },
        "all_solar_PV": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": all_solar_PV,
            "text": "all solar PV technolgoies",
        },
        "all_distsolar_PV": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": all_distsolar_PV,
            "text": "all distributed solar PV technolgoies",
        },
        "all_utilsolar_PV": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": all_utilsolar_PV,
            "text": "all utility scale solar PV technolgoies",
        },
        "all_solar_therm": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": all_solar_therm,
            "text": "all utility scale solar thermal technolgoies",
        },
        "nuclear": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": nuclear,
            "text": "nuclear technologies",
        },
        "store": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": store,
            "text": "storage technologies",
        },
        "battery": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": energy_storage,
            "text": "battery storage technologies",
        },
        "renew": {
            "type": "set",
            "domain": ["k"],
            "domain_info": "regular",
            "elements": renew,
            "text": "renewable technologies",
        },
        "reeds_regions": {
            "type": "set",
            "domain": ["regions"],
            "domain_info": "regular",
            "elements": reeds_region,
            "text": "NREL ReEDS regions",
        },
        "reeds_balauth": {
            "type": "set",
            "domain": ["regions"],
            "domain_info": "regular",
            "elements": reeds_balauth,
            "text": "NREL ReEDS balancing authority regions",
        },
        "nrel_solar": {"type": "set", "domain": ["k"], "elements": nrel_solar},
        "uid": {
            "type": "set",
            "elements": uid,
            "text": "unique id numbers from EPA NEEDS database",
        },
        "regions": {"type": "set", "elements": regions, "text": "all regions"},
        "fips": {
            "type": "set",
            "domain": ["regions"],
            "domain_info": "regular",
            "elements": fips,
            "text": "all FIPS codes",
        },
        "offshore_fips": {
            "type": "set",
            "domain": ["regions"],
            "domain_info": "regular",
            "elements": offshore_fips,
            "text": "FIPS codes that have shoreline",
        },
        "ipm": {
            "type": "set",
            "domain": ["regions"],
            "domain_info": "regular",
            "elements": ipm_regions,
            "text": "all IPM codes",
        },
        "state": {
            "type": "set",
            "domain": ["regions"],
            "domain_info": "regular",
            "elements": states,
            "text": "all states",
        },
        "hrs": {"type": "set", "elements": hrs, "text": "hours in a year"},
        "epoch": {"type": "set", "elements": epoch, "text": "timestamp"},
        "time": {
            "type": "set",
            "domain": ["epoch", "hrs"],
            "domain_info": "regular",
            "elements": time,
            "text": "relationship between epoch and hrs",
        },
        "map_fips_reeds_regions": {
            "type": "set",
            "domain": ["regions", "regions"],
            "domain_info": "regular",
            "elements": map_fips_reeds_regions,
            "text": "map between FIPS5 codes and NREL ReEDS regions",
        },
        "map_fips_reeds_balauth": {
            "type": "set",
            "domain": ["regions", "regions"],
            "domain_info": "regular",
            "elements": map_fips_reeds_balauth,
            "text": "map between FIPS5 codes and NREL ReEDS balancing authority regions",
        },
        "map_fips_ipm": {
            "type": "set",
            "domain": ["regions", "regions"],
            "domain_info": "regular",
            "elements": map_fips_ipm,
            "text": "map between FIPS5 codes and IPM regions",
        },
        "map_fips_state": {
            "type": "set",
            "domain": ["regions", "regions"],
            "domain_info": "regular",
            "elements": map_fips_state,
            "text": "map between FIPS5 codes and State regions",
        },
        "map_uid_fips": {
            "type": "set",
            "domain": ["uid", "regions"],
            "domain_info": "regular",
            "elements": map_uid_fips,
            "text": "map between unit generator ID and FIPS5 codes",
        },
        "map_uid_ipm": {
            "type": "set",
            "domain": ["uid", "regions"],
            "domain_info": "regular",
            "elements": map_uid_ipm,
            "text": "map between unit generator ID and IPM region",
        },
        "map_uid_type": {
            "type": "set",
            "domain": ["uid", "k"],
            "domain_info": "regular",
            "elements": map_uid_type,
            "text": "map between unit generator ID and technolgy type",
        },
        "ldc_raw": {
            "type": "parameter",
            "domain": ["epoch", "hrs", "regions"],
            "domain_info": "regular",
            "elements": ldc_raw,
            "text": "raw load duration curves",
        },
        "lat": {
            "type": "parameter",
            "domain": ["regions"],
            "domain_info": "regular",
            "elements": lat,
            "text": "latitude",
        },
        "lng": {
            "type": "parameter",
            "domain": ["regions"],
            "domain_info": "regular",
            "elements": lng,
            "text": "longitude",
        },
        "cap": {
            "type": "parameter",
            "domain": ["uid"],
            "domain_info": "regular",
            "elements": cap,
            "text": "generation nameplate capacity (units: MW)",
        },
        "hr": {
            "type": "parameter",
            "domain": ["uid"],
            "domain_info": "regular",
            "elements": hr,
            "text": "generator efficiency (i.e., heat rate) (units: Btu/kWh)",
        },
        "population": {
            "type": "parameter",
            "domain": ["regions"],
            "domain_info": "regular",
            "elements": pop,
            "text": "population of a region (units: count)",
        },
        "miso_gen": {
            "type": "parameter",
            "domain": ["fips", "k", "*"],
            "domain_info": "relaxed",
            "elements": miso_gen,
            "text": "Projects listed in the MISO Generation Interconnection Queue",
        },
        "nrel_solar_cf": {
            "type": "parameter",
            "domain": ["k", "regions", "hrs"],
            "domain_info": "regular",
            "elements": nrel_solar_cf,
            "text": "solar capacity factor (units: unitless)",
        },
        "nrel_wind_cf": {
            "type": "parameter",
            "domain": ["k", "regions", "hrs"],
            "domain_info": "regular",
            "elements": nrel_wind_cf,
            "text": "wind capacity factor (units: unitless)",
        },
        "nrel_wind_cap": {
            "type": "parameter",
            "domain": ["k", "regions"],
            "domain_info": "regular",
            "elements": nrel_wind_cap,
            "text": "wind potential capacity (units: MW)",
        },
        "nrel_wind_cost": {
            "type": "parameter",
            "domain": ["k", "regions"],
            "domain_info": "regular",
            "elements": nrel_wind_cost,
            "text": "wind costs (units: $/MW/year)",
        },
        "nrel_solar_cap": {
            "type": "parameter",
            "domain": ["k", "regions"],
            "domain_info": "regular",
            "elements": nrel_solar_cap,
            "text": "solar potential capacity (units: MW)",
        },
        "nrel_solar_cost": {
            "type": "parameter",
            "domain": ["k", "regions"],
            "domain_info": "regular",
            "elements": nrel_solar_cost,
            "text": "solar costs (units: $/MW/year)",
        },
    }

    #
    #
    # GDX creation
    gdx = gmsxfr.GdxContainer("/Applications/GAMS30.3/Resources/sysdir")
    gdx.validate(data)

    gdx.add_to_gdx(data, standardize_data=True, inplace=True, quality_checks=False)
    gdx.write_gdx("werewolf_data_test.gdx", compress=True)
