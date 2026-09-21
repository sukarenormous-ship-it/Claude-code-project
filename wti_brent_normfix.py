"""
ข้อ 2: แก้ normalization ให้ทนราคาสุดขั้ว (WTI-Brent walk-forward OOS)
ปัญหาเดิม: return รายวัน = pnl / gross_ณวันนั้น  -> ตอน WTI ร่วงเหลือ ~$16 ปี 2020
           ตัวหารหด + spread blow out -> return พองเป็น artifact
แก้: ล็อก gross notional ตอน "เปิดสถานะ" แล้วใช้ค่านั้นตลอดการถือ
     (= return ต่อทุนที่ commit จริง แบบที่เทรดจริงทำ)
เทียบ before(daily gross) vs after(entry-locked gross)
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(f): return pd.read_csv(f, parse_dates=["Date"]).set_index("Date")["Price"]
df = pd.concat([load("/tmp/wti-daily.csv").rename("WTI"),
                load("/tmp/brent-daily.csv").rename("Brent")], axis=1).dropna()
df=df.loc["2016-01-01":"2024-12-31"]; W=df["WTI"].values; B=df["Brent"].values; N=len(df)

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

def backtest(beta,entry,lo,hi,cost_bps=5,carry_annual=0.04,lock_notional=True):
    cost=cost_bps/1e4; carry=carry_annual/252.0
    sp=W-beta*B; z=zscore(sp); pos=0; beta_e=0.0; gross_e=0.0; rets=np.zeros(N)
    for t in range(max(lo,1),hi):
        if pos!=0:
            pnl=pos*((W[t]-W[t-1])-beta_e*(B[t]-B[t-1]))
            denom = gross_e if lock_notional else (abs(W[t-1])+abs(beta_e*B[t-1]))
            rets[t]=pnl/denom - carry
        if pos==0:
            if abs(z[t])>entry:
                pos=-1 if z[t]>0 else 1; beta_e=beta[t]
                gross_e=abs(W[t])+abs(beta_e*B[t]); rets[t]-=cost
        else:
            if (pos==-1 and z[t]<=0) or (pos==1 and z[t]>=0): pos=0; rets[t]-=cost
    return rets[lo:hi]

beta_k=kalman(); grid=[1.0,1.25,1.5,1.75,2.0,2.25,2.5]; TRAIN,TEST=504,126

def walkforward(lock):
    wins=[]; lo=120
    while lo+TRAIN+TEST<=N:
        tr0,tr1=lo,lo+TRAIN; te0,te1=tr1,tr1+TEST
        best=None
        for e in grid:
            s=sharpe(backtest(beta_k,e,tr0,tr1,lock_notional=lock))
            if best is None or s>best[1]: best=(e,s)
        r=backtest(beta_k,best[0],te0,te1,lock_notional=lock)
        wins.append((df.index[te0].date(), np.prod(1+r)-1, r))
        lo+=TEST
    return wins

old=walkforward(False); new=walkforward(True)
print(f"{'OOS window':<14}{'OLD ret(daily gross)':>22}{'NEW ret(locked)':>18}")
print("-"*54)
for (d,ro,_),(_,rn,_) in zip(old,new):
    flag = "  <-- artifact" if abs(ro)>1.0 else ""
    print(f"{str(d):<14}{ro*100:>20.1f}%{rn*100:>16.1f}%{flag}")

ro_all=np.concatenate([w[2] for w in old]); rn_all=np.concatenate([w[2] for w in new])
print(f"\nStitched OOS:")
print(f"  OLD (daily gross) : Sharpe {sharpe(ro_all):.2f}  total ret {(np.prod(1+ro_all)-1)*100:.0f}%")
print(f"  NEW (locked)      : Sharpe {sharpe(rn_all):.2f}  total ret {(np.prod(1+rn_all)-1)*100:.0f}%")

# ตัดหน้าต่าง COVID 2020 (เริ่ม 2020-01-10) ออก -> ภาพ regime ปกติ
rn_ex = np.concatenate([w[2] for w in new if str(w[0])!="2020-01-10"])
print(f"\n  NEW ตัดหน้าต่าง COVID 2020 ออก: Sharpe {sharpe(rn_ex):.2f}  total ret {(np.prod(1+rn_ex)-1)*100:.0f}%  (~{(np.prod(1+rn_ex)**(252/len(rn_ex))-1)*100:.1f}%/ปี)")

fig,ax=plt.subplots(1,2,figsize=(13,5))
ax[0].plot(np.cumprod(1+ro_all),'C3'); ax[0].set_title(f"OLD: daily gross (Sharpe {sharpe(ro_all):.2f})\n2020 artifact dominates")
ax[0].set_yscale('log'); ax[0].set_ylabel('equity (log)'); ax[0].grid(alpha=.3)
ax[1].plot(np.cumprod(1+rn_all),'C0'); ax[1].set_title(f"NEW: entry-locked notional (Sharpe {sharpe(rn_all):.2f})\nrealistic compounding")
ax[1].set_ylabel('equity'); ax[1].grid(alpha=.3)
for a in ax: a.set_xlabel('OOS trading days'); a.axhline(1,color='gray',ls=':')
plt.tight_layout(); plt.savefig("/home/user/Claude-code-project/wti_brent_normfix.png",dpi=110)
print("\nบันทึกกราฟ: wti_brent_normfix.png")
