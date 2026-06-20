"""
WTI-Brent pairs trading ด้วย Kalman filter + train/test split (70/30 OOS)
หลักการกัน lookahead:
 - static OLS beta ประมาณจาก train เท่านั้น
 - entry threshold เลือกจาก train (จูน Sharpe) แล้วล็อกไปใช้กับ OOS
 - Kalman เป็น online/causal อยู่แล้ว (ใช้แค่ข้อมูลอดีต)
 - รายงานผล train (IS) กับ test (OOS) แยกกัน — ตัวที่นับคือ OOS
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(f): return pd.read_csv(f, parse_dates=["Date"]).set_index("Date")["Price"]
df = pd.concat([load("/tmp/wti-daily.csv").rename("WTI"),
                load("/tmp/brent-daily.csv").rename("Brent")], axis=1).dropna()
df = df.loc["2016-01-01":"2024-12-31"]
W = df["WTI"].values; B = df["Brent"].values; N = len(df)
BURN = 120
split = int(0.70*N)
print(f"ทั้งหมด {N} วัน | train {BURN}..{split} ({df.index[split].date()} แบ่ง) | OOS {split}..{N}")

def kalman(q=1e-4, r=1.0):
    x=np.array([1.0,0.0]); P=np.eye(2); Q=np.eye(2)*q; R=r; beta=np.zeros(N)
    for t in range(N):
        H=np.array([B[t],1.0]); P=P+Q
        e=W[t]-H@x; S=H@P@H+R; K=(P@H)/S
        x=x+K*e; P=P-np.outer(K,H)@P; beta[t]=x[0]
    return beta

def zscore(spread, win=60):
    s=pd.Series(spread); mu=s.rolling(win).mean().values; sd=s.rolling(win).std().values
    return np.where(sd>0,(spread-mu)/sd,0.0)

def backtest(beta, entry, lo, hi, cost_bps=5.0):
    """รัน backtest เฉพาะช่วง [lo,hi); คืน rets, #trades"""
    cost=cost_bps/1e4; spread=W-beta*B; z=zscore(spread)
    pos=0; beta_e=0.0; rets=np.zeros(N); trades=0
    for t in range(max(lo,1),hi):
        if pos!=0:
            pnl=pos*((W[t]-W[t-1])-beta_e*(B[t]-B[t-1]))
            rets[t]=pnl/(abs(W[t-1])+abs(beta_e*B[t-1]))
        if pos==0:
            if z[t]>entry: pos=-1;beta_e=beta[t];trades+=1;rets[t]-=cost
            elif z[t]<-entry: pos=1;beta_e=beta[t];trades+=1;rets[t]-=cost
        else:
            if (pos==-1 and z[t]<=0) or (pos==1 and z[t]>=0): pos=0;trades+=1;rets[t]-=cost
    return rets[lo:hi], trades

def stats(rets, trades):
    n=len(rets); eq=np.cumprod(1+rets)
    ann=eq[-1]**(252/n)-1 if eq[-1]>0 else float('nan')
    sr=np.mean(rets)/np.std(rets)*np.sqrt(252) if np.std(rets)>0 else 0
    mdd=np.min(eq/np.maximum.accumulate(eq)-1)
    return ann,sr,mdd,trades

# beta: Kalman (online) และ static OLS จาก train เท่านั้น
beta_k = kalman()
beta_ols = np.polyfit(B[BURN:split], W[BURN:split], 1)[0]
beta_s = np.full(N, beta_ols)
print(f"static OLS beta (จาก train) = {beta_ols:.3f}")

# เลือก entry ที่ดีสุดบน train (จูน Sharpe) แยกกันแต่ละกลยุทธ์
grid=[1.0,1.25,1.5,1.75,2.0,2.25,2.5]
def pick_entry(beta):
    best=None
    for e in grid:
        r,_=backtest(beta,e,BURN,split); _,sr,_,_=stats(r,0)
        if best is None or sr>best[1]: best=(e,sr)
    return best[0]
e_k=pick_entry(beta_k); e_s=pick_entry(beta_s)
print(f"entry ที่เลือกจาก train: Kalman={e_k}, Static={e_s}")

print("\n=== ผล TRAIN (in-sample) ===")
print(f"{'':<22}{'ann':>8}{'Sharpe':>8}{'MDD':>8}{'trades':>8}")
rk_is,tk=backtest(beta_k,e_k,BURN,split); a,s,m,_=stats(rk_is,tk); print(f"{'Kalman':<22}{a*100:7.1f}%{s:8.2f}{m*100:7.1f}%{tk:8d}")
rs_is,ts=backtest(beta_s,e_s,BURN,split); a,s,m,_=stats(rs_is,ts); print(f"{'Static OLS':<22}{a*100:7.1f}%{s:8.2f}{m*100:7.1f}%{ts:8d}")

print("\n=== ผล OOS (out-of-sample) <-- ตัวจริง ===")
print(f"{'':<22}{'ann':>8}{'Sharpe':>8}{'MDD':>8}{'trades':>8}")
rk_oos,tk=backtest(beta_k,e_k,split,N); ak,sk,mk,_=stats(rk_oos,tk); print(f"{'Kalman':<22}{ak*100:7.1f}%{sk:8.2f}{mk*100:7.1f}%{tk:8d}")
rs_oos,ts=backtest(beta_s,e_s,split,N); a2,s2,m2,_=stats(rs_oos,ts); print(f"{'Static OLS':<22}{a2*100:7.1f}%{s2:8.2f}{m2*100:7.1f}%{ts:8d}")

# พล็อต equity OOS
fig,ax=plt.subplots(figsize=(11,5))
ax.plot(df.index[split:], np.cumprod(1+rk_oos), 'C0', label=f"Kalman OOS (Sharpe {sk:.2f})")
ax.plot(df.index[split:], np.cumprod(1+rs_oos), 'C3', label=f"Static OLS OOS (Sharpe {s2:.2f})")
ax.axhline(1,color='gray',ls=':'); ax.set_title("Out-of-sample equity curve (start=1.0)")
ax.legend(); ax.grid(alpha=.3); plt.tight_layout()
plt.savefig("/home/user/Claude-code-project/wti_brent_oos.png", dpi=110)
print("\nบันทึกกราฟ: wti_brent_oos.png")
