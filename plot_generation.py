import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axis as axes
import seaborn as sns
import gdxtools as gt
import style_parameters

pd.plotting.register_matplotlib_converters()


if __name__ == '__main__':

    #
    #
    # get model results
    gdxin = gt.gdxrw.gdxReader('./final_results.gdx')
    cntlreg = gdxin.rgdx(name='cntlreg')
    not_cntlreg = gdxin.rgdx(name='not_cntlreg')
    y_ikr = gdxin.rgdx(name='y_ikr')
    frac_r = gdxin.rgdx(name='frac_r')
    r = gdxin.rgdx(name='r')

    results_path = gdxin.rgdx(name='results_folder')
    results_path = results_path['text']

    x_title = gdxin.rgdx(name='x_title')
    x_title = x_title['text']

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

    gen['r'] = gen['r'].map(carbon)
    gen['value'] = gen['value'] / 1000  # convert to GWh
    gen['r'] = gen['r'] * 100  # convert to %

    gen['is_cntlreg'] = [i in cntlreg['elements'] for i in gen['i']]
    gen['is_fossil'] = [i in fossil['elements'] for i in gen['k']]

    #
    #
    # plot aggregate generation for fossil and renew by policy scenario and cntlreg
    gen_2 = gen.groupby(['is_fossil', 'is_cntlreg', 'r']).sum()
    gen_2.reset_index(drop=False, inplace=True)

    n_plt = list(set(zip(gen_2.is_fossil, gen_2.is_cntlreg)))

    # label mapping
    fossil_map = {True: 'Fossil', False: 'Renew'}
    cntlreg_map = {True: 'Cntl Reg', False: 'Not Cntl Reg'}

    colorPalette = sns.color_palette(palette='Set3', n_colors=len(n_plt))
    colorDict = dict(zip(n_plt, colorPalette))

    plt.style.use(['seaborn-white', 'werewolf_style.mplstyle'])

    fig, ax = plt.subplots()
    for n, (i, j) in enumerate(n_plt):

        df = gen_2[(gen_2.is_fossil == i) & (gen_2.is_cntlreg == j)]

        ax.plot(df['r'], df['value'],
                visible=True,
                color=colorDict[(i, j)],
                linewidth=1,
                label=f'{fossil_map[i]} ({cntlreg_map[j]})')

        # plt.suptitle('super title here')
        plt.xlabel(x_title)
        plt.ylabel('Total Actual Generation (GWh)')
        plt.tight_layout()
        plt.ylim(0, 250000)
        ax.grid(which='major', axis='both', linestyle='--')
        ax.legend(loc='best', frameon=True)

    plt.savefig(results_path + '/summary_plots/agg_generation.png', dpi=600, format='png')

    #
    #
    # plot disaggregated generation for fossil and renew by policy scenario for cntlreg ONLY
    gen['is_solar'] = [i in all_solar['elements'] for i in gen['k']]
    gen['is_wind'] = [i in all_wind['elements'] for i in gen['k']]
    gen['is_nuclear'] = [i in nuclear['elements'] for i in gen['k']]
    gen['is_hydro'] = [i in hydro['elements'] for i in gen['k']]

    gen.loc[gen[gen['is_solar'] == True].index, 'k'] = 'Solar'
    gen.loc[gen[gen['is_wind'] == True].index, 'k'] = 'Wind'
    gen.loc[gen[gen['is_nuclear'] == True].index, 'k'] = 'Nuclear'
    gen.loc[gen[gen['is_hydro'] == True].index, 'k'] = 'Hydro'

    gen_2 = gen.groupby(['k', 'is_cntlreg', 'r']).sum()
    gen_2.reset_index(drop=False, inplace=True)

    # for this plot we only want to focus on generation in cntlreg
    gen_2.loc[gen_2[gen_2['is_cntlreg'] == False].index, 'value'] = 0

    n_plt = list(set(gen_2.k))
    n_plt.sort()

    colorPalette = sns.color_palette(palette='Set3', n_colors=len(n_plt))
    colorDict = dict(zip(n_plt, colorPalette))
    marker = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8',
              's', 'p', 'P', '*', 'h', 'H', '+', 'x', 'X', 'D', 'd', '|', '_']
    markerDict = dict(zip(colorDict.keys(), marker[0:len(colorDict)+1]))

    plt.style.use(['seaborn-white', 'werewolf_style.mplstyle'])

    fig, ax = plt.subplots()
    for n, i in enumerate(n_plt):
        df = gen_2[(gen_2.is_cntlreg == True) & (gen_2.k == i)]

        if sum(df.value == 0) != len(df):
            ax.plot(df['r'], df['value'],
                    visible=True,
                    color=colorDict[i],
                    linewidth=1,
                    label=i,
                    marker=markerDict[i],
                    markerSize=6)

        # plt.suptitle('super title here')
        plt.xlabel(x_title)
        plt.ylabel('Total Actual Generation (GWh)')
        plt.tight_layout()
        plt.ylim(0, 60000)
        ax.grid(which='major', axis='both', linestyle='--')
        ax.legend(loc='best', frameon=True)

    plt.savefig(results_path + '/summary_plots/agg_generation_cntlreg.png', dpi=600, format='png')
