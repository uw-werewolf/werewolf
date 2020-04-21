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

    import_ibr = gdxin.rgdx(name='import_ibr')
    import_ir = gdxin.rgdx(name='import_ir')
    export_ibr = gdxin.rgdx(name='export_ibr')
    export_ir = gdxin.rgdx(name='export_ir')

    cntlreg = gdxin.rgdx(name='cntlreg')
    not_cntlreg = gdxin.rgdx(name='not_cntlreg')
    frac_r = gdxin.rgdx(name='frac_r')
    r = gdxin.rgdx(name='r')

    results_path = gdxin.rgdx(name='results_folder')
    results_path = results_path['text']

    x_title = gdxin.rgdx(name='x_title')
    x_title = x_title['text']

    carbon = {i: frac_r['values'][i] if frac_r['values'][i] >
              np.finfo(float).tiny else 0 for i in frac_r['values']}

    imports = pd.DataFrame(data=import_ir['values'].keys(), columns=import_ir['domain'])
    imports['value'] = import_ir['values'].values()
    imports.loc[imports[imports['value'] < np.finfo(float).tiny].index, 'value'] = 0
    imports['r'] = imports['r'].map(carbon)
    imports['r'] = imports['r'] * 100  # convert to %

    exports = pd.DataFrame(data=export_ir['values'].keys(), columns=export_ir['domain'])
    exports['value'] = export_ir['values'].values()
    exports.loc[exports[exports['value'] < np.finfo(float).tiny].index, 'value'] = 0
    exports['r'] = exports['r'].map(carbon)
    exports['r'] = exports['r'] * 100  # convert to %

    exim = imports.set_index(['i', 'r']).copy()
    exim.rename(columns={'value': 'imports'}, inplace=True)
    exim['exports'] = exports.set_index(['i', 'r']).value
    exim['net'] = exim['imports'] - exim['exports']
    exim.reset_index(drop=False, inplace=True)

    exim = exim[exim.net != 0].copy()

    #
    #
    # plot ex/imports by region for policy scenario
    n_plt = list(set(exim.i))

    colorPalette = sns.color_palette(palette='bright', n_colors=len(n_plt))
    colorDict = dict(zip(n_plt, colorPalette))

    plt.style.use(['seaborn-white', 'werewolf_style.mplstyle'])

    # plot for cntlreg
    fig, ax = plt.subplots()
    for n, i in enumerate(n_plt):
        df = exim[exim.i == i]

        ax.plot(df['r'], df['net'],
                visible=True,
                color=colorDict[i],
                linewidth=1,
                label=i)

        ax.plot(df['r'], [0 for _ in range(len(carbon))],
                visible=True,
                color='black',
                linewidth=2,
                linestyle='--')

        # plt.suptitle('super title here')
        plt.xlabel(x_title)
        plt.ylabel('Net Imports to Wisconsin (MW)')
        plt.tight_layout()
        plt.ylim(-5000, 20000)
        ax.grid(which='major', axis='both', linestyle='--')
        ax.legend(loc='best', frameon=True)

    plt.savefig(results_path + '/summary_plots/agg_exim.png', dpi=600, format='png')
