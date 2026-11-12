# ตัวเลขตัวอย่างสำหรับข้อเสนอแนว C (nature-first) — คิดซ้ำจากสมมติฐานของต้นฉบับ v0.9
from decimal import Decimal as D, ROUND_HALF_UP
def r2(x): return D(x).quantize(D('0.01'), rounding=ROUND_HALF_UP)
S0, F0, days, cap = D(100000), D(103000), D(90), D(125000)
basis = F0-S0
def ladder(fee, F=F0, capital=cap, S_exp=D(105000), hurdle=D('0.04'), d=days):
    b = F-S0
    simple = b/S0*D(365)/d*100
    on_cap = b/capital*D(365)/d*100
    fees = fee*(S0+F+S_exp)
    net = b-fees
    net_y = net/capital*D(365)/d*100
    opp = capital*hurdle*d/D(365)
    exc = net-opp
    exc_y = exc/capital*D(365)/d*100
    return dict(basis=b, simple=r2(simple), on_cap=r2(on_cap), fees=r2(fees), net=r2(net), net_y=r2(net_y), opp=r2(opp), excess=r2(exc), excess_y=r2(exc_y))
print('ladder 0.05%', ladder(D('0.0005')))
print('ladder 0.10%', ladder(D('0.001')))
print('ladder 0.02%', ladder(D('0.0002')))
print('hurdle 9%', ladder(D('0.0005'), hurdle=D('0.09')))
for b in [3000,2500,2000,1500,1000,500]:
    print('crowding basis',b, ladder(D('0.0005'), F=S0+D(b)))
# safety vs return
for c in [115000,120000,125000,150000]:
    c=D(c); free=c-S0-D('0.10')*F0
    buf=free/D('1.1'); pct=buf/F0*100
    L=ladder(D('0.0005'),capital=c)
    print('capital',c,'free',free,'buffer_move',r2(buf),'pct',r2(pct),'net_y',L['net_y'],'excess_y',L['excess_y'])
# blowup rounds
net=D(100000+3000)-D(100000)  # placeholder
net=ladder(D('0.0005'))['net']
print('rounds to repay 125000:', r2(cap/net), 'years', r2(cap/net*days/365))
print('rounds to repay 25000 (เฉพาะเงินบน exchange ถ้า spot อยู่ที่อื่น):', r2(D(25000)/net), 'years', r2(D(25000)/net*days/365))
# funding paths with unified fee 0.05% x 4 trades of 100,000 = 200
fee=D('0.0005')*4*S0
paths={}
paths['A']=[D(10)]*90
paths['B']=[D(30)]*30+[D(5)]*60
paths['C']=[D(10)]*45+[D(-10)]*45
d=[]
while len(d)<90:
    d+= [D(10)]*5 + [D(-5)]*3
paths['D']=d[:90]
for k,p in paths.items():
    tot=sum(p); net=tot-fee
    # rule: exit after 3 consecutive negative
    cum=D(0); neg=0; exit_cum=None
    for i,x in enumerate(p):
        cum+=x
        neg = neg+1 if x<0 else 0
        if neg==3 and exit_cum is None: exit_cum=cum; exit_i=i+1
    rule_net = (exit_cum-fee) if exit_cum is not None else net
    print('funding',k,'total',tot,'net',net,'pct_y',r2(net/cap*D(365)/D(30)*100),'rule_net',rule_net, 'exit_at', exit_cum)
print('rounds to cover fee 200 at 10/round:', fee/10, '; at 0.02% (80):', D('0.0002')*4*S0/10)
# funding crowding: rate falls to 0.003%
for rate in ['0.0001','0.00005','0.00003']:
    tot=D(rate)*S0*90; net=tot-fee
    print('funding rate',rate,'per30d',tot,'net',net,'pct_y',r2(net/cap*D(365)/D(30)*100))
# 08.03 breakeven
print('breakeven +16/-21:', r2(D(21)/D(37)*100))
for mix in [(D('0.60'),D('0.25'),D('0.15')),(D('0.45'),D('0.20'),D('0.35'))]:
    ev=mix[0]*16+mix[1]*2+mix[2]*(-21)
    print('mix',mix,'EV',ev)
# 05.08
print('05.08 EV', D('0.65')*1-D('0.35')*3-D('0.1'), 'breakeven', r2(D('3.1')/D(4)*100))
# tail 01.04
for n in [10,20,50,100,250]:
    print('no-loss prob',n, r2(D('0.99')**n*100))
# 50 pairs
for n in [1,10,20,50,100,200]:
    print('at least one fake pass at 5%', n, r2((1-D('0.95')**n)*100))
# capacity: hypothetical book
levels=[(D('0.0005'),D(2000)),(D('0.0010'),D(3000)),(D('0.0020'),D(5000)),(D('0.0040'),D(10000)),(D('0.0080'),D(20000))]
def slip(size):
    rem=size; cost=D(0)
    for p,q in levels:
        take=min(rem,q); cost+=take*p; rem-=take
        if rem<=0: break
    return cost/size if rem<=0 else None
gross_edge=D(17)/D(2021)  # 08.03 กำไรจากราคา 17 ต่อมูลค่าสองขา 2,021
fee_rate=D('0.0005')
for size in [1000,2000,5000,10000,20000,30000,40000]:
    s=slip(D(size))
    net_edge = gross_edge - 2*fee_rate - 2*s  # เข้า+ออก ต่อขา (เฉลี่ยสองขาเท่ากัน)
    print('size per leg',size,'avg slip %',r2(s*100) if s else None,'net edge % of notional', r2(net_edge*100), 'net money per round (2 legs)', r2(net_edge*2*size))
print('gross edge %', r2(gross_edge*100))
# มิน scale
print('Min: net per 90d', ladder(D('0.0005'))['net']/100, 'excess', ladder(D('0.0005'))['excess']/100, 'THB @34.5', r2(ladder(D('0.0005'))['net']/100*D('34.5')))
