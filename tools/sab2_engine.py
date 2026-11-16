#!/usr/bin/env python3
"""เครื่อง backtest กลางของเล่ม 2 (stdlib) · shared pair backtest engine for volume 2 (บท 13 เป็นต้นไป)

วงห้าขั้นต่อวัน t (five-step event loop, one pass per close):
  1) รู้อะไร   ค่าสัญญาณของวัน t − lag (data known at the signal close; lag 0 = แอบดูอนาคต)
  2) สัญญาณ    rule(z, held) → ทิศที่อยาก (+1 long X · −1 short X · 0 ว่าง) + เวลาถือเกิน hold / ขาดทุนเกินงบ → ปิด
  3) คำสั่ง    qa = Δทิศ × sets (ขา A) · qb = −Δทิศ × sets × h (ขา B)
  4) fill      ราคาปิดวัน t · ค่าธรรมเนียม fee × มูลค่าที่ซื้อขาย (ฐานเดียวของเล่ม 1: taker 0.05% ต่อ fill)
  5) ลงบัญชี  เงินสด · จำนวนที่ถือแต่ละขา · Equity = เงินสด + มูลค่าที่ถือ ณ ราคาปิด · ค่าธรรมเนียมสะสม

    from sab2_engine import run
    r = run(A, B, h, z, sets=0.01)                 # fill ราคาปิดวันถัดไป (ค่าเริ่มต้น)
    print(r["trades"], r["wins"], round(r["net"], 2), round(r["max_drawdown"], 2))

fill: "next" (lag 1 · ค่าเริ่มต้น) · "same" (lag 0 · result["lookahead"] = True — โกง ใช้สาธิตเท่านั้น) · lag=N (N ≥ 1)
signal: list ยาวเท่าราคา หรือฟังก์ชัน signal(t) → ค่าที่รู้ ณ ปิดวัน t · rule: ฟังก์ชัน rule(z, held) → ทิศใหม่
(ค่าเริ่มต้น threshold_rule(enter, leave): ว่าง & |z| ≥ enter → สวนทิศ z · ถือ & |z| ≤ leave → ปิด)

h เปลี่ยนทุกวัน (บท 5 rolling · บท 6 Kalman): run_hpath(A, B, hs, z, sets, rebalance=True, band=0.0) — ปรับขา B ตาม h ใหม่
ระหว่างถือ (ค่าธรรมเนียมแยกเป็น costs_rebalance) · บัญชีตามจำนวนที่ถือจริง · price_pnl / chart_pnl / redefinition

    python3 tools/sab2_engine.py --selftest
"""

import math
import random
import sys

FEE = 0.0005          # 0.05% ของมูลค่าต่อ fill (taker · ฐานต้นทุนเดียวของเล่ม 1 บท 11)
CAPITAL = 1000.0      # ทุนคู่ของเล่ม 1
REASON_TH = {"enter": "เข้า", "target": "เป้า", "time": "เวลา", "loss": "งบขาดทุน"}


def threshold_rule(enter=2.0, leave=0.5):
    """กฎเส้นของเล่ม 1: เข้าเมื่อ |z| ≥ enter (สวนทิศ z) · ออกเมื่อ |z| ≤ leave"""
    def rule(z, held):
        if held == 0 and abs(z) >= enter:
            return -1 if z > 0 else 1
        if held != 0 and abs(z) <= leave:
            return 0
        return held
    return rule


def run(A, B, h, signal, sets=1.0, capital=CAPITAL, rule=None, fill="next", lag=None, fee=FEE,
        enter=2.0, leave=0.5, hold=30, loss_budget=None):
    """เดินวงห้าขั้นบนคู่ X = A − h·B · คืน dict สรุป (ดู docstring ของโมดูล)
    hold = ถือได้ไม่เกินกี่วัน (None = ไม่จำกัด) · loss_budget = ปิดเมื่อไม้ที่ถือขาดทุน ≥ ค่านี้ (คิดที่ราคาปิดวันสัญญาณ)"""
    if lag is None:
        lag = {"next": 1, "same": 0}[fill]
    rule = rule or threshold_rule(enter, leave)
    sig = signal if callable(signal) else signal.__getitem__
    cash, held, t_in, before, costs = float(capital), 0, 0, None, 0.0
    equity, ledger, fills, trades = [], [], [], []
    for t in range(len(A)):
        if t >= lag:
            s = t - lag
            zt = sig(s)                                              # 1) รู้อะไร
            want = rule(zt, held)                                    # 2) สัญญาณ
            why = "enter" if held == 0 else "target"
            if held != 0 and want == held:
                if hold is not None and t - t_in >= hold:
                    want, why = 0, "time"
                elif loss_budget is not None and \
                        cash + held * sets * (A[s] - h * B[s]) - before <= -loss_budget:
                    want, why = 0, "loss"
            if want != held:                                         # 3) คำสั่ง  4) fill ราคาปิดวัน t
                if held == 0:
                    before = cash
                qa, qb = (want - held) * sets, -(want - held) * sets * h
                f = fee * (abs(qa) * A[t] + abs(qb) * B[t])
                cash -= qa * A[t] + qb * B[t] + f
                costs += f
                fills.append({"t": t, "side": want, "A": A[t], "B": B[t], "fee": f, "cash": cash, "reason": why,
                              "signal": zt, "signal_t": s})
                if held != 0:
                    trades.append({"side": held, "t_in": t_in, "t_out": t, "pnl": cash - before, "reason": why})
                    if want != 0:                                    # กลับทิศในคำสั่งเดียว = ปิดแล้วเปิดใหม่
                        before = cash
                held, t_in = want, t
        eq = cash + held * sets * (A[t] - h * B[t])                  # 5) ลงบัญชี
        equity.append(eq)
        ledger.append({"t": t, "cash": cash, "units_A": held * sets, "units_B": -held * sets * h, "equity": eq,
                       "costs": costs})
    peak, mdd = float(capital), 0.0
    for e in equity:
        peak = max(peak, e)
        mdd = max(mdd, peak - e)
    return {"equity": equity, "ledger": ledger, "fill_list": fills, "trade_list": trades,
            "fills": len(fills), "trades": len(trades), "wins": sum(1 for x in trades if x["pnl"] > 0),
            "net": (equity[-1] if equity else capital) - capital, "costs": costs, "max_drawdown": mdd,
            "min_equity": min(equity) if equity else capital, "open": held, "lag": lag, "lookahead": lag == 0}


def run_hpath(A, B, hs, signal, sets=1.0, capital=CAPITAL, fill="next", lag=None, fee=FEE, enter=2.0, leave=0.5,
              hold=30, rebalance=True, band=0.0):
    """วงห้าขั้นเดียวกับ run แต่ h เปลี่ยนได้ทุกวัน (เล่ม 2 บท 5 · rolling h / Kalman) · time-varying hedge ratio
    hs[t] = h ที่รู้ ณ ปิดวัน t (None = ยังไม่มี → ไม่เปิดไม้ใหม่) · คำสั่งวัน t ใช้ hs[t − lag] เหมือนสัญญาณ
    เข้า: A +ทิศ×sets · B −ทิศ×sets×h · ระหว่างถือ rebalance=True → ปรับขา B ให้ตรง h ใหม่ทุกวัน (จ่าย fee × มูลค่าที่ซื้อขาย)
    เมื่อ |ส่วนที่ต้องซื้อขาย| > band × |ขา B ที่ถือ| (band = กันชนไม่เทรด เป็นสัดส่วน) · ออก: ปิดทั้งสองขาตามจำนวนที่ถือจริง
    บัญชีตามจำนวนที่ถือจริง: Equity = เงินสด + qA×A + qB×B (ไม่ใช่ ชุด × X ใหม่)
    คืนเหมือน run + costs_trade (ค่าธรรมเนียมเข้า/ออก) · costs_rebalance · rebalances (จำนวนครั้งที่ปรับ) ·
    price_pnl (Σ จำนวนที่ถือก่อนราคาขยับ × ราคาที่ขยับ = เงินจริงก่อนค่าธรรมเนียม) · chart_pnl (Σ ทิศเมื่อวาน × sets ×
    การเปลี่ยนของ X ที่วาดด้วย h ของแต่ละวัน = backtest แบบไร้เดียงสา) · redefinition = chart_pnl − price_pnl"""
    if lag is None:
        lag = {"next": 1, "same": 0}[fill]
    rule = threshold_rule(enter, leave)
    sig = signal if callable(signal) else signal.__getitem__
    hof = hs if callable(hs) else hs.__getitem__
    cash, held, t_in, before = float(capital), 0, 0, None
    qa = qb = 0.0
    c_trade = c_reb = 0.0
    n_reb, price_pnl, chart_pnl = 0, 0.0, 0.0
    equity, ledger, fills, trades = [], [], [], []
    held_prev, x_prev = 0, None
    for t in range(len(A)):
        if t > 0:
            price_pnl += qa * (A[t] - A[t - 1]) + qb * (B[t] - B[t - 1])
        ht = hof(t)
        x_now = None if ht is None else A[t] - ht * B[t]
        if held_prev != 0 and x_prev is not None and x_now is not None:
            chart_pnl += held_prev * sets * (x_now - x_prev)
        if t >= lag:
            s = t - lag
            zt, hsig = sig(s), hof(s)
            want = held if zt is None else rule(zt, held)
            if held == 0 and hsig is None:
                want = 0
            why = "enter" if held == 0 else "target"
            if held != 0 and want == held and hold is not None and t - t_in >= hold:
                want, why = 0, "time"
            if want != held:
                if held == 0:
                    before = cash
                ta = want * sets
                tb = -want * sets * hsig if want != 0 else 0.0
                da, db = ta - qa, tb - qb
                f = fee * (abs(da) * A[t] + abs(db) * B[t])
                cash -= da * A[t] + db * B[t] + f
                c_trade += f
                qa, qb = ta, tb
                fills.append({"t": t, "side": want, "A": A[t], "B": B[t], "h": hsig, "fee": f, "cash": cash,
                              "reason": why, "signal": zt, "signal_t": s})
                if held != 0:
                    trades.append({"side": held, "t_in": t_in, "t_out": t, "pnl": cash - before, "reason": why})
                    if want != 0:
                        before = cash
                held, t_in = want, t
            elif held != 0 and rebalance and hsig is not None:
                db = -held * sets * hsig - qb
                if db != 0 and abs(db) > band * abs(qb):
                    f = fee * abs(db) * B[t]
                    cash -= db * B[t] + f
                    c_reb += f
                    n_reb += 1
                    qb += db
        eq = cash + qa * A[t] + qb * B[t]
        equity.append(eq)
        ledger.append({"t": t, "cash": cash, "units_A": qa, "units_B": qb, "equity": eq, "costs": c_trade + c_reb})
        held_prev, x_prev = held, x_now
    peak, mdd = float(capital), 0.0
    for e in equity:
        peak = max(peak, e)
        mdd = max(mdd, peak - e)
    return {"equity": equity, "ledger": ledger, "fill_list": fills, "trade_list": trades,
            "fills": len(fills), "trades": len(trades), "wins": sum(1 for x in trades if x["pnl"] > 0),
            "net": (equity[-1] if equity else capital) - capital, "costs": c_trade + c_reb,
            "costs_trade": c_trade, "costs_rebalance": c_reb, "rebalances": n_reb,
            "price_pnl": price_pnl, "chart_pnl": chart_pnl, "redefinition": chart_pnl - price_pnl,
            "max_drawdown": mdd, "min_equity": min(equity) if equity else capital, "open": held,
            "open_units": (qa, qb), "lag": lag, "lookahead": lag == 0}


# ═══════════════════════════ selftest ═══════════════════════════

def _reference(A, B, h, z, sets, lag=1, fee=FEE, enter=2, leave=0.5, hold=30):
    """ลูปในบล็อก 💻 ของ docs/sab2-part13.html ตรงตัว (ต้นแบบที่เครื่องต้องให้ผลเท่ากันทุกบิต)"""
    cash, held, t_in, eq, n = 1000.0, 0, 0, [], 0
    for t in range(len(A)):
        if t >= lag:
            zt, want = z[t - lag], held
            if held == 0 and abs(zt) >= enter:
                want = -1 if zt > 0 else 1
            elif held != 0 and (abs(zt) <= leave or t - t_in >= hold):
                want = 0
            if want != held:
                qa, qb = (want - held) * sets, -(want - held) * sets * h
                cash -= qa * A[t] + qb * B[t] + fee * (abs(qa) * A[t] + abs(qb) * B[t])
                held, t_in, n = want, t, n + 1
        eq.append(cash + held * sets * (A[t] - h * B[t]))
    return eq, n


def selftest():
    ok, n = True, 0

    def check(label, cond, detail=""):
        nonlocal ok, n
        n += 1
        if not cond:
            ok = False
            print(f"  ✗ {label} {detail}")

    # 1) สิบวันของบท 13 (ตอน ก): ราคาวันถัดไป 1010.96 · ราคาวันเดียวกัน 1016.96 (ตรงบรรทัดคาดหวังของหน้า)
    A = [100.6, 103.4, 106.3, 105, 103.6, 101.1, 99.4, 100.7, 100.5, 96.8]
    B = [50, 51, 52, 51.5, 51, 50, 49.5, 50, 50.5, 49]
    X = [a - 2 * b for a, b in zip(A, B)]
    r1, r0 = run(A, B, 2, X, 10), run(A, B, 2, X, 10, fill="same")
    check("สิบวัน: 1010.96 / 1016.96", (round(r1["equity"][-1], 2), round(r0["equity"][-1], 2)) == (1010.96, 1016.96),
          f"{r1['equity'][-1]} {r0['equity'][-1]}")
    check("fill same ติดป้าย lookahead · next ไม่ติด", r0["lookahead"] and not r1["lookahead"] and r1["lag"] == 1)
    check("สิบวัน: 2 fill · 1 ไม้ · ชนะ 1 · net = กำไรไม้", r1["fills"] == 2 and r1["trades"] == 1 and r1["wins"] == 1
          and abs(r1["net"] - r1["trade_list"][0]["pnl"]) < 1e-9)
    check("บัญชี: equity = เงินสด + จำนวนถือ × ราคา ทุกวัน · ค่าธรรมเนียมสะสม = ผลรวม fee",
          all(abs(row["equity"] - (row["cash"] + row["units_A"] * a + row["units_B"] * b)) < 1e-9
              for row, a, b in zip(r1["ledger"], A, B))
          and abs(r1["ledger"][-1]["costs"] - sum(f["fee"] for f in r1["fill_list"])) < 1e-12)
    # 2) เท่ากับลูปต้นแบบทุกบิต: 200 โลกสุ่ม × lag 0/1/2 × fee 0/ฐาน/สามเท่า
    rng = random.Random(12)
    same = True
    for k in range(200):
        m = rng.randint(20, 120)
        b = [50.0]
        x = [0.0]
        for _ in range(m - 1):
            b.append(b[-1] * (1 + rng.gauss(0, 0.02)))
            x.append(0.85 * x[-1] + rng.gauss(0, 1.0))
        hh = rng.choice([1, 2, 1.7])
        a = [hh * u + 3 + v for u, v in zip(b, x)]
        z = [v / 2.0 for v in x]
        lag, fee = k % 3, (0.0, FEE, 3 * FEE)[k % 3 - 1]
        eq, nf = _reference(a, b, hh, z, 0.5, lag=lag, fee=fee)
        r = run(a, b, hh, z, 0.5, lag=lag, fee=fee)
        same = same and eq == r["equity"] and nf == r["fills"]
    check("เท่าลูปในบล็อก 💻 ทุกบิต (200 โลก × lag 0/1/2 × fee)", same)
    # 3) lag ช้า: fill ช้าลง N วัน · signal เป็นฟังก์ชันได้
    r2 = run(A, B, 2, X, 10, lag=2)
    rf = run(A, B, 2, lambda t: X[t], 10)
    check("lag 2: fill แรกช้ากว่า lag 1 หนึ่งวัน · signal ฟังก์ชัน = list",
          r2["fill_list"][0]["t"] == r1["fill_list"][0]["t"] + 1 and rf["equity"] == r1["equity"])
    # 4) เวลาถือ · งบขาดทุน · drawdown
    up = [100 + 2 * t for t in range(40)]
    flat = [50.0] * 40
    zz = [3.0] * 40                                                    # สัญญาณค้างเหนือเส้น: short X ตลอด
    rt = run(up, flat, 1, zz, 1, hold=5)
    check("เวลาถือ 5 วัน: ปิดด้วยเหตุ time แล้วเข้าใหม่", rt["trade_list"][0]["reason"] == "time"
          and rt["trade_list"][0]["t_out"] - rt["trade_list"][0]["t_in"] == 5)
    rl = run(up, flat, 1, zz, 1, hold=None, loss_budget=5)
    check("งบขาดทุน 5: ปิดด้วยเหตุ loss ภายในไม่กี่วัน (คิดที่ราคาวันสัญญาณ)", rl["trade_list"][0]["reason"] == "loss"
          and rl["trade_list"][0]["t_out"] - rl["trade_list"][0]["t_in"] <= 4 and rl["trade_list"][0]["pnl"] < -5)
    rn = run(up, flat, 1, zz, 1, hold=None)
    check("max drawdown = จุดสูงสุด − จุดต่ำสุดหลังจากนั้น", abs(rn["max_drawdown"] - (1000.0 - rn["min_equity"])) < 1e-9
          and rn["max_drawdown"] > 70 and rn["open"] == -1)
    # 5) run_hpath (บท 5): h คงที่ → เท่า run · บัญชีรวมกลับ · h เปลี่ยน → แยกเงินจากราคา / ผลจากการนิยามใหม่
    rng = random.Random(5)
    agree, ident = True, True
    for k in range(60):
        m = rng.randint(30, 150)
        b, x = [50.0], [0.0]
        for _ in range(m - 1):
            b.append(b[-1] * (1 + rng.gauss(0, 0.02)))
            x.append(0.85 * x[-1] + rng.gauss(0, 1.0))
        hh = rng.choice([1, 2, 1.7])
        a = [hh * u + 3 + v for u, v in zip(b, x)]
        z = [v / 2.0 for v in x]
        r = run(a, b, hh, z, 0.5)
        rh = run_hpath(a, b, [hh] * m, z, 0.5)
        agree = agree and r["fills"] == rh["fills"] and r["trades"] == rh["trades"] and rh["rebalances"] == 0 \
            and max(abs(p - q) for p, q in zip(r["equity"], rh["equity"])) < 1e-8 and abs(rh["redefinition"]) < 1e-8
        hp = [hh + 0.3 * math.sin(t / 7.0) for t in range(m)]
        rv = run_hpath(a, b, hp, z, 0.5)
        ident = ident and abs(rv["price_pnl"] - rv["costs"] - rv["net"]) < 1e-8 and all(
            abs(row["equity"] - (row["cash"] + row["units_A"] * p + row["units_B"] * q)) < 1e-9
            for row, p, q in zip(rv["ledger"], a, b))
    check("run_hpath: h คงที่เท่า run (fill · ไม้ · Equity) · ไม่มีการปรับ · ผลนิยามใหม่ 0", agree)
    check("run_hpath: h เปลี่ยน → เงินจากราคา − ค่าธรรมเนียม = net · Equity = เงินสด + จำนวนถือ × ราคา", ident)
    # ไม้มือ: short X 1 ชุดที่ h 2 → วันถัดไป h 2.2 ราคาไม่ขยับ → เงินจากราคา 0 · X บนจอ −(2.2 − 2) × 50 = −10 → ไม้ short เห็น +10
    A2, B2 = [100.0, 104, 104, 104, 104], [50.0, 50, 50, 50, 50]
    r5 = run_hpath(A2, B2, [2, 2, 2, 2.2, 2.2], [0, 2.5, 2.5, 2.5, 2.5], 1, fee=0.0, hold=None)
    check("run_hpath: ราคานิ่ง h 2 → 2.2 · ไม่มีเงินจากราคา · ผลนิยามใหม่ +10 · ปรับขา B หนึ่งครั้ง",
          abs(r5["price_pnl"]) < 1e-12 and abs(r5["chart_pnl"] - 10) < 1e-9 and r5["rebalances"] == 1
          and abs(r5["open_units"][1] - 2.2) < 1e-12)
    print("selftest", f"ผ่าน ✓ ({n} ข้อ · สิบวันของบท 13 ตรงหน้า · เท่าลูป 💻 ทุกบิต 200 โลก · lag/same/ฟังก์ชันสัญญาณ · "
          "เวลาถือ · งบขาดทุน · บัญชีเงินสด/จำนวนถือ/ค่าธรรมเนียม · drawdown · run_hpath h เปลี่ยนได้)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    print(__doc__)
    sys.exit(2)
