import pandas as pd
import numpy as np
import folium
import gdxtools as gt
from scipy import stats


def solar_capacity_factor(to_csv=False):
    df = pd.read_csv('./raw_input_data/solar_hourly_capacity_factor.csv', engine='c')
    df.drop(columns=['Unnamed: 0'], inplace=True)  # drop index_col
    df['timestamp'] = pd.to_datetime(df['timestamp'])  # convert timestamp to type datetime

    cap = pd.read_csv('./raw_input_data/solar_capacity_MW.csv', engine='c')
    cap.drop(columns=['Unnamed: 0', 'trb'], inplace=True)  # drop index_col
    cap['total'] = cap[['cost_bin1', 'cost_bin2', 'cost_bin3',
                        'cost_bin4', 'cost_bin5']].sum(axis=1)

    cap = cap.merge(cap[['tech', 'reeds.ba', 'total']].groupby(
        'reeds.ba').sum(), left_on='reeds.ba', right_on='reeds.ba').copy()
    cap['weight'] = cap['total_x'] / cap['total_y']

    pt = df[['tech', 'reeds_region', 'value']].groupby(['tech', 'reeds_region']).mean().copy()
    pt.reset_index(drop=False, inplace=True)

    pt = pt.merge(cap[['tech', 'reeds.ba', 'weight']], left_on=[
        'tech', 'reeds_region'], right_on=['tech', 'reeds.ba']).copy()

    pt['cf_weighted'] = pt['value'] * pt['weight']

    cf = pt[['tech', 'reeds_region', 'cf_weighted']].groupby(['reeds_region']).sum().copy()

    # calculate weighted std
    cf['std'] = 0
    for i in set(pt.reeds_region):
        values = pt[pt['reeds_region'] == i]['value'].values
        average = np.average(pt[pt['reeds_region'] == i]['value'].values,
                             weights=pt[pt['reeds_region'] == i]['weight'].values)

        cf.loc[i, 'std'] = np.sqrt(np.average(
            (values - average)**2, weights=pt[pt['reeds_region'] == i]['weight'].values))
    cf.reset_index(drop=False, inplace=True)

    cf_dict = dict(zip(cf['reeds_region'], cf['cf_weighted']))
    cf_std_dict = dict(zip(cf['reeds_region'], cf['std']))

    rr = pd.read_csv('./raw_input_data/nrel_regions.csv', index_col=0)
    rr.reset_index(drop=False, inplace=True)
    rr['reeds.reg'] = [rr.loc[i, 'reeds.reg'].split('s')[1] for i in rr.index]
    rr['reeds.reg'] = rr['reeds.reg'].map(int)
    reg_ba = dict(zip(rr['reeds.reg'], rr['reeds.ba']))

    d = {}
    d2 = {}
    for i in set(rr['reeds.reg'].values):
        try:
            d[i] = cf_dict[reg_ba[i]]
            d2[i] = cf_std_dict[reg_ba[i]]
        except:
            d[i] = 0
            d2[i] = 0

    dd = pd.DataFrame.from_dict(d, orient='index')
    dd.reset_index(drop=False, inplace=True)
    dd.rename(columns={'index': 'reeds_region', 0: 'cf_mean'}, inplace=True)
    dd['std'] = dd['reeds_region'].map(d2)

    if to_csv == True:
        dd.to_csv('./processed_input_data/solar_capacity_factor.csv')

    return dd


def clean_geojson():

    df = pd.read_csv('./raw_input_data/nrel_regions.csv', index_col=0)
    reeds_region = list(df['reeds.reg'].unique())
    reeds_region = [int(i.split('s')[1]) for i in reeds_region]  # drop the leading 's'

    with open('./raw_input_data/nrel-lpreg3.json') as f:
        data = json.load(f)

    n = {'type': 'FeatureCollection', 'features': []}

    for i in range(len(data['features'])):
        if int(data['features'][i]['properties']['gid']) in reeds_region:
            a = data['features'][i]
            a['id'] = int(data['features'][i]['properties']['gid'])
            n['features'].append(a)

    with open('./processed_input_data/nrel-lpreg3_no_canada.json', 'w') as outfile:
        json.dump(n, outfile)


def map_cfs():
    # create a base map
    us_center = [39.8333333, -98.585522]  # lat, lng
    geo_data = './processed_input_data/nrel-lpreg3_no_canada.json'

    #
    #
    # Solar CF map
    cf = solar_capacity_factor(to_csv=True)

    my_map = folium.Map(location=us_center, zoom_start=4)
    folium.Choropleth(geo_data=geo_data,
                      name='Solar PV',
                      data=cf['cf_mean'],
                      columns=['reeds_region', 'value'],
                      key_on='feature.id',
                      fill_color='YlOrRd',
                      fill_opacity=0.7,
                      line_opacity=0.2,
                      legend_name='Solar PV Capacity Factor (%)').add_to(my_map)

    my_map.save('./output/solar_capacity_factors.html')


if __name__ == '__main__':

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--dir', default='./gdx_temp/', type=str)
    #
    # args = parser.parse_args()

    # gdxin = gt.gdxrw.gdxReader(args.dir+'solar_data.gdx')

    gdxin = gt.gdxrw.gdxReader('./gdx_temp/solar_data.gdx')

    cf = gdxin.rgdx(name='nrel_solar_cf')
    mbh = gdxin.rgdx(name='map_block_hour')
    ldc = gdxin.rgdx(name='loadblockhours_compact')

    # make a dataframe for capacity factor
    cf2 = pd.DataFrame(data=cf['values'].keys(), columns=cf['domain'])
    cf2['value'] = cf['values'].values()

    # make a dataframe for block hour mapping
    mbh2 = pd.DataFrame(data=mbh['elements'], columns=mbh['domain'])
    bh_map = dict(zip(zip(mbh2.i, mbh2.hrs), mbh2.b))

    # map in block hour dimension
    cf2['block_hour'] = list(zip(cf2.i, cf2.hrs))
    cf2['block_hour'] = cf2['block_hour'].map(bh_map)

    results = pd.DataFrame(data=set(list(zip(cf2.i, cf2.k, cf2.block_hour))),
                           columns=['region', 'tech', 'block_hour'])
    results.sort_values(by=['region', 'tech', 'block_hour'], ignore_index=True, inplace=True)

    features = ['count', 'mean', 'std', 'min', '10%', '25%', '50%', '75%', '90%', 'max']
    for i in range(len(results)):
        print(i)
        cf21 = cf2[(cf2.i == results.loc[i, 'region'])]
        cf22 = cf21[(cf21.k == results.loc[i, 'tech']) & (
            cf21.block_hour == results.loc[i, 'block_hour'])]

        samples = cf22.value.values

        t = pd.DataFrame(data=samples).describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])

        for n, j in enumerate(features):
            results.loc[i, j] = round(t[0].values[n], 3)

        # k2, p = stats.normaltest(samples)
        w_stat, p_norm = stats.shapiro(samples)
        chi2_stat, p_uni = stats.chisquare(samples)

        print(p_norm, p_uni)

        if p_norm > 0.05:
            results.loc[i, 'normal_test'] = 'normal'
        else:
            results.loc[i, 'normal_test'] = 'not_normal'

        if p_uni > 0.05:
            results.loc[i, 'uniform_test'] = 'uniform'
        else:
            results.loc[i, 'uniform_test'] = 'not_uniform'
