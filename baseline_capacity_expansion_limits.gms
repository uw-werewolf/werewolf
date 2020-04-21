*--------------------
* BASELINE CASE Generator capacity control parameters
*--------------------

* * simuBuild is defined as the number of plants that could be built over the entire cntlreg
* simuBuild('Hydro') = 0;
* simuBuild('Pumped_Storage') = 0;
* simuBuild('Biomass') = 0;
* simuBuild('Coal_Steam') = 0;
* simuBuild('Combined_Cycle') = 1;
* simuBuild('Combustion_Turbine') = 5;
* simuBuild('Fossil_Waste') = 0;
* simuBuild('IGCC') = 2;
* simuBuild('Nuclear') = 1;
* simuBuild('Municipal_Solid_Waste') = 0;
* simuBuild('Landfill_Gas') = 0;
* simuBuild('Non_Fossil_Waste') = 0;
* simuBuild('OG_Steam') = 0;
* simuBuild('Tires') = 0;
*
* simuBuild('Geothermal') = 0;
* simuBuild('Fuel_Cell') = 0;
* simuBuild('battery_slow') = 5;
* simuBuild('battery_med') = 5;
* simuBuild('Battery_fast') = 5;
* simuBuild(all_onwind(k)) = 10;
* simuBuild(all_offwind(k)) = 2;
* simuBuild(all_solar_PV(k)) = 10;
* simuBuild('Solar_Thermal') = 0;

* additional fossil generation
u('fossil_gen_agent',i,'Coal_Steam') = 0;
u('fossil_gen_agent',i,'Combined_Cycle') = 0.20 * capU('fossil_gen_agent',i,'Combined_Cycle');
u('fossil_gen_agent',i,'Combustion_Turbine') = 0.20 * capU('fossil_gen_agent',i,'Combustion_Turbine');
u('fossil_gen_agent',i,'Fossil_Waste') = 0;
u('fossil_gen_agent',i,'IGCC') = 0.20 * capU('fossil_gen_agent',i,'IGCC');
u('fossil_gen_agent',i,'Landfill_Gas') = 0;
u('fossil_gen_agent',i,'Municipal_Solid_Waste') = 0;
u('fossil_gen_agent',i,'Non_Fossil_Waste') = 0;
u('fossil_gen_agent',i,'OG_Steam') = 0;
u('fossil_gen_agent',i,'Tires') = 0;

* additional nuclear generation
u('fossil_gen_agent',i,nuclear) = 0;

* additional geothermal generation
u('fossil_gen_agent',i,geothermal) = 0;

* additional hydro generation
u('renew_gen_agent',i,'Hydro') = 0;
u('renew_gen_agent',i,'Pumped_Storage') = 0;

* generalized growth of all renewables
* u('renew_gen_agent',i,k) = capU('renew_gen_agent',i,k) * 0.1;
u('renew_gen_agent',i,k) = 0;

* additional storage generation
* u('renew_gen_agent',i,battery) = 0;
u('renew_gen_agent',i,'Battery_fast') = 10;
u('renew_gen_agent',i,'Battery_med') = 10;
u('renew_gen_agent',i,'Battery_slow') = 10;

* No addl capacity... forces investment into NREL technology types (solar PV, on/offshore wind)
u('renew_gen_agent',i,'Solar_PV') = 0;
u('renew_gen_agent',i,'Onshore_Wind') = 0;
u('renew_gen_agent',i,'Offshore_Wind') = 0;

* Add back in total technology potential for NREL technology types
u('renew_gen_agent',i,nrel_solar_PV) = cap_nrel(nrel_solar_PV,i);
u('renew_gen_agent',i,nrel_onwind) = cap_nrel(nrel_onwind,i);
u('renew_gen_agent',i,nrel_offwind) = cap_nrel(nrel_offwind,i);
*--------------------
