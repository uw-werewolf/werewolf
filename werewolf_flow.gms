$TITLE Wisconsin Renewable Energy Model -- WEREWOLF

* $SET sysdir "/Applications/GAMS30.3/Resources/sysdir"
* $SET data_repo "."


*
* Main model steps
*

* werewolf_0_disagg.gms will disaggregate all necessary data and transform it into FIPS regions
EXECUTE "gams werewolf_0_disagg.gms s=disaggregated_data"

* werewolf_1_aggr.gms will aggregate the FIPS level data into custom regions specified by the user
* user would need to modify this step werewolf in order to adjust the LDCs before they are grouped into loadblocks
* running this file generates the "processed_werewolf_data.gdx" file
EXECUTE "gams werewolf_1_aggr.gms r=disaggregated_data"

* create the transmission network
* not included right now becuase we assume the network for WI is static
* EXECUTE "python ./werewolf_python/create_network.py --gams_sysdir %sysdir% --data_repo %data_repo%"

* create the load duration curves
* not included right now becuase we assume that there arent any modifications to the LDCs are necessary
* EXECUTE "python ./werewolf_python/create_ldcs.py --gams_sysdir %sysdir% --data_repo %data_repo%"

* werewolf_2_aggr.gms will generate the solar/wind/hydro models used in the SP part of the model
EXECUTE "gams werewolf_2_declare.gms s=vre_models"

* werewolf_3_model.gms is the actual model
* at the moment, werewolf_4_reports.gms does not get called... in order to design a better results handling system
EXECUTE "gams werewolf_3_model.gms r=vre_models"
