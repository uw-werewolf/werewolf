$INCLUDE 'model.gms'

q.UP(t,a,i,n,w,b)$inb(t,i,n,b) = fractionLR * load(t,a,b,i);
f.UP(t,i,j,n,w,b)$ij(i,j) = fcap(i,j);
* s.UP(i,n,t) = reservoircap(i);
x.UP(a,i,k)$aik(a,i,k) = u(a,i,k);

* allow shutdowns?
x.LO(a,i,k)$aik(a,i,k) = 0;

* allow carbon shutdowns?
z.LO(a,i,k)$aik(a,i,k) = capU(a,i,k)$(NOT carbemit(k));

* No shutdowns
*z.LO(a,i,k)$aik(a,i,k) = capU(a,i,k);

LOOP(r,
frac = r.VAL;

SOLVE capsysopt USING lp min sysobj;

build(r,a,i,k) = x.L(a,i,k);
ZZ(r,n,w,t) = sum(a, sum((i,k,b)$(aik(a,i,k) AND gen(k)), loadblockhours(t,b) * gcost(k,y.L(t,a,i,k,n,w,b)))
                  + sum((i,b)$inb(t,i,n,b), loadblockhours(t,b) * (capR * q.L(t,a,i,n,w,b) + 0 * q.L(t,a,i,n,w,b))));

ZL(r,n,w,t) = sum(a, sum((i,b)$inb(t,i,n,b), loadblockhours(t,b) * (v * q.L(t,a,i,n,w,b))));

ExpCost(r,'Invest') = (sum(a, sum((i,k)$aik(a,i,k), ecost(k,x.L(a,i,k))))) / scalefac ;
ExpCost(r,'Maintain') = sum(a, sum((i,k)$aik(a,i,k), ocost(k,z.L(a,i,k)))) / scalefac ;
ExpCost(r,'Operate') = sum(n$prob(n), sum((w,t), wprob(w,t) * prob(n) * ZZ(r,n,w,t))) / scalefac ;
ExpCost(r,'LostLoad') = sum(n$prob(n), sum((w,t), wprob(w,t) * prob(n) * ZL(r,n,w,t))) / scalefac ;

TotalCost(r) = sysobj.L / scalefac;
TotalCostM(r) = max(eps, TotalCost(r) / 1000000);
TotalCarbon(r) = max(eps, sum((t,a,i,k,n,w,b)$(aik(a,i,k) AND carbemit(k) AND prob(n)), prob(n) * wprob(w,t) * loadblockhours(t,b) * y.L(t,a,i,k,n,w,b) * TonnesCO2(k)));

* # Co2price(r) = max(eps,(co2cap.m$co2redn + renewcap.m$capredn + energycap.m$nrenergyredn)/scalefac);
lostMWhours(r,a) =  sum((t,n,w)$prob(n), prob(n) * wprob(w,t) * sum((i,b)$inb(t,i,n,b), loadblockhours(t,b) * (q.L(t,a,i,n,w,b))));

capacity(r,a,i,k) = eps + z.L(a,i,k) * (1$(NOT store(k)) + chargerate(k)$store(k));

)

EXECUTE_UNLOAD 'output_%agg%_%almostsure%.gdx';

* EXECUTE 'python graph_gen.py';
* EXECUTE 'open test.png';
