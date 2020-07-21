$SETENV GDXCOMPRESS 1

$IFTHENI %system.filesys% == UNIX $SET sep "/"
$ELSE $SET sep "\"
$ENDIF

OPTION limrow = 0;
OPTION limcol = 0;

$ONEMPTY
SCALAR myerrorlevel;

$IF NOT SETGLOBAL ev_factor $SETGLOBAL ev_factor 0
$IF NOT SETGLOBAL proj_year $SETGLOBAL proj_year 2030
$IF NOT SETGLOBAL base_year $SETGLOBAL base_year 2020

$IF NOT SETGLOBAL output_gdx $SETGLOBAL output_gdx "processed_werewolf_data.gdx"


* controls the growth of demand
* EIA AEO 2020 says that demand will grow at approximately 0.8% year by year
* https://www.eia.gov/outlooks/aeo/data/browser/#/?id=8-AEO2020&cases=ref2020&sourcekey=0
$IF NOT SETGLOBAL demand_growth $SETGLOBAL demand_growth 0.8
PARAMETER demand_growth / %demand_growth% /;

SET yr "annual time horizon" / 2020*%proj_year% /;

PARAMETER growth_factor;
growth_factor = (1 + %demand_growth%/100)**(%proj_year% - %base_year%);

PARAMETER ldc_raw_scaled(epoch,hrs,regions) 'scaled load duration curves';
* scale demand to reflect future demand in year = %proj_year%
ldc_raw_scaled(time(epoch,hrs),regions) = growth_factor * ldc_raw(epoch,hrs,regions);

*--------------------
* Other model data
*--------------------
SCALAR lifetime 'plant lifetime (unit: years)' / 25 /;
*--------------------


*--------------------
* Set up regions to be in the model
*--------------------
* to define the regions in the model we need two components:
* 1) all model regions that are at the fips level
* 2) all model regions that have somehow been aggregated from fips level
SET i(regions) 'regions in the model';
SET i_aggr(regions) 'regions to aggregate in model' / MI_UP, IL_CHI, IL_OTH, IA, MN /;
SET map_aggr(regions,fips) 'aggregation scheme';
*--------------------



*--------------------
* Adoption of EVs Model
*--------------------
SCALAR pi / 3.14159 /;
SCALAR eer / 3 /;
PARAMETER transport_energy;

* (average mpg) * (LDV in the US) * (1000 vmt/month) * (months/year) * (MJ/gal) * (1/engine efficiency) * (kWh/MJ) * (years/hour) * (MW/kW) = (average MW)
transport_energy = (1/24.9) * %ev_factor% * (193672370) * (1000) * (12) * (126958036/1e6) * (1/3.6) * (1/8760) * (1/1000);

PARAMETER total_population;
total_population = sum(fips_p, population(fips_p));

PARAMETER ev_load(epoch,hrs,regions);
ev_load(time(epoch,hrs),fips) = (sin((pi/180)*((0.5*24)*hrs.val - 120)) + 1) * transport_energy/eer * population(fips) / total_population;
*--------------------



*--------------------
* Aggregation Scheme: WI is broken into 2 nodes
*--------------------
* i(i_aggr) = yes;
*
* map_aggr('MI_UP',fips) = yes$((map_fips_ipm(fips,'MIS_WUMS') * map_fips_state(fips,'MI')) + (map_fips_ipm(fips,'MIS_MNWI') * map_fips_state(fips,'MI')));
*
* map_aggr('IL_CHI',fips) = yes$(SAMEAS(fips, '17031') OR SAMEAS(fips, '17097') OR SAMEAS(fips, '17043') OR SAMEAS(fips, '17197') OR SAMEAS(fips, '17089') OR SAMEAS(fips, '17093'));
*
* map_aggr('IL_OTH',fips) = yes$(map_fips_state(fips,'IL') - map_aggr('IL_CHI',fips));
*
* map_aggr('IA',fips) = yes$map_fips_state(fips,'IA');
* map_aggr('MN',fips) = yes$map_fips_state(fips,'MN');
* map_aggr('WI_1',fips) = yes$(map_fips_ipm(fips,'MIS_MNWI') * map_fips_state(fips,'WI'));
* map_aggr('WI_2',fips) = yes$(map_fips_ipm(fips,'MIS_WUMS') * map_fips_state(fips,'WI'));
*
* SET map_wi(regions,regions);
* map_wi('WI','WI_1') = yes;
* map_wi('WI','WI_2') = yes;
*--------------------


*--------------------
* Aggregation Scheme: WI is broken into all fips areas
*--------------------
i(regions) = yes$map_fips_state(regions,'WI');
i(i_aggr) = yes;

map_aggr('MI_UP',fips) = yes$((map_fips_ipm(fips,'MIS_WUMS') * map_fips_state(fips,'MI')) + (map_fips_ipm(fips,'MIS_MNWI') * map_fips_state(fips,'MI')));

map_aggr('IL_CHI',fips) = yes$(SAMEAS(fips, '17031') OR SAMEAS(fips, '17097') OR SAMEAS(fips, '17043') OR SAMEAS(fips, '17197') OR SAMEAS(fips, '17089') OR SAMEAS(fips, '17093'));

map_aggr('IL_OTH',fips) = yes$(map_fips_state(fips,'IL') - map_aggr('IL_CHI',fips));

map_aggr('IA',fips) = yes$map_fips_state(fips,'IA');
map_aggr('MN',fips) = yes$map_fips_state(fips,'MN');
map_aggr(fips,fips)$(map_fips_state(fips,'WI')) = yes;

SET cntlreg(regions) 'all regions in model that are subject to policy controls';
cntlreg(fips)$map_fips_state(fips,'WI') = yes;

SET not_cntlreg(regions) 'all regions in model that are not subject to policy controls' / MN, IA, IL_OTH, IL_CHI, MI_UP /;

OPTION map_aggr:0:0:1;
DISPLAY map_aggr;
*--------------------


*--------------------
* Geographic Parameter Mapping
*--------------------
lng(i_aggr) = sum(fips$map_aggr(i_aggr,fips), lng(fips)) / sum(fips$map_aggr(i_aggr,fips), 1);
lat(i_aggr) = sum(fips$map_aggr(i_aggr,fips), lat(fips)) / sum(fips$map_aggr(i_aggr,fips), 1);

PARAMETER map_center(*) 'lat/lng for the center of all modeled regions';
map_center('lat') = sum(i, lat(i)) / CARD(i);
map_center('lng') = sum(i, lng(i)) / CARD(i);
*--------------------



*--------------------
* Generator Parameter Mapping
*--------------------
* find the average heat rates for each node in the model
PARAMETER hr_num(regions,k);
PARAMETER hr_dem(regions,k);
PARAMETER hr_ave(regions,k) 'average heat rate at nodes for each technology type (units: Btu/kWh)';

hr_num(i,k) = sum(fips$map_aggr(i,fips), sum(uid$(map_uid_fips(uid,fips) AND map_uid_type(uid,k)), hr(uid)));

hr_dem(i,k) = sum(fips$map_aggr(i,fips), sum(uid$(map_uid_fips(uid,fips) AND map_uid_type(uid,k)), 1));

hr_ave(i,k)$(hr_dem(i,k) <> 0) = hr_num(i,k) / hr_dem(i,k);


* aggregate generator types to each node in the model
PARAMETER cap_agg(regions,k) 'aggregated existing nameplate capacity at nodes (units: MW)';

cap_agg(i,k) = sum(fips$map_aggr(i,fips), sum(uid$(map_uid_fips(uid,fips) AND map_uid_type(uid,k)), cap(uid))) + sum(fips$map_aggr(i,fips), sum(yr$(yr.val <= %proj_year%), miso_gen(fips,k,yr)));

PARAMETER n_gen(regions,k) 'numer of generators of type k in model region i';
n_gen(i,k) = sum(fips$map_aggr(i,fips), sum(uid$(map_uid_fips(uid,fips) AND map_uid_type(uid,k)), 1));
*--------------------



*--------------------
* Create data containers to hold capacities and capcosts from NREL
*--------------------
PARAMETER cap_nrel(k,regions) 'potential capacity (units: MW)';
PARAMETER capcost_nrel(k,regions) 'capacity weighted capital costs (units: $/MW/year)';
*--------------------



*--------------------
* Merge NREL solar data into model regions
*--------------------
nrel_solar_cf(k,i,hrs) = sum(fips$map_aggr(i,fips), nrel_solar_cf(k,fips,hrs)) / sum(fips_p$map_aggr(i,fips_p), 1);

* calculate data for all model regions that are aggregations of fips regions
nrel_solar_cap(nrel_solar,i) = sum(fips$map_aggr(i,fips), nrel_solar_cap(nrel_solar,fips));

* calculate aggregated capacity for all regions
cap_nrel(nrel_solar,regions) = nrel_solar_cap(nrel_solar,regions);
cap_nrel(nrel_solar,i) = sum(fips$map_aggr(i,fips), nrel_solar_cap(nrel_solar,fips));


PARAMETER w_reg(k,regions,regions) 'regional weight factor by capacity';
w_reg(nrel_solar,map_aggr(i,fips))$(cap_nrel(nrel_solar,i) <> 0) = cap_nrel(nrel_solar,fips)
/ cap_nrel(nrel_solar,i);

capcost_nrel(nrel_solar,i) = sum(fips$map_aggr(i,fips), w_reg(nrel_solar,i,fips) * nrel_solar_cost(nrel_solar,fips));
*--------------------



*--------------------
* Merge NREL wind data into model regions
*--------------------
nrel_wind_cf(k,i,hrs) = sum(fips$map_aggr(i,fips), nrel_wind_cf(k,fips,hrs)) / sum(fips_p$map_aggr(i,fips_p), 1);


* Onshore Wind
* calculate data for all model regions that are aggregations of fips regions
nrel_wind_cap(all_onwind,i) = sum(fips$map_aggr(i,fips), nrel_wind_cap(all_onwind,fips));

* calculate aggregated capacity for all regions
cap_nrel(all_onwind,regions) = nrel_wind_cap(all_onwind,regions);
cap_nrel(all_onwind,i) = sum(fips$map_aggr(i,fips), nrel_wind_cap(all_onwind,fips));

w_reg(all_onwind,map_aggr(i,fips))$(cap_nrel(all_onwind,i) <> 0) = cap_nrel(all_onwind,fips)
/ cap_nrel(all_onwind,i);

capcost_nrel(all_onwind,i) = sum(fips$map_aggr(i,fips), w_reg(all_onwind,i,fips) * nrel_wind_cost(all_onwind,fips));


* Offshore Wind
* calculate data for all model regions that are aggregations of fips regions
nrel_wind_cap(all_offwind,i) = sum(fips$map_aggr(i,fips), nrel_wind_cap(all_offwind,fips));

* calculate aggregated capacity for all regions
cap_nrel(all_offwind,regions) = nrel_wind_cap(all_offwind,regions);
cap_nrel(all_offwind,i) = sum(fips$map_aggr(i,fips), nrel_wind_cap(all_offwind,fips));

w_reg(all_offwind,map_aggr(i,fips))$(cap_nrel(all_offwind,i) <> 0) = cap_nrel(all_offwind,fips)
/ cap_nrel(all_offwind,i);


capcost_nrel(all_offwind,i) = sum(fips$map_aggr(i,fips), w_reg(all_offwind,i,fips) * nrel_wind_cost(all_offwind,fips));
*--------------------



*--------------------
* Financial data
*--------------------
PARAMETER eC(k,regions) 'capital costs (units: $/MW/year)';
* ref: https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2020.pdf -- Table 2
* ref: https://atb.nrel.gov/electricity/2019/index.html?t=cc
* reg: https://www.epa.gov/sites/production/files/2020-02/documents/incremental_documentation_for_epa_v6_january_2020_reference_case.pdf
* ref: https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capcost_assumption.pdf

* input data has units of $/kW
eC('Energy_Storage_fast',i) = 6 * 1484;
eC('Energy_Storage_med',i) = 3 * 1484;
eC('Energy_Storage_slow',i) = 1484;

* NREL ATB 2019 (Dedicated biopower plant, not cofired)
eC('Biomass',i) = 3990;

* NREL ATB 2019 (Coal-new-ConstantCF)
eC('Coal_Steam',i) = 4036;

* NREL ATB 2019 (Coal-IGCC-AvgCF)
eC('IGCC',i) = 4409;

* NREL ATB 2019 (Gas-CC-AvgCF)
eC('Combined_Cycle',i) = 927;

* NREL ATB 2019 (Gas-CT-AvgCF)
eC('Combustion_Turbine',i) = 919;

* ??
eC('OG_Steam',i) = 3311;

* ??
eC('Fossil_Waste',i) = 3250;

* ??
eC('Fuel_Cell',i) = 6700;

* NREL ATB 2019 (GEO-Hydro Binary example)
eC('Geothermal',i) = 5918;

* NREL ATB 2019 (NPD 2)
eC('Hydro',i) = 5620;

* ??
eC('Landfill_Gas',i) = 9023;

* estimated to be similar to a cofired biopower plant
eC('Municipal_Solid_Waste',i) = 4184;
eC('Non_Fossil_Waste',i) = 4184;
eC('Tires',i) = 4184;

* NREL ATB 2019
eC('Nuclear',i) = 6742;

* * NREL ATB 2019 (TRG 3 - Offshore Fixed)
* eC('Offshore_Wind',i) = 3835;
*
* * NREL ATB 2019
* eC('Onshore_Wind',i) = 1623;

* ??
eC('Pumped_Storage',i) = 5626;

* NREL ATB 2019 (Utility PV)
eC('Solar_PV',i) = 1100;

* NREL ATB 2019 (CSP - 10hrs TES - Class 1)
eC('Solar_Thermal',i) = 6450;

* these units are already in $/MW/year... do not need to convert in next step
eC(nrel_solar,i) = capcost_nrel(nrel_solar,i);
eC(all_onwind,i) = capcost_nrel(all_onwind,i);
eC(all_offwind,i) = capcost_nrel(all_offwind,i);

* convert to annualized capital costs (units: $/MW/year)
eC(k,i)$(NOT nrel_solar(k) AND NOT all_onwind(k) AND NOT all_offwind(k)) = eC(k,i) * 1000 / lifetime;



PARAMETER oC(k) 'fixed operating and maintenance costs (units: $/MW/yr)';
* NREL ATB 2019 (Battery Storage - Mid - 2020)
oC('Energy_Storage_fast') = 32100;
oC('Energy_Storage_med') = 32100;
oC('Energy_Storage_slow') = 32100;

* NREL ATB 2019 (Dedicated)
oC('Biomass') = 112000;

* NREL ATB 2019 (Coal-new-ConstantCF)
oC('Coal_Steam') = 33000;

* NREL ATB 2019 (Gas-CC-AvgCF)
oC('Combined_Cycle') = 12000;

* NREL ATB 2019 (Gas-CT-AvgCF)
oC('Combustion_Turbine') = 12000;

* ??
oC('Fossil_Waste') = 50000;

* ??
oC('Fuel_Cell') = 10000;

* NREL ATB 2019 (GEO-Hydro Binary example)
oC('Geothermal') = 178000;

* NREL ATB 2019 (NPD 2)
oC('Hydro') = 31000;

* NREL ATB 2019 (Coal-IGCC-AvgCF)
oC('IGCC') = 54000;

* ??
oC('Landfill_Gas') = 50000;

* estimated to be similar to a cofired biopower plant
oC('Municipal_Solid_Waste') = 33000;
oC('Non_Fossil_Waste') = 33000;
oC('Tires') = 33000;

* NREL ATB 2019
oC('Nuclear') = 101000;

* ??
oC('OG_Steam') = 45000;

* NREL ATB 2019 (TRG 3 - Offshore Fixed)
oC('Offshore_Wind') = 134000;

* NREL ATB 2019
oC('Onshore_Wind') = 44000;

* ??
oC('Pumped_Storage') = 75000;

* NREL ATB 2019 (Utility PV)
oC('Solar_PV') = 20000;

* NREL ATB 2019 (CSP - 10hrs TES - Class 1)
oC('Solar_Thermal') = 66000;

* NREL ATB 2019 (Utility PV)
oC(nrel_solar(k)) = 20000;

* NREL ATB 2019
oC(all_onwind(k)) = 44000;

* NREL ATB 2019 (TRG 3 - Offshore Fixed)
oC(all_offwind(k)) = 134000;


PARAMETER gC(k) 'SRMC [fuel + variable O&M costs] (units: $/MWh/year)';
* NREL ATB 2019 (Battery Storage - Mid - 2020)
gC('Energy_Storage_fast') = 0;
gC('Energy_Storage_med') = 0;
gC('Energy_Storage_slow') = 0;

* NREL ATB 2019 (Dedicated)
gC('Biomass') = 47;

* NREL ATB 2019 (Coal-new-ConstantCF)
gC('Coal_Steam') = 23;

* NREL ATB 2019 (Gas-CC-AvgCF)
gC('Combined_Cycle') = 24;

* NREL ATB 2019 (Gas-CT-AvgCF)
gC('Combustion_Turbine') = 40;

* ??
gC('Fossil_Waste') = 47;

* ??
gC('Fuel_Cell') = 5;

* NREL ATB 2019 (GEO-Hydro Binary example)
gC('Geothermal') = 0;

* NREL ATB 2019 (NPD 2)
gC('Hydro') = 0;

* NREL ATB 2019 (Coal-IGCC-AvgCF)
gC('IGCC') = 26;

* ??
gC('Landfill_Gas') = 50;

* estimated to be similar to a cofired biopower plant
gC('Municipal_Solid_Waste') = 35;
gC('Non_Fossil_Waste') = 35;
gC('Tires') = 35;

* NREL ATB 2019
gC('Nuclear') = 9;

* ??
gC('OG_Steam') = 30;

* NREL ATB 2019 (TRG 3 - Offshore Fixed)
gC('Offshore_Wind') = 0;

* NREL ATB 2019
gC('Onshore_Wind') = 0;

* ??
gC('Pumped_Storage') = 5;

* NREL ATB 2019 (Utility PV)
gC('Solar_PV') = 0;

* NREL ATB 2019 (CSP - 10hrs TES - Class 1)
gC('Solar_Thermal') = 3.5;

* NREL ATB 2019 (Utility PV)
gC(nrel_solar(k)) = 0;
*--------------------





*--------------------
* Load Duration Curve (LDC) data
*--------------------
PARAMETER load_description(*,regions);
load_description("ev",i) = sum(time(epoch,hrs), sum(fips$map_aggr(i,fips), ev_load(epoch,hrs,fips))) / CARD(hrs);

load_description("new_baseload",i) = sum(time(epoch,hrs), sum(fips$map_aggr(i,fips), ldc_raw_scaled(epoch,hrs,fips))) / CARD(hrs);

load_description("2020",i) = sum(time(epoch,hrs), sum(fips$map_aggr(i,fips), ldc_raw_scaled(epoch,hrs,fips))) / CARD(hrs);


PARAMETER ldc_container(epoch,hrs,regions,*) 'load duration curve';

ldc_container(time(epoch,hrs),i,"2020") = sum(fips$map_aggr(i,fips), ldc_raw(epoch,hrs,fips));

ldc_container(time(epoch,hrs),i,"new_baseload") = sum(fips$map_aggr(i,fips), ldc_raw_scaled(epoch,hrs,fips));

ldc_container(time(epoch,hrs),i,"ev") = sum(fips$map_aggr(i,fips), ev_load(epoch,hrs,fips));

ldc_container(time(epoch,hrs),i,"total") = sum(fips$map_aggr(i,fips), ldc_raw_scaled(epoch,hrs,fips) + ev_load(epoch,hrs,fips));
*--------------------


EXECUTE_UNLOAD "%output_gdx%";
