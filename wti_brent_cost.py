"""
ข้อ 1: Cost sensitivity + cost of carry (WTI-Brent pairs, walk-forward OOS)
ต้นทุน 2 แบบ:
 - transaction cost: คิดต่อครั้งที่เปิด/ปิด (bps ของ gross notional, ครอบทั้ง 2 ขา)
 - cost of carry   : ต้นทุนถือครองต่อวันที่มีสถานะเปิด (financing + ค่ายืม short)
                     = carry_annual/252 ของ gross ต่อวัน
วัดบน stitched OOS ของ walk-forward (train 2y / test 6m) แล้วหา break-even
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(f): return pd.read_csv(f, parse_dates=["Date"]).set_index("Date")["Price"]
df = pd.concat([load("/tmp/wti-daily.csv").rename("WTI"),
                load("/tmp/brent-daily.csv").rename("Brent")], axis=1).dropna()
df = df.loc["2016-01-01":"2024-12-31"]
W=df["WTI"].values; B=df["Brent"].values; N=len(df)

def kalman(q=1e-4,r=1.0):
    x=np.array([1.0,0.0]);P=np.eye(2);Q=np.eye(2)*q;R=r;beta=np.zeros(N)
    for t in range(N):
        H=np.array([B[t],1.0]);P=P+Q;e=W[t]-H@x;S=H@P@H+R;K=(P@H)/S
        x=x+K*e;P=P-np.outer(K,H)@P;beta[t]=x[0]
    return beta
def zscore(sp,win=60):
    s=pd.Series(sp);mu=s.rolling(win).mean().values;sd=s.rolling(win).std().values
    return np.where(sd>0,(sp-mu)/sd,0.0)
def sharpe(r): return np.mean(r)/np.std(r)*np.sqrt(252) if np.std(r)>0 else 0.0

def backtest(beta,entry,lo,hi,cost_bps,carry_annual):
    cost=cost_bps/1e4; carry=carry_annual/252.0
    sp=W-beta*B; z=zscore(sp); pos=0; beta_e=0.0; rets=np.zeros(N)
    for t in range(max(lo,1),hi):
        if pos!=0:
            pnl=pos*((W[t]-W[t-1])-beta_e*(B[t]-B[t-1]))
            rets[t]=pnl/(abs(W[t-1])+abs(beta_e*B[t-1]))
            rets[t]-=carry                      # cost of carry รายวันที่ถือ
        if pos==0:
            if z[t]>entry: pos=-1;beta_e=beta[t];rets[t]-=cost
            elif z[t]<-entry: pos=1;beta_e=beta[t];rets[t]-=cost
        else:
            if (pos==-1 and z[t]<=0) or (pos==1 and z[t]>=0): pos=0;rets[t]-=cost
    return rets[lo:hi]

beta_k=kalman(); grid=[1.0,1.25,1.5,1.75,2.0,2.25,2.5]; TRAIN,TEST=504,126

def walkforward(beta_fn, cost_bps, carry_annual):
    """คืน stitched OOS returns. beta_fn(lo,hi)->beta array (เต็มความยาว N)"""
    out=[]; lo=120
    while lo+TRAIN+TEST<=N:
        tr0,tr1=lo,lo+TRAIN; te0,te1=tr1,tr1+TEST
        beta=beta_fn(tr0,tr1)
        # เลือก entry จาก train (ใช้ต้นทุนชุดเดียวกัน)
        best=None
        for e in grid:
            s=sharpe(backtest(beta,e,tr0,tr1,cost_bps,carry_annual))
            if best is None or s>best[1]: best=(e,s)
        out.append(backtest(beta,best[0],te0,te1,cost_bps,carry_annual))
        lo+=TEST
    return np.concatenate(out)

beta_kal=lambda lo,hi: beta_k
def beta_ols(lo,hi): return np.full(N, np.polyfit(B[lo:hi],W[lo:hi],1)[0])

# ---- กวาด transaction cost (carry คงที่ 4%/ปี = financing สมจริง) ----
CARRY=0.04
costs=[0,2,5,10,15,20,30,40,50]
print(f"cost of carry คงที่ = {CARRY*100:.0f}%/ปี | กวาด transaction cost (bps/ครั้ง, ครอบ 2 ขา)\n")
print(f"{'tx cost(bps)':<13}{'Kalman SR':>11}{'Kalman ret':>12}{'Static SR':>11}{'Static ret':>12}")
print("-"*60)
SRk=[];SRs=[]
for c in costs:
    rk=walkforward(beta_kal,c,CARRY); rs=walkforward(beta_ols,c,CARRY)
    sk=sharpe(rk); ss=sharpe(rs); SRk.append(sk); SRs.append(ss)
    ak=(np.prod(1+rk)-1)*100; as_=(np.prod(1+rs)-1)*100
    print(f"{c:<13}{sk:>11.2f}{ak:>11.0f}%{ss:>11.2f}{as_:>11.0f}%")

# ---- กวาด cost of carry (tx cost คงที่ 5 bps) ----
print(f"\ntransaction cost คงที่ = 5 bps | กวาด cost of carry (%/ปี)\n")
print(f"{'carry(%/ปี)':<13}{'Kalman SR':>11}{'Static SR':>11}")
print("-"*36)
carries=[0,0.02,0.04,0.06,0.08,0.10,0.15,0.20]
SRk2=[];SRs2=[]
for cy in carries:
    sk=sharpe(walkforward(beta_kal,5,cy)); ss=sharpe(walkforward(beta_ols,5,cy))
    SRk2.append(sk);SRs2.append(ss)
    print(f"{cy*100:<13.0f}{sk:>11.2f}{ss:>11.2f}")

fig,ax=plt.subplots(1,2,figsize=(13,5))
ax[0].plot(costs,SRk,'o-',label='Kalman'); ax[0].plot(costs,SRs,'s-',label='Static',color='C3')
ax[0].axhline(0,color='k',lw=.8); ax[0].set_xlabel('transaction cost (bps/trade, both legs)')
ax[0].set_ylabel('stitched OOS Sharpe'); ax[0].set_title(f'Sensitivity to transaction cost (carry={CARRY*100:.0f}%/yr)')
ax[0].legend(); ax[0].grid(alpha=.3)
ax[1].plot([c*100 for c in carries],SRk2,'o-',label='Kalman'); ax[1].plot([c*100 for c in carries],SRs2,'s-',label='Static',color='C3')
ax[1].axhline(0,color='k',lw=.8); ax[1].set_xlabel('cost of carry (%/year)')
ax[1].set_ylabel('stitched OOS Sharpe'); ax[1].set_title('Sensitivity to cost of carry (tx=5bps)')
ax[1].legend(); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig("/home/user/Claude-code-project/wti_brent_cost.png",dpi=110)
print("\nบันทึกกราฟ: wti_brent_cost.png")
