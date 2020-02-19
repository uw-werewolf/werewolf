$TITLE Wisconsin Renewable Energy Model -- WEREWOLF
* areas to fix are denoated with an XXXX flag

$SETENV GDXCOMPRESS 1
$IFTHENI %system.filesys% == UNIX $SET sep "/"
$ELSE $SET sep "\"
$ENDIF

$ONEMPTY
SCALAR myerrorlevel;


*-----------------
* LOAD SETS
*-----------------
$GDXIN 'werewolf_data.gdx'
SET k 'all technolgy types in the model';
$LOAD k

SET uid 'unique id numbers from EPA NEEDS database';
$LOAD uid

SET hrs 'hours in a year';
$LOAD hrs

SET cost_bin 'cost bin';
$LOAD cost_bin

SET epoch 'timestamp';
$LOAD epoch

SET time(epoch,hrs) 'relationship between epoch and hrs';
$LOADDC time

SET add_regions 'new regions in model' / MI_UP, IL_CHI, IL_OTH /;

SET data_regions 'all regions in the data';
$LOAD data_regions=regions

SET regions 'all regions' / #add_regions, #data_regions /;

SET state(regions) 'All states';
$LOAD state

SET fips(regions) 'All FIPS codes';
$LOAD fips

SET ipm(regions) 'IPM regions';
$LOAD ipm

SET reeds_balauth(regions) 'NREL ReEDS balancing authority regions';
$LOAD reeds_balauth

SET reeds_regions(regions) 'NREL ReEDS regions';
$LOAD reeds_regions

SET a 'model agent type';
$LOAD a

SET prodn(a) 'model agent type that generates electricity';
$LOAD prodn

SET gen(k) 'all electricty generation technolgy types in the model';
$LOADDC gen

SET hydro(k) 'hydro technologies';
$LOADDC hydro

SET renew(k) 'renewable technologies';
$LOADDC renew

SET nuclear(k) 'nuclear technologies';
$LOADDC nuclear

SET geothermal(k) 'geothermal technologies';
$LOADDC geothermal

SET fossil(k) 'fossil technologies';
$LOADDC fossil

SET store(k) 'storage technologies';
$LOADDC store

SET battery(k) 'battery technologies';
$LOADDC battery

SET nrel_solar_PV(k) 'solar PV technologies';
$LOADDC nrel_solar_PV

SET nrel_onwind(k) 'onshore wind technologies';
$LOADDC nrel_onwind

SET nrel_offwind(k) 'offshore wind technologies';
$LOADDC nrel_offwind

SET map_fips_ipm(regions,regions) 'map between FIPS5 codes and IPM regions';
$LOADDC map_fips_ipm

SET map_uid_fips(uid,regions) 'map between unit generator ID and FIPS5 codes';
$LOADDC map_uid_fips

SET map_fips_state(regions,regions) 'map between FIPS5 codes and IPM regions';
$LOADDC map_fips_state

SET map_uid_ipm(uid,regions) 'map between unit generator ID and IPM regions';
$LOADDC map_uid_ipm

SET map_uid_type(uid,k) 'map between unit generator ID and generation technolgy type';
$LOADDC map_uid_type

SET map_fips_reeds_balauth(regions,regions) 'map between FIPS5 codes and NREL ReEDS balancing authority regions';
$LOADDC map_fips_reeds_balauth

SET map_fips_reeds_regions(regions,regions) 'map between FIPS5 codes and NREL ReEDS regions';
$LOADDC map_fips_reeds_regions

ALIAS(fips,fips_p);
ALIAS(cost_bin,cost_bin_p);
*-----------------



*-----------------
* LOAD PARAMETERS
*-----------------
PARAMETER nrel_solar_cap(k,regions,cost_bin) 'solar potential capacity (units: MW)';
$LOADDC nrel_solar_cap

PARAMETER nrel_solar_cost(k,regions,cost_bin) 'solar costs (units: $/MW)';
$LOADDC nrel_solar_cost

PARAMETER nrel_solar_cf(k,regions,hrs) 'solar capacity factor (units: unitless)';
$LOADDC nrel_solar_cf

PARAMETER nrel_wind_cap(k,regions,cost_bin) 'wind potential capacity (units: MW)';
$LOADDC nrel_wind_cap

PARAMETER nrel_wind_cost(k,regions,cost_bin) 'wind costs (units: $/MW)';
$LOADDC nrel_wind_cost

PARAMETER nrel_wind_cf(k,regions,hrs) 'wind capacity factor (units: unitless)';
$LOADDC nrel_wind_cf

PARAMETER ldc_raw(epoch,hrs,regions) 'raw load duration curves';
$LOADDC ldc_raw

PARAMETER lat(regions) 'latitude';
$LOADDC lat

PARAMETER lng(regions) 'longitude';
$LOADDC lng

PARAMETER population(regions) 'population (units: count)';
$LOADDC population


* calculate aggregate population figures
population(state) = sum(fips$map_fips_state(fips,state), population(fips));
population(ipm) = sum(fips$map_fips_ipm(fips,ipm), population(fips));
population(reeds_balauth) = sum(fips$map_fips_reeds_balauth(fips,reeds_balauth), population(fips));
population(reeds_regions) = sum(fips$map_fips_reeds_regions(fips,reeds_regions), population(fips));

PARAMETER wp(fips,ipm) 'population weighting (unitless)';
wp(fips,ipm) = (population(fips) / population(ipm))$map_fips_ipm(fips,ipm);

PARAMETER cap(uid) 'generation nameplate capacity (units: MW)';
$LOADDC cap

PARAMETER hr(uid) 'generator efficiency (i.e., heat rate) (units: Btu/kWh)';
$LOADDC hr


* check for correct weight factors, otherwise abort
PARAMETER w_chk(ipm);
w_chk(ipm) = sum(fips, wp(fips,ipm));
w_chk(ipm) = round(w_chk(ipm), 3);
display w_chk;
LOOP(ipm, ABORT$(w_chk(ipm) <> 1.000) 'population weight factors are wrong for some reason');
*-----------------



*--------------------
* Other model data
*--------------------
SCALAR lifetime 'plant lifetime (unit: years)' / 25 /;
*--------------------



*--------------------
* Calculate number of fips regions per other region
*--------------------
parameter n_fips(regions);
n_fips(reeds_balauth) = sum(fips$map_fips_reeds_balauth(fips,reeds_balauth), 1);
n_fips(reeds_regions) = sum(fips$map_fips_reeds_regions(fips,reeds_regions), 1);
*--------------------



*--------------------
* Diaggregate LDCs to FIPS level
*--------------------
ldc_raw(time(epoch,hrs),fips) = sum(ipm$map_fips_ipm(fips,ipm), wp(fips,ipm) * ldc_raw(epoch,hrs,ipm));
*--------------------



*--------------------
* Diaggregate NREL Solar Data (reeds_balauth) to FIPS level
*--------------------
nrel_solar_cf(k,fips,hrs) = sum(reeds_balauth$map_fips_reeds_balauth(fips,reeds_balauth), nrel_solar_cf(k,reeds_balauth,hrs));

nrel_solar_cost(k,fips,cost_bin) = sum(reeds_balauth$map_fips_reeds_balauth(fips,reeds_balauth), nrel_solar_cost(k,reeds_balauth,cost_bin));

nrel_solar_cap(k,fips,cost_bin) = sum(reeds_balauth$map_fips_reeds_balauth(fips,reeds_balauth), nrel_solar_cap(k,reeds_balauth,cost_bin) / n_fips(reeds_balauth));
*--------------------



*--------------------
* Diaggregate NREL Wind Data (reeds_regions) to FIPS level
*--------------------
nrel_wind_cf(k,fips,hrs) = sum(reeds_regions$map_fips_reeds_regions(fips,reeds_regions), nrel_wind_cf(k,reeds_regions,hrs));

nrel_wind_cost(k,fips,cost_bin) = sum(reeds_regions$map_fips_reeds_regions(fips,reeds_regions), nrel_wind_cost(k,reeds_regions,cost_bin));

nrel_wind_cap(k,fips,cost_bin) = sum(reeds_regions$map_fips_reeds_regions(fips,reeds_regions), nrel_wind_cap(k,reeds_regions,cost_bin) / n_fips(reeds_regions));
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
* calculate average lat/lng for different geographic regions
lat(state) = sum(fips$map_fips_state(fips,state), lat(fips)) / sum(fips$map_fips_state(fips,state), 1);
lat(ipm) = sum(fips$map_fips_ipm(fips,ipm), lat(fips)) / sum(fips$map_fips_ipm(fips,ipm), 1);
lat(i_aggr) = sum(fips$map_aggr(i_aggr,fips), lat(fips)) / sum(fips$map_aggr(i_aggr,fips), 1);
lat(reeds_regions) = sum(fips$map_fips_reeds_regions(fips,reeds_regions), lat(fips)) / sum(fips$map_fips_reeds_regions(fips,reeds_regions), 1);
lat(reeds_balauth) = sum(fips$map_fips_reeds_balauth(fips,reeds_balauth), lat(fips)) / sum(fips$map_fips_reeds_balauth(fips,reeds_balauth), 1);

lng(state) = sum(fips$map_fips_state(fips,state), lng(fips)) / sum(fips$map_fips_state(fips,state), 1);
lng(ipm) = sum(fips$map_fips_ipm(fips,ipm), lng(fips)) / sum(fips$map_fips_ipm(fips,ipm), 1);
lng(i_aggr) = sum(fips$map_aggr(i_aggr,fips), lng(fips)) / sum(fips$map_aggr(i_aggr,fips), 1);
lng(reeds_regions) = sum(fips$map_fips_reeds_regions(fips,reeds_regions), lng(fips)) / sum(fips$map_fips_reeds_regions(fips,reeds_regions), 1);
lng(reeds_balauth) = sum(fips$map_fips_reeds_balauth(fips,reeds_balauth), lng(fips)) / sum(fips$map_fips_reeds_balauth(fips,reeds_balauth), 1);
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

cap_agg(i,k) = sum(fips$map_aggr(i,fips), sum(uid$(map_uid_fips(uid,fips) AND map_uid_type(uid,k)), cap(uid)));
*--------------------




PARAMETER cap_nrel(k,regions) 'potential capacity (units: MW)';
*--------------------
* Merge NREL solar data into model regions
*--------------------
nrel_solar_cf(k,i,hrs) = sum(fips$map_aggr(i,fips), nrel_solar_cf(k,fips,hrs)) / sum(fips_p$map_aggr(i,fips_p), 1);

cap_nrel(nrel_solar_PV,i) = sum(fips$(map_aggr(i,fips)), sum(cost_bin, nrel_solar_cap(nrel_solar_PV,fips,cost_bin)));


PARAMETER w_cap(k,regions,regions,cost_bin) 'weight factor';
w_cap(nrel_solar_PV,i,fips,cost_bin)$(map_aggr(i,fips) AND sum(fips_p$map_aggr(i,fips_p), sum(cost_bin_p, nrel_solar_cap(nrel_solar_PV,fips_p,cost_bin_p))) <> 0) = nrel_solar_cap(nrel_solar_PV,fips,cost_bin) / sum(fips_p$map_aggr(i,fips_p), sum(cost_bin_p, nrel_solar_cap(nrel_solar_PV,fips_p,cost_bin_p)));

nrel_solar_cost(nrel_solar_PV,i,cost_bin) = sum(fips$map_aggr(i,fips), w_cap(nrel_solar_PV,i,fips,cost_bin) * nrel_solar_cost(nrel_solar_PV,fips,cost_bin));
*--------------------


*--------------------
* Merge NREL wind data into model regions
*--------------------
* simple average, should change to capacity weighted cost
nrel_wind_cf(k,i,hrs) = sum(fips$map_aggr(i,fips), nrel_wind_cf(k,fips,hrs)) / sum(fips_p$map_aggr(i,fips_p), 1);

* Onshore Wind
cap_nrel(nrel_onwind,i) = sum(fips$(map_aggr(i,fips)), sum(cost_bin, nrel_wind_cap(nrel_onwind,fips,cost_bin)));

w_cap(nrel_onwind,i,fips,cost_bin)$(map_aggr(i,fips) AND sum(fips_p$map_aggr(i,fips_p), sum(cost_bin_p, nrel_wind_cap(nrel_onwind,fips_p,cost_bin_p))) <> 0) = nrel_wind_cap(nrel_onwind,fips,cost_bin) / sum(fips_p$map_aggr(i,fips_p), sum(cost_bin_p, nrel_wind_cap(nrel_onwind,fips_p,cost_bin_p)));

nrel_wind_cost(nrel_onwind,i,cost_bin) = sum(fips$map_aggr(i,fips), w_cap(nrel_onwind,i,fips,cost_bin) * nrel_wind_cost(nrel_onwind,fips,cost_bin));



* Offshore Wind
cap_nrel(nrel_offwind,i) = sum(fips$(map_aggr(i,fips)), sum(cost_bin, nrel_wind_cap(nrel_offwind,fips,cost_bin)));

w_cap(nrel_offwind,i,fips,cost_bin)$(map_aggr(i,fips) AND sum(fips_p$map_aggr(i,fips_p), sum(cost_bin_p, nrel_wind_cap(nrel_offwind,fips_p,cost_bin_p))) <> 0) = nrel_wind_cap(nrel_offwind,fips,cost_bin) / sum(fips_p$map_aggr(i,fips_p), sum(cost_bin_p, nrel_wind_cap(nrel_offwind,fips_p,cost_bin_p)));

nrel_wind_cost(nrel_offwind,i,cost_bin) = sum(fips$map_aggr(i,fips), w_cap(nrel_offwind,i,fips,cost_bin) * nrel_wind_cost(nrel_offwind,fips,cost_bin));
*--------------------



*--------------------
* Financial data
*--------------------
PARAMETER eC(k,regions) 'capital costs (units: $/MW/year)';
* input data has units of $/kW
eC('Battery_fast',i) = 2813;
eC('Battery_med',i) = 2813;
eC('Battery_slow',i) = 2813;
eC('Biomass',i) = 2198;
eC('Coal_Steam',i) = 1021;
eC('Combined_Cycle',i) = 1021;
eC('Combustion_Turbine',i) = 717;
eC('Fossil_Waste',i) = 3250;
eC('Fuel_Cell',i) = 3250;
eC('Geothermal',i) = 3000;
eC('Hydro',i) = 5312;
eC('IGCC',i) = 1021;
eC('Landfill_Gas',i) = 1104;
eC('Municipal_Solid_Waste',i) = 4985;
eC('Non_Fossil_Waste',i) = 3250;
eC('Nuclear',i) = 5495;
eC('OG_Steam',i) = 678;
eC('Offshore_Wind',i) = 3260;
eC('Onshore_Wind',i) = 1630;
eC('Pumped_Storage',i) = 4000;
eC('Solar_PV',i) = 2434;
eC('Solar_Thermal',i) = 2800;
eC('Tires',i) = 4000;


* these units are already in $/MW/year... do not need to convert in next step
eC(nrel_solar_PV,i) = sum(fips$map_aggr(i,fips), sum(cost_bin, w_cap(nrel_solar_PV,i,fips,cost_bin) * nrel_solar_cost(nrel_solar_PV,fips,cost_bin)));

eC(nrel_onwind,i) = sum(fips$map_aggr(i,fips), sum(cost_bin, w_cap(nrel_onwind,i,fips,cost_bin) * nrel_wind_cost(nrel_onwind,fips,cost_bin)));

eC(nrel_offwind,i) = sum(fips$map_aggr(i,fips), sum(cost_bin, w_cap(nrel_offwind,i,fips,cost_bin) * nrel_wind_cost(nrel_offwind,fips,cost_bin)));

* convert to annualized capital costs (units: $/MW/year)
eC(k,i)$(NOT nrel_solar_PV(k) AND NOT nrel_onwind(k) AND NOT nrel_offwind(k)) = eC(k,i) * 1000 / lifetime;


PARAMETER oC(k) 'operating costs (units: $/MW/yr)' /
    'Battery_fast' 7000
    'Battery_med' 6000
    'Battery_slow' 5000
    'Biomass' 45000
    'Coal_Steam' 45000
    'Combined_Cycle' 15000
    'Combustion_Turbine' 15000
    'Fossil_Waste' 50000
    'Fuel_Cell' 10000
    'Geothermal' 20000
    'Hydro' 0
    'IGCC' 15000
    'Landfill_Gas' 50000
    'Municipal_Solid_Waste' 50000
    'Non_Fossil_Waste' 50000
    'Nuclear' 300000
    'OG_Steam' 45000
    'Offshore_Wind' 30000
    'Onshore_Wind' 20000
    'Pumped_Storage' 5000
    'Solar_PV' 35000
    'Solar_Thermal' 35000
    'Tires' 50000 /;

* XXXX needs refinement -- not assumed to be location dependent right now
oC(nrel_solar_PV(k)) = 35000;
oC(nrel_onwind(k)) = 20000;
oC(nrel_offwind(k)) = 30000;


PARAMETER gC(k) 'SRMC [fuel + variable O&M costs] (units: $/MWh)' /
    'Battery_fast' 0,
    'Battery_med' 0,
    'Battery_slow' 0,
    'Biomass' 70,
    'Coal_Steam' 48,
    'Combined_Cycle' 70,
    'Combustion_Turbine' 70,
    'Fossil_Waste' 35,
    'Fuel_Cell' 5,
    'Geothermal' 0,
    'Hydro' 6,
    'IGCC' 70,
    'Landfill_Gas' 50,
    'Municipal_Solid_Waste' 50,
    'Non_Fossil_Waste' 50,
    'Nuclear' 140,
    'OG_Steam' 93,
    'Offshore_Wind' 24,
    'Onshore_Wind' 12,
    'Pumped_Storage' 30,
    'Solar_PV' 2,
    'Solar_Thermal' 5,
    'Tires' 40 /;

* XXXX needs refinement -- not assumed to be location dependent right now
gC(nrel_solar_PV(k)) = 2;
gC(nrel_onwind(k)) = 12;
gC(nrel_offwind(k)) = 24;
*--------------------


*--------------------
* Load Duration Curve (LDC) data
*--------------------
PARAMETER ldc_container(epoch,hrs,regions) 'load duration curve';
ldc_container(time(epoch,hrs),i) = sum(fips$map_aggr(i,fips), ldc_raw(epoch,hrs,fips));
*--------------------



*--------------------
* OUTPUT: Generator Parameters
*--------------------
FILE cap_aggr /'.%sep%output%sep%capacity_aggr.csv'/;
PUT cap_aggr;
cap_aggr.PW = 32767;
PUT 'Region,GenType,Capacity (MW)' /;
loop((i,k), PUT i.tl:0 ',' k.tl:0 ',' cap_agg(i,k) /; );


FILE hr_average /'.%sep%output%sep%heat_rate_ave.csv'/;
PUT hr_average;
hr_average.PW = 32767;
PUT 'Region,GenType,Average Heat Rate (Btu/kWh)' /;
loop((i,k), PUT i.tl:0 ',' k.tl:0 ',' hr_ave(i,k) /; );
*--------------------




*--------------------
* OUTPUT: Node Map
*--------------------
* this code creates a map of all the nodes for QA purposes
EXECUTE_UNLOAD '.%sep%gdx_temp%sep%nodes.gdx' i, lat, lng, map_aggr;
EXECUTE 'python map_nodes.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: map_nodes.py did not finish successfully...";
*--------------------



*--------------------
* Transmission network triangulation data (reads from nodes.gdx)
*--------------------
* create the network triangulation
EXECUTE 'python create_network.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: create_network.py did not finish successfully...";
*--------------------



*--------------------
* OUTPUT: LDC plots
*--------------------
* this code creates all the load duration curves to be used in the model
EXECUTE_UNLOAD '.%sep%gdx_temp%sep%ldc.gdx' ldc_container, regions, hrs;
EXECUTE 'python create_ldcs.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: create_ldcs.py did not finish successfully...";




EXECUTE_UNLOAD '.%sep%gdx_temp%sep%processed_werewolf_data.gdx';
