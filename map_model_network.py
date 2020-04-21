import pandas as pd
import numpy as np
import gdxtools as gt
import folium
import json

if __name__ == '__main__':

    #
    #
    # get network data
    gdxin = gt.gdxrw.gdxReader('./gdx_temp/nodes.gdx')
    lat = gdxin.rgdx(name='lat')
    lng = gdxin.rgdx(name='lng')
    map_aggr = gdxin.rgdx(name='map_aggr')

    gdxin = gt.gdxrw.gdxReader('final_results.gdx')
    model_regions = gdxin.rgdx(name='i')
    map_center = gdxin.rgdx(name='map_center')
    results_folder = gdxin.rgdx(name='results_folder')
    results_folder = results_folder['text']

    gdxin = gt.gdxrw.gdxReader('./gdx_temp/network_arcs.gdx')
    ij = gdxin.rgdx(name='ij')

    agg = pd.DataFrame(index=model_regions['elements'])
    agg['lat'] = pd.DataFrame(data=lat['values'].values(), index=lat['values'].keys())
    agg['lng'] = pd.DataFrame(data=lng['values'].values(), index=lng['values'].keys())

    agg_pts = dict(zip(agg.index, list(zip(agg.lat, agg.lng))))

    #
    #
    # map network with Delaunay triangulation
    with open(results_folder + '/regions.json') as f:
        geodata = json.load(f)

    # map_center = [39.8333333, -98.585522]  # lat, lng for center of US
    map_center = [map_center['values']['lat'], map_center['values']['lng']]

    my_map = folium.Map(location=map_center, zoom_start=6)

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

    borders = folium.FeatureGroup('WEREWOLF Regions', show=False)
    folium.GeoJson(geodata, name='WEREWOLF Regions',
                   style_function=lambda x: {'weight': 0.25}).add_to(borders)
    my_map.add_child(borders)

    arcs = folium.FeatureGroup('Synthetic Transmission Network', control=True, show=False)
    for i, j in ij['elements']:
        line = folium.PolyLine([(lat['values'][i], lng['values'][i]),
                                (lat['values'][j], lng['values'][j])], weight=0.75, color='black')
        arcs.add_child(line)

    nodes = folium.FeatureGroup('Node Labels', control=True, show=False)
    for i in model_regions['elements']:
        circ = folium.Circle([lat['values'][i], lng['values'][i]],
                             popup=i,
                             radius=500,
                             color='orange',
                             fill=True,
                             fill_color='orange')
        nodes.add_child(circ)

    my_map.add_child(arcs)
    my_map.add_child(nodes)
    folium.LayerControl().add_to(my_map)
    my_map.save(results_folder + '/transmission_network.html')
