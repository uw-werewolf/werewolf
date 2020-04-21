*--------------------
* BASELINE CASE Generator capacity control parameters
*--------------------
* restrict investment to model regions in WI
u('fossil_gen_agent',not_cntlreg,k) = 0;
u('renew_gen_agent',not_cntlreg,k) = 0;


* additional fossil generation
u('fossil_gen_agent',cntlreg,'Coal_Steam') = 0;
u('fossil_gen_agent',cntlreg,'Combined_Cycle') = 0.20 * capU('fossil_gen_agent',cntlreg,'Combined_Cycle');
u('fossil_gen_agent',cntlreg,'Combustion_Turbine') = 0.20 * capU('fossil_gen_agent',cntlreg,'Combustion_Turbine');
u('fossil_gen_agent',cntlreg,'Fossil_Waste') = 0;
u('fossil_gen_agent',cntlreg,'IGCC') = 0.20 * capU('fossil_gen_agent',cntlreg,'IGCC');
u('fossil_gen_agent',cntlreg,'Landfill_Gas') = 0;
u('fossil_gen_agent',cntlreg,'Municipal_Solid_Waste') = 0;
u('fossil_gen_agent',cntlreg,'Non_Fossil_Waste') = 0;
u('fossil_gen_agent',cntlreg,'OG_Steam') = 0;
u('fossil_gen_agent',cntlreg,'Tires') = 0;

* additional nuclear generation
u('fossil_gen_agent',cntlreg,nuclear) = 0;

* additional geothermal generation
u('fossil_gen_agent',cntlreg,geothermal) = 0;

* additional hydro generation
u('renew_gen_agent',i,'Hydro') = 0;
u('renew_gen_agent',i,'Pumped_Storage') = 0;

* generalized growth of all renewables
* u('renew_gen_agent',cntlreg,k) = capU('renew_gen_agent',cntlreg,k) * 0.1;
u('renew_gen_agent',cntlreg,k) = 0;

* additional storage generation
* u('renew_gen_agent',cntlreg,battery) = 0;
u('renew_gen_agent',cntlreg,'Battery_fast') = 10;
u('renew_gen_agent',cntlreg,'Battery_med') = 10;
u('renew_gen_agent',cntlreg,'Battery_slow') = 10;

* No addl capacity... forces investment into NREL technology types (solar PV, on/offshore wind)
u('renew_gen_agent',cntlreg,'Solar_PV') = 0;
u('renew_gen_agent',cntlreg,'Onshore_Wind') = 0;
u('renew_gen_agent',cntlreg,'Offshore_Wind') = 0;

* Add in total technology potential for NREL technology types
u('renew_gen_agent',cntlreg,nrel_solar_PV) = cap_nrel(nrel_solar_PV,cntlreg);
u('renew_gen_agent',cntlreg,nrel_onwind) = cap_nrel(nrel_onwind,cntlreg);
u('renew_gen_agent',cntlreg,nrel_offwind) = cap_nrel(nrel_offwind,cntlreg);
*--------------------
