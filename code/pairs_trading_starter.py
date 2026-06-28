"""
Pairs Trading Starter — โค้ดคู่มือประกอบ Arbitrage Part V (Stat Arb, บท 18-21)
รายย่อยรันได้จริง: ใช้ข้อมูลฟรีจาก Yahoo Finance + statsmodels

ติดตั้ง:  pip install -r requirements.txt
รัน:      python pairs_trading_starter.py KO PEP

โค้ดนี้เพื่อ "เรียนรู้และวิจัย" ไม่ใช่คำแนะนำการลงทุน — backtest/ผลในอดีต
ไม่รับประกันอนาคต และตัวเลขก่อนหักต้นทุน (gross) จะดูดีกว่าจริงเสมอ
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
    """ดึงราคาปิดปรับแล้ว (adjusted close) ของสองตัว เรียงคอลัมน์เป็น [A, B]"""
    raw = yf.download([ticker_a, ticker_b], start=start, end=end,
                      auto_adjust=True, progress=False)
    close = raw["Close"][[ticker_a, ticker_b]].dropna()
    if close.shape[1] != 2 or len(close) < 250:
        raise ValueError("ข้อมูลไม่พอหรือ ticker ผิด — ต้องมีอย่างน้อย ~1 ปี")
    return close


# ---------- ขั้นที่ 2: hedge ratio + spread ----------
def hedge_ratio(y: pd.Series, x: pd.Series) -> float:
    """beta จาก OLS:  y = alpha + beta*x"""
    model = sm.OLS(y, sm.add_constant(x)).fit()
    return float(model.params.iloc[1])


# ---------- ขั้นที่ 3: half-life ของ mean reversion ----------
def half_life(spread: pd.Series) -> float:
    """Half-life = -ln(2)/b  จาก  ds_t = a + b*s_{t-1}  (b ต้องติดลบจึงจะ mean-revert)"""
    s = spread.dropna()
    ds = s.diff().dropna()
    s_lag = s.shift(1).loc[ds.index]
    b = float(sm.OLS(ds, sm.add_constant(s_lag)).fit().params.iloc[1])
    if b >= 0:
        return float("inf")  # ไม่ mean-revert
    return -np.log(2) / b


# ---------- ขั้นที่ 4: สัญญาณ Z-score ----------
def zscore(spread: pd.Series, window: int = 30) -> pd.Series:
    """Z-score แบบ rolling (กัน look-ahead bias)"""
    mean = spread.rolling(window).mean()
    std = spread.rolling(window).std()
    return (spread - mean) / std


# ---------- ขั้นที่ 5: backtest (มีต้นทุน) ----------
def backtest(close: pd.DataFrame, beta: float,
             entry: float = 2.0, exit_: float = 0.5, stop: float = 4.0,
             window: int = 30, cost_bps: float = 10.0) -> dict:
    """
    Backtest บน spread = A - beta*B
      entry : เปิดเมื่อ |z| > entry
      exit_ : ปิดเมื่อ |z| < exit_
      stop  : ตัดเมื่อ |z| > stop (อาจเป็น structural break)
      cost_bps : ต้นทุนต่อการเปลี่ยนสถานะ 1 ครั้ง (รวม spread+commission+slippage)
    """
    a, b = close.iloc[:, 0], close.iloc[:, 1]
    spread = a - beta * b
    z = zscore(spread, window)

    pos = np.zeros(len(z))  # +1 = long spread, -1 = short spread
    for i in range(1, len(z)):
        prev, zi = pos[i - 1], z.iloc[i]
        if np.isnan(zi):
            pos[i] = prev
            continue
        if prev == 0:
            if zi > entry:
                pos[i] = -1            # spread แพงไป -> short
            elif zi < -entry:
                pos[i] = 1             # spread ถูกไป -> long
        else:
            pos[i] = 0 if (abs(zi) < exit_ or abs(zi) > stop) else prev
    pos = pd.Series(pos, index=z.index)

    # P&L โดยประมาณ: position เมื่อวาน * การเปลี่ยนของ spread (normalize ด้วยราคา A)
    gross = pos.shift(1) * spread.diff() / a.shift(1)
    trades = pos.diff().abs()
    net = (gross - trades * (cost_bps / 1e4)).fillna(0.0)

    eq = (1 + net).cumprod()
    ann = 252.0
    sh_gross = gross.mean() / gross.std() * np.sqrt(ann) if gross.std() else 0.0
    sh_net = net.mean() / net.std() * np.sqrt(ann) if net.std() else 0.0
    return {
        "sharpe_gross": float(sh_gross),
        "sharpe_net": float(sh_net),
        "total_return_net": float(eq.iloc[-1] - 1),
        "n_trades": int(trades.sum()),
    }


def main() -> None:
    ta = sys.argv[1] if len(sys.argv) > 1 else "KO"
    tb = sys.argv[2] if len(sys.argv) > 2 else "PEP"
    print(f"คู่: {ta} vs {tb}")

    close = download_prices(ta, tb)
    a, b = close.iloc[:, 0], close.iloc[:, 1]

    _t, pval, _crit = coint(a, b)
    ok_coint = pval < 0.05
    print(f"[1] Cointegration p-value = {pval:.4f}  "
          f"({'ผ่าน ✓' if ok_coint else 'ไม่ผ่าน ✗ — อย่าเทรดคู่นี้'})")

    beta = hedge_ratio(a, b)
    spread = a - beta * b
    hl = half_life(spread)
    print(f"[2] Hedge ratio beta = {beta:.3f}")
    print(f"[3] Half-life = {hl:.1f} วัน  "
          f"({'ดี ✓' if 2 <= hl <= 30 else 'ระวัง — สั้น/ยาวเกินไป'})")

    r = backtest(close, beta)
    print(f"[5] Backtest: Sharpe gross = {r['sharpe_gross']:.2f}, "
          f"net (หลังต้นทุน 10bps) = {r['sharpe_net']:.2f}, "
          f"trades = {r['n_trades']}, return_net = {r['total_return_net'] * 100:.1f}%")
    print("    ⚠️ Sharpe สวยเกิน (>3) สงสัยไว้ก่อนว่า overfit — ทดสอบ out-of-sample/paper trade")
    print("    ขั้นต่อไป: paper trade ก่อน แล้วค่อย size เล็กด้วยเงินที่เสียได้เท่านั้น")


if __name__ == "__main__":
    main()
