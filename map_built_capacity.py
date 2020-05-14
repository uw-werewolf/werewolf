import pandas as pd
import numpy as np
import folium
import json
import branca
import os
import filesys as fs
import style_parameters as sp
import gmsxfr

if __name__ == "__main__":

    #
    #
    # get model results
    gdx = gmsxfr.GdxContainer(fs.gams_sysdir, os.path.join(fs.gdx_temp, "nodes.gdx"))
    gdx.rgdx()

    model_regions = gdx.to_dict("i")["elements"]

    gdx = gmsxfr.GdxContainer(fs.gams_sysdir, "final_results.gdx")
    gdx.rgdx()

    build = gdx.to_dataframe("build")
    map_center = gdx.to_dict("map_center")

    carbon = {
        i: gdx.to_dict("frac_r")["elements"][i]
        if gdx.to_dict("frac_r")["elements"][i] > np.finfo(float).tiny
        else 0
        for i in gdx.to_dict("frac_r")["elements"]
    }

    cap = build["elements"].copy()
    cap.loc[cap[cap["L"] <= np.finfo(float).tiny].index, "L"] = 0

    cap["is_solar"] = cap["k"].isin(gdx.to_dict("all_solar")["elements"])
    cap["is_wind"] = cap["k"].isin(gdx.to_dict("all_wind")["elements"])
    cap["is_nuclear"] = cap["k"].isin(gdx.to_dict("nuclear")["elements"])
    cap["is_hydro"] = cap["k"].isin(gdx.to_dict("hydro")["elements"])

    # rename technologies
    cap["k"] = cap["k"].map(sp.gen_map)

    # groupby
    cap_ikr = cap.groupby(["k", "i", "r"]).sum()
    cap_ikr.reset_index(drop=False, inplace=True)

    # calculate % change from baseline scenario
    n_plt = list(set(zip(cap_ikr.k, cap_ikr.i)))
    n_plt.sort()

    for a1, a2 in n_plt:
        idx = cap_ikr[(cap_ikr.k == a1) & (cap_ikr.i == a2)].index
        idx2 = cap_ikr[(cap_ikr.k == a1) & (cap_ikr.i == a2) & (cap_ikr.r == "1")].index
        cap_ikr.loc[idx, "pct_delta"] = (
            cap_ikr.loc[idx, "L"] - cap_ikr.loc[idx2, "L"].values[0]
        ) / cap_ikr.loc[idx2, "L"].values[0]

    cap_ikr["pct_delta"] = round(cap_ikr["pct_delta"] * 100, 2)  # convert to %
    cap_ikr.fillna(0, inplace=True)

    #
    #
    # map pct delta from baseline maps
    with open(os.path.join(gdx.symText["results_folder"], "regions.json")) as f:
        geodata = json.load(f)

    # map_center = [39.8333333, -98.585522]  # lat, lng for center of US
    map_center = [map_center["elements"]["lat"], map_center["elements"]["lng"]]

    def style_function(feature):
        return {
            "fillColor": feature["properties"]["color"],
            "color": "black",
            "weight": 0.25,
            "fillOpacity": 0.8,
        }

    n_plt = list(set(zip(cap_ikr.k, cap_ikr.r)))
    n_plt.sort()

    for a1, a2 in n_plt:
        cap = cap_ikr[(cap_ikr.k == a1)]

        if sum(cap.pct_delta == 0) != len(cap):
            cap = cap_ikr[(cap_ikr.k == a1) & (cap_ikr.r == a2)]

            my_map = folium.Map(location=map_center, zoom_start=6)

            pct_vals = dict(zip(cap.i, cap.pct_delta))

            colormap = branca.colormap.linear.RdBu_09.scale(-100, 100)
            colormap.caption = "% Change from Baseline Scenario"
            my_map.add_child(colormap)

            color_dict = {key: colormap(pct_vals[key]) for key in pct_vals.keys()}

            for feature in geodata["features"]:
                feature["properties"]["color"] = color_dict[
                    feature["properties"]["GEOID"]
                ]

            plt = folium.FeatureGroup(f"{carbon[a2]*100}% Carbon Reduction", show=False)
            for feature in geodata["features"]:
                folium.GeoJson(
                    feature,
                    name=f"{carbon[a2]*100}% Carbon Reduction",
                    style_function=style_function,
                    show=False,
                ).add_to(plt)
            my_map.add_child(plt)

            my_map.save(
                os.path.join(
                    gdx.symText["results_folder"],
                    "summary_maps",
                    "built_capacity",
                    f'{a1.replace("/","_").replace(" ","_")}_{a2}_pct_delta_built_cap.html',
                )
            )

    #
    #
    # map abs values
    n_plt = list(set(zip(cap_ikr.k, cap_ikr.r)))
    n_plt.sort()

    for a1, a2 in n_plt:
        cap = cap_ikr[(cap_ikr.k == a1)]
        max_value = round(cap.L.max(), 2)

        if sum(cap.L == 0) != len(cap):
            cap = cap_ikr[(cap_ikr.k == a1) & (cap_ikr.r == a2)]

            my_map = folium.Map(location=map_center, zoom_start=6)

            vals = dict(zip(cap.i, cap.L))

            colormap = branca.colormap.linear.PuBu_09.scale(0, max_value)
            colormap.caption = "Built Generation Capacity (MW)"
            my_map.add_child(colormap)

            color_dict = {key: colormap(vals[key]) for key in vals.keys()}

            for feature in geodata["features"]:
                feature["properties"]["color"] = color_dict[
                    feature["properties"]["GEOID"]
                ]

            plt = folium.FeatureGroup(f"{carbon[a2]*100}% Carbon Reduction", show=False)
            for feature in geodata["features"]:
                folium.GeoJson(
                    feature,
                    name=f"{carbon[a2]*100}% Carbon Reduction",
                    style_function=style_function,
                    show=False,
                ).add_to(plt)
            my_map.add_child(plt)

            my_map.save(
                os.path.join(
                    gdx.symText["results_folder"],
                    "summary_maps",
                    "built_capacity",
                    f'{a1.replace("/","_").replace(" ","_")}_{a2}__abs_built_cap.html',
                )
            )
