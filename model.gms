$INCLUDE 'decl.gms'

OPTION limrow = 0;
OPTION limcol = 0;

SCALAR frac / 0 /;
SCALAR co2redn / 0 /;
SCALAR capredn / 0 /;
SCALAR nrenergyredn / 1 /;
scalar tlossval / 0.01 /;

ALIAS(b,bp);

POSITIVE VARIABLE CVap(a,n,w0,w1,w2,w3) 'shortfall variables for cvar';
POSITIVE VARIABLE sigma;
POSITIVE VARIABLE pi(t,i,n,w,b);
POSITIVE VARIABLE yy(n,w0,w1,w2,w3) 'shortfall variables for cvar';
POSITIVE VARIABLE z(a,i,k) 'capacity after expansion in k';
POSITIVE VARIABLE y(t,a,i,k,n,w,b) 'generation by agent a using technology k in block b';
POSITIVE VARIABLE q(t,a,i,n,w,b) 'load shed by a at location i in block b';
POSITIVE VARIABLE m(t,a,i,k,n,w,b,bp) 'supply (MW)at i moved from b to bp using battery tech k';
POSITIVE VARIABLE f(t,i,j,n,w,b) 'energy at location i moved to location j';
* POSITIVE VARIABLE s(i,n,t) 'energy transfer from season t to t+1 in region in scenario n';
POSITIVE VARIABLE saverage(i,t) 'nonanticipative storage';

VARIABLE tt 'Var';
VARIABLE aVap(a);
VARIABLE yfix(t,n) 'for smelter';
VARIABLE x(a,i,k) 'cap expansion at i in technology k';
VARIABLE obj(a);
VARIABLE sysobj;


* convenience sets
SET aik(a,i,k) 'agent has technology k at location i';
aik(a,i,k) = yes$(prodn(a) AND capU(a,i,k) + u(a,i,k) > 0);

SET inb(t,i,n,b) 'demand at i in block b in some scenario n';
inb(t,i,n,b) = yes$(prob(n) * smax(a, load(t,a,b,i)) > 0);

SET carbemit(k) 'technolgies that emit carbon';
*carbemit(k) = yes$((NOT renew(k)) AND TonnesCO2(k) > 0);
carbemit(k) = yes$(TonnesCO2(k) > 0);


* scale cost data
SCALAR scalefac / 1e-3 /;
eC(k) = eC(k) * scalefac;
oC(k) = oC(k) * scalefac;
gC(k) = gC(k) * scalefac;
coeff(k) = coeff(k) * scalefac;
capR = capR * scalefac;
v = v * scalefac;

EQUATION caplim(a,i,k);
EQUATION genClim(t,a,i,k,n,w,b);
EQUATION genElim(a,i,k,n,w,t);
EQUATION blim(t,a,i,k,n,w);
EQUATION brate(t,a,i,k,n,w,b);
EQUATION balance(t,i,n,w,b);
EQUATION renewcap;
* EQUATION smelter(t,n,w,b);
* EQUATION nonanticS1(i,n,t);
* EQUATION nonanticS2(i,n,t);


caplim(a,i,k)$aik(a,i,k)..
  z(a,i,k)
  =L=
  x(a,i,k) + capU(a,i,k);

genClim(t,a,i,k,n,w,b)$(aik(a,i,k) AND prob(n) AND gen(k))..
  y(t,a,i,k,n,w,b)
  =L=
  tmu(t,i,k,n,w,b) * z(a,i,k);

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
blim(t,a,i,k,n,w)$(aik(a,i,k) AND prob(n) AND store(k))..
  sum(b, loadblockhours(t,b)*sum(bp$(NOT SAMEAS(b,bp)), m(t,a,i,k,n,w,b,bp)))
  =L=
  z(a,i,k) * loadblockdays(t,i);

brate(t,a,i,k,n,w,b)$(aik(a,i,k) AND prob(n) AND store(k))..
  sum(bp$(NOT SAMEAS(b,bp)), m(t,a,i,k,n,w,b,bp))
  =L=
  z(a,i,k) * chargerate(k);

balance(t,i,n,w,b)$inb(t,i,n,b)..
  sum((a,k)$aik(a,i,k), y(t,a,i,k,n,w,b)$gen(k) + sum(bp$(NOT SAMEAS(b,bp) AND store(k)),
* received from load block bp with battery loss
     eff(k)*m(t,a,i,k,n,w,bp,b) * loadblockhours(t,bp) / loadblockhours(t,b)
* sent to load block bp
     - m(t,a,i,k,n,w,b,bp)))

*  transmission flows
  + sum(j$ij(j,i), (1-tlossval) * f(t,j,i,n,w,b)) - sum(j$ij(i,j), (1+tlossval) * f(t,i,j,n,w,b))
*  load shedding
  + sum(a$load(t,a,b,i), q(t,a,i,n,w,b) - load(t,a,b,i)) =G= 0;

renewcap$capredn..
  (1-frac) * maxNR
  =G=
  sum((a,i,k)$(aik(a,i,k) AND (NOT renew(k))), z(a,i,k));

* %almostsure% == flag to do in every scenario
$IFTHEN.ASD %almostsure% == 1

EQUATION co2cap(n);
EQUATION energycap(n);

co2cap(n)$(co2redn AND prob(n))..
  (1-frac) * maxCarbon
  =G=
  sum((t,a,i,k,w,b)$(aik(a,i,k) AND carbemit(k)), wprob(w,t) * loadblockhours(t,b) * y(t,a,i,k,n,w,b) * TonnesCO2(k));

energycap(n)$(nrenergyredn AND prob(n))..
  (1-frac) * maxnrEnergy
  =G=
  sum((t,a,i,k,w,b)$(aik(a,i,k) AND (NOT renew(k))), wprob(w,t) * loadblockhours(t,b) * y(t,a,i,k,n,w,b));

$ELSE.ASD

EQUATION co2cap;
EQUATION energycap;

co2cap$co2redn..
  (1-frac) * maxCarbon
  =G=
  sum((t,a,i,k,n,w,b)$(aik(a,i,k) AND carbemit(k) AND prob(n)), prob(n) * wprob(w,t) * loadblockhours(t,b) * y(t,a,i,k,n,w,b) * TonnesCO2(k));

energycap$nrenergyredn..
  (1-frac) * maxnrEnergy
  =G= sum((t,a,i,k,n,w,b)$(aik(a,i,k) AND (NOT renew(k)) AND prob(n)), prob(n) * wprob(w,t) * loadblockhours(t,b) * y(t,a,i,k,n,w,b));

$ENDIF.ASD

$MACRO ecost(k,x) (eC(k) * x)
$MACRO ocost(k,z) (oC(k) * z)
* $MACRO gcost(k,y) (gC(k) * y + coeff(k) * sqr(y))
$MACRO gcost(k,y) (gC(k) * y)

$MACRO capZ(a,n,w,t) (sum((i,k,b)$(aik(a,i,k) AND gen(k)),loadblockhours(t,b) * gcost(k,y(t,a,i,k,n,w,b))) + sum((i,b)$inb(t,i,n,b),loadblockhours(t,b)*(capR*(q(t,a,i,n,w,b)-load(t,a,b,i))+v*q(t,a,i,n,w,b))$load(t,a,b,i)))

$MACRO capZC(a,n,w,t) (sum((i,k,b)$aik(a,i,k),loadblockhours(t,b)*(gcost(k,y(t,a,i,k,n,w,b)$gen(k))+sigma*TonnesCO2(k)*y(t,a,i,k,n,w,b)$carbemit(k))) + sum((i,b)$inb(t,i,n,b),loadblockhours(t,b)*(capR*(q(t,a,i,n,w,b)-load(t,a,b,i))+v*q(t,a,i,n,w,b))$load(t,a,b,i)))

$MACRO capZE(a,n,w,t) (capZ(a,n,w,t)-sum((i,k,b)$(inb(t,i,n,b) AND aik(a,i,k) AND gen(k)),pi(t,i,n,w,b)*y(t,a,i,k,n,w,b))-sum((i,k,b)$(inb(t,i,n,b) AND aik(a,i,k) AND store(k)),pi(t,i,n,w,b)*sum(bp$(NOT SAMEAS(b,bp)),eff(k)*m(t,a,i,k,n,w,bp,b)*loadblockhours(t,bp)/loadblockhours(t,b)-m(t,a,i,k,n,w,b,bp)))-sum((i,b)$(inb(t,i,n,b) AND SAMEAS(a,'trn')),pi(t,i,n,w,b)*(sum(j$ij(j,i), (1-tlossval)*f(t,j,i,n,w,b)) - sum(j$ij(i,j), (1+tlossval)*f(t,i,j,n,w,b))))-sum((i,b)$(inb(t,i,n,b) AND load(t,a,b,i)),pi(t,i,n,w,b)*(q(t,a,i,n,w,b) - load(t,a,b,i)))+sigma*sum((i,k,b)$(aik(a,i,k) AND carbemit(k)),loadblockhours(t,b)*y(t,a,i,k,n,w,b)*TonnesCO2(k)))

* $MACRO capZEL(a,n,w,t) (sum((i,k,b)$(aik(a,i,k) AND gen(k)),loadblockhours(t,b)*gcost(k,y.l(t,a,i,k,n,w,b))) + sum((i,b)$inb(t,i,n,b),loadblockhours(t,b)*(capR*(q.l(t,a,i,n,w,b)-load(t,a,b,i))+v*q.l(t,a,i,n,w,b))$load(t,a,b,i))-sum((i,k,b)$(inb(t,i,n,b) AND aik(a,i,k) AND gen(k)),pi.l(t,i,n,w,b)*y.l(t,a,i,k,n,w,b))-sum((i,k,b)$(inb(t,i,n,b) AND aik(a,i,k) AND store(k)),pi.l(t,i,n,w,b)*sum(bp$(NOT SAMEAS(b,bp)),eff(k)*m.l(t,a,i,k,n,w,bp,b)*loadblockhours(t,bp)/loadblockhours(t,b)-m.l(t,a,i,k,n,w,b,bp)))-sum((i,b)$(inb(t,i,n,b) AND SAMEAS(a,'trn')),pi.l(t,i,n,w,b)*(sum(j$ij(j,i), (1-tlossval)*f.l(t,j,i,n,w,b)) - sum(j$ij(i,j), (1+tlossval)*f.l(t,i,j,n,w,b))))-sum((i,b)$(inb(t,i,n,b) AND load(t,a,b,i)),pi.l(t,i,n,w,b)*(q.l(t,a,i,n,w,b) - load(t,a,b,i)))+sigma.l*sum((i,k,b)$(aik(a,i,k) AND carbemit(k)),loadblockhours(t,b)*y.l(t,a,i,k,n,w,b)*TonnesCO2(k)))

$MACRO capZEL(a,n,w,t) (sum((i,k,b)$(aik(a,i,k) AND gen(k)),loadblockhours(t,b)*gcost(k,y.l(t,a,i,k,n,w,b))) + sum((i,b)$inb(t,i,n,b),loadblockhours(t,b)*(capR*(q.l(t,a,i,n,w,b)-load(t,a,b,i))+v*q.l(t,a,i,n,w,b))$load(t,a,b,i))-sum((i,k,b)$(inb(t,i,n,b) AND aik(a,i,k) AND gen(k)),pi.l(t,i,n,w,b)*y.l(t,a,i,k,n,w,b))-sum((i,k,b)$(inb(t,i,n,b) AND aik(a,i,k) AND store(k)),pi.l(t,i,n,w,b)*sum(bp$(NOT SAMEAS(b,bp)),eff(k)*m.l(t,a,i,k,n,w,bp,b)*loadblockhours(t,bp)/loadblockhours(t,b)-m.l(t,a,i,k,n,w,b,bp)))-sum((i,b)$(inb(t,i,n,b) AND SAMEAS(a,'trn')),pi.l(t,i,n,w,b)*(sum(j$ij(j,i), (1-tlossval)*f.l(t,j,i,n,w,b)) - sum(j$ij(i,j), (1+tlossval)*f.l(t,i,j,n,w,b))))-sum((i,b)$(inb(t,i,n,b) AND load(t,a,b,i)),pi.l(t,i,n,w,b)*(q.l(t,a,i,n,w,b) - load(t,a,b,i))))

EQUATION shortfalldef(n,w0,w1,w2,w3);
EQUATION CVapdef(a,n,w0,w1,w2,w3);
EQUATION sysobjdef;
EQUATION objdef(a);

sysobjdef..
* Risk averse
  sysobj
  =E=
  sum(a, sum((i,k)$aik(a,i,k), ecost(k,x(a,i,k)) + ocost(k,z(a,i,k))))
* this is the expected cost
  + (1-lambda) * sum(a, sum(n$prob(n), sum((w,t), wprob(w,t) * prob(n) * capZ(a,n,w,t))));
* this is the CVaR risk meausre
*  + lambda * (tt + sum(n$prob(n), prob(n) * sum((w0,w1,w2,w3), wtreeprob(w0,w1,w2,w3) * yy(n,w0,w1,w2,w3))) / CVARalpha);

objdef(a)$used(a)..
* Risk averse
  obj(a)
  =E=
  sum((i,k)$aik(a,i,k), ecost(k,x(a,i,k)) + ocost(k,z(a,i,k)))
* this is the expected cost
  + (1-lambda$(NOT SAMEAS(a,'trn'))) * sum(n$prob(n), sum((w,t), wprob(w,t) * prob(n) * capZE(a,n,w,t)));
* this is the CVaR risk measure
*  + lambda * (aVap(a) + sum(n$prob(n), prob(n) * sum((w0,w1,w2,w3), wtreeprob(w0,w1,w2,w3) * CVap(a,n,w0,w1,w2,w3) / CVARalpha )))$(NOT SAMEAS(a,'trn'));


* shortfalldef(n,w0,w1,w2,w3)$lambda..
*   yy(n,w0,w1,w2,w3)
*   =G=
*   sum(a, capZ(a,n,w0,'0')
*   + capZ(a,n,w1,'1')
*   + capZ(a,n,w2,'2')
*   + capZ(a,n,w3,'3'))
*   - tt;

* CVapdef(a,n,w0,w1,w2,w3)$(lambda AND used(a) AND (NOT SAMEAS(a,'trn')))..
*   CVap(a,n,w0,w1,w2,w3)
*   =G=
*   capZE(a,n,w0,'0')
*   + capZE(a,n,w1,'1')
*   + capZE(a,n,w2,'2')
*   + capZE(a,n,w3,'3')
*   - aVap(a);

* smelter(t,n,w,b)..
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
*   sum(a, sum((i,k)$aik(a,i,k), ecost(k,x(a,i,k)) + ocost(k,z(a,i,k))))
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
*   sum((t,a,i,k,b)$(aik(a,i,k) AND carbemit(k)), loadblockhours(t,b)*y(t,a,i,k,n,w,b)*TonnesCO2(k))
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
