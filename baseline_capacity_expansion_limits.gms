*--------------------
* BASELINE CASE Generator capacity control parameters
*--------------------

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
u('renew_gen_agent',i,'Energy_Storage_fast') = 10;
u('renew_gen_agent',i,'Energy_Storage_med') = 10;
u('renew_gen_agent',i,'Energy_Storage_slow') = 10;

* No addl capacity... forces investment into NREL technology types (solar PV, on/offshore wind)
u('renew_gen_agent',i,'Solar_PV') = 0;
u('renew_gen_agent',i,'Onshore_Wind') = 0;
u('renew_gen_agent',i,'Offshore_Wind') = 0;

* Add back in total technology potential for NREL technology types
u('renew_gen_agent',i,nrel_solar) = cap_nrel(nrel_solar,i);
u('renew_gen_agent',i,all_onwind) = cap_nrel(all_onwind,i);
u('renew_gen_agent',i,all_offwind) = cap_nrel(all_offwind,i);
*--------------------
