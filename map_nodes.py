import pandas as pd
import numpy as np
import gdxtools as gt
import folium


def make_node_map(geoPts, featureName):
    if not isinstance(featureName, (str, list)):
        raise Exception('featureName must be of type str or list')

    if not isinstance(geoPts, (dict, list)):
        raise Exception('geoPts must be a type dict or list')

    if isinstance(geoPts, dict):
        geoPts = [geoPts]
        featureName = [featureName]

    if len(featureName) != len(geoPts):
        raise Exception('featureName and geoPts must have the same length')

    if isinstance(geoPts, list):
        for i in geoPts:
            if not isinstance(i, dict):
                raise Exception(
                    'each element of geoPts must be a type dict and in format {region:(lat,lng)}')

    # create a base map
    wi_center = [44.437778, -90.130186]  # lat, lng
    my_map = folium.Map(location=wi_center, zoom_start=6)

    borders = folium.FeatureGroup('Counties', show=False)
    folium.GeoJson('../../data/raw_data/county_borders.json', name='Counties',
                   style_function=lambda x: {'weight': 0.25}).add_to(borders)
    my_map.add_child(borders)

    borders = folium.FeatureGroup('Tribal Lands', show=False)
    folium.GeoJson('../../data/raw_data/nrel-bia_tribal_lands.json', name='Tribal Lands',
                   style_function=lambda x: {'weight': 0.25}).add_to(borders)
    my_map.add_child(borders)

    borders = folium.FeatureGroup('NREL ReEDS Regions', show=False)
    folium.GeoJson('../../data/raw_data/nrel-lpreg3.json', name='NREL ReEDS Regions',
                   style_function=lambda x: {'weight': 0.25}).add_to(borders)
    my_map.add_child(borders)

    colors = ['orange', 'black']

    for n, pts in enumerate(geoPts):
        nodes = folium.FeatureGroup(featureName[n], control=True, show=False)

        for j in pts:
            circ = folium.Circle([pts[j][0], pts[j][1]],
                                 popup=j,
                                 radius=1000,
                                 color=colors[n],
                                 fill=True,
                                 fill_color=colors[n])
            nodes.add_child(circ)

        my_map.add_child(nodes)
    folium.LayerControl().add_to(my_map)
    my_map.save('./output/node_map.html')


if __name__ == '__main__':

    gdxin = gt.gdxrw.gdxReader('./gdx_temp/nodes.gdx')

    i = gdxin.rgdx(name='i')
    lat = gdxin.rgdx(name='lat')
    lng = gdxin.rgdx(name='lng')
    map_aggr = gdxin.rgdx(name='map_aggr')

    disagg = pd.DataFrame(data=map_aggr['elements'], columns=map_aggr['domain'])
    disagg['lat'] = disagg.fips.map(lat['values'])
    disagg['lng'] = disagg.fips.map(lng['values'])

    agg = pd.DataFrame(index=i['elements'])
    agg['lat'] = pd.DataFrame(data=lat['values'].values(), index=lat['values'].keys())
    agg['lng'] = pd.DataFrame(data=lng['values'].values(), index=lng['values'].keys())

    disagg_pts = dict(zip(disagg.fips, list(zip(disagg.lat, disagg.lng))))
    agg_pts = dict(zip(agg.index, list(zip(agg.lat, agg.lng))))

    make_node_map(geoPts=[disagg_pts, agg_pts], featureName=[
                  'Disaggregated Nodes', 'Aggregated Nodes'])
