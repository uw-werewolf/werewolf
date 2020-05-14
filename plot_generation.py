import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axis as axes
import seaborn as sns
import style_parameters as sp
import os
import filesys as fs
import gmsxfr

pd.plotting.register_matplotlib_converters()


if __name__ == "__main__":

    #
    #
    # get model results
    gdx = gmsxfr.GdxContainer(fs.gams_sysdir, "final_results.gdx")
    gdx.rgdx()

    carbon = {
        i: gdx.to_dict("frac_r")["elements"][i]
        if gdx.to_dict("frac_r")["elements"][i] > np.finfo(float).tiny
        else 0
        for i in gdx.to_dict("frac_r")["elements"]
    }

    gen = gdx.to_dataframe("y_ikr")["elements"]
    gen.loc[gen[gen["L"] <= np.finfo(float).tiny].index, "L"] = 0

    gen["r"] = gen["r"].map(carbon)
    gen["L"] = gen["L"] / 1000  # convert to GWh
    gen["r"] = gen["r"] * 100  # convert to %

    gen["is_cntlreg"] = gen["i"].isin(gdx.to_dict("cntlreg")["elements"])
    gen["is_fossil"] = gen["k"].isin(gdx.to_dict("fossil")["elements"])

    #
    #
    # plot aggregate generation for fossil and renew by policy scenario and cntlreg
    gen_2 = gen.groupby(["is_fossil", "is_cntlreg", "r"]).sum()
    gen_2.reset_index(drop=False, inplace=True)

    # label mapping
    fossil_map = {True: "Fossil", False: "Renew"}
    gen_2["is_fossil"] = gen_2["is_fossil"].map(fossil_map)

    cntlreg_map = {True: "Cntl Reg", False: "Not Cntl Reg"}
    gen_2["is_cntlreg"] = gen_2["is_cntlreg"].map(cntlreg_map)

    n_plt = list(set(zip(gen_2.is_fossil, gen_2.is_cntlreg)))

    plt.style.use(["seaborn-white", "werewolf_style.mplstyle"])

    fig, ax = plt.subplots()
    y_div = 25000
    for n, (i, j) in enumerate(n_plt):

        df = gen_2[(gen_2.is_fossil == i) & (gen_2.is_cntlreg == j)]

        ax.plot(
            df["r"],
            df["L"],
            visible=True,
            color=sp.cm_fossil[(i, j)],
            linewidth=1,
            label=f"{i} ({j})",
        )

        # plt.suptitle('super title here')
        plt.xlabel(gdx.symText["x_title"])
        plt.ylabel("Total Actual Generation (GWh)")
        plt.tight_layout()
        plt.ylim(0, y_div * (max(gen_2["L"]) // y_div + 1))
        ax.grid(which="major", axis="both", linestyle="--")
        ax.legend(loc="best", frameon=True)

    plt.savefig(
        os.path.join(
            gdx.symText["results_folder"], "summary_plots", "agg_generation.png"
        ),
        dpi=600,
        format="png",
    )

    #
    #
    # plot disaggregated generation for fossil and renew by policy scenario for cntlreg ONLY
    gen["is_solar"] = gen["k"].isin(gdx.to_dict("all_solar")["elements"])
    gen["is_wind"] = gen["k"].isin(gdx.to_dict("all_wind")["elements"])
    gen["is_nuclear"] = gen["k"].isin(gdx.to_dict("nuclear")["elements"])
    gen["is_hydro"] = gen["k"].isin(gdx.to_dict("hydro")["elements"])

    gen["k"] = gen["k"].map(sp.gen_map)
    if sum(gen["k"].isnull()) != 0:
        raise Exception("incomplete generation mapping from style_parameters")

    gen_2 = gen.groupby(["k", "is_cntlreg", "r"]).sum()
    gen_2.reset_index(drop=False, inplace=True)

    include_techs = (
        gen_2[gen_2["is_cntlreg"] == True].groupby(["k", "is_cntlreg"]).sum()
    )
    include_techs.reset_index(drop=False, inplace=True)
    gen_2["include"] = gen_2["k"].isin(include_techs[include_techs["L"] > 0].k)

    n_plt = list(set(gen_2[gen_2["include"] == True].k))
    n_plt.sort()

    plt.style.use(["seaborn-white", "werewolf_style.mplstyle"])

    fig, ax = plt.subplots()
    for n, i in enumerate(n_plt):
        df = gen_2[(gen_2.is_cntlreg == True) & (gen_2.k == i)]

        ax.plot(
            df["r"], df["L"], visible=True, color=sp.cm_gen[i], linewidth=1, label=i
        )

    # plt.suptitle('super title here')
    plt.xlabel(gdx.symText["x_title"])
    plt.ylabel("Total Actual Generation (GWh)")
    plt.tight_layout()
    plt.ylim(0, y_div * (max(gen_2[gen_2["is_cntlreg"] == True]["L"]) // y_div + 1))
    ax.grid(which="major", axis="both", linestyle="--")
    ax.legend(loc="best", frameon=True)
    plt.savefig(
        os.path.join(
            gdx.symText["results_folder"], "summary_plots", "agg_generation_cntlreg.png"
        ),
        dpi=600,
        format="png",
    )
