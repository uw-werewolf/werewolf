$TITLE Wisconsin Renewable Energy Model -- WEREWOLF

* run only if you need to recreate the dataset for some reason
EXECUTE 'python werewolf_data_pipe.py'


*
* Main model steps
*

* werewolf_0_disagg.gms will disaggregate the EPA data into FIPS regions
EXECUTE 'gams werewolf_0_disagg.gms s=disaggregated_data o=/dev/null'

* werewolf_1_aggr.gms will aggregate the FIPS level data into custom regions specified by the user
* also allows the user to adjust the LDCs before they are grouped into loadblocks
EXECUTE 'gams werewolf_1_aggr.gms r=disaggregated_data o=/dev/null --ev_factor 0.50'

* werewolf_2_aggr.gms will generate the solar/wind/hydro models used in the SP part of the model
EXECUTE 'gams werewolf_2_declare.gms s=vre_models o=/dev/null'

* werewolf_3_model.gms is the actual model, will also call werewolf_4_reports.gms in order to generate output on the fly
EXECUTE 'gams werewolf_3_model.gms r=vre_models o=/dev/null'
