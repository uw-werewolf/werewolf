_rename_cols = {}

# data column mapping: epa_2019
_rename_cols["epa_2019"] = {}
_rename_cols["epa_2019"]["epa_ipm_to_fips"] = {
    "fips": "fips.full",
    "state": "state.fullname",
    "county": "cnty.fullname",
    "region name": "region.epa.ipm",
}
_rename_cols["epa_2019"]["reeds_regions"] = {
    "county": "cnty.fullname",
    "state": "state.fullname",
    "state.abb": "state.abbv",
    "id": "id",
    "alt.id": "alt.id",
    "state.fips": "fips.state",
    "cnty.fips": "fips.cnty",
    "reeds.reg": "region.reeds.reg",
    "reeds.ba": "region.reeds.ba",
    "cens.div.num": "region.cens.div",
    "fips": "fips.full",
}
_rename_cols["epa_2019"]["epa_needs"] = {
    "Plant Name": "plant_name",
    "UniqueID_Final": "unique_id_final",
    "ORIS Plant Code": "oris_plant_code",
    "Boiler/Generator/Committed Unit": "Boiler/Generator/Committed Unit",
    "Unit ID": "unit_id",
    "CAMD Database UnitID": "camd_database_unit_id",
    "PlantType": "plant_type",
    "Combustion Turbine/IC Engine": "Combustion Turbine/IC Engine",
    "Region Name": "region.epa.ipm",
    "State Code": "fips.state",
    "County": "cnty.fullname",
    "County Code": "fips.cnty",
    "FIPS5": "fips.full",
    "Capacity (MW)": "value.capacity.MW",
    "Heat Rate (Btu/kWh)": "value.heat_rate.btu_per_kwh",
    "On Line Year": "online_year",
    "Retirement Year": "retirement_year",
    "Firing": "firing",
    "Bottom": "bottom",
    "Cogen?": "cogen_flag",
    "Modeled Fuels": "modeled_fuels",
}

_rename_cols["epa_2019"]["egrid"] = {
    "DOE/EIA ORIS plant or facility code": "oris_plant_code",
    "Plant capacity factor": "value.capacity_factor.unitless",
}

_rename_cols["epa_2019"]["latlng"] = {
    "fips": "fips.full",
    "state": "state.fullname",
    "population": "value.population.count",
    "lat": "lat",
    "lng": "lng",
}
_rename_cols["epa_2019"]["ldc"] = {
    "timestamp": "timestamp",
    "epoch": "epoch",
    "hour": "hour",
    "Region": "region.epa.ipm",
    "value": "value.demand.MW",
}
_rename_cols["epa_2019"]["reeds_wind_cf"] = {
    "tech": "tech.label",
    "trb": "tech.bin",
    "reeds_region": "region.reeds.reg",
    "hour": "hour",
    "value": "value.capacity_factor.unitless",
}
_rename_cols["epa_2019"]["reeds_wind_cap"] = {
    "reeds.reg": "region.reeds.reg",
    "trb": "tech.bin",
    "tech": "tech.label",
    "cost_bin1": "value.cost.bin.1.MW",
    "cost_bin2": "value.cost.bin.2.MW",
    "cost_bin3": "value.cost.bin.3.MW",
    "cost_bin4": "value.cost.bin.4.MW",
    "cost_bin5": "value.cost.bin.5.MW",
}
_rename_cols["epa_2019"]["reeds_wind_costs"] = {
    "reeds.reg": "region.reeds.reg",
    "trb": "tech.bin",
    "tech": "tech.label",
    "cost_bin1": "value.cost.bin.1.usd_per_MW_per_year",
    "cost_bin2": "value.cost.bin.2.usd_per_MW_per_year",
    "cost_bin3": "value.cost.bin.3.usd_per_MW_per_year",
    "cost_bin4": "value.cost.bin.4.usd_per_MW_per_year",
    "cost_bin5": "value.cost.bin.5.usd_per_MW_per_year",
}
_rename_cols["epa_2019"]["reeds_solar_cf"] = {
    "tech": "tech.label",
    "trb": "tech.bin",
    "reeds_region": "region.reeds.ba",
    "hour": "hour",
    "value": "value.capacity_factor.unitless",
}
_rename_cols["epa_2019"]["reeds_solar_cap"] = {
    "reeds.ba": "region.reeds.ba",
    "trb": "tech.bin",
    "tech": "tech.label",
    "cost_bin1": "value.cost.bin.1.MW",
    "cost_bin2": "value.cost.bin.2.MW",
    "cost_bin3": "value.cost.bin.3.MW",
    "cost_bin4": "value.cost.bin.4.MW",
    "cost_bin5": "value.cost.bin.5.MW",
}
_rename_cols["epa_2019"]["reeds_solar_costs"] = {
    "reeds.ba": "region.reeds.ba",
    "trb": "tech.bin",
    "tech": "tech.label",
    "cost_bin1": "value.cost.bin.1.usd_per_MW_per_year",
    "cost_bin2": "value.cost.bin.2.usd_per_MW_per_year",
    "cost_bin3": "value.cost.bin.3.usd_per_MW_per_year",
    "cost_bin4": "value.cost.bin.4.usd_per_MW_per_year",
    "cost_bin5": "value.cost.bin.5.usd_per_MW_per_year",
}
_rename_cols["epa_2019"]["offshore"] = {
    "statefp": "fips.state",
    "countyfp": "fips.county",
    "name": "cnty.fullname",
    "namelsad": "cnty.fullname",
    "fips.full": "fips.full",
}


# data column mapping: wi_psc
_rename_cols["wi_psc"] = _rename_cols["epa_2019"]
_rename_cols["wi_psc"]["miso_gen"] = {
    "Project #": "project_number",
    "County": "cnty.fullname",
    "State": "state.abbv",
    "Fuel": "plant_type",
    "Generating Facility": "generating_facility",
    "Negotiated In Service Date": "year_in_service",
    "Decision Point 2 NRIS MW": "value.capacity.MW",
    "POI Name": "poi_name",
}


_col_dtypes = {}
_col_dtypes["epa_2019"] = {
    "cnty.fullname": str,
    "value.cost.bin.1.usd_per_MW_per_year": float,
    "value.cost.bin.2.usd_per_MW_per_year": float,
    "value.cost.bin.3.usd_per_MW_per_year": float,
    "value.cost.bin.4.usd_per_MW_per_year": float,
    "value.cost.bin.5.usd_per_MW_per_year": float,
    "epoch": int,
    "fips.cnty": str,
    "fips.full": str,
    "fips.state": str,
    "hour": str,
    "lat": float,
    "lng": float,
    "online_year": int,
    "plant_name": str,
    "plant_type": str,
    "region.epa.ipm": str,
    "region.reeds.ba": str,
    "region.reeds.reg": str,
    "retirement_year": int,
    "state.abbv": str,
    "state.fullname": str,
    "tech.bin": str,
    "tech.label": str,
    "timestamp": str,
    "unique_id_final": str,
    "value.capacity.MW": float,
    "value.capacity_factor.unitless": float,
    "value.demand.MW": float,
    "value.heat_rate.btu_per_kwh": float,
    "value.population.count": int,
}
_col_dtypes["wi_psc"] = {
    "poi_name": str,
    "project_number": str,
    "fuel": str,
    "generating_facility": str,
    "year_in_service": str,
    "oris_plant_code": str,
    "cnty.fullname": str,
    "value.cost.bin.1.MW": float,
    "value.cost.bin.2.MW": float,
    "value.cost.bin.3.MW": float,
    "value.cost.bin.4.MW": float,
    "value.cost.bin.5.MW": float,
    "value.cost.bin.1.usd_per_MW_per_year": float,
    "value.cost.bin.2.usd_per_MW_per_year": float,
    "value.cost.bin.3.usd_per_MW_per_year": float,
    "value.cost.bin.4.usd_per_MW_per_year": float,
    "value.cost.bin.5.usd_per_MW_per_year": float,
    "epoch": int,
    "fips.cnty": str,
    "fips.full": str,
    "fips.state": str,
    "hour": str,
    "lat": float,
    "lng": float,
    "online_year": int,
    "plant_name": str,
    "plant_type": str,
    "region.epa.ipm": str,
    "region.reeds.ba": str,
    "region.reeds.reg": str,
    "retirement_year": int,
    "state.abbv": str,
    "state.fullname": str,
    "tech.bin": str,
    "tech.label": str,
    "timestamp": str,
    "unique_id_final": str,
    "value.capacity.MW": float,
    "value.capacity_factor.unitless": float,
    "value.demand.MW": float,
    "value.heat_rate.btu_per_kwh": float,
    "value.population.count": int,
}
