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
import numpy as np
import pandas as pd

try:
    import yfinance as yf
    import statsmodels.api as sm
    from statsmodels.tsa.stattools import coint
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


# ---------- ขั้นที่ 3: half-life ของ mean reversion ----------
def half_life(spread: pd.Series) -> float:
    """Half-life = -ln(2)/b  จาก  ds_t = a + b*s_{t-1}  (b ต้องติดลบจึงจะ mean-revert)"""
    s = spread.dropna()
    ds = s.diff().dropna()
    s_lag = s.shift(1).loc[ds.index]
    b = float(sm.OLS(ds, sm.add_constant(s_lag)).fit().params.iloc[1])
    return float("inf") if b >= 0 else -np.log(2) / b


# ---------- ขั้นที่ 4: สัญญาณ Z-score ----------
def zscore(spread: pd.Series, window: int = 30) -> pd.Series:
    """Z-score แบบ rolling (กัน look-ahead bias)"""
    return (spread - spread.rolling(window).mean()) / spread.rolling(window).std()


def positions_from_z(z: pd.Series, entry: float = 2.0,
                     exit_: float = 0.5, stop: float = 4.0) -> pd.Series:
    """สร้างสถานะ: +1 = long spread, -1 = short spread, 0 = ว่าง"""
    pos = np.zeros(len(z))
    for i in range(1, len(z)):
        prev, zi = pos[i - 1], z.iloc[i]
        if np.isnan(zi):
            pos[i] = prev
        elif prev == 0:
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
                  entry: float = 2.0, exit_: float = 0.5, stop: float = 4.0) -> str:
    zc = z.dropna()
    if zc.empty:
        return "ข้อมูลไม่พอสำหรับสัญญาณ"
    last_z, last_date = zc.iloc[-1], zc.index[-1].date()
    if abs(last_z) > stop:
        act = "อย่าเข้า / ถ้าถืออยู่ให้ STOP ปิดสถานะ (อาจ structural break)"
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
    _t, pval, _crit = coint(a_tr, b_tr)
    ok_coint = pval < 0.05
    print(f"[1] Cointegration p-value (train) = {pval:.4f}  "
          f"({'ผ่าน ✓' if ok_coint else 'ไม่ผ่าน ✗ — อย่าเทรดคู่นี้'})")

    # 2) hedge ratio (train)
    beta = hedge_ratio(a_tr, b_tr)
    print(f"[2] Hedge ratio beta (train) = {beta:.3f}")

    # 3) half-life (train)
    hl = half_life(a_tr - beta * b_tr)
    ok_hl = 5 <= hl <= 30
    print(f"[3] Half-life (train) = {hl:.1f} วัน  "
          f"({'ดี ✓' if ok_hl else 'ระวัง — นอกช่วง 5-30 วัน'})")

    # 4-5) สัญญาณบนทั้งชุด, วัด Sharpe in-sample เทียบ out-of-sample
    spread = close.iloc[:, 0] - beta * close.iloc[:, 1]
    z = zscore(spread)
    pos = positions_from_z(z)
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
    print(f"[6] สัญญาณวันนี้: {todays_signal(z, ta, tb, beta)}")

    if not (ok_coint and ok_hl and sh_oos > 1):
        print("\n→ คู่นี้ยังไม่ผ่าน Checklist ครบ — ใช้เพื่อ 'เรียนรู้' ได้ แต่ยังไม่ควรเทรดเงินจริง")
    print("→ ขั้นต่อไป: paper trade ≥ 2-3 เดือน (จดสัญญาณ [6] ทุกวัน) ก่อน size เล็ก ≤ 1-2%/คู่")


if __name__ == "__main__":
    main()
