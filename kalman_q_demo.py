"""
Kalman filter: Q สูง vs Q ต่ำ — ผลต่อความกระตุกของ beta, จำนวนเทรด และต้นทุน
สาธิตบน pair จำลองที่ควบคุมได้ (กำหนด half-life + ให้ hedge ratio จริงดริฟต์ตามเวลา)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)
N = 1000  # วันเทรด (~4 ปี)

# ---- 1) สร้าง pair จำลอง ----
# X = log price ของขาแรก (random walk)
X = np.cumsum(rng.normal(0, 1.0, N)) + 100.0

# true hedge ratio ดริฟต์ช้าๆ จาก 1.0 -> 1.4 (ความสัมพันธ์เปลี่ยนตามเวลา)
beta_true = np.linspace(1.0, 1.4, N)

# spread จริง = กระบวนการ OU mean-reverting รอบ 0 (กำหนด half-life)
half_life = 15.0                      # วัน
theta = np.log(2) / half_life         # speed of reversion
sig_s = 1.0                           # ความผันผวนของ spread
spread_true = np.zeros(N)
for t in range(1, N):
    spread_true[t] = spread_true[t-1] - theta * spread_true[t-1] + rng.normal(0, sig_s)

# Y ที่สังเกตได้
Y = beta_true * X + spread_true

# ---- 2) Kalman filter สำหรับ [beta, intercept] ----
def run_kalman(q, r=1.0):
    """q = process noise (ปุ่มความเร็วการ adapt). คืน beta_hat, z-score (innovation/sqrt(S))"""
    x = np.array([1.0, 0.0])          # [beta, intercept] เริ่มต้น
    P = np.eye(2) * 1.0
    Q = np.eye(2) * q
    R = r
    beta_hat = np.zeros(N)
    z = np.zeros(N)
    for t in range(N):
        H = np.array([X[t], 1.0])     # Y_t = beta*X_t + intercept + noise
        # predict (random walk state)
        P = P + Q
        # innovation
        e = Y[t] - H @ x
        S = H @ P @ H + R
        K = (P @ H) / S
        # update
        x = x + K * e
        P = P - np.outer(K, H) @ P
        beta_hat[t] = x[0]
        z[t] = e / np.sqrt(S)
    return beta_hat, z

# ---- 3) Backtest: เข้าเมื่อ |z|>entry, ออกเมื่อ z ข้าม 0. Lock hedge ตอนเข้า ----
def backtest(z, beta_hat, entry=2.0, cost_bps=10.0):
    cost = cost_bps / 1e4
    pos = 0          # +1 long spread, -1 short spread, 0 flat
    trades = 0
    pnl = 0.0
    cost_drag = 0.0
    for t in range(1, N):
        # pnl ของสถานะที่ถืออยู่ (กำไรจากการเปลี่ยนแปลงของ spread จริง)
        if pos != 0:
            pnl += pos * (spread_true[t] - spread_true[t-1])
        # logic เปิด/ปิด
        if pos == 0:
            if z[t] > entry:
                pos = -1; trades += 1; cost_drag += cost * abs(beta_hat[t]+1)  # 2 ขา
            elif z[t] < -entry:
                pos = +1; trades += 1; cost_drag += cost * abs(beta_hat[t]+1)
        else:
            if (pos == -1 and z[t] <= 0) or (pos == +1 and z[t] >= 0):
                pos = 0; trades += 1; cost_drag += cost * abs(beta_hat[t]+1)
    return trades, pnl, cost_drag

# ปุ่มที่เราจะเทียบ: Q ต่ำ (นิ่ง) vs Q สูง (ไล่ noise)
configs = {"Q ต่ำ (นิ่ง)": 1e-5, "Q กลาง": 1e-3, "Q สูง (ไล่ noise)": 1e-1}

print(f"{'config':<22}{'β jitter':>12}{'β turnover':>13}{'#trades':>10}{'gross':>9}{'cost':>9}{'net':>9}")
print("-"*84)
results = {}
for name, q in configs.items():
    bh, z = run_kalman(q)
    jitter = np.std(np.diff(bh))                 # ความกระตุกรายวันของ beta
    turnover = np.sum(np.abs(np.diff(bh)))       # ถ้า re-hedge ทุกวันต้องเทรดเท่านี้
    trades, gross, cd = backtest(z, bh)
    net = gross - cd
    results[name] = (bh, z)
    print(f"{name:<22}{jitter:>12.4f}{turnover:>13.2f}{trades:>10d}{gross:>9.2f}{cd:>9.2f}{net:>9.2f}")

# ---- 4) พล็อตเทียบ ----
fig, ax = plt.subplots(2, 1, figsize=(11, 8))
ax[0].plot(beta_true, 'k--', lw=2, label='true beta')
ax[0].plot(results["Q ต่ำ (นิ่ง)"][0], 'C0', lw=1.2, label='Kalman low Q (smooth)')
ax[0].plot(results["Q สูง (ไล่ noise)"][0], 'C3', lw=0.8, alpha=0.8, label='Kalman high Q (jittery)')
ax[0].set_title('Hedge ratio (beta): low Q tracks smoothly / high Q chases noise')
ax[0].set_ylabel('beta'); ax[0].legend(); ax[0].grid(alpha=0.3)

ax[1].plot(results["Q สูง (ไล่ noise)"][1], 'C3', lw=0.6, alpha=0.7, label='z-score (high Q) -> compressed')
ax[1].plot(results["Q ต่ำ (นิ่ง)"][1], 'C0', lw=0.9, label='z-score (low Q) -> clean signal')
ax[1].axhline(2, color='gray', ls=':'); ax[1].axhline(-2, color='gray', ls=':')
ax[1].set_title('z-score (entry signal): low Q crosses +/-2 cleanly / high Q rarely triggers')
ax[1].set_ylabel('z'); ax[1].set_xlabel('day'); ax[1].legend(); ax[1].grid(alpha=0.3)
plt.tight_layout()
plt.savefig('/home/user/Claude-code-project/kalman_q_demo.png', dpi=110)
print("\nบันทึกกราฟ: kalman_q_demo.png")
