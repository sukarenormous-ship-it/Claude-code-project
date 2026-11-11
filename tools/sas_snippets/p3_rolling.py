import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import sas_core as C

# ใช้: python3 tools/sas_snippets/p3_rolling.py [<ไฟล์.csv> <คอลัมน์ Y> <คอลัมน์ X>]
#      ไม่ใส่อะไร = คู่จำลอง good · drift · fake
# คำถาม: β จาก 250 แท่งล่าสุดแกว่งเพราะ noise, เพราะจุดผูกสายเลื่อน (β จริงเปลี่ยน) หรือเพราะไม่มีสายจูง
W = 250


def rolling_beta(y, x):                  # ค่าที่ t ใช้แท่ง t−250 … t−1 = β ที่รู้ ณ ปิดแท่ง t−1
    return np.array([C.ols(y[t - W:t], x[t - W:t])["coef"][1] for t in range(W, len(y) + 1)])


if len(sys.argv) == 4:
    d = np.genfromtxt(sys.argv[1], delimiter=",", names=True)
    P = np.log(np.column_stack([d[c.replace(" ", "_")] for c in sys.argv[2:4]]))
    pairs = {"yours": P[np.all(np.isfinite(P), axis=1)].T}
else:
    pairs = {k: (C.demo_pair(k)["y"], C.demo_pair(k)["x"]) for k in ("good", "drift", "fake")}
print(f"{'pair':>6} {'first':>7} {'middle':>7} {'last':>7} {'min':>7} {'max':>7} {'range':>7}")
for name, (y, x) in pairs.items():
    b = rolling_beta(y, x)
    cols = (b[0], b[len(b) // 2], b[-1], b.min(), b.max(), np.ptp(b))
    print(f"{name:>6} " + " ".join(f"{v:7.2f}" for v in cols))
print("อ่าน: good มี β จริงคงที่ 1.4 แต่ยังแกว่ง = ขนาดของ noise จาก 250 แท่ง ใช้เป็นเส้นฐาน")
print("      ไต่ขึ้นหรือลงต่อเนื่องเกินเส้นฐาน = β เลื่อน (จุดผูกสายเลื่อน) ต้องประมาณใหม่")
print("      เหวี่ยงจนกลับเครื่องหมาย = อาจไม่มีสายจูง")
