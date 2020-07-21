import pandas as pd
import numpy as np
import folium
import json
import branca
import os
import gmsxfr
import style_parameters as sp
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--gams_sysdir", dest="gams_sysdir", default=None, type=str)
    parser.add_argument("--data_repo", dest="data_repo", default=None, type=str)
    parser.add_argument("--output", dest="output", default=None, type=str)
    parser.add_argument("--data_dir", dest="data_dir", default=None, type=str)

    # parser.set_defaults(gams_sysdir="some path here")
    # parser.set_defaults(data_repo="some path here")
    # parser.set_defaults(data_dir="some path here")

    args = parser.parse_args()

    #
    #
    # create directory for results
    if os.path.isdir(os.path.join(args.output, "generation")) == False:
        os.mkdir(os.path.join(args.output, "generation"))

    #
    #
    # get model results
    gdx = gmsxfr.GdxContainer(
        args.gams_sysdir, os.path.join(args.data_repo, "final_results.gdx")
    )
    gdx.rgdx(
        ["y_ikr", "map_center", "frac_r", "all_solar", "all_wind", "nuclear", "hydro"]
    )

    y_ikr = gdx.to_dataframe("y_ikr")
    map_center = gdx.to_dict("map_center")

    carbon = {
        i: gdx.to_dict("frac_r")["elements"][i]
        if gdx.to_dict("frac_r")["elements"][i] > np.finfo(float).tiny
        else 0
        for i in gdx.to_dict("frac_r")["elements"]
    }

    gen = y_ikr["elements"].copy()
    gen.loc[gen[gen["L"] <= np.finfo(float).tiny].index, "L"] = 0

    gen["is_solar"] = gen["k"].isin(gdx.to_dict("all_solar")["elements"])
    gen["is_wind"] = gen["k"].isin(gdx.to_dict("all_wind")["elements"])
    gen["is_nuclear"] = gen["k"].isin(gdx.to_dict("nuclear")["elements"])
    gen["is_hydro"] = gen["k"].isin(gdx.to_dict("hydro")["elements"])

    # rename technologies
    gen["k"] = gen["k"].map(sp.gen_map)

    # groupby
    gen_ikr = gen.groupby(["k", "i", "r"]).sum()
    gen_ikr.reset_index(drop=False, inplace=True)
    gen_ikr["L"] = gen_ikr["L"] / 1e3  # convert to GWh

    # calculate % change from baseline scenario
    n_plt = list(set(zip(gen_ikr.k, gen_ikr.i)))
    n_plt.sort()

    for a1, a2 in n_plt:
        idx = gen_ikr[(gen_ikr.k == a1) & (gen_ikr.i == a2)].index
        idx2 = gen_ikr[(gen_ikr.k == a1) & (gen_ikr.i == a2) & (gen_ikr.r == "1")].index
        gen_ikr.loc[idx, "pct_delta"] = (
            gen_ikr.loc[idx, "L"] - gen_ikr.loc[idx2, "L"].values[0]
        ) / gen_ikr.loc[idx2, "L"].values[0]

    gen_ikr["pct_delta"] = round(gen_ikr["pct_delta"] * 100, 2)  # convert to %
    gen_ikr.fillna(0, inplace=True)

    #
    #
    # map pct delta from baseline maps
    with open(os.path.join(args.data_repo, "regions.json")) as f:
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

    n_plt = list(set(zip(gen_ikr.k, gen_ikr.r)))
    n_plt.sort()

    for a1, a2 in n_plt:
        gen = gen_ikr[(gen_ikr.k == a1)]

        if sum(gen.pct_delta == 0) != len(gen):
            gen = gen_ikr[(gen_ikr.k == a1) & (gen_ikr.r == a2)]

            my_map = folium.Map(location=map_center, zoom_start=6)

            pct_vals = dict(zip(gen.i, gen.pct_delta))

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
                    args.output,
                    "generation",
                    f"{a1.replace('/','_').replace(' ','_')}_{a2}_pct_delta_gen.html",
                )
            )

    #
    #
    # map abs values
    n_plt = list(set(zip(gen_ikr.k, gen_ikr.r)))
    n_plt.sort()

    for a1, a2 in n_plt:
        gen = gen_ikr[(gen_ikr.k == a1)]
        max_value = round(gen.L.max(), 2)

        if sum(gen.L == 0) != len(gen):
            gen = gen_ikr[(gen_ikr.k == a1) & (gen_ikr.r == a2)]

            my_map = folium.Map(location=map_center, zoom_start=6)

            vals = dict(zip(gen.i, gen.L))

            colormap = branca.colormap.linear.PuBu_09.scale(0, max_value)
            colormap.caption = "Generation (GWh)"
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
                    args.output,
                    "generation",
                    f"{a1.replace('/','_').replace(' ','_')}_{a2}_abs_gen.html",
                )
            )
