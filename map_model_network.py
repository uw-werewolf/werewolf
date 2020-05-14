import pandas as pd
import numpy as np
import folium
import json
import filesys as fs
import gmsxfr
import os

if __name__ == "__main__":

    #
    #
    # get network data
    gdx = gmsxfr.GdxContainer(fs.gams_sysdir, os.path.join(fs.gdx_temp, "nodes.gdx"))
    gdx.rgdx()

    lat = gdx.to_dict("lat")
    lng = gdx.to_dict("lng")
    map_aggr = gdx.to_dataframe("map_aggr")

    gdx = gmsxfr.GdxContainer(
        fs.gams_sysdir, os.path.join(fs.gdx_temp, "network_arcs.gdx")
    )
    gdx.rgdx()

    ij = gdx.to_dict("ij")

    gdx = gmsxfr.GdxContainer(fs.gams_sysdir, "final_results.gdx")
    gdx.rgdx()

    model_regions = gdx.to_dict("i")
    map_center = gdx.to_dict("map_center")
    results_folder = gdx.symText["results_folder"]

    agg = gdx.to_dataframe("i")["elements"].copy().set_index("i")
    agg["lat"] = agg.index.map(lat["elements"])
    agg["lng"] = agg.index.map(lng["elements"])

    agg_pts = dict(zip(agg.index, list(zip(agg.lat, agg.lng))))

    #
    #
    # map network with Delaunay triangulation
    with open(os.path.join(results_folder, "regions.json")) as f:
        geodata = json.load(f)

    # map_center = [39.8333333, -98.585522]  # lat, lng for center of US
    map_center = [map_center["elements"]["lat"], map_center["elements"]["lng"]]

    my_map = folium.Map(location=map_center, zoom_start=6)

    borders = folium.FeatureGroup("Counties", show=False)

    folium.GeoJson(
        os.path.join(fs.raw_data_dir, "county_borders.json"),
        name="Counties",
        style_function=lambda x: {"weight": 0.25},
    ).add_to(borders)
    my_map.add_child(borders)

    borders = folium.FeatureGroup("Tribal Lands", show=False)
    folium.GeoJson(
        os.path.join(fs.raw_data_dir, "nrel-bia_tribal_lands.json"),
        name="Tribal Lands",
        style_function=lambda x: {"weight": 0.25},
    ).add_to(borders)
    my_map.add_child(borders)

    borders = folium.FeatureGroup("NREL ReEDS Regions", show=False)
    folium.GeoJson(
        os.path.join(fs.raw_data_dir, "nrel-lpreg3.json"),
        name="NREL ReEDS Regions",
        style_function=lambda x: {"weight": 0.25},
    ).add_to(borders)
    my_map.add_child(borders)

    borders = folium.FeatureGroup("WEREWOLF Regions", show=False)
    folium.GeoJson(
        geodata, name="WEREWOLF Regions", style_function=lambda x: {"weight": 0.25}
    ).add_to(borders)
    my_map.add_child(borders)

    arcs = folium.FeatureGroup(
        "Synthetic Transmission Network", control=True, show=False
    )
    for i, j in ij["elements"]:
        line = folium.PolyLine(
            [
                (lat["elements"][i], lng["elements"][i]),
                (lat["elements"][j], lng["elements"][j]),
            ],
            weight=0.75,
            color="black",
        )
        arcs.add_child(line)

    nodes = folium.FeatureGroup("Node Labels", control=True, show=False)
    for i in model_regions["elements"]:
        circ = folium.Circle(
            [lat["elements"][i], lng["elements"][i]],
            popup=i,
            radius=500,
            color="orange",
            fill=True,
            fill_color="orange",
        )
        nodes.add_child(circ)

    my_map.add_child(arcs)
    my_map.add_child(nodes)
    folium.LayerControl().add_to(my_map)
    my_map.save(os.path.join(results_folder, "transmission_network.html"))
