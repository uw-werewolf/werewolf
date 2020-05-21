import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axis as axes
import seaborn as sns
import os
import gmsxfr
import style_parameters as sp
import filesys as fs

pd.plotting.register_matplotlib_converters()


if __name__ == "__main__":

    #
    #
    # get model results
    gdx = gmsxfr.GdxContainer(fs.gams_sysdir, "final_results.gdx")
    gdx.rgdx()

    TotalCost = gdx.to_dict("TotalCost")
    ExpCost_r = gdx.to_dataframe("ExpCost_r")
    ExpCost_ir = gdx.to_dataframe("ExpCost_ir")

    carbon = {
        i: gdx.to_dict("frac_r")["elements"][i]
        if gdx.to_dict("frac_r")["elements"][i] > np.finfo(float).tiny
        else 0
        for i in gdx.to_dict("frac_r")["elements"]
    }

    #
    #
    # plot aggregate costs for policy scenario
    plt.style.use(["seaborn-white", "werewolf_style.mplstyle"])

    fig, ax = plt.subplots()
    y_div = 500
    dollars = [
        i / 1e6 for i in TotalCost["elements"].values()
    ]  # convert to millions of dollars
    ax.plot(np.array(list(carbon.values())) * 100, dollars, visible=True)

    # plt.suptitle('super title here')
    plt.xlabel(gdx.symText["x_title"])
    plt.ylabel("Total Costs (M$)")
    plt.ylim(-y_div * (-min(dollars) // y_div + 1), y_div * (max(dollars) // y_div + 1))
    plt.tight_layout()
    ax.grid(which="major", axis="both", linestyle="--")
    plt.savefig(
        os.path.join(gdx.symText["results_folder"], "summary_plots", "total_costs.png"),
        dpi=600,
        format="png",
    )

    #
    #
    # plot disaggregated system costs for policy scenario
    syscosts = ExpCost_r["elements"].copy()
    syscosts["L"] = syscosts["L"] / 1e6  # convert to millions of USD
    syscosts.loc[syscosts[syscosts["L"] <= np.finfo(float).tiny].index, "L"] = 0
    syscosts["r"] = syscosts["r"].map(carbon)
    syscosts["r"] = syscosts["r"] * 100

    syscosts["ctype"] = syscosts["ctype"].map(sp.cost_map)

    n_plt = list(set(syscosts.ctype))

    fig, ax = plt.subplots()
    for i in n_plt:
        df = syscosts[syscosts.ctype == i]

        if sum(syscosts.L == 0) != len(df):
            ax.plot(df.r, df.L, visible=True, color=sp.cm_cost[i], label=i)

        # plt.suptitle('super title here')
        plt.xlabel(gdx.symText["x_title"])
        plt.ylabel("Cost (M$)")
        plt.ylim(
            -y_div * (-min(syscosts["L"]) // y_div + 1),
            y_div * (max(syscosts["L"]) // y_div + 1),
        )
        ax.legend(loc="upper right", frameon=True, prop={"size": 6})
        plt.tight_layout()
        ax.grid(which="major", axis="both", linestyle="--")
    plt.savefig(
        os.path.join(
            gdx.symText["results_folder"], "summary_plots", "system_costs.png"
        ),
        dpi=600,
        format="png",
    )

    #
    #
    # plot disaggregated costs by region for policy scenario
    syscosts = ExpCost_ir["elements"].copy()
    syscosts["L"] = syscosts["L"] / 1e6  # convert to millions of USD
    syscosts.loc[syscosts[syscosts["L"] <= np.finfo(float).tiny].index, "L"] = 0
    syscosts["r"] = syscosts["r"].map(carbon)
    syscosts["r"] = syscosts["r"] * 100

    syscosts["is_cntlreg"] = syscosts["i"].isin(gdx.to_dict("cntlreg")["elements"])

    # rename
    syscosts["i"] = syscosts["i"].map(sp.region_map)
    syscosts["ctype"] = syscosts["ctype"].map(sp.cost_map)

    # groupby
    syscosts_cir = syscosts.groupby(["i", "ctype", "r"]).sum()
    syscosts_cir.reset_index(drop=False, inplace=True)

    n_plt = list(set(syscosts.ctype))

    for i in n_plt:
        df = syscosts_cir[syscosts_cir.ctype == i]

        fig, ax = plt.subplots()

        if sum(syscosts_cir.L == 0) != len(df):
            for j in set(df.i):
                ax.plot(
                    df[df.i == j].r,
                    df[df.i == j].L,
                    visible=True,
                    color=sp.cm_region[j],
                    label=j,
                )

            # plt.suptitle('super title here')
            plt.xlabel(gdx.symText["x_title"])
            plt.ylabel(f"{i} (M$)")
            plt.ylim(
                -y_div * (-min(df["L"]) // y_div + 1),
                y_div * (max(df["L"]) // y_div + 1),
            )
            ax.legend(loc="upper right", frameon=True, prop={"size": 6})
            plt.tight_layout()
            ax.grid(which="major", axis="both", linestyle="--")
        plt.savefig(
            os.path.join(
                gdx.symText["results_folder"],
                "summary_plots",
                f"{i.lower()}_by_region.png",
            ),
            dpi=600,
            format="png",
        )
