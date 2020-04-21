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
    TotalCost = gdxin.rgdx(name='TotalCost')
    ExpCost_r = gdxin.rgdx(name='ExpCost_r')
    ExpCost_ir = gdxin.rgdx(name='ExpCost_ir')
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

    #
    #
    # plot aggregate costs for policy scenario
    plt.style.use(['seaborn-white', 'werewolf_style.mplstyle'])

    fig, ax = plt.subplots()
    dollars = [i/1e6 for i in TotalCost['values'].values()]  # convert to millions of dollars
    ax.plot(np.array(list(carbon.values()))*100, dollars,
            visible=True)

    # plt.suptitle('super title here')
    plt.xlabel(x_title)
    plt.ylabel('Total Costs in Million USD (M$)')
    # plt.ylim(0,10)
    plt.tight_layout()
    ax.grid(which='major', axis='both', linestyle='--')
    plt.savefig(results_path + '/summary_plots/total_costs.png', dpi=600, format='png')

    #
    #
    # plot disaggregated system costs for policy scenario
    syscosts = pd.DataFrame(data=ExpCost_r['values'].keys(), columns=ExpCost_r['domain'])
    syscosts['value'] = ExpCost_r['values'].values()
    syscosts['value'] = syscosts['value'] / 1e6  # convert to millions of USD
    syscosts.loc[syscosts[syscosts['value'] < np.finfo(float).tiny].index, 'value'] = 0
    syscosts['r'] = syscosts['r'].map(carbon)
    syscosts['r'] = syscosts['r']*100

    n_plt = list(set(syscosts.ctype))

    label_map = {'Invest': 'Investment', 'Maintain': 'Maintenance',
                 'Operate': 'Operational', 'LostLoad': 'Cost of Lost Load'}

    fig, ax = plt.subplots()
    for i in n_plt:
        df = syscosts[syscosts.ctype == i]

        if sum(syscosts.value == 0) != len(df):
            ax.plot(df.r, df.value,
                    visible=True,
                    label=label_map[i])

            # plt.suptitle('super title here')
            plt.xlabel(x_title)
            plt.ylabel('Cost in Million USD (M$)')
            # plt.ylim(0,10)
            ax.legend(loc='best', frameon=True)
            plt.tight_layout()
            ax.grid(which='major', axis='both', linestyle='--')
    plt.savefig(results_path + '/summary_plots/system_costs.png', dpi=600, format='png')

    #
    #
    # plot disaggregated costs by region for policy scenario
    syscosts = pd.DataFrame(data=ExpCost_ir['values'].keys(), columns=ExpCost_ir['domain'])
    syscosts['value'] = ExpCost_ir['values'].values()
    syscosts['value'] = syscosts['value'] / 1e6  # convert to millions of USD
    syscosts.loc[syscosts[syscosts['value'] < np.finfo(float).tiny].index, 'value'] = 0
    syscosts['r'] = syscosts['r'].map(carbon)
    syscosts['r'] = syscosts['r'] * 100

    syscosts['is_cntlreg'] = [i in cntlreg['elements'] for i in syscosts['i']]

    # rename regions
    syscosts.loc[syscosts[syscosts.is_cntlreg == True].index, 'i'] = 'WI'

    # groupby
    syscosts_cir = syscosts.groupby(['i', 'ctype', 'r']).sum()
    syscosts_cir.reset_index(drop=False, inplace=True)

    n_plt = list(set(syscosts.ctype))

    label_map = {'Invest': 'Investment', 'Maintain': 'Maintenance',
                 'Operate': 'Operational', 'LostLoad': 'Cost of Lost Load'}

    for i in n_plt:
        df = syscosts_cir[syscosts_cir.ctype == i]

        fig, ax = plt.subplots()

        if sum(syscosts_cir.value == 0) != len(df):
            for j in set(df.i):
                ax.plot(df[df.i == j].r, df[df.i == j].value,
                        visible=True,
                        label=j)

                # plt.suptitle('super title here')
                plt.xlabel(x_title)
                plt.ylabel(f'{label_map[i]} Costs in Million USD (M$)')
                # plt.ylim(0, 1.25 * max(df[df.is_cntlreg == j].value))
                ax.legend(loc='best', frameon=True)
                plt.tight_layout()
                ax.grid(which='major', axis='both', linestyle='--')
        plt.savefig(results_path +
                    f'/summary_plots/{i.lower()}_costs_by_region.png', dpi=600, format='png')
