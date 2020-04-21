import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axis as axes
import seaborn as sns
import gdxtools as gt

pd.plotting.register_matplotlib_converters()


if __name__ == '__main__':

    #
    #
    # get model results
    gdxin = gt.gdxrw.gdxReader('./final_results.gdx')
    capacity = gdxin.rgdx(name='capacity')
    cntlreg = gdxin.rgdx(name='cntlreg')
    not_cntlreg = gdxin.rgdx(name='not_cntlreg')
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

    cap = pd.DataFrame(data=capacity['values'].keys(), columns=capacity['domain'])
    cap['value'] = capacity['values'].values()
    cap.loc[cap[cap['value'] < np.finfo(float).tiny].index, 'value'] = 0
    cap['r'] = cap['r'].map(carbon)
    cap['r'] = cap['r'] * 100  # convert to %

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

    #
    #
    # plot aggregate emissions by region for policy scenario
    cap_2 = cap.groupby(['is_cntlreg', 'k', 'r']).sum()
    cap_2.reset_index(drop=False, inplace=True)

    n_plt = list(set(cap_2.k))

    colorPalette = sns.color_palette(palette='Set3', n_colors=len(n_plt))
    colorDict = dict(zip(n_plt, colorPalette))

    plt.style.use(['seaborn-white', 'werewolf_style.mplstyle'])

    # plot for cntlreg
    i = True
    df = cap_2[(cap_2.is_cntlreg == i) & (cap_2.value > 0)]
    tech = []
    labels = []
    for ii in set(df.k):
        labels.append(ii)
        df2 = cap_2[(cap_2.is_cntlreg == i) & (cap_2.k == ii)]
        tech.append(list(df2.sort_values(by='r')['value'].values))

    tech = np.array(tech)
    sort_order = tech[:, 1].argsort()[::-1]
    labels = [labels[i] for i in sort_order]
    tech = tech[sort_order]

    fig, ax = plt.subplots()
    ax.grid(which='major', axis='both', linestyle='--')
    ax.stackplot(np.array(list(carbon.values()))*100, tech, labels=labels)
    ax.legend(loc='lower left', frameon=True)
    plt.xlabel(x_title)
    plt.ylabel('Generation Capacity (MW)')
    plt.ylim(0, 30000)
    plt.tight_layout()
    plt.savefig(results_path + '/summary_plots/agg_capacity_cntlreg.png', dpi=600, format='png')

    # plot for not_cntlreg
    i = False
    df = cap_2[(cap_2.is_cntlreg == i) & (cap_2.value > 0)]
    tech = []
    labels = []
    for ii in set(df.k):
        labels.append(ii)
        df2 = cap_2[(cap_2.is_cntlreg == i) & (cap_2.k == ii)]
        tech.append(list(df2.sort_values(by='r')['value'].values))

    tech = np.array(tech)
    sort_order = tech[:, 1].argsort()[::-1]
    labels = [labels[i] for i in sort_order]
    tech = tech[sort_order]

    fig, ax = plt.subplots()
    ax.grid(which='major', axis='both', linestyle='--')
    ax.stackplot(np.array(list(carbon.values()))*100, tech, labels=labels)
    ax.legend(loc='lower left', frameon=True)
    plt.xlabel(x_title)
    plt.ylabel('Generation Capacity (MW)')
    plt.ylim(0, 30000)
    plt.tight_layout()
    plt.savefig(results_path + '/summary_plots/agg_capacity_not_cntlreg.png', dpi=600, format='png')
