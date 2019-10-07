$TITLE Wisconsin Renewable Energy Model -- WEREWOLF
* areas to fix are denoated with an XXXX flag

* --agg flag controls the aggregation possiblities are [fips, miso]
$IF NOT SETGLOBAL agg $SETGLOBAL agg 'miso'
$IF NOT SETGLOBAL almostsure $SETGLOBAL almostsure 0

$GDXIN 'werewolf_data.gdx'

*-----------
* LOAD SETS
*-----------
SET b 'loadblock segments';
$LOAD b

SET r 'values to describe different values of the parameter frac';
$LOAD r

SET n 'modeled annual time periods';
$LOAD n

SET k 'all technolgy types in the model';
$LOAD k

SET uid 'unique id numbers from EPA NEEDS database';
$LOAD uid

SET a 'model agent type';
$LOAD a

SET prodn(a) 'model agent type that generates electricity';
$LOAD prodn

SET w 'unknown set'
$LOAD w

SET t 'season';
$LOAD t

* SET season 'season';
* $LOAD season
*
* SET daytype 'type of day';
* $LOAD daytype
*
* SET windtype 'wind scenario';
* $LOAD windtype
*
*
*
* SET scn(season,daytype,windtype) 'list of scenarios (flat)';
* $LOADDC scn


SET cnty 'Wisconsin county names';
$LOAD cnty

SET gen(k) 'all electricty generation technolgy types in the model';
$LOADDC gen

SET hydro(k) 'hydro technologies';
$LOADDC hydro

SET renew(k) 'renewable technologies';
$LOADDC renew

SET fossil(k) 'fossil technologies';
$LOAD fossil

SET store(k) 'storage technologies';
$LOADDC store

SET regions 'all regions';
$LOAD regions

SET i(regions) 'all nodes in model';

SET fips(regions) 'All FIPS codes';
$IF %agg% == 'fips' $LOAD i=fips
$LOAD fips

SET miso(regions) 'MISO regions';
$IF %agg% == 'miso' $LOAD i=miso
$LOAD miso

SET plnt 'Plant names';
$LOAD plnt

SET ij(i,i) 'transmission arcs used in model';
SET ij_miso(miso,miso) 'transmission arcs (miso level aggregation)';
$IF %agg% == 'miso' $LOADDC ij=ij_miso
$LOADDC ij_miso

SET ij_fips(fips,fips) 'transmission arcs (fips level aggregation)';
$IF %agg% == 'fips' $LOADDC ij=ij_fips
$LOADDC ij_fips

* XXXX -- note that this mapping is an approximation for now and assumes 1:1
SET map_fips_miso(fips,miso) 'map between FIPS5 codes and MISO regions';
$LOADDC map_fips_miso

SET map_fips_cnty(fips,cnty) 'map between FIPS5 codes and county names';
$LOADDC map_fips_cnty

SET map_uid_cnty(uid,cnty) 'map between unit generator ID and county names';
$LOADDC map_uid_cnty

SET map_uid_fips(uid,fips) 'map between unit generator ID and FIPS5 codes';
$LOADDC map_uid_fips

SET map_uid_miso(uid,miso) 'map between unit generator ID and MISO regions';
$LOADDC map_uid_miso

SET map_uid_plnt(uid,plnt) 'map between unit generator ID and plant names';
$LOADDC map_uid_plnt

SET map_uid_type(uid,k) 'map between unit generator ID and generation technolgy type';
$LOADDC map_uid_type



*-----------------
* LOAD PARAMETERS
*-----------------
PARAMETER population(*) 'county level population (units: count)';
$LOADDC population

PARAMETER geothermalloadfactor 'geothermal load factor (unitless factor)';
$LOAD geothermalloadfactor

PARAMETER windloadfactor 'XXXX';
$LOAD windloadfactor

PARAMETER batteryEff 'battery efficiency (unitless factor)';
$LOAD batteryEff

PARAMETER fractionLR 'maximum possible load reduction (unitless factor)';
$LOAD fractionLR

PARAMETER maxCarbon 'current CO2 emissions (units: tonnes)';
$LOAD maxCarbon

PARAMETER maxnrEnergy 'maximum non-renewable energy allowed (units: unknown)';
$LOAD maxnrEnergy

PARAMETER maxNR 'current thermal generation capacity (units: MW)';
$LOAD maxNR

PARAMETER capR 'XXXX';
$LOAD capR

PARAMETER mufactor 'XXXX';
$LOAD mufactor

PARAMETER nufactor 'XXXX';
$LOAD nufactor

PARAMETER chargerate(k) 'battery charge rate (units: MW)';
$LOADDC chargerate

PARAMETER CVARalpha 'CVaR parameter (unitless factor)';
$LOAD CVARalpha

PARAMETER lambda 'risk parameter lambda (unitless factor)';
$LOAD lambda

* PARAMETER fcap(fips,fips) 'Transmission line capacity (units: MW)';
* $LOADDC fcap

PARAMETER v 'value of lost load (units: $)';
$LOAD v

PARAMETER TonnesCO2(k) 'emissions for generator types (units: tonnes/MWh)';
$LOADDC TonnesCO2

PARAMETER cap(uid) 'generation nameplate capacity (units: MW)';
$LOADDC cap

PARAMETER loadblockhours(t,b) '# of hours per loadblock';
$LOADDC loadblockhours

PARAMETER eC(k) 'annualized capital costs (units: $/MW/year)';
$LOADDC eC

PARAMETER gC(k) 'SRMC [fuel + variable O&M costs] (units: $/MWh)';
$LOADDC gC

PARAMETER oC(k) 'operating costs (units: $/MW/yr)';
$LOADDC oC

PARAMETER load_miso(t,b,miso) 'electrical demand (units: MW)';
$LOADDC load_miso

PARAMETER alpha(t,b,i);
PARAMETER alpha_miso(t,b,miso) 'capacity adjustment to shift RoR hydro into peak periods (units: unitless)';
$IF %agg% == 'miso' $LOADDC alpha=alpha_miso

PARAMETER alpha_fips(t,b,fips) 'capacity adjustment to shift RoR hydro into peak periods (units: unitless)';
$IF %agg% == 'fips' $LOADDC alpha=alpha_fips

PARAMETER windS0(t,b,i) 'wind factor S0 (units: unitless)';
PARAMETER windS0_miso(t,b,miso) 'wind factor S0 (units: unitless)';
$IF %agg% == 'miso' $LOADDC windS0=windS0_miso

PARAMETER windS0_fips(t,b,fips) 'wind factor S0 (units: unitless)';
$IF %agg% == 'fips' $LOADDC windS0=windS0_fips

PARAMETER windS1(t,b,i) 'wind factor S1 (units: unitless)';
PARAMETER windS1_miso(t,b,miso) 'wind factor S1 (units: unitless)';
$IF %agg% == 'miso' $LOADDC windS1=windS1_miso

PARAMETER windS1_fips(t,b,fips) 'wind factor S1 (units: unitless)';
$IF %agg% == 'fips' $LOADDC windS1=windS1_fips

PARAMETER Windprob(t) 'seasonal wind probability (units: unitless)';
$LOADDC Windprob

PARAMETER insolation(t,b,i) 'solar factor (units: unitless)';
PARAMETER insolation_miso(t,b,miso) 'solar factor (units: unitless)';
$IF %agg% == 'miso' $LOADDC insolation=insolation_miso

PARAMETER insolation_fips(t,b,fips) 'solar factor (units: unitless)';
$IF %agg% == 'fips' $LOADDC insolation=insolation_fips

PARAMETER insol(fips) 'annual average ghi insolation (units: kWh/m^2/day)';
$LOADDC insol

PARAMETER inflowmu(n,t,i) 'run of river hydro generation scale factor (units: unitless)';
PARAMETER inflows_miso(n,t,miso) 'run of river hydro generation scale factor (units: unitless)';
$IF %agg% == 'miso' $LOADDC inflowmu=inflows_miso

PARAMETER inflows_fips(n,t,fips) 'run of river hydro generation scale factor (units: unitless)';
$IF %agg% == 'fips' $LOADDC inflowmu=inflows_fips

$GDXIN

* Logic to control sets and parameters that are sensitive to %agg%
ALIAS(miso,miso_p);
ALIAS(fips,fips_p);
ALIAS(i,j);


PARAMETER fcap(i,i) 'Transmission line capacity (units: MW)';
PARAMETER load(t,a,b,regions) 'electrical demand (units: MW)';

* XXXX placeholder for tranmission line capacity
fcap(ij(i,j)) = 1000000;

* we need some supplemental data to untangle the WI only load data in the 'MIS_MNWI' region
* we do this by simple weighting by population
population('MN') = 5611179;
population('WI') = sum(fips, population(fips));

population('MIS_WUMS') = sum(map_fips_miso(fips,'MIS_WUMS'), population(fips));
population('MIS_MNWI') = sum(map_fips_miso(fips,'MIS_MNWI'), population(fips));

* necessary to scale miso data to remove effects of MN
load_miso(t,b,'MIS_MNWI') = sum(map_fips_miso(fips,'MIS_MNWI'), population(fips)) / (population('MIS_MNWI') + population('MN')) * load_miso(t,b,'MIS_MNWI');


* implement county diassgretation if choosen
PARAMETER wp(fips,miso) 'population weight factor';
$IF %agg% == 'fips' wp(fips,miso) = (population(fips)/population(miso))$map_fips_miso(fips,miso);
$IF %agg% == 'fips' load(t,'dem',b,fips) = sum(miso, wp(fips,miso) * load_miso(t,b,miso));

$IF %agg% == 'miso' load(t,'dem',b,miso) = load_miso(t,b,miso);


PARAMETER max_data_emissions(t);
max_data_emissions(t) = sum((b,i), loadblockhours(t,b) * load(t,'dem',b,i) * smax(k, TonnesCO2(k)));


* need to catalogue generator capacity into a single parameter
PARAMETER cap_agg(regions,k) 'aggregated existing nameplate capacity at nodes (Units: MW)';
PARAMETER capU(a,regions,k) 'existing nameplate capacity at nodes (Units: MW)';

$IF %agg% == 'fips' cap_agg(fips,k) = sum(uid$(map_uid_fips(uid,fips) AND map_uid_type(uid,k)), cap(uid));
$IF %agg% == 'miso' cap_agg(miso,k) = sum(uid$(map_uid_miso(uid,miso) AND map_uid_type(uid,k)), cap(uid));


capU('fos',i,k) = cap_agg(i,k)$fossil(k);
capU('ren',i,k) = cap_agg(i,k)$renew(k);
DISPLAY capU;

* XXXX just an estimate right now... this would need refinement
PARAMETER u(a,regions,k) 'additional capacity options at nodes in 2035 (MW)';

u('ren',i,k) = capU('ren',i,k) * 0.3;
u('ren',i,k)$store(k) = 10;
DISPLAY u;

SET used(a);
used(a) = yes;

* Derived parameters
PARAMETER storagegatewidth;
storagegatewidth = 500.0;

PARAMETER eff(k) ;
eff(store) = batteryEff;

PARAMETER coeff(k);
coeff(k) = 0.001;

PARAMETER prob(n);
prob(n) = 1 / card(n);

PARAMETER wprob(w,t);
wprob('0',t) = Windprob(t);
wprob('1',t) = 1.0 - Windprob(t);

PARAMETER loadblockdays(t,*);
loadblockdays(t,i) = sum(b, loadblockhours(t,b)) / 24;


PARAMETER mu(regions,k,n,b) 'limit on capacity of wind or inflow event';
mu(i,k,n,b) = 1.0;
mu(i,'Onshore_Wind',n,b) = windloadfactor;

PARAMETER tmu(t,*,k,n,w,b) 'unknown parameter (units: XXXX)';
tmu(t,i,k,n,w,b) = mu(i,k,n,b);

tmu(t,i,'Hydro',n,w,b) =  alpha(t,b,i) * inflowmu(n,t,i);
tmu(t,i,'Solar_PV',n,w,b) = insolation(t,b,i);

* Add wind intermittency
tmu(t,i,'Onshore_Wind',n,'0',b) = windS0(t,b,i);
tmu(t,i,'Onshore_Wind',n,'1',b) = windS0(t,b,i);

* parameter only used if there is hydro storage, removed for now
* PARAMETER nu(*,k,n) 'limit on energy of drought event';
* nu(i,k,n) = 1.0;


* parameter only used if there is hydro storage, removed for now
* PARAMETER tnu(t,i,k,n);
* tnu(t,i,k,n) = nu(i,k,n);
* *tnu(t,i,'HYDROs',n)= nu(i,'HYDROs',n)*inflowscale(t);
* tnu(t,'SI','HYDROs',n) = inflownuSI(n,t);
* tnu(t,'NI','HYDROs',n) = inflownuNI(n,t);


SET ctype / 'Invest', 'Maintain', 'Operate', 'LostLoad' /;
PARAMETER build(r,a,i,k);
PARAMETER ZZ(r,n,w,t);
PARAMETER ZL(r,n,w,t);
PARAMETER TotalCost(r);
PARAMETER lostMWhours(r,a);
PARAMETER capacity(r,a,i,k);
PARAMETER ExpCost(r,ctype)
PARAMETER TotalCostM(r);
PARAMETER TotalCarbon(r);
PARAMETER Co2price(r);
PARAMETER lostloadenergy(a,*);
