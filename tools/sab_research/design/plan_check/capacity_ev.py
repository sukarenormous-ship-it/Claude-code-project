# capacity ด้วยค่าคาดหมายต่อรอบ (ตามคำสั่งกรรมการ practitioner ข้อ 7.2) แทน edge ของเส้นทางดีที่สุด 17/2021
from decimal import Decimal as D, ROUND_HALF_UP
def r2(x): return D(x).quantize(D('0.01'), rounding=ROUND_HALF_UP)
levels=[(D('0.0005'),D(2000)),(D('0.0010'),D(3000)),(D('0.0020'),D(5000)),(D('0.0040'),D(10000)),(D('0.0080'),D(20000))]
def slip(size):
    rem=size; cost=D(0)
    for p,q in levels:
        take=min(rem,q); cost+=take*p; rem-=take
        if rem<=0: break
    return cost/size if rem<=0 else None
fee=D('0.0005')
notional=D(2021)
for name,mix in [('60/25/15',(D('0.60'),D('0.25'),D('0.15'))),('45/20/35',(D('0.45'),D('0.20'),D('0.35')))]:
    ev_after_cost1 = mix[0]*16+mix[1]*2+mix[2]*(-21)
    gross = ev_after_cost1 + 1   # คืนต้นทุน 1 ของการ์ดกติกา เพื่อได้กำไรจากราคาก่อนต้นทุน
    edge = gross/notional
    print('mix',name,'EV(after cost 1)',ev_after_cost1,'gross',gross,'edge %',r2(edge*100))
    best=None
    for size in [500,1000,2000,3000,5000,7500,10000,20000]:
        s=slip(D(size)); net=edge-2*fee-2*s; money=net*2*size
        print('   size/leg',size,'slip%',r2(s*100),'net edge%',r2(net*100),'money/round',r2(money))
