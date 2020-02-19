$TITLE Wisconsin Renewable Energy Model -- WEREWOLF
* areas to fix are denoated with an XXXX flag
$SETENV GDXCOMPRESS 1
$IFTHENI %system.filesys% == UNIX $SET sep "/"
$ELSE $SET sep "\"
$ENDIF

$IF NOT SETGLOBAL almostsure $SETGLOBAL almostsure 0
$IF NOT SETGLOBAL wind_scn $SETGLOBAL wind_scn 10
$IF NOT SETGLOBAL hydro_scn $SETGLOBAL hydro_scn 1

$ONEMPTY



*-------------------
* LOAD Tranmission Network Data
*-------------------
SET i 'regions in the model';
SET ij(i,i) 'arcs in the network';

$GDXIN '.%sep%gdx_temp%sep%network_arcs.gdx'
$LOAD i<ij.dim1
$LOADDC ij
$GDXIN

ALIAS(i,j);

PARAMETER fcap(i,i) 'Transmission line capacity (units: MW)';
fcap(ij(i,j)) = 1000000;
*-------------------


*---------------------------
* LOAD Load Duration Curves
*---------------------------
SET t 'season';
SET b 'loadblock segments';
SET hrs 'hours in a year';
SET map_block_hour(i,b,hrs) 'map between regions, loadblocks and hours of the year';

PARAMETER ldc_compact(t,b,i) 'electrical demand (units: MW)';
PARAMETER loadblockhours_compact(t,b) '# of hours per loadblock';

$GDXIN '.%sep%gdx_temp%sep%ldc_fit.gdx'
$LOAD t<ldc_compact.dim1
$LOAD b<ldc_compact.dim2
$LOADDC ldc_compact

$LOAD hrs<map_block_hour.dim3
$LOADDC map_block_hour
$LOADDC loadblockhours_compact
$GDXIN
*-------------------



*-----------------
* LOAD general model data
*-----------------
SET k 'all technolgy types in the model';
SET uid 'unique id numbers from EPA NEEDS database';
SET a 'model agent type';
SET prodn(a) 'model agent type that generates electricity';
SET gen(k) 'all electricty generation technolgy types in the model';
SET hydro(k) 'hydro technologies';
SET renew(k) 'renewable technologies';
SET fossil(k) 'fossil technologies';
SET geothermal(k) 'geothermal technologies';
SET nuclear(k) 'nuclear technologies';
SET store(k) 'storage technologies';
SET battery(k) 'battery technologies';
SET nrel_solar_PV(k) 'solar PV technologies from NREL';
SET nrel_offwind(k) 'offshore wind technologies from NREL';
SET nrel_onwind(k) 'onshore wind technologies from NREL';
SET cost_bin 'cost bin';

$GDXIN '.%sep%werewolf_data.gdx'
$LOAD k, uid, a, prodn, fossil, cost_bin
$LOADDC gen, hydro, renew, store, nuclear, battery, geothermal, nrel_solar_PV, nrel_onwind, nrel_offwind
$GDXIN
*-----------------



*-------------------
* LOAD processed data (model specific subset from processed_werewolf_data.gdx)
*-------------------
SET not_cntlreg(i) 'all regions in model that are not subject to policy controls';
SET cntlreg(i) 'all regions in model that are subject to policy controls';
PARAMETER lat(i) 'latitude';
PARAMETER lng(i) 'longitude';
PARAMETER cap_agg(i,k) 'aggregated existing nameplate capacity at nodes (units: MW)';
PARAMETER cap_nrel(k,i) 'technology potential for differnt renewables (units: MW)';
PARAMETER hr_ave(i,k) 'average heat rate at nodes for each technology type (units: Btu/kWh)';
PARAMETER nrel_solar_cost(k,i,cost_bin) 'solar costs (units: $/MW)';
PARAMETER nrel_solar_cf(k,i,hrs) 'solar capacity factor (units: unitless)';
PARAMETER nrel_wind_cost(k,i,cost_bin) 'wind costs (units: $/MW)';
PARAMETER nrel_wind_cf(k,i,hrs) 'wind capacity factor (units: unitless)';

$GDXIN '.%sep%gdx_temp%sep%processed_werewolf_data.gdx'
$LOAD lat, lng, cap_agg, cap_nrel, hr_ave, not_cntlreg, cntlreg, nrel_solar_cf, nrel_solar_cost, nrel_wind_cf, nrel_wind_cost
$GDXIN
*-------------------



*-------------------
* Stochastic scenario index scheme
*-------------------
SET wn 'wind scenario index number' / w1*w%wind_scn% /;
SET hn 'hydro scenario index number' / h1*h%hydro_scn% /;
SET scn(t,wn,hn) 'scenario tuple' / #t.#wn.#hn /;
*-------------------



*-------------------
* DEFINE model data
*-------------------
SET fuels 'all fuels that can be burned to produce electricity' / propane, butane, butane_propane_mix, home_heating_and_diesel_fuel, kerosene, coal, natural_gas, gasoline, residual_heating_fuel_businesses_only, jet_fuel, aviation_gas, flared_natural_gas, petroleum_coke, other_petroleum_miscellaneous, anthracite, bituminous, subbituminous, lignite, coke, geothermal, municipal_solid_waste, tire_derived_fuel, waste_oil, none /;

* ref: https://www.eia.gov/environment/emissions/co2_vol_mass.php
PARAMETER kgCO2(fuels) 'emissions for fuel types (units: kgCO2/MMBtu)' /
    'propane' 63.07,
    'butane' 64.95,
    'butane_propane_mix' 64.01,
    'home_heating_and_diesel_fuel' 73.16,
    'kerosene' 72.30,
    'coal' 95.35,
    'natural_gas'	53.07,
    'gasoline' 71.30,
    'residual_heating_fuel_businesses_only' 78.79,
    'jet_fuel' 70.90,
    'aviation_gas' 69.20,
    'flared_natural_gas' 54.70,
    'petroleum_coke' 102.10,
    'other_petroleum_miscellaneous'	72.62,
    'anthracite' 103.70,
    'bituminous' 93.30,
    'subbituminous' 97.20,
    'lignite' 97.70,
    'coke' 114.12,
    'geothermal' 7.71,
    'municipal_solid_waste'	41.69,
    'tire_derived_fuel' 85.97,
    'waste_oil' 95.25
    'none' 0/;

SET map_gen_fuel(fuels,k) 'mapping between fuel types and generator types' /
    'none'.(#renew,#nuclear),
    'coal'.('Coal_Steam'),
    'natural_gas'.('Combined_Cycle', 'Combustion_Turbine', 'IGCC')
    'geothermal'. ('Geothermal'),
    'other_petroleum_miscellaneous'.('OG_Steam','Fossil_Waste'),
    'flared_natural_gas'.('Landfill_Gas'),
    'municipal_solid_waste'.('Municipal_Solid_Waste', 'Non_Fossil_Waste')
    'tire_derived_fuel'.('Tires') /;


PARAMETER MMTonnesCO2(i,k) 'emissions factor for a generator (units: million metric tons of CO2 per MWh)';
MMTonnesCO2(i,k) = sum(fuels$map_gen_fuel(fuels,k), hr_ave(i,k) * kgCO2(fuels) * (1/1e6) * 1000 * (1/1000) * (1/1e6));

OPTION MMTonnesCO2:0:0:1;
DISPLAY MMTonnesCO2;


SCALAR maxCarbon 'current CO2 emissions (units: million metric tons of CO2)';
SCALAR maxnrEnergy 'maximum non-renewable energy allowed (units: unknown)';
SCALAR maxNR 'current thermal generation capacity in WI (units: MW)';

* maxNR = sum(i$map_wi('WI',i), sum(k$fossil(k), cap_agg(i,k)));
* maxnrEnergy = sum(i$map_wi('WI',i), sum(k$fossil(k), cap_agg(i,k) * 8760));
* maxCarbon = sum(i$map_wi('WI',i), sum(k$fossil(k), cap_agg(i,k) ));

maxNR = sum(i$cntlreg(i), sum(k$fossil(k), cap_agg(i,k)));
maxnrEnergy = sum(i$cntlreg(i), sum(k$fossil(k), cap_agg(i,k) * 8760));
maxCarbon = sum((i,k)$cntlreg(i), MMTonnesCO2(i,k) * cap_agg(i,k) * 8760);

DISPLAY maxNR;
DISPLAY maxnrEnergy;
DISPLAY maxCarbon;


*--------------------
* Solar model data
*--------------------
* find the average capacity factor for solar systems
PARAMETER ave_solar_cf(t,i,k,b);
ave_solar_cf(t,i,k,b) = sum(hrs$(map_block_hour(i,b,hrs)), nrel_solar_cf(k,i,hrs)) / loadblockhours_compact(t,b);
*--------------------



*--------------------
* Wind model data
*--------------------
* create N wind scenarios to use
* wind capacify factor is randomly scaled by region (no correlation) for all hours in the top two loadblocks (b9,b8)

PARAMETER scn_nrel_wind_cf(t,wn,k,i,hrs);
loop(wn,

    scn_nrel_wind_cf(t,wn,k,i,hrs) = nrel_wind_cf(k,i,hrs);

    scn_nrel_wind_cf(t,wn,k,i,hrs)$(map_block_hour(i,'b9',hrs)) = uniform(0,1) * nrel_wind_cf(k,i,hrs);

    scn_nrel_wind_cf(t,wn,k,i,hrs)$(map_block_hour(i,'b8',hrs)) = uniform(0,1) * nrel_wind_cf(k,i,hrs);

    scn_nrel_wind_cf(t,wn,k,i,hrs)$(map_block_hour(i,'b7',hrs)) = uniform(0,1) * nrel_wind_cf(k,i,hrs);

    );

* make 'w1' scenario contain zero wind in first two loadblocks (extreme event)
scn_nrel_wind_cf(t,'w1',k,i,hrs)$(map_block_hour(i,'b9',hrs)) = 0;
scn_nrel_wind_cf(t,'w1',k,i,hrs)$(map_block_hour(i,'b8',hrs)) = 0;
scn_nrel_wind_cf(t,'w1',k,i,hrs)$(map_block_hour(i,'b7',hrs)) = 0;
scn_nrel_wind_cf(t,'w1',k,i,hrs)$(map_block_hour(i,'b6',hrs)) = 0;
scn_nrel_wind_cf(t,'w1',k,i,hrs)$(map_block_hour(i,'b5',hrs)) = 0;
scn_nrel_wind_cf(t,'w1',k,i,hrs)$(map_block_hour(i,'b4',hrs)) = 0;
scn_nrel_wind_cf(t,'w1',k,i,hrs)$(map_block_hour(i,'b3',hrs)) = 0;
scn_nrel_wind_cf(t,'w1',k,i,hrs)$(map_block_hour(i,'b2',hrs)) = 0;
scn_nrel_wind_cf(t,'w1',k,i,hrs)$(map_block_hour(i,'b1',hrs)) = 0;
scn_nrel_wind_cf(t,'w1',k,i,hrs)$(map_block_hour(i,'b0',hrs)) = 0;



* take this new scenario data and average the capacity factors by loadblock
PARAMETER ave_wind_cf(t,wn,i,k,b);
ave_wind_cf(t,wn,i,k,b) = sum(hrs$(map_block_hour(i,b,hrs)), scn_nrel_wind_cf(t,wn,k,i,hrs)) / loadblockhours_compact(t,b);
*--------------------


*--------------------
* Hydro model data
*--------------------
* create N hydro scenarios to use
* wind capacify factor is randomly scaled by region (no correlation) for all hours in the top two loadblocks (b9,b8)

PARAMETER scn_hydro_cf(t,hn,k,i,hrs);

loop(hn,

    scn_hydro_cf(t,hn,hydro,i,hrs) = uniform(0.4,0.6);
    scn_hydro_cf(t,hn,hydro,i,hrs)$(map_block_hour(i,'b9',hrs)) = uniform(0.4,0.6);
    scn_hydro_cf(t,hn,hydro,i,hrs)$(map_block_hour(i,'b8',hrs)) = uniform(0.4,0.6);

    );

* make 'h1' scenario contain zero hydro in first two loadblocks (extreme event)
scn_hydro_cf(t,'h1',hydro,i,hrs)$(map_block_hour(i,'b9',hrs)) = 0;
scn_hydro_cf(t,'h1',hydro,i,hrs)$(map_block_hour(i,'b8',hrs)) = 0;
scn_hydro_cf(t,'h1',hydro,i,hrs)$(map_block_hour(i,'b7',hrs)) = 0;
scn_hydro_cf(t,'h1',hydro,i,hrs)$(map_block_hour(i,'b6',hrs)) = 0;
scn_hydro_cf(t,'h1',hydro,i,hrs)$(map_block_hour(i,'b5',hrs)) = 0;
scn_hydro_cf(t,'h1',hydro,i,hrs)$(map_block_hour(i,'b4',hrs)) = 0;
scn_hydro_cf(t,'h1',hydro,i,hrs)$(map_block_hour(i,'b3',hrs)) = 0;
scn_hydro_cf(t,'h1',hydro,i,hrs)$(map_block_hour(i,'b2',hrs)) = 0;
scn_hydro_cf(t,'h1',hydro,i,hrs)$(map_block_hour(i,'b1',hrs)) = 0;
scn_hydro_cf(t,'h1',hydro,i,hrs)$(map_block_hour(i,'b0',hrs)) = 0;




* take this new scenario data and average the capacity factors by loadblock
PARAMETER ave_hydro_cf(t,hn,i,k,b);
ave_hydro_cf(t,hn,i,k,b) = sum(hrs$(map_block_hour(i,b,hrs)), scn_hydro_cf(t,hn,k,i,hrs)) / loadblockhours_compact(t,b);
*--------------------


*--------------------
* Battery model data
*--------------------
PARAMETER chargerate(k) 'battery charge rate (units: MW)' /
    'battery_fast' 2.7660
    'battery_med' 0.8846
    'battery_slow' 0.1617 /;
*--------------------



*--------------------
* Generator capacity control parameters
*--------------------
PARAMETER capU(a,i,k) 'agent-based nameplate capacity at nodes (units: MW)';
capU('fossil_gen_agent',i,k) = cap_agg(i,k)$(fossil(k) OR nuclear(k) OR geothermal(k));
capU('renew_gen_agent',i,k) = cap_agg(i,k)$renew(k);


* u(a,i,k) limits investments into certain categories
PARAMETER u(a,i,k) 'agent-based ADDITIONAL capacity options at nodes in 2035 (MW)';

* restrict investment to model regions in WI
u('fossil_gen_agent',not_cntlreg,k) = 0;
u('renew_gen_agent',not_cntlreg,k) = 0;


* additional fossil generation
u('fossil_gen_agent',cntlreg,'Coal_Steam') = 0;
u('fossil_gen_agent',cntlreg,'Combined_Cycle') = u('fossil_gen_agent',cntlreg,'Combined_Cycle') * 0.2;
u('fossil_gen_agent',cntlreg,'Combustion_Turbine') = u('fossil_gen_agent',cntlreg,'Combustion_Turbine') * 0.2;
u('fossil_gen_agent',cntlreg,'Fossil_Waste') = 0;
u('fossil_gen_agent',cntlreg,'IGCC') = u('fossil_gen_agent',cntlreg,'IGCC') * 0.2;
u('fossil_gen_agent',cntlreg,'Landfill_Gas') = 0;
u('fossil_gen_agent',cntlreg,'Municipal_Solid_Waste') = 0;
u('fossil_gen_agent',cntlreg,'Non_Fossil_Waste') = 0;
u('fossil_gen_agent',cntlreg,'OG_Steam') = 0;
u('fossil_gen_agent',cntlreg,'Tires') = 0;

* additional nuclear generation
u('fossil_gen_agent',cntlreg,nuclear) = 0;

* additional geothermal generation
u('fossil_gen_agent',cntlreg,geothermal) = 0;

* additional storage generation
* u('renew_gen_agent',cntlreg,battery) = 0;
u('renew_gen_agent',cntlreg,'Battery_fast') = 0;
u('renew_gen_agent',cntlreg,'Battery_med') = 10;
u('renew_gen_agent',cntlreg,'Battery_slow') = 10;

* generalized growth of all renewables
u('renew_gen_agent',cntlreg,k) = capU('renew_gen_agent',cntlreg,k) * 0.1;

* No addl capacity... forces investment into NREL technology types (solar PV, on/offshore wind)
u('renew_gen_agent',cntlreg,'Solar_PV') = 0;
u('renew_gen_agent',cntlreg,'Onshore_Wind') = 0;
u('renew_gen_agent',cntlreg,'Offshore_Wind') = 0;

* Add in total technology potential for NREL technology types
u('renew_gen_agent',cntlreg,nrel_solar_PV) = cap_nrel(nrel_solar_PV,cntlreg);
u('renew_gen_agent',cntlreg,nrel_onwind) = cap_nrel(nrel_onwind,cntlreg);
u('renew_gen_agent',cntlreg,nrel_offwind) = cap_nrel(nrel_offwind,cntlreg);

OPTION u:0:0:1;
DISPLAY u;

FILE uu /'.%sep%output%sep%potentialcapacity_aggr.csv'/;
PUT uu;
uu.PW = 32767;
PUT 'Agent,Region,GenType,Potential Capacity (MW)' /;
loop((a,i,k), PUT a.tl:0 ',' i.tl:0 ',' k.tl:0 ',' u(a,i,k) /; );
*--------------------


SET used(a);
used(a) = yes;

* Derived parameters
* PARAMETER storagegatewidth;
* storagegatewidth = 500;

PARAMETER eff(k) 'battery efficiency parameter';
eff(battery) = 0.80;

PARAMETER coeff(k) 'nonlinear coefficient for gcost marginal cost curve macro';
coeff(k) = 0.001;


PARAMETER loadblockdays_compact(t,i);
loadblockdays_compact(t,i) = sum(b, loadblockhours_compact(t,b)) / 24;


*--------------------
* Capacity factor container
*--------------------
PARAMETER tmu(t,wn,hn,i,k,b) 'capacity factor data container (units: unitless)';

* follow Philpott -- most technologies have a CF = 1 unless wind/solar/hydro
tmu(scn(t,wn,hn),i,k,b) = 1;
tmu(scn(t,wn,hn),i,geothermal,b) = 0.85;

* Add hydro intermittency
tmu(scn(t,wn,hn),i,hydro,b) = ave_hydro_cf(t,hn,i,hydro,b);

* Add wind intermittency
* need to assume a CF for generic 'On/Offshore_Wind' technologies
tmu(scn(t,wn,hn),i,'Onshore_Wind',b) = ave_wind_cf(t,wn,i,'Onshore_Wind_2',b);
tmu(scn(t,wn,hn),i,'Offshore_Wind',b) = ave_wind_cf(t,wn,i,'Offshore_Wind_2',b);
tmu(scn(t,wn,hn),i,nrel_onwind,b) = ave_wind_cf(t,wn,i,nrel_onwind,b);
tmu(scn(t,wn,hn),i,nrel_offwind,b) = ave_wind_cf(t,wn,i,nrel_offwind,b);

* Add solar capacity factors
* need to assume a CF for generic 'Solar_PV' technologies
tmu(scn(t,wn,hn),i,'Solar_PV',b) = ave_solar_cf(t,i,'SolarUtil_PV_2',b);
tmu(scn(t,wn,hn),i,nrel_solar_PV,b) = ave_solar_cf(t,i,nrel_solar_PV,b);

* scenario weightings
PARAMETER wprob(t,wn,hn);
wprob(t,wn,hn)$scn(t,wn,hn) = 1 / card(scn);

PARAMETER loadblockhours(t,wn,hn,b) '# of hours per loadblock';
PARAMETER ldc(t,wn,hn,a,b,i) 'agent-based electrical demand (units: MW)';
* PARAMETER loadblockdays(t,wn,hn,i);

loadblockhours(scn(t,wn,hn),b) = loadblockhours_compact(t,b);
ldc(scn(t,wn,hn),'demand_agent',b,i) = ldc_compact(t,b,i);
* loadblockdays(scn(t,wn,hn),i) = loadblockdays_compact(t,i);
