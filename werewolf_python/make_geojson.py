import pandas as pd
import json
import shapely.ops
import shapely.geometry
import gmsxfr
import os
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--gams_sysdir", dest="gams_sysdir", default=None, type=str)
    parser.add_argument("--data_repo", dest="data_repo", default=None, type=str)
    parser.add_argument("--data_dir", dest="data_dir", default=None, type=str)

    # parser.set_defaults(gams_sysdir="some path here")
    # parser.set_defaults(data_repo="some path here")
    # parser.set_defaults(support_data="some path here")
    # parser.set_defaults(data_dir="some path here")

    args = parser.parse_args()

    with open(os.path.join(args.data_dir, "county_borders.json")) as f:
        geodata = json.load(f)

    n = {"type": "FeatureCollection", "features": []}

    gdx = gmsxfr.GdxContainer(
        args.gams_sysdir, os.path.join(args.data_repo, "processed_werewolf_data.gdx")
    )
    gdx.rgdx(["i", "map_aggr"])

    model_regions = gdx.to_dataframe("i")
    map_aggr = gdx.to_dataframe("map_aggr")

    m = map_aggr["elements"].copy()

    new_geodata = {"type": "FeatureCollection", "features": []}
    for i in model_regions["elements"]["regions"].tolist():
        merge_regions = set(m[m["regions"] == i].fips.values)

        # make a list of polygons
        polygons = []
        for n, j in enumerate(geodata["features"]):
            if geodata["features"][n]["properties"]["GEOID"] in merge_regions:
                # print(n, geodata['features'][n]['properties']['GEOID'])
                polygons.append(
                    shapely.geometry.asShape(geodata["features"][n]["geometry"])
                )

        # polygon union
        boundary = shapely.ops.unary_union(polygons)

        # build new json
        if isinstance(boundary, shapely.geometry.multipolygon.MultiPolygon):
            # find main area
            area = [i.area / sum([j.area for j in boundary]) for i in boundary]
            idx = area.index(max(area))

            coordinates = []
            coordinates.append([[x, y] for x, y in list(boundary[idx].exterior.coords)])
            new_geodata["features"].append(
                {
                    "type": "Feature",
                    "properties": {"GEOID": i},
                    "geometry": {"type": "Polygon", "coordinates": coordinates},
                }
            )

        else:
            coordinates = []
            coordinates.append([[x, y] for x, y in list(boundary.exterior.coords)])
            new_geodata["features"].append(
                {
                    "type": "Feature",
                    "properties": {"GEOID": i},
                    "geometry": {"type": "Polygon", "coordinates": coordinates},
                }
            )

        # write json
        with open(os.path.join(args.data_repo, "regions.json"), "w") as outfile:
            json.dump(new_geodata, outfile)
