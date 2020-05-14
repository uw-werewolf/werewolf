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
gen_labels.sort()
# cm = plt.get_cmap('gist_ncar')
cm = plt.get_cmap("jet")
cm_gen = {i: cm(1.0 * n / len(gen_labels)) for n, i in enumerate(gen_labels)}

# region color map
region_labels = list(set(region_map.values()))
region_labels.sort()
colorPalette = sns.color_palette(palette="bright", n_colors=len(region_labels))
cm_region = {i: cm(1.0 * n / len(region_labels)) for n, i in enumerate(region_labels)}

# cntlreg/not_cntlreg color map
colorPalette = sns.color_palette(palette="bright", n_colors=2)
cm_cntlreg = dict(zip([True, False], colorPalette))


# cntlreg/not_cntlreg color map
colorPalette = sns.color_palette(palette="bright", n_colors=4)
cm_fossil = dict(
    zip(
        [
            ("Renew", "Cntl Reg"),
            ("Fossil", "Not Cntl Reg"),
            ("Renew", "Not Cntl Reg"),
            ("Fossil", "Cntl Reg"),
        ],
        colorPalette,
    )
)


# costs color map
cost_values = list(cost_map.values())
cost_values.sort()
colorPalette = sns.color_palette(palette="bright", n_colors=len(cost_map))
cm_cost = dict(zip(cost_values, colorPalette))
