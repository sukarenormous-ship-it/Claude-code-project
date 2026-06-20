"""
ข้อ 3: Half-life de-selection filter (WTI-Brent walk-forward OOS)
แนวคิด: spread ที่ mean-revert จริง -> half-life สั้น. ถ้า half-life ยาวขึ้น/ติดลบ
        = mean reversion อ่อน/พัง = pair กำลังตาย -> หยุดเทรด
Filter:
 - เปิดสถานะใหม่ได้เฉพาะเมื่อ 0 < half-life < HL_MAX
 - ถ้าถืออยู่แล้ว half-life แย่ (>HL_EXIT หรือ ติดลบ) -> บังคับปิด (de-select)
เทียบ baseline (ไม่มี filter) vs with half-life filter
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(f): return pd.read_csv(f, parse_dates=["Date"]).set_index("Date")["Price"]
df=pd.concat([load("/tmp/wti-daily.csv").rename("WTI"),
              load("/tmp/brent-daily.csv").rename("Brent")],axis=1).dropna()
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

def rolling_halflife(sp, win=90):
    """half-life ของ AR(1): Δs = a + b*s_lag ; hl = -ln2/b (b<0). คืน array (nan ถ้าไม่ mean-revert)"""
    hl=np.full(N, np.nan)
    for t in range(win, N):
        s=sp[t-win:t]; lag=s[:-1]; dif=np.diff(s)
        v=np.var(lag)
        if v<=0: continue
        b=np.cov(lag,dif,bias=True)[0,1]/v
        if b<0: hl[t]=-np.log(2)/b
    return hl

def backtest(beta,entry,lo,hi,hl=None,HL_MAX=None,HL_EXIT=None,cost_bps=5,carry_annual=0.04):
    cost=cost_bps/1e4; carry=carry_annual/252.0
    sp=W-beta*B; z=zscore(sp)
    pos=0;beta_e=0.0;gross_e=0.0;rets=np.zeros(N);trades=0;blocked=0
    for t in range(max(lo,1),hi):
        if pos!=0:
            pnl=pos*((W[t]-W[t-1])-beta_e*(B[t]-B[t-1])); rets[t]=pnl/gross_e - carry
        # de-selection: บังคับปิดถ้า pair กำลังตาย
        if pos!=0 and hl is not None:
            dead = np.isnan(hl[t]) or hl[t]>HL_EXIT
            if dead: pos=0; rets[t]-=cost; trades+=1; continue
        if pos==0:
            if abs(z[t])>entry:
                ok=True
                if hl is not None:
                    ok = (not np.isnan(hl[t])) and (0<hl[t]<HL_MAX)
                if ok:
                    pos=-1 if z[t]>0 else 1; beta_e=beta[t]
                    gross_e=abs(W[t])+abs(beta_e*B[t]); rets[t]-=cost; trades+=1
                else: blocked+=1
        else:
            if (pos==-1 and z[t]<=0) or (pos==1 and z[t]>=0): pos=0; rets[t]-=cost; trades+=1
    return rets[lo:hi], trades, blocked

beta_k=kalman()
HL=rolling_halflife(W-B)   # monitor บน level spread (เศรษฐกิจจริง) ไม่ใช่ Kalman residual
grid=[1.0,1.25,1.5,1.75,2.0,2.25,2.5]; TRAIN,TEST=504,126
HL_MAX, HL_EXIT = 5, 10   # เปิดได้ถ้า hl<5 วัน, บังคับออกถ้า hl>10 วัน (กัดจริง)

def walkforward(use_filter):
    wins=[]; lo=120
    while lo+TRAIN+TEST<=N:
        tr0,tr1=lo,lo+TRAIN; te0,te1=tr1,tr1+TEST
        hl_arg=HL if use_filter else None
        best=None
        for e in grid:
            r,_,_=backtest(beta_k,e,tr0,tr1,hl_arg,HL_MAX,HL_EXIT); s=sharpe(r)
            if best is None or s>best[1]: best=(e,s)
        r,tr,bl=backtest(beta_k,best[0],te0,te1,hl_arg,HL_MAX,HL_EXIT)
        wins.append((df.index[te0].date(),sharpe(r),np.prod(1+r)-1,tr,bl,r))
        lo+=TEST
    return wins

base=walkforward(False); filt=walkforward(True)
print(f"half-life filter: เปิดได้ถ้า hl<{HL_MAX}วัน, บังคับออกถ้า hl>{HL_EXIT}วัน\n")
print(f"{'OOS window':<13}{'BASE SR':>9}{'BASE ret':>10}{'BASE tr':>8}  |{'FILT SR':>9}{'FILT ret':>10}{'FILT tr':>8}{'blocked':>9}")
print("-"*86)
for (d,sb,rb,tb,_,_),(_,sf,rf,tf,bl,_) in zip(base,filt):
    mark=" *COVID" if str(d)=="2020-01-10" else ""
    print(f"{str(d):<13}{sb:>9.2f}{rb*100:>9.1f}%{tb:>8}  |{sf:>9.2f}{rf*100:>9.1f}%{tf:>8}{bl:>9}{mark}")

rb_all=np.concatenate([w[5] for w in base]); rf_all=np.concatenate([w[5] for w in filt])
def ex_covid(wins): return np.concatenate([w[5] for w in wins if str(w[0])!="2020-01-10"])
print(f"\nStitched OOS รวม:")
print(f"  Baseline      : Sharpe {sharpe(rb_all):.2f}  ret {(np.prod(1+rb_all)-1)*100:.0f}%  trades {sum(w[3] for w in base)}")
print(f"  + HL filter   : Sharpe {sharpe(rf_all):.2f}  ret {(np.prod(1+rf_all)-1)*100:.0f}%  trades {sum(w[3] for w in filt)}  blocked {sum(w[4] for w in filt)}")
print(f"\nStitched OOS (ตัด COVID):")
print(f"  Baseline      : Sharpe {sharpe(ex_covid(base)):.2f}  ret {(np.prod(1+ex_covid(base))-1)*100:.0f}%")
print(f"  + HL filter   : Sharpe {sharpe(ex_covid(filt)):.2f}  ret {(np.prod(1+ex_covid(filt))-1)*100:.0f}%")

fig,ax=plt.subplots(2,1,figsize=(12,9))
ax[0].plot(df.index, HL, 'C2', lw=.8); ax[0].axhline(HL_MAX,color='C0',ls='--',label=f'entry max {HL_MAX}d')
ax[0].axhline(HL_EXIT,color='C3',ls='--',label=f'exit {HL_EXIT}d'); ax[0].set_ylim(0,120)
ax[0].set_title("Rolling half-life of WTI-Brent spread (สูง = mean reversion อ่อน/ตาย)")
ax[0].set_ylabel("half-life (days)"); ax[0].legend(); ax[0].grid(alpha=.3)
ax[1].plot(np.cumprod(1+rb_all),'C3',label=f'Baseline (SR {sharpe(rb_all):.2f})')
ax[1].plot(np.cumprod(1+rf_all),'C0',label=f'+ half-life filter (SR {sharpe(rf_all):.2f})')
ax[1].set_yscale('log'); ax[1].axhline(1,color='gray',ls=':')
ax[1].set_title("Stitched OOS equity (log): filter หลบช่วง pair ตาย"); ax[1].set_xlabel("OOS days"); ax[1].legend(); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig("/home/user/Claude-code-project/wti_brent_halflife.png",dpi=110)
print("\nบันทึกกราฟ: wti_brent_halflife.png")
