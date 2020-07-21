import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axis as axes
import seaborn as sns
import style_parameters as sp
import os
import gmsxfr
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
    gdx.rgdx(
        [
            "frac_r",
            "y_ikr",
            "cntlreg",
            "fossil",
            "all_solar",
            "all_wind",
            "nuclear",
            "hydro",
            "capacity",
        ]
    )

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
        plt.xlabel(x_title)
        plt.ylabel("Total Actual Generation (GWh)")
        plt.tight_layout()
        plt.ylim(0, y_div * (max(gen_2["L"]) // y_div + 1))
        ax.grid(which="major", axis="both", linestyle="--")
        ax.legend(loc="upper right", frameon=True, prop={"size": 6})

    plt.savefig(
        os.path.join(args.output, "agg_generation.png"), dpi=600, format="png",
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
    plt.xlabel(x_title)
    plt.ylabel("Total Actual Generation (GWh)")
    plt.tight_layout()
    plt.ylim(0, y_div * (max(gen_2[gen_2["is_cntlreg"] == True]["L"]) // y_div + 1))
    ax.grid(which="major", axis="both", linestyle="--")
    ax.legend(loc="upper right", frameon=True, prop={"size": 6})
    plt.savefig(
        os.path.join(args.output, "agg_generation_cntlreg.png"), dpi=600, format="png",
    )

    #
    #
    # plot disaggregated capacity factor for fossil and renew by policy scenario for all regions
    gen["i"] = gen["i"].map(sp.region_map)
    if sum(gen["i"].isnull()) != 0:
        raise Exception("incomplete region mapping from style_parameters")

    cap = gdx.to_dataframe("capacity")["elements"].copy()
    cap.loc[cap[cap["L"] <= np.finfo(float).tiny].index, "L"] = 0
    cap["r"] = cap["r"].map(carbon)

    cap["is_cntlreg"] = cap["i"].isin(gdx.to_dict("cntlreg")["elements"])
    cap["is_fossil"] = cap["k"].isin(gdx.to_dict("fossil")["elements"])

    cap["is_solar"] = cap["k"].isin(gdx.to_dict("all_solar")["elements"])
    cap["is_wind"] = cap["k"].isin(gdx.to_dict("all_wind")["elements"])
    cap["is_nuclear"] = cap["k"].isin(gdx.to_dict("nuclear")["elements"])
    cap["is_hydro"] = cap["k"].isin(gdx.to_dict("hydro")["elements"])

    cap["k"] = cap["k"].map(sp.gen_map)
    if sum(cap["k"].isnull()) != 0:
        raise Exception("incomplete generation mapping from style_parameters")

    cap["i"] = cap["i"].map(sp.region_map)
    if sum(cap["i"].isnull()) != 0:
        raise Exception("incomplete region mapping from style_parameters")

    cap_2 = cap.groupby(["k", "i", "r"]).sum()
    cap_2.reset_index(drop=False, inplace=True)

    gen_2 = gen.groupby(["k", "i", "r"]).sum()
    gen_2.reset_index(drop=False, inplace=True)

    gen_2.set_index(["k", "i", "r"], inplace=True)
    gen_2["capacity"] = cap_2.set_index(["k", "i", "r"])["L"]
    gen_2["cf"] = round(gen_2["L"] * 1000 / (gen_2["capacity"] * 8760), 4)
    gen_2.fillna(0, inplace=True)
    gen_2.reset_index(drop=False, inplace=True)

    n_plt = list(set(zip(gen_2.k, gen_2.i)))
    n_plt.sort()

    plt.style.use(["seaborn-white", "werewolf_style.mplstyle"])

    for region in set(gen_2["i"]):
        fig, ax = plt.subplots()
        df = gen_2[(gen_2.i == region) & (gen_2.L > 0)]

        for tech in set(df.k):
            df = gen_2[(gen_2.i == region) & (gen_2.k == tech)]
            ax.plot(
                df["r"],
                df["cf"],
                visible=True,
                color=sp.cm_gen[tech],
                linewidth=1,
                label=tech,
            )

        # plt.suptitle('super title here')
        plt.xlabel(x_title)
        plt.ylabel("Capacity Factor (unitless)")
        plt.tight_layout()
        plt.ylim(0, 1.05)
        ax.grid(which="major", axis="both", linestyle="--")
        ax.legend(loc="upper right", frameon=True, prop={"size": 6})
        plt.savefig(
            os.path.join(args.output, f"capacity_factor_region_{region}.png",),
            dpi=600,
            format="png",
        )
