$TITLE Wisconsin Renewable Energy Model -- WEREWOLF

EXECUTE 'gams region_spec.gms'
EXECUTE 'gams decl.gms s=s1'
EXECUTE 'gams model.gms r=s1 s=s2'
EXECUTE 'gams run.gms r=s2'
