$TITLE Wisconsin Renewable Energy Model -- WEREWOLF

$SETENV GDXCOMPRESS 1
$IFTHENI %system.filesys% == UNIX $SET sep "/"
$ELSE $SET sep "\"
$ENDIF


$IF NOT SET reldir $SETGLOBAL reldir '.'
$IF NOT SET folder $SETGLOBAL folder 'results'
SET results_folder '%reldir%%sep%output%sep%%folder%%sep%' / 1 /;


$IF DEXIST '%reldir%%sep%output%sep%%folder%' ABORT 'results directory already exists, rename or remove existing'


*-------------------
* Create results directory structure
*-------------------
$IF NOT DEXIST '%reldir%%sep%output%sep%%folder%' $CALL mkdir '%reldir%%sep%output%sep%%folder%'
$IF NOT DEXIST '%reldir%%sep%output%sep%%folder%%sep%summary_maps' $CALL mkdir '%reldir%%sep%output%sep%%folder%%sep%summary_maps'

$IF NOT DEXIST '%reldir%%sep%output%sep%%folder%%sep%summary_plots' $CALL mkdir '%reldir%%sep%output%sep%%folder%%sep%summary_plots'

$IF NOT DEXIST '%reldir%%sep%output%sep%%folder%%sep%summary_maps%sep%built_capacity' $CALL mkdir '%reldir%%sep%output%sep%%folder%%sep%summary_maps%sep%built_capacity'

$IF NOT DEXIST '%reldir%%sep%output%sep%%folder%%sep%summary_maps%sep%generation' $CALL mkdir '%reldir%%sep%output%sep%%folder%%sep%summary_maps%sep%generation'

$IF NOT DEXIST '%reldir%%sep%output%sep%%folder%%sep%summary_maps%sep%total_capacity' $CALL mkdir '%reldir%%sep%output%sep%%folder%%sep%summary_maps%sep%total_capacity'
*-------------------


OPTION limrow = 0;
OPTION limcol = 0;

SCALAR frac / 0 /;
SCALAR co2redn / 1 /;
SCALAR capredn / 0 /;
SCALAR nrenergyredn / 0 /;
SCALAR carbonleakage '1 => no constraint on imports to cntlreg, can be in an almostsure model'/ 1 /;

SCALAR tlossval / 0.01 /;

ALIAS(b,bp);

* POSITIVE VARIABLE CVap(a,n,w0,w1,w2,w3) 'shortfall variables for cvar';
* POSITIVE VARIABLE yy(n,w0,w1,w2,w3) 'shortfall variables for cvar';
* POSITIVE VARIABLE s(i,n,t) 'energy transfer from season t to t+1 in region in scenario n';

POSITIVE VARIABLE sigma;

* first stage decision variables
VARIABLE x(a,i,k) 'cap expansion (+) or shutdown (-) at i in technology k by agent a';
POSITIVE VARIABLE z(a,i,k) 'capacity after expansion in k';

* second stage decision variables
POSITIVE VARIABLE pi(t,wn,sn,hn,i,b);
POSITIVE VARIABLE y(t,wn,sn,hn,a,i,k,b) 'generation by agent a using technology k in block b (units: MW)';
POSITIVE VARIABLE q(t,wn,sn,hn,a,i,b) 'load shed by a at location i in block b';
POSITIVE VARIABLE m(t,wn,sn,hn,a,i,k,b,bp) 'supply (MW) at i moved from b to bp using battery tech k';
POSITIVE VARIABLE f(t,wn,sn,hn,i,j,b) 'energy flow from location i to location j';
* POSITIVE VARIABLE saverage(i,t) 'nonanticipative storage';

* CVaR associated variables
* VARIABLE tt 'Var';
* VARIABLE aVap(a);
* VARIABLE yfix(t,n) 'for smelter';

* objectives
VARIABLE obj(a);
VARIABLE sysobj;

* convenience sets
SET aik(a,i,k) 'agent has technology k at location i';
aik(a,i,k) = yes$(prodn(a) AND capU(a,i,k) + u(a,i,k) > 0);

SET inb(t,wn,sn,hn,i,b) 'demand at i in block b in some scenario scn(t,wn,sn,hn)';
inb(scn(t,wn,sn,hn),i,b) = yes$(wprob(t,wn,sn,hn) * smax(a, ldc(t,wn,sn,hn,a,b,i)) > 0);

SET carbemit(i,k) 'technolgies that emit carbon at a node i';
carbemit(i,k) = yes$(MMTonnesCO2(i,k) > 0);


* scale cost data
SCALAR scalefac / 1e-3 /;
PARAMETER eC(k,i) 'capital costs (units: $/MW/year)';
PARAMETER oC(k) 'operating costs (units: $/MW/year)';
PARAMETER gC(k) 'SRMC [fuel + variable O&M costs] (units: $/MWh)';

SCALAR fractionLR 'maximum possible load reduction (unitless factor)' / 0.20 /;
SCALAR capR '? (units: unknown)' / 0 /;
SCALAR c 'cost of load shedding (units: $)' / 10000 /;
SCALAR CVARalpha 'CVaR parameter (unitless factor)' / 0.10 /;
SCALAR lambda 'risk parameter lambda (unitless factor)' / 0.1 /;
SCALAR v 'value of lost load (units: $)' / 10000 /;

$GDXIN '.%sep%gdx_temp%sep%processed_werewolf_data.gdx'
$LOAD eC, oC, gC
$GDXIN

eC(k,i) = eC(k,i) * scalefac;
oC(k) = oC(k) * scalefac;
gC(k) = gC(k) * scalefac;
coeff(k) = coeff(k) * scalefac;
capR = capR * scalefac;
v = v * scalefac;


EQUATION caplim(a,i,k);
EQUATION genClim(t,wn,sn,hn,a,i,k,b);
EQUATION genElim(t,wn,sn,hn,a,i,k);
EQUATION blim(t,wn,sn,hn,a,i,k);
EQUATION brate(t,wn,sn,hn,a,i,k,b);
EQUATION balance(t,wn,sn,hn,i,b);
EQUATION renewcap;
* EQUATION smelter(t,wn,sn,hn,b);
* EQUATION nonanticS1(i,n,t);
* EQUATION nonanticS2(i,n,t);


caplim(a,i,k)$aik(a,i,k)..
  z(a,i,k)
  =L=
  x(a,i,k) + capU(a,i,k);


genClim(scn(t,wn,sn,hn),a,i,k,b)$(aik(a,i,k) AND gen(k))..
  y(t,wn,sn,hn,a,i,k,b)
  =L=
  tmu(t,wn,sn,hn,i,k,b) * z(a,i,k);


* genElim(a,i,k,n,w,t)$(aik(a,i,k) AND prob(n) AND reservoir(k))..
*   (sum(b, loadblockhours(t,b)*y(t,a,i,k,n,w,b)) + s(i,n,t) - s(i,n,t--1) ) /sum(b, loadblockhours(t,b))
*   =L=
*   tnu(t,i,k,n) * z(a,i,k);

* nonanticS1(i,n,t)..
*   s(i,n,t)
*   =L=
*   saverage(i,t) + storagegatewidth;
*
* nonanticS2(i,n,t)..
*   s(i,n,t)
*   =G=
*   saverage(i,t) - storagegatewidth;

* New battery constraint ABP
* z(a,i,k) is battery capacity in MWh
* If every day is the same then we can transfer z(a,i,k)*loadblockdaysdays(t,i) in season t
* Total transfer of energy out of a block b in a season is
*          seasonhours(t,i,b)*sum(bp$(NOT SAMEAS(b,bp)), m(t,a,i,k,n,b,bp)))

blim(scn(t,wn,sn,hn),a,i,k)$(aik(a,i,k) AND battery(k))..
  sum(b, loadblockhours(t,wn,sn,hn,b) * sum(bp$(NOT SAMEAS(b,bp)), m(t,wn,sn,hn,a,i,k,b,bp)))
  =L=
  sum(b, z(a,i,k) * loadblockhours(t,wn,sn,hn,b));


brate(scn(t,wn,sn,hn),a,i,k,b)$(aik(a,i,k) AND battery(k))..
  sum(bp$(NOT SAMEAS(b,bp)), m(t,wn,sn,hn,a,i,k,b,bp))
  =L=
  z(a,i,k) * chargerate(k);


balance(scn(t,wn,sn,hn),i,b)$(inb(t,wn,sn,hn,i,b))..
  sum((a,k)$aik(a,i,k), y(t,wn,sn,hn,a,i,k,b)$gen(k) + sum(bp$(NOT SAMEAS(b,bp) AND battery(k)),
* received from load block bp with battery loss
     eff(k) * m(t,wn,sn,hn,a,i,k,bp,b) * loadblockhours(t,wn,sn,hn,bp) / loadblockhours(t,wn,sn,hn,b)
* sent to load block bp
     - m(t,wn,sn,hn,a,i,k,b,bp)))
*  transmission flows
  + sum(j$ij(j,i), (1 - tlossval) * f(t,wn,sn,hn,j,i,b)) - sum(j$ij(i,j), (1 + tlossval) * f(t,wn,sn,hn,i,j,b))
*  load shedding
  + sum(a$ldc(t,wn,sn,hn,a,b,i), q(t,wn,sn,hn,a,i,b) - ldc(t,wn,sn,hn,a,b,i))
  =G=
  0;


renewcap$capredn..
  (1-frac) * maxNR
  =G=
  sum((a,i,k)$(aik(a,i,k) AND cntlreg(i) AND (NOT renew(k))), z(a,i,k));


* almostsure == flag to do in every scenario
$IFTHEN.ASD almostsure == 1

EQUATION co2cap(t,wn,sn,hn);
EQUATION energycap(t,wn,sn,hn);
EQUATION transboundary(t,wn,sn,hn,i,b);
PARAMETER baseline_imports(t,wn,sn,hn,i,b);

* need to initalize this parameter with something to avoid error
baseline_imports(t,wn,sn,hn,not_cntlreg(i),b) = 1;


transboundary(scn(t,wn,sn,hn),not_cntlreg(i),b)$(1-carbonleakage)..
baseline_imports(t,wn,sn,hn,i,b)
=G=
sum(ij(i,j)$cntlreg(j), wprob(t,wn,sn,hn) * f(t,wn,sn,hn,i,j,b));


co2cap(scn(t,wn,sn,hn))$co2redn..
  (1 - frac) * maxCarbon
  =G=
  sum((a,i,k,b)$(aik(a,i,k) AND carbemit(i,k) AND cntlreg(i)), wprob(t,wn,sn,hn) * loadblockhours(t,wn,sn,hn,b) * y(t,wn,sn,hn,a,i,k,b) * MMTonnesCO2(i,k));


energycap(scn(t,wn,sn,hn))$nrenergyredn..
  (1 - frac) * maxnrEnergy
  =G=
  sum((a,i,k,b)$(aik(a,i,k) AND cntlreg(i) AND (NOT renew(k))), wprob(t,wn,sn,hn) * loadblockhours(t,wn,sn,hn,b) * y(t,wn,sn,hn,a,i,k,b));

$ELSE.ASD


EQUATION co2cap;
EQUATION energycap;
EQUATION transboundary(i,b);
PARAMETER baseline_imports(i,b);

* need to initalize this parameter with something to avoid error
baseline_imports(not_cntlreg(i),b) = 1;

transboundary(not_cntlreg(i),b)$(1-carbonleakage)..
baseline_imports(i,b)
=G=
sum(ij(i,j)$cntlreg(j), sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * f(t,wn,sn,hn,i,j,b)));


co2cap$co2redn..
  (1-frac) * maxCarbon
  =G=
  sum((scn(t,wn,sn,hn),a,i,k,b)$(aik(a,i,k) AND carbemit(i,k) AND cntlreg(i)), wprob(t,wn,sn,hn) * loadblockhours(t,wn,sn,hn,b) * y(t,wn,sn,hn,a,i,k,b) * MMTonnesCO2(i,k));


energycap$nrenergyredn..
  (1-frac) * maxnrEnergy
  =G=
  sum((scn(t,wn,sn,hn),a,i,k,b)$(aik(a,i,k) AND cntlreg(i) AND (NOT renew(k))), wprob(t,wn,sn,hn) * loadblockhours(t,wn,sn,hn,b) * y(t,wn,sn,hn,a,i,k,b));

$ENDIF.ASD


$MACRO ecost(k,i,x) (eC(k,i) * x)
$MACRO ocost(k,z) (oC(k) * z)
* $MACRO gcost(k,y) (gC(k) * y + coeff(k) * sqr(y))
$MACRO gcost(k,y) (gC(k) * y)

$MACRO capZ(t,wn,sn,hn,a) (sum((i,k,b)$(aik(a,i,k) AND gen(k)), loadblockhours(t,wn,sn,hn,b) * gcost(k,y(t,wn,sn,hn,a,i,k,b))) + sum((i,b)$inb(t,wn,sn,hn,i,b), loadblockhours(t,wn,sn,hn,b) * (capR * (q(t,wn,sn,hn,a,i,b) - ldc(t,wn,sn,hn,a,b,i)) + v * q(t,wn,sn,hn,a,i,b))$ldc(t,wn,sn,hn,a,b,i)))

$MACRO capZC(t,wn,sn,hn,a) (sum((i,k,b)$aik(a,i,k), loadblockhours(t,wn,sn,hn,b) * (gcost(k,y(t,wn,sn,hn,a,i,k,b)$gen(k)) + sigma * MMTonnesCO2(i,k) * y(t,wn,sn,hn,a,i,k,b)$carbemit(i,k))) + sum((i,b)$inb(t,wn,sn,hn,i,b), loadblockhours(t,wn,sn,hn,b) * (capR * (q(t,wn,sn,hn,a,i,b) - ldc(t,wn,sn,hn,a,b,i)) + v * q(t,wn,sn,hn,a,i,b))$ldc(t,wn,sn,hn,a,b,i)))


$MACRO capZE(t,wn,sn,hn,a) (capZ(t,wn,sn,hn,a) - sum((i,k,b)$(inb(t,wn,sn,hn,i,b) AND aik(a,i,k) AND gen(k)), pi(t,wn,sn,hn,i,b) * y(t,wn,sn,hn,a,i,k,b)) - sum((i,k,b)$(inb(t,wn,sn,hn,i,b) AND aik(a,i,k) AND battery(k)), pi(t,wn,sn,hn,i,b) * sum(bp$(NOT SAMEAS(b,bp)), eff(k) * m(t,wn,sn,hn,a,i,k,bp,b) * loadblockhours(t,wn,sn,hn,bp)  / loadblockhours(t,wn,sn,hn,b) - m(t,wn,sn,hn,a,i,k,b,bp))) - sum((i,b)$(inb(t,wn,sn,hn,i,b) AND SAMEAS(a,'transmission_agent')), pi(t,wn,sn,hn,i,b) * (sum(j$ij(j,i), (1-tlossval) * f(t,wn,sn,hn,j,i,b)) - sum(j$ij(i,j), (1+tlossval) * f(t,wn,sn,hn,i,j,b)))) - sum((i,b)$(inb(t,wn,sn,hn,i,b) AND ldc(t,wn,sn,hn,a,b,i)), pi(t,wn,sn,hn,i,b) * (q(t,wn,sn,hn,a,i,b) - ldc(t,wn,sn,hn,a,b,i))) + sigma * sum((i,k,b)$(aik(a,i,k) AND carbemit(i,k)), loadblockhours(t,wn,sn,hn,b) * y(t,wn,sn,hn,a,i,k,b) * MMTonnesCO2(i,k)))

* XXXX has not been fixed with new domain structure yet
* $MACRO capZEL(a,n,w,t) (sum((i,k,b)$(aik(a,i,k) AND gen(k)),loadblockhours(t,b)*gcost(k,y.L(t,a,i,k,n,w,b))) + sum((i,b)$inb(t,i,n,b),loadblockhours(t,b)*(capR*(q.L(t,a,i,n,w,b)-ldc(t,a,b,i))+v*q.L(t,a,i,n,w,b))$ldc(t,a,b,i))-sum((i,k,b)$(inb(t,i,n,b) AND aik(a,i,k) AND gen(k)),pi.L(t,i,n,w,b)*y.L(t,a,i,k,n,w,b))-sum((i,k,b)$(inb(t,i,n,b) AND aik(a,i,k) AND battery(k)),pi.L(t,i,n,w,b)*sum(bp$(NOT SAMEAS(b,bp)),eff(k)*m.L(t,a,i,k,n,w,bp,b)*loadblockhours(t,bp)/loadblockhours(t,b)-m.L(t,a,i,k,n,w,b,bp)))-sum((i,b)$(inb(t,i,n,b) AND SAMEAS(a,'transmission_agent')),pi.L(t,i,n,w,b)*(sum(j$ij(j,i), (1-tlossval)*f.L(t,j,i,n,w,b)) - sum(j$ij(i,j), (1+tlossval)*f.L(t,i,j,n,w,b))))-sum((i,b)$(inb(t,i,n,b) AND ldc(t,a,b,i)),pi.L(t,i,n,w,b)*(q.L(t,a,i,n,w,b) - ldc(t,a,b,i)))+sigma.L*sum((i,k,b)$(aik(a,i,k) AND carbemit(i,k)),loadblockhours(t,b)*y.L(t,a,i,k,n,w,b)*MMTonnesCO2(i,k)))

$MACRO capZEL(t,wn,sn,hn,a) (sum((i,k,b)$(aik(a,i,k) AND gen(k)), loadblockhours(t,wn,sn,hn,b) * gcost(k,y.L(t,wn,sn,hn,a,i,k,b))) + sum((i,b)$inb(t,wn,sn,hn,i,b), loadblockhours(t,wn,sn,hn,b) * (capR * (q.L(t,wn,sn,hn,a,i,b) - ldc(t,wn,sn,hn,a,b,i)) + v * q.L(t,wn,sn,hn,a,i,b))$ldc(t,wn,sn,hn,a,b,i)) - sum((i,k,b)$(inb(t,wn,sn,hn,i,b) AND aik(a,i,k) AND gen(k)), pi.L(t,wn,sn,hn,i,b) * y.L(t,wn,sn,hn,a,i,k,b)) - sum((i,k,b)$(inb(t,wn,sn,hn,i,b) AND aik(a,i,k) AND battery(k)), pi.L(t,wn,sn,hn,i,b) * sum(bp$(NOT SAMEAS(b,bp)), eff(k) * m.L(t,wn,sn,hn,a,i,k,bp,b) * loadblockhours(t,wn,sn,hn,bp)/loadblockhours(t,wn,sn,hn,b) - m.L(t,wn,sn,hn,a,i,k,b,bp))) - sum((i,b)$(inb(t,wn,sn,hn,i,b) AND SAMEAS(a,'transmission_agent')), pi.L(t,wn,sn,hn,i,b) * (sum(j$ij(j,i), (1-tlossval) * f.L(t,wn,sn,hn,j,i,b)) - sum(j$ij(i,j), (1+tlossval) * f.L(t,wn,sn,hn,i,j,b)))) - sum((i,b)$(inb(t,wn,sn,hn,i,b) AND ldc(t,wn,sn,hn,a,b,i)), pi.L(t,wn,sn,hn,i,b) * (q.L(t,wn,sn,hn,a,i,b) - ldc(t,wn,sn,hn,a,b,i))))


* EQUATION shortfalldef(n,w0,w1,w2,w3);
* EQUATION CVapdef(a,n,w0,w1,w2,w3);
EQUATION sysobjdef;
EQUATION objdef(a);

sysobjdef..
* Risk averse
  sysobj
  =E=
  sum(a, sum((i,k)$aik(a,i,k), ecost(k,i,x(a,i,k)) + ocost(k,z(a,i,k))))
* this is the expected cost
  + (1-lambda) * sum(a, sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * capZ(t,wn,sn,hn,a)));
* this is the CVaR risk meausre
*  + lambda * (tt + sum(n$prob(n), prob(n) * sum((w0,w1,w2,w3), wtreeprob(w0,w1,w2,w3) * yy(n,w0,w1,w2,w3))) / CVARalpha);


objdef(a)$used(a)..
* Risk averse
  obj(a)
  =E=
  sum((i,k)$aik(a,i,k), ecost(k,i,x(a,i,k)) + ocost(k,z(a,i,k)))
* this is the expected cost
  + (1-lambda$(NOT SAMEAS(a,'transmission_agent'))) * sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * capZE(t,wn,sn,hn,a));
* this is the CVaR risk measure
*  + lambda * (aVap(a) + sum(n$prob(n), prob(n) * sum((w0,w1,w2,w3), wtreeprob(w0,w1,w2,w3) * CVap(a,n,w0,w1,w2,w3) / CVARalpha )))$(NOT SAMEAS(a,'transmission_agent'));


* shortfalldef(n,w0,w1,w2,w3)$lambda..
*   yy(n,w0,w1,w2,w3)
*   =G=
*   sum(a, capZ(a,n,w0,'0')
*   + capZ(a,n,w1,'1')
*   + capZ(a,n,w2,'2')
*   + capZ(a,n,w3,'3'))
*   - tt;

* CVapdef(a,n,w0,w1,w2,w3)$(lambda AND used(a) AND (NOT SAMEAS(a,'transmission_agent')))..
*   CVap(a,n,w0,w1,w2,w3)
*   =G=
*   capZE(a,n,w0,'0')
*   + capZE(a,n,w1,'1')
*   + capZE(a,n,w2,'2')
*   + capZE(a,n,w3,'3')
*   - aVap(a);

* smelter(t,wn,sn,hn,b)..
*   sum(a$aik(a,'SI','DR'), y(t,a,'SI','DR',n,w,b))
*   =E=
*   yfix(t,n);

*** This is the only model that gets solved
MODEL capsysopt / sysobjdef,
*                  totalCapLim,
                  caplim,
*                  buildshut,
                  genClim,
*                  genElim,
                  balance,
                  transboundary,
*                  shortfalldef,
                  renewcap,
                  co2cap,
                  energycap,
                  blim,
                  brate /;
*                  smelter,
*                  nonanticS1,
*                  nonanticS2 /;

* EQUATION Lsysobjdef;
* EQUATION Lshortfalldef(n,w0,w1,w2,w3);
*
* Lshortfalldef(n,w0,w1,w2,w3)$lambda..
*   yy(n,w0,w1,w2,w3)
*   =G=
*   sum(a, capZC(a,n,w0,'0')
*   + capZC(a,n,w1,'1')
*   + capZC(a,n,w2,'2')
*   + capZC(a,n,w3,'3'))
*   - tt;
*
* * Lagragnian model (incentive model)
* Lsysobjdef..
* * Risk averse
*   sysobj
*   =E=
*   sum(a, sum((i,k)$aik(a,i,k), ecost(k,i,x(a,i,k)) + ocost(k,z(a,i,k))))
* * + sigma*z(a,i,k)$(NOT renew(k)) ))
*   + (1-lambda)*sum(a, sum(n$prob(n), sum((w,t), wprob(w,t)*prob(n)*capZC(a,n,w,t))))
*   + lambda*(tt + sum(n$prob(n), prob(n)*sum((w0,w1,w2,w3),wtreeprob(w0,w1,w2,w3)*yy(n,w0,w1,w2,w3)))/CVARalpha);
*
*
* MODEL Lcapsysopt / Lsysobjdef,
*                    caplim,
*                    genClim,
*                    genElim,
*                    balance,
*                    Lshortfalldef,
*                    blim,
*                    brate /;
* *                   smelter,
* *                   nonanticS1,
* *                   nonanticS2 /;
*
*
* * Chance constraints
* EQUATION co2cc(n,w);
* EQUATION probcons;
*
* BINARY VARIABLES delta(n);
*
* SCALAR CCalpha / 0.5 /;
* SCALAR bigM / 1e7 /;
*
*
* * chance contraint
* co2cc(n,w)$prob(n)..
*   sum((t,a,i,k,b)$(aik(a,i,k) AND carbemit(i,k)), loadblockhours(t,b)*y(t,a,i,k,n,w,b)*MMTonnesCO2(i,k))
*   =L=
*   bigM * delta(n);
*
* probcons..
*   sum(n$prob(n), delta(n))
*   =L=
*   CCalpha * sum(n$prob(n), 1);
*
* MODEL ccsysopt / sysobjdef,
*                  caplim,
*                  genClim,
*                  genElim,
*                  balance,
*                  shortfalldef,
*                  co2cc,
*                  probcons,
*                  blim,
*                  brate,
*                  smelter,
*                  nonanticS1,
*                  nonanticS2 /;




*-------------------
* Year 2020 Model Constraints
*-------------------
* scale back load duration curve to current day (2020)
ldc(t,wn,sn,hn,a,b,i) = ldc(t,wn,sn,hn,a,b,i) / growth_factor;

* limit the amount of load shed that is possible
q.UP(scn(t,wn,sn,hn),a,i,b)$inb(t,wn,sn,hn,i,b) = fractionLR * ldc(t,wn,sn,hn,a,b,i);

* transmission line capacities
f.UP(scn(t,wn,sn,hn),i,j,b)$ij(i,j) = fcap(i,j);

* provide some sort of upper bound to investment
* no capacity expansion for Year 2020 -- run system as is
x.UP(a,i,k)$aik(a,i,k) = 0;

* no shutdowns -- run system as is
x.LO(a,i,k)$aik(a,i,k) = 0;
z.LO(a,i,k)$aik(a,i,k) = capU(a,i,k);

* SOLVE Year 2020 Model
frac = 0;
co2redn = 0;
capredn = 0;
nrenergyredn = 0;
carbonleakage = 1;
SOLVE capsysopt USING lp min sysobj;

* calculate year 2020 carbon emissions and non-renewable capacity
maxCarbon = sum((scn(t,wn,sn,hn),a,i,k,b)$(aik(a,i,k) AND carbemit(i,k) AND cntlreg(i)), wprob(t,wn,sn,hn) * loadblockhours(t,wn,sn,hn,b) * y.L(t,wn,sn,hn,a,i,k,b) * MMTonnesCO2(i,k));

maxNR = sum((a,i,k)$(aik(a,i,k) AND cntlreg(i) AND (NOT renew(k))), z.L(a,i,k));

DISPLAY maxCarbon;
DISPLAY maxNR;


PARAMETER z_cntlreg(k,*) 'total capacity for the cntlreg by technology and policy scenario (units: MW)';
PARAMETER x_cntlreg(k,*) 'total built/shutdown capacity for the cntlreg by technology and policy scenario (units: MW)';
PARAMETER y_cntlreg(k,*) 'actual generation for the cntlreg by policy scenario (units: MWh)';

z_cntlreg(k,'2020') = eps + sum((a,i)$cntlreg(i), z.L(a,i,k));
x_cntlreg(k,'2020') = eps + sum((a,i)$cntlreg(i), x.L(a,i,k));
y_cntlreg(k,'2020') = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * sum((a,i)$cntlreg(i), sum(b, y.L(t,wn,sn,hn,a,i,k,b) * loadblockhours_compact(t,b))));
*-------------------

parameter gen_test1(k);
gen_test1(k) = sum((scn(t,wn,sn,hn),a,i,b)$(aik(a,i,k) AND cntlreg(i)), wprob(t,wn,sn,hn) * loadblockhours(t,wn,sn,hn,b) * y.L(t,wn,sn,hn,a,i,k,b));

parameter test1(k);
test1(k) = sum((a,i)$(aik(a,i,k) AND cntlreg(i)), z.L(a,i,k));

option gen_test1:0:0:1;
display gen_test1;

option test1:0:0:5;
display test1;


*-------------------
* Year %proj_year% Model Constraints
*-------------------
* scale to %proj_year% with growth_factor
ldc(t,wn,sn,hn,a,b,i) = ldc(t,wn,sn,hn,a,b,i) * growth_factor;

* limit the amount of load shed that is possible
q.UP(scn(t,wn,sn,hn),a,i,b)$inb(t,wn,sn,hn,i,b) = fractionLR * ldc(t,wn,sn,hn,a,b,i);

* transmission line capacities
f.UP(scn(t,wn,sn,hn),i,j,b)$ij(i,j) = fcap(i,j);

* provide upper bound to investment (investment can happen anywhere in the system)
$INCLUDE 'baseline_capacity_expansion_limits.gms'
aik(a,i,k) = yes$(prodn(a) AND capU(a,i,k) + u(a,i,k) > 0);
* reset constraint
x.UP(a,i,k)$aik(a,i,k) = inf;
x.UP(a,i,k)$aik(a,i,k) = u(a,i,k);

* * shutdowns not allowed
* x.LO(a,i,k)$aik(a,i,k) = 0;
* z.LO(a,i,k)$aik(a,i,k) = capU(a,i,k);

* shutdowns allowed
x.LO(a,i,k)$aik(a,i,k) = -capU(a,i,k);
z.LO(a,i,k)$aik(a,i,k) = 0;


* SOLVE baseline scenario model
frac = 0;
* must hold baseline policy to that generated in 2020
co2redn = 0;
capredn = 1;
nrenergyredn = 0;
carbonleakage = 1;
SOLVE capsysopt USING lp min sysobj;

* * calculate carbon emissions and non-renewable capacity
* maxCarbon = sum((scn(t,wn,sn,hn),a,i,k,b)$(aik(a,i,k) AND carbemit(i,k) AND cntlreg(i)), wprob(t,wn,sn,hn) * loadblockhours(t,wn,sn,hn,b) * y.L(t,wn,sn,hn,a,i,k,b) * MMTonnesCO2(i,k));
*
* maxNR = sum((a,i,k)$(aik(a,i,k) AND cntlreg(i) AND (NOT renew(k))), z.L(a,i,k));
*
* DISPLAY maxCarbon;
* DISPLAY maxNR;

* calculate imports into cntlreg
$IFTHEN.imports almostsure == 1
baseline_imports(scn(t,wn,sn,hn),not_cntlreg(i),b) = sum(ij(i,j)$cntlreg(j), wprob(t,wn,sn,hn) * f.L(t,wn,sn,hn,i,j,b));
$ELSE.imports
baseline_imports(not_cntlreg(i),b) = sum(ij(i,j)$cntlreg(j), sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * f.L(t,wn,sn,hn,i,j,b)));
$ENDIF.imports

display baseline_imports;

z_cntlreg(k,'2030') = eps + sum((a,i)$cntlreg(i), z.L(a,i,k));
x_cntlreg(k,'2030') = eps + sum((a,i)$cntlreg(i), x.L(a,i,k));
y_cntlreg(k,'2030') = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * sum((a,i)$cntlreg(i), sum(b, y.L(t,wn,sn,hn,a,i,k,b) * loadblockhours_compact(t,b))));
*-------------------



*-------------------
* Define SCENARIO Model
*-------------------
* provide upper bound to investment (investment can happen only in cntlreg)
* $INCLUDE 'baseline_capacity_expansion_limits.gms'
* aik(a,i,k) = yes$(prodn(a) AND capU(a,i,k) + u(a,i,k) > 0);
* x.UP(a,i,k)$aik(a,i,k) = inf;
* x.UP(a,i,k)$aik(a,i,k) = u(a,i,k);

* fix expansion in not_cntlreg
x.FX(a,not_cntlreg(i),k)$aik(a,i,k) = x.L(a,i,k);


SET r 'scenario iteration' / 1*5 /;
SET rr / 2020, 2030, #r /;
PARAMETER frac_r(r) /
    '1' 0.00
    '2' 0.20
    '3' 0.40
    '4' 0.60
    '5' 0.80 /;
frac_r(r) = eps + frac_r(r);


*-------------------
* Output data containers
*-------------------
SET ctype / 'Invest', 'Maintain', 'Operate', 'LostLoad' /;
PARAMETER build(i,k,r);
PARAMETER ZZ(t,wn,sn,hn,r);
PARAMETER ZZ_i(t,wn,sn,hn,i,r);
PARAMETER ZL(t,wn,sn,hn,r);
PARAMETER ZL_i(t,wn,sn,hn,i,r);
PARAMETER TotalCost(r);
PARAMETER lostMWhours(r);
PARAMETER capacity(i,k,r);
PARAMETER capacity_2(i,k,r);
PARAMETER ExpCost_r(ctype,r);
PARAMETER ExpCost_ir(ctype,i,r);
* PARAMETER TotalCarbon(a,i,k,b,r);
PARAMETER TotalCarbon_r(r);
PARAMETER TotalCarbon_ir(i,r);
PARAMETER Co2price(r);
PARAMETER f_out(t,wn,sn,hn,i,j,b,r);
PARAMETER y_out(t,wn,sn,hn,i,k,b,r);
PARAMETER q_out(t,wn,sn,hn,i,b,r);
*-------------------


* Loop over policy scenarios
* SET x_title 'Demand Increase (%)' / 1 /;
* SET x_title 'Carbon Reduction (% from baseline)' / 1 /;
SET x_title 'Max Non-Renewable Capacity Reduction (% from baseline)' / 1 /;
* SET x_title 'Carbon Reduction, w/Demand Shock (% from baseline)' / 1 /;

* Demand shock
* ldc(t,wn,sn,hn,a,b,cntlreg(i)) = 1.20 * ldc(t,wn,sn,hn,a,b,i);

LOOP(r,
frac = frac_r(r);
co2redn = 0;
capredn = 1;
nrenergyredn = 0;
carbonleakage = 0;

SOLVE capsysopt USING lp min sysobj;

f_out(scn(t,wn,sn,hn),i,j,b,r) = eps + f.L(t,wn,sn,hn,i,j,b);
y_out(scn(t,wn,sn,hn),i,k,b,r) = eps + sum(a, y.L(t,wn,sn,hn,a,i,k,b));
q_out(scn(t,wn,sn,hn),i,b,r) = eps + sum(a, q.L(t,wn,sn,hn,a,i,b));

build(i,k,r) = eps + sum(a, x.L(a,i,k));
capacity(i,k,r) = eps + sum(a, z.L(a,i,k));
capacity_2(i,k,r) = eps + sum(a, z.L(a,i,k) * (1$(NOT battery(k)) + chargerate(k)$battery(k)));

ZZ(scn(t,wn,sn,hn),r) = eps + sum(a, sum((i,k,b)$(aik(a,i,k) AND gen(k)), loadblockhours(t,wn,sn,hn,b) * gcost(k,y.L(t,wn,sn,hn,a,i,k,b))) + sum((i,b)$inb(t,wn,sn,hn,i,b), loadblockhours(t,wn,sn,hn,b) * (capR * q.L(t,wn,sn,hn,a,i,b) + v * q.L(t,wn,sn,hn,a,i,b))));

ZL(scn(t,wn,sn,hn),r) = eps + sum(a, sum((i,b)$inb(t,wn,sn,hn,i,b), loadblockhours(t,wn,sn,hn,b) * (v * q.L(t,wn,sn,hn,a,i,b))));

ZZ_i(scn(t,wn,sn,hn),i,r) = eps + sum(a, sum((k,b)$(aik(a,i,k) AND gen(k)), loadblockhours(t,wn,sn,hn,b) * gcost(k,y.L(t,wn,sn,hn,a,i,k,b))) + sum(b$inb(t,wn,sn,hn,i,b), loadblockhours(t,wn,sn,hn,b) * (capR * q.L(t,wn,sn,hn,a,i,b) + v * q.L(t,wn,sn,hn,a,i,b))));

ZL_i(scn(t,wn,sn,hn),i,r) = eps + sum(a, sum((b)$inb(t,wn,sn,hn,i,b), loadblockhours(t,wn,sn,hn,b) * (v * q.L(t,wn,sn,hn,a,i,b))));




ExpCost_ir('Invest',i,r) = eps + sum(a, sum(k$aik(a,i,k), ecost(k,i,x.L(a,i,k)))) / scalefac;
ExpCost_ir('Maintain',i,r) = eps + sum(a, sum(k$aik(a,i,k), ocost(k,z.L(a,i,k)))) / scalefac;

ExpCost_ir('Operate',i,r) = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * ZZ_i(t,wn,sn,hn,i,r)) / scalefac;
ExpCost_ir('LostLoad',i,r) = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * ZL_i(t,wn,sn,hn,i,r)) / scalefac;

ExpCost_r('Invest',r) = eps + sum(a, sum((i,k)$aik(a,i,k), ecost(k,i,x.L(a,i,k)))) / scalefac;
ExpCost_r('Maintain',r) = eps + sum(a, sum((i,k)$aik(a,i,k), ocost(k,z.L(a,i,k)))) / scalefac;
ExpCost_r('Operate',r) = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * ZZ(t,wn,sn,hn,r)) / scalefac;
ExpCost_r('LostLoad',r) = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * ZL(t,wn,sn,hn,r)) / scalefac;

TotalCost(r) = sysobj.L / scalefac;

* TotalCarbon(aik(a,i,k),b,r)$(carbemit(i,k)) = max(eps, sum(scn(t,wn,sn,hn)$(cntlreg(i)), wprob(t,wn,sn,hn) * loadblockhours(t,wn,sn,hn,b) * y.L(t,wn,sn,hn,a,i,k,b) * MMTonnesCO2(i,k)));

TotalCarbon_r(r) = eps + sum((scn(t,wn,sn,hn),a,i,k,b)$(aik(a,i,k) AND carbemit(i,k)), wprob(t,wn,sn,hn) * loadblockhours(t,wn,sn,hn,b) * y.L(t,wn,sn,hn,a,i,k,b) * MMTonnesCO2(i,k));

TotalCarbon_ir(i,r) = eps + sum((scn(t,wn,sn,hn),a,k,b)$(aik(a,i,k) AND carbemit(i,k)), wprob(t,wn,sn,hn) * loadblockhours(t,wn,sn,hn,b) * y.L(t,wn,sn,hn,a,i,k,b) * MMTonnesCO2(i,k));

Co2price(r) = eps + (co2cap.M$co2redn + renewcap.M$capredn + energycap.M$nrenergyredn) / scalefac;

lostMWhours(r) =  eps + sum(a, sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * sum((i,b)$inb(t,wn,sn,hn,i,b), loadblockhours(t,wn,sn,hn,b) * (q.L(t,wn,sn,hn,a,i,b)))));

z_cntlreg(k,r) = eps + sum((a,i)$cntlreg(i), z.L(a,i,k));
x_cntlreg(k,r) = eps + sum((a,i)$cntlreg(i), x.L(a,i,k));
y_cntlreg(k,r) = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * sum((a,i)$cntlreg(i), sum(b, y.L(t,wn,sn,hn,a,i,k,b) * loadblockhours_compact(t,b))));
);
*-------------------

display x_cntlreg;
display z_cntlreg;
display y_cntlreg;



*-------------------
* Include file that contains aggregate metrics
*-------------------
$INCLUDE output_report.gms
*-------------------





* FILE uuu /'.%sep%output%sep%addl_cap.csv'/;
* PUT uuu;
* uuu.PW = 32767;
* PUT 'Agent,Region,GenType,Cur Cap (MW),Addl Cap (MW),Tot Cap (MW),Poten Cap (MW),Cost ($/MW/yr)' /;
*
* loop((aik(a,i,k)), PUT a.tl:0 ',' i.tl:0 ',' k.tl:0 ',' capU(a,i,k) ',' x.L(a,i,k) ',' z.L(a,i,k) ','  u(a,i,k) ',' eC(k,i)  /; );
*
*
* EXECUTE 'gdxdump out.gdx symb=ave_y format=csv output=ave_y.csv'
* EXECUTE 'gdxdump out.gdx symb=ave_f format=csv output=ave_f.csv'
* EXECUTE 'gdxdump out.gdx symb=ave_y_cntlreg format=csv output=ave_y_cntlreg.csv'
* EXECUTE 'gdxdump out.gdx symb=ave_y_not_cntlreg format=csv output=ave_y_not_cntlreg.csv'
