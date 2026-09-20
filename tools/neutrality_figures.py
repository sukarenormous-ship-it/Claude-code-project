#!/usr/bin/env python3
"""สร้าง docs/neutrality-figures.json — ตัวเลขของบท "เป็นกลาง แปลว่าอะไร"

ตอบคำถามของหลักสูตร Part XV (Portfolio Engineering) แบบเดินเลข:
dollar-neutral / beta-neutral / factor-neutral เป็นสามขั้นที่ต่างกันจริงแค่ไหน
แล้ว turnover control กินกำไรที่เหลือไปเท่าไร

ข้อมูล — ต้องบอกให้ชัดว่าอะไรจริงอะไรจำลอง:
  - **ปัจจัยตลาดเป็นของจริง**: ผลตอบแทนรายวันของ BTC จาก docs/nq-figures.json
    (ชุดเดียวกับทุกบทในคลัง — มีทั้งช่วงนิ่งหกสัปดาห์และช่วงทะยาน +27% ใน 10 วัน)
  - **หน้าตัดขวางเป็นของจำลอง**: เหรียญสมมติ 8 ตัวสร้างจาก r_i = β_i·r_mkt + γ_i·f2 + idio
    ด้วย seed คงที่ — เพราะคลังนี้ไม่มีแผงราคาหลายสินทรัพย์ที่รันซ้ำได้
    (แบบเดียวกับคู่ A/B ของ math-part9 §9.1 ที่ประกาศตัวว่าเป็นข้อมูลสร้างขึ้น)

เหตุที่จำลองหน้าตัดขวางได้โดยไม่เสียความซื่อสัตย์: บทนี้สอน **กลไกเลขคณิต**
ของการทำให้เป็นกลาง ซึ่งเป็นจริงไม่ขึ้นกับว่าข้อมูลมาจากไหน · และเพราะรู้ β จริง
จึงวัด "ความผิดพลาดของ β ที่ประมาณมา" ได้ตรง ๆ ซึ่งข้อมูลจริงทำไม่ได้

    python3 tools/neutrality_figures.py
"""

import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "nq-figures.json")
OUT = os.path.join(ROOT, "docs", "neutrality-figures.json")

SEED = 20260919
N_ASSETS = 8
EST_WINDOW = 20                 # วันที่ใช้ประมาณ β — สั้นพอให้เห็นความผิดพลาดจริง
COST_BPS = 10                   # ต้นทุนไป-กลับ 10 bps ของมูลค่าที่ซื้อขาย (0.10%)
SURGE_FROM, SURGE_TO = "2026-08-17", "2026-08-27"   # ช่วงที่ BTC ทะยาน +27% — ใช้อ้างอิงในบท


def market_returns():
    """ผลตอบแทนรายวันของ BTC (%) — ของจริง ชุดเดียวกับทุกบท"""
    with open(SRC, encoding="utf-8") as fh:
        px = json.load(fh)["ราคารายวัน"]
    days = sorted(px)
    p = np.array([float(px[d]) for d in days])
    return days[1:], (p[1:] / p[:-1] - 1) * 100


ALPHA_FAST = 0.18               # แรงของ alpha เร็ว — idio กลับตัวจากเมื่อวาน (หมดฤทธิ์ใน 1 วัน)
ALPHA_SLOW = 0.12               # แรงของ alpha ช้า — สถานะที่อยู่ทนแล้วค่อย ๆ จ่าย
SLOW_PHI = 0.90                 # ความทนของสถานะช้า (ครึ่งชีวิต ≈ 6.6 วัน)


def panel(days, mkt):
    """เหรียญสมมติ 8 ตัว — ฝัง alpha ไว้สองชนิดที่เสื่อมด้วยความเร็วต่างกัน

    r_i,t = β_i·ตลาด_t + γ_i·ปัจจัยสอง_t + ALPHA_SLOW·v_i,t−1 + idio_i,t

    โดย v เป็นสถานะที่อยู่ทน (AR φ = 0.90) ส่วน idio มีการกลับตัวหนึ่งวันฝังอยู่
    ทำแบบนี้เพราะบทต้องแสดงว่า **ความเร็วที่ควรเทรด ขึ้นกับความเร็วที่ alpha เสื่อม**
    ถ้ามี alpha ชนิดเดียวจะสรุปได้ด้านเดียว
    """
    rng = np.random.default_rng(SEED)
    n = len(mkt)
    beta = np.round(np.linspace(0.60, 1.80, N_ASSETS), 3)
    gamma = np.round(rng.uniform(-0.8, 0.8, N_ASSETS), 3)
    f2 = rng.normal(0, 1.2, n)                      # ปัจจัยที่สอง (ตั้งฉากกับตลาดโดยสร้าง)
    f2 = f2 - (f2 @ mkt) / (mkt @ mkt) * mkt
    idio = rng.normal(0, 1.4, (N_ASSETS, n))
    for i in range(N_ASSETS):                       # alpha เร็ว: กลับตัวจากเมื่อวาน
        for t in range(1, n):
            idio[i, t] -= ALPHA_FAST * idio[i, t - 1]
    v = np.zeros((N_ASSETS, n))                     # alpha ช้า: สถานะที่อยู่ทน
    shock = rng.normal(0, 1.0, (N_ASSETS, n))
    for t in range(1, n):
        v[:, t] = SLOW_PHI * v[:, t - 1] + shock[:, t]
    slow = np.zeros((N_ASSETS, n))
    slow[:, 1:] = ALPHA_SLOW * v[:, :-1]
    r = beta[:, None] * mkt[None, :] + gamma[:, None] * f2[None, :] + slow + idio
    return beta, gamma, f2, idio, r


def residuals(r, mkt, beta_est):
    """ส่วนที่ตลาดอธิบายไม่ได้ — ใช้ β ที่ประมาณจากหน้าต่างย้อนหลัง (ข้อมูลที่รู้ได้จริง)"""
    n = r.shape[1]
    e = np.full(r.shape, np.nan)
    for t in range(n):
        if not np.isnan(beta_est[:, t]).any():
            e[:, t] = r[:, t] - beta_est[:, t] * mkt[t]
    return e


def signal_fast(e):
    """สัญญาณเร็ว: เมื่อวานหล่นเกินที่ตลาดอธิบายได้ พรุ่งนี้คาดว่าจะเด้ง — จับ alpha เร็ว"""
    return -e


def signal_slow(e, win=10):
    """สัญญาณช้า: ค่าเฉลี่ยของ residual ย้อนหลัง win วัน — ประมาณ "สถานะที่อยู่ทน" v

    residual = ALPHA_SLOW·v + เสียงรบกวน · เฉลี่ยหลายวันทำให้เสียงหักล้างกัน เหลือ v
    """
    n = e.shape[1]
    s = np.full(e.shape, np.nan)
    for t in range(win, n):
        w = e[:, t - win + 1:t + 1]
        if not np.isnan(w).any():
            s[:, t] = w.mean(axis=1)
    return s


def weights_from(sig, mode, beta_est=None, gamma_est=None):
    """แปลงสัญญาณเป็นน้ำหนัก — สี่โหมดคือสี่ขั้นของความเป็นกลาง"""
    w = np.where(np.isnan(sig), 0.0, sig)
    if np.abs(w).sum() == 0:
        return w
    w = w / np.abs(w).sum()                         # รวมมูลค่าสัมบูรณ์ = 1 เสมอ (เทียบกันได้)
    if mode == "naive":
        return w
    ones = np.ones_like(w)
    if mode == "dollar":                            # ขั้น 1: ผลรวมน้ำหนัก = 0
        X = ones[:, None]
    elif mode == "beta":                            # ขั้น 2: ผลรวม = 0 **และ** w·β = 0 พร้อมกัน
        X = np.column_stack([ones, beta_est])
    else:                                           # ขั้น 3: เพิ่มปัจจัยที่สองเข้าไปอีกคอลัมน์
        X = np.column_stack([ones, beta_est, gamma_est])
    # ฉายน้ำหนักออกจากสเปซของคอลัมน์ทั้งหมดพร้อมกัน — ทำทีละตัวแล้วหักค่าเฉลี่ยทีหลัง
    # จะทำลายความเป็นกลางที่เพิ่งสร้าง เพราะเวกเตอร์ 1 กับ β ไม่ตั้งฉากกัน
    w = w - X @ np.linalg.lstsq(X, w, rcond=None)[0]
    tot = np.abs(w).sum()
    return w / tot if tot > 1e-12 else w


def rolling_beta(r, mkt, win=EST_WINDOW):
    """β ที่ประมาณจากหน้าต่างย้อนหลัง — คือสิ่งที่ใช้ได้จริง (ต่างจาก β จริงที่รู้เพราะเราสร้างเอง)"""
    n = r.shape[1]
    out = np.full(r.shape, np.nan)
    for t in range(win, n):
        m = mkt[t - win:t]
        mc = m - m.mean()
        den = mc @ mc
        for i in range(r.shape[0]):
            y = r[i, t - win:t]
            out[i, t] = (mc @ (y - y.mean())) / den if den else np.nan
    return out


def rolling_gamma(r, mkt, f2, win=EST_WINDOW):
    """γ ที่ประมาณพร้อมกับ β ด้วย OLS สองตัวแปร"""
    n = r.shape[1]
    out = np.full(r.shape, np.nan)
    for t in range(win, n):
        X = np.column_stack([np.ones(win), mkt[t - win:t], f2[t - win:t]])
        for i in range(r.shape[0]):
            out[i, t] = np.linalg.lstsq(X, r[i, t - win:t], rcond=None)[0][2]
    return out


def run(r, mkt, f2, sig, beta_est, gamma_est, beta_true, gamma_true, mode, lam=1.0):
    """เดินพอร์ตวันต่อวัน — คืนผลตอบแทนรายวัน, turnover, และ exposure ที่เหลือจริง"""
    n = r.shape[1]
    prev = np.zeros(r.shape[0])
    rets, turns, exp_b, exp_g, mk_next = [], [], [], [], []
    for t in range(EST_WINDOW, n - 1):
        if np.isnan(sig[:, t]).all() or np.isnan(beta_est[:, t]).any():
            continue
        w = weights_from(sig[:, t], mode, beta_est[:, t], gamma_est[:, t])
        if lam < 1.0:
            # turnover control แบบถ่วงน้ำหนัก: เดินจากพอร์ตเดิมไปหาเป้าหมายแค่ λ ของระยะทาง
            #
            # ข้อควรระวังที่พลาดง่ายมาก: ผลผสมเชิงเส้นของพอร์ตที่เป็นกลาง "ยังเป็นกลาง" จริง
            # เฉพาะเมื่อทั้งสองตัวตั้งฉากกับ **คอลัมน์ชุดเดียวกัน** · แต่ที่นี่ β̂ และ γ̂
            # ถูกประมาณใหม่ทุกวัน พอร์ตเมื่อวานจึงตั้งฉากกับคอลัมน์ของ *เมื่อวาน* ไม่ใช่ของวันนี้
            # ถ้าไม่ฉายซ้ำ ความเป็นกลางจะรั่วออกตามขนาดที่ β̂ เปลี่ยน (วัดได้ถึง |w·γ̂| = 0.14 ที่ λ ต่ำ)
            # มีแต่ข้อจำกัด dollar-neutral (คอลัมน์ 1 ซึ่งคงที่) ที่รอดโดยไม่ต้องฉายซ้ำ
            w = weights_from(lam * w + (1 - lam) * prev, mode, beta_est[:, t], gamma_est[:, t])
        turns.append(float(np.abs(w - prev).sum()))
        rets.append(float(w @ r[:, t + 1]))         # ถือข้ามคืน กินผลตอบแทนวันถัดไป
        exp_b.append(float(w @ beta_true))          # exposure จริง วัดด้วย β จริง ไม่ใช่ที่ประมาณ
        exp_g.append(float(w @ gamma_true))
        mk_next.append(float(mkt[t + 1]))
        prev = w
    return (np.array(rets), np.array(turns), np.array(exp_b), np.array(exp_g), np.array(mk_next))


def stats(rets, turns, cost_bps=COST_BPS):
    gross = float(rets.sum())
    # COST_BPS เป็นต้นทุน "ไป-กลับ" (ซื้อแล้วขายคืน) แต่การปรับพอร์ตแต่ละวันคือขาเดียว
    # จึงจ่ายครึ่งเดียวของค่านั้นต่อหนึ่งหน่วย turnover · 10 bps ไป-กลับ = 5 bps ต่อขา
    cost = float(turns.sum() * cost_bps / 100 / 2)
    sd = float(rets.std(ddof=1)) if len(rets) > 1 else 0.0
    n = max(len(rets), 1)
    return {"กำไรรวมเปอร์เซ็นต์": round(gross, 3),
            "ต้นทุนรวมเปอร์เซ็นต์": round(cost, 3),
            "กำไรสุทธิเปอร์เซ็นต์": round(gross - cost, 3),
            "กำไรขั้นต้นต่อวันเปอร์เซ็นต์": round(gross / n, 4),
            "ต้นทุนต่อวันเปอร์เซ็นต์": round(cost / n, 4),
            "กำไรสุทธิต่อวันเปอร์เซ็นต์": round((gross - cost) / n, 4),
            "ความผันผวนรายวันเปอร์เซ็นต์": round(sd, 3),
            "turnoverเฉลี่ยต่อวัน": round(float(turns.mean()), 3),
            "จำนวนวัน": int(len(rets))}


def build():
    days, mkt = market_returns()
    beta_true, gamma_true, f2, idio, r = panel(days, mkt)
    beta_est = rolling_beta(r, mkt)
    gamma_est = rolling_gamma(r, mkt, f2)
    e = residuals(r, mkt, beta_est)
    sig = signal_fast(e)
    sig_slow = signal_slow(e)

    modes = [("naive", "ไม่ทำอะไรเลย"), ("dollar", "ขั้น 1 · dollar-neutral"),
             ("beta", "ขั้น 2 · beta-neutral"), ("factor", "ขั้น 3 · factor-neutral")]
    ladder, series = [], {}
    for key, label in modes:
        rets, turns, eb, eg, mk = run(r, mkt, f2, sig, beta_est, gamma_est, beta_true, gamma_true, key)
        st = stats(rets, turns)
        st["ขั้น"] = label
        st["exposureตลาดเฉลี่ย"] = round(float(np.mean(eb)), 4)
        st["exposureตลาดสัมบูรณ์เฉลี่ย"] = round(float(np.mean(np.abs(eb))), 4)
        st["exposureปัจจัยสองสัมบูรณ์เฉลี่ย"] = round(float(np.mean(np.abs(eg))), 4)
        # ตัวชี้วัดหลัก: ความแปรปรวนของพอร์ตกี่ % มาจากตลาด — นิ่งกว่ากำไรบนข้อมูลสั้น
        from_mkt = eb * mk
        share = float(np.var(from_mkt, ddof=1) / np.var(rets, ddof=1) * 100) if len(rets) > 1 else 0.0
        st["ความผันผวนที่มาจากตลาดเปอร์เซ็นต์"] = round(share, 1)
        st["ความผันผวนจากตลาดต่อวันเปอร์เซ็นต์"] = round(float(np.std(from_mkt, ddof=1)), 4)
        st["กำไรที่มาจากตลาดเปอร์เซ็นต์"] = round(float(from_mkt.sum()), 3)
        ladder.append(st)
        series[key] = [round(float(v), 4) for v in np.cumsum(rets)]

    # ── หางซ้าย: ความเป็นกลางมีไว้กันวันแย่ ๆ ไม่ใช่เพิ่มกำไรเฉลี่ย ──
    tail = []
    for key, label in modes:
        rets, _, eb, _, mkn = run(r, mkt, f2, sig, beta_est, gamma_est, beta_true, gamma_true, key)
        worst = int(np.argmin(rets))
        # วันที่ตลาดขยับแรงที่สุด พอร์ตแต่ละขั้นโดนไปเท่าไร
        big = np.argsort(-np.abs(mkn))[:5]
        tail.append({"ขั้น": label,
                     "วันแย่ที่สุดเปอร์เซ็นต์": round(float(rets[worst]), 3),
                     "ผลตอบแทนตลาดวันนั้นเปอร์เซ็นต์": round(float(mkn[worst]), 3),
                     "ขาดทุนสะสมสูงสุดเปอร์เซ็นต์": round(float(np.min(np.cumsum(rets) - np.maximum.accumulate(np.cumsum(rets)))), 3),
                     "ค่าสัมบูรณ์เฉลี่ยของกำไร5วันที่ตลาดขยับแรงสุด": round(float(np.mean(np.abs(rets[big]))), 3)})

    # ── β ที่ประมาณมา ผิดจาก β จริงเท่าไร ──
    valid = ~np.isnan(beta_est)
    err = beta_est[valid] - np.repeat(beta_true[:, None], beta_est.shape[1], axis=1)[valid]
    per_asset = []
    for i in range(N_ASSETS):
        e = beta_est[i][~np.isnan(beta_est[i])]
        per_asset.append({"เหรียญ": f"เหรียญ {i+1}",
                          "เบต้าจริง": float(beta_true[i]),
                          "เบต้าประมาณเฉลี่ย": round(float(e.mean()), 3),
                          "เบต้าประมาณต่ำสุด": round(float(e.min()), 3),
                          "เบต้าประมาณสูงสุด": round(float(e.max()), 3),
                          "ความคลาดเคลื่อนสัมบูรณ์เฉลี่ย": round(float(np.abs(e - beta_true[i]).mean()), 3)})
    beta_err = {"_อ่านว่า": "β จริงรู้ได้เพราะหน้าตัดขวางเป็นข้อมูลจำลอง — ของจริงไม่มีทางรู้",
                "หน้าต่างที่ใช้ประมาณ": EST_WINDOW,
                "ความคลาดเคลื่อนสัมบูรณ์เฉลี่ยทั้งแผง": round(float(np.abs(err).mean()), 3),
                "ความคลาดเคลื่อนสัมบูรณ์สูงสุด": round(float(np.abs(err).max()), 3),
                "รายเหรียญ": per_asset}

    # ── beta-neutral ด้วย β ที่ประมาณ ยังเหลือ exposure เท่าไร ──
    _, _, eb_est, _, _ = run(r, mkt, f2, sig, beta_est, gamma_est, beta_true, gamma_true, "beta")
    _, _, eb_perfect, _, _ = run(r, mkt, f2, sig,
                              np.repeat(beta_true[:, None], r.shape[1], axis=1),
                              np.repeat(gamma_true[:, None], r.shape[1], axis=1),
                              beta_true, gamma_true, "beta")
    residual = {"exposureเหลือเมื่อใช้เบต้าประมาณ": round(float(np.mean(np.abs(eb_est))), 4),
                "exposureเหลือถ้ารู้เบต้าจริง": round(float(np.mean(np.abs(eb_perfect))), 4),
                "อ่านว่า": "ตัวเลขแรกคือสิ่งที่ทำได้จริง ตัวที่สองคือเพดานที่ทำไม่ได้"}

    # ── turnover control: แถบไม่ขยับกว้างแค่ไหนถึงคุ้ม ──
    lams = [1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05]

    def sweep(signal):
        g = []
        for lm in lams:
            rets, turns, eb, _, _ = run(r, mkt, f2, signal, beta_est, gamma_est,
                                        beta_true, gamma_true, "factor", lam=lm)
            st = stats(rets, turns)
            st["ความเร็วปรับพอร์ต"] = lm
            st["exposureตลาดสัมบูรณ์เฉลี่ย"] = round(float(np.mean(np.abs(eb))), 4)
            g.append(st)
        return g

    grid = sweep(sig)
    grid_slow = sweep(sig_slow)
    best = max(grid, key=lambda g: g["กำไรสุทธิเปอร์เซ็นต์"])
    best_slow = max(grid_slow, key=lambda g: g["กำไรสุทธิเปอร์เซ็นต์"])
    none_band = grid[0]

    # ── alpha เสื่อมเร็วแค่ไหน: IC ของแต่ละสัญญาณที่ระยะล่วงหน้า 1..5 วัน ──
    def ic_at(signal, h):
        """IC เฉลี่ยรายวัน พร้อม SE และ t — IC เปล่า ๆ ไม่มีความหมาย (ดู statarb-ic-lab)"""
        vals = []
        for t in range(EST_WINDOW, r.shape[1] - h):
            sv = signal[:, t]
            if np.isnan(sv).any():
                continue
            fwd = r[:, t + 1:t + 1 + h].sum(axis=1) - beta_true * mkt[t + 1:t + 1 + h].sum()
            if sv.std() > 1e-12 and fwd.std() > 1e-12:
                vals.append(float(np.corrcoef(sv, fwd)[0, 1]))
        if not vals:
            return None
        a = np.array(vals)
        se = float(a.std(ddof=1) / np.sqrt(len(a)))
        return {"IC": round(float(a.mean()), 4), "SE": round(se, 4),
                "tstat": round(float(a.mean() / se), 2) if se > 0 else None,
                "จำนวนวัน": int(len(a)),
                "หลุดฐาน": bool(abs(a.mean()) > 2 * se)}

    decay = {"_อ่านว่า": "IC เฉลี่ยรายวันของสัญญาณ เทียบกับผลตอบแทนส่วนเกินสะสม h วันข้างหน้า "
                          "· SE จากการกระจายของ IC รายวัน · \"หลุดฐาน\" = |IC| เกิน 2 เท่าของ SE",
             "สัญญาณเร็ว": {f"{h} วัน": ic_at(sig, h) for h in (1, 2, 3, 5)},
             "สัญญาณช้า": {f"{h} วัน": ic_at(sig_slow, h) for h in (1, 2, 3, 5)}}

    return {
        "_อ่านก่อน": "สร้างด้วย tools/neutrality_figures.py — ห้ามแก้ด้วยมือ",
        "ข้อมูล": {
            "ปัจจัยตลาด": "ผลตอบแทนรายวัน BTC ของจริง จาก docs/nq-figures.json",
            "ตั้งแต่": days[0], "ถึง": days[-1], "จำนวนวันผลตอบแทน": len(mkt),
            "หน้าตัดขวาง": f"เหรียญจำลอง {N_ASSETS} ตัว สร้างด้วย seed {SEED}",
            "สูตรสร้าง": "r_i = β_i × ตลาด + γ_i × ปัจจัยสอง + idio (idio มี mean reversion 0.18 ฝังไว้)",
            "เบต้าจริง": [float(v) for v in beta_true],
            "แกมมาจริง": [float(v) for v in gamma_true],
            "หน้าต่างประมาณค่า": EST_WINDOW,
            "ต้นทุนไปกลับbps": COST_BPS,
            "ข้อจำกัดที่ต้องบอก": "หน้าตัดขวางเป็นข้อมูลจำลอง — ตัวเลขกำไรจึงไม่ใช่ผลของกลยุทธ์จริง "
                                    "สิ่งที่อ่านได้คือ *ความต่างระหว่างขั้น* ซึ่งเป็นผลเชิงกลไก",
            "สิ่งที่การจำลองยื่นให้ฟรี": [
                "γ ประมาณจากปัจจัยที่สอง *ตัวจริง* — ของจริงต้องประมาณตัวปัจจัยเองก่อน "
                "ผลของขั้น factor-neutral จึงเป็นเพดาน ไม่ใช่สิ่งที่ทำได้",
                "IC คำนวณโดยหักผลตอบแทนตลาดด้วย β *จริง* — ซึ่งบทเองพิสูจน์ใน §5 ว่าไม่มีทางรู้",
                "alpha ทั้งสองความเร็วถูกฝังไว้ตอนสร้างข้อมูล และสัญญาณสองตัวคือเครื่องตรวจจับ "
                "ที่ตรงกับมันพอดี — ข้อสรุปเรื่อง λ จึงเป็นความสัมพันธ์เชิงกลไก ไม่ใช่หลักฐานจากตลาด",
            ],
        },
        "ขั้นบันไดความเป็นกลาง": ladder,
        "เส้นกำไรสะสม": series,
        "หางซ้าย": {"_อ่านว่า": "ความเป็นกลางซื้ออะไร — วัดที่วันแย่ที่สุดและวันที่ตลาดขยับแรงที่สุด",
                     "ผลของแต่ละขั้น": tail},
        "ความผิดพลาดของเบต้า": beta_err,
        "exposureที่เหลือจริง": residual,
        "ความเร็วที่alphaเสื่อม": decay,
        "turnoverControl": {"_อ่านว่า": "λ = สัดส่วนของระยะทางที่เดินไปหาพอร์ตเป้าหมายในแต่ละวัน "
                                          "(1.0 = ไปถึงเป้าทุกวัน · 0.1 = ขยับทีละ 10%)",
                            "สัญญาณเร็ว": {"ที่ลอง": grid, "ดีที่สุด": best, "ไม่คุมเลย": none_band,
                                            "กำไรสุทธิเปลี่ยนไปเปอร์เซ็นต์": round(best["กำไรสุทธิเปอร์เซ็นต์"]
                                                                                    - none_band["กำไรสุทธิเปอร์เซ็นต์"], 3)},
                            "สัญญาณช้า": {"ที่ลอง": grid_slow, "ดีที่สุด": best_slow, "ไม่คุมเลย": grid_slow[0],
                                           "กำไรสุทธิเปลี่ยนไปเปอร์เซ็นต์": round(best_slow["กำไรสุทธิเปอร์เซ็นต์"]
                                                                                   - grid_slow[0]["กำไรสุทธิเปอร์เซ็นต์"], 3)}},
    }


if __name__ == "__main__":
    data = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("เขียน", os.path.relpath(OUT, ROOT))
