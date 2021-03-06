$TITLE Wisconsin Renewable Energy Model -- WEREWOLF
* areas to fix are denoated with an XXXX flag

$SETENV GDXCOMPRESS 1
$IFTHENI %system.filesys% == UNIX $SET sep "/"
$ELSE $SET sep "\"
$ENDIF

$ONEMPTY

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

SET offshore_fips(regions) 'FIPS codes that have shoreline';
$LOAD offshore_fips

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

SET nrel_solar(k) 'solar PV technologies';
$LOADDC nrel_solar

SET all_wind(k) 'all wind technolgoies';
$LOADDC all_wind

SET all_offwind(k) 'all offshore wind technolgoies';
$LOADDC all_offwind

SET all_onwind(k) 'all onshore wind technolgoies';
$LOADDC all_onwind

SET all_solar(k) 'all solar technolgoies';
$LOADDC all_solar

SET all_solar_PV(k) 'all solar PV technolgoies';
$LOADDC all_solar_PV

SET all_distsolar_PV(k) 'all distributed solar PV technolgoies';
$LOADDC all_distsolar_PV

SET all_utilsolar_PV(k) 'all utility scale solar PV technolgoies';
$LOADDC all_utilsolar_PV

SET all_solar_therm(k) 'all utility scale solar thermal technolgoies';
$LOADDC all_solar_therm

SET map_fips_ipm(regions,regions) 'map between FIPS5 codes and IPM regions';
$LOADDC map_fips_ipm

SET map_uid_fips(uid,regions) 'map between unit generator ID and FIPS5 codes';
$LOADDC map_uid_fips

SET map_fips_state(regions,regions) 'map between FIPS5 codes and states';
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
*-----------------



*-----------------
* LOAD PARAMETERS
*-----------------
PARAMETER nrel_solar_cap(k,regions) 'solar potential capacity (units: MW)';
$LOADDC nrel_solar_cap

PARAMETER nrel_solar_cost(k,regions) 'solar costs (units: $/MW)';
$LOADDC nrel_solar_cost

PARAMETER nrel_solar_cf(k,regions,hrs) 'solar capacity factor (units: unitless)';
$LOADDC nrel_solar_cf

PARAMETER nrel_wind_cap(k,regions) 'wind potential capacity (units: MW)';
$LOADDC nrel_wind_cap

PARAMETER nrel_wind_cost(k,regions) 'wind costs (units: $/MW)';
$LOADDC nrel_wind_cost

PARAMETER nrel_wind_cf(k,regions,hrs) 'wind capacity factor (units: unitless)';
$LOADDC nrel_wind_cf

PARAMETER ldc_raw(epoch,hrs,regions) 'load duration curves for 2020';
$LOADDC ldc_raw

PARAMETER lat(regions) 'latitude';
$LOADDC lat

PARAMETER lng(regions) 'longitude';
$LOADDC lng

PARAMETER miso_gen(regions,k,*) 'Projects listed in the MISO Generation Interconnection Queue';
$LOAD miso_gen

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

nrel_solar_cost(nrel_solar,fips) = sum(reeds_balauth$map_fips_reeds_balauth(fips,reeds_balauth), nrel_solar_cost(nrel_solar,reeds_balauth));

nrel_solar_cap(nrel_solar,fips) = sum(reeds_balauth$map_fips_reeds_balauth(fips,reeds_balauth), nrel_solar_cap(nrel_solar,reeds_balauth) / n_fips(reeds_balauth));
*--------------------



*--------------------
* Diaggregate NREL Wind Data (reeds_regions) to FIPS level
*--------------------
nrel_wind_cf(k,fips,hrs) = sum(reeds_regions$map_fips_reeds_regions(fips,reeds_regions), nrel_wind_cf(k,reeds_regions,hrs));

nrel_wind_cost(k,fips) = sum(reeds_regions$map_fips_reeds_regions(fips,reeds_regions), nrel_wind_cost(k,reeds_regions));

* onshore wind
nrel_wind_cap(all_onwind,fips) = sum(reeds_regions$map_fips_reeds_regions(fips,reeds_regions), nrel_wind_cap(all_onwind,reeds_regions) / n_fips(reeds_regions));

* offshore wind
PARAMETER n_fips_offshore(regions);
n_fips_offshore(reeds_regions) = sum(fips$(map_fips_reeds_regions(fips,reeds_regions) AND offshore_fips(fips)), 1);

nrel_wind_cap(all_offwind,fips) = sum(reeds_regions$(map_fips_reeds_regions(fips,reeds_regions) AND offshore_fips(fips)), nrel_wind_cap(all_offwind,reeds_regions) / n_fips_offshore(reeds_regions));
*--------------------


*--------------------
* Geographic Parameter Mapping
*--------------------
* calculate average lat/lng for different geographic regions
lat(state) = sum(fips$map_fips_state(fips,state), lat(fips)) / sum(fips$map_fips_state(fips,state), 1);
lat(ipm) = sum(fips$map_fips_ipm(fips,ipm), lat(fips)) / sum(fips$map_fips_ipm(fips,ipm), 1);
lat(reeds_regions) = sum(fips$map_fips_reeds_regions(fips,reeds_regions), lat(fips)) / sum(fips$map_fips_reeds_regions(fips,reeds_regions), 1);
lat(reeds_balauth) = sum(fips$map_fips_reeds_balauth(fips,reeds_balauth), lat(fips)) / sum(fips$map_fips_reeds_balauth(fips,reeds_balauth), 1);

lng(state) = sum(fips$map_fips_state(fips,state), lng(fips)) / sum(fips$map_fips_state(fips,state), 1);
lng(ipm) = sum(fips$map_fips_ipm(fips,ipm), lng(fips)) / sum(fips$map_fips_ipm(fips,ipm), 1);
lng(reeds_regions) = sum(fips$map_fips_reeds_regions(fips,reeds_regions), lng(fips)) / sum(fips$map_fips_reeds_regions(fips,reeds_regions), 1);
lng(reeds_balauth) = sum(fips$map_fips_reeds_balauth(fips,reeds_balauth), lng(fips)) / sum(fips$map_fips_reeds_balauth(fips,reeds_balauth), 1);
*--------------------
