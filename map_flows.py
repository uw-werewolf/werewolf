import pandas as pd
import numpy as np
import gdxtools as gt
import folium
import math
from geographiclib.geodesic import Geodesic
import pdb


def get_bearing(i, j):
    lat_i, lng_i = i
    lat_j, lng_j = j

    lng_diff = np.radians(lng_j - lng_i)

    lat_i = np.radians(lat_i)
    lat_j = np.radians(lat_j)

    x = np.sin(lng_diff) * np.cos(lat_j)
    y = np.cos(lat_i) * np.sin(lat_j) - (
        np.sin(lat_i) * np.cos(lat_j) * np.cos(lng_diff)
    )
    bearing = np.degrees(np.arctan2(x, y))

    bearing = (bearing + 360) % 360

    return bearing - 90


def get_midpt(i, j):
    lat_i, lng_i = i
    lat_j, lng_j = j

    # Compute path from 1 to 2
    g = Geodesic.WGS84.Inverse(lat_i, lng_i, lat_j, lng_j)

    # Compute midpoint starting at 1
    h1 = Geodesic.WGS84.Direct(lat_i, lng_i, g["azi1"], g["s12"] / 2)

    return (h1["lat2"], h1["lon2"])


def make_power_flow_map(geoPts, flows):
    # create a base map
    wi_center = [44.437778, -90.130186]  # lat, lng
    my_map = folium.Map(location=wi_center, zoom_start=6)

    borders = folium.FeatureGroup("Boundaries", show=True)
    folium.GeoJson(
        "../../data/raw_data/county_borders.json",
        name="Counties",
        style_function=lambda x: {"weight": 0.25},
    ).add_to(borders)
    my_map.add_child(borders)

    colors = ["orange", "black"]

    pts = folium.FeatureGroup("Nodes", control=True, show=True)
    for j in geoPts:
        circ = folium.Circle(
            [geoPts[j][0], geoPts[j][1]],
            popup=j,
            radius=1000,
            color="orange",
            fill=True,
            fill_color="orange",
        )
        pts.add_child(circ)
    my_map.add_child(pts)

    for i in flows.keys():
        arcs = folium.FeatureGroup(
            "Power Flow in Block {}".format(i), control=True, show=False
        )
        for j in flows[i].keys():
            if flows[i][j] != 0:

                # pdb.set_trace()
                lat_i, lng_i = geoPts[j[0]][0], geoPts[j[0]][1]
                lat_j, lng_j = geoPts[j[1]][0], geoPts[j[1]][1]

                h = get_midpt((lat_i, lng_i), (lat_j, lng_j))

                line = folium.PolyLine(
                    [(lat_i, lng_i), h, (lat_j, lng_j)], weight=1.5, color="black"
                )

                rot = get_bearing((lat_i, lng_i), (lat_j, lng_j))
                marker = folium.RegularPolygonMarker(
                    location=h,
                    color="black",
                    fill_color="black",
                    number_of_sides=3,
                    radius=5,
                    rotation=rot,
                )

                arcs.add_child(line)
                arcs.add_child(marker)
        my_map.add_child(arcs)

    folium.LayerControl().add_to(my_map)
    my_map.save("./output/power_flow_map.html")


if __name__ == "__main__":

    gdxin = gt.gdxrw.gdxReader("./output.gdx")

    f = gdxin.rgdx(name="ave_f")
    lat = gdxin.rgdx(name="lat")
    lng = gdxin.rgdx(name="lng")
    ij = gdxin.rgdx(name="ij")
    nn = gdxin.rgdx(name="i")
    b = gdxin.rgdx(name="b")

    flows = pd.DataFrame(data=f["values"].keys(), columns=f["domain"])
    flows["values"] = f["values"].values()

    scn_lst = ["1"]
    for i in scn_lst:
        flows_p = flows[flows["r"] == i].copy()
        flows_p = pd.pivot_table(
            flows_p, values=["values"], columns=["b"], index=["i", "j"], fill_value=0
        ).reset_index(drop=False)

        flows_p = pd.concat([flows_p[["i", "j"]], flows_p["values"]], axis=1)
        flows_p.rename(columns={("i", ""): "i", ("j", ""): "j"}, inplace=True)

        arcs = pd.DataFrame(data=ij["elements"], columns=["i", "j"])
        all_arcs = arcs.merge(flows_p, on=["i", "j"], how="outer")
        all_arcs.fillna(0, inplace=True)
        all_arcs = pd.melt(all_arcs, id_vars=["i", "j"], var_name="b")

        arcs = {}
        for i in b["elements"]:
            a = all_arcs[all_arcs["b"] == i].copy()
            arcs[i] = dict(zip(list(zip(a["i"], a["j"])), a["value"]))

        nodes = {n: (lat["values"][n], lng["values"][n]) for n in nn["elements"]}

        make_power_flow_map(geoPts=nodes, flows=arcs)
