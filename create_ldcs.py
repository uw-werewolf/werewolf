import pandas as pd
import numpy as np
import gdxtools as gt
import matplotlib.pyplot as plt
import matplotlib.axis as axes
import seaborn as sns
import argparse
import glob
import os

pd.plotting.register_matplotlib_converters()


def fit_ldc(ldc, to_csv=False):
    ldc['season'] = 'annual'

    ldc['timestamp'] = pd.to_datetime(ldc['epoch'], unit='s')

    # map in day of week
    # monday is 0 and sunday is 6
    ldc['weekday'] = [i.weekday() for i in ldc['timestamp']]
    day = {0: 'weekday', 1: 'weekday', 2: 'weekday',
           3: 'weekday', 4: 'weekday', 5: 'weekend', 6: 'weekend'}
    ldc['daytype'] = ldc['weekday'].map(day)

    # 24 hour label
    ldc['24hr'] = [i.hour for i in ldc['timestamp']]

    # aggregate regions as necessary
    ldc = ldc.groupby(['timestamp', 'epoch', 'hrs', 'season', 'weekday',
                       'daytype', '24hr', 'region']).sum().reset_index(drop=False)

    # map in seasons
    # s = ['winter', 'spring', 'summer', 'fall', 'winter']
    # n = [1095, 2190, 2190, 2190, 1095]
    #
    # s = ['winter', 'summer', 'winter']
    # n = [2190, 4380, 2190]
    #
    # b = []
    # for i, k in enumerate(s):
    #     b.extend([s[i] for j in range(n[i])])
    #
    # ldc['season'] = ldc['hrs'].map(dict(zip([str(i) for i in range(1, 8760+1)], b)))

    # break regions into their ldc curves and assign loadblocks
    ldc['loadblock'] = None
    ldc['fit'] = 0

    for n, i in enumerate(ldc.region.unique()):

        ldc_1 = ldc[(ldc['region'] == i)].copy()

        ldc_1['loadblock'] = pd.qcut(ldc_1['value'], q=[
            0, 0.05, 0.15, 0.25, 0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 1], labels=False)

        for k in ldc_1.loadblock.unique():
            idx = ldc_1[ldc_1['loadblock'] == k].index
            ldc_1.loc[idx, 'fit'] = ldc_1.loc[idx, 'value'].mean()

        # nicer subseason labeling
        ldc_1['loadblock'] = ['b'+str(ldc_1.loc[i, 'loadblock']) for i in ldc_1.index]

        # put back into main dataframe
        ldc.loc[ldc_1.index, 'loadblock'] = ldc_1.loadblock
        ldc.loc[ldc_1.index, 'fit'] = ldc_1.fit

    return ldc


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='./gdx_temp/', type=str)

    args = parser.parse_args()

    gdxin = gt.gdxrw.gdxReader(args.dir+'ldc.gdx')

    ldc = gdxin.rgdx(name='ldc_container')
    regions = gdxin.rgdx(name='regions')
    hrs = gdxin.rgdx(name='hrs')

    load = pd.DataFrame(data=ldc['values'].keys())
    load.rename(columns={0: 'epoch', 1: 'hrs', 2: 'region'}, inplace=True)
    load['value'] = ldc['values'].values()

    ldc_fit = fit_ldc(ldc=load, to_csv=False)

    #
    #
    # export data to gdx
    gdxout = gt.gdxrw.gdxWriter(args.dir+'ldc_fit.gdx')

    season = ldc_fit.season.unique().tolist()
    gdxout.add_set(gamssetname='t',
                   toset=season,
                   desc='season')

    daytype = ldc_fit.daytype.unique().tolist()
    gdxout.add_set(gamssetname='daytype',
                   toset=daytype,
                   desc='type of day')

    b = ldc_fit.loadblock.unique().tolist()
    b.sort()
    gdxout.add_set(gamssetname='b',
                   toset=b,
                   desc='loadblock segments')

    hrs = ldc_fit.hrs.unique().tolist()
    gdxout.add_set(gamssetname='hrs',
                   toset=hrs,
                   desc='hours in a year')

    map_block_hour = list(zip(ldc_fit['region'], ldc_fit['loadblock'], ldc_fit['hrs']))
    gdxout.add_set_dc(gamssetname='map_block_hour',
                      domain=['regions', 'b', 'hrs'],
                      toset=map_block_hour,
                      desc='map between regions, loadblocks and hours of the year')

    loadblockhours = {}
    for i in ldc_fit.season.unique():
        for k in ldc_fit.loadblock.unique():
            idx = ldc_fit[(ldc_fit['region'] == ldc_fit.region.unique()[0]) & (
                ldc_fit['season'] == i) & (ldc_fit['loadblock'] == k)].index
            loadblockhours[(i, k)] = len(idx)
    gdxout.add_parameter_dc(gamsparametername='loadblockhours_compact',
                            domain=['t', 'b'],
                            toparameter=loadblockhours,
                            desc='# of hours per loadblock')

    load_compact = pd.pivot_table(ldc_fit[['season', 'loadblock', 'region', 'value']],
                                  index=['season', 'loadblock', 'region'],
                                  values='value',
                                  aggfunc=np.mean)
    load_compact.reset_index(drop=False, inplace=True)
    load_compact = dict(zip(load_compact[['season', 'loadblock', 'region']].itertuples(
        index=False, name=None), load_compact['value']))
    gdxout.add_parameter_dc(gamsparametername='ldc_compact',
                            domain=['t', 'b', 'regions'],
                            toparameter=load_compact,
                            desc='electrical demand (units: MW)')

    gdxout.export_gdx()

    # plot LDCs
    # first remove all files in the directory
    mydir = './output/ldc_curves/'
    filelist = glob.glob(os.path.join(mydir, "*"))
    for f in filelist:
        os.remove(f)

    # now plot

    plt.style.use(['seaborn-white', 'werewolf_style.mplstyle'])

    for i in ldc_fit.region.unique():
        fig, ax = plt.subplots()
        df = pd.DataFrame()
        df['raw'] = ldc_fit[ldc_fit['region'] == i].value.values.tolist()
        df['fit'] = ldc_fit[ldc_fit['region'] == i].fit.values.tolist()

        df.sort_values(by='raw', ascending=False, inplace=True)

        ax.plot(df.raw.values, linewidth=1, color='blue', label='raw')
        ax.plot(df.fit.values, linewidth=1, color='grey', label='fit')

        plt.suptitle('Load Demand Curve')
        plt.title('Node = ' + i)

        plt.ylim(bottom=0)
        plt.xlim(left=0, right=8760)
        ax = plt.gca()
        ax.grid(which='major', axis='y', linestyle='--')
        ax.grid(which='major', axis='x', linestyle='--')

        # plt.xlabel('Hour')
        plt.ylabel('Load (MW)')
        ax.legend(loc='best', frameon=True)
        ax.set_xticklabels([])
        plt.savefig(mydir + str(i) + '.png', dpi=600, format='png')
        plt.close()
