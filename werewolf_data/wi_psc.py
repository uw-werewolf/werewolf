import pandas as pd
import numpy as np
import re
import datetime
import pickle
import os
import json


def read_fips_region(data_dir):
    # read in entire sheet
    df = pd.read_excel(
        os.path.join(
            data_dir,
            "raw_data",
            "v 6.17 IPM Region-State-County Mapping - 04-03-17 v2 ToEPA.xlsx",
        ),
        usecols="A:D",
        sheet_name="TO_GIS 04-03-2017",
        engine="openpyxl",
    )

    # remove rows with all NaN
    df.dropna(how="all", inplace=True)

    # rename
    df.rename(
        columns={
            "FIPS5": "fips",
            "State": "state",
            "County": "county",
            "v6.17 Model Region": "region name",
        },
        inplace=True,
    )

    # mapping = pd.read_csv(
    #     os.path.join(
    #         os.path.abspath(os.path.join(data_dir, os.pardir)),
    #         "mappings",
    #         "region_codes.csv",
    #     ),
    #     index_col=None,
    # )
    # df["state"] = df["state"].map(dict(zip(mapping["from"], mapping["to"])))

    # typing
    df["fips"] = df["fips"].map(int).map(str)

    return df


def read_miso_gen_queue(data_dir):
    df = pd.read_csv(
        os.path.join(data_dir, "raw_data", "Generation Interconnection Queue.csv"),
        engine="c",
    )

    # drop withdrawn project
    df.drop(df[df["Withdrawn Date"].isnull() == False].index, inplace=True)
    df.drop(df[df["Request Status"] == "Withdrawn"].index, inplace=True)

    # drop all projects that do not have a service date
    df.drop(df[df["Negotiated In Service Date"].isnull() == True].index, inplace=True)

    # drop all projects that do not have a specificed capacity
    df.drop(df[df["Decision Point 2 NRIS MW"] == 0].index, inplace=True)

    # drop projects that are not in certain states
    df.drop(
        df[df["State"].isin({"WI", "IL", "IA", "MN", "MI"}) == False].index,
        inplace=True,
    )

    # drop projects that are already in service
    df.drop(
        df[
            df["Post GIA Status"].isin({"Not Started", "Under Construction"}) == False
        ].index,
        inplace=True,
    )

    df.drop(
        columns=[
            "Request Status",
            "Queue Date",
            "Withdrawn Date",
            "Done Date",
            "Appl In Service Date",
            "Transmission Owner",
            "Study Cycle",
            "Study Group",
            "Study Phase",
            "Service Type",
            "Summer MW",
            "Winter MW",
            "Post GIA Status",
            "Decision Point 1 ERIS MW",
            "Decision Point 1 NRIS MW",
            "Decision Point 2 ERIS MW",
        ],
        inplace=True,
    )

    df["Negotiated In Service Date"] = pd.to_datetime(df["Negotiated In Service Date"])
    df["Negotiated In Service Date"] = df["Negotiated In Service Date"].dt.year

    # drop all projects that have negotiated in service dates before 2020
    df.drop(df[df["Negotiated In Service Date"] < 2020].index, inplace=True)

    return df


def read_needs_data(data_dir):
    df = pd.read_excel(
        os.path.join(data_dir, "raw_data", "needs_v6_03-26-2020.xlsx"),
        usecols="A:AX",
        sheet_name="NEEDS v6_active",
    )

    # pull out only these columns
    cols = [
        "Plant Name",
        "UniqueID_Final",
        "ORIS Plant Code",
        "Boiler/Generator/Committed Unit",
        "Unit ID",
        "CAMD Database UnitID",
        "PlantType",
        "Combustion Turbine/IC Engine",
        "Region Name",
        "State Code",
        "County",
        "County Code",
        "FIPS5",
        "Capacity (MW)",
        "Heat Rate (Btu/kWh)",
        "On Line Year",
        "Retirement Year",
        "Firing",
        "Bottom",
        "Cogen?",
        "Modeled Fuels",
    ]

    df = df[cols].copy()

    # remove rows with all NaN
    df.dropna(how="all", inplace=True)

    # clean up
    df.replace(
        {"#": "", " ": "_", "/": "", "\(": "", "\)": "", "-": "_"},
        regex=True,
        inplace=True,
    )

    df["FIPS5"] = df["FIPS5"].map(int).map(str)
    df["State Code"] = df["State Code"].map(str)
    df["County Code"] = df["County Code"].map(int)
    df["ORIS Plant Code"] = df["ORIS Plant Code"].map(int)
    df["On Line Year"] = df["On Line Year"].map(int)
    df["Retirement Year"] = df["Retirement Year"].map(int)

    return df


def read_egrid(data_dir):
    df = pd.read_excel(
        os.path.join(data_dir, "raw_data", "egrid2018_data_v2.xlsx"),
        usecols="A:AX",
        sheet_name="PLNT18",
    )

    # pull out only these columns
    cols = ["DOE/EIA ORIS plant or facility code", "Plant capacity factor"]
    df = df[cols].copy()

    # remove rows with all NaN
    df.dropna(how="all", inplace=True)
    df.drop(0, inplace=True)

    df["DOE/EIA ORIS plant or facility code"] = (
        df["DOE/EIA ORIS plant or facility code"].map(int).map(str)
    )
    df["Plant capacity factor"] = df["Plant capacity factor"].map(float)

    return df


def read_latlng(data_dir):
    # read data
    df = pd.read_csv(
        os.path.join(data_dir, "raw_data", "population_geo.csv"),
        index_col=None,
        engine="c",
    )

    df["STATEFP"] = df["STATEFP"] * 1000
    df["fips"] = df["STATEFP"] + df["COUNTYFP"]
    df["fips"] = df["fips"].map(str)

    # mapping = pd.read_csv(
    #     os.path.join(
    #         os.path.abspath(os.path.join(data_dir, os.pardir)),
    #         "mappings",
    #         "region_codes.csv",
    #     ),
    #     index_col=None,
    # )
    # df["STNAME"] = df["STNAME"].map(dict(zip(mapping["from"], mapping["to"])))

    df = df[["fips", "STNAME", "POPULATION", "LATITUDE", "LONGITUDE"]].copy()
    df.rename(
        columns={
            "STNAME": "state",
            "POPULATION": "population",
            "LATITUDE": "lat",
            "LONGITUDE": "lng",
        },
        inplace=True,
    )
    return df


def read_ldc(data_dir):
    # read data
    df = pd.read_excel(
        os.path.join(
            data_dir,
            "raw_data",
            "table_2-2_load_duration_curves_used_in_epa_platform_v6.xlsx",
        ),
        usecols="B:AB",
        sheet_name="Table 2-2",
        skiprows=3,
        engine="openpyxl",
    )

    # remove rows with all NaN
    df.dropna(how="all", inplace=True)

    df = pd.melt(
        df,
        id_vars=["Region", "Month", "Day"],
        value_vars=list(set(df.keys()) - {"Region", "Month", "Day"}),
        var_name="Hour",
    )

    df.replace({"Hour ": ""}, regex=True, inplace=True)
    df["Month"] = df["Month"].map(int)
    df["Day"] = df["Day"].map(int)
    df["Hour"] = df["Hour"].map(int)

    df["timestamp"] = [
        datetime.datetime(year=2021, month=1, day=1)
        + datetime.timedelta(
            days=int(df.loc[n, "Day"]) - 1, hours=int(df.loc[n, "Hour"]) - 1
        )
        for n, v in enumerate(df.value)
    ]

    df["epoch"] = [df.loc[n, "timestamp"].timestamp() for n, v in enumerate(df.value)]

    df["hour"] = [
        (
            df.loc[n, "timestamp"] - datetime.datetime(year=2021, month=1, day=1)
        ).total_seconds()
        / 60
        / 60
        + 1
        for n, v in enumerate(df.value)
    ]

    df["epoch"] = df["epoch"].map(int)
    df["hour"] = df["hour"].map(int)

    df = df[["timestamp", "epoch", "hour", "Region", "value"]].copy()
    df.sort_values(by=["Region", "epoch"], ascending=True, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def read_nrel_reeds_wind_cf(data_dir):
    file = [
        "LDC_static_inputs_06_27_2019_wind1.pkl",
        "LDC_static_inputs_06_27_2019_wind2.pkl",
        "LDC_static_inputs_06_27_2019_wind3.pkl",
        "LDC_static_inputs_06_27_2019_wind4.pkl",
    ]

    data = []
    for i in file:
        with open(os.path.join(data_dir, "raw_data", i), "rb") as f:
            d = pickle.load(f)
        data.append(d)

    df = pd.concat(data, axis=1)
    df.reset_index(drop=False, inplace=True)

    df = pd.melt(df, id_vars=["hour"])
    new = df["resource"].str.split("_", expand=True)

    df["tech"] = new[0]
    df["trb"] = new[1]
    df["reeds_region"] = new[2]
    df.drop(columns="resource", inplace=True)

    df = df[["tech", "trb", "reeds_region", "hour", "value"]]
    df["tech"] = df["tech"].map(
        {"wind-ons": "Onshore_Wind", "wind-ofs": "Offshore_Wind"}
    )
    df["tech"] = df["tech"] + "_" + df["trb"]

    return df


def read_nrel_reeds_solar_cf(data_dir):
    file = ["LDC_static_inputs_06_27_2019_upv.pkl"]

    data = []
    for i in file:
        with open(os.path.join(data_dir, "raw_data", i), "rb") as f:
            d = pickle.load(f)
        data.append(d)

    df = pd.concat(data, axis=1)
    df.reset_index(drop=False, inplace=True)

    df = pd.melt(df, id_vars=["hour"])
    new = df["resource"].str.split("_", expand=True)

    df["tech"] = new[0]
    df["trb"] = new[1]
    df["reeds_region"] = new[2]
    df.drop(columns="resource", inplace=True)

    df = df[["tech", "trb", "reeds_region", "hour", "value"]]
    df["tech"] = df["tech"].map({"dupv": "SolarDistUtil_PV", "upv": "SolarUtil_PV"})
    df["tech"] = df["tech"] + "_" + df["trb"]

    return df


def read_reeds_regions(data_dir):
    reeds_reg = pd.read_csv(
        os.path.join(data_dir, "raw_data", "nrel_reeds_region_mapping.csv"),
        index_col=None,
    )
    reeds_reg["fips"] = reeds_reg["state.fips"] * 1000 + reeds_reg["cnty.fips"]
    reeds_reg.drop(
        reeds_reg[reeds_reg["state.abb"].isin({"HI", "AK"}) == True].index, inplace=True
    )

    # fix NREL ReEDS regions (errors?)
    reeds_reg.loc[reeds_reg[reeds_reg["fips"] == 37133].index, "reeds.reg"] = 293
    reeds_reg.loc[reeds_reg[reeds_reg["fips"] == 53029].index, "reeds.reg"] = 3

    reeds_reg["reeds.reg"] = reeds_reg["reeds.reg"].map(int)

    reeds_reg["reeds.reg"] = ["s" + str(i) for i in reeds_reg["reeds.reg"]]
    reeds_reg["reeds.ba"] = ["p" + str(i) for i in reeds_reg["reeds.ba"]]

    return reeds_reg


def read_reeds_wind_cap(data_dir):

    df = pd.read_csv(
        os.path.join(data_dir, "raw_data", "wind_supply_curves_capacity_NARIS.csv"),
        index_col=None,
        engine="c",
    )
    df.rename(
        columns={"Unnamed: 0": "reeds.reg", "Unnamed: 1": "trb", "Unnamed: 2": "tech"},
        inplace=True,
    )

    df.rename(
        columns={
            "wsc1": "cost_bin1",
            "wsc2": "cost_bin2",
            "wsc3": "cost_bin3",
            "wsc4": "cost_bin4",
            "wsc5": "cost_bin5",
        },
        inplace=True,
    )

    # add in leading 's' to regions for consistancy
    df["reeds.reg"] = df["reeds.reg"].map(str)
    df["reeds.reg"] = "s" + df["reeds.reg"]

    df["trb"] = [i[1] for i in df["trb"].str.split("class")]

    df["tech"] = df["tech"].map(
        {"wind-ons": "Onshore_Wind", "wind-ofs": "Offshore_Wind"}
    )
    df["tech"] = df["tech"] + "_" + df["trb"]

    return df


def read_reeds_wind_costs(data_dir):
    df = pd.read_csv(
        os.path.join(data_dir, "raw_data", "wind_supply_curves_cost_NARIS.csv"),
        index_col=None,
    )
    df.rename(
        columns={"Unnamed: 0": "reeds.reg", "Unnamed: 1": "trb", "Unnamed: 2": "tech"},
        inplace=True,
    )

    # add in leading 's' to regions for consistancy
    df["reeds.reg"] = df["reeds.reg"].map(str)
    df["reeds.reg"] = "s" + df["reeds.reg"]

    df["trb"] = [i[1] for i in df["trb"].str.split("class")]

    df["tech"] = df["tech"].map(
        {"wind-ons": "Onshore_Wind", "wind-ofs": "Offshore_Wind"}
    )
    df["tech"] = df["tech"] + "_" + df["trb"]

    df.rename(
        columns={
            "wsc1": "cost_bin1",
            "wsc2": "cost_bin2",
            "wsc3": "cost_bin3",
            "wsc4": "cost_bin4",
            "wsc5": "cost_bin5",
        },
        inplace=True,
    )

    return df


def read_reeds_solar_cap(data_dir):
    file = "UPV_supply_curves_capacity_NARIS.csv"
    file2 = "DUPV_supply_curves_capacity_NARIS.csv"

    df = pd.read_csv(os.path.join(data_dir, "raw_data", file), index_col=None)
    df["tech"] = "SolarUtil_PV"

    df2 = pd.read_csv(os.path.join(data_dir, "raw_data", file2), index_col=None)
    df2["tech"] = "SolarDistUtil_PV"

    df.rename(
        columns={
            "upvsc1": "cost_bin1",
            "upvsc2": "cost_bin2",
            "upvsc3": "cost_bin3",
            "upvsc4": "cost_bin4",
            "upvsc5": "cost_bin5",
        },
        inplace=True,
    )

    df2.rename(
        columns={
            "dupvsc1": "cost_bin1",
            "dupvsc2": "cost_bin2",
            "dupvsc3": "cost_bin3",
            "dupvsc4": "cost_bin4",
            "dupvsc5": "cost_bin5",
        },
        inplace=True,
    )

    df.rename(columns={"Unnamed: 0": "reeds.ba", "Unnamed: 1": "trb"}, inplace=True)
    df2.rename(columns={"Unnamed: 0": "reeds.ba", "Unnamed: 1": "trb"}, inplace=True)

    # reorder the columns
    df = df[
        [
            "reeds.ba",
            "trb",
            "tech",
            "cost_bin1",
            "cost_bin2",
            "cost_bin3",
            "cost_bin4",
            "cost_bin5",
        ]
    ].copy()

    df2 = df2[
        [
            "reeds.ba",
            "trb",
            "tech",
            "cost_bin1",
            "cost_bin2",
            "cost_bin3",
            "cost_bin4",
            "cost_bin5",
        ]
    ].copy()

    df = pd.concat([df, df2], axis=0)

    df["trb"] = [i[1] for i in df["trb"].str.split("class")]
    df["tech"] = df["tech"] + "_" + df["trb"]

    return df


def read_reeds_solar_costs(data_dir):
    file = "UPV_supply_curves_cost_NARIS.csv"
    file2 = "DUPV_supply_curves_cost_NARIS.csv"

    df = pd.read_csv(os.path.join(data_dir, "raw_data", file), index_col=None)
    df["tech"] = "SolarUtil_PV"

    df2 = pd.read_csv(os.path.join(data_dir, "raw_data", file2), index_col=None)
    df2["tech"] = "SolarDistUtil_PV"

    df.rename(
        columns={
            "upvsc1": "cost_bin1",
            "upvsc2": "cost_bin2",
            "upvsc3": "cost_bin3",
            "upvsc4": "cost_bin4",
            "upvsc5": "cost_bin5",
        },
        inplace=True,
    )

    df2.rename(
        columns={
            "dupvsc1": "cost_bin1",
            "dupvsc2": "cost_bin2",
            "dupvsc3": "cost_bin3",
            "dupvsc4": "cost_bin4",
            "dupvsc5": "cost_bin5",
        },
        inplace=True,
    )

    df.rename(columns={"Unnamed: 0": "reeds.ba", "Unnamed: 1": "trb"}, inplace=True)
    df2.rename(columns={"Unnamed: 0": "reeds.ba", "Unnamed: 1": "trb"}, inplace=True)

    # reorder the columns
    df = df[
        [
            "reeds.ba",
            "trb",
            "tech",
            "cost_bin1",
            "cost_bin2",
            "cost_bin3",
            "cost_bin4",
            "cost_bin5",
        ]
    ].copy()
    df2 = df2[
        [
            "reeds.ba",
            "trb",
            "tech",
            "cost_bin1",
            "cost_bin2",
            "cost_bin3",
            "cost_bin4",
            "cost_bin5",
        ]
    ].copy()

    df = pd.concat([df, df2], axis=0)

    df["trb"] = [i[1] for i in df["trb"].str.split("class")]
    df["tech"] = df["tech"] + "_" + df["trb"]

    return df


def read_counties_with_shoreline(data_dir):

    df = pd.read_csv(
        os.path.join(data_dir, "raw_data", "offshore_wind_counties.csv"), index_col=None
    )

    df.drop(
        columns=[
            "Y",
            "X",
            "countyns",
            "geoid",
            "lsad",
            "namelsad",
            "classfp",
            "mtfcc",
            "csafp",
            "cbsafp",
            "metdivfp",
            "funcstat",
            "aland",
            "awater",
            "intptlat",
            "intptlon",
        ],
        inplace=True,
    )

    df["fips.full"] = df["statefp"] * 1000 + df["countyfp"]

    return df
