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
    cntlreg = gdxin.rgdx(name='cntlreg')
    not_cntlreg = gdxin.rgdx(name='not_cntlreg')
    totalcarbon = gdxin.rgdx(name='TotalCarbon_ir')
    frac_r = gdxin.rgdx(name='frac_r')
    r = gdxin.rgdx(name='r')

    results_path = gdxin.rgdx(name='results_folder')
    results_path = results_path['text']

    x_title = gdxin.rgdx(name='x_title')
    x_title = x_title['text']

    carbon = {i: frac_r['values'][i] if frac_r['values'][i] >
              np.finfo(float).tiny else 0 for i in frac_r['values']}

    emis = pd.DataFrame(data=totalcarbon['values'].keys(), columns=totalcarbon['domain'])
    emis['value'] = totalcarbon['values'].values()
    emis.loc[emis[emis['value'] < np.finfo(float).tiny].index, 'value'] = 0
    emis['r'] = emis['r'].map(carbon)
    emis['r'] = emis['r'] * 100  # convert to %
    emis['is_cntlreg'] = [i in cntlreg['elements'] for i in emis['i']]

    #
    #
    # plot aggregate emissions by region for policy scenario
    emis_2 = emis.groupby(['is_cntlreg', 'r']).sum()
    emis_2.reset_index(drop=False, inplace=True)

    n_plt = list(set(emis_2.is_cntlreg))
    labels = dict(zip(n_plt, ['Not Cntl Reg', 'Cntl Reg']))

    colorPalette = sns.color_palette(palette='bright', n_colors=len(n_plt))
    colorDict = dict(zip(n_plt, colorPalette))

    plt.style.use(['seaborn-white', 'werewolf_style.mplstyle'])

    fig, ax = plt.subplots()
    for n, i in enumerate(n_plt):
        df = emis_2[emis_2.is_cntlreg == i]

        ax.plot(df['r'], df['value'],
                visible=True,
                color=colorDict[i],
                linewidth=1,
                label=labels[i])

        # plt.suptitle('super title here')
        plt.xlabel(x_title)
        plt.ylabel('Total Carbon Emissions (Million Metric Tons CO2)')
        plt.ylim(0)
        plt.tight_layout()
        ax.grid(which='major', axis='both', linestyle='--')
        ax.legend(loc='best', frameon=True)

    plt.savefig(results_path + '/summary_plots/agg_emissions.png', dpi=600, format='png')
