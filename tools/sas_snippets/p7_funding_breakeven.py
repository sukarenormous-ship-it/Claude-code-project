import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import statarb_lab as LAB

# ใช้: python3 tools/sas_snippets/p7_funding_breakeven.py [ไฟล์.csv คอลัมน์ งวดต่อวัน]
# คอลัมน์ = funding ต่องวดเป็น % ตามที่หน้าจอแสดง (เช่น 0.01) · มีคอลัมน์วันเวลา = เรียงเก่าไปใหม่ให้
# ไม่ใส่ไฟล์ = ข้อมูลจำลองหน้าตาคล้าย 7b (ปกติ 1 bps · ช่วงติดลบ -1.5 bps)
RATE, COST = 4.0, 20      # ต้นทุนเงินของขา spot %/ปี · ค่าซื้อขายไปกลับ bps
if len(sys.argv) == 4:
    f = LAB.load_columns(sys.argv[1], [sys.argv[2]], "log")[1][:, 0] * 100   # "log" = ไม่แปลงค่า · % -> bps
    per_day = int(sys.argv[3])
else:
    g, s, f, per_day = np.random.default_rng(9), False, [], 3
    for t in range(2 * 1095):
        s = g.random() < (44 / 45 if s else 1 / 270)       # เข้า/ออกช่วงติดลบ
        f.append((-1.5 if s else 1.0) + 0.7 * g.standard_normal())
    f = np.array(f)
fin = RATE * 100 / 365 / per_day                 # ต้นทุนเงินต่องวด (bps)
c = np.concatenate([[0], np.cumsum(f - fin)])    # ผลสะสมหลังต้นทุนเงิน
days, h = [], 7 * per_day
for i in range(len(f) // 2):                     # เริ่มในครึ่งแรก ตามดูถึงท้ายข้อมูล
    ok = np.nonzero(c[i + 1:] - c[i] >= COST)[0]
    days.append((ok[0] + 1) / per_day if len(ok) else np.inf)
w = 30 * per_day
g30 = np.convolve(f, np.ones(w), "valid").min()
lose7 = np.mean(c[h:len(f) // 2 + h] - c[:len(f) // 2] < COST)
print(f"{len(f):,} งวด · funding เฉลี่ย {f.mean() * per_day * 3.65:.1f}% ต่อปี (ยังไม่หักอะไร)")
print(f"งวดติดลบ {100 * np.mean(f < 0):.0f}% · 30 วันที่แย่ที่สุด {g30:.0f} bps")
print(f"วันคุ้มทุน (หัก {COST} bps + ต้นทุนเงิน {RATE:.0f}%/ปี) ค่ากลาง"
      f" {np.median(days):.0f} วัน · ไม่ถึงเลย {100 * np.mean(np.isinf(days)):.0f}%")
print(f"ถือ 7 วัน แพ้การฝากเงิน {100 * lose7:.0f}% ของจุดเริ่ม")
