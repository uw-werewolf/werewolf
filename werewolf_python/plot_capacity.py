import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axis as axes
import seaborn as sns
import gmsxfr
import style_parameters as sp
import os
import argparse

pd.plotting.register_matplotlib_converters()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--gams_sysdir", dest="gams_sysdir", default=None, type=str)
    parser.add_argument("--data_repo", dest="data_repo", default=None, type=str)
    parser.add_argument("--output", dest="output", default=None, type=str)

    # parser.set_defaults(
    #     gams_sysdir=os.path.join("/", "Applications", "GAMS30.3", "Resources", "sysdir")
    # )
    # parser.set_defaults(
    #     data_repo=os.path.join(
    #         "~/",
    #         "Projects",
    #         "werewolf",
    #         "gams",
    #         "werewolf",
    #         "output",
    #         "scenario_label_1",
    #         "data_repo",
    #     )
    # )
    #
    # parser.set_defaults(
    #     output=os.path.join(
    #         "~/",
    #         "Projects",
    #         "werewolf",
    #         "gams",
    #         "werewolf",
    #         "output",
    #         "scenario_label_1",
    #     )
    # )

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
    gdx.rgdx(["frac_r", "capacity", "cntlreg"])

    carbon = {
        i: gdx.to_dict("frac_r")["elements"][i]
        if gdx.to_dict("frac_r")["elements"][i] > np.finfo(float).tiny
        else 0
        for i in gdx.to_dict("frac_r")["elements"]
    }

    cap = gdx.to_dataframe("capacity")["elements"].copy()
    cap.loc[cap[cap["L"] <= np.finfo(float).tiny].index, "L"] = 0
    cap["r"] = cap["r"].map(carbon)

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

        df.to_csv(os.path.join(args.output, f"gen_cap_cntlreg_{cr}.csv"))

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
            np.array(list(carbon.values())),
            tech,
            labels=labels,
            colors=[sp.cm_gen[i] for i in labels],
            alpha=0.7,
            edgecolor="k",
            linewidth=0.5,
        )

        ax.legend(loc="upper right", frameon=True, prop={"size": 6})
        plt.xlabel(x_title)
        plt.title(f"Generation Capacity for Control Region -- {cr}")
        plt.ylabel("Generation Capacity (MW)")
        plt.ylim(
            0, y_div * (sum(cap_2[cap_2["r"] == max(cap_2["r"])]["L"]) // y_div + 1)
        )
        plt.tight_layout()
        plt.savefig(
            os.path.join(args.output, f"agg_capacity_cntlreg_{cr}.png",),
            dpi=600,
            format="png",
        )

    # separate plots for each not_cntlreg
    for cr in set(cap[cap["is_cntlreg"] == False].i):

        cap_2 = cap[cap["i"] == cr].groupby(["i", "k", "r"]).sum()
        cap_2.reset_index(drop=False, inplace=True)

        df = cap_2[(cap_2["i"] == cr) & (cap_2["L"] > 0)]

        df.to_csv(os.path.join(args.output, f"gen_cap_not_cntlreg_{cr}.csv"))

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
            np.array(list(carbon.values())),
            tech,
            labels=labels,
            colors=[sp.cm_gen[i] for i in labels],
            alpha=0.7,
            edgecolor="k",
            linewidth=0.5,
        )

        ax.legend(loc="upper right", frameon=True, prop={"size": 6})
        plt.xlabel(x_title)
        plt.title(f"Generation Capacity for Non-Control Region -- {cr}")
        plt.ylabel("Generation Capacity (MW)")
        plt.ylim(
            0, y_div * (sum(cap_2[cap_2["r"] == max(cap_2["r"])]["L"]) // y_div + 1)
        )
        plt.tight_layout()
        plt.savefig(
            os.path.join(args.output, f"agg_capacity_not_cntlreg_{cr}.png",),
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
        np.array(list(carbon.values())),
        tech,
        labels=labels,
        colors=[sp.cm_gen[i] for i in labels],
        alpha=0.7,
        edgecolor="k",
        linewidth=0.5,
    )

    ax.legend(loc="upper right", frameon=True, prop={"size": 6})
    plt.xlabel(x_title)
    plt.title(f"Aggregate Generation Capacity for All Non-Control Regions")
    plt.ylabel("Generation Capacity (MW)")
    plt.ylim(0, y_div * (sum(cap_2[cap_2["r"] == max(cap_2["r"])]["L"]) // y_div + 1))
    plt.tight_layout()
    plt.savefig(
        os.path.join(args.output, f"agg_capacity_not_cntlreg_all.png",),
        dpi=600,
        format="png",
    )
