import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axis as axes
import seaborn as sns
import argparse
import glob
import os
import gmsxfr
import argparse

pd.plotting.register_matplotlib_converters()


def fit_ldc(ldc, to_csv=False):
    ldc["season"] = "annual"

    ldc["timestamp"] = pd.to_datetime(ldc["epoch"], unit="s")

    # map in day of week
    # monday is 0 and sunday is 6
    ldc["weekday"] = [i.weekday() for i in ldc["timestamp"]]
    day = {
        0: "weekday",
        1: "weekday",
        2: "weekday",
        3: "weekday",
        4: "weekday",
        5: "weekend",
        6: "weekend",
    }
    ldc["daytype"] = ldc["weekday"].map(day)

    # 24 hour label
    ldc["24hr"] = [i.hour for i in ldc["timestamp"]]

    # aggregate regions as necessary
    ldc = (
        ldc.groupby(
            [
                "timestamp",
                "epoch",
                "hrs",
                "season",
                "weekday",
                "daytype",
                "24hr",
                "regions",
                "*",
            ]
        )
        .sum()
        .reset_index(drop=False)
    )

    # map in seasons
    # s = ['winter', 'spring', 'summer', 'fall', 'winter']
    # n = [1095, 2190, 2190, 2190, 1095]
    #
    # s = ['winter', 'summer', 'winter']
    # n = [2190, 4380, 2190]
    #
    # b = []
    # for i, k in enumerate(s):
    #     b.extend([s[i] for j in range(n[i])])
    #
    # ldc['season'] = ldc['hrs'].map(dict(zip([str(i) for i in range(1, 8760+1)], b)))

    # break regions into their ldc curves and assign loadblocks
    ldc["loadblock"] = None
    ldc["fit"] = 0

    for n, i in enumerate(ldc.regions.unique()):

        ldc_1 = ldc[ldc["regions"] == i].copy()

        ldc_1["loadblock"] = pd.qcut(
            ldc_1["L"],
            q=[0, 0.05, 0.15, 0.25, 0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 1],
            labels=False,
        )

        for k in ldc_1.loadblock.unique():
            idx = ldc_1[ldc_1["loadblock"] == k].index
            ldc_1.loc[idx, "fit"] = ldc_1.loc[idx, "L"].mean()

        # nicer subseason labeling
        ldc_1["loadblock"] = ldc_1["loadblock"].map(str)
        ldc_1["loadblock"] = "b" + ldc_1["loadblock"]

        # put back into main dataframe
        ldc.loc[ldc_1.index, "loadblock"] = ldc_1.loadblock
        ldc.loc[ldc_1.index, "fit"] = ldc_1.fit

    return ldc


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--gams_sysdir", dest="gams_sysdir", default=None, type=str)
    parser.add_argument("--data_repo", dest="data_repo", default=None, type=str)
    parser.add_argument("--ldc_curves", dest="ldc_curves", default=None, type=str)

    # parser.set_defaults(gams_sysdir="some path here")
    # parser.set_defaults(data_repo="some path here")
    # parser.set_defaults(ldc_curves="some path here")

    args = parser.parse_args()

    gdx = gmsxfr.GdxContainer(
        args.gams_sysdir, os.path.join(args.data_repo, "processed_werewolf_data.gdx")
    )

    # load data from GDX
    gdx.rgdx(["ldc_container", "regions", "hrs"])

    ldc = gdx.to_dataframe("ldc_container")
    regions = gdx.to_dataframe("regions")
    hrs = gdx.to_dataframe("hrs")

    # create load duration curves
    ldc_fit = {}
    for i in set(ldc["elements"]["*"]):
        ldc_fit[i] = ldc["elements"][ldc["elements"]["*"] == i].copy()
        ldc_fit[i] = fit_ldc(ldc=ldc_fit[i], to_csv=False)

    #
    #
    # export data to gdx
    season = ldc_fit["total"].season.unique().tolist()
    daytype = ldc_fit["total"].daytype.unique().tolist()

    b = ldc_fit["total"].loadblock.unique().tolist()
    b.sort()

    regions = regions["elements"]["*"].unique().tolist()
    hrs = ldc_fit["total"].hrs.unique().tolist()

    map_block_hour = list(
        zip(
            ldc_fit["total"]["regions"],
            ldc_fit["total"]["loadblock"],
            ldc_fit["total"]["hrs"],
        )
    )

    loadblockhours = {}
    for i in season:
        for k in b:
            idx = ldc_fit["total"][
                (ldc_fit["total"]["regions"] == ldc_fit["total"].regions.unique()[0])
                & (ldc_fit["total"]["season"] == i)
                & (ldc_fit["total"]["loadblock"] == k)
            ].index
            loadblockhours[(i, k)] = len(idx)

    load_compact = {}
    for i in set(ldc["elements"]["*"]):
        ldc_compact = ldc_fit[i].copy()
        load_compact[i] = pd.pivot_table(
            ldc_compact[["season", "loadblock", "regions", "L"]],
            index=["season", "loadblock", "regions"],
            values="L",
            aggfunc=np.mean,
        )
        load_compact[i].reset_index(drop=False, inplace=True)
        load_compact[i] = dict(
            zip(
                load_compact[i][["season", "loadblock", "regions"]].itertuples(
                    index=False, name=None
                ),
                load_compact[i]["L"],
            )
        )

    data = {
        "t": {"type": "set", "elements": season, "text": "season"},
        "regions": {"type": "set", "elements": regions, "text": "model regions"},
        "daytype": {"type": "set", "elements": daytype, "text": "type of day"},
        "b": {"type": "set", "elements": b, "text": "loadblock segments"},
        "hrs": {"type": "set", "elements": hrs, "text": "hours in a year"},
        "map_block_hour": {
            "type": "set",
            "domain": ["regions", "b", "hrs"],
            "elements": map_block_hour,
            "text": "map between regions, loadblocks and hours of the year",
        },
        "loadblockhours_compact": {
            "type": "parameter",
            "domain": ["t", "b"],
            "domain_info": "regular",
            "elements": loadblockhours,
            "text": "# of hours per loadblock",
        },
        "ldc_compact": {
            "type": "parameter",
            "domain": ["t", "b", "regions"],
            "elements": load_compact["total"],
            "text": "electrical demand (units: MW)",
        },
        "ldc_compact_2020": {
            "type": "parameter",
            "domain": ["t", "b", "regions"],
            "elements": load_compact["2020"],
            "text": "electrical demand (units: MW)",
        },
        "ldc_compact_new_baseload": {
            "type": "parameter",
            "domain": ["t", "b", "regions"],
            "elements": load_compact["new_baseload"],
            "text": "electrical demand (units: MW)",
        },
    }

    # write gdx file
    gdx = gmsxfr.GdxContainer(args.gams_sysdir)
    gdx.validate(data)
    gdx.add_to_gdx(data, standardize_data=True, inplace=True, quality_checks=False)
    gdx.write_gdx(os.path.join(args.data_repo, "ldc_fit.gdx"))

    # plot LDCs
    plt.style.use(["seaborn-white", "werewolf_style.mplstyle"])

    for i in set(ldc_fit["total"]["regions"]):
        fig, ax = plt.subplots()
        df = pd.DataFrame()
        df["total"] = ldc_fit["total"][
            ldc_fit["total"]["regions"] == i
        ].L.values.tolist()

        df["2020"] = ldc_fit["2020"][ldc_fit["2020"]["regions"] == i].L.values.tolist()

        df["new_baseload"] = ldc_fit["new_baseload"][
            ldc_fit["new_baseload"]["regions"] == i
        ].L.values.tolist()

        df["fit"] = ldc_fit["total"][
            ldc_fit["total"]["regions"] == i
        ].fit.values.tolist()

        total = df.total.values.tolist()
        total.sort(reverse=True)
        ax.plot(total, linewidth=1, color="red", label="EVs + New Baseload")

        baseload_2020 = df["2020"].values.tolist()
        baseload_2020.sort(reverse=True)
        ax.plot(baseload_2020, linewidth=1, color="green", label="Orig Baseload")

        new_baseload = df.new_baseload.values.tolist()
        new_baseload.sort(reverse=True)
        ax.plot(new_baseload, linewidth=1, color="blue", label="New Baseload")

        fit = df.fit.values.tolist()
        fit.sort(reverse=True)
        ax.plot(fit, linewidth=1, color="grey", label="fit")

        plt.suptitle("Load Demand Curve")
        plt.title(f"Node = {i}")

        plt.ylim(bottom=0)
        plt.xlim(left=0, right=8760)
        ax = plt.gca()
        ax.grid(which="major", axis="y", linestyle="--")
        ax.grid(which="major", axis="x", linestyle="--")

        # plt.xlabel('Hour')
        plt.ylabel("Load (MW)")
        ax.legend(loc="best", frameon=True, prop={"size": 6})
        ax.set_xticklabels([])
        plt.savefig(os.path.join(args.ldc_curves, f"{i}.png"), dpi=600, format="png")
        plt.close()
