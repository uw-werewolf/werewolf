$TITLE Wisconsin Renewable Energy Model -- WEREWOLF

$SETENV GDXCOMPRESS 1
$IFTHENI %system.filesys% == UNIX $SET sep "/"
$ELSE $SET sep "\"
$ENDIF

OPTION limrow = 0;
OPTION limcol = 0;

$IF NOT SETGLOBAL frac $SETGLOBAL frac 0
$IF NOT SETGLOBAL co2redn $SETGLOBAL co2redn 0
$IF NOT SETGLOBAL capredn $SETGLOBAL capredn 0
$IF NOT SETGLOBAL nrenergyredn $SETGLOBAL nrenergyredn 0
$IF NOT SETGLOBAL carbonleakage $SETGLOBAL carbonleakage 1
$IF NOT SETGLOBAL policy_model $SETGLOBAL policy_model 1
$IF NOT SETGLOBAL demand_model $SETGLOBAL demand_model 0

$IF NOT SETGLOBAL processed_data $SETGLOBAL processed_data "processed_werewolf_data.gdx"
$IF NOT SETGLOBAL final_results $SETGLOBAL final_results "final_results.gdx"
$IF NOT SETGLOBAL frac_gdx $SETGLOBAL frac_gdx "frac_gdx.gdx"
* $IF NOT SETGLOBAL solve_model $SETGLOBAL solve_model "solve_mode.gdx"


SCALAR frac / %frac% /;
SCALAR co2redn / %co2redn% /;
SCALAR capredn / %capredn% /;
SCALAR nrenergyredn / %nrenergyredn% /;
SCALAR carbonleakage '1 => no constraint on imports to cntlreg, can be in an almostsure model'/ %carbonleakage% /;

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

$GDXIN "%processed_data%"
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

PARAMETER z_cntlreg(k,*) 'total capacity for the cntlreg by technology and policy scenario (units: MW)';
PARAMETER x_cntlreg(k,*) 'total built/shutdown capacity for the cntlreg by technology and policy scenario (units: MW)';
PARAMETER y_cntlreg(k,*) 'actual generation for the cntlreg by policy scenario (units: MWh)';


$IFTHEN %policy_model% == 1
EXECUTE "echo RUNNING... policy model";
$INCLUDE werewolf_3_1_policy_model.gms
$ENDIF

$IFTHEN %demand_model% == 1
EXECUTE "echo RUNNING... demand model";
$INCLUDE werewolf_3_1_demand_model.gms
$ENDIF


display x_cntlreg;
display z_cntlreg;
display y_cntlreg;


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
EXECUTE_UNLOAD "%final_results%";
*-------------------

$exit

*-------------------
* Include file that contains python scripts
*-------------------
$INCLUDE werewolf_4_reports.gms
*-------------------
