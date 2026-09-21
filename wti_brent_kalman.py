"""
Pairs trading: WTI vs Brent ด้วย Kalman filter (ข้อมูลจริง EIA spot)
- Kalman ประมาณ hedge ratio (beta) + intercept แบบ time-varying
- z-score จาก innovation -> เข้าเมื่อ |z|>entry, ออกเมื่อ z ข้าม 0
- lock hedge ตอนเข้า, คิดต้นทุนซื้อขาย
- เทียบกับ static OLS hedge ratio
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- 1) โหลดข้อมูลจริง ----
def load(f):
    d = pd.read_csv(f, parse_dates=["Date"]).set_index("Date")["Price"]
    return d
brent = load("/tmp/brent-daily.csv").rename("Brent")
wti   = load("/tmp/wti-daily.csv").rename("WTI")
df = pd.concat([wti, brent], axis=1).dropna()
df = df.loc["2016-01-01":"2024-12-31"]          # ช่วงหลัง structural break shale
W = df["WTI"].values; B = df["Brent"].values
N = len(df)
print(f"ข้อมูล: {df.index[0].date()} ถึง {df.index[-1].date()}  ({N} วัน)")
print(f"WTI-Brent spread เฉลี่ย {np.mean(W-B):.2f}, sd {np.std(W-B):.2f}")

# ---- 2) Kalman filter: หา hedge ratio beta_t (time-varying) ----
# model: WTI_t = beta_t*Brent_t + c_t + noise ; ใช้ beta_t สร้าง spread = WTI - beta_t*Brent
def kalman(q=1e-4, r=1.0):
    x = np.array([1.0, 0.0]); P = np.eye(2)*1.0
    Q = np.eye(2)*q; R = r
    beta = np.zeros(N)
    for t in range(N):
        H = np.array([B[t], 1.0])
        P = P + Q
        e = W[t] - H @ x
        S = H @ P @ H + R
        K = (P @ H)/S
        x = x + K*e
        P = P - np.outer(K,H) @ P
        beta[t]=x[0]
    return beta

# ---- 3) Backtest (lock hedge ตอนเข้า, z จาก rolling window ของ spread) ----
BURN = 120   # ข้ามช่วง Kalman ยังไม่ converge
def zscore(spread, win=60):
    s=pd.Series(spread); mu=s.rolling(win).mean().values; sd=s.rolling(win).std().values
    return np.where(sd>0,(spread-mu)/sd,0.0)

def backtest(beta, entry=1.5, cost_bps=5.0):
    cost = cost_bps/1e4
    spread = W - beta*B
    z = zscore(spread)
    pos=0; beta_e=0.0; rets=np.zeros(N); trades=0
    for t in range(BURN,N):
        if pos!=0:
            pnl = pos*((W[t]-W[t-1]) - beta_e*(B[t]-B[t-1]))
            gross = abs(W[t-1]) + abs(beta_e*B[t-1])
            rets[t] = pnl/gross
        if pos==0:
            if z[t]>entry:  pos=-1; beta_e=beta[t]; trades+=1; rets[t]-=cost
            elif z[t]<-entry: pos=1; beta_e=beta[t]; trades+=1; rets[t]-=cost
        else:
            if (pos==-1 and z[t]<=0) or (pos==1 and z[t]>=0):
                pos=0; trades+=1; rets[t]-=cost
    return rets, trades

def stats(rets, trades, name):
    eq = np.cumprod(1+rets)
    ann_ret = eq[-1]**(252/N)-1
    sr = np.mean(rets)/np.std(rets)*np.sqrt(252) if np.std(rets)>0 else 0
    mdd = np.min(eq/np.maximum.accumulate(eq)-1)
    print(f"{name:<28} ann.ret {ann_ret*100:6.2f}%  Sharpe {sr:5.2f}  MDD {mdd*100:6.2f}%  trades {trades}")
    return eq

# Kalman (time-varying beta)
beta_k = kalman(q=1e-4)
rets_k, tr_k = backtest(beta_k)

# Static OLS hedge (beta คงที่จากทั้ง sample) -> z จาก rolling เหมือนกัน
beta_ols = np.polyfit(B, W, 1)[0]
beta_static = np.full(N, beta_ols)
rets_o, tr_o = backtest(beta_static)
print(f"static OLS beta = {beta_ols:.3f}")

print("\n--- ผลทดสอบ (entry |z|>1.5, cost 5bps/ขา) ---")
eq_k = stats(rets_k, tr_k, "Kalman (time-varying beta)")
eq_o = stats(rets_o, tr_o, "Static OLS + rolling z")

# ---- 4) พล็อต ----
fig, ax = plt.subplots(3,1, figsize=(12,10))
ax[0].plot(df.index, W, label="WTI"); ax[0].plot(df.index, B, label="Brent")
ax[0].set_title("WTI & Brent spot price"); ax[0].legend(); ax[0].grid(alpha=.3)
ax[1].plot(df.index, beta_k, 'C2'); ax[1].axhline(beta_ols, color='gray', ls='--', label=f'static OLS beta={beta_ols:.2f}')
ax[1].set_title("Kalman hedge ratio (beta) — time-varying"); ax[1].legend(); ax[1].grid(alpha=.3)
ax[2].plot(df.index, eq_k, 'C0', label=f"Kalman (time-varying beta)")
ax[2].plot(df.index, eq_o, 'C3', label="Static OLS beta")
ax[2].set_title("Equity curve (start = 1.0)"); ax[2].legend(); ax[2].grid(alpha=.3)
plt.tight_layout(); plt.savefig("/home/user/Claude-code-project/wti_brent_kalman.png", dpi=110)
print("\nบันทึกกราฟ: wti_brent_kalman.png")
