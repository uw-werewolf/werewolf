$TITLE Wisconsin Renewable Energy Model -- WEREWOLF


EXECUTE 'python werewolf_data_pipe.py'
EXECUTE 'gams werewolf_0_disagg.gms s=disagg o=/dev/null'
EXECUTE 'gams werewolf_1_aggr.gms r=disagg o=/dev/null --ev_factor 0'
* EXECUTE 'gams werewolf_0_regions.gms restart=disagg o=/dev/null'
EXECUTE 'gams werewolf_2_decl.gms s=s1 o=/dev/null'
EXECUTE 'gams werewolf_3_model.gms r=s1 o=/dev/null'
