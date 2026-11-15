# ค่าใหม่ต่อบทของเล่ม 2 (ปลั๊กอินของ `tools/sab_figures.py --book sab2`)

โฟลเดอร์นี้ว่างโดยตั้งใจ (โครงเฟส 1) · ไฟล์ `chNN.py` หนึ่งไฟล์ต่อบท (เลขบทเล่ม 2 · `ch01`–`ch17`) มีฟังก์ชันเดียว
แบบเดียวกับเล่ม 1 (`tools/sab_figures_ch/README.md`):

```python
def extend(data, D, q):
    """data = JSON ที่สร้างแล้ว · D = Decimal · q(x, n) = ปัด half-up n ตำแหน่ง"""
    import sab2_sim, sab2_stats          # โฟลเดอร์ tools/ อยู่ใน sys.path แล้ว
    w = sab2_sim.stationary_pair(seed=101, n=250, phi=0.95)
    return {"phi_ประมาณ": q(sab2_stats.ar1(w["X"])["phi"], 2)}
```

ค่าที่คืนเติมใต้ `data["chNN"]` · ห้ามทับคีย์เดิม · `_claims` / `_แบบฝึก` ใช้เหมือนเล่ม 1 ·
ชื่อไฟล์อื่นที่รับ: `realdata.py` · `drills.py` · `cases.py` (ภาคผนวก)

กติกาเฉพาะเล่ม 2
- สถิติใช้ `tools/sab2_stats.py` (stdlib · ทดสอบเทียบ numpy/ค่าอ้างอิงแล้ว) · โลกจำลองใช้ `tools/sab2_sim.py` (ระบุ seed เสมอ)
- ข้อมูลจริงใช้ `tools/sab2_realdata.py` (`load_closes(split=…)` · `load_funding(split=…)`)
- ตัวเลขเล่ม 1 ใช้ `sab_book.load_figures("sab")` (ห้ามเปิด docs/sab-figures.json ตรง · V11) · backtest ใช้ `tools/sab2_engine.py` (`run`)
- **ช่วงทดสอบสุดท้ายเปิดได้เฉพาะ `ch17.py`** — ปลั๊กอินอื่นที่มีคำว่า `unlock_final` (นอกจาก `unlock_final=False`)
  ถูก `sab_qa.py --book sab2` ฟ้อง (กฎ V11)

หลังแก้: `python3 -I tools/sab_figures.py --book sab2 && python3 -I tools/sab_figures.py --book sab2 --check`
