import pandas as pd
import numpy as np
import folium
import json
import gdxtools as gt
import branca

if __name__ == '__main__':

    #
    #
    # get model results
    gdxin = gt.gdxrw.gdxReader('./gdx_temp/nodes.gdx')
    model_regions = gdxin.rgdx(name='i')

    gdxin = gt.gdxrw.gdxReader('./final_results.gdx')
    y_ikr = gdxin.rgdx(name='y_ikr')
    frac_r = gdxin.rgdx(name='frac_r')
    r = gdxin.rgdx(name='r')
    map_center = gdxin.rgdx(name='map_center')

    results_path = gdxin.rgdx(name='results_folder')
    results_path = results_path['text']

    fossil = gdxin.rgdx(name='fossil')
    hydro = gdxin.rgdx(name='hydro')
    renew = gdxin.rgdx(name='renew')
    store = gdxin.rgdx(name='store')
    nuclear = gdxin.rgdx(name='nuclear')
    battery = gdxin.rgdx(name='battery')
    geothermal = gdxin.rgdx(name='geothermal')
    all_wind = gdxin.rgdx(name='all_wind')
    all_offwind = gdxin.rgdx(name='all_offwind')
    all_onwind = gdxin.rgdx(name='all_onwind')
    all_solar = gdxin.rgdx(name='all_solar')
    all_solar_PV = gdxin.rgdx(name='all_solar_PV')
    all_distsolar_PV = gdxin.rgdx(name='all_distsolar_PV')
    all_utilsolar_PV = gdxin.rgdx(name='all_utilsolar_PV')
    all_solar_therm = gdxin.rgdx(name='all_solar_therm')

    carbon = {i: frac_r['values'][i] if frac_r['values'][i] >
              np.finfo(float).tiny else 0 for i in frac_r['values']}

    gen = pd.DataFrame(data=y_ikr['values'].keys(), columns=y_ikr['domain'])
    gen['value'] = y_ikr['values'].values()
    gen.loc[gen[gen['value'] < np.finfo(float).tiny].index, 'value'] = 0

    gen['is_solar'] = [i in all_solar['elements'] for i in gen['k']]
    gen['is_wind'] = [i in all_wind['elements'] for i in gen['k']]
    gen['is_nuclear'] = [i in nuclear['elements'] for i in gen['k']]
    gen['is_hydro'] = [i in hydro['elements'] for i in gen['k']]

    # rename technologies
    gen.loc[gen[gen['is_solar'] == True].index, 'k'] = 'Solar'
    gen.loc[gen[gen['is_wind'] == True].index, 'k'] = 'Wind'
    gen.loc[gen[gen['is_nuclear'] == True].index, 'k'] = 'Nuclear'
    gen.loc[gen[gen['is_hydro'] == True].index, 'k'] = 'Hydro'

    # groupby
    gen_ikr = gen.groupby(['k', 'i', 'r']).sum()
    gen_ikr.reset_index(drop=False, inplace=True)
    gen_ikr['value'] = gen_ikr['value'] / 1e3  # convert to GWh

    # calculate % change from baseline scenario
    n_plt = list(set(zip(gen_ikr.k, gen_ikr.i)))
    n_plt.sort()

    for a1, a2 in n_plt:
        idx = gen_ikr[(gen_ikr.k == a1) & (gen_ikr.i == a2)].index
        idx2 = gen_ikr[(gen_ikr.k == a1) & (gen_ikr.i == a2) & (gen_ikr.r == '1')].index
        gen_ikr.loc[idx, 'pct_delta'] = (gen_ikr.loc[idx, 'value'] -
                                         gen_ikr.loc[idx2, 'value'].values[0]) / gen_ikr.loc[idx2, 'value'].values[0]

    gen_ikr['pct_delta'] = round(gen_ikr['pct_delta'] * 100, 2)  # convert to %
    gen_ikr.fillna(0, inplace=True)

    #
    #
    # map pct delta from baseline maps
    with open(results_path + '/regions.json') as f:
        geodata = json.load(f)

    # map_center = [39.8333333, -98.585522]  # lat, lng for center of US
    map_center = [map_center['values']['lat'], map_center['values']['lng']]

    def style_function(feature):
        return {'fillColor': feature['properties']['color'],
                'color': 'black',
                'weight': 0.25,
                'fillOpacity': 0.8}

    n_plt = list(set(zip(gen_ikr.k, gen_ikr.r)))
    n_plt.sort()

    for a1, a2 in n_plt:
        gen = gen_ikr[(gen_ikr.k == a1)]

        if sum(gen.pct_delta == 0) != len(gen):
            gen = gen_ikr[(gen_ikr.k == a1) & (gen_ikr.r == a2)]

            my_map = folium.Map(location=map_center, zoom_start=6)

            pct_vals = dict(zip(gen.i, gen.pct_delta))

            # borders = folium.FeatureGroup('Model Regions', show=True)
            # folium.GeoJson(data=geodata,
            #                name='Model Regions',
            #                style_function=lambda x: {'weight': 0.25}).add_to(borders)
            # my_map.add_child(borders)

            colormap = branca.colormap.linear.RdBu_09.scale(-100, 100)
            colormap.caption = '% Change from Baseline Scenario'
            my_map.add_child(colormap)

            color_dict = {key: colormap(pct_vals[key]) for key in pct_vals.keys()}

            for feature in geodata['features']:
                feature['properties']['color'] = color_dict[feature['properties']['GEOID']]

            plt = folium.FeatureGroup(f'{carbon[a2]*100}% Carbon Reduction', show=False)
            for feature in geodata['features']:
                folium.GeoJson(feature,
                               name=f'{carbon[a2]*100}% Carbon Reduction',
                               style_function=style_function,
                               show=False).add_to(plt)
            my_map.add_child(plt)

            # folium.LayerControl(collapsed=True).add_to(my_map)
            my_map.save(results_path + f'/summary_maps/generation/{a1}_r{a2}_pct_delta_gen.html')

    #
    #
    # map abs values
    n_plt = list(set(zip(gen_ikr.k, gen_ikr.r)))
    n_plt.sort()

    for a1, a2 in n_plt:
        gen = gen_ikr[(gen_ikr.k == a1)]
        max_value = round(gen.value.max(), 2)

        if sum(gen.value == 0) != len(gen):
            gen = gen_ikr[(gen_ikr.k == a1) & (gen_ikr.r == a2)]

            my_map = folium.Map(location=map_center, zoom_start=6)

            vals = dict(zip(gen.i, gen.value))

            # borders = folium.FeatureGroup('Model Regions', show=True)
            # folium.GeoJson(data=geodata,
            #                name='Model Regions',
            #                style_function=lambda x: {'weight': 0.25}).add_to(borders)
            # my_map.add_child(borders)

            colormap = branca.colormap.linear.PuBu_09.scale(0, max_value)
            colormap.caption = 'Generation (GWh)'
            my_map.add_child(colormap)

            color_dict = {key: colormap(vals[key]) for key in vals.keys()}

            for feature in geodata['features']:
                feature['properties']['color'] = color_dict[feature['properties']['GEOID']]

            plt = folium.FeatureGroup(f'{carbon[a2]*100}% Carbon Reduction', show=False)
            for feature in geodata['features']:
                folium.GeoJson(feature,
                               name=f'{carbon[a2]*100}% Carbon Reduction',
                               style_function=style_function,
                               show=False).add_to(plt)
            my_map.add_child(plt)

            # folium.LayerControl(collapsed=True).add_to(my_map)
            my_map.save(results_path + f'/summary_maps/generation/{a1}_r{a2}_abs_gen.html')
