# แปลง z ของคู่อันดับ 1 (seed 11) เป็นเงิน — สำเนาตรรกะ selection_bias ของ v09_ch06_ch07_demo.py
import math, random
def rw(rng,n,sd):
    x,o=0.0,[]
    for _ in range(n): x+=rng.gauss(0,sd); o.append(x)
    return o
def pair_h(rng,n):
    c=rw(rng,n,0.03); a=[ci+ui for ci,ui in zip(c,rw(rng,n,0.01))]; b=[ci+ui for ci,ui in zip(c,rw(rng,n,0.01))]; return a,b
def zstats(s,nf):
    f=s[:nf]; m=sum(f)/nf; sd=math.sqrt(sum((x-m)**2 for x in f)/(nf-1)); z=[(x-m)/sd for x in s]
    cross=sum(1 for u,v in zip(z[:nf-1],z[1:nf]) if (u>0)!=(v>0)); return z,cross,m,sd
rng=random.Random(11); n,nf=500,250; rows=[]
for i in range(200):
    a,b=pair_h(rng,n); s=[x-y for x,y in zip(a,b)]; z,cross,m,sd=zstats(s,nf); rows.append((cross,z,m,sd,s,a,b))
rows.sort(key=lambda r:-r[0]); cross,z,m,sd,s,a,b=rows[0]
test=z[nf:]; imin=min(range(len(test)),key=lambda i:test[i])
print('crossings',cross,'sd(log spread)',round(sd,4),'min z',round(test[imin],2),'at test day',imin+1,'log-spread move from mean',round(test[imin]*sd,4))
# first test-period entry by rule |z|>=2, hold until |z|<=0.5 (no time limit) — report P&L per 100 per leg (log approx)
pos=0
for i in range(nf,n):
    if pos==0 and abs(z[i])>=2:
        pos=-1 if z[i]>0 else 1; ei=i; print('entry day',i-nf+1,'z',round(z[i],2)); break
if pos:
    worst=min(pos*(s[j]-s[ei]) for j in range(ei,n)); end=pos*(s[n-1]-s[ei])
    ex=next((j for j in range(ei+1,n) if abs(z[j])<=0.5),None)
    print('worst P&L per 100/leg',round(100*worst,2),'end-of-test',round(100*end,2),'exit day',None if ex is None else ex-nf+1)

print('--- trades: entry |z|>=2, exit |z|<=0.5, no stop/time limit, 100 per leg (log approx)')
pos=0; i=nf
while i<n:
    if pos==0 and abs(z[i])>=2:
        pos=-1 if z[i]>0 else 1; ei=i
    elif pos!=0 and abs(z[i])<=0.5:
        print('trade days',ei-nf+1,'->',i-nf+1,'z',round(z[ei],2),'->',round(z[i],2),'P&L',round(100*pos*(s[i]-s[ei]),2)); pos=0
    i+=1
if pos: print('open at end from day',ei-nf+1,'z',round(z[ei],2),'-> last z',round(z[n-1],2),'P&L',round(100*pos*(s[n-1]-s[ei]),2),'worst',round(min(100*pos*(s[j]-s[ei]) for j in range(ei,n)),2))

print('--- z in test days 1..80 (every 5)')
print([ (d, round(z[nf+d-1],2)) for d in range(1,81,5)])
print('test-day of first |z|>=2:', next(d for d in range(1,251) if abs(z[nf+d-1])>=2))
print('z days 190-230 every 5', [ (d, round(z[nf+d-1],2)) for d in range(190,251,5)])
