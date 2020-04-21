import pandas as pd
import json
import shapely.ops
import shapely.geometry
import gdxtools as gt


def create_geojson():
    with open('../../data/raw_data/county_borders.json') as f:
        geodata = json.load(f)

    n = {'type': 'FeatureCollection', 'features': []}

    gdxin = gt.gdxrw.gdxReader('./gdx_temp/nodes.gdx')

    model_regions = gdxin.rgdx(name='i')
    map_aggr = gdxin.rgdx(name='map_aggr')

    gdxin = gt.gdxrw.gdxReader('./final_results.gdx')
    results_path = gdxin.rgdx(name='results_folder')
    results_path = results_path['text']

    m = pd.DataFrame(data=map_aggr['elements'], columns=['model_region', 'fips'])

    new_geodata = {'type': 'FeatureCollection', 'features': []}
    for i in model_regions['elements']:
        merge_regions = set(m[m['model_region'] == i].fips.values)

        # make a list of polygons
        polygons = []
        for n, j in enumerate(geodata['features']):
            if geodata['features'][n]['properties']['GEOID'] in merge_regions:
                # print(n, geodata['features'][n]['properties']['GEOID'])
                polygons.append(shapely.geometry.asShape(geodata['features'][n]['geometry']))

        # polygon union
        boundary = shapely.ops.unary_union(polygons)

        # build new json
        if isinstance(boundary, shapely.geometry.multipolygon.MultiPolygon):
            # find main area
            area = [i.area / sum([j.area for j in boundary]) for i in boundary]
            idx = area.index(max(area))

            coordinates = []
            coordinates.append([[x, y] for x, y in list(boundary[idx].exterior.coords)])
            new_geodata['features'].append({'type': 'Feature', 'properties': {'GEOID': i}, 'geometry': {
                                           'type': 'Polygon', 'coordinates': coordinates}})

        else:
            coordinates = []
            coordinates.append([[x, y] for x, y in list(boundary.exterior.coords)])
            new_geodata['features'].append({'type': 'Feature', 'properties': {'GEOID': i}, 'geometry': {
                                           'type': 'Polygon', 'coordinates': coordinates}})

        # write json
        with open(results_path + 'regions.json', 'w') as outfile:
            json.dump(new_geodata, outfile)


if __name__ == '__main__':

    create_geojson()
