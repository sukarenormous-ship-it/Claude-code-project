#!/usr/bin/env python3
"""เครื่อง backtest กลางของเล่ม 2 (stdlib) · shared pair backtest engine for volume 2 (บท 12 เป็นต้นไป)

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

    python3 tools/sab2_engine.py --selftest
"""

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


# ═══════════════════════════ selftest ═══════════════════════════

def _reference(A, B, h, z, sets, lag=1, fee=FEE, enter=2, leave=0.5, hold=30):
    """ลูปในบล็อก 💻 ของ docs/sab2-part12.html ตรงตัว (ต้นแบบที่เครื่องต้องให้ผลเท่ากันทุกบิต)"""
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

    # 1) สิบวันของบท 12 (ตอน ก): ราคาวันถัดไป 1010.96 · ราคาวันเดียวกัน 1016.96 (ตรงบรรทัดคาดหวังของหน้า)
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
    print("selftest", f"ผ่าน ✓ ({n} ข้อ · สิบวันของบท 12 ตรงหน้า · เท่าลูป 💻 ทุกบิต 200 โลก · lag/same/ฟังก์ชันสัญญาณ · "
          "เวลาถือ · งบขาดทุน · บัญชีเงินสด/จำนวนถือ/ค่าธรรมเนียม · drawdown)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    print(__doc__)
    sys.exit(2)
