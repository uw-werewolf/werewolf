*-------------------
* Year 2020 Model Constraints
*-------------------
* scale back load duration curve to current day (2020)
ldc(t,wn,sn,hn,a,b,i) = ldc_2020(t,wn,sn,hn,a,b,i);

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


PARAMETER mode;

* $GDXIN "%solve_mode%"
* $LOAD mode
* $GDXIN

* SOLVE Year 2020 Model
frac = 0;
co2redn = 0;
capredn = 0;
nrenergyredn = 0;
carbonleakage = 1;

* co2redn = mode("2020_baseline","co2redn");
* capredn = mode("2020_baseline","capredn");
* nrenergyredn = mode("2020_baseline","nrenergyredn");
* carbonleakage = mode("2020_baseline","carbonleakage");

SOLVE capsysopt USING lp min sysobj;

* calculate year 2020 carbon emissions and non-renewable capacity
maxCarbon = sum((scn(t,wn,sn,hn),a,i,k,b)$(aik(a,i,k) AND carbemit(i,k) AND cntlreg(i)), wprob(t,wn,sn,hn) * loadblockhours(t,wn,sn,hn,b) * y.L(t,wn,sn,hn,a,i,k,b) * MMTonnesCO2(i,k));

maxNR = sum((a,i,k)$(aik(a,i,k) AND cntlreg(i) AND (NOT renew(k))), z.L(a,i,k));

DISPLAY maxCarbon;
DISPLAY maxNR;


z_cntlreg(k,'2020') = eps + sum((a,i)$cntlreg(i), z.L(a,i,k));
x_cntlreg(k,'2020') = eps + sum((a,i)$cntlreg(i), x.L(a,i,k));
y_cntlreg(k,'2020') = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * sum((a,i)$cntlreg(i), sum(b, y.L(t,wn,sn,hn,a,i,k,b) * loadblockhours_compact(t,b))));
*-------------------



*-------------------
* Year %proj_year% (baseline) Model Constraints
*-------------------
* scale to %proj_year%
ldc(t,wn,sn,hn,a,b,i) = ldc_total(t,wn,sn,hn,a,b,i);

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
co2redn = 1;
capredn = 0;
nrenergyredn = 0;
carbonleakage = 1;

* co2redn = mode("proj_year_baseline","co2redn");
* capredn = mode("proj_year_baseline","capredn");
* nrenergyredn = mode("proj_year_baseline","nrenergyredn");
* carbonleakage = mode("proj_year_baseline","carbonleakage");

SOLVE capsysopt USING lp min sysobj;

* calculate imports into cntlreg
$IFTHEN.imports almostsure == 1
baseline_imports(scn(t,wn,sn,hn),not_cntlreg(i),b) = sum(ij(i,j)$cntlreg(j), wprob(t,wn,sn,hn) * f.L(t,wn,sn,hn,i,j,b));
$ELSE.imports
baseline_imports(not_cntlreg(i),b) = sum(ij(i,j)$cntlreg(j), sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * f.L(t,wn,sn,hn,i,j,b)));
$ENDIF.imports

display baseline_imports;

z_cntlreg(k,'%proj_year%') = eps + sum((a,i)$cntlreg(i), z.L(a,i,k));
x_cntlreg(k,'%proj_year%') = eps + sum((a,i)$cntlreg(i), x.L(a,i,k));
y_cntlreg(k,'%proj_year%') = eps + sum(scn(t,wn,sn,hn), wprob(t,wn,sn,hn) * sum((a,i)$cntlreg(i), sum(b, y.L(t,wn,sn,hn,a,i,k,b) * loadblockhours_compact(t,b))));
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


SET r "scenario iteration" / 1*10 /;
PARAMETER frac_r(r) /
1 0,
2 0.1,
3 0.2,
4 0.3,
5 0.4,
6 0.5,
7 0.6,
8 0.7,
9 0.8,
10 0.9 /;


* $GDXIN "%frac_gdx%"
* $LOAD r, frac_r
* $GDXIN

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




LOOP(r,
frac = frac_r(r);
co2redn = 1;
capredn = 0;
nrenergyredn = 0;
carbonleakage = 0;

* co2redn = mode("proj_year_scn","co2redn");
* capredn = mode("proj_year_scn","capredn");
* nrenergyredn = mode("proj_year_scn","nrenergyredn");
* carbonleakage = mode("proj_year_scn","carbonleakage");

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
