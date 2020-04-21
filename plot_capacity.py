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

    # colorPalette = sns.color_palette(palette='bright', n_colors=len(n_plt))
    # colorDict = dict(zip(n_plt, colorPalette))

    colorDict = {'Solar': (0.00784313725490196, 0.24313725490196078, 1.0),
                 'Battery_slow': (1.0, 0.48627450980392156, 0.0),
                 'Fuel_Cell': (0.10196078431372549, 0.788235294117647, 0.2196078431372549),
                 'Tires': (0.9098039215686274, 0.0, 0.043137254901960784),
                 'OG_Steam': (0.5450980392156862, 0.16862745098039217, 0.8862745098039215),
                 'IGCC': (0.6235294117647059, 0.2823529411764706, 0.0),
                 'Fossil_Waste': (0.9450980392156862, 0.2980392156862745, 0.7568627450980392),
                 'Hydro': (0.6392156862745098, 0.6392156862745098, 0.6392156862745098),
                 'Municipal_Solid_Waste': (1.0, 0.7686274509803922, 0.0),
                 'Non_Fossil_Waste': (0.0, 0.8431372549019608, 1.0),
                 'Combined_Cycle': (0.00784313725490196, 0.24313725490196078, 1.0),
                 'Battery_med': (1.0, 0.48627450980392156, 0.0),
                 'Combustion_Turbine': (0.10196078431372549,
                                        0.788235294117647,
                                        0.2196078431372549),
                 'Nuclear': (0.9098039215686274, 0.0, 0.043137254901960784),
                 'Geothermal': (0.5450980392156862, 0.16862745098039217, 0.8862745098039215),
                 'Biomass': (0.6235294117647059, 0.2823529411764706, 0.0),
                 'Battery_fast': (0.9450980392156862, 0.2980392156862745, 0.7568627450980392),
                 'Landfill_Gas': (0.6392156862745098, 0.6392156862745098, 0.6392156862745098),
                 'Coal_Steam': (1.0, 0.7686274509803922, 0.0),
                 'Wind': (0.0, 0.8431372549019608, 1.0)}

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
    ax.stackplot(np.array(list(carbon.values()))*100, tech,
                 labels=labels, colors=[colorDict[i] for i in labels])
    ax.legend(loc='lower left', frameon=True)
    plt.xlabel(x_title)
    plt.ylabel('Generation Capacity (MW)')
    plt.ylim(0, 30000)
    plt.tight_layout()
    plt.savefig('agg_capacity_cntlreg.png', dpi=600, format='png')
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
    ax.stackplot(np.array(list(carbon.values()))*100, tech,
                 labels=labels, colors=[colorDict[i] for i in labels])
    ax.legend(loc='lower left', frameon=True)
    plt.xlabel(x_title)
    plt.ylabel('Generation Capacity (MW)')
    plt.ylim(0, 30000)
    plt.tight_layout()
    plt.savefig(results_path + '/summary_plots/agg_capacity_not_cntlreg.png', dpi=600, format='png')
