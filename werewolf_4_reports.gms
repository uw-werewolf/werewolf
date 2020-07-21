* *-------------------
* * Merge GeoJSON polygons
* *-------------------
* EXECUTE 'python make_geojson.py > %system.nullfile%';
* myerrorlevel = errorlevel;
* ABORT$(myerrorlevel <> 0) "ERROR: make_geojson.py did not finish successfully...";
* *-------------------
*


* *-------------------
* * Map nodes and transmission network
* *-------------------
* EXECUTE 'python map_model_network.py > %system.nullfile%';
* myerrorlevel = errorlevel;
* ABORT$(myerrorlevel <> 0) "ERROR: map_model_network.py did not finish successfully...";
* *-------------------



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


* *-------------------
* * Map
* *-------------------
* EXECUTE 'python map_generation.py > %system.nullfile%';
* myerrorlevel = errorlevel;
* ABORT$(myerrorlevel <> 0) "ERROR: map_generation.py did not finish successfully...";
*
* EXECUTE 'python map_generation_cntlreg.py > %system.nullfile%';
* myerrorlevel = errorlevel;
* ABORT$(myerrorlevel <> 0) "ERROR: map_generation_cntlreg.py did not finish successfully...";
*
* EXECUTE 'python map_built_capacity.py > %system.nullfile%';
* myerrorlevel = errorlevel;
* ABORT$(myerrorlevel <> 0) "ERROR: map_built_capacity.py did not finish successfully...";
*
* EXECUTE 'python map_built_capacity_cntlreg.py > %system.nullfile%';
* myerrorlevel = errorlevel;
* ABORT$(myerrorlevel <> 0) "ERROR: map_built_capacity_cntlreg.py did not finish successfully...";
*
* EXECUTE 'python map_total_capacity.py > %system.nullfile%';
* myerrorlevel = errorlevel;
* ABORT$(myerrorlevel <> 0) "ERROR: map_total_capacity.py did not finish successfully...";
* *-------------------



*
* * create a map of powerline flows
* EXECUTE 'python map_flows.py';
