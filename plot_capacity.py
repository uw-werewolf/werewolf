import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axis as axes
import seaborn as sns
import gmsxfr
import style_parameters as sp
import filesys as fs
import os

pd.plotting.register_matplotlib_converters()


if __name__ == "__main__":

    #
    #
    # get model results
    gdx = gmsxfr.GdxContainer(fs.gams_sysdir, "final_results.gdx")

    # load data from GDX
    gdx.rgdx()

    carbon = {
        i: gdx.to_dict("frac_r")["elements"][i]
        if gdx.to_dict("frac_r")["elements"][i] > np.finfo(float).tiny
        else 0
        for i in gdx.to_dict("frac_r")["elements"]
    }

    cap = gdx.to_dataframe("capacity")["elements"].copy()
    cap.loc[cap[cap["L"] <= np.finfo(float).tiny].index, "L"] = 0
    cap["r"] = cap["r"].map(carbon)
    cap["r"] = cap["r"] * 100  # convert to %

    cap["is_cntlreg"] = cap["i"].isin(gdx.to_dict("cntlreg")["elements"])

    cap["i"] = cap["i"].map(sp.region_map)
    if sum(cap["i"].isnull()) != 0:
        raise Exception("incomplete region mapping from style_parameters")

    cap["k"] = cap["k"].map(sp.gen_map)
    if sum(cap["k"].isnull()) != 0:
        raise Exception("incomplete generator mapping from style_parameters")

    plt.style.use(["seaborn-white", "werewolf_style.mplstyle"])
    y_div = 20000

    # separate plots for all possible cntlreg
    for cr in set(cap[cap["is_cntlreg"] == True].i):

        cap_2 = cap[cap["i"] == cr].groupby(["i", "k", "r"]).sum()
        cap_2.reset_index(drop=False, inplace=True)

        df = cap_2[(cap_2["i"] == cr) & (cap_2["L"] > 0)]
        tech = []
        labels = []
        for ii in set(df.k):
            labels.append(ii)
            df2 = cap_2[cap_2.k == ii]
            tech.append(list(df2.sort_values(by="r")["L"].values))

        tech = np.array(tech)
        sort_order = tech[:, 1].argsort()[::-1]
        labels = [labels[i] for i in sort_order]
        tech = tech[sort_order]

        fig, ax = plt.subplots()
        ax.grid(which="major", axis="both", linestyle="--")
        ax.stackplot(
            np.array(list(carbon.values())) * 100,
            tech,
            labels=labels,
            colors=[sp.cm_gen[i] for i in labels],
            alpha=0.7,
            edgecolor="k",
            linewidth=0.5,
        )

        ax.legend(loc="upper right", frameon=True, prop={"size": 6})
        plt.xlabel(gdx.symText["x_title"])
        plt.title(f"Generation Capacity for Control Region -- {cr}")
        plt.ylabel("Generation Capacity (MW)")
        plt.ylim(
            0, y_div * (sum(cap_2[cap_2["r"] == max(cap_2["r"])]["L"]) // y_div + 1)
        )
        plt.tight_layout()
        plt.savefig(
            os.path.join(
                gdx.symText["results_folder"],
                "summary_plots",
                f"agg_capacity_cntlreg_{cr}.png",
            ),
            dpi=600,
            format="png",
        )

    # separate plots for each not_cntlreg
    for cr in set(cap[cap["is_cntlreg"] == False].i):

        cap_2 = cap[cap["i"] == cr].groupby(["i", "k", "r"]).sum()
        cap_2.reset_index(drop=False, inplace=True)

        df = cap_2[(cap_2["i"] == cr) & (cap_2["L"] > 0)]
        tech = []
        labels = []
        for ii in set(df.k):
            labels.append(ii)
            df2 = cap_2[cap_2.k == ii]
            tech.append(list(df2.sort_values(by="r")["L"].values))

        tech = np.array(tech)
        sort_order = tech[:, 1].argsort()[::-1]
        labels = [labels[i] for i in sort_order]
        tech = tech[sort_order]

        fig, ax = plt.subplots()
        ax.grid(which="major", axis="both", linestyle="--")
        ax.stackplot(
            np.array(list(carbon.values())) * 100,
            tech,
            labels=labels,
            colors=[sp.cm_gen[i] for i in labels],
            alpha=0.7,
            edgecolor="k",
            linewidth=0.5,
        )

        ax.legend(loc="upper right", frameon=True, prop={"size": 6})
        plt.xlabel(gdx.symText["x_title"])
        plt.title(f"Generation Capacity for Non-Control Region -- {cr}")
        plt.ylabel("Generation Capacity (MW)")
        plt.ylim(
            0, y_div * (sum(cap_2[cap_2["r"] == max(cap_2["r"])]["L"]) // y_div + 1)
        )
        plt.tight_layout()
        plt.savefig(
            os.path.join(
                gdx.symText["results_folder"],
                "summary_plots",
                f"agg_capacity_not_cntlreg_{cr}.png",
            ),
            dpi=600,
            format="png",
        )

    # aggregate plot for all not_cntlreg
    cap_2 = cap[(cap["is_cntlreg"] == False) & (cap["L"] > 0)]
    cap_2 = cap_2.groupby(["k", "r"]).sum()
    cap_2.reset_index(drop=False, inplace=True)

    tech = []
    labels = []
    for ii in set(cap_2.k):
        labels.append(ii)
        df2 = cap_2[(cap_2["k"] == ii)]
        tech.append(list(df2.sort_values(by="r")["L"].values))

    tech = np.array(tech)
    sort_order = tech[:, 1].argsort()[::-1]
    labels = [labels[i] for i in sort_order]
    tech = tech[sort_order]

    fig, ax = plt.subplots()
    ax.grid(which="major", axis="both", linestyle="--")
    ax.stackplot(
        np.array(list(carbon.values())) * 100,
        tech,
        labels=labels,
        colors=[sp.cm_gen[i] for i in labels],
        alpha=0.7,
        edgecolor="k",
        linewidth=0.5,
    )

    ax.legend(loc="upper right", frameon=True, prop={"size": 6})
    plt.xlabel(gdx.symText["x_title"])
    plt.title(f"Aggregate Generation Capacity for All Non-Control Regions")
    plt.ylabel("Generation Capacity (MW)")
    plt.ylim(0, y_div * (sum(cap_2[cap_2["r"] == max(cap_2["r"])]["L"]) // y_div + 1))
    plt.tight_layout()
    plt.savefig(
        os.path.join(
            gdx.symText["results_folder"],
            "summary_plots",
            f"agg_capacity_not_cntlreg_all.png",
        ),
        dpi=600,
        format="png",
    )
