# สเปกกราฟต่อบท (ปลั๊กอินของ `tools/sab_charts.py`)

ไฟล์ `chNN.py` หนึ่งไฟล์ต่อบท:

```python
from sab_charts import chart, wrap, bars, waterfall, lines, steps, dots, grouped_bars, stacked_bars, \
    range_rows, slip_strip, ladder_bars, text, Frame, C, B

@chart("sab-คีย์")
def _k(fig):
    d = fig["ch05"]["บันได"]
    parts = ladder_bars([("บนจอ", d["บนจอ"]), ("ต่อทุน", d["ต่อทุน"])], "หัวกราฟ")
    return wrap(760, 320, "คำอธิบายสำหรับโปรแกรมอ่านจอ", parts, "คำบรรยาย", "สอน")   # สอน | จำลอง | จริง | แนวคิด
```

ตัวเลขทุกตัวอ่านจาก `fig` (= docs/sab-figures.json) · ตรวจด้วย `python3 tools/sab_charts.py --selftest`
