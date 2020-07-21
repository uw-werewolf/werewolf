import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axis as axes
import seaborn as sns
import gmsxfr
import os
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
    gdx.rgdx(["frac_r", "import_ibr", "import_ir", "export_ibr", "export_ir"])

    carbon = {
        i: gdx.to_dict("frac_r")["elements"][i]
        if gdx.to_dict("frac_r")["elements"][i] > np.finfo(float).tiny
        else 0
        for i in gdx.to_dict("frac_r")["elements"]
    }

    import_ibr = gdx.to_dataframe("import_ibr")
    import_ir = gdx.to_dataframe("import_ir")
    export_ibr = gdx.to_dataframe("export_ibr")
    export_ir = gdx.to_dataframe("export_ir")

    imports = import_ir["elements"].copy()
    imports.loc[imports[imports["L"] <= np.finfo(float).tiny].index, "L"] = 0
    imports["r"] = imports["r"].map(carbon)

    exports = export_ir["elements"].copy()
    exports.loc[exports[exports["L"] <= np.finfo(float).tiny].index, "L"] = 0
    exports["r"] = exports["r"].map(carbon)

    exim = imports.set_index(["i", "r"]).copy()
    exim.rename(columns={"L": "imports"}, inplace=True)
    exim["exports"] = exports.set_index(["i", "r"]).L
    exim["net"] = exim["imports"] - exim["exports"]
    exim.reset_index(drop=False, inplace=True)

    exim = exim[exim.net != 0].copy()
    exim["i"] = exim["i"].map(sp.region_map)

    if sum(exim["i"].isnull()) != 0:
        raise Exception("incomplete region mapping from style_parameters")

    #
    #
    # plot ex/imports by region for policy scenario
    n_plt = list(set(exim.i))

    plt.style.use(["seaborn-white", "werewolf_style.mplstyle"])

    # plot for cntlreg
    fig, ax = plt.subplots()
    y_div = 5000
    for n, i in enumerate(n_plt):
        df = exim[exim.i == i]

        ax.plot(
            df["r"],
            df["net"],
            visible=True,
            color=sp.cm_region[i],
            linewidth=1,
            label=i,
        )

        ax.plot(
            df["r"],
            [0 for _ in range(len(carbon))],
            visible=True,
            color="black",
            linewidth=2,
            linestyle="--",
        )

        # plt.suptitle('super title here')
        plt.xlabel(x_title)
        plt.ylabel("Net Imports to Cntl Region (MW)")
        plt.tight_layout()
        plt.ylim(
            -y_div * (-min(exim["net"]) // y_div + 1),
            y_div * (max(exim["net"]) // y_div + 1),
        )
        ax.grid(which="major", axis="both", linestyle="--")
        ax.legend(loc="upper right", frameon=True, prop={"size": 6})

    plt.savefig(
        os.path.join(args.output, "agg_exim.png"), dpi=600, format="png",
    )
