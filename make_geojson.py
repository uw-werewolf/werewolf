import pandas as pd
import json
import shapely.ops
import shapely.geometry
import filesys as fs
import gmsxfr
import os


def create_geojson():
    with open(os.path.join(fs.raw_data_dir, "county_borders.json")) as f:
        geodata = json.load(f)

    n = {"type": "FeatureCollection", "features": []}

    gdx = gmsxfr.GdxContainer(fs.gams_sysdir, os.path.join(fs.gdx_temp, "nodes.gdx"))
    gdx.rgdx()

    model_regions = gdx.to_dataframe("i")
    map_aggr = gdx.to_dataframe("map_aggr")

    gdx = gmsxfr.GdxContainer(fs.gams_sysdir, "final_results.gdx")
    gdx.rgdx()

    results_path = gdx.symText["results_folder"]

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
        with open(os.path.join(results_path, "regions.json"), "w") as outfile:
            json.dump(new_geodata, outfile)


if __name__ == "__main__":

    create_geojson()
