*-------------------
* Generation results
*-------------------
PARAMETER y_ikr(i,k,r) 'actual generation by agent, region, technology, policy scenario (units: MWh)';
y_ikr(i,k,r) = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * sum(b, y_out(t,wn,sn,hn,i,k,b,r) * loadblockhours_compact(t,b)));


PARAMETER y_ir(i,r) 'actual generation by agent, region, policy scenario (units: MWh)';
y_ir(i,r) = eps + sum(k, sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * sum(b, y_out(t,wn,sn,hn,i,k,b,r) * loadblockhours_compact(t,b))));


PARAMETER y_r(r) 'actual generation by agent, policy scenario (units: MWh)';
y_r(r) = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * sum(i, sum(k, sum(b, y_out(t,wn,sn,hn,i,k,b,r) * loadblockhours_compact(t,b)))));
*-------------------



*-------------------
* Transmission results
*-------------------
PARAMETER f_ijbr(i,j,b,r) 'power trasmission by from region, to region, loadblock, policy scenario (units: MW)';
f_ijbr(i,j,b,r) = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * f_out(t,wn,sn,hn,i,j,b,r));

PARAMETER f_ijr(i,j,r) 'power trasmission by from region, to region, policy scenario (units: MW)';
f_ijr(i,j,r) = eps + sum(b, sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * f_out(t,wn,sn,hn,i,j,b,r)));
*-------------------


*-------------------
* Net transmission from neighboring regions
*-------------------
PARAMETER import_ibr(i,b,r);
import_ibr(i,b,r) = eps + sum(ij(i,j)$(not_cntlreg(i) and cntlreg(j)), sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * f_out(t,wn,sn,hn,i,j,b,r)));

PARAMETER import_ir(i,r);
import_ir(i,r) = eps + sum(ij(i,j)$(not_cntlreg(i) and cntlreg(j)), sum(b, sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * f_out(t,wn,sn,hn,i,j,b,r))));


PARAMETER export_ibr(i,b,r);
export_ibr(i,b,r) = eps + sum(ij(i,j)$(not_cntlreg(i) and cntlreg(j)), sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * f_out(t,wn,sn,hn,j,i,b,r)));

PARAMETER export_ir(i,r);
export_ir(i,r) = eps + sum(ij(i,j)$(not_cntlreg(i) and cntlreg(j)), sum(b, sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * f_out(t,wn,sn,hn,j,i,b,r))));
*-------------------



*-------------------
* Load shed results
*-------------------
PARAMETER q_ibr(i,b,r) 'power shed by agent, region, loadblock, policy scenario (units: MW)';
q_ibr(i,b,r) = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * q_out(t,wn,sn,hn,i,b,r));

PARAMETER q_ir(i,r) 'power shed by agent, region, policy scenario (units: MW)';
q_ir(i,r) = eps + sum(b, sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * q_out(t,wn,sn,hn,i,b,r)));
*-------------------



*-------------------
* Operating costs
*-------------------
PARAMETER ZZ_r(r) 'total operating costs by policy scenario (units: $)';
ZZ_r(r) = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * ZZ(t,wn,sn,hn,r));
*-------------------



*-------------------
* Value of lost load
*-------------------
PARAMETER ZL_r(r) 'total value of lost load by policy scenario (units: $)';
ZL_r(r) = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * ZL(t,wn,sn,hn,r));
*-------------------




*-------------------
* Unload results
*-------------------
EXECUTE_UNLOAD 'final_results.gdx', k, r, y_ikr, y_ir, y_r, TotalCarbon_r, TotalCarbon_ir, frac_r, cntlreg, not_cntlreg, i, a, build, TotalCost, capacity, lostMWhours, ExpCost_r, ExpCost_ir Co2price, f_ijbr, f_ijr, q_ibr, q_ir, ZL_r, ZZ_r, fossil, gen, hydro, renew, store, nuclear, battery, geothermal, nrel_solar_PV, nrel_onwind, nrel_offwind, all_wind, all_offwind, all_onwind, all_solar, all_solar_PV, all_distsolar_PV, all_utilsolar_PV, all_solar_therm, ij, import_ibr, import_ir, export_ibr, export_ir, map_center, results_folder, x_title, x_cntlreg, z_cntlreg, y_cntlreg;
*-------------------



* FILE xxx /'.%sep%output%sep%x.csv'/;
* PUT xxx;
* xxx.PW = 32767;
* PUT 'BuiltCap,'
* loop(rr, PUT rr.tl:0 ',')
* PUT /;
*
*
* loop(k,
*   PUT k.tl:0 ','
*   loop(rr, PUT x_cntlreg(k,rr) ',')
*   PUT /;
*   );
*
*
* FILE yyy /'.%sep%output%sep%y.csv'/;
* PUT yyy;
* yyy.PW = 32767;
* PUT 'Generation,'
* loop(rr, PUT rr.tl:0 ',')
* PUT /;
* loop(k,
*   PUT k.tl:0 ','
*   loop(rr, PUT y_cntlreg(k,rr) ',')
*   PUT /;
*   );
*
*
* FILE zzz /'.%sep%output%sep%z.csv'/;
* PUT zzz;
* zzz.PW = 32767;
* PUT 'TotalCap,'
* loop(rr, PUT rr.tl:0 ',')
* PUT /;
* loop(k,
*   PUT k.tl:0 ','
*   loop(rr, PUT z_cntlreg(k,rr) ',')
*   PUT /;
*   );



*-------------------
* Merge GeoJSON polygons
*-------------------
EXECUTE 'python make_geojson.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: make_geojson.py did not finish successfully...";
*-------------------



*-------------------
* Map nodes and transmission network
*-------------------
EXECUTE 'python map_model_network.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: map_model_network.py did not finish successfully...";
*-------------------



*-------------------
* Plot
*-------------------
EXECUTE 'python plot_carbon_emissions.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: plot_carbon_emissions.py did not finish successfully...";

EXECUTE 'python plot_generation.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: plot_generation.py did not finish successfully...";

EXECUTE 'python plot_capacity.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: plot_capacity.py did not finish successfully...";

EXECUTE 'python plot_transmission_exim.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: plot_transmission_exim.py did not finish successfully...";

EXECUTE 'python plot_costs.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: plot_costs.py did not finish successfully...";
*-------------------


*-------------------
* Map
*-------------------
EXECUTE 'python map_generation.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: map_generation.py did not finish successfully...";

EXECUTE 'python map_generation_cntlreg.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: map_generation_cntlreg.py did not finish successfully...";

EXECUTE 'python map_built_capacity.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: map_built_capacity.py did not finish successfully...";

EXECUTE 'python map_built_capacity_cntlreg.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: map_built_capacity_cntlreg.py did not finish successfully...";

EXECUTE 'python map_total_capacity.py > %system.nullfile%';
myerrorlevel = errorlevel;
ABORT$(myerrorlevel <> 0) "ERROR: map_total_capacity.py did not finish successfully...";
*-------------------



*
* * create a map of powerline flows
* EXECUTE 'python map_flows.py';
