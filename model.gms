$TITLE Wisconsin Renewable Energy Model -- WEREWOLF

$SETENV GDXCOMPRESS 1
$IFTHENI %system.filesys% == UNIX $SET sep "/"
$ELSE $SET sep "\"
$ENDIF

OPTION limrow = 0;
OPTION limcol = 0;

SCALAR frac / 0 /;
SCALAR co2redn / 1 /;
SCALAR capredn / 0 /;
SCALAR nrenergyredn / 0 /;
SCALAR tlossval / 0.01 /;

ALIAS(b,bp);

* POSITIVE VARIABLE CVap(a,n,w0,w1,w2,w3) 'shortfall variables for cvar';
* POSITIVE VARIABLE yy(n,w0,w1,w2,w3) 'shortfall variables for cvar';
* POSITIVE VARIABLE s(i,n,t) 'energy transfer from season t to t+1 in region in scenario n';

POSITIVE VARIABLE sigma;

* first stage decision variables
VARIABLE x(a,i,k) 'cap expansion at i in technology k';
POSITIVE VARIABLE z(a,i,k) 'capacity after expansion in k';

* second stage decision variables
POSITIVE VARIABLE pi(t,wn,hn,i,b);
POSITIVE VARIABLE y(t,wn,hn,a,i,k,b) 'generation by agent a using technology k in block b (units: MW)';
POSITIVE VARIABLE q(t,wn,hn,a,i,b) 'load shed by a at location i in block b';
POSITIVE VARIABLE m(t,wn,hn,a,i,k,b,bp) 'supply (MW) at i moved from b to bp using battery tech k';
POSITIVE VARIABLE f(t,wn,hn,i,j,b) 'energy flow from location i to location j';
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

SET inb(t,wn,hn,i,b) 'demand at i in block b in some scenario scn(t,wn,hn)';
inb(scn(t,wn,hn),i,b) = yes$(wprob(t,wn,hn) * smax(a, ldc(t,wn,hn,a,b,i)) > 0);

SET carbemit(i,k) 'technolgies that emit carbon at a node i';
carbemit(i,k) = yes$(MMTonnesCO2(i,k) > 0);


* scale cost data
SCALAR scalefac / 1e-3 /;
PARAMETER eC(k,i) 'capital costs (units: $/MW/year)';
PARAMETER oC(k) 'operating costs (units: $/MW/yr)';
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
EQUATION genClim(t,wn,hn,a,i,k,b);
EQUATION genElim(t,wn,hn,a,i,k);
EQUATION blim(t,wn,hn,a,i,k);
EQUATION brate(t,wn,hn,a,i,k,b);
EQUATION balance(t,wn,hn,i,b);
EQUATION renewcap;
* EQUATION smelter(t,wn,hn,b);
* EQUATION nonanticS1(i,n,t);
* EQUATION nonanticS2(i,n,t);


caplim(a,i,k)$aik(a,i,k)..
  z(a,i,k)
  =L=
  x(a,i,k) + capU(a,i,k);


genClim(scn(t,wn,hn),a,i,k,b)$(aik(a,i,k) AND gen(k))..
  y(t,wn,hn,a,i,k,b)
  =L=
  tmu(t,wn,hn,i,k,b) * z(a,i,k);



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

blim(scn(t,wn,hn),a,i,k)$(aik(a,i,k) AND battery(k))..
  sum(b, loadblockhours(t,wn,hn,b) * sum(bp$(NOT SAMEAS(b,bp)), m(t,wn,hn,a,i,k,b,bp)))
  =L=
  sum(b, z(a,i,k) * loadblockhours(t,wn,hn,b));


brate(scn(t,wn,hn),a,i,k,b)$(aik(a,i,k) AND battery(k))..
  sum(bp$(NOT SAMEAS(b,bp)), m(t,wn,hn,a,i,k,b,bp))
  =L=
  z(a,i,k) * chargerate(k);


balance(scn(t,wn,hn),i,b)$(inb(t,wn,hn,i,b))..
  sum((a,k)$aik(a,i,k), y(t,wn,hn,a,i,k,b)$gen(k) + sum(bp$(NOT SAMEAS(b,bp) AND battery(k)),
* received from load block bp with battery loss
     eff(k) * m(t,wn,hn,a,i,k,bp,b) * loadblockhours(t,wn,hn,bp) / loadblockhours(t,wn,hn,b)
* sent to load block bp
     - m(t,wn,hn,a,i,k,b,bp)))
*  transmission flows
  + sum(j$ij(j,i), (1 - tlossval) * f(t,wn,hn,j,i,b)) - sum(j$ij(i,j), (1 + tlossval) * f(t,wn,hn,i,j,b))
*  load shedding
  + sum(a$ldc(t,wn,hn,a,b,i), q(t,wn,hn,a,i,b) - ldc(t,wn,hn,a,b,i))
  =G=
  0;


renewcap$capredn..
  (1-frac) * maxNR
  =G=
  sum((a,i,k)$(aik(a,i,k) AND cntlreg(i) AND (NOT renew(k))), z(a,i,k));


* %almostsure% == flag to do in every scenario
$IFTHEN.ASD %almostsure% == 1

EQUATION co2cap(t,wn,hn);
EQUATION energycap(t,wn,hn);

co2cap(scn(t,wn,hn))$co2redn..
  (1 - frac) * maxCarbon
  =G=
  sum((a,i,k,b)$(aik(a,i,k) AND carbemit(i,k) AND cntlreg(i)), wprob(t,wn,hn) * loadblockhours(t,wn,hn,b) * y(t,wn,hn,a,i,k,b) * MMTonnesCO2(i,k));

energycap(scn(t,wn,hn))$nrenergyredn..
  (1 - frac) * maxnrEnergy
  =G=
  sum((a,i,k,b)$(aik(a,i,k) AND cntlreg(i) AND (NOT renew(k))), wprob(t,wn,hn) * loadblockhours(t,wn,hn,b) * y(t,wn,hn,a,i,k,b));

$ELSE.ASD


EQUATION co2cap;
EQUATION energycap;

co2cap$co2redn..
  (1-frac) * maxCarbon
  =G=
  sum((scn(t,wn,hn),a,i,k,b)$(aik(a,i,k) AND carbemit(i,k) AND cntlreg(i)), wprob(t,wn,hn) * loadblockhours(t,wn,hn,b) * y(t,wn,hn,a,i,k,b) * MMTonnesCO2(i,k));

energycap$nrenergyredn..
  (1-frac) * maxnrEnergy
  =G=
  sum((scn(t,wn,hn),a,i,k,b)$(aik(a,i,k) AND cntlreg(i) AND (NOT renew(k))), wprob(t,wn,hn) * loadblockhours(t,wn,hn,b) * y(t,wn,hn,a,i,k,b));

$ENDIF.ASD


$MACRO ecost(k,i,x) (eC(k,i) * x)
$MACRO ocost(k,z) (oC(k) * z)
* $MACRO gcost(k,y) (gC(k) * y + coeff(k) * sqr(y))
$MACRO gcost(k,y) (gC(k) * y)

$MACRO capZ(t,wn,hn,a) (sum((i,k,b)$(aik(a,i,k) AND gen(k)), loadblockhours(t,wn,hn,b) * gcost(k,y(t,wn,hn,a,i,k,b))) + sum((i,b)$inb(t,wn,hn,i,b), loadblockhours(t,wn,hn,b) * (capR * (q(t,wn,hn,a,i,b) - ldc(t,wn,hn,a,b,i)) + v * q(t,wn,hn,a,i,b))$ldc(t,wn,hn,a,b,i)))

$MACRO capZC(t,wn,hn,a) (sum((i,k,b)$aik(a,i,k), loadblockhours(t,wn,hn,b) * (gcost(k,y(t,wn,hn,a,i,k,b)$gen(k)) + sigma * MMTonnesCO2(i,k) * y(t,wn,hn,a,i,k,b)$carbemit(i,k))) + sum((i,b)$inb(t,wn,hn,i,b), loadblockhours(t,wn,hn,b) * (capR * (q(t,wn,hn,a,i,b) - ldc(t,wn,hn,a,b,i)) + v * q(t,wn,hn,a,i,b))$ldc(t,wn,hn,a,b,i)))


$MACRO capZE(t,wn,hn,a) (capZ(t,wn,hn,a) - sum((i,k,b)$(inb(t,wn,hn,i,b) AND aik(a,i,k) AND gen(k)), pi(t,wn,hn,i,b) * y(t,wn,hn,a,i,k,b)) - sum((i,k,b)$(inb(t,wn,hn,i,b) AND aik(a,i,k) AND battery(k)), pi(t,wn,hn,i,b) * sum(bp$(NOT SAMEAS(b,bp)), eff(k) * m(t,wn,hn,a,i,k,bp,b) * loadblockhours(t,wn,hn,bp)  / loadblockhours(t,wn,hn,b) - m(t,wn,hn,a,i,k,b,bp))) - sum((i,b)$(inb(t,wn,hn,i,b) AND SAMEAS(a,'transmission_agent')), pi(t,wn,hn,i,b) * (sum(j$ij(j,i), (1-tlossval) * f(t,wn,hn,j,i,b)) - sum(j$ij(i,j), (1+tlossval) * f(t,wn,hn,i,j,b)))) - sum((i,b)$(inb(t,wn,hn,i,b) AND ldc(t,wn,hn,a,b,i)), pi(t,wn,hn,i,b) * (q(t,wn,hn,a,i,b) - ldc(t,wn,hn,a,b,i))) + sigma * sum((i,k,b)$(aik(a,i,k) AND carbemit(i,k)), loadblockhours(t,wn,hn,b) * y(t,wn,hn,a,i,k,b) * MMTonnesCO2(i,k)))

* XXXX has not been fixed with new domain structure yet
* $MACRO capZEL(a,n,w,t) (sum((i,k,b)$(aik(a,i,k) AND gen(k)),loadblockhours(t,b)*gcost(k,y.L(t,a,i,k,n,w,b))) + sum((i,b)$inb(t,i,n,b),loadblockhours(t,b)*(capR*(q.L(t,a,i,n,w,b)-ldc(t,a,b,i))+v*q.L(t,a,i,n,w,b))$ldc(t,a,b,i))-sum((i,k,b)$(inb(t,i,n,b) AND aik(a,i,k) AND gen(k)),pi.L(t,i,n,w,b)*y.L(t,a,i,k,n,w,b))-sum((i,k,b)$(inb(t,i,n,b) AND aik(a,i,k) AND battery(k)),pi.L(t,i,n,w,b)*sum(bp$(NOT SAMEAS(b,bp)),eff(k)*m.L(t,a,i,k,n,w,bp,b)*loadblockhours(t,bp)/loadblockhours(t,b)-m.L(t,a,i,k,n,w,b,bp)))-sum((i,b)$(inb(t,i,n,b) AND SAMEAS(a,'transmission_agent')),pi.L(t,i,n,w,b)*(sum(j$ij(j,i), (1-tlossval)*f.L(t,j,i,n,w,b)) - sum(j$ij(i,j), (1+tlossval)*f.L(t,i,j,n,w,b))))-sum((i,b)$(inb(t,i,n,b) AND ldc(t,a,b,i)),pi.L(t,i,n,w,b)*(q.L(t,a,i,n,w,b) - ldc(t,a,b,i)))+sigma.L*sum((i,k,b)$(aik(a,i,k) AND carbemit(i,k)),loadblockhours(t,b)*y.L(t,a,i,k,n,w,b)*MMTonnesCO2(i,k)))

$MACRO capZEL(t,wn,hn,a) (sum((i,k,b)$(aik(a,i,k) AND gen(k)), loadblockhours(t,wn,hn,b) * gcost(k,y.L(t,wn,hn,a,i,k,b))) + sum((i,b)$inb(t,wn,hn,i,b), loadblockhours(t,wn,hn,b) * (capR * (q.L(t,wn,hn,a,i,b) - ldc(t,wn,hn,a,b,i)) + v * q.L(t,wn,hn,a,i,b))$ldc(t,wn,hn,a,b,i)) - sum((i,k,b)$(inb(t,wn,hn,i,b) AND aik(a,i,k) AND gen(k)), pi.L(t,wn,hn,i,b) * y.L(t,wn,hn,a,i,k,b)) - sum((i,k,b)$(inb(t,wn,hn,i,b) AND aik(a,i,k) AND battery(k)), pi.L(t,wn,hn,i,b) * sum(bp$(NOT SAMEAS(b,bp)), eff(k) * m.L(t,wn,hn,a,i,k,bp,b) * loadblockhours(t,wn,hn,bp)/loadblockhours(t,wn,hn,b) - m.L(t,wn,hn,a,i,k,b,bp))) - sum((i,b)$(inb(t,wn,hn,i,b) AND SAMEAS(a,'transmission_agent')), pi.L(t,wn,hn,i,b) * (sum(j$ij(j,i), (1-tlossval) * f.L(t,wn,hn,j,i,b)) - sum(j$ij(i,j), (1+tlossval) * f.L(t,wn,hn,i,j,b)))) - sum((i,b)$(inb(t,wn,hn,i,b) AND ldc(t,wn,hn,a,b,i)), pi.L(t,wn,hn,i,b) * (q.L(t,wn,hn,a,i,b) - ldc(t,wn,hn,a,b,i))))


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
  + (1-lambda) * sum(a, sum(scn(t,wn,hn), wprob(t,wn,hn) * capZ(t,wn,hn,a)));
* this is the CVaR risk meausre
*  + lambda * (tt + sum(n$prob(n), prob(n) * sum((w0,w1,w2,w3), wtreeprob(w0,w1,w2,w3) * yy(n,w0,w1,w2,w3))) / CVARalpha);


objdef(a)$used(a)..
* Risk averse
  obj(a)
  =E=
  sum((i,k)$aik(a,i,k), ecost(k,i,x(a,i,k)) + ocost(k,z(a,i,k)))
* this is the expected cost
  + (1-lambda$(NOT SAMEAS(a,'transmission_agent'))) * sum(scn(t,wn,hn), wprob(t,wn,hn) * capZE(t,wn,hn,a));
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

* smelter(t,wn,hn,b)..
*   sum(a$aik(a,'SI','DR'), y(t,a,'SI','DR',n,w,b))
*   =E=
*   yfix(t,n);

*** This is the only model that gets solved
MODEL capsysopt / sysobjdef,
                  caplim,
                  genClim,
*                  genElim,
                  balance,
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
* Additional model constraints
*-------------------
q.UP(scn(t,wn,hn),a,i,b)$inb(t,wn,hn,i,b) = fractionLR * ldc(t,wn,hn,a,b,i);
f.UP(scn(t,wn,hn),i,j,b)$ij(i,j) = fcap(i,j);
* s.UP(i,n,t) = reservoircap(i);
x.UP(a,i,k)$aik(a,i,k) = u(a,i,k);

* allow shutdowns? (zero = no)
x.LO(a,i,k)$aik(a,i,k) = 0;

m.FX(t,wn,hn,a,i,battery(k),b,bp) = 0;

* allow carbon shutdowns?
* z.LO(a,i,k)$aik(a,i,k) = capU(a,i,k)$(NOT carbemit(i,k));

* No shutdowns
z.LO(a,i,k)$aik(a,i,k) = capU(a,i,k);
*-------------------






*-------------------
* Solver options
*-------------------
* $onecho > cplex.opt
* baralg 3
* $offecho
*
* capsysopt.optfile = 1;
*-------------------


SET ctype / 'Invest', 'Maintain', 'Operate', 'LostLoad' /;
SET r 'scenario iteration' / 1 /;
PARAMETER frac_r(r) /
    '1' 0.00 /;
* '2' 0.20 /;
* '3' 0.40
* '4' 0.60
* '5' 0.80 /;


*-------------------
* Output data containers
*-------------------
PARAMETER build(a,i,k,r);
PARAMETER ZZ(t,wn,hn,r);
PARAMETER ZL(t,wn,hn,r);
PARAMETER TotalCost(r);
PARAMETER lostMWhours(r,a);
PARAMETER capacity(r,a,i,k);
PARAMETER ExpCost(r,ctype)
PARAMETER TotalCostM(r);
PARAMETER TotalCarbon(a,i,k,b,r);
PARAMETER TotalCarbon_r(r);
PARAMETER Co2price(r);
PARAMETER lostloadenergy(a,*);
PARAMETER f_out(t,wn,hn,i,j,b,r);
PARAMETER y_out(t,wn,hn,a,i,k,b,r);
PARAMETER q_out(t,wn,hn,a,i,b,r);
*-------------------



LOOP(r,
frac = frac_r(r);

SOLVE capsysopt USING lp min sysobj;

f_out(scn(t,wn,hn),i,j,b,r) = f.L(t,wn,hn,i,j,b);
y_out(scn(t,wn,hn),a,i,k,b,r) = y.L(t,wn,hn,a,i,k,b);
q_out(scn(t,wn,hn),a,i,b,r) = q.L(t,wn,hn,a,i,b);

build(a,i,k,r) = x.L(a,i,k);

* ZZ(scn(t,wn,hn),r) = sum(a, sum((i,k,b)$(aik(a,i,k) AND gen(k)), loadblockhours(t,n,w,b) * gcost(k,y.L(t,n,w,a,i,k,b)))
*                   + sum((i,b)$inb(t,n,w,i,b), loadblockhours(t,n,w,b) * (capR * q.L(t,n,w,a,i,b) + 0 * q.L(t,n,w,a,i,b))));
*
* ZL(scn(t,wn,hn),r) = sum(a, sum((i,b)$inb(t,n,w,i,b), loadblockhours(t,n,w,b) * (v * q.L(t,n,w,a,i,b))));
*
* ExpCost(r,'Invest') = (sum(a, sum((i,k)$aik(a,i,k), ecost(k,x.L(a,i,k))))) / scalefac;
* ExpCost(r,'Maintain') = sum(a, sum((i,k)$aik(a,i,k), ocost(k,z.L(a,i,k)))) / scalefac;
* ExpCost(r,'Operate') = sum(scn(t,wn,hn), wprob(t,n,w) * ZZ(t,n,w,r)) / scalefac;
* ExpCost(r,'LostLoad') = sum(scn(t,wn,hn), wprob(t,n,w) * ZL(t,n,w,r)) / scalefac;
*
* TotalCost(r) = sysobj.L / scalefac;
* TotalCostM(r) = max(eps, TotalCost(r) / 1000000);
TotalCarbon(aik(a,i,k),b,r)$(carbemit(i,k)) = max(eps, sum(scn(t,wn,hn)$(cntlreg(i)), wprob(t,wn,hn) * loadblockhours(t,wn,hn,b) * y.L(t,wn,hn,a,i,k,b) * MMTonnesCO2(i,k)));

TotalCarbon_r(r) = max(eps, sum((scn(t,wn,hn),a,i,k,b)$(aik(a,i,k) AND carbemit(i,k) AND cntlreg(i)), wprob(t,wn,hn) * loadblockhours(t,wn,hn,b) * y.L(t,wn,hn,a,i,k,b) * MMTonnesCO2(i,k)));


* * # Co2price(r) = max(eps,(co2cap.m$co2redn + renewcap.m$capredn + energycap.m$nrenergyredn)/scalefac);
* lostMWhours(r,a) =  sum(scn(t,wn,hn), wprob(t,n,w) * sum((i,b)$inb(t,n,w,i,b), loadblockhours(t,n,w,b) * (q.L(t,n,w,a,i,b))));
*
* capacity(r,a,i,k) = eps + z.L(a,i,k) * (1$(NOT battery(k)) + chargerate(k)$battery(k));

)


* PARAMETER ave_f(i,j,b,r);
*
* ALIAS(t,tp);
* ALIAS(n,np);
* ALIAS(w,wp);
* ave_f(i,j,b,r) = sum(scn(t,wn,hn), f_out(t,n,w,i,j,b,r)) / sum(scn(tp,np,wp), 1);

EXECUTE_UNLOAD 'out.gdx';
