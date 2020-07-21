import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axis as axes
import seaborn as sns
import os
import gmsxfr
import style_parameters as sp
import argparse

pd.plotting.register_matplotlib_converters()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--gams_sysdir", dest="gams_sysdir", default=None, type=str)
    parser.add_argument("--data_repo", dest="data_repo", default=None, type=str)
    parser.add_argument("--output", dest="output", default=None, type=str)

    # parser.set_defaults(gams_sysdir="some path here")
    # parser.set_defaults(data_repo="some path here")

    args = parser.parse_args()

    #
    #
    # get model results
    gdx = gmsxfr.GdxContainer(
        args.gams_sysdir, os.path.join(args.data_repo, "solve_mode.gdx")
    )
    gdx.rgdx(["x_title"])
    x_title = gdx.to_dict("x_title")["text"]

    gdx = gmsxfr.GdxContainer(
        args.gams_sysdir, os.path.join(args.data_repo, "final_results.gdx")
    )
    gdx.rgdx(["frac_r", "TotalCarbon_ir", "cntlreg"])

    carbon = {
        i: gdx.to_dict("frac_r")["elements"][i]
        if gdx.to_dict("frac_r")["elements"][i] > np.finfo(float).tiny
        else 0
        for i in gdx.to_dict("frac_r")["elements"]
    }

    emis = gdx.to_dataframe("TotalCarbon_ir")["elements"].copy()
    emis.loc[emis[emis["L"] <= np.finfo(float).tiny].index, "L"] = 0
    emis["r"] = emis["r"].map(carbon)

    emis["is_cntlreg"] = emis["i"].isin(gdx.to_dict("cntlreg")["elements"])

    emis["i"] = emis["i"].map(sp.region_map)
    if sum(emis["i"].isnull()) != 0:
        raise Exception("incomplete region mapping from style_parameters")

    #
    #
    # plot aggregate emissions by region for policy scenario
    emis_2 = emis.groupby(["is_cntlreg", "r"]).sum()
    emis_2.reset_index(drop=False, inplace=True)

    n_plt = [True, False]
    labels = dict(zip([False, True], ["Not Cntl Reg", "Cntl Reg"]))

    plt.style.use(["seaborn-white", "werewolf_style.mplstyle"])

    y_div = 25
    fig, ax = plt.subplots()
    for n, i in enumerate(n_plt):
        df = emis_2[emis_2.is_cntlreg == i]

        ax.plot(
            df["r"],
            df["L"],
            visible=True,
            color=sp.cm_cntlreg[i],
            linewidth=1,
            label=labels[i],
        )

    # plt.suptitle('super title here')
    plt.xlabel(x_title)
    plt.ylabel("Total Carbon Emissions (Million Metric Tons CO2)")
    plt.ylim(0, y_div * (max(emis_2["L"]) // y_div + 1))
    plt.tight_layout()
    ax.grid(which="major", axis="both", linestyle="--")
    ax.legend(loc="upper right", frameon=True, prop={"size": 6})

    plt.savefig(
        os.path.join(args.output, "agg_emissions.png"), dpi=600, format="png",
    )
