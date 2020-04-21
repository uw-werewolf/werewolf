$TITLE Wisconsin Renewable Energy Model -- WEREWOLF
* areas to fix are denoated with an XXXX flag
$SETENV GDXCOMPRESS 1
$IFTHENI %system.filesys% == UNIX $SET sep "/"
$ELSE $SET sep "\"
$ENDIF

$IF NOT SETGLOBAL almostsure $SETGLOBAL almostsure 0
$IF NOT SETGLOBAL wind_scn $SETGLOBAL wind_scn 10
$IF NOT SETGLOBAL solar_scn $SETGLOBAL solar_scn 1
$IF NOT SETGLOBAL hydro_scn $SETGLOBAL hydro_scn 1
$IF NOT SETGLOBAL solar_data_output $SETGLOBAL solar_data_output 0


$ONEMPTY
SCALAR myerrorlevel;
SCALAR almostsure / %almostsure% /;

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
SET all_wind(k) 'all wind technolgoies';
SET all_offwind(k) 'all offshore wind technolgoies';
SET all_onwind(k) 'all onshore wind technolgoies';
SET all_solar(k) 'all solar technolgoies';
SET all_solar_PV(k) 'all solar PV technolgoies';
SET all_distsolar_PV(k) 'all distributed solar PV technolgoies';
SET all_utilsolar_PV(k) 'all utility scale solar PV technolgoies';
SET all_solar_therm(k) 'all utility scale solar thermal technolgoies';

$GDXIN '.%sep%werewolf_data.gdx'
$LOAD k, uid, a, prodn, fossil, cost_bin
$LOADDC gen, hydro, renew, store, nuclear, battery, geothermal, nrel_solar_PV, nrel_onwind, nrel_offwind, all_wind, all_offwind, all_onwind, all_solar, all_solar_PV, all_distsolar_PV, all_utilsolar_PV, all_solar_therm
$GDXIN
*-----------------



*-------------------
* LOAD processed data (model specific subset from processed_werewolf_data.gdx)
*-------------------
SET not_cntlreg(i) 'all regions in model that are not subject to policy controls';
SET cntlreg(i) 'all regions in model that are subject to policy controls';
PARAMETER growth_factor;
PARAMETER lat(i) 'latitude';
PARAMETER lng(i) 'longitude';
PARAMETER map_center 'lat/lng for the center of all modeled regions';
PARAMETER cap_agg(i,k) 'aggregated existing nameplate capacity at nodes (units: MW)';
PARAMETER cap_nrel(k,i) 'technology potential for differnt renewables (units: MW)';
PARAMETER hr_ave(i,k) 'average heat rate at nodes for each technology type (units: Btu/kWh)';
PARAMETER nrel_solar_cost(k,i,cost_bin) 'solar costs (units: $/MW)';
PARAMETER nrel_solar_cf(k,i,hrs) 'solar capacity factor (units: unitless)';
PARAMETER nrel_wind_cost(k,i,cost_bin) 'wind costs (units: $/MW)';
PARAMETER nrel_wind_cf(k,i,hrs) 'wind capacity factor (units: unitless)';

$GDXIN '.%sep%gdx_temp%sep%processed_werewolf_data.gdx'
$LOAD lat, lng, map_center, cap_agg, cap_nrel, hr_ave, not_cntlreg, cntlreg, nrel_solar_cf, nrel_solar_cost, nrel_wind_cf, nrel_wind_cost, growth_factor
$GDXIN
*-------------------



*-------------------
* Stochastic scenario index scheme
*-------------------
SET wn 'wind scenario index number' / w1*w%wind_scn% /;
SET sn 'solar scenario index number' / s1*s%solar_scn% /;
SET hn 'hydro scenario index number' / h1*h%hydro_scn% /;
SET scn(t,wn,sn,hn) 'scenario tuple' / #t.#wn.#sn.#hn /;
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
* $IFTHEN %solar_data_output% == 1
* EXECUTE_UNLOAD '.%sep%gdx_temp%sep%solar_data.gdx', nrel_solar_cf, map_block_hour, loadblockhours_compact;
*
* EXECUTE 'python solar_data.py > %system.nullfile%';
* myerrorlevel = errorlevel;
* ABORT$(myerrorlevel <> 0) "ERROR: solar_data.py did not finish successfully...";
* $ENDIF

* create N solar scenarios to use
PARAMETER scn_nrel_solar_cf(t,sn,k,i,hrs);
loop(sn,

    scn_nrel_solar_cf(t,sn,k,i,hrs) = nrel_solar_cf(k,i,hrs);

    loop(b, scn_nrel_solar_cf(t,sn,k,i,hrs)$(map_block_hour(i,b,hrs)) = uniform(0,1) * nrel_solar_cf(k,i,hrs)

        );
    );

* * make 's1' scenario contain zero solar in first two loadblocks (extreme event)
* scn_nrel_solar_cf(t,'s1',k,i,hrs)$(map_block_hour(i,'b9',hrs)) = 0;
* scn_nrel_solar_cf(t,'s1',k,i,hrs)$(map_block_hour(i,'b8',hrs)) = 0;


* take this new scenario data and average the capacity factors by loadblock
PARAMETER ave_solar_cf(t,sn,i,k,b);
ave_solar_cf(t,sn,i,k,b) = sum(hrs$(map_block_hour(i,b,hrs)), scn_nrel_solar_cf(t,sn,k,i,hrs)) / loadblockhours_compact(t,b);
*--------------------



*--------------------
* Wind model data
*--------------------
* create N wind scenarios to use
PARAMETER scn_nrel_wind_cf(t,wn,k,i,hrs);
loop(wn,

    scn_nrel_wind_cf(t,wn,k,i,hrs) = nrel_wind_cf(k,i,hrs);

    loop(b, scn_nrel_wind_cf(t,wn,k,i,hrs)$(map_block_hour(i,b,hrs)) = uniform(0,1) * nrel_wind_cf(k,i,hrs)

        );
    );

* make 'w1' scenario contain zero wind in first two loadblocks (extreme event)
scn_nrel_wind_cf(t,'w1',k,i,hrs)$(map_block_hour(i,'b9',hrs)) = 0;
scn_nrel_wind_cf(t,'w1',k,i,hrs)$(map_block_hour(i,'b8',hrs)) = 0;


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
* Capacity related parameters
*--------------------
PARAMETER capU(a,i,k) 'agent-based nameplate capacity at nodes (units: MW)';
capU('fossil_gen_agent',i,k) = cap_agg(i,k)$(fossil(k) OR nuclear(k) OR geothermal(k));
capU('renew_gen_agent',i,k) = cap_agg(i,k)$renew(k);

* u(a,i,k) limits investments into certain categories
PARAMETER u(a,i,k) 'agent-based ADDITIONAL capacity options at nodes in 2035 (MW)';
* need to put something in here to avoid an error
u(a,i,k) = 0;

PARAMETER buildRate(k) 'practical (engineering based) construction times for a single generating plant (units: MW/year)';

* https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2020.pdf
buildRate('Hydro') = 100 / (36/12);
buildRate('Pumped_Storage') = 100 / (72/12);

* https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2020.pdf
buildRate('Biomass') = 30 / (26/12);

* https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2020.pdf
buildRate('Coal_Steam') = 650 / (60/12);

* https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2020.pdf
buildRate('Combined_Cycle') = 1083 / (42/12);

* https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2020.pdf
buildRate('Combustion_Turbine') = 105 / (40/12);

* assume same as coal plant
buildRate('Fossil_Waste') = 650 / (60/12);

buildRate('IGCC') = 1083 / (60/12);
buildRate('Nuclear') = 2156 / (72/12);

* assume same as coal plant
buildRate('Municipal_Solid_Waste') = 650 / (60/12);
buildRate('Landfill_Gas') = 650 / (60/12);
buildRate('Non_Fossil_Waste') = 650 / (60/12);
buildRate('OG_Steam') = 650 / (60/12);
buildRate('Tires') = 650 / (60/12);

buildRate('Geothermal') = 50 / (60/12);

* https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2020.pdf
buildRate('Fuel_Cell') = 10 / (20/12);

* assume same as fuel cell
buildRate('battery_slow') = 10 / (20/12);
buildRate('battery_med') = 10 / (20/12);
buildRate('Battery_fast') = 10 / (20/12);

* https://www.energy.gov/eere/wind/maps/wind-vision

* downscale this data because of the multiple technology bins in the model
buildRate(all_onwind(k)) = 50 / (18/12);

* downscale this data because of the multiple technology bins in the model
buildRate(all_offwind(k)) = 400 / (36/12);

* https://www.seia.org/research-resources/solar-market-insight-report-2019-q4
* downscale this data because of the multiple technology bins in the model
buildRate(all_solar_PV(k)) = 150 / (18/12);

* https://www.eia.gov/analysis/studies/powerplants/capitalcost/pdf/capital_cost_AEO2020.pdf
buildRate('Solar_Thermal') = 115 / (30/12);

OPTION buildRate:0:0:5;
DISPLAY buildRate;


PARAMETER simuBuild(k) 'number of plants that might be built at the same time (units: count)';
* need to define this to avoid an error
simuBuild(k) = 0;
*--------------------



*--------------------
* Capacity factor container
*--------------------
PARAMETER tmu(t,wn,sn,hn,i,k,b) 'capacity factor data container (units: unitless)';

* follow Philpott -- most technologies have a CF = 1 unless wind/solar/hydro
tmu(scn(t,wn,sn,hn),i,k,b) = 1;
tmu(scn(t,wn,sn,hn),i,geothermal,b) = 0.85;

* Add hydro intermittency
tmu(scn(t,wn,sn,hn),i,hydro,b) = ave_hydro_cf(t,hn,i,hydro,b);

* Add wind intermittency
* need to assume a CF for generic 'On/Offshore_Wind' technologies
tmu(scn(t,wn,sn,hn),i,'Onshore_Wind',b) = ave_wind_cf(t,wn,i,'Onshore_Wind_2',b);
tmu(scn(t,wn,sn,hn),i,'Offshore_Wind',b) = ave_wind_cf(t,wn,i,'Offshore_Wind_2',b);
tmu(scn(t,wn,sn,hn),i,nrel_onwind,b) = ave_wind_cf(t,wn,i,nrel_onwind,b);
tmu(scn(t,wn,sn,hn),i,nrel_offwind,b) = ave_wind_cf(t,wn,i,nrel_offwind,b);

* Add solar capacity factors
* need to assume a CF for generic 'Solar_PV' technologies
tmu(scn(t,wn,sn,hn),i,'Solar_PV',b) = ave_solar_cf(t,sn,i,'SolarUtil_PV_2',b);
tmu(scn(t,wn,sn,hn),i,nrel_solar_PV,b) = ave_solar_cf(t,sn,i,nrel_solar_PV,b);

* scenario weightings
PARAMETER wprob(t,wn,sn,hn);
wprob(t,wn,sn,hn)$scn(t,wn,sn,hn) = 1 / card(scn);

PARAMETER loadblockhours(t,wn,sn,hn,b) '# of hours per loadblock';
PARAMETER ldc(t,wn,sn,hn,a,b,i) 'agent-based electrical demand (units: MW)';
* PARAMETER loadblockdays(t,wn,sn,hn,i);

loadblockhours(scn(t,wn,sn,hn),b) = loadblockhours_compact(t,b);
ldc(scn(t,wn,sn,hn),'demand_agent',b,i) = ldc_compact(t,b,i);
* loadblockdays(scn(t,wn,sn,hn),i) = loadblockdays_compact(t,i);


* EXECUTE_UNLOAD 'decl_out.gdx';
