"""คณิตของ payoff diagram (เลขคณิตล้วน ไม่ใช้ numpy) — ใช้ร่วมกันโดย
tools/make_figures.py (วาดภาพ) และ tools/book_figures.py (ทวนตัวเลขในข้อความ)

ขา = Leg(kind, K, qty, premium)
  kind    : "call" "put" "stock" "bond" "dcall" "dput"  (dcall/dput = digital จ่าย 1 หน่วยเมื่อ ITM)
  K       : สไตรก์ · สำหรับ stock = ราคาที่ซื้อ · สำหรับ bond = เงินต้นที่ได้คืน
  qty     : จำนวน (+ long · − short)
  premium : เบี้ยต่อหน่วย (จ่ายเมื่อ long รับเมื่อ short) · สำหรับ bond = ราคาที่จ่ายวันนี้
โดเมนราคา S ∈ [0, ∞) ตามอนุสัญญาของเล่ม (Short Put ขาดทุนสูงสุดที่ S = 0)
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Leg:
    kind: str
    K: float
    qty: float = 1.0
    premium: float = 0.0
    pay: float = 1.0          # ขนาดจ่ายของ digital

    def intrinsic(self, S):
        k = self.kind
        if k == "call":  v = max(S - self.K, 0.0)
        elif k == "put": v = max(self.K - S, 0.0)
        elif k == "stock": v = S - self.K
        elif k == "bond": v = self.K
        elif k == "dcall": v = self.pay if S > self.K else 0.0
        elif k == "dput":  v = self.pay if S < self.K else 0.0
        else: raise ValueError(k)
        return self.qty * v

    def cost(self):
        return self.qty * self.premium


def net_premium(legs):
    """เบี้ยสุทธิที่จ่าย (+ = debit · − = credit)"""
    return sum(l.cost() for l in legs)


def value(legs, S, with_premium=True):
    v = sum(l.intrinsic(S) for l in legs)
    return v - net_premium(legs) if with_premium else v


def strikes(legs):
    return sorted({l.K for l in legs if l.kind not in ("bond", "stock")})   # หุ้นไม่มีจุดหัก


def slope_between(legs, a, b, with_premium=True):
    m = (a + b) / 2
    return (value(legs, m + 1e-6, with_premium) - value(legs, m - 1e-6, with_premium)) / 2e-6


def segments(legs, x0, x1, with_premium=True):
    """ช่วงเชิงเส้นระหว่างสไตรก์: [(a, b, slope, f(a+), f(b−)), …]"""
    ks = [k for k in strikes(legs) if x0 < k < x1]
    pts = [x0] + ks + [x1]
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        fa = value(legs, a + 1e-9, with_premium); fb = value(legs, b - 1e-9, with_premium)
        out.append((a, b, round(slope_between(legs, a, b, with_premium), 6), fa, fb))
    return out


def breakevens(legs, with_premium=True):
    """จุดคุ้มทุนบนโดเมน [0, ∞) — รากของแต่ละช่วงเชิงเส้น และรอยกระโดดของ digital ที่ข้ามศูนย์"""
    ks = strikes(legs)
    hi = (max(ks) if ks else 100) * 3 + 100
    out = []
    for a, b, s, fa, fb in segments(legs, 0.0, hi, with_premium):
        if abs(fa) < 1e-9 and s != 0: out.append(a)          # แตะศูนย์พอดีที่สไตรก์แล้วออกจากศูนย์
        if fa * fb < 0 and s != 0: out.append(a + (0 - fa) / s)
    for k in ks:  # กระโดดข้ามศูนย์ที่สไตรก์ (digital)
        fl, fr = value(legs, k - 1e-9, with_premium), value(legs, k + 1e-9, with_premium)
        if fl * fr < 0 and abs(fl - fr) > 1e-9 and not any(abs(k - x) < 1e-6 for x in out): out.append(k)
    return sorted(round(x, 6) for x in set(round(x, 6) for x in out))


def right_slope(legs):
    hi = (max(strikes(legs)) if strikes(legs) else 100) * 3 + 100
    return round(slope_between(legs, hi, hi + 10), 6)


def left_slope(legs):
    return round(slope_between(legs, 0.0, min(strikes(legs)) if strikes(legs) else 1.0), 6)


def extremes(legs, with_premium=True):
    """(max_profit, ตำแหน่ง) และ (max_loss, ตำแหน่ง) · None = ไม่จำกัด (ปลายขวาชันไม่หยุด) · ตำแหน่ง 'S→∞' หรือ 'S=0' หรือค่า S"""
    ks = strikes(legs)
    cand = [(value(legs, 0.0, with_premium), 0.0)] + [(value(legs, k, with_premium), k) for k in ks]
    rs = right_slope(legs)
    mp = max(cand); ml = min(cand)
    max_profit = None if rs > 0 else mp
    max_loss = None if rs < 0 else ml
    return max_profit, max_loss


def summary(legs, with_premium=True):
    mp, ml = extremes(legs, with_premium)
    return dict(net_premium=net_premium(legs), breakevens=breakevens(legs, with_premium),
                max_profit=None if mp is None else mp[0], max_profit_at=None if mp is None else mp[1],
                max_loss=None if ml is None else ml[0], max_loss_at=None if ml is None else ml[1],
                left_slope=left_slope(legs), right_slope=right_slope(legs))


if __name__ == "__main__":
    lc = [Leg("call", 100, 1, 5)]
    print("Long Call 100 @5:", summary(lc))
    sp = [Leg("put", 100, -1, 5)]
    print("Short Put 100 @5:", summary(sp))
    bcs = [Leg("call", 90, 1, 8), Leg("call", 110, -1, 3)]
    print("BCS 90/110 net 5:", summary(bcs))
    bf = [Leg("call", 90, 1, 12), Leg("call", 100, -2, 6), Leg("call", 110, 1, 3)]
    print("Butterfly net 3:", summary(bf))
    ratio = [Leg("call", 100, 1, 5), Leg("call", 110, -2, 2)]
    print("1x2 ratio:", summary(ratio))
    rng = [Leg("dcall", 90, 1), Leg("dcall", 100, -1)]
    print("Range Yes 90-100:", summary(rng, with_premium=False))
