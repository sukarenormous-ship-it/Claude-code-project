import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sas_core as C

# ใช้: python3 tools/sas_snippets/p7_carry.py [spot future วัน ต้นทุนเงิน%ต่อปี bpsต่อขา]
# ไม่ใส่ค่า = ตัวอย่างสมมติของ 7b · ซื้อ spot + ขาย future แล้วถือถึงวันหมดอายุ
# สมมติ: spot ไม่มีผลตอบแทน · ดอกเบี้ยอย่างง่าย actual/365 · 4 ขา (เข้า 2 ออก 2)
#        ขาออกคิดที่ราคา spot วันนี้ · ยังไม่รวมต้นทุนเงินของหลักประกันขา future
a = [float(v) for v in sys.argv[1:6]] if len(sys.argv) == 6 else [100, 102.5, 90, 4, 5]
spot, fut, days, rate, c = a[0], a[1], a[2], a[3] / 100, a[4] / 1e4
fin = spot * rate * days / 365            # ต้นทุนเงินที่จมในขา spot
fair = spot + fin                         # ราคา future ที่ไม่มีใครได้เปรียบ
cost = c * (spot + fut) + c * 2 * spot    # ค่าซื้อขาย ขาเข้า + ขาออก
conv = fut - fair                         # ε: ส่วนที่แพงเกินราคายุติธรรม
carry = (fair - spot) - fin               # ดอกเบี้ยใน basis − ต้นทุนเงิน (= 0)
net = conv + carry - cost
be = (fair + 3 * c * spot) / (1 - c)      # future ต่ำสุดที่ยังไม่ขาดทุน
yr = C.rd(100 * net / spot * 365 / days, 2)
print(f"spot {spot:.2f} | future {fut:.2f} | {days:.0f} วัน | "
      f"ต้นทุนเงิน {100 * rate:.1f}%/ปี | {1e4 * c:.0f} bps x 4 ขา")
print(f"ราคายุติธรรม {fair:.2f} -> future แพงเกิน (ε) {conv:.2f} บาท"
      f" = {1e4 * conv / spot:.0f} bps")
print(f"P&L = convergence + carry - costs"
      f" = {conv:.2f} + {carry:.2f} - {cost:.2f} = {net:.2f} บาท")
print(f"    = {yr:.2f}% ต่อปี เกินการฝากเงิน"
      + (" (ล็อกไว้ ถ้าถือถึงวันหมดอายุได้)" if net > 0 else ""))
if conv < 0:
    print("future ถูกกว่าราคายุติธรรม: ฝั่งที่ถูกคือ reverse cash-and-carry"
          " (short spot ซื้อ future) ซึ่งต้องยืมของได้และมีค่ายืม")
print(f"จุดคุ้มทุน: future ต้องเกิน {be:.2f} (ε > {1e4 * (be - fair) / spot:.0f} bps)"
      + ("" if net > 0 else "  -> ไม่คุ้ม"))
