import seaborn as sns

labelmap = {'Battery_fast': 'Battery - Fast',
            'Battery_med': 'Battery - Med',
            'Battery_slow': 'Battery - Slow',
            'Biomass': 'Biomass',
            'Coal_Steam': 'Coal Steam',
            'Combined_Cycle': 'Combined Cycle',
            'Combustion_Turbine': 'Combustion Turbine',
            'Fossil_Waste': 'Fossil Waste',
            'Fuel_Cell': 'Fuel Cell',
            'Geothermal': 'Geothermal',
            'Hydro': 'Hydro',
            'IGCC': 'IGCC',
            'Landfill_Gas': 'Landfill Gas',
            'Municipal_Solid_Waste': 'Municipal Solid Waste',
            'Non_Fossil_Waste': 'Non Fossil Waste',
            'Nuclear': 'Nuclear',
            'OG_Steam': 'Oil/Gas Steam',
            'Offshore_Wind': 'Wind',
            'Offshore_Wind_1': 'Wind',
            'Offshore_Wind_10': 'Wind',
            'Offshore_Wind_11': 'Wind',
            'Offshore_Wind_12': 'Wind',
            'Offshore_Wind_13': 'Wind',
            'Offshore_Wind_14': 'Wind',
            'Offshore_Wind_15': 'Wind',
            'Offshore_Wind_2': 'Wind',
            'Offshore_Wind_3': 'Wind',
            'Offshore_Wind_4': 'Wind',
            'Offshore_Wind_5': 'Wind',
            'Offshore_Wind_6': 'Wind',
            'Offshore_Wind_7': 'Wind',
            'Offshore_Wind_8': 'Wind',
            'Offshore_Wind_9': 'Wind',
            'Onshore_Wind': 'Wind',
            'Onshore_Wind_1': 'Wind',
            'Onshore_Wind_10': 'Wind',
            'Onshore_Wind_2': 'Wind',
            'Onshore_Wind_3': 'Wind',
            'Onshore_Wind_4': 'Wind',
            'Onshore_Wind_5': 'Wind',
            'Onshore_Wind_6': 'Wind',
            'Onshore_Wind_7': 'Wind',
            'Onshore_Wind_8': 'Wind',
            'Onshore_Wind_9': 'Wind',
            'Pumped_Storage': 'Pumped Storage',
            'SolarDistUtil_PV_1': 'Solar PV',
            'SolarDistUtil_PV_2': 'Solar PV',
            'SolarDistUtil_PV_3': 'Solar PV',
            'SolarDistUtil_PV_4': 'Solar PV',
            'SolarDistUtil_PV_5': 'Solar PV',
            'SolarDistUtil_PV_6': 'Solar PV',
            'SolarDistUtil_PV_7': 'Solar PV',
            'SolarUtil_PV_1': 'Solar PV',
            'SolarUtil_PV_2': 'Solar PV',
            'SolarUtil_PV_3': 'Solar PV',
            'SolarUtil_PV_4': 'Solar PV',
            'SolarUtil_PV_5': 'Solar PV',
            'SolarUtil_PV_6': 'Solar PV',
            'SolarUtil_PV_7': 'Solar PV',
            'Solar_PV': 'Solar PV',
            'Solar_Thermal': 'Solar Thermal',
            'Tires': 'Tires',
            'WI': 'WI',
            'IL': 'IL',
            'MI_UP': 'MI (UP)',
            'IL_CHI': 'Chicago',
            'IL_OTH': 'IL - Other',
            'IA': 'IA',
            'MN': 'MN'}


marker = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8',
          's', 'p', 'P', '*', 'h', 'H', '+', 'x', 'X', 'D', 'd', '|', '_']


labels = list(set(labelmap.values()))
colorPalette = sns.color_palette(palette='bright', n_colors=10)

linestyle = [(i, j) for i in marker for j in colorPalette]

linemap = dict(zip(labels, linestyle[0:len(labels)]))

# sns.palplot(sns.color_palette('bright', 10))
# plt.show()
