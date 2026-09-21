"""
Walk-forward analysis: WTI-Brent pairs trading (Kalman vs Static OLS)
- เลื่อนหน้าต่าง: train ~2 ปี (504 วัน) -> test ~6 เดือน (126 วัน) -> ก้าวต่อ 126 วัน
- แต่ละหน้าต่าง: ประมาณ beta(static) + เลือก entry "จาก train เท่านั้น" แล้ววัดบน test (OOS)
- รวบการกระจายตัวของ Sharpe ทุกหน้าต่าง -> ดูว่ากลยุทธ์ robust หรือพึ่งโชค regime
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(f): return pd.read_csv(f, parse_dates=["Date"]).set_index("Date")["Price"]
df = pd.concat([load("/tmp/wti-daily.csv").rename("WTI"),
                load("/tmp/brent-daily.csv").rename("Brent")], axis=1).dropna()
df = df.loc["2016-01-01":"2024-12-31"]
W = df["WTI"].values; B = df["Brent"].values; N = len(df)

def kalman(q=1e-4, r=1.0):
    x=np.array([1.0,0.0]); P=np.eye(2); Q=np.eye(2)*q; R=r; beta=np.zeros(N)
    for t in range(N):
        H=np.array([B[t],1.0]); P=P+Q; e=W[t]-H@x; S=H@P@H+R; K=(P@H)/S
        x=x+K*e; P=P-np.outer(K,H)@P; beta[t]=x[0]
    return beta
def zscore(spread, win=60):
    s=pd.Series(spread); mu=s.rolling(win).mean().values; sd=s.rolling(win).std().values
    return np.where(sd>0,(spread-mu)/sd,0.0)
def backtest(beta, entry, lo, hi, cost_bps=5.0):
    cost=cost_bps/1e4; spread=W-beta*B; z=zscore(spread)
    pos=0; beta_e=0.0; rets=np.zeros(N); trades=0
    for t in range(max(lo,1),hi):
        if pos!=0:
            pnl=pos*((W[t]-W[t-1])-beta_e*(B[t]-B[t-1])); rets[t]=pnl/(abs(W[t-1])+abs(beta_e*B[t-1]))
        if pos==0:
            if z[t]>entry: pos=-1;beta_e=beta[t];trades+=1;rets[t]-=cost
            elif z[t]<-entry: pos=1;beta_e=beta[t];trades+=1;rets[t]-=cost
        else:
            if (pos==-1 and z[t]<=0) or (pos==1 and z[t]>=0): pos=0;trades+=1;rets[t]-=cost
    return rets[lo:hi], trades
def sharpe(r): return np.mean(r)/np.std(r)*np.sqrt(252) if np.std(r)>0 else 0.0

beta_k = kalman()
grid=[1.0,1.25,1.5,1.75,2.0,2.25,2.5]
TRAIN, TEST = 504, 126

windows=[]
lo=120
while lo+TRAIN+TEST <= N:
    tr0,tr1 = lo, lo+TRAIN
    te0,te1 = tr1, tr1+TEST
    # static beta จาก train ของหน้าต่างนี้
    beta_ols=np.polyfit(B[tr0:tr1],W[tr0:tr1],1)[0]; beta_s=np.full(N,beta_ols)
    # เลือก entry จาก train แต่ละกลยุทธ์
    def pick(beta):
        best=None
        for e in grid:
            r,_=backtest(beta,e,tr0,tr1); s=sharpe(r)
            if best is None or s>best[1]: best=(e,s)
        return best[0]
    ek,es=pick(beta_k),pick(beta_s)
    rk,tk=backtest(beta_k,ek,te0,te1); rs,ts=backtest(beta_s,es,te0,te1)
    windows.append(dict(start=df.index[te0].date(), end=df.index[te1-1].date(),
                        sk=sharpe(rk), ss=sharpe(rs),
                        rk=np.prod(1+rk)-1, rs=np.prod(1+rs)-1, tk=tk, ts=ts,
                        rk_arr=rk, rs_arr=rs))
    lo += TEST

print(f"จำนวนหน้าต่าง OOS: {len(windows)} (train {TRAIN}d / test {TEST}d)\n")
print(f"{'OOS period':<26}{'Kalman SR':>11}{'Static SR':>11}{'K ret':>8}{'S ret':>8}{'K tr':>6}")
print("-"*72)
for w in windows:
    print(f"{str(w['start'])+'..'+str(w['end']):<26}{w['sk']:>11.2f}{w['ss']:>11.2f}{w['rk']*100:>7.1f}%{w['rs']*100:>7.1f}%{w['tk']:>6}")

sk=np.array([w['sk'] for w in windows]); ss=np.array([w['ss'] for w in windows])
print("\n=== สรุปการกระจายตัวของ OOS Sharpe ===")
print(f"{'':<10}{'mean':>8}{'median':>8}{'std':>8}{'min':>8}{'max':>8}{'% บวก':>8}")
print(f"{'Kalman':<10}{sk.mean():>8.2f}{np.median(sk):>8.2f}{sk.std():>8.2f}{sk.min():>8.2f}{sk.max():>8.2f}{(sk>0).mean()*100:>7.0f}%")
print(f"{'Static':<10}{ss.mean():>8.2f}{np.median(ss):>8.2f}{ss.std():>8.2f}{ss.min():>8.2f}{ss.max():>8.2f}{(ss>0).mean()*100:>7.0f}%")

# stitched OOS equity (ต่อ test ทุกหน้าต่างเรียงกัน)
rk_all=np.concatenate([w['rk_arr'] for w in windows]); rs_all=np.concatenate([w['rs_arr'] for w in windows])
print(f"\nStitched OOS รวม: Kalman Sharpe {sharpe(rk_all):.2f} ret {(np.prod(1+rk_all)-1)*100:.1f}% | Static Sharpe {sharpe(rs_all):.2f} ret {(np.prod(1+rs_all)-1)*100:.1f}%")

fig,ax=plt.subplots(2,1,figsize=(12,9))
x=np.arange(len(windows)); labels=[str(w['start']) for w in windows]
ax[0].bar(x-0.2,sk,0.4,label='Kalman',color='C0'); ax[0].bar(x+0.2,ss,0.4,label='Static OLS',color='C3')
ax[0].axhline(0,color='k',lw=.8); ax[0].set_xticks(x); ax[0].set_xticklabels(labels,rotation=45,ha='right',fontsize=8)
ax[0].set_title("OOS Sharpe per walk-forward window"); ax[0].set_ylabel("annualized Sharpe"); ax[0].legend(); ax[0].grid(alpha=.3,axis='y')
ax[1].plot(np.cumprod(1+rk_all),'C0',label=f'Kalman stitched OOS (SR {sharpe(rk_all):.2f})')
ax[1].plot(np.cumprod(1+rs_all),'C3',label=f'Static stitched OOS (SR {sharpe(rs_all):.2f})')
ax[1].axhline(1,color='gray',ls=':'); ax[1].set_title("Stitched out-of-sample equity (all windows)")
ax[1].set_xlabel("OOS trading days"); ax[1].legend(); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig("/home/user/Claude-code-project/wti_brent_walkforward.png",dpi=110)
print("\nบันทึกกราฟ: wti_brent_walkforward.png")
