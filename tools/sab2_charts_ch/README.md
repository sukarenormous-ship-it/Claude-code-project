# สเปกกราฟต่อบทของเล่ม 2 (ปลั๊กอินของ `tools/sab_charts.py --book sab2`)

โฟลเดอร์นี้ว่างโดยตั้งใจ (โครงเฟส 1) · ไฟล์ `chNN.py` หนึ่งไฟล์ต่อบท ใช้ `from sab_charts import *` แบบเล่ม 1
(`tools/sab_charts_ch/README.md`) · คีย์กราฟขึ้นต้นด้วย `sab2-` · ตัวคั่นในหน้า `<!--CHART:sab2-คีย์--><!--/CHART:sab2-คีย์-->`

```python
from sab_charts import *  # noqa: F401,F403

@chart("sab2-phi-ladder")
def _phi_ladder(fig):
    c = fig["ch04"]
    parts = bars(["20 วัน", "60 วัน", "250 วัน"], c["phi"], "φ ที่ประมาณได้")
    return wrap(760, 320, "คำอธิบายภาพสำหรับโปรแกรมอ่านหน้าจอ", parts, "คำบรรยาย", "จำลอง")
```

กราฟของเล่ม 1 (คีย์ `sab-*`) ไม่ถูกโหลดเมื่อรันด้วย `--book sab2` · กราฟอ่านตัวเลขจาก `docs/sab2-figures.json` เท่านั้น
(ไม่โหลดข้อมูลเอง — กฎ V11 ตรวจโฟลเดอร์นี้ด้วย)
