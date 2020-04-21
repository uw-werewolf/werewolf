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
    build = gdxin.rgdx(name='build')
    cntlreg = gdxin.rgdx(name='cntlreg')
    not_cntlreg = gdxin.rgdx(name='not_cntlreg')
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

    cap = pd.DataFrame(data=build['values'].keys(), columns=build['domain'])
    cap['value'] = build['values'].values()
    cap.loc[cap[cap['value'] < np.finfo(float).tiny].index, 'value'] = 0

    cap['is_cntlreg'] = [i in cntlreg['elements'] for i in cap['i']]
    cap['is_solar'] = [i in all_solar['elements'] for i in cap['k']]
    cap['is_wind'] = [i in all_wind['elements'] for i in cap['k']]
    cap['is_nuclear'] = [i in nuclear['elements'] for i in cap['k']]
    cap['is_hydro'] = [i in hydro['elements'] for i in cap['k']]

    # rename technologies
    cap.loc[cap[cap['is_solar'] == True].index, 'k'] = 'Solar'
    cap.loc[cap[cap['is_wind'] == True].index, 'k'] = 'Wind'
    cap.loc[cap[cap['is_nuclear'] == True].index, 'k'] = 'Nuclear'
    cap.loc[cap[cap['is_hydro'] == True].index, 'k'] = 'Hydro'

    # groupby
    cap_ikr = cap.groupby(['is_cntlreg', 'k', 'i', 'r']).sum()
    cap_ikr.reset_index(drop=False, inplace=True)

    # focus only on cntlregs (zero out other regions)
    cap_ikr.loc[cap_ikr[cap_ikr.is_cntlreg == False].index, 'value'] = 0

    # calculate % change from baseline scenario
    n_plt = list(set(zip(cap_ikr.k, cap_ikr.i)))
    n_plt.sort()

    for a1, a2 in n_plt:
        idx = cap_ikr[(cap_ikr.k == a1) & (cap_ikr.i == a2)].index
        idx2 = cap_ikr[(cap_ikr.k == a1) & (cap_ikr.i == a2) & (cap_ikr.r == '1')].index
        cap_ikr.loc[idx, 'pct_delta'] = (cap_ikr.loc[idx, 'value'] -
                                         cap_ikr.loc[idx2, 'value'].values[0]) / cap_ikr.loc[idx2, 'value'].values[0]

    cap_ikr['pct_delta'] = round(cap_ikr['pct_delta'] * 100, 2)  # convert to %
    cap_ikr.fillna(0, inplace=True)

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

    n_plt = list(set(zip(cap_ikr.k, cap_ikr.r)))
    n_plt.sort()

    for a1, a2 in n_plt:
        cap = cap_ikr[(cap_ikr.k == a1)]

        if sum(cap.pct_delta == 0) != len(cap):
            cap = cap_ikr[(cap_ikr.k == a1) & (cap_ikr.r == a2)]

            my_map = folium.Map(location=map_center, zoom_start=6)

            pct_vals = dict(zip(cap.i, cap.pct_delta))

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
            my_map.save(results_path +
                        f'/summary_maps/built_capacity/{a1}_r{a2}_pct_delta_built_cap_cntlreg.html')

    #
    #
    # map abs values
    n_plt = list(set(zip(cap_ikr.k, cap_ikr.r)))
    n_plt.sort()

    for a1, a2 in n_plt:
        cap = cap_ikr[(cap_ikr.k == a1)]
        max_value = round(cap.value.max(), 2)

        if sum(cap.value == 0) != len(cap):
            cap = cap_ikr[(cap_ikr.k == a1) & (cap_ikr.r == a2)]

            my_map = folium.Map(location=map_center, zoom_start=6)

            vals = dict(zip(cap.i, cap.value))

            # borders = folium.FeatureGroup('Model Regions', show=True)
            # folium.GeoJson(data=geodata,
            #                name='Model Regions',
            #                style_function=lambda x: {'weight': 0.25}).add_to(borders)
            # my_map.add_child(borders)

            colormap = branca.colormap.linear.PuBu_09.scale(0, max_value)
            colormap.caption = 'Built Generation Capacity (MW)'
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
            my_map.save(results_path +
                        f'/summary_maps/built_capacity/{a1}_r{a2}_abs_built_cap_cntlreg.html')
