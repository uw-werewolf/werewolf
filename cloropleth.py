import pandas as pd
import numpy as np
import folium


def solar_capacity_factor(to_csv=False):
    df = pd.read_csv(
        "../../data/processed_data/solar_hourly_capacity_factor.csv", engine="c"
    )
    df.drop(columns=["Unnamed: 0"], inplace=True)  # drop index_col
    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )  # convert timestamp to type datetime

    pt = df[["reeds_region", "value"]].groupby(["reeds_region"]).mean().copy()
    pt.reset_index(drop=False, inplace=True)
    pt_dict = dict(zip(pt["reeds_region"], pt["value"]))

    rr = pd.read_csv("../../data/processed_data/nrel_regions.csv", index_col=0)
    rr.reset_index(drop=False, inplace=True)
    rr["reeds.reg"] = [rr.loc[i, "reeds.reg"].split("s")[1] for i in rr.index]
    rr["reeds.reg"] = rr["reeds.reg"].map(int)
    reg_ba = dict(zip(rr["reeds.reg"], rr["reeds.ba"]))

    d = {}
    for i in set(rr["reeds.reg"].values):
        try:
            d[i] = pt_dict[reg_ba[i]]
        except:
            d[i] = 0

    dd = pd.DataFrame.from_dict(d, orient="index")
    dd.reset_index(drop=False, inplace=True)
    dd.rename(columns={"index": "reeds_region", 0: "value"}, inplace=True)

    if to_csv == True:
        dd.to_csv("../../data/processed_data/solar_agg_capacity_factor.csv")

    return dd


def wind_capacity_factor(to_csv=False):
    df = pd.read_csv(
        "../../data/processed_data/wind_hourly_capacity_factor.csv", engine="c"
    )
    df.drop(columns=["Unnamed: 0"], inplace=True)  # drop index_col
    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )  # convert timestamp to type datetime

    df["tech"] = df["tech"].str.split("_")
    df["tech"] = ["_".join(df.loc[i, "tech"][0:2]) for i in df.index]
    df["reeds_region"] = [df.loc[i, "reeds_region"].split("s")[1] for i in df.index]

    pt = (
        df[["tech", "reeds_region", "value"]]
        .groupby(["tech", "reeds_region"])
        .mean()
        .copy()
    )
    pt.reset_index(drop=False, inplace=True)
    pt["reeds_region"] = pt["reeds_region"].map(int)
    pt_dict = dict(zip(zip(pt["tech"], pt["reeds_region"]), pt["value"]))

    rr = pd.read_csv("../../data/processed_data/nrel_regions.csv", index_col=0)
    rr.reset_index(drop=False, inplace=True)
    rr["reeds.reg"] = [rr.loc[i, "reeds.reg"].split("s")[1] for i in rr.index]
    rr["reeds.reg"] = rr["reeds.reg"].map(int)

    d = {}
    for i in set(df["tech"].unique()):
        for j in set(rr["reeds.reg"].values):
            try:
                d[(i, j)] = pt_dict[(i, j)]
            except:
                d[(i, j)] = 0

    dd = pd.DataFrame.from_dict(pt_dict, orient="index")
    dd.reset_index(drop=False, inplace=True)
    dd.rename(columns={0: "value"}, inplace=True)

    dd["tech"] = [dd.loc[i, "index"][0] for i in dd.index]
    dd["reeds_region"] = [dd.loc[i, "index"][1] for i in dd.index]

    dd = dd[["tech", "reeds_region", "value"]].copy()

    if to_csv == True:
        dd.to_csv("../../data/processed_data/wind_agg_capacity_factor.csv")

    return dd


def wind_potential(to_csv=False):
    df = pd.read_csv("../../data/processed_data/wind_capacity_MW.csv", engine="c")

    df.drop(columns=["Unnamed: 0"], inplace=True)  # drop index_col
    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )  # convert timestamp to type datetime

    df["tech"] = df["tech"].str.split("_")
    df["tech"] = ["_".join(df.loc[i, "tech"][0:2]) for i in df.index]
    df["reeds_region"] = [df.loc[i, "reeds_region"].split("s")[1] for i in df.index]

    pt = (
        df[["tech", "reeds_region", "value"]]
        .groupby(["tech", "reeds_region"])
        .mean()
        .copy()
    )
    pt.reset_index(drop=False, inplace=True)
    pt["reeds_region"] = pt["reeds_region"].map(int)
    pt_dict = dict(zip(zip(pt["tech"], pt["reeds_region"]), pt["value"]))

    rr = pd.read_csv("./raw_input_data/nrel_regions.csv", index_col=0)
    rr.reset_index(drop=False, inplace=True)
    rr["reeds.reg"] = [rr.loc[i, "reeds.reg"].split("s")[1] for i in rr.index]
    rr["reeds.reg"] = rr["reeds.reg"].map(int)

    d = {}
    for i in set(df["tech"].unique()):
        for j in set(rr["reeds.reg"].values):
            try:
                d[(i, j)] = pt_dict[(i, j)]
            except:
                d[(i, j)] = 0

    dd = pd.DataFrame.from_dict(pt_dict, orient="index")
    dd.reset_index(drop=False, inplace=True)
    dd.rename(columns={0: "value"}, inplace=True)

    dd["tech"] = [dd.loc[i, "index"][0] for i in dd.index]
    dd["reeds_region"] = [dd.loc[i, "index"][1] for i in dd.index]

    dd = dd[["tech", "reeds_region", "value"]].copy()

    if to_csv == True:
        dd.to_csv("./processed_input_data/wind_capacity_factor.csv")

    return dd


def clean_geojson():

    df = pd.read_csv("./raw_input_data/nrel_regions.csv", index_col=0)
    reeds_region = list(df["reeds.reg"].unique())
    reeds_region = [int(i.split("s")[1]) for i in reeds_region]  # drop the leading 's'

    with open("./raw_input_data/nrel-lpreg3.json") as f:
        data = json.load(f)

    n = {"type": "FeatureCollection", "features": []}

    for i in range(len(data["features"])):
        if int(data["features"][i]["properties"]["gid"]) in reeds_region:
            a = data["features"][i]
            a["id"] = int(data["features"][i]["properties"]["gid"])
            n["features"].append(a)

    with open("./processed_input_data/nrel-lpreg3_no_canada.json", "w") as outfile:
        json.dump(n, outfile)


def map_cfs():
    # create a base map
    us_center = [39.8333333, -98.585522]  # lat, lng
    geo_data = "./processed_input_data/nrel-lpreg3_no_canada.json"

    #
    #
    # Solar CF map
    cf = solar_capacity_factor(to_csv=True)

    my_map = folium.Map(location=us_center, zoom_start=4)
    folium.Choropleth(
        geo_data=geo_data,
        name="Solar PV",
        data=cf,
        columns=["reeds_region", "value"],
        key_on="feature.id",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Solar PV Capacity Factor (%)",
    ).add_to(my_map)

    my_map.save("./output/solar_capacity_factors.html")

    #
    #
    # Wind CF map
    cf = wind_capacity_factor(to_csv=True)

    my_map = folium.Map(location=us_center, zoom_start=4)
    folium.Choropleth(
        geo_data=geo_data,
        name="Onshore Wind",
        data=cf[cf["tech"] == "Onshore_Wind"][["reeds_region", "value"]],
        columns=["reeds_region", "value"],
        key_on="feature.id",
        fill_color="YlGnBu",
        nan_fill_color="white",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Onshore Wind Capacity Factor (%)",
    ).add_to(my_map)
    my_map.save("./output/onshore_wind_capacity_factors.html")

    my_map = folium.Map(location=us_center, zoom_start=4)
    folium.Choropleth(
        geo_data=geo_data,
        name="Offshore Wind",
        data=cf[cf["tech"] == "Offshore_Wind"][["reeds_region", "value"]],
        columns=["reeds_region", "value"],
        key_on="feature.id",
        fill_color="YlGnBu",
        nan_fill_color="white",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Offshore Wind Capacity Factor (%)",
    ).add_to(my_map)
    my_map.save("./output/offshore_wind_capacity_factors.html")


if __name__ == "__main__":

    map_cfs()
