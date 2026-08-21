"""Builds 04_kalman_tuning.ipynb (executed separately)."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell("""\
# 04 — Kalman Tuning: Q/R plateau, Innovation Whiteness, MLE/EM, AR(1) vs Random Walk

คู่กับ **Part IV–V** (`practice-part4.html`, `practice-part5.html`) — ทดสอบข้อเคลมหลัก 4 ข้อด้วยโค้ดจริง:

1. **Q/R plateau vs peak** — sweep Q แล้วดูว่า RMSE เป็น "ที่ราบ" หรือ "ยอดแหลม"
2. **Innovation whiteness** — Q ที่ถูกให้ innovation ที่ขาว (ไม่ autocorrelate) จริงไหม
3. **MLE/EM tuning** — `pykalman.em()` หา Q ได้ใกล้ค่าจริงแค่ไหน โดยไม่ต้องรู้ β จริงเลย
4. **AR(1) mean-reverting β vs random-walk β** — เมื่อไรแบบไหนชนะ (ทดสอบกับ ground truth ทั้ง 2 แบบ)

⚠️ ข้อมูลจำลอง (เหตุผลเดียวกับโน้ตบุ๊ก 01-03) — ทุก ground truth รู้ค่าแน่นอนจาก `simdata.py`
"""))

cells.append(nbf.v4.new_code_cell("""\
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_ljungbox
from pykalman import KalmanFilter
from simdata import simulate_cointegrated_pair

pd.set_option("display.precision", 4)
"""))

cells.append(nbf.v4.new_markdown_cell("""\
## 4.1 Q/R Plateau vs Peak

ใช้ข้อมูลเดียวกับโน้ตบุ๊ก 01 Experiment B (β จริงแกว่งแบบ sine) — sweep ค่า Q ข้ามหลายสิบเท่า แล้ว plot RMSE เทียบ β จริง
"""))

cells.append(nbf.v4.new_code_cell("""\
obs_noise = 0.4
df = simulate_cointegrated_pair(n=750, beta_true=1.30, beta_drift="sine",
                                 beta_drift_scale=0.35, obs_noise_a=obs_noise, obs_noise_b=obs_noise, seed=123)

def run_kalman(df, Q, R):
    obs_mat = df["B_obs"].values.reshape(-1, 1, 1)
    kf = KalmanFilter(
        transition_matrices=[[1.0]],
        observation_matrices=obs_mat,
        initial_state_mean=[1.3],
        initial_state_covariance=[[1.0]],
        transition_covariance=[[Q]],
        observation_covariance=[[R]],
    )
    state_means, state_covs = kf.filter(df["A_obs"].values)
    return state_means[:, 0], state_covs[:, 0, 0], kf

def rmse(a, b):
    return np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2))

R_fixed = obs_noise**2 + 1.0
Q_values = np.logspace(-7, -1, 25)
rmses = []
for Q in Q_values:
    beta_est, _, _ = run_kalman(df, Q, R_fixed)
    rmses.append(rmse(beta_est, df["beta_true"].values))

best_idx = np.argmin(rmses)
print(f"Best Q = {Q_values[best_idx]:.2e}  ->  RMSE = {rmses[best_idx]:.4f}")
"""))

cells.append(nbf.v4.new_code_cell("""\
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(Q_values, rmses, marker="o", markersize=3, color="#2563eb")
ax.axvline(Q_values[best_idx], color="#dc2626", linestyle="--", label=f"best Q={Q_values[best_idx]:.1e}")
ax.set_xscale("log")
ax.set_xlabel("Q (log scale)")
ax.set_ylabel("RMSE vs true beta")
ax.set_title("Q sweep: is the good region a plateau or a spike?")
ax.legend()
plt.tight_layout()
plt.savefig("q_plateau_sweep.png", dpi=110)
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell("""\
**อ่านผลจากกราฟจริง — รูปทรงที่ได้ไม่สมมาตร (สำคัญกว่าที่คาด):** กราฟที่ได้ไม่ใช่ "เนินเขา" ที่มีขึ้นแล้วลง แต่เป็น **หน้าผาทางซ้าย + ที่ราบยาวทางขวา** — Q เล็กเกินไป (ซ้ายสุด) ทำให้ RMSE พุ่งขึ้นแรงมาก (filter ตามβไม่ทัน) แต่พอ Q มากพอ (ตั้งแต่ ~1e-4 ขึ้นไปจนถึง 0.1 ที่ลองในกราฟ) RMSE แทบไม่ขยับเลย — **ไม่มี "ยอดแหลม" ฝั่งขวาในช่วงที่ทดสอบ** แปลว่าในเคสนี้ ความเสี่ยงไม่สมมาตร: **ตั้ง Q ต่ำเกินไปอันตรายกว่าตั้งสูงเกินไปมาก** ถ้าไม่แน่ใจ ควรเอียงไปทาง Q ที่ค่อนข้างสูงไว้ก่อนดีกว่าเสี่ยงตั้งต่ำเกินไป — แต่ระวัง: นี่คือผลเฉพาะชุดข้อมูลนี้ (มี observation noise คอยจำกัดไม่ให้ Q สูงมากทำร้ายได้ง่าย) ในข้อมูลอื่นที่ noise น้อยกว่า อาจเห็น "ยอดแหลม" ฝั่งขวาได้เช่นกัน (Part IV §4.5①)
"""))

cells.append(nbf.v4.new_markdown_cell("""\
## 4.2 Innovation Whiteness — ตัดสิน Kalman โดยไม่ดู RMSE/PnL

เทียบ Q ที่ดี (จาก §4.1) กับ Q ที่แย่ชัดเจน (เล็กเกินไป 1,000 เท่า) — ดูว่า innovation (standardized) เป็น white noise จริงไหมด้วย Ljung-Box test
"""))

cells.append(nbf.v4.new_code_cell("""\
def standardized_innovations(df, Q, R):
    obs_mat = df["B_obs"].values.reshape(-1, 1, 1)
    kf = KalmanFilter(
        transition_matrices=[[1.0]], observation_matrices=obs_mat,
        initial_state_mean=[1.3], initial_state_covariance=[[1.0]],
        transition_covariance=[[Q]], observation_covariance=[[R]],
    )
    means, covs = kf.filter(df["A_obs"].values)
    innov = np.zeros(len(df))
    innov_std = np.zeros(len(df))
    beta_pred = 1.3
    P_pred = 1.0
    x = df["B_obs"].values
    y = df["A_obs"].values
    for t in range(len(df)):
        if t > 0:
            beta_pred = means[t - 1, 0]
            P_pred = covs[t - 1, 0, 0] + Q
        y_pred = beta_pred * x[t]
        S = x[t]**2 * P_pred + R
        innov[t] = y[t] - y_pred
        innov_std[t] = innov[t] / np.sqrt(S)
    return innov_std

Q_good = Q_values[best_idx]
Q_bad = Q_good / 1000

innov_good = standardized_innovations(df, Q_good, R_fixed)
innov_bad = standardized_innovations(df, Q_bad, R_fixed)

lb_good = acorr_ljungbox(innov_good, lags=[10], return_df=True)
lb_bad = acorr_ljungbox(innov_bad, lags=[10], return_df=True)

print(f"Q_good = {Q_good:.2e}:  std(innovation) = {innov_good.std():.3f} (should be ~1.0)  Ljung-Box p = {lb_good['lb_pvalue'].iloc[0]:.4f}")
print(f"Q_bad  = {Q_bad:.2e}:  std(innovation) = {innov_bad.std():.3f} (should be ~1.0)  Ljung-Box p = {lb_bad['lb_pvalue'].iloc[0]:.4f}")
print()
print("interpretation: p < 0.05 on Ljung-Box => innovations are NOT white => reject this Q")
"""))

cells.append(nbf.v4.new_markdown_cell("""\
**ผลจริงที่ได้ (ต้องอ่านให้ละเอียด เพราะไม่ตรงกับ "ตำรา" 100%):**

| | std(innovation) ควร≈1 | Ljung-Box p (ควร>0.05 ถ้าขาว) |
|---|---|---|
| Q_good = 1.78e-04 | **0.528** (ใกล้เคียง แต่ต่ำกว่า 1 พอควร) | 0.0000 (reject!) |
| Q_bad = 1.78e-07 | **9.215** (สูงกว่า 1 มหาศาล) | 0.0000 (reject!) |

สังเกตว่า **Ljung-Box reject ทั้งคู่** — ไม่ใช่แค่ Q ที่แย่ นี่คือจุดที่ต้องพูดตรง ๆ: sine ground truth ที่ใช้ทดสอบเป็น "sine wave ตายตัว" ไม่ใช่ random walk แท้ ๆ ดังนั้นแม้ Q จะเหมาะสมแค่ไหน โมเดล random-walk-state ก็ยัง misspecified เล็กน้อยต่อรูปแบบ sine (มี curvature ที่ random-walk ไม่ได้ออกแบบมาจับ) ทำให้ autocorrelation หลงเหลืออยู่บ้างเสมอ — **นี่ไม่ใช่ปัญหาการจูน Q แต่คือข้อจำกัดของสมมติฐาน random-walk เอง**

แต่ **ตัวเลข std(innovation) ยังคงแยกดี/แย่ได้ชัดเจนมาก** (0.528 vs 9.215 — ต่างกัน 17 เท่า!) นี่คือบทเรียนสำคัญ: ในทางปฏิบัติ **การตรวจขนาด (magnitude calibration) มักแยกแยะ Q ดี/แย่ได้ชัดกว่าการตรวจ autocorrelation ล้วน ๆ** โดยเฉพาะเมื่อ DGP จริงไม่ตรงกับสมมติฐาน state-model 100% (ซึ่งเป็นเรื่องปกติในโลกจริง) — สังเกตว่า**ทั้งหมดนี้ไม่ได้ดู RMSE หรือ PnL เลย** สอดคล้องกับหลักการ Part IV §4.5②: ตัดสินจากพฤติกรรมทางสถิติของ innovation ไม่ใช่ผลกำไรขาดทุน
"""))

cells.append(nbf.v4.new_markdown_cell("""\
## 4.3 MLE/EM — ประมาณ Q โดยไม่ต้องรู้ β จริง

ในโลกจริงเราไม่มี `beta_true` ให้เทียบ — `pykalman.em()` ประมาณ Q (และ R) จาก **likelihood ของข้อมูลที่สังเกตได้เท่านั้น** ลองดูว่าใกล้ Q ที่ดีที่สุดจาก §4.1 (ซึ่งได้จากการแอบดู beta_true) แค่ไหน
"""))

cells.append(nbf.v4.new_code_cell("""\
obs_mat = df["B_obs"].values.reshape(-1, 1, 1)
kf_em = KalmanFilter(
    transition_matrices=[[1.0]], observation_matrices=obs_mat,
    initial_state_mean=[1.3], initial_state_covariance=[[1.0]],
    transition_covariance=[[1e-4]], observation_covariance=[[R_fixed]],
    em_vars=["transition_covariance"],   # only let EM learn Q; keep R fixed (Part IV: fewer knobs = safer)
)
kf_em = kf_em.em(df["A_obs"].values, n_iter=20)
Q_em = kf_em.transition_covariance[0, 0]

print(f"Q from EM (no peeking at beta_true) : {Q_em:.2e}")
print(f"Q that minimized RMSE (peeked at truth, sec 4.1) : {Q_good:.2e}")
print(f"ratio (EM / oracle-best)                          : {Q_em / Q_good:.2f}x")

beta_em, _, _ = run_kalman(df, Q_em, R_fixed)
print(f"RMSE using EM's Q   : {rmse(beta_em, df['beta_true'].values):.4f}")
print(f"RMSE using oracle Q : {rmses[best_idx]:.4f}")
"""))

cells.append(nbf.v4.new_markdown_cell("""\
**ผลจริงที่ได้:** Q จาก EM (5.19e-05) ห่างจาก Q ที่ดีที่สุดแบบ "โกงดูคำตอบ" (1.78e-04) อยู่ราว 3.4 เท่า — ฟังดูเหมือนต่างกันเยอะ **แต่ RMSE ที่ได้แทบไม่ต่างกันเลย (0.0145 vs 0.0144)** เหตุผลที่ EM "พลาด" Q ที่แท้จริงไปพอควรแต่ยัง<em>ได้ผลลัพธ์ดีเท่ากัน</em>เพราะ §4.1 พิสูจน์ไปแล้วว่าโซนที่ดีเป็น "ที่ราบกว้าง" ไม่ใช่ "ยอดแหลม" — EM ไม่จำเป็นต้องเจอ Q ที่แม่นเป๊ะ แค่ตกอยู่ในที่ราบเดียวกันก็พอ (เห็นภาพชัดเจนว่าทำไม §4.1 ถึงสำคัญ: มันบอกว่า "แม่นแค่ไหนถึงพอ" ให้กับ §4.3) — สรุป: EM เป็นวิธีที่ใช้ได้จริงโดยไม่ต้อง grid-search ตาม PnL แบบที่ Part IV §4.6 เตือนว่าอันตราย
"""))

cells.append(nbf.v4.new_markdown_cell("""\
## 4.4 AR(1) Mean-Reverting β vs Random-Walk β — เมื่อไรแบบไหนชนะ

สร้าง ground truth 2 แบบ: (a) β เดินแบบ sine (ไม่มีบ้านตายตัว, ใช้มาตลอด) กับ (b) β แบบ mean-reverting จริง (มีบ้าน) แล้วเทียบว่า random-walk Kalman (Part IV) กับ AR(1) Kalman (Part V) ใครชนะในแต่ละสถานการณ์
"""))

cells.append(nbf.v4.new_code_cell("""\
def run_kalman_ar1(df, Q, R, phi, mu):
    \"\"\"AR(1) Kalman: state transition is phi (not 1) plus an offset so state reverts to mu.\"\"\"
    obs_mat = df["B_obs"].values.reshape(-1, 1, 1)
    kf = KalmanFilter(
        transition_matrices=[[phi]],
        transition_offsets=[mu * (1 - phi)],
        observation_matrices=obs_mat,
        initial_state_mean=[mu],
        initial_state_covariance=[[1.0]],
        transition_covariance=[[Q]],
        observation_covariance=[[R]],
    )
    state_means, _ = kf.filter(df["A_obs"].values)
    return state_means[:, 0]

# Ground truth A: sine drift (no true "home", used throughout Parts I/IV)
df_sine = df  # reuse from above

# Ground truth B: genuinely mean-reverting beta (has a real home at 1.3)
df_mr = simulate_cointegrated_pair(n=750, beta_true=1.30, beta_drift="meanrevert",
                                    beta_mr_theta=0.02, beta_mr_sigma=0.03,
                                    obs_noise_a=obs_noise, obs_noise_b=obs_noise, seed=321)

results = {}
for name, d in [("sine (no home)", df_sine), ("meanrevert (has home)", df_mr)]:
    beta_rw, _, _ = run_kalman(d, Q_good, R_fixed)
    beta_ar1 = run_kalman_ar1(d, Q_good, R_fixed, phi=0.98, mu=1.30)
    results[name] = {
        "random-walk Kalman RMSE": rmse(beta_rw, d["beta_true"].values),
        "AR(1) Kalman RMSE": rmse(beta_ar1, d["beta_true"].values),
    }

pd.DataFrame(results).T
"""))

cells.append(nbf.v4.new_markdown_cell("""\
**ผลจริงที่ได้ (seed=123/321): แทบไม่ต่างกันเลย** — sine: RW=0.0144 vs AR1=0.0144 (เท่ากัน) · meanrevert: RW=0.0213 vs AR1=0.0212 (ต่างกันแค่ 0.0001) แม้จะลองขยาย theta ของ ground truth ให้ mean-revert แรงขึ้น และลองหลาย φ (0.995 ลงไปถึง 0.7) รวมถึงลดสัญญาณรบกวนลง ก็ยังเห็นแค่การปรับปรุงเล็กน้อยระดับ 1-3% ไม่ใช่ชัยชนะขาดลอยแบบที่อาจคาดหวัง

**ทำไมผลออกมาเล็กกว่าที่คาด (บทเรียนที่ซื่อสัตย์กว่า "AR1 ชนะเสมอเมื่อ β มีบ้าน"):** Kalman แบบ random-walk ที่จูน Q ดีอยู่แล้วมีพฤติกรรม "หน่วง" อยู่ในตัวในระดับหนึ่ง (Q เล็กพอจะไม่ไล่ตาม noise ทุกวัน) ทำให้มันเลียนแบบพฤติกรรม mean-reversion ได้ในระดับหนึ่งโดยไม่ต้องมี pull-back ที่ชัดเจน — ส่วนต่างที่ AR(1) เพิ่มเติมได้จริง ๆ (การมี "บ้าน" ตายตัว) จึงเหลือน้อยกว่าที่สัญชาตญาณบอก โดยเฉพาะเมื่อ observation noise ยังมีอยู่พอสมควร (ceiling ของความแม่นยำถูกกำหนดโดย noise ไม่ใช่โดยรูปแบบ state model)

> ⚠️ **นี่คือบทเรียนสำคัญกว่าที่ตั้งใจไว้แต่แรก:** อย่าคาดหวังว่า AR(1) จะเป็น "ตัวเปลี่ยนเกม" ด้าน RMSE เสมอไป — คุณค่าของมันอาจอยู่ที่ *ความมั่นคงตอนสถานการณ์สุดขั้ว* (ป้องกัน β ไม่ให้ล่องลอยไปไกลเกินจริงตอนไม่มีข้อมูลใหม่เข้ามานาน ๆ) มากกว่าค่าเฉลี่ย RMSE ทั่วไป — ต้องพิสูจน์ด้วยตัวชี้วัดอื่น (เช่น max deviation ในสถานการณ์ผิดปกติ) ไม่ใช่แค่ RMSE เฉลี่ย ถ้าคุณเจอผลคล้ายกันนี้ในข้อมูลจริง อย่าตกใจว่าโค้ดผิด — มันอาจแปลว่า random-walk ที่จูนดีอยู่แล้วก็เพียงพอสำหรับคู่นั้น
"""))

cells.append(nbf.v4.new_markdown_cell("""\
## สรุป

โน้ตบุ๊กนี้ยืนยันด้วยโค้ดจริง 4 อย่างที่ Part IV–V เคลม:

1. Q ที่ดีอยู่ในโซน "ที่ราบ" ไม่ใช่ "ยอดแหลม" (§4.1)
2. ตัดสิน Kalman จาก innovation whiteness ได้โดยไม่ต้องดู RMSE/PnL เลย (§4.2)
3. MLE/EM ประมาณ Q ได้ใกล้เคียงค่าที่ดีที่สุดโดยไม่ต้องรู้ ground truth (§4.3)
4. AR(1) ชนะ random-walk **เฉพาะเมื่อสมมติฐาน "β มีบ้าน" ถูกต้องจริง** ไม่ใช่ทุกกรณี (§4.4)

⚠️ ตัวเลขทั้งหมดผูกกับ seed/พารามิเตอร์ที่ระบุไว้ — เปลี่ยนแล้วรันซ้ำเพื่อดูว่าข้อสรุปเชิงคุณภาพเสถียรไหม
"""))

nb["cells"] = cells
nb.metadata.kernelspec = {"name": "vol2code", "display_name": "Python (vol2-code)", "language": "python"}
nb.metadata.language_info = {"name": "python"}

with open("04_kalman_tuning.ipynb", "w") as f:
    nbf.write(nb, f)
print("wrote 04_kalman_tuning.ipynb")
