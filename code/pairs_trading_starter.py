"""
Pairs Trading Starter — โค้ดคู่มือประกอบ Arbitrage Part V (Stat Arb, บท 18-21)
รายย่อยรันได้จริง: ใช้ข้อมูลฟรีจาก Yahoo Finance + statsmodels

ติดตั้ง:  pip install -r requirements.txt
รัน:      python pairs_trading_starter.py KO PEP

โค้ดนี้เพื่อ "เรียนรู้และวิจัย" ไม่ใช่คำแนะนำการลงทุน — backtest/ผลในอดีต
ไม่รับประกันอนาคต และตัวเลขก่อนหักต้นทุน (gross) จะดูดีกว่าจริงเสมอ

⚠️ การ short มีความเสี่ยงขาดทุนไม่จำกัด + margin call + ค่า borrow รายวัน
   อย่าเทรดเงินจริงก่อน paper trade อย่างน้อย 2-3 เดือน และ size ≤ 1-2%/คู่
"""

from __future__ import annotations
import sys
import warnings
import numpy as np
import pandas as pd

try:
    import yfinance as yf
    import statsmodels.api as sm
    from statsmodels.tsa.stattools import coint, kpss
except ImportError as exc:  # pragma: no cover
    sys.exit(f"ขาดไลบรารี: {exc}\nรัน: pip install -r requirements.txt")


# ---------- ขั้นที่ 1: ข้อมูล ----------
def download_prices(ticker_a: str, ticker_b: str,
                    start: str = "2018-01-01", end: str | None = None) -> pd.DataFrame:
    """ดึงราคาปิดปรับแล้ว (adjusted close) ของสองตัว เรียงคอลัมน์เป็น [A, B]
    กัน ticker ผิด / เน็ตล่ม ให้ขึ้น error ที่อ่านเข้าใจ แทน traceback ดิบ"""
    try:
        raw = yf.download([ticker_a, ticker_b], start=start, end=end,
                          auto_adjust=True, progress=False)
    except Exception as exc:  # network ฯลฯ
        raise ValueError(f"ดึงข้อมูลไม่ได้ (เน็ต?): {exc}") from exc
    if raw is None or raw.empty or "Close" not in raw.columns.get_level_values(0):
        raise ValueError(f"ไม่พบข้อมูล — ตรวจ ticker ({ticker_a}, {ticker_b}) หรือการเชื่อมต่อ")
    close_all = raw["Close"]
    missing = [t for t in (ticker_a, ticker_b) if t not in close_all.columns]
    if missing:
        raise ValueError(f"ticker ไม่พบข้อมูล: {missing}")
    close = close_all[[ticker_a, ticker_b]].dropna()
    if close.shape[1] != 2 or len(close) < 250:
        raise ValueError("ข้อมูลไม่พอ — ต้องมีอย่างน้อย ~1 ปี")
    return close


def split_train_test(close: pd.DataFrame, train_frac: float = 0.7):
    """แบ่งข้อมูลเป็น train (ประเมินพารามิเตอร์) / test (out-of-sample) — กัน look-ahead"""
    n = int(len(close) * train_frac)
    return close.iloc[:n], close.iloc[n:]


# ---------- ขั้นที่ 2: hedge ratio + spread ----------
def hedge_ratio(y: pd.Series, x: pd.Series) -> float:
    """beta จาก OLS:  y = alpha + beta*x"""
    return float(sm.OLS(y, sm.add_constant(x)).fit().params.iloc[1])


def kpss_pvalue(spread: pd.Series) -> float:
    """KPSS: null กลับด้านกับ ADF (null = stationary)
    p < 0.05 = reject stationarity (ขัดกับสมมติฐาน mean-revert)
    ใช้ cross-check กับ coint(): EG reject + KPSS ไม่ reject = หลักฐานแข็งสองทาง"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # kpss เตือนเมื่อ p ชนขอบตาราง [0.01, 0.1]
        _stat, p, _lags, _crit = kpss(spread.dropna(), regression="c", nlags="auto")
    return float(p)


def evidence_tier(eg_pval: float, kpss_p: float, hl: float, sh_oos: float) -> tuple[str, str]:
    """จัดระดับหลักฐานตาม Evidence Tiers ในหนังสือ — ไม่ใช้ p-value เป็นสวิตช์ตัวเดียว
    คืน (tier, เหตุผล)"""
    if eg_pval >= 0.05 and kpss_p < 0.05:
        return ("🔴 Reject", "EG ไม่ reject และ KPSS ชี้ไม่ stationary — หลักฐานลบสองทาง")
    if eg_pval >= 0.05:
        return ("🟡 Watchlist", "ยังอ้าง cointegration ไม่ได้ (EG ไม่ reject) — "
                "อาจเป็น power ต่ำ/sample สั้น เก็บข้อมูลดูต่อ ห้ามเทรด")
    if kpss_p < 0.05:
        return ("🟡 Watchlist", "EG reject แต่ KPSS ขัด — หลักฐานขัดกัน รอความชัดเจน")
    if not (5 <= hl <= 30):
        return ("🟡 Watchlist", f"half-life {hl:.0f} วัน นอกช่วง 5-30 — โครงสร้างยังไม่เหมาะเทรด")
    if sh_oos <= 0:
        return ("🔴 Reject", "OOS Sharpe ติดลบ — edge ไม่รอดต้นทุนนอกตัวอย่าง")
    if sh_oos > 3:
        return ("🔵 Research candidate", "OOS Sharpe สูงผิดปกติ (>3) — ตรวจ overfit/data ก่อนเชื่อ")
    if sh_oos < 1:
        return ("🔵 Research candidate", "หลักฐานสถิติครบแต่ OOS Sharpe < 1 — paper trade/ปรับโมเดลต่อ")
    return ("🟢 Trade candidate", "หลักฐานครบทุกชั้น — เริ่ม paper trade 2-3 เดือนก่อนเงินจริง")


# ---------- ขั้นที่ 3: half-life ของ mean reversion ----------
def half_life(spread: pd.Series) -> float:
    """Half-life = -ln(2)/b  จาก  ds_t = a + b*s_{t-1}  (b ต้องติดลบจึงจะ mean-revert)"""
    s = spread.dropna()
    ds = s.diff().dropna()
    s_lag = s.shift(1).loc[ds.index]
    b = float(sm.OLS(ds, sm.add_constant(s_lag)).fit().params.iloc[1])
    return float("inf") if b >= 0 else -np.log(2) / b


# ---------- ขั้นที่ 4: ต้นทุน, สัญญาณ Z-score, และด่าน "หน่วยเงิน" ----------
def round_trip_cost(close: pd.DataFrame, beta: float,
                    cost_bps: float = 20.0) -> pd.Series:
    """ต้นทุนไป-กลับโดยประมาณ ในหน่วยเดียวกับ spread (เข้า 1 ครั้ง + ออก 1 ครั้ง)
    ฐานคือ gross notional ทั้งสองขา = |A| + |beta|*|B|"""
    a, b = close.iloc[:, 0], close.iloc[:, 1]
    notional = a.abs() + abs(beta) * b.abs()
    return notional * (cost_bps / 1e4) * 2.0


def zscore(spread: pd.Series, window: int = 30,
           sigma_floor: pd.Series | float | None = None) -> pd.Series:
    """Z-score แบบ rolling (กัน look-ahead bias)

    sigma_floor : พื้นขั้นต่ำของ sigma — กัน z "พองเอง" ตอนตลาดนิ่ง
        ช่วง Bollinger squeeze ค่า sigma ยุบ ทำให้ราคาขยับนิดเดียวก็แตะ 2-3 sigma
        ทั้งที่ระยะทางจริงสั้นเกินกว่าจะคุ้มค่าธรรมเนียม (ดูบท 18.2)
        ค่าที่แนะนำ = 2 x ต้นทุนไป-กลับ (อนุมานจาก (z_in - z_out) * sigma >= k * cost)
    """
    mean = spread.rolling(window).mean()
    sd = spread.rolling(window).std()
    if sigma_floor is not None:
        sd = sd.clip(lower=sigma_floor)
    return (spread - mean) / sd


def edge_ok(spread: pd.Series, window: int, cost: pd.Series,
            edge_k: float = 3.0) -> pd.Series:
    """ด่านนัยสำคัญ 'ทางเศรษฐกิจ': ระยะห่างในหน่วยเงินต้องคุ้มต้นทุนกี่เท่า
    |spread - mean| >= edge_k * ต้นทุนไป-กลับ"""
    mean = spread.rolling(window).mean()
    return (spread - mean).abs() >= (edge_k * cost)


def positions_from_z(z: pd.Series, entry: float = 2.0,
                     exit_: float = 0.5, stop: float = 4.0,
                     ok: pd.Series | None = None) -> pd.Series:
    """สร้างสถานะ: +1 = long spread, -1 = short spread, 0 = ว่าง

    ok : ด่านหน่วยเงิน (จาก edge_ok) — ถ้า False จะ "ไม่เปิด" สถานะใหม่
         แต่ยัง "ปิด" สถานะเดิมได้ตามปกติ (ไม่ขังเงินไว้)
    """
    pos = np.zeros(len(z))
    for i in range(1, len(z)):
        prev, zi = pos[i - 1], z.iloc[i]
        if np.isnan(zi):
            pos[i] = prev
        elif prev == 0:
            allowed = True if ok is None else bool(ok.iloc[i])
            if not allowed:
                pos[i] = 0.0
            else:
                pos[i] = -1.0 if zi > entry else (1.0 if zi < -entry else 0.0)
        else:
            pos[i] = 0.0 if (abs(zi) < exit_ or abs(zi) > stop) else prev
    return pd.Series(pos, index=z.index)


# ---------- ขั้นที่ 5: ผลตอบแทน (มีต้นทุน + ค่า borrow) ----------
def strategy_returns(close: pd.DataFrame, beta: float, pos: pd.Series,
                     cost_bps: float = 20.0, borrow_bps_annual: float = 100.0) -> pd.Series:
    """
    return ต่อวันโดยประมาณ = position เมื่อวาน * การเปลี่ยนของ spread / ทุนทั้งสองขา
      cost_bps          : ต้นทุนต่อการเปลี่ยนสถานะ 1 หน่วย (spread+commission+slippage, ต่อขา)
      borrow_bps_annual : ค่ายืมหุ้น (short) ต่อปี — คิดทุกวันที่ถือสถานะ
    หมายเหตุ: ทุน = ราคา A + |beta|*ราคา B (gross notional ทั้งสองขา) ไม่ใช่ขา A อย่างเดียว
    """
    a, b = close.iloc[:, 0], close.iloc[:, 1]
    spread = a - beta * b
    capital = a.shift(1) + abs(beta) * b.shift(1)
    gross = pos.shift(1) * spread.diff() / capital
    tc = pos.diff().abs() * (cost_bps / 1e4)
    borrow = pos.shift(1).abs() * (borrow_bps_annual / 252 / 1e4)
    return (gross - tc - borrow).fillna(0.0)


def sharpe(returns: pd.Series, ann: float = 252.0) -> float:
    sd = returns.std()
    return float(returns.mean() / sd * np.sqrt(ann)) if sd else 0.0


# ---------- ขั้นที่ 6: สัญญาณวันนี้ (สำหรับ paper trade) ----------
def todays_signal(z: pd.Series, ta: str, tb: str, beta: float,
                  entry: float = 2.0, exit_: float = 0.5, stop: float = 4.0,
                  ok: pd.Series | None = None) -> str:
    zc = z.dropna()
    if zc.empty:
        return "ข้อมูลไม่พอสำหรับสัญญาณ"
    last_z, last_date = zc.iloc[-1], zc.index[-1].date()
    passes_edge = True if ok is None else bool(ok.loc[zc.index[-1]])
    if abs(last_z) > stop:
        act = "อย่าเข้า / ถ้าถืออยู่ให้ STOP ปิดสถานะ (อาจ structural break)"
    elif abs(last_z) >= entry and not passes_edge:
        act = ("มีสัญญาณสถิติ แต่ไม่ผ่านด่านหน่วยเงิน → ไม่เข้า "
               "(ระยะห่างสั้นเกินกว่าจะคุ้มค่าธรรมเนียม — ช่วงแบนด์บีบตัว)")
    elif last_z > entry:
        act = f"SHORT spread: ขาย(short) {ta}, ซื้อ {beta:.2f}×{tb}"
    elif last_z < -entry:
        act = f"LONG spread: ซื้อ {ta}, ขาย(short) {beta:.2f}×{tb}"
    elif abs(last_z) < exit_:
        act = "EXIT/ปิดสถานะถ้ามี (spread กลับเข้าใกล้ค่าเฉลี่ย)"
    else:
        act = "ถือ/รอ — ยังไม่มีสัญญาณใหม่"
    return f"{last_date}: Z = {last_z:+.2f} → {act}"


def main() -> None:
    ta = sys.argv[1] if len(sys.argv) > 1 else "KO"
    tb = sys.argv[2] if len(sys.argv) > 2 else "PEP"
    print(f"คู่: {ta} vs {tb}  (ประเมินพารามิเตอร์บน train, วัดผลบน out-of-sample)")

    close = download_prices(ta, tb)
    train, test = split_train_test(close)
    a_tr, b_tr = train.iloc[:, 0], train.iloc[:, 1]

    # 1) cointegration (train เท่านั้น)
    # ใช้ coint() เท่านั้น — มันใช้ Engle-Granger/MacKinnon critical values ให้ถูกชุด
    # ห้ามรัน adfuller() บน residual เองด้วย critical values ปกติ (จะ reject ง่ายเกินจริง)
    _t, pval, _crit = coint(a_tr, b_tr)
    print(f"[1] Cointegration p-value (train) = {pval:.4f}  "
          f"({'reject ✓ หลักฐานแข็ง' if pval < 0.05 else 'ยัง reject ไม่ได้ — ยังอ้าง cointegration ไม่ได้'})")

    # 2) hedge ratio (train)
    beta = hedge_ratio(a_tr, b_tr)
    print(f"[2] Hedge ratio beta (train) = {beta:.3f}")

    # 3) half-life + KPSS cross-check (train)
    spread_tr = a_tr - beta * b_tr
    hl = half_life(spread_tr)
    print(f"[3] Half-life (train) = {hl:.1f} วัน  "
          f"({'ดี ✓' if 5 <= hl <= 30 else 'ระวัง — นอกช่วง 5-30 วัน'})")
    kp = kpss_pvalue(spread_tr)
    print(f"[4] KPSS cross-check (null=stationary): p = {kp:.3f}  "
          f"({'ไม่ขัด ✓' if kp >= 0.05 else 'ขัด! — KPSS ชี้ไม่ stationary'})")

    # 5) สัญญาณบนทั้งชุด, วัด Sharpe in-sample เทียบ out-of-sample
    spread = close.iloc[:, 0] - beta * close.iloc[:, 1]
    cost = round_trip_cost(close, beta)          # ต้นทุนไป-กลับ (หน่วยเดียวกับ spread)
    # sigma floor = 2 x cost  -> กัน z พองเองตอนตลาดนิ่ง (Bollinger squeeze, บท 18.2)
    z = zscore(spread, sigma_floor=2.0 * cost)
    ok = edge_ok(spread, 30, cost)               # ด่านหน่วยเงิน: ระยะห่าง >= 3 x cost
    pos = positions_from_z(z, ok=ok)
    blocked = int(((z.abs() >= 2.0) & ~ok).sum())
    print(f"[4b] ด่านหน่วยเงิน: บล็อกสัญญาณสถิติที่ไม่คุ้มต้นทุนไป {blocked} วัน "
          f"(z ถึงเกณฑ์ แต่ระยะห่าง < 3x ต้นทุน)")
    net = strategy_returns(close, beta, pos)
    sh_is = sharpe(net.loc[train.index])
    sh_oos = sharpe(net.loc[test.index])
    print(f"[5] Sharpe (หลังต้นทุน 20bps + borrow 1%/ปี): "
          f"in-sample = {sh_is:.2f}  |  out-of-sample = {sh_oos:.2f}  ← เชื่อตัว OOS")
    if sh_is - sh_oos > 1.0:
        print("    ⚠️ in-sample ดีกว่า OOS มาก = สัญญาณ overfit — ระวัง")
    if sh_oos > 3:
        print("    ⚠️ OOS Sharpe สูงผิดปกติ (>3) สงสัยไว้ก่อนว่ายัง overfit")

    # 6) สัญญาณวันนี้ (เอาไปจดใน paper trade log)
    print(f"[6] สัญญาณวันนี้: {todays_signal(z, ta, tb, beta, ok=ok)}")

    # 7) verdict แบบ Evidence Tier — ไม่ใช่ ผ่าน/ตก ด้วย p-value ตัวเดียว
    tier, reason = evidence_tier(pval, kp, hl, sh_oos)
    print(f"\n[7] Evidence Tier: {tier}")
    print(f"    เหตุผล: {reason}")
    print("→ ทุก tier ที่ไม่ใช่ Reject: paper trade ≥ 2-3 เดือน (จดสัญญาณ [6] ทุกวัน) "
          "ก่อนคิดเรื่องเงินจริง ≤ 1-2%/คู่")


if __name__ == "__main__":
    main()
