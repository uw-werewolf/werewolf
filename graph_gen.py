import gdxtools as gt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axis as axes
import seaborn as sns

pd.plotting.register_matplotlib_converters()


def hottick(data, divisor):
    t = (max(data) // divisor**int(np.floor(np.log10(max(data)))) + 1) * \
        divisor**int(np.floor(np.log10(max(data))))
    return t


if __name__ == '__main__':

    filename = 'output_miso_0.gdx'

    gdxin = gt.gdxrw.gdx_reader(filename)

    y = gdxin.rgdx(name='y')

    y_df = pd.DataFrame(data=y['values']['domain'], columns=y['domain'])
    y_df['level'] = y['values']['level']
    y_df.drop(columns=['t'], inplace=True)

    y_piv = pd.pivot_table(y_df, values='level', index=[
                           'a', 'k', 'n'], aggfunc=np.sum, fill_value=0)
    y_piv.reset_index(drop=False, inplace=True)

    plt.style.use(['seaborn-white', 'werewolf_style.mplstyle'])

    colorPalette = sns.color_palette(palette='bright', n_colors=len(y_piv.k.unique()))
    cols = list(y_piv.k.unique())
    cols.sort()

    colorDict = {key: colorPalette[value] for (key, value) in zip(
        cols, [n for n in range(len(y_piv.k.unique()))])}

    fig, ax = plt.subplots()
    for i in y_piv.k.unique():
        ax.plot(y_piv[y_piv['k'] == i].n, y_piv[y_piv['k'] == i].level,
                visible=True,
                color=colorDict[i],
                linewidth=1,
                label=i)

    plt.xlabel('Year')
    plt.ylabel('Generation (MWh)')
    plt.ylim(bottom=0, top=max(y_piv['level']))
    ax = plt.gca()
    ax.grid(which='major', axis='y', linestyle='--')
    ax.legend(loc='best', frameon=True)
    plt.savefig('./test' + '.png', dpi=600, format='png')
    plt.close()
