"""
kalman_pairs.py — Pairs trading ด้วย Kalman filter (สูตรที่ผ่านการทดสอบ)
ต้องการแค่:  numpy, pandas

หลักการสำคัญ (อย่าข้าม):
  1. Kalman ประมาณ hedge ratio (beta) แบบ time-varying — ตั้ง Q ต่ำ
  2. z-score คำนวณจาก rolling window ของ spread (ไม่ใช่ innovation ของ Kalman)
  3. LOCK beta ตอนเปิดสถานะ -> ถือค่านั้นจนปิด (ห้าม re-hedge รายวัน)
  4. ใส่ทั้ง transaction cost และ cost of carry เสมอ
  5. ประเมินด้วย walk-forward / out-of-sample เท่านั้น อย่าเชื่อ in-sample
"""
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# 1) Kalman filter: ประมาณ hedge ratio beta_t  (model: p1 = beta*p2 + c + noise)
# ---------------------------------------------------------------------------
def kalman_beta(p1, p2, q=1e-4, r=1.0):
    """
    p1, p2 : array ราคาของสองขา (เช่น WTI, Brent) ความยาวเท่ากัน
    q      : process noise — ยิ่งต่ำ beta ยิ่งนิ่ง (กัน over-trade). แนะนำ 1e-4..1e-5
    r      : observation noise (ปล่อย 1.0 ได้)
    คืน beta : array hedge ratio รายวัน (causal — ใช้แค่ข้อมูลอดีต)
    """
    p1 = np.asarray(p1, float); p2 = np.asarray(p2, float)
    n = len(p1)
    x = np.array([1.0, 0.0])          # state = [beta, intercept]
    P = np.eye(2)
    Q = np.eye(2) * q
    beta = np.zeros(n)
    for t in range(n):
        H = np.array([p2[t], 1.0])
        P = P + Q                       # predict (random walk)
        e = p1[t] - H @ x              # innovation
        S = H @ P @ H + r
        K = (P @ H) / S               # gain
        x = x + K * e                 # update
        P = P - np.outer(K, H) @ P
        beta[t] = x[0]
    return beta


# ---------------------------------------------------------------------------
# 2) z-score ของ spread จาก rolling window
# ---------------------------------------------------------------------------
def rolling_zscore(spread, win=60):
    s = pd.Series(spread)
    mu = s.rolling(win).mean()
    sd = s.rolling(win).std()
    z = (s - mu) / sd
    return z.fillna(0.0).values


# ---------------------------------------------------------------------------
# 3) Backtest — lock hedge ตอนเข้า, ใส่ต้นทุน + cost of carry
# ---------------------------------------------------------------------------
def pairs_backtest(p1, p2, beta, z, entry=1.5,
                   cost_bps=5.0, carry_annual=0.04, start=0):
    """
    p1, p2 : ราคาสองขา
    beta   : hedge ratio รายวัน (จาก kalman_beta) หรือค่าคงที่ (static OLS)
    z      : z-score รายวัน
    entry  : เปิดเมื่อ |z| > entry, ปิดเมื่อ z ข้าม 0
    cost_bps     : ต้นทุนต่อครั้งเปิด/ปิด (bps ของ gross notional, ครอบ 2 ขา)
    carry_annual : cost of carry ต่อปี (financing + ค่ายืม short)
    start  : index เริ่มเทรด (ข้าม burn-in ของ Kalman ~120)
    คืน dict: rets(array), trades, equity(array)
    """
    p1 = np.asarray(p1, float); p2 = np.asarray(p2, float)
    beta = np.broadcast_to(np.asarray(beta, float), p1.shape)
    n = len(p1)
    cost = cost_bps / 1e4
    carry = carry_annual / 252.0
    pos = 0; beta_e = 0.0; gross_e = 0.0
    rets = np.zeros(n); trades = 0
    for t in range(max(start, 1), n):
        if pos != 0:                              # MtM ของสถานะที่ถืออยู่
            pnl = pos * ((p1[t]-p1[t-1]) - beta_e*(p2[t]-p2[t-1]))
            rets[t] = pnl / gross_e - carry       # หารด้วย notional ที่ LOCK ตอนเข้า
        if pos == 0:
            if abs(z[t]) > entry:                 # เปิด
                pos = -1 if z[t] > 0 else 1
                beta_e = beta[t]                  # << LOCK hedge ratio
                gross_e = abs(p1[t]) + abs(beta_e*p2[t])
                rets[t] -= cost
                trades += 1
        else:
            if (pos == -1 and z[t] <= 0) or (pos == 1 and z[t] >= 0):  # ปิดเมื่อข้าม 0
                pos = 0; rets[t] -= cost; trades += 1
    eq = np.cumprod(1 + rets)
    return dict(rets=rets, trades=trades, equity=eq)


def perf(rets, trades=None):
    """metrics รายปี: annualized return, Sharpe, max drawdown"""
    rets = np.asarray(rets); n = len(rets); eq = np.cumprod(1+rets)
    ann = eq[-1]**(252/n) - 1 if eq[-1] > 0 else float('nan')
    sr = np.mean(rets)/np.std(rets)*np.sqrt(252) if np.std(rets) > 0 else 0.0
    mdd = np.min(eq/np.maximum.accumulate(eq) - 1)
    return dict(ann_return=ann, sharpe=sr, max_drawdown=mdd, trades=trades)


# ---------------------------------------------------------------------------
# 4) ตัวช่ว walk-forward (เลือก beta + entry จาก train, วัดบน test เท่านั้น)
# ---------------------------------------------------------------------------
def walk_forward(p1, p2, q=1e-4, train=504, test=126, burn=120,
                 entry_grid=(1.0,1.25,1.5,1.75,2.0,2.25,2.5),
                 cost_bps=5.0, carry_annual=0.04, use_kalman=True):
    p1 = np.asarray(p1, float); p2 = np.asarray(p2, float); n = len(p1)
    beta_full = kalman_beta(p1, p2, q=q) if use_kalman else None
    oos = []
    lo = burn
    while lo + train + test <= n:
        tr0, tr1, te0, te1 = lo, lo+train, lo+train, lo+train+test
        if use_kalman:
            beta = beta_full
        else:                                     # static OLS beta จาก train เท่านั้น
            b = np.polyfit(p2[tr0:tr1], p1[tr0:tr1], 1)[0]
            beta = np.full(n, b)
        spread = p1 - beta*p2
        z = rolling_zscore(spread)
        # เลือก entry ที่ Sharpe ดีสุดบน train
        best = max(entry_grid,
                   key=lambda e: perf(pairs_backtest(p1,p2,beta,z,e,cost_bps,carry_annual,tr0)['rets'][tr0:tr1])['sharpe'])
        r = pairs_backtest(p1, p2, beta, z, best, cost_bps, carry_annual, te0)['rets'][te0:te1]
        oos.append(r)
        lo += test
    return np.concatenate(oos)


# ---------------------------------------------------------------------------
# ตัวอย่างการใช้งาน
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # ---- โหลดราคาสองขาของคุณเอง (ตัวอย่าง: WTI, Brent) ----
    # df ต้องมีคอลัมน์ราคาสองตัว index เป็นวันที่ เรียงเก่า->ใหม่
    def load(f): return pd.read_csv(f, parse_dates=["Date"]).set_index("Date")["Price"]
    df = pd.concat([load("/tmp/wti-daily.csv").rename("P1"),
                    load("/tmp/brent-daily.csv").rename("P2")], axis=1).dropna()
    df = df.loc["2016-01-01":"2024-12-31"]
    p1, p2 = df["P1"].values, df["P2"].values

    # ---- วิธีที่ 1: รันตรงๆ ทั้ง sample (ดูคร่าวๆ — in-sample, อย่าเชื่อมาก) ----
    beta = kalman_beta(p1, p2, q=1e-4)            # Q ต่ำ
    spread = p1 - beta*p2
    z = rolling_zscore(spread, win=60)
    res = pairs_backtest(p1, p2, beta, z, entry=1.5,
                         cost_bps=5.0, carry_annual=0.04, start=120)
    print("In-sample (ระวัง optimistic):", perf(res['rets'], res['trades']))

    # ---- วิธีที่ 2: walk-forward OOS (ตัวเลขที่เชื่อได้) ----
    oos_kalman = walk_forward(p1, p2, q=1e-4, use_kalman=True)
    oos_static = walk_forward(p1, p2, use_kalman=False)
    print("OOS Kalman :", perf(oos_kalman))
    print("OOS Static :", perf(oos_static))
