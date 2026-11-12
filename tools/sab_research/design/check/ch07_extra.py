# ตรวจตัวเลขเสริมของบท 7 ด้วยตรรกะเดียวกับ v09_ch06_ch07_demo.py (seed 7) — สำเนาตรรกะ ไม่ import ไฟล์ต้นฉบับ
import math, random
def rw(rng,n,sd):
    x,o=0.0,[]
    for _ in range(n): x+=rng.gauss(0,sd); o.append(x)
    return o
def ar1(rng,n,phi,sd):
    x,o=0.0,[]
    for _ in range(n): x=phi*x+rng.gauss(0,sd); o.append(x)
    return o
def corr(a,b):
    ma,mb=sum(a)/len(a),sum(b)/len(b)
    cov=sum((x-ma)*(y-mb) for x,y in zip(a,b)); va=sum((x-ma)**2 for x in a); vb=sum((y-mb)**2 for y in b)
    return cov/math.sqrt(va*vb)
def diff(x): return [b-a for a,b in zip(x,x[1:])]
def ar_fit(s):
    x,y=s[:-1],s[1:]; mx,my=sum(x)/len(x),sum(y)/len(y)
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/sum((a-mx)**2 for a in x)
def pair_h(rng,n):
    c=rw(rng,n,0.03); a=[ci+ui for ci,ui in zip(c,rw(rng,n,0.01))]; b=[ci+ui for ci,ui in zip(c,rw(rng,n,0.01))]; return a,b
def pair_c(rng,n):
    c=rw(rng,n,0.03); a=[ci+ui for ci,ui in zip(c,rw(rng,n,0.01))]; e=ar1(rng,n,0.9,0.03); b=[ai+ei for ai,ei in zip(a,e)]; return a,b
def band(s,lo,hi):
    seg=s[lo:hi]; m=sum(seg)/len(seg); sd=math.sqrt(sum((x-m)**2 for x in seg)/(len(seg)-1)); return m,sd
rng=random.Random(7); n,nf=500,250
for name,maker in (("H",pair_h),("C",pair_c)):
    same=[];inb=[];leak=[];corrs=[];p85=[]
    for _ in range(200):
        a,b=maker(rng,n); s=[x-y for x,y in zip(a,b)]
        ra,rb=diff(a),diff(b); corrs.append(corr(ra,rb))
        same.append(sum(1 for u,v in zip(ra,rb) if (u>0)==(v>0))/len(ra))
        m,sd=band(s,0,nf); t=[abs((x-m)/sd)<=2 for x in s[nf:]]; inb.append(sum(t)/len(t))
        m2,sd2=band(s,0,n); t2=[abs((x-m2)/sd2)<=2 for x in s[nf:]]; leak.append(sum(t2)/len(t2))
    print(name,'corr',round(sum(corrs)/200,3),'same-direction',round(sum(same)/200,3),'inband',round(sum(inb)/200,3),'leak-band inband',round(sum(leak)/200,3),
          'share pass 85%',round(sum(1 for v in inb if v>=0.85)/200,3))
