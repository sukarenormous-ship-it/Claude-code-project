"""ภาคผนวก K — เดินข้อมูลจริงโดยไม่เขียนโค้ด (ปลั๊กอินของ tools/sab_figures.py · ลงใต้ data["realdata"])

อ่าน docs/sab-data/btc-eth-daily.csv (สร้างโดย tools/sab_realdata.py จากไฟล์ดิบ Binance/Kraken ที่ไม่แก้)
แล้วคิดทุกตัวเลขของหน้า docs/sab-appendix-realdata.html ด้วย Decimal จากสตริงราคาในไฟล์ (ไม่มีเลขพิมพ์ลอย)

ข้อตกลงที่ตรึงไว้ก่อนดูช่วงทดสอบ (หน้า K ตอน 2 และ 4 พิมพ์ซ้ำ):
  A = BTC · B = ETH · ช่วงเลือก 2025-01-01..2025-12-31 · ช่วงทดสอบ 2026-01-01..2026-11-14
  h สองทาง: มูลค่าเท่ากันวันแรกของช่วงเลือก (BTC ÷ ETH) · ขยับรวมด้วยมือ (Σ|ΔBTC| ÷ Σ|ΔETH| ของช่วงเลือก แบบบท 11)
  ปัดเป็นจำนวนเต็ม · ถ้าสองทางห่างกันไม่เกิน 20% ใช้ทางมูลค่าเท่ากัน มิฉะนั้นใช้ทางข้อมูล
  X = BTC − h × ETH · ไม้บรรทัด = Mean และ STDEV (n − 1) ของ X ในช่วงเลือก
  การ์ด: ขนาด 0.01 ชุด · เข้าเมื่อ Z-score ข้ามจากข้างในไปถึง ≥ 2 (short X) หรือ ≤ −2 (long X) · ออกเมื่อถึง Mean
  ครบ 30 วันหลังได้ราคาเข้า · งบขาดทุนสุทธิ (รวมค่าธรรมเนียมเข้าและค่าออกโดยประมาณ) = 0.01 × SD · ลำดับ งบ → สัญญาณ → เวลา
  ออกเพราะงบแล้วไม่เปิดไม้ใหม่ (การ์ดบท 12 บรรทัด 6) · taker 0.05% ของมูลค่าแต่ละ fill (ฐานต้นทุนเดียวของบท 11–15)
  ตัดสินที่ราคาปิดวัน t ได้ราคาที่ราคาปิดวัน t + 1 · เงินทุกช่องปัดเป็นเซนต์แบบ exchange
การเปลี่ยนหนึ่งข้อ (เขียนก่อนรัน): ไม้บรรทัดจาก 90 วันสุดท้ายของช่วงเลือก ที่เหลือคงเดิม · เป็นการดูครั้งที่สองบนช่วงทดสอบเดิม
"""

import csv
import os
from decimal import Decimal, ROUND_HALF_UP

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        "docs", "sab-data", "btc-eth-daily.csv")
FORM_END, TEST_START = "2025-12-31", "2026-01-01"
SIZE = Decimal("0.01")
FEE = Decimal("0.0005")
ENTRY_Z, TIME_LIMIT, AGREE_PCT, WINDOW = 2, 30, 20, 90
CENT = Decimal("0.01")


def cents(x):
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


def read_csv():
    meta, rows = {}, []
    with open(CSV_PATH, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for ln in lines:
        if ln.startswith("# ") and ": " in ln:
            k, v = ln[2:].split(": ", 1)
            meta[k] = v
    body = [ln for ln in lines if ln and not ln.startswith("#")]
    for d, a, b in csv.reader(body[1:]):
        rows.append((d, Decimal(a), Decimal(b)))
    return meta, rows


def mean(xs):
    return sum(xs) / len(xs)


def stdev(xs):
    m = mean(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)).sqrt()


def count_sd(xs):
    """SD แบบนับของบท 9: เรียงระยะจาก Mean · ขอบแถบอยู่กึ่งกลางระยะลำดับที่ ⌈2n/3⌉ กับลำดับถัดไป"""
    m = mean(xs)
    dist = sorted(abs(x - m) for x in xs)
    k = round(len(xs) * 2 / 3)                      # 10 วัน → 7 · 365 วัน → 243
    return (dist[k - 1] + dist[k]) / 2, dist, k


def walk(rows, X, m, sd, h, test_idx, capital=Decimal(1000)):
    """เดินช่วงทดสอบตามการ์ดทีละวัน: (1) ทำคำสั่งที่ตัดสินเมื่อวานที่ราคาปิดวันนี้ (2) ตีมูลค่าบัญชีที่ราคาปิดวันนี้
    (3) ตัดสินคำสั่งของพรุ่งนี้จากราคาปิดวันนี้ · คืน dict ของสัญญาณ ไม้ ชุด equity รายวัน และ drawdown"""
    Z = [(x - m) / sd for x in X]
    budget = cents(SIZE * sd)
    qty = {"A": SIZE, "B": SIZE * h}
    st = {"cash": capital, "A": Decimal(0), "B": Decimal(0)}
    pos, pending, halted = None, None, False
    signals, trades, equity = [], [], []

    def px(leg, j):
        return rows[j][1] if leg == "A" else rows[j][2]

    def mark(j):
        return st["cash"] + sum((1 if st[g] >= 0 else -1) * cents(abs(st[g]) * px(g, j)) for g in "AB")

    def fill(sides, j):
        """sides = {"A": ±1, "B": ±1} (+1 ซื้อ · −1 ขาย) ที่ราคาปิดวัน j · ขาที่ขายทำก่อน เงินสดจึงไม่ติดลบระหว่างทาง (บท 11)"""
        steps = []
        for g in sorted("AB", key=lambda g: sides[g]):
            s, p = sides[g], px(g, j)
            v = cents(qty[g] * p)
            f = cents(v * FEE)
            st["cash"] += -s * v - f
            st[g] += s * qty[g]
            steps.append({"วัน": rows[j][0], "ขา": g, "ทำ": "ซื้อ" if s > 0 else "ขาย", "จำนวน": float(qty[g]),
                          "ราคา": float(p), "มูลค่า": float(v), "ค่าธรรมเนียม": float(f), "เงินสดหลัง": float(st["cash"]),
                          "ถือA": float(st["A"]), "ถือB": float(st["B"]),
                          "มูลค่าA": float((1 if st["A"] >= 0 else -1) * cents(abs(st["A"]) * rows[j][1])),
                          "มูลค่าB": float((1 if st["B"] >= 0 else -1) * cents(abs(st["B"]) * rows[j][2])),
                          "equityหลัง": float(mark(j))})
        return steps

    for n, i in enumerate(test_idx):
        last = n == len(test_idx) - 1
        if pending and pending[0] == "เข้า":
            _, side, sig_i = pending
            eq0 = st["cash"]
            pos = {"side": side, "sig_i": sig_i, "fill_i": i, "equity_before": eq0,
                   "steps": fill({"A": side, "B": -side}, i)}
        elif pending and pending[0] == "ออก":
            _, why, dec_i, net_dec = pending
            side = pos["side"]
            steps = fill({"A": -side, "B": side}, i)
            fi = pos["fill_i"]
            ga = side * (cents(qty["A"] * rows[i][1]) - cents(qty["A"] * rows[fi][1]))
            gb = -side * (cents(qty["B"] * rows[i][2]) - cents(qty["B"] * rows[fi][2]))
            fees = sum(Decimal(str(x["ค่าธรรมเนียม"])) for x in pos["steps"] + steps)
            trades.append({
                "ฝั่ง": "long X" if side > 0 else "short X",
                "วันสัญญาณ": rows[pos["sig_i"]][0], "zสัญญาณ": float(round(Z[pos["sig_i"]], 2)),
                "Xสัญญาณ": float(X[pos["sig_i"]]),
                "วันเข้า": rows[fi][0], "Xเข้า": float(X[fi]), "zเข้า": float(round(Z[fi], 2)),
                "Aเข้า": float(rows[fi][1]), "Bเข้า": float(rows[fi][2]),
                "วันตัดสินออก": rows[dec_i][0], "เหตุ": why, "zตัดสิน": float(round(Z[dec_i], 2)),
                "Xตัดสิน": float(X[dec_i]), "สุทธิถ้าปิดวันตัดสิน": float(net_dec), "วันถือ": i - fi,
                "วันออก": rows[i][0], "Xออก": float(X[i]), "zออก": float(round(Z[i], 2)),
                "Aออก": float(rows[i][1]), "Bออก": float(rows[i][2]),
                "ขาA": float(ga), "ขาB": float(gb), "กำไรจากราคา": float(ga + gb),
                "ผ่านX": float(cents(side * SIZE * (X[i] - X[fi]))),
                "ค่าธรรมเนียม": float(fees), "สุทธิ": float(ga + gb - fees),
                "equityก่อน": float(pos["equity_before"]), "equityหลัง": float(st["cash"]),
                "fill": pos["steps"] + steps,
            })
            pos = None
        pending = None
        equity.append(mark(i))
        if last:
            if pos is None and not halted:
                zp, z = Z[i - 1], Z[i]
                if abs(zp) < ENTRY_Z <= abs(z):
                    signals.append({"วัน": rows[i][0], "z": float(round(z, 2)), "X": float(X[i]), "ทำได้": False})
            break
        if pos is not None:
            side = pos["side"]
            exit_fee = sum(cents(cents(qty[g] * px(g, i)) * FEE) for g in "AB")
            net_now = mark(i) - pos["equity_before"] - exit_fee
            why = None
            if net_now <= -budget:
                why = "งบ"
            elif (side < 0 and Z[i] <= 0) or (side > 0 and Z[i] >= 0):
                why = "สัญญาณ"
            elif i - pos["fill_i"] >= TIME_LIMIT:
                why = "เวลา"
            if why:
                pending = ("ออก", why, i, net_now)
                halted = halted or why == "งบ"
        elif not halted:
            zp, z = Z[i - 1], Z[i]
            if abs(zp) < ENTRY_Z <= abs(z):
                signals.append({"วัน": rows[i][0], "z": float(round(z, 2)), "X": float(X[i]), "ทำได้": True})
                pending = ("เข้า", -1 if z > 0 else 1, i)
    peak, dd, dd_from, dd_to, peak_i = equity[0], Decimal(0), None, None, test_idx[0]
    for n, e in enumerate(equity):
        if e > peak:
            peak, peak_i = e, test_idx[n]
        if e - peak < dd:
            dd, dd_from, dd_to = e - peak, peak_i, test_idx[n]
    return {"Z": Z, "budget": budget, "signals": signals, "trades": trades, "equity": equity, "open": pos,
            "dd": dd, "dd_from": dd_from, "dd_to": dd_to}


def extend(data, D, q):
    meta, rows = read_csv()
    dates = [r[0] for r in rows]
    F = [i for i, d in enumerate(dates) if d <= FORM_END]
    T = [i for i, d in enumerate(dates) if d >= TEST_START]

    # ── ตอน 1: หนึ่งแถว และการตรวจ ──
    drop = meta["dropped_A"].split()
    drop_b = meta["dropped_B"].split()
    kr = {}
    for leg in "AB":
        parts = meta[f"check_kraken_{leg}"].split(" · ")
        med = Decimal(parts[2].split("มัธยฐาน ")[1].rstrip("%"))
        mx_s, mx_day = parts[3].split("มากสุด ")[1].split(" (")
        kr[leg] = {"วัน": int(parts[1].split()[0]), "มัธยฐาน": q(med, 2), "มากสุด": q(Decimal(mx_s.rstrip("%")), 2),
                   "มัธยฐานเต็ม": float(med), "มากสุดเต็ม": float(Decimal(mx_s.rstrip("%"))), "วันมากสุด": mx_day.rstrip(")")}
    first = rows[0]
    one_row = {"วัน": first[0], "BTC": float(first[1]), "ETH": float(first[2]),
               "เวลาเปิดms": 1735689600000, "เวลาปิดms": 1735775999999, "ห่างแท่งms": 86400000}

    # ── ตอน 2: h สองทาง (ใช้เฉพาะช่วงเลือก) ──
    fa = [rows[i][1] for i in F]
    fb = [rows[i][2] for i in F]
    h_eq = fa[0] / fb[0]
    move_a = sum(abs(fa[k] - fa[k - 1]) for k in range(1, len(fa)))
    move_b = sum(abs(fb[k] - fb[k - 1]) for k in range(1, len(fb)))
    h_data = move_a / move_b
    h_eq_r, h_data_r = int(h_eq.quantize(D(1), rounding=ROUND_HALF_UP)), int(h_data.quantize(D(1), rounding=ROUND_HALF_UP))
    gap_pct = abs(h_eq - h_data) / h_eq * 100
    h = h_eq_r if gap_pct <= AGREE_PCT else h_data_r
    X = [a - h * b for _, a, b in rows]
    X_eq = [a - h_eq_r * b for _, a, b in rows]

    # ── ตอน 3: ไม้บรรทัด ──
    fx = [X[i] for i in F]
    m, sd = mean(fx), stdev(fx)
    csd, dist_all, k_all = count_sd(fx)
    ex = F[-10:]
    exx = [X[i] for i in ex]
    m10 = cents(mean(exx))                      # ผู้อ่านใช้ Mean ที่ปัดแล้ว ระยะทุกแถวจึงลงตัวสองตำแหน่ง
    dist10 = sorted(abs(x - m10) for x in exx)
    k10 = round(len(exx) * 2 / 3)
    csd10 = (dist10[k10 - 1] + dist10[k10]) / 2
    excerpt = {
        "แถว": [{"วัน": dates[i], "BTC": float(rows[i][1]), "ETH": float(rows[i][2]), "hETH": float(h * rows[i][2]),
                 "X": float(X[i]), "ห่าง": float(X[i] - m10), "ระยะ": float(abs(X[i] - m10))} for i in ex],
        "ผลรวม": float(sum(exx)), "Mean": float(m10), "ระยะเรียง": [float(x) for x in dist10],
        "ลำดับ": k10, "ลำดับถัดไป": k10 + 1, "SDนับ": q(csd10, 2), "STDEV": q(stdev(exx), 2),
        "SDนับห่างเปอร์เซ็นต์": q((csd10 - stdev(exx)) / stdev(exx) * 100, 0),
        "วันแรก": dates[ex[0]], "วันสุดท้าย": dates[ex[-1]],
    }
    zs_f = [(x - m) / sd for x in fx]
    ruler = {
        "Mean": q(m, 2), "SD": q(sd, 2), "SDนับ": q(csd, 2), "ลำดับนับ": k_all, "วัน": len(F),
        "ผลรวม": q(sum(fx), 2), "Meanเต็ม": str(m.quantize(D("0.000001"))), "SDเต็ม": str(sd.quantize(D("0.000001"))),
        "Xต่ำสุด": float(min(fx)), "Xสูงสุด": float(max(fx)),
        "วันXต่ำสุด": dates[F[fx.index(min(fx))]], "วันXสูงสุด": dates[F[fx.index(max(fx))]],
        "เส้นบน": q(m + 2 * sd, 2), "เส้นล่าง": q(m - 2 * sd, 2), "สองSD": q(2 * sd, 2),
        "ในกรอบเปอร์เซ็นต์": q(D(sum(1 for z in zs_f if abs(z) <= 2)) / len(F) * 100, 1),
        "Xวันแรก": float(X[F[0]]), "Xวันสุดท้าย": float(X[F[-1]]),
        "zวันสุดท้าย": q((X[F[-1]] - m) / sd, 2),
    }
    # ไม้บรรทัดของ h อีกทาง (ใช้ในแบบฝึกข้อ 2 และ 🔎)
    fxe = [X_eq[i] for i in F]
    m_e, sd_e = mean(fxe), stdev(fxe)

    # φ ด้วยมือแบบบท 13 (ระยะจาก Mean ของช่วงเลือก)
    dev = [x - m for x in fx]
    num = sum(dev[k] * dev[k + 1] for k in range(len(dev) - 1))
    den = sum(dev[k] * dev[k] for k in range(len(dev) - 1))
    phi = num / den
    hl, p_ = 0, D(1)
    while p_ > D("0.5"):
        p_ *= phi
        hl += 1

    # ── ตอน 4: เดินช่วงทดสอบ (ตามที่ตรึงไว้) ──
    main = walk(rows, X, m, sd, h, T)
    zt = [main["Z"][i] for i in T]
    zmin_i, zmax_i = T[zt.index(min(zt))], T[zt.index(max(zt))]
    test = {
        "วัน": len(T), "zต่ำสุด": q(min(zt), 2), "zสูงสุด": q(max(zt), 2),
        "วันzต่ำสุด": dates[zmin_i], "Xที่zต่ำสุด": float(X[zmin_i]), "วันzสูงสุด": dates[zmax_i], "Xที่zสูงสุด": float(X[zmax_i]),
        "ยังขาดถึงเส้นล่าง": q(min(zt) + 2, 2), "ยังขาดถึงเส้นล่างดอลลาร์": q(X[zmin_i] - (m - 2 * sd), 2),
        "ในกรอบวัน": sum(1 for z in zt if abs(z) <= 2), "ในกรอบเปอร์เซ็นต์": q(D(sum(1 for z in zt if abs(z) <= 2)) / len(T) * 100, 1),
        "สัญญาณ": len(main["signals"]), "ไม้": len(main["trades"]), "สุทธิ": q(sum(D(str(t["สุทธิ"])) for t in main["trades"]), 2),
        "equityจบ": float(main["equity"][-1]), "drawdown": float(main["dd"]),
        "งบ": float(main["budget"]),
        "Xวันสุดท้าย": float(X[T[-1]]), "zวันสุดท้าย": q(main["Z"][T[-1]], 2),
        "zต่ำสุดถ้าh28": q(min((X_eq[i] - m_e) / sd_e for i in T), 2),
        "zสูงสุดถ้าh28": q(max((X_eq[i] - m_e) / sd_e for i in T), 2),
        "สัญญาณถ้าh28": len(walk(rows, X_eq, m_e, sd_e, h_eq_r, T)["signals"]),
    }

    # ── การเปลี่ยนหนึ่งข้อ: ไม้บรรทัด 90 วันสุดท้าย (ดูครั้งที่สอง) ──
    W = F[-WINDOW:]
    wx = [X[i] for i in W]
    m90, sd90 = mean(wx), stdev(wx)
    alt = walk(rows, X, m90, sd90, h, T)
    zt90 = [alt["Z"][i] for i in T]
    tr = alt["trades"]
    total_net = sum(D(str(t["สุทธิ"])) for t in tr)
    explore = {
        "วันแรก": dates[W[0]], "วันสุดท้าย": dates[W[-1]], "วัน": len(W),
        "Mean": q(m90, 2), "SD": q(sd90, 2), "Meanเต็ม": str(m90.quantize(D("0.000001"))), "SDเต็ม": str(sd90.quantize(D("0.000001"))),
        "เส้นบน": q(m90 + 2 * sd90, 2), "เส้นล่าง": q(m90 - 2 * sd90, 2), "สองSD": q(2 * sd90, 2),
        "งบ": float(alt["budget"]),
        "ในกรอบเปอร์เซ็นต์": q(D(sum(1 for z in zt90 if abs(z) <= 2)) / len(T) * 100, 1),
        "สัญญาณ": alt["signals"], "จำนวนสัญญาณ": len(alt["signals"]),
        "ไม้": tr, "จำนวนไม้": len(tr),
        "ชนะ": sum(1 for t in tr if t["สุทธิ"] > 0), "แพ้": sum(1 for t in tr if t["สุทธิ"] <= 0),
        "สุทธิรวม": q(total_net, 2), "ค่าธรรมเนียมรวม": q(sum(D(str(t["ค่าธรรมเนียม"])) for t in tr), 2),
        "กำไรจากราคารวม": q(sum(D(str(t["กำไรจากราคา"])) for t in tr), 2),
        "equityจบ": float(alt["equity"][-1]), "drawdown": float(alt["dd"]),
        "ddจาก": dates[alt["dd_from"]] if alt["dd_from"] is not None else None,
        "ddถึง": dates[alt["dd_to"]] if alt["dd_to"] is not None else None,
        "ต่อทุนเปอร์เซ็นต์": q(total_net / 10, 2),
        "เฉลี่ยต่อไม้": q(total_net / len(tr), 2) if tr else 0,
        "ddยอด": float(max(alt["equity"][:[k for k, i in enumerate(T) if i == alt["dd_to"]][0] + 1])) if alt["dd_to"] else None,
        "ddก้น": float(alt["equity"][[k for k, i in enumerate(T) if i == alt["dd_to"]][0]]) if alt["dd_to"] else None,
        "เปิดค้าง": alt["open"] is not None,
    }
    if tr:
        t1 = tr[0]
        explore["ไม้1"] = {
            "เข้าXคิด": q(D(str(t1["Aเข้า"])) - h * D(str(t1["Bเข้า"])), 2),
            "hBเข้า": float(h * D(str(t1["Bเข้า"]))), "hBออก": float(h * D(str(t1["Bออก"]))),
            "ส่วนต่างสองวิธี": q(D(str(t1["กำไรจากราคา"])) - D(str(t1["ผ่านX"])), 2),
            "ขยับX": float(D(str(t1["Xออก"])) - D(str(t1["Xเข้า"]))),
            "zเป้า": 0,
            "Xขยับก่อนได้ราคา": float(D(str(t1["Xเข้า"])) - D(str(t1["Xสัญญาณ"]))),
            "เงินที่หายก่อนได้ราคา": float(cents(SIZE * (D(str(t1["Xเข้า"])) - D(str(t1["Xสัญญาณ"]))))),
            "ค่าเข้า": float(sum(D(str(x["ค่าธรรมเนียม"])) for x in t1["fill"][:2])),
            "ค่าออก": float(sum(D(str(x["ค่าธรรมเนียม"])) for x in t1["fill"][2:])),
        }
        # ถ้าทำได้ที่ราคาปิดวันสัญญาณ (อคติมองล่วงหน้า) — แบบฝึกข้อ 3
        si = dates.index(t1["วันสัญญาณ"])
        di = dates.index(t1["วันตัดสินออก"])
        side = 1 if t1["ฝั่ง"] == "long X" else -1
        va = lambda i: cents(SIZE * rows[i][1])       # noqa: E731
        vb = lambda i: cents(SIZE * h * rows[i][2])   # noqa: E731
        g = side * (va(di) - va(si)) - side * (vb(di) - vb(si))
        fees = sum(cents(v * FEE) for v in (va(si), vb(si), va(di), vb(di)))
        explore["ไม้1"]["มองล่วงหน้า"] = {"กำไรจากราคา": float(g), "ค่าธรรมเนียม": float(fees), "สุทธิ": float(g - fees),
                                         "ต่างจากจริง": float(g - fees - D(str(t1["สุทธิ"])))}

    # การ์ดที่ตรึงไว้สำหรับรอบหน้า: ไม้บรรทัด 90 วันล่าสุดของไฟล์ (ใช้กับข้อมูลหลังวันสุดท้ายเท่านั้น)
    N = list(range(len(rows)))[-WINDOW:]
    nx = [X[i] for i in N]
    mn, sdn = mean(nx), stdev(nx)
    nxt = {"วันแรก": dates[N[0]], "วันสุดท้าย": dates[N[-1]], "Mean": q(mn, 2), "SD": q(sdn, 2),
           "เส้นบน": q(mn + 2 * sdn, 2), "เส้นล่าง": q(mn - 2 * sdn, 2), "งบ": float(cents(SIZE * sdn)),
           "zวันสุดท้าย": q((X[-1] - mn) / sdn, 2)}

    # ตัวเลขกลางทางที่หน้าพิมพ์ (ตามที่มาได้ในหน้า) และแนวคำตอบ ✍️
    r0, rL, rT = rows[0], rows[F[-1]], rows[T[0]]
    t1 = tr[0] if tr else None
    mid = {
        "แถวแรกhETH": float(h * r0[2]), "จำนวนการขยับ": len(F) - 1,
        "ปลายช่วงเลือกห่างMean": q(X[F[-1]] - m, 2),
        "ข้อ1ห่างMean": q(X[T[0]] - m, 2),
        "ข้อ2ห่างMean": q(X_eq[T[0]] - m_e, 2),
        "ข้อ3Xขยับ": float(X[dates.index(t1["วันตัดสินออก"])] - X[dates.index(t1["วันสัญญาณ"])]) if t1 else None,
        "ไม้1ช่วงที่ถือXต่ำสุด": float(min(X[dates.index(t1["วันเข้า"]):dates.index(t1["วันออก"]) + 1])) if t1 else None,
    }

    def series(vals, nd):
        return [q(v, nd) if nd else int(v.quantize(D(1), rounding=ROUND_HALF_UP)) for v in vals]

    ex_rows = {}
    for nm, idx in (("ปลายช่วงเลือก", F[-1]), ("ต้นช่วงทดสอบ", T[0])):
        ex_rows[nm] = {"วัน": dates[idx], "BTC": float(rows[idx][1]), "ETH": float(rows[idx][2]),
                       "hETH": float(h * rows[idx][2]), "X": float(X[idx]),
                       "z": q((X[idx] - m) / sd, 2), "z90": q((X[idx] - m90) / sd90, 2),
                       "h28ETH": float(h_eq_r * rows[idx][2]), "Xh28": float(X_eq[idx]),
                       "zh28": q((X_eq[idx] - m_e) / sd_e, 2)}

    return {
        "แหล่ง": {
            "ปีเริ่ม": 2025, "ปีจบ": 2026, "แถวดิบ": int(meta["raw_rows_A"]), "แถว": len(rows),
            "วันช่วงเลือก": len(F), "วันช่วงทดสอบ": len(T), "ดึงเมื่อ": meta["fetched_A_utc"],
            "ตัด": {"วัน": drop[0], "เวลาปิด": drop[2], "BTCตอนดึง": float(D(drop[-1].rstrip(")"))),
                    "ETHตอนดึง": float(D(drop_b[-1].rstrip(")")))},
            "kraken": kr, "แถวแรก": one_row,
            "วันสุดท้าย": dates[-1], "BTCวันสุดท้าย": float(rows[-1][1]), "ETHวันสุดท้าย": float(rows[-1][2]),
        },
        "h": {
            "มูลค่าเท่ากัน": q(h_eq, 2), "มูลค่าเท่ากันปัด": h_eq_r, "มูลค่าเท่ากันเต็ม": str(h_eq.quantize(D("0.000001"))),
            "BTCขยับรวม": float(move_a), "ETHขยับรวม": float(move_b),
            "ข้อมูล": q(h_data, 2), "ข้อมูลปัด": h_data_r, "ข้อมูลเต็ม": str(h_data.quantize(D("0.000001"))),
            "ห่างเปอร์เซ็นต์": q(gap_pct, 1), "เกณฑ์เปอร์เซ็นต์": AGREE_PCT, "เลือก": h,
            "ETHต่อขนาด": float(SIZE * h), "ETHต่อขนาดh28": float(SIZE * h_eq_r),
            "วันแรกBTC": float(fa[0]), "วันแรกETH": float(fb[0]),
            "วันแรกขาA": float(cents(SIZE * fa[0])), "วันแรกขาB": float(cents(SIZE * h * fb[0])),
            "วันแรกขาBh28": float(cents(SIZE * h_eq_r * fb[0])),
        },
        "ไม้บรรทัด": ruler, "ตัวอย่างสิบวัน": excerpt,
        "ไม้บรรทัดh28": {"Mean": q(m_e, 2), "SD": q(sd_e, 2)},
        "phi": {"ค่า": q(phi, 2), "เต็ม": str(phi.quantize(D("0.000001"))), "halflife": hl},
        "การ์ด": {"ขนาด": float(SIZE), "เข้า": ENTRY_Z, "ออก": 0, "เวลา": TIME_LIMIT, "ค่าธรรมเนียม": float(FEE * 100),
                  "งบ": float(main["budget"]), "งบ90": float(alt["budget"]), "fillต่อไม้": 4, "หน้าต่าง": WINDOW},
        "ทดสอบ": test, "สำรวจ90": explore, "แถวตัวอย่าง": ex_rows, "รอบหน้า": nxt, "กลางทาง": mid,
        "เทียบ": {"บท9ไม่มีเชือก": data["ch09"]["ไม่มีเชือก"]["ในกรอบ"], "บท9มีเชือก": data["ch09"]["มีเชือก"]["ในกรอบ"]},
        "ชุดกราฟ": {
            "X": series(X, 0), "equity90": series(alt["equity"], 1), "equity": series(main["equity"], 1),
            "iทดสอบเริ่ม": T[0], "iหน้าต่างเริ่ม": W[0],
            "แกนX": list(range(20000, 70001, 10000)), "แกนequity": list(range(960, 1011, 10)),
            "เดือน": [{"i": i, "ป้าย": ["ม.ค.", "เม.ย.", "ก.ค.", "ต.ค."][(int(d[5:7]) - 1) // 3] + (" " + d[:4] if d[5:7] == "01" else "")}
                      for i, d in enumerate(dates) if d[8:] == "01" and d[5:7] in ("01", "04", "07", "10")],
        },
    }
