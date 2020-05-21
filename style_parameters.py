import seaborn as sns
import os
import filesys as fs
import matplotlib.pyplot as plt


gen_map = {
    "Battery_fast": "Battery - Fast",
    "Battery_med": "Battery - Med",
    "Battery_slow": "Battery - Slow",
    "Biomass": "Biomass",
    "Coal_Steam": "Coal Steam",
    "Combined_Cycle": "Combined Cycle",
    "Combustion_Turbine": "Combustion Turbine",
    "Fossil_Waste": "Fossil Waste",
    "Fuel_Cell": "Fuel Cell",
    "Geothermal": "Geothermal",
    "Hydro": "Hydro",
    "IGCC": "IGCC",
    "Landfill_Gas": "Landfill Gas",
    "Municipal_Solid_Waste": "Municipal Solid Waste",
    "Non_Fossil_Waste": "Non Fossil Waste",
    "Nuclear": "Nuclear",
    "OG_Steam": "Oil/Gas Steam",
    "Offshore_Wind": "Offshore Wind",
    "Offshore_Wind_1": "Offshore Wind",
    "Offshore_Wind_10": "Offshore Wind",
    "Offshore_Wind_11": "Offshore Wind",
    "Offshore_Wind_12": "Offshore Wind",
    "Offshore_Wind_13": "Offshore Wind",
    "Offshore_Wind_14": "Offshore Wind",
    "Offshore_Wind_15": "Offshore Wind",
    "Offshore_Wind_2": "Offshore Wind",
    "Offshore_Wind_3": "Offshore Wind",
    "Offshore_Wind_4": "Offshore Wind",
    "Offshore_Wind_5": "Offshore Wind",
    "Offshore_Wind_6": "Offshore Wind",
    "Offshore_Wind_7": "Offshore Wind",
    "Offshore_Wind_8": "Offshore Wind",
    "Offshore_Wind_9": "Offshore Wind",
    "Onshore_Wind": "Onshore Wind",
    "Onshore_Wind_1": "Onshore Wind",
    "Onshore_Wind_10": "Onshore Wind",
    "Onshore_Wind_2": "Onshore Wind",
    "Onshore_Wind_3": "Onshore Wind",
    "Onshore_Wind_4": "Onshore Wind",
    "Onshore_Wind_5": "Onshore Wind",
    "Onshore_Wind_6": "Onshore Wind",
    "Onshore_Wind_7": "Onshore Wind",
    "Onshore_Wind_8": "Onshore Wind",
    "Onshore_Wind_9": "Onshore Wind",
    "Pumped_Storage": "Pumped Storage",
    "SolarDistUtil_PV_1": "Solar PV",
    "SolarDistUtil_PV_2": "Solar PV",
    "SolarDistUtil_PV_3": "Solar PV",
    "SolarDistUtil_PV_4": "Solar PV",
    "SolarDistUtil_PV_5": "Solar PV",
    "SolarDistUtil_PV_6": "Solar PV",
    "SolarDistUtil_PV_7": "Solar PV",
    "SolarUtil_PV_1": "Solar PV",
    "SolarUtil_PV_2": "Solar PV",
    "SolarUtil_PV_3": "Solar PV",
    "SolarUtil_PV_4": "Solar PV",
    "SolarUtil_PV_5": "Solar PV",
    "SolarUtil_PV_6": "Solar PV",
    "SolarUtil_PV_7": "Solar PV",
    "Solar_PV": "Solar PV",
    "Solar_Thermal": "Solar Thermal",
    "Tires": "Tires",
}

region_map = {
    "55001": "WI",
    "55003": "WI",
    "55005": "WI",
    "55007": "WI",
    "55009": "WI",
    "55011": "WI",
    "55013": "WI",
    "55015": "WI",
    "55017": "WI",
    "55019": "WI",
    "55021": "WI",
    "55023": "WI",
    "55025": "WI",
    "55027": "WI",
    "55029": "WI",
    "55031": "WI",
    "55033": "WI",
    "55035": "WI",
    "55037": "WI",
    "55039": "WI",
    "55041": "WI",
    "55043": "WI",
    "55045": "WI",
    "55047": "WI",
    "55049": "WI",
    "55051": "WI",
    "55053": "WI",
    "55055": "WI",
    "55057": "WI",
    "55059": "WI",
    "55061": "WI",
    "55063": "WI",
    "55065": "WI",
    "55067": "WI",
    "55069": "WI",
    "55071": "WI",
    "55073": "WI",
    "55075": "WI",
    "55077": "WI",
    "55078": "WI",
    "55079": "WI",
    "55081": "WI",
    "55083": "WI",
    "55085": "WI",
    "55087": "WI",
    "55089": "WI",
    "55091": "WI",
    "55093": "WI",
    "55095": "WI",
    "55097": "WI",
    "55099": "WI",
    "55101": "WI",
    "55103": "WI",
    "55105": "WI",
    "55107": "WI",
    "55109": "WI",
    "55111": "WI",
    "55113": "WI",
    "55115": "WI",
    "55117": "WI",
    "55119": "WI",
    "55121": "WI",
    "55123": "WI",
    "55125": "WI",
    "55127": "WI",
    "55129": "WI",
    "55131": "WI",
    "55133": "WI",
    "55135": "WI",
    "55137": "WI",
    "55139": "WI",
    "55141": "WI",
    "IL": "IL",
    "MI_UP": "MI (UP)",
    "IL_CHI": "Chicago",
    "IL_OTH": "IL - Other",
    "IA": "IA",
    "MN": "MN",
}

cost_map = {
    "Invest": "Investment Costs",
    "Maintain": "Maintenance Costs",
    "Operate": "Operational Costs",
    "LostLoad": "Cost of Lost Load",
}


# generator type color map
gen_labels = list(set(gen_map.values()))
# cm = plt.get_cmap("jet")
# cm_gen = {i: cm(1.0 * n / len(gen_labels)) for n, i in enumerate(gen_labels)}

cm_gen = {
    "Non Fossil Waste": (0.0, 0.0, 0.5, 1.0),
    "Combustion Turbine": (0.0, 0.0, 0.696078431372549, 1.0),
    "Offshore Wind": (0.0, 0.0, 0.892156862745098, 1.0),
    "Solar Thermal": (0.0, 0.0176470588235293, 1.0, 1.0),
    "Fossil Waste": (0.0, 0.19019607843137254, 1.0, 1.0),
    "Geothermal": (0.0, 0.3627450980392157, 1.0, 1.0),
    "Battery - Slow": (0.0, 0.5352941176470586, 1.0, 1.0),
    "Onshore Wind": (0.0, 0.707843137254902, 1.0, 1.0),
    "Combined Cycle": (0.0, 0.8960784313725491, 0.9709044908285895, 1.0),
    "Municipal Solid Waste": (0.13598987982289687, 1.0, 0.8317520556609741, 1.0),
    "Nuclear": (0.2751423149905123, 1.0, 0.6925996204933587, 1.0),
    "Battery - Fast": (0.4142947501581275, 1.0, 0.5534471853257434, 1.0),
    "IGCC": (0.5534471853257431, 1.0, 0.4142947501581278, 1.0),
    "Landfill Gas": (0.6925996204933585, 1.0, 0.27514231499051234, 1.0),
    "Coal Steam": (0.831752055660974, 1.0, 0.1359898798228969, 1.0),
    "Battery - Med": (0.9709044908285893, 0.9593318809005086, 0.0, 1.0),
    "Solar PV": (1.0, 0.7850399419026872, 0.0, 1.0),
    "Pumped Storage": (1.0, 0.6252723311546844, 0.0, 1.0),
    "Hydro": (1.0, 0.46550472040668145, 0.0, 1.0),
    "Tires": (1.0, 0.3057371096586785, 0.0, 1.0),
    "Biomass": (1.0, 0.14596949891067557, 0.0, 1.0),
    "Fuel Cell": (0.8921568627450983, 0.0, 0.0, 1.0),
    "Oil/Gas Steam": (0.6960784313725497, 0.0, 0.0, 1.0),
}


# region color map
region_labels = list(set(region_map.values()))
# colorPalette = sns.color_palette(palette="bright", n_colors=len(region_labels))
# cm_region = {i: cm(1.0 * n / len(region_labels)) for n, i in enumerate(region_labels)}

cm_region = {
    "IL - Other": (0.0, 0.0, 0.5, 1.0),
    "IL": (0.0, 0.06470588235294118, 1.0, 1.0),
    "IA": (0.0, 0.6450980392156863, 1.0, 1.0),
    "MI (UP)": (0.24984187223276405, 1.0, 0.717900063251107, 1.0),
    "WI": (0.7179000632511068, 1.0, 0.2498418722327641, 1.0),
    "Chicago": (1.0, 0.7269426289034134, 0.0, 1.0),
    "MN": (1.0, 0.18954248366013093, 0.0, 1.0),
}

# cntlreg/not_cntlreg color map
# colorPalette = sns.color_palette(palette="bright", n_colors=2)
# cm_cntlreg = dict(zip([True, False], colorPalette))

cm_cntlreg = {
    True: (0.00784313725490196, 0.24313725490196078, 1.0),
    False: (1.0, 0.48627450980392156, 0.0),
}


# cntlreg/not_cntlreg color map
# colorPalette = sns.color_palette(palette="bright", n_colors=4)
# cm_fossil = dict(
#     zip(
#         [
#             ("Renew", "Cntl Reg"),
#             ("Fossil", "Not Cntl Reg"),
#             ("Renew", "Not Cntl Reg"),
#             ("Fossil", "Cntl Reg"),
#         ],
#         colorPalette,
#     )
# )
cm_fossil = {
    ("Renew", "Cntl Reg"): (0.00784313725490196, 0.24313725490196078, 1.0),
    ("Fossil", "Not Cntl Reg"): (1.0, 0.48627450980392156, 0.0),
    ("Renew", "Not Cntl Reg"): (
        0.10196078431372549,
        0.788235294117647,
        0.2196078431372549,
    ),
    ("Fossil", "Cntl Reg"): (0.9098039215686274, 0.0, 0.043137254901960784),
}

# costs color map
# cost_values = list(cost_map.values())
# cost_values.sort()
# colorPalette = sns.color_palette(palette="bright", n_colors=len(cost_map))
# cm_cost = dict(zip(cost_values, colorPalette))


cm_cost = {
    "Cost of Lost Load": (0.00784313725490196, 0.24313725490196078, 1.0),
    "Investment Costs": (1.0, 0.48627450980392156, 0.0),
    "Maintenance Costs": (0.10196078431372549, 0.788235294117647, 0.2196078431372549),
    "Operational Costs": (0.9098039215686274, 0.0, 0.043137254901960784),
}
