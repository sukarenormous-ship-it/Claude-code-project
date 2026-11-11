#!/usr/bin/env python3
"""
statarb_lab — ห้องทดลองเจ็ดสถานี สำหรับตรวจ "คู่" ของคุณเอง
(เครื่องมือประจำตอนที่ 8 ของชุด "แกะสไลด์ Stat Arb" · ใช้ numpy อย่างเดียว)

คำสั่ง
    python3 tools/statarb_lab.py make-demo demo.csv
        เขียนคู่ตัวอย่างจำลองสี่คู่ (good / drift / break / fake) ลงไฟล์ CSV ไว้ลองมือ

    python3 tools/statarb_lab.py check FILE --y COL --x COL
            [--cost-bps 5] [--train 250] [--entry 2 --exit 0] [--prices raw|log] [--sims 20000]
            [--pnl-out pnl.csv]
        พาคู่ Y, X ผ่านเจ็ดสถานี แต่ละสถานีจบด้วย ✅ / ⚠️ / ❌ แล้วสรุปเป็นคำตัดสินบรรทัดเดียว

    python3 tools/statarb_lab.py scan FILE [--top 15]
        ทดสอบสายจูงของ "ทุกคู่" ในไฟล์ พร้อมบอกว่าลองไปกี่คู่ และกี่คู่จะผ่านได้ด้วยโชคล้วน ๆ

    python3 tools/statarb_lab.py basket FILE --y COL --basket A,B,C
        Y เทียบกับตะกร้าหลายขา โดยใช้เส้นตัดของจำนวนสินทรัพย์นั้น (ยิ่งหลายขา เส้นตัดยิ่งเข้ม)

ไฟล์ CSV: บรรทัดแรกเป็นชื่อคอลัมน์ · หนึ่งแถวต่อหนึ่งแท่ง (วัน) เรียงจากเก่าไปใหม่ ·
มีคอลัมน์วันที่หรือไม่มีก็ได้ · ค่าเป็นราคาดิบ (--prices raw ค่าตั้งต้น) หรือ log price (--prices log)

เจ็ดสถานีของ check (ครึ่งแรกของข้อมูล = "ช่วงศึกษา" · ครึ่งหลัง = "ช่วงสอบ")
    1 ข้อมูล        แถวที่ใช้ได้ · ค่าว่าง · วันที่ซ้ำ · ราคา ≤ 0 · ราคากระโดด · ราคาค้าง
    2 β             OLS y~x · OLS x~y (กลับเศษส่วน) · TLS · β ครึ่งแรกเทียบครึ่งหลัง
    3 สายจูง         Engle-Granger ของครึ่งแรก เทียบเส้นตัดที่จำลองเองสำหรับจำนวนแท่งนี้
    4 จังหวะ         half-life · σ ของ ε · จำนวนครั้งที่ ε ข้ามค่าเฉลี่ยต่อปี
    5 สองครึ่ง       ไม้บรรทัดของครึ่งแรกยังวัดครึ่งหลังได้ไหม (ค่าเฉลี่ยเลื่อนกี่ σ · กว้างขึ้นกี่เท่า)
    6 ต้นทุน         หนึ่งรอบได้ ≈ (entry − exit)·σ/(1+|β|) เทียบกับค่าใช้จ่าย 2c
    7 เดินหน้า       backtest แบบ walk-forward บนครึ่งหลัง ที่ lag 1 และ lag 2 หลังหักต้นทุน

ไม่มีสถานีไหนตัดสินใจด้วยข้อมูลอนาคต: สถานี 3, 4, 6 ใช้เฉพาะครึ่งแรก · สถานี 5 เอาไม้บรรทัดของครึ่งแรก
ไปวัดครึ่งหลัง · สถานี 7 เทรดเฉพาะครึ่งหลัง โดยประมาณค่าจากอดีตแล้วเทรดแท่งถัดไปเท่านั้น · สถานี 2 เทียบ β
ของสองครึ่งเพื่อเตือนอย่างเดียว (β ที่ใช้สร้าง ε มาจากครึ่งแรก)
ทำไมสถานี 7 ไม่ backtest ครึ่งแรกด้วย: คู่ที่ผ่านสถานี 3 (หรือถูกเลือกมาจาก scan) ย่อมดูดีในช่วงที่ใช้เลือก
ต่อให้ไม่มีสายจูงจริง — ช่วงศึกษาจึงพิมพ์ไว้หนึ่งแถวให้เห็นความต่าง แต่ไม่ใช้ตัดสิน

เรียกจากโค้ดก็ได้ (sas_exp8.py ทำแบบนี้):
    import statarb_lab as LAB
    stations = LAB.run_stations(y, x, LAB.options())     # y, x = log price
    code, line, hints = LAB.verdict(stations)             # code = "pass" | "warn" | "fail"

เกณฑ์ตัดสินทุกตัวเป็นค่าคงที่ตั้งชื่อไว้ข้างล่างนี้ — อยากเข้มหรือผ่อนให้แก้ที่เดียว
นี่คือเครื่องมือเพื่อการเรียนรู้ ไม่ใช่คำแนะนำการลงทุน: "ผ่านครบ" แปลว่าควรค่าแก่การศึกษาต่อ
ไม่ได้แปลว่าจะกำไร
"""
import argparse
import csv
import datetime
import functools
import math
import os
import re
import sys
import types
import unicodedata

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sas_core as C  # noqa: E402  (ต้องเพิ่มโฟลเดอร์ของไฟล์นี้ก่อน จึงรันจากโฟลเดอร์ไหนก็ได้)

# ───────────────────────── เกณฑ์ตัดสิน (แก้ที่นี่ที่เดียว) ─────────────────────────

# สถานี 1 — ข้อมูล
MIN_HALF_BARS = 120        # แต่ละครึ่งต้องมีอย่างน้อยเท่านี้ ไม่งั้นการทดสอบสายจูงแทบจับอะไรไม่ได้ → ❌
MIN_TEST_BARS = 126        # ช่วงที่สถานี 7 เทรดจริง (ครึ่งหลัง และหลังหน้าต่าง train แรก) ต้องยาวอย่างน้อยครึ่งปี → ❌
FEW_BARS_WARN = 500        # ข้อมูลน้อยกว่าสองปี: ทดสอบได้ แต่สายจูงจริงก็มีโอกาสสอบตกสูง → ⚠️
JUMP_SIGMAS = 8.0          # ผลตอบแทนแท่งเดียวที่ไกลเกิน 8 เท่าของ sd แบบทนค่าผิดปกติ = "ราคากระโดด" → ⚠️
FLAT_SHARE_WARN = 0.20     # ราคาไม่ขยับเกิน 20% ของแท่ง = ซื้อขายบาง ราคาปิดอาจไม่ใช่ราคาที่เทรดได้ → ⚠️

# สถานี 2 — β (สถานีนี้เตือนอย่างเดียว ตัวตัดสินคือสถานี 3 และ 5)
BETA_GAP_WARN = 0.10       # β จาก x~y (กลับเศษส่วน) ห่างจาก β ของ y~x เกิน 10% = ความสัมพันธ์หลวม → ⚠️
BETA_CHANGE_WARN = 0.15    # β ของครึ่งหลังต่างจากครึ่งแรกเกิน 15% = β ไม่นิ่ง → ⚠️

# สถานี 3 — สายจูง
P_PASS = 0.05              # p-value จำลองต่ำกว่า 5% → ✅
P_WARN = 0.10              # อยู่ระหว่าง 5% กับ 10% → ⚠️ ก้ำกึ่ง · ตั้งแต่ 10% ขึ้นไป → ❌
EG_LAGS = 1                # จำนวนพจน์ Δε ย้อนหลังในการทดสอบ (ตายตัว เส้นตัดจำลองด้วยค่าเดียวกัน)

# สถานี 4 — จังหวะ
HL_MIN_BARS = 1.0          # half-life สั้นกว่า 1 แท่ง = กลับเร็วกว่าที่เทรดทัน (มักเป็น noise ของราคาปิด) → ⚠️
TRAIN_MIN_HALF_LIVES = 8.0  # หน้าต่าง train ควรยาว ≥ 8 เท่าของ half-life จึงจะประมาณ μ, σ ได้นิ่ง → ⚠️
CROSSINGS_MIN_PER_YEAR = 12.0  # ε ข้ามค่าเฉลี่ยน้อยกว่าเดือนละครั้ง = โอกาสครบรอบน้อย → ⚠️

# สถานี 5 — ครึ่งแรกเทียบครึ่งหลัง (วัดด้วยไม้บรรทัดของครึ่งแรก)
SHIFT_MAX_SIGMA = 1.0      # ค่าเฉลี่ยของ ε ครึ่งหลังเลื่อนเกิน 1σ = ไม้บรรทัดเลื่อน
SD_RATIO_MAX = 1.5         # sd ของ ε ครึ่งหลังกว้างเกิน 1.5 เท่า (หรือแคบกว่า 1/1.5) = ไม้บรรทัดผิดขนาด
#   ไม้บรรทัดเพี้ยน + ครึ่งหลังยังสอบผ่านด้วย β ของตัวเอง → ⚠️ (สายจูงยืด ต้องประมาณใหม่เป็นรอบ ๆ)
#   ไม้บรรทัดเพี้ยน + ครึ่งหลังสอบไม่ผ่าน              → ❌ (สายจูงหาย)

# สถานี 6 — ต้นทุน
COST_RATIO_MIN = 1.0       # กำไรที่คาดต่อรอบ ÷ ต้นทุนต่อรอบ ต่ำกว่า 1 = ต้นทุนกินหมด → ❌
COST_RATIO_OK = 3.0        # อยากได้ ≥ 3 เท่า เผื่อ slippage และ σ ที่ประมาณคลาด · ระหว่าง 1 กับ 3 → ⚠️

# สถานี 7 — backtest แบบเดินหน้า
#   สถานีนี้เทรดเฉพาะ "ครึ่งหลัง" — ช่วงที่สถานี 3 ไม่เคยเห็น: backtest บนช่วงที่ใช้ตัดสินว่ามีสายจูง
#   ดูดีเกินจริงเสมอ (คู่ที่ไม่มีสายจูงแต่บังเอิญผ่านสถานี 3 ได้ Sharpe ช่วงนั้นราว +0.9 ทั้งที่ช่วงสอบราว 0)
#   ช่วงศึกษาถูกพิมพ์ไว้หนึ่งแถวให้เทียบเท่านั้น ไม่ใช้ตัดสิน
REFIT_BARS = 21            # ประมาณ α, β, μ, σ ใหม่ทุก 21 แท่ง (ราวหนึ่งเดือน)
SHARPE_Z = 1.645           # ผ่านเมื่อ Sharpe (lag 2) − 1.645/√ปี > 0 คือยังเป็นบวกแม้หักความคลาดด้านเดียว 5%
MIN_TRADES = 5             # น้อยกว่า 5 ไม้ ต่อให้ชนะทุกไม้ก็ยังแยกจากการโยนเหรียญไม่ได้ (0.5⁴ = 6% > 5%) → ⚠️
#   5 ไม้คือขั้นต่ำสุดทางสถิติ ไม่ใช่ "พอ" — ผลลัพธ์จึงพิมพ์ความคลาดของอัตราชนะจากจำนวนไม้จริงไว้ด้วยเสมอ

# ค่าตั้งต้นของคำสั่ง
DEFAULT_COST_BPS = 5.0     # ต้นทุนเที่ยวเดียวต่อขา (bps ของมูลค่าที่ซื้อขาย)
DEFAULT_TRAIN = 250        # หน้าต่างประมาณค่าของ walk-forward (แท่ง)
DEFAULT_ENTRY = 2.0        # เข้าเมื่อ |z| ≥ 2 (z วัดด้วย σ ที่ประมาณจากหน้าต่าง train ไม่ใช่ σ จริง)
DEFAULT_EXIT = 0.0         # ออกเมื่อ z กลับถึงค่าเฉลี่ย
DEFAULT_SIMS = 20000       # จำนวนโลกจำลองที่ใช้หาเส้นตัดและ p-value (เส้นตัด 5% คลาดราว ±0.01–0.02
                           # พอให้ทศนิยมสองตำแหน่งที่พิมพ์ไม่แกว่ง · 4,000 โลกแกว่งได้ถึง ±0.05)
MIN_SIMS, MAX_SIMS = 500, 200000   # น้อยกว่านี้เส้นตัดแกว่งจนใช้ไม่ได้ · มากกว่านี้รอนานเกินไป
MAX_LEGS = 10              # ตะกร้าไม่เกิน 10 ขา (ขายิ่งมาก น้ำหนักยิ่งพอดีกับอดีต และการจำลองยิ่งช้า)
NULL_SEED_OFFSET = 800     # seed ของโลกจำลอง (C.rng(800 + จำนวนสินทรัพย์)) — รันกี่ครั้งก็ได้เลขเดิม

OK, WARN, FAIL = "✅", "⚠️", "❌"
WIDTH = 88                 # ความกว้างสูงสุดของบรรทัดผลลัพธ์ (พอดีกรอบ <pre> ของหนังสือ) — ยาวกว่านี้ตัดขึ้นบรรทัดใหม่
RULE = "-" * WIDTH


def thresholds():
    """เกณฑ์ทั้งหมดในรูป dict (sas_exp8.figures() ส่งออกให้เนื้อหาตอนที่ 8 อ้างตรงตัว)"""
    return {
        "min_half_bars": MIN_HALF_BARS, "min_test_bars": MIN_TEST_BARS, "few_bars_warn": FEW_BARS_WARN,
        "jump_sigmas": JUMP_SIGMAS, "flat_share_warn": FLAT_SHARE_WARN,
        "beta_gap_warn": BETA_GAP_WARN, "beta_change_warn": BETA_CHANGE_WARN,
        "p_pass": P_PASS, "p_warn": P_WARN, "eg_lags": EG_LAGS,
        "hl_min_bars": HL_MIN_BARS, "train_min_half_lives": TRAIN_MIN_HALF_LIVES,
        "crossings_min_per_year": CROSSINGS_MIN_PER_YEAR,
        "shift_max_sigma": SHIFT_MAX_SIGMA, "sd_ratio_max": SD_RATIO_MAX,
        "cost_ratio_min": COST_RATIO_MIN, "cost_ratio_ok": COST_RATIO_OK,
        "refit_bars": REFIT_BARS, "sharpe_z": SHARPE_Z, "min_trades": MIN_TRADES,
        "default_cost_bps": DEFAULT_COST_BPS, "default_train": DEFAULT_TRAIN,
        "default_entry": DEFAULT_ENTRY, "default_exit": DEFAULT_EXIT, "default_sims": DEFAULT_SIMS,
        "min_sims": MIN_SIMS, "max_sims": MAX_SIMS, "max_legs": MAX_LEGS,
    }


class LabError(SystemExit):
    """ข้อผิดพลาดที่อธิบายให้ผู้ใช้แก้เองได้ (ไฟล์ไม่พบ · ไม่มีคอลัมน์ · ข้อมูลไม่พอ)
    เป็นลูกของ SystemExit: โค้ดที่เรียก load_columns ตรง ๆ (snippet ของแต่ละตอน) ไม่ต้องดักเอง —
    ถ้าไม่มีใครดัก Python พิมพ์ "❌ ข้อความ" แล้วจบด้วยรหัส 1 แทน traceback · main() ยังดักได้ตามปกติ"""

    def __init__(self, msg):
        super().__init__(msg)
        self.code = f"{FAIL} {msg}"          # สิ่งที่ Python พิมพ์เมื่อไม่มีใครดัก (str(e) ยังเป็น msg)


def options(cost_bps=DEFAULT_COST_BPS, train=DEFAULT_TRAIN, entry=DEFAULT_ENTRY, exit=DEFAULT_EXIT,
            sims=DEFAULT_SIMS):
    """ชุดตัวเลือกของ check ในรูปที่เรียกจากโค้ดได้ (sas_exp8 ใช้ตอนจำลองหลายร้อยโลก)"""
    return types.SimpleNamespace(cost_bps=float(cost_bps), train=int(train), entry=float(entry),
                                 exit=float(exit), sims=int(sims))


# ───────────────────────── อ่านและทำความสะอาด CSV ─────────────────────────

MISSING_WORDS = {"", "na", "n/a", "#n/a", "nan", "null", "none", "-", "."}
DATE_NAMES = {"date", "datetime", "time", "timestamp", "วันที่"}
NOT_PRICE_NAMES = {"index", "unnamed: 0", "volume", "vol"}      # คอลัมน์ที่ scan ไม่ควรนับเป็นราคา
DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M")


def parse_number(cell, decimal_comma=False):
    """ข้อความในช่อง → float · ค่าว่าง ข้อความ หรือ inf/NaN → None
    มีทั้ง "," และ "." → ตัวที่อยู่ท้ายสุดคือจุดทศนิยม ("1,234.56" และ "1.234,56" = 1234.56)
    มีแค่ "," → จุดทศนิยมถ้าไฟล์คั่นด้วย ";" (แบบยุโรป) ไม่งั้นเป็นตัวคั่นหลักพัน"""
    s = cell.strip().replace(" ", "").replace(" ", "")
    if s.lower() in MISSING_WORDS:
        return None
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    else:
        s = s.replace(",", ".") if decimal_comma else s.replace(",", "")
    try:
        v = float(s)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def read_table(path):
    """อ่าน CSV ทั้งไฟล์ → (หัวคอลัมน์, แถวข้อมูล, จำนวนบรรทัดว่างที่ข้าม, ตัวคั่น)"""
    if not os.path.isfile(path):
        raise LabError(f'ไม่พบไฟล์ "{path}" — ตรวจชื่อไฟล์ หรือสร้างไฟล์ตัวอย่างด้วย  make-demo demo.csv')
    try:
        with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
            text = fh.read()
        first = next((ln for ln in text.splitlines() if ln.strip()), "")
        delim = max(",;\t|", key=first.count) if first else ","
        raw = list(csv.reader(text.splitlines(), delimiter=delim))
    except (OSError, csv.Error) as e:
        raise LabError(f'อ่านไฟล์ "{path}" ไม่ได้: {e}') from None
    rows = [[c.strip() for c in r] for r in raw if any(c.strip() for c in r)]
    if len(rows) < 2:
        raise LabError(f'ไฟล์ "{path}" ไม่มีข้อมูล (ต้องมีบรรทัดหัวคอลัมน์ และข้อมูลอย่างน้อยหนึ่งแถว)')
    header = rows[0]
    if all(parse_number(h) is not None for h in header):
        raise LabError("บรรทัดแรกของไฟล์เป็นตัวเลขล้วน — ต้องมีชื่อคอลัมน์ในบรรทัดแรก (เช่น date,AAA,BBB)")
    return header, rows[1:], len(raw) - len(rows), delim


def find_column(header, name):
    """ตำแหน่งของคอลัมน์ชื่อ name (ตรงตัวก่อน แล้วค่อยไม่สนตัวพิมพ์เล็กใหญ่)"""
    for match in ([i for i, h in enumerate(header) if h == name],
                  [i for i, h in enumerate(header) if h.lower() == name.lower()]):
        if len(match) == 1:
            return match[0]
        if len(match) > 1:
            raise LabError(f'มีคอลัมน์ชื่อ "{name}" มากกว่าหนึ่งคอลัมน์ — ตั้งชื่อให้ไม่ซ้ำกันก่อน')
    odd = (" · ชื่อคอลัมน์มีตัวอักษรที่อ่านไม่ออก (�) — บันทึกไฟล์เป็น CSV แบบ UTF-8 แล้วลองใหม่"
           if any("�" in h for h in header) else "")
    raise LabError(f'ไม่พบคอลัมน์ "{name}" — คอลัมน์ที่มีในไฟล์: {", ".join(h for h in header if h)}{odd}')


def find_date_column(header, rows):
    """คอลัมน์วันที่: ดูจากชื่อก่อน ไม่งั้นถือว่าคอลัมน์แรกเป็นวันที่ถ้าส่วนใหญ่ไม่ใช่ตัวเลข · ไม่มี → None"""
    for i, h in enumerate(header):
        if h.lower() in DATE_NAMES:
            return i
    head = [r[0] for r in rows[:50] if r]
    if head and sum(parse_number(c) is None for c in head) > len(head) / 2:
        return 0
    return None


def be_to_ce(s):
    """ปี พ.ศ. → ค.ศ.: เลขปีสี่หลักที่เกิน 2400 ถือเป็น พ.ศ. แล้วลบ 543 (29/02/2567 → 29/02/2024)
    ต้องทำก่อน strptime เพราะ 2567 ไม่ใช่ปีอธิกสุรทินแบบสากล 29/02/2567 จึงอ่านไม่ออกทั้งคอลัมน์"""
    fix = lambda m: str(int(m.group(1)) - 543) if int(m.group(1)) > 2400 else m.group(1)
    if re.fullmatch(r"\d{8}", s[:8]) and not s[8:9].isdigit():             # 25670229 (แบบ %Y%m%d)
        return fix(re.match(r"(\d{4})", s)) + s[4:]
    return re.sub(r"(?<!\d)(\d{4})(?!\d)", fix, s)


def parse_dates(strings):
    """แปลงวันที่ทั้งคอลัมน์ด้วยรูปแบบเดียวกัน · อ่านไม่ออกสักแถว → None (จะเชื่อลำดับในไฟล์แทน)
    ลองทั้งข้อความเต็ม และ 10 ตัวอักษรแรก (วันที่ที่มีเวลาหรือเขตเวลาต่อท้าย เช่น 2020-01-02 00:00:00+07:00)
    ปี พ.ศ. (เช่น 15/01/2567) ถูกแปลงเป็น ค.ศ. ก่อน"""
    strings = [be_to_ce(s) for s in strings]
    for cut in (None, 10):
        for fmt in DATE_FORMATS:
            try:
                return [datetime.datetime.strptime(s[:cut], fmt) for s in strings]
            except ValueError:
                continue
    return None


def load_columns(path, names, prices):
    """อ่านคอลัมน์ราคาที่ต้องการ → ทิ้งแถวเสีย → เรียงเวลา → log price
    names = None หมายถึง "ทุกคอลัมน์ที่เป็นตัวเลข" (ใช้กับ scan)
    คืน (ชื่อคอลัมน์, อาร์เรย์ n×k ของ log price, รายการวันที่หรือ None, รายงานว่าทำอะไรไปบ้าง)"""
    header, rows, blank, delim = read_table(path)
    dcol = find_date_column(header, rows)
    dec = delim == ";"
    rep = {"file": os.path.basename(path), "rows_read": len(rows), "blank_lines": blank, "missing": 0,
           "nonpos": 0, "dup_dates": 0, "reordered": None, "skipped_cols": [], "scale_note": None,
           "all_small": False, "odd_chars": "�" in "".join(header),
           "date_col": header[dcol] if dcol is not None else None, "first": None, "last": None}
    if names is None:
        idx = []
        for i, h in enumerate(header):
            if i == dcol or not h or h.lower() in NOT_PRICE_NAMES:
                continue
            good = sum(parse_number(r[i], dec) is not None for r in rows if i < len(r))
            (idx if good >= 0.8 * len(rows) else rep["skipped_cols"]).append(i)
        rep["skipped_cols"] = [header[i] for i in rep["skipped_cols"]]
        if len(idx) < 2:
            raise LabError("ไฟล์นี้มีคอลัมน์ราคาที่เป็นตัวเลขไม่ถึง 2 คอลัมน์ — scan ต้องมีอย่างน้อยสองสินทรัพย์")
    else:
        idx = [find_column(header, nm) for nm in names]
        if len(set(idx)) < len(idx):
            raise LabError("เลือกคอลัมน์เดียวกันซ้ำ — Y และ X (หรือขาในตะกร้า) ต้องเป็นคนละสินทรัพย์")
    keep, seen = [], set()
    for r in rows:
        vals = [parse_number(r[i], dec) if i < len(r) else None for i in idx]
        day = r[dcol] if dcol is not None and dcol < len(r) else None
        if any(v is None for v in vals) or day == "":
            rep["missing"] += 1
        elif prices == "raw" and any(v <= 0 for v in vals):
            rep["nonpos"] += 1
        elif day is not None and day in seen:
            rep["dup_dates"] += 1
        else:
            seen.add(day)
            keep.append((day, vals))
    if not keep:
        raise LabError("ไม่เหลือแถวที่ใช้ได้เลยหลังทิ้งค่าว่าง/ราคา ≤ 0 — ตรวจชื่อคอลัมน์และตัวเลือก --prices")
    keep = order_by_date(keep, rep)
    dates = [d for d, _ in keep] if dcol is not None else None
    mat = np.array([v for _, v in keep], dtype=float)
    if prices == "raw":
        if rep["nonpos"] > 0.2 * rep["rows_read"]:
            rep["scale_note"] = "ราคา ≤ 0 เยอะผิดปกติ — ถ้าไฟล์เก็บ log price อยู่แล้ว ให้ใช้ --prices log"
        rep["all_small"] = bool(np.max(mat) < 15.0)
        mat = np.log(mat)
    elif float(np.max(np.abs(mat))) > 15.0:
        rep["scale_note"] = "ค่าใหญ่เกินกว่าจะเป็น log price — ถ้าไฟล์เก็บราคาดิบ ให้ใช้ --prices raw"
    if dates:
        rep["first"], rep["last"] = dates[0], dates[-1]
    return [header[i] for i in idx], mat, dates, rep


def order_by_date(keep, rep):
    """เรียงแถวจากเก่าไปใหม่ถ้าอ่านวันที่ออก (ไฟล์ที่ดาวน์โหลดมามักเรียงใหม่ → เก่า) และจดไว้ว่าทำ"""
    if keep[0][0] is None:
        return keep
    stamps = parse_dates([d for d, _ in keep])
    if stamps is None:
        rep["reordered"] = "unparsed"
        return keep
    if all(a < b for a, b in zip(stamps, stamps[1:])):
        return keep
    if all(a > b for a, b in zip(stamps, stamps[1:])):
        rep["reordered"] = "reversed"
        return keep[::-1]
    rep["reordered"] = "sorted"
    order = sorted(range(len(keep)), key=lambda i: stamps[i])
    return [keep[i] for i in order]


# ───────────────────────── ตัวช่วยคำนวณและจัดรูป ─────────────────────────

def longest_run(mask):
    """ความยาวของช่วง True ที่ติดกันยาวที่สุด"""
    best = cur = 0
    for v in mask:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def series_health(logp):
    """ตรวจอนุกรมราคาเส้นเดียว: ตำแหน่งที่ราคากระโดด · สัดส่วนแท่งที่ราคาไม่ขยับ · ช่วงค้างยาวสุด"""
    r = np.diff(logp)
    med = float(np.median(r))
    scale = 1.4826 * float(np.median(np.abs(r - med)))      # sd แบบทนค่าผิดปกติ (จาก MAD)
    if scale == 0.0:
        scale = float(np.std(r))
    jumps = np.flatnonzero(np.abs(r - med) > JUMP_SIGMAS * scale) + 1 if scale > 0 else np.array([], int)
    flat = r == 0.0
    return {"jumps": jumps, "ret": r, "flat_share": float(flat.mean()) if len(r) else 0.0,
            "flat_run": longest_run(flat)}


@functools.lru_cache(maxsize=32)
def null_eg(n_obs, n_vars, n_sim):
    """ค่า Engle-Granger ของโลกที่ "ไม่มีสายจูง" (random walk อิสระ) สำหรับจำนวนแท่งและจำนวนสินทรัพย์นี้
    จำไว้ใช้ซ้ำ (เส้นตัดขึ้นกับ n_obs, n_vars, lags — ต้องจำลองด้วยค่าเดียวกับตัวทดสอบจริง)"""
    return C.mc_null_eg(n_obs, n_vars, n_sim=n_sim, lags=EG_LAGS, g=C.rng(NULL_SEED_OFFSET + n_vars))


def cutoff_noise(null_sorted, q):
    """ความคลาดของเส้นตัด (ครึ่งความกว้างของช่วง 90%) เพราะจำลองโลกได้จำนวนจำกัด — จากสถิติลำดับ"""
    n = len(null_sorted)
    half = 1.645 * math.sqrt(n * q * (1 - q))
    lo, hi = int(max(0, math.floor(n * q - half))), int(min(n - 1, math.ceil(n * q + half)))
    return float(null_sorted[hi] - null_sorted[lo]) / 2.0


def leash_test(y, X, n_sim):
    """Engle-Granger + เส้นตัดและ p-value จากการจำลองที่ขนาดตัวอย่างเดียวกัน"""
    r = C.eg_test(y, X, lags=EG_LAGS)
    null = null_eg(r["n_obs"], r["n_vars"], n_sim)
    r["cv"] = C.crit_values(null)
    r["p"] = C.p_value(r["adf"], null)
    r["cv_noise"] = cutoff_noise(null, 0.05)
    r["n_sim"] = n_sim
    return r


def crossings_per_year(eps):
    """จำนวนครั้งที่ ε ข้ามค่าเฉลี่ยของตัวเอง ต่อปี (252 แท่ง)"""
    side = np.sign(eps - np.mean(eps))
    side = side[side != 0]
    return float(np.sum(side[1:] != side[:-1])) / (len(eps) / C.DAYS_PER_YEAR)


def fmt_p(p):
    """p-value จำลอง: ค่าที่เล็กมากพิมพ์ว่า "< 0.001" (จำลองได้จำนวนโลกจำกัด จึงไม่มี p = 0 จริง ๆ)
    ตั้งแต่ 0.1 ขึ้นไปพิมพ์สองตำแหน่ง: ทศนิยมตำแหน่งที่สามของ p ขนาดนั้นแกว่งตามการสุ่ม (±0.003 ที่ 20,000 โลก)"""
    if not math.isfinite(p):
        return "n/a"
    return "< 0.001" if p < 0.001 else f"{p:.3f}" if p < 0.1 else f"{p:.2f}"


def rel_p(p):
    """p-value พร้อมเครื่องหมายเทียบ สำหรับแทรกในประโยค เช่น '< 0.001' หรือ '= 0.651'"""
    return fmt_p(p) if p < 0.001 or not math.isfinite(p) else "= " + fmt_p(p)


def fmt_change(v):
    """สัดส่วนการเปลี่ยนแปลงแบบมีเครื่องหมาย (ไม่พิมพ์ -0.0%)"""
    return "0.0%" if abs(v) < 0.0005 else f"{v:+.1%}"


def shown_width(s):
    """จำนวนคอลัมน์ที่ข้อความกินบนจอ: สระบน/ล่างและวรรณยุกต์ไทยไม่กินที่ · อีโมจิกินสองช่อง"""
    return sum(0 if unicodedata.category(ch) in ("Mn", "Me", "Cf") else 2 if ch in "✅❌⚠" else 1 for ch in s)


def unbreakable(body):
    """แบ่งข้อความเป็นชิ้นที่ห้ามตัดกลาง: ไม้ยมก (ๆ) ติดกับคำหน้า · ตัวเลขติดกับหน่วยสั้น ๆ ที่ตามมา
    ("250 แท่ง") · เครื่องหมายเทียบติดกับสองข้าง ("p < 0.05")"""
    ops = ("=", "<", ">", "≥", "≤")
    out = []
    for word in body.split(" "):
        last = out[-1].rsplit(" ", 1)[-1] if out else ""
        unit = last[-1:].isdigit() and len(word) <= 8 and word[:1] not in "(·→—"
        if out and (word == "ๆ" or word in ops or last in ops or unit):
            out[-1] += " " + word
        else:
            out.append(word)
    return out


def wrap_line(line, hang):
    """ตัดบรรทัดที่ยาวเกิน WIDTH ตรงช่องว่าง · บรรทัดต่อเยื้องเข้า hang ช่อง"""
    if shown_width(line) <= WIDTH:
        return [line]
    body = line.lstrip(" ")
    out, cur, first = [], line[:len(line) - len(body)], True
    for piece in unbreakable(body):
        if not first and shown_width(cur + " " + piece) > WIDTH:
            out.append(cur)
            cur = " " * hang + piece
        else:
            cur = cur + piece if first else cur + " " + piece
        first = False
    return out + [cur]


def emit(lines):
    """พิมพ์ผลลัพธ์ทั้งชุด · แต่ละรายการเป็นข้อความ หรือ (ข้อความ, ระยะเยื้องของบรรทัดต่อ)"""
    for item in lines:
        text, hang = item if isinstance(item, tuple) else (item, len(item) - len(item.lstrip(" ")) + 2)
        print("\n".join(wrap_line(text, hang)))


def fmt_cv(r):
    """บรรทัดเส้นตัด 1% / 5% / 10%"""
    cv = r["cv"]
    return f"1%: {cv[0.01]:.2f}   5%: {cv[0.05]:.2f}   10%: {cv[0.1]:.2f}"


def station(no, short, title, status, rows, read, **metrics):
    """ผลของหนึ่งสถานี: สถานะ + บรรทัดตัวเลข + คำอ่านหนึ่งบรรทัด + ตัวเลขดิบ (m) ไว้ให้โค้ดอื่นใช้ต่อ"""
    return {"no": no, "short": short, "title": title, "status": status, "rows": rows, "read": read,
            "m": metrics}


# ───────────────────────── เจ็ดสถานี ─────────────────────────

def station_data(y, x, opt, rep=None, dates=None):
    """สถานี 1 — ข้อมูลพอและสะอาดพอจะทดสอบไหม (y, x = log price ที่ทิ้งแถวเสียแล้ว)
    rep = รายงานของ load_columns (ไม่มี = ข้อมูลมาจากโค้ดโดยตรง) · dates ใช้บอกวันที่ของราคากระโดด"""
    n = len(y)
    rep = rep or {"rows_read": n, "missing": 0, "nonpos": 0, "dup_dates": 0, "blank_lines": 0}
    hy, hx = series_health(y), series_health(x)
    n_jump = len(hy["jumps"]) + len(hx["jumps"])
    dropped = rep["missing"] + rep["nonpos"] + rep["dup_dates"]
    flat_run = max(hy["flat_run"], hx["flat_run"])
    rows = [f"แถว: อ่านได้ {rep['rows_read']:,} · ใช้ได้ {n:,} · ทิ้ง {dropped:,}",
            f"ที่ทิ้ง: ค่าว่างหรือไม่ใช่ตัวเลข {rep['missing']:,} · ราคาไม่เป็นบวก {rep['nonpos']:,} · "
            f"วันที่ซ้ำ {rep['dup_dates']:,}"
            + (f" · ข้ามบรรทัดว่าง {rep['blank_lines']:,}" if rep["blank_lines"] else ""),
            f"ราคากระโดดเกิน {JUMP_SIGMAS:g} sd: Y {len(hy['jumps'])} จุด · X {len(hx['jumps'])} จุด",
            f"แท่งที่ราคาไม่ขยับ: Y {hy['flat_share']:.1%} · X {hx['flat_share']:.1%} · "
            f"ค้างติดกันยาวสุด {flat_run} แท่ง"]
    order_note = {"reversed": "วันที่ในไฟล์เรียงจากใหม่ไปเก่า → กลับลำดับให้แล้ว",
                  "sorted": "วันที่ในไฟล์ไม่เรียงลำดับ → เรียงจากเก่าไปใหม่ให้แล้ว",
                  "unparsed": "อ่านรูปแบบวันที่ไม่ออก → ใช้ลำดับแถวตามไฟล์ (ต้องเรียงจากเก่าไปใหม่)"}
    if rep.get("reordered"):
        rows.append(order_note[rep["reordered"]])
    if rep.get("all_small"):
        rows.append("ค่าทุกตัวต่ำกว่า 15: ถ้าเป็น log price อยู่แล้วต้องใส่ --prices log (ราคาจริงไม่ต้องทำอะไร)")
    if n_jump:
        rows.append("จุดที่กระโดด: " + ", ".join(jump_list(hy, "Y", dates) + jump_list(hx, "X", dates)))
    stop = []
    if n // 2 < MIN_HALF_BARS:
        stop.append(f"มีแค่ {n:,} แท่ง — ต้องมีอย่างน้อย {2 * MIN_HALF_BARS:,} แท่ง (ครึ่งละ {MIN_HALF_BARS})")
    elif n - exam_start(n, opt.train) < MIN_TEST_BARS:
        stop.append(f"มี {n:,} แท่ง แต่ช่วงสอบที่เทรดได้ (ครึ่งหลัง หลังหน้าต่าง train {opt.train:,} แท่ง) "
                    f"เหลือไม่ถึง {MIN_TEST_BARS} แท่ง — หาข้อมูลเพิ่ม หรือลด --train")
    if flat_run + 1 >= opt.train:
        stop.append(f"ราคาค้างเป็นค่าเดียวติดกัน {flat_run + 1:,} แท่ง (ยาวกว่าหน้าต่าง train) — คำนวณ β ไม่ได้")
    notes = []
    if dropped:
        notes.append(f"ทิ้งแถวเสีย {dropped:,} แถว")
    if n_jump:
        notes.append(f"ราคากระโดด {n_jump} จุด (ตรวจ split / ปันผล / ข้อมูลผิด)")
    if max(hy["flat_share"], hx["flat_share"]) > FLAT_SHARE_WARN:
        notes.append("ราคาไม่ขยับบ่อย (สภาพคล่องต่ำ ราคาปิดอาจเทรดไม่ได้จริง)")
    if n < FEW_BARS_WARN:
        notes.append(f"ข้อมูลน้อยกว่า {FEW_BARS_WARN} แท่ง (สายจูงจริงก็สอบตกได้ง่าย)")
    if rep.get("scale_note"):
        notes.append(rep["scale_note"])
    unparsed = rep.get("reordered") == "unparsed"
    if unparsed:
        notes.append("อ่านวันที่ไม่ออก (ตรวจเองว่าแถวเรียงจากเก่าไปใหม่)")
    if stop:
        return station(1, "ข้อมูล", "ข้อมูล", FAIL, rows, "ไปต่อไม่ได้: " + " · ".join(stop), n=n,
                       dates_unparsed=unparsed)
    if notes:
        read = f"ใช้ได้ {n:,} แท่ง แต่มีข้อสังเกต: " + " · ".join(notes)
    else:
        read = f"ข้อมูลสะอาด ใช้ได้ครบ {n:,} แท่ง"
    return station(1, "ข้อมูล", "ข้อมูล", WARN if notes else OK, rows, read, n=n, dropped=dropped, jumps=n_jump,
                   dates_unparsed=unparsed)


def jump_list(h, leg, dates=None, limit=3):
    """รายการราคากระโดดของขาหนึ่ง (ไม่เกิน limit จุด): ขา · วันที่หรือลำดับแท่ง · ขนาดการเปลี่ยนแปลง"""
    items = [f"{leg} {dates[t] if dates else 'แท่งที่ ' + str(int(t) + 1)} ({math.expm1(h['ret'][t - 1]):+.0%})"
             for t in h["jumps"][:limit]]
    if len(h["jumps"]) > limit:
        items.append(f"{leg} อีก {len(h['jumps']) - limit} จุด")
    return items


def fit_first_half(y, x):
    """ไม้บรรทัดของช่วงศึกษา: α, β (OLS y~x) และ σ ของ ε จากครึ่งแรก · ครึ่งหลัง = h แท่งสุดท้าย"""
    h = len(y) // 2
    y1, x1, y2, x2 = y[:h], x[:h], y[-h:], x[-h:]
    fit = C.ols(y1, x1)
    a, b = float(fit["coef"][0]), float(fit["coef"][1])
    if float(np.std(fit["resid"])) <= 1e-9 * float(np.std(y1)):
        raise LabError("Y เขียนได้จาก X แบบเป๊ะ ๆ (เช่น ใส่สินทรัพย์เดียวกันสองคอลัมน์) — ไม่มีสเปรดให้ทดสอบ")
    return {"h": h, "y1": y1, "x1": x1, "y2": y2, "x2": x2, "alpha": a, "beta": b,
            "eps1": fit["resid"], "sd1": float(np.std(fit["resid"], ddof=1)), "r2": float(fit["r2"])}


def station_beta(f):
    """สถานี 2 — β สามวิธี (ถ้าสามวิธีเถียงกัน แปลว่าเส้นตรงนี้หลวม) + β ครึ่งแรกเทียบครึ่งหลัง"""
    b = f["beta"]
    slope_xy = float(C.ols(f["x1"], f["y1"])["coef"][1])
    b_inv = 1.0 / slope_xy if slope_xy != 0 else float("inf")
    b_tls = float(C.tls_beta(f["y1"], f["x1"])[1])
    b2 = float(C.ols(f["y2"], f["x2"])["coef"][1])
    gap = abs(b_inv - b) / abs(b) if b != 0 and math.isfinite(b_inv) else float("inf")
    change = (b2 - b) / abs(b) if b != 0 else float("inf")
    rows = ["method              beta",
            f"OLS y~x          {b:7.3f}   <- ใช้ตัวนี้สร้าง ε = Y - alpha - beta*X",
            f"OLS x~y -> 1/b   {b_inv:7.3f}",
            f"TLS              {b_tls:7.3f}   (สามวิธีห่างกันสุด {gap:.1%})",
            f"first half       {b:7.3f}",
            f"second half      {b2:7.3f}   (เปลี่ยน {fmt_change(change)})"]
    notes = []
    if b <= 0:
        notes.append("β ไม่เป็นบวก → สองตัวนี้ไม่ได้วิ่งไปด้วยกัน การ 'ซื้อตัวหนึ่ง ขายอีกตัว' ไม่ได้ตัดตลาดออก")
    if gap > BETA_GAP_WARN:
        notes.append(f"สามวิธีให้ β ห่างกัน {gap:.0%} (เกิน {BETA_GAP_WARN:.0%}) → ความสัมพันธ์หลวม "
                     "β ขึ้นกับว่าเลือกวิธีไหน")
    if abs(change) > BETA_CHANGE_WARN:
        notes.append(f"β เปลี่ยน {change:+.0%} ระหว่างสองครึ่ง (เกิน {BETA_CHANGE_WARN:.0%}) → β ไม่นิ่ง "
                     "อย่าใช้ β ตัวเดียวทั้งช่วง")
    read = " · ".join(notes) if notes else (
        f"สามวิธีให้ β ใกล้กัน (ห่างกันสุด {gap:.1%}) · สองครึ่งต่างกัน {abs(change):.1%} "
        f"(ไม่เกิน {BETA_CHANGE_WARN:.0%}) → β นิ่งพอ")
    return station(2, "β", "β สามวิธี และ β นิ่งไหม", WARN if notes else OK, rows, read,
                   beta=b, beta_inv=b_inv, beta_tls=b_tls, beta2=b2, gap=gap, change=change)


def station_leash(f, opt):
    """สถานี 3 — สายจูง: Engle-Granger ของครึ่งแรก เทียบเส้นตัดจำลองที่จำนวนแท่งเดียวกัน"""
    r = leash_test(f["y1"], f["x1"], opt.sims)
    adf, p = r["adf"], r["p"]
    rows = [f"EG statistic = {adf:.2f}   (ครึ่งแรก {f['h']:,} แท่ง · lags = {EG_LAGS})",
            f"cut-offs       {fmt_cv(r)}",
            f"p-value      {rel_p(p)}   (จำลอง {opt.sims:,} โลกที่ไม่มีสายจูง · "
            f"เส้นตัด 5% คลาดได้ราว ±{r['cv_noise']:.2f})"]
    if not math.isfinite(adf):
        status = FAIL
        read = "ทดสอบไม่ได้ (Y เขียนได้จาก X เป๊ะ หรือข้อมูลสั้นเกินไป) — ตรวจว่าไม่ได้ใส่สินทรัพย์เดียวกันสองครั้ง"
    elif p < P_PASS:
        status = OK
        read = (f"ติดลบกว่าเส้นตัด 5% (p {rel_p(p)}) → มีหลักฐานว่า ε ถูกดึงกลับ "
                "(โลกที่ไม่มีสายจูงแทบไม่ให้ค่าแบบนี้)")
    elif p < P_WARN:
        status = WARN
        read = f"อยู่ระหว่างเส้นตัด 5% กับ 10% (p = {p:.3f}) → ก้ำกึ่ง ยังไม่พอจะเชื่อว่ามีสายจูง"
    else:
        status = FAIL
        read = (f"ติดลบไม่ถึงเส้นตัด (p = {p:.3f}) → แยกไม่ออกจากสองตัวที่แค่เดินไปทางเดียวกัน "
                "= ไม่มีหลักฐานของสายจูง")
    return station(3, "สายจูง", "สายจูง (Engle-Granger)", status, rows, read,
                   adf=adf, p=p, cv5=r["cv"][0.05], cv1=r["cv"][0.01], cv10=r["cv"][0.1], cv_noise=r["cv_noise"])


def station_rhythm(f, opt, leash_status):
    """สถานี 4 — จังหวะของ ε ในครึ่งแรก: half-life · σ · จำนวนครั้งที่ข้ามค่าเฉลี่ยต่อปี"""
    ar = C.fit_ar1(f["eps1"])
    hl = float(ar["half_life"])
    cross = crossings_per_year(f["eps1"])
    per_hl = opt.train / hl if math.isfinite(hl) and hl > 0 else float("inf")
    hl_txt = ("— (สถานี 3 ไม่ผ่าน)" if leash_status == FAIL       # ไม่มีสายจูง = ไม่มี half-life ให้อ่าน
              else f"{hl:.1f} แท่ง" if math.isfinite(hl) else "inf แท่ง")
    rows = [f"half-life = {hl_txt} · σ ของ ε = {f['sd1']:.2%} · ε ข้ามค่าเฉลี่ย {cross:.0f} ครั้งต่อปี",
            f"หน้าต่าง train {opt.train:,} แท่ง = "
            + ("— เท่าของ half-life" if leash_status == FAIL else f"{per_hl:.1f} เท่าของ half-life")]
    if not math.isfinite(hl):
        status, read = FAIL, "ประมาณ half-life ไม่ได้ (φ ≥ 1) → ε ไม่ถูกดึงกลับเลย"
    elif leash_status == FAIL:
        status = WARN
        read = ("สถานี 3 ไม่ผ่าน → เลขพวกนี้ยังเชื่อไม่ได้ (random walk แท้ ๆ ก็ให้ half-life "
                "เป็นเลขดูดีได้เกือบทุกครั้ง)")
    else:
        notes = []
        if hl < HL_MIN_BARS:
            notes.append(f"half-life สั้นกว่า {HL_MIN_BARS:g} แท่ง → กลับเร็วกว่าที่เทรดทัน "
                         "อาจเป็นแค่ noise ของราคาปิด")
        if per_hl < TRAIN_MIN_HALF_LIVES:
            notes.append(f"หน้าต่าง train ยาวแค่ {per_hl:.1f} เท่าของ half-life (อยากได้ ≥ {TRAIN_MIN_HALF_LIVES:g}) "
                         "→ μ, σ ที่ประมาณได้จะแกว่ง ลองเพิ่ม --train")
        if cross < CROSSINGS_MIN_PER_YEAR:
            notes.append(f"ε ข้ามค่าเฉลี่ยแค่ {cross:.0f} ครั้งต่อปี (น้อยกว่า {CROSSINGS_MIN_PER_YEAR:g}) "
                         "→ โอกาสครบรอบน้อย")
        status = WARN if notes else OK
        read = " · ".join(notes) if notes else (f"กลับครึ่งทางในราว {hl:.0f} แท่ง ข้ามค่าเฉลี่ยราว "
                                                f"{cross:.0f} ครั้งต่อปี → มีจังหวะให้เทรด และ train ยาวพอ")
    return station(4, "จังหวะ", "จังหวะของ ε", status, rows, read,
                   half_life=hl, sigma=f["sd1"], crossings=cross, train_per_hl=per_hl)


def station_halves(f, opt, leash_status):
    """สถานี 5 — เอาไม้บรรทัดของครึ่งแรก (α, β, μ, σ) ไปวัดครึ่งหลัง แล้วถามซ้ำว่าครึ่งหลังยังมีสายจูงไหม"""
    eps2 = f["y2"] - f["alpha"] - f["beta"] * f["x2"]
    shift = float(np.mean(eps2)) / f["sd1"]              # μ ของครึ่งแรก = 0 (ส่วนเหลือของ OLS)
    ratio = float(np.std(eps2, ddof=1)) / f["sd1"]
    own = leash_test(f["y2"], f["x2"], opt.sims)
    ruler_ok = abs(shift) <= SHIFT_MAX_SIGMA and 1.0 / SD_RATIO_MAX <= ratio <= SD_RATIO_MAX
    leash_ok = math.isfinite(own["p"]) and own["p"] < P_PASS
    rows = [f"วัดครึ่งหลังด้วยไม้บรรทัดของครึ่งแรก: ค่าเฉลี่ยของ ε เลื่อน {shift:+.2f}σ · sd ของ ε = {ratio:.2f} เท่า",
            f"ครึ่งหลังทดสอบเดี่ยว ๆ ด้วย β ของตัวเอง: EG statistic = {own['adf']:.2f} · p-value "
            f"{rel_p(own['p'])}"]
    moved = f"เลื่อน {shift:+.1f}σ · กว้าง {ratio:.1f} เท่า"
    if ruler_ok and leash_ok:
        status = OK
        read = f"ไม้บรรทัดของครึ่งแรกยังวัดครึ่งหลังได้ ({moved}) และครึ่งหลังก็ยังมีสายจูง"
    elif ruler_ok:
        status = WARN
        read = (f"ไม้บรรทัดเดิมยังพอใช้ได้ ({moved}) แต่ครึ่งหลังทดสอบเดี่ยว ๆ ไม่ผ่าน "
                "→ แรงดึงอาจอ่อนลง จับตาดู")
    elif leash_ok and leash_status == FAIL:
        status = WARN
        read = (f"ครึ่งแรกไม่มีหลักฐานของสายจูง แต่ครึ่งหลังทดสอบเดี่ยว ๆ กลับผ่าน ({moved}) → อาจเพิ่งเกิด "
                "หรืออาจเป็นโชค: ครึ่งหลังใช้ยืนยันตัวเองไม่ได้ ต้องรอข้อมูลใหม่มาสอบ")
    elif leash_ok:
        status = WARN
        read = (f"ไม้บรรทัดของครึ่งแรกใช้กับครึ่งหลังไม่ได้ ({moved}) แต่ครึ่งหลังยังมีสายจูงเมื่อใช้ β ของตัวเอง "
                "→ สายจูงยืด ไม่ได้ขาด: ต้องประมาณใหม่เป็นรอบ ๆ")
    elif leash_status == FAIL:
        status = FAIL
        read = (f"ไม้บรรทัดของครึ่งแรกใช้กับครึ่งหลังไม่ได้ ({moved}) และครึ่งหลังทดสอบเดี่ยว ๆ ก็ไม่ผ่านเช่นกัน "
                "→ ไม่มีสายจูงทั้งสองครึ่ง")
    else:
        status = FAIL
        read = (f"ไม้บรรทัดของครึ่งแรกใช้ไม่ได้ ({moved}) และครึ่งหลังทดสอบเดี่ยว ๆ ก็ไม่ผ่าน "
                "→ สายจูงที่เห็นในครึ่งแรกหายไปแล้ว")
    return station(5, "สองครึ่ง", "ครึ่งแรกเทียบครึ่งหลัง", status, rows, read,
                   shift=shift, sd_ratio=ratio, adf2=own["adf"], p2=own["p"])


def station_cost(f, opt, leash_status):
    """สถานี 6 — หนึ่งรอบ (เข้าที่ entry ออกที่ exit) คาดว่าได้เท่าไรต่อเงินรวมสองขา เทียบกับต้นทุน 2c"""
    c = opt.cost_bps / 1e4
    earn = (opt.entry - opt.exit) * f["sd1"] / (1.0 + abs(f["beta"]))
    cost = 2.0 * c
    ratio = earn / cost if cost > 0 else float("inf")
    ratio_txt = f"{ratio:.1f} เท่า" if math.isfinite(ratio) else "ไม่จำกัด (ไม่ได้ใส่ต้นทุน)"
    rows = [f"ได้ต่อรอบ ≈ (entry - exit) x σ / (1 + |β|) = ({opt.entry:g} - {opt.exit:g}) x {f['sd1']:.2%} / "
            f"(1 + {abs(f['beta']):.3f}) = {earn * 1e4:.0f} bps",
            f"จ่ายต้นทุนไปกลับ 2c = {cost * 1e4:g} bps · อัตราส่วน = {ratio_txt}"]
    if ratio < COST_RATIO_MIN:
        status = FAIL
        read = f"ต้นทุนกินหมด: รอบหนึ่งคาดว่าได้ {earn * 1e4:.0f} bps แต่จ่าย {cost * 1e4:g} bps"
    elif leash_status == FAIL:
        status = WARN
        read = "สูตรนี้ถือว่า ε กลับมาที่ค่าเฉลี่ยเสมอ — สถานี 3 ไม่ผ่าน ตัวเลขนี้จึงยังเชื่อไม่ได้"
    elif ratio < COST_RATIO_OK:
        status = WARN
        read = (f"กำไรต่อรอบบาง: ได้ราว {ratio:.1f} เท่าของต้นทุน (อยากได้ ≥ {COST_RATIO_OK:g} เท่า) "
                "→ slippage นิดเดียวก็หมด")
    else:
        status = OK
        read = (f"รอบหนึ่งคาดว่าได้ราว {earn * 1e4:.0f} bps ของเงินรวมสองขา จ่ายต้นทุน {cost * 1e4:g} bps "
                "→ ต้นทุนไม่ใช่ปัญหาของคู่นี้")
    return station(6, "ต้นทุน", "ต้นทุนเทียบกำไรต่อรอบ", status, rows, read,
                   earn=earn, cost=cost, ratio=ratio)


def exam_start(n, train):
    """แท่งแรกที่สถานี 7 เทรด (นับจาก 0): ต้นครึ่งหลัง (ชุดเดียวกับที่สถานี 5 ใช้ = h แท่งสุดท้าย)
    หรือหลังหน้าต่าง train แรก ถ้าครึ่งแรกสั้นกว่า train"""
    return max(n - n // 2, train)


def walk(y, x, opt, lag):
    """walk-forward ตามกฎของ check (ประมาณจาก train แท่งล่าสุด ทุก REFIT_BARS แท่ง) → ผลของ C.walk_forward_pair"""
    return C.walk_forward_pair(y, x, train=opt.train, refit=REFIT_BARS, entry=opt.entry, exit=opt.exit,
                               cost_per_leg=opt.cost_bps / 1e4, lag=lag)


def backtest_row(label, s):
    """หนึ่งแถวของตาราง backtest (ASCII ล้วน ให้คอลัมน์ตรงกันใน <pre>)"""
    return (f"{label:<11s} {s['sharpe']:6.2f}   {s['ann_return']:8.2%}   {int(s['n_trades']):6d}   "
            f"{s['hit_rate']:7.0%}   {s['avg_trade'] * 1e4:+6.0f} bps   {s['max_dd']:11.1%}")


def station_backtest(y, x, opt, n_jumps=0):
    """สถานี 7 — walk-forward บน "ครึ่งหลัง" (ช่วงสอบ) เท่านั้น: ประมาณค่าจาก train แท่งล่าสุด เทรดแท่งถัดไป
    หักต้นทุน · lag 1 และ lag 2 · หน้าต่าง train แรกคือปลายครึ่งแรก (อดีต) จึงไม่มีอะไรเห็นอนาคต
    ช่วงศึกษา (ที่สถานี 3 ใช้ตัดสินว่ามีสายจูง) ถูก backtest แยกไว้หนึ่งแถวให้เทียบ — ไม่ใช้ตัดสิน เพราะคู่ที่
    ผ่านสถานี 3 มาได้ ย่อมดูดีในช่วงนั้นเสมอ ต่อให้ไม่มีสายจูงจริง
    n_jumps = จำนวนราคากระโดดที่สถานี 1 เจอ (มีแล้ว ผล backtest จะเชื่อไม่ได้ จึงไม่ให้ ✅)"""
    n, h = len(y), len(y) // 2
    start = exam_start(n, opt.train)
    runs = {lag: walk(y[start - opt.train:], x[start - opt.train:], opt, lag) for lag in (1, 2)}
    s1, s2 = runs[1]["stats"], runs[2]["stats"]
    study = walk(y[:h], x[:h], opt, 2)["stats"] if h - opt.train >= REFIT_BARS else None
    n_test = n - start
    years = n_test / C.DAYS_PER_YEAR
    margin = SHARPE_Z / math.sqrt(years)
    n_tr = int(s2["n_trades"])
    hit_noise = 100.0 * 1.645 * 0.5 / math.sqrt(n_tr) if n_tr > 0 else float("nan")
    rows = ["            Sharpe   return/yr   trades   hit rate   avg trade   max drawdown",
            backtest_row("exam lag 1", s1), backtest_row("exam lag 2", s2)]
    if study is not None:
        rows += [backtest_row("study lag 2", study),
                 f"แถว study = แท่ง {opt.train + 1:,}-{h:,} ซึ่งสถานี 3 ใช้ตัดสินแล้ว จึงดูดีเกินจริงได้ — "
                 "พิมพ์ไว้เทียบเท่านั้น ไม่ใช้ตัดสิน"]
    rows.append(f"ช่วงสอบ (exam) = แท่ง {start + 1:,}-{n:,} ({years:.2f} ปี) · ประมาณใหม่ทุก "
                f"{REFIT_BARS} แท่ง · อยู่ในตลาด {s2['time_in_market']:.0%} ของเวลา")
    rows.append(f"z วัดด้วย σ ที่ประมาณจากหน้าต่าง train: sd ของ z นอกตัวอย่าง = {s1['z_sd']:.2f} (ไม่ใช่ 1)")
    rows.append(f"ความไม่แน่นอน: Sharpe จาก {years:.1f} ปี คลาดได้ราว ±{margin:.2f} · "
                + (f"อัตราชนะจาก {n_tr} ไม้ คลาดได้ถึง ±{hit_noise:.0f} จุด" if n_tr else "ไม่มีไม้ให้นับอัตราชนะ"))
    if s2["open_at_end"] or s1["open_at_end"]:
        rows.append("หมายเหตุ: ไม้สุดท้ายยังเปิดค้างตอนข้อมูลจบ (ตีมูลค่าที่ราคาปิดสุดท้าย ยังไม่ได้จ่ายค่าออก)")
    sh1, sh2 = float(s1["sharpe"]), float(s2["sharpe"])
    if n_tr == 0:
        status = WARN
        read = ("กฎนี้ไม่เปิดสถานะเลยในช่วงสอบ (|z| ไม่เคยถึง entry) → ยังตัดสินอะไรไม่ได้ "
                "(ถ้าจะลด --entry ให้นับเป็นการลองครั้งใหม่ และจดลงสมุด)")
    elif not (sh2 > 0 and sh1 > 0):
        status = FAIL
        read = (f"ในช่วงสอบ หลังหักต้นทุน Sharpe = {sh1:.2f} (lag 1) / {sh2:.2f} (lag 2) "
                "→ กฎนี้กับคู่นี้ไม่รอดนอกตัวอย่าง")
    else:
        notes = []
        if sh2 - margin <= 0:
            notes.append(f"Sharpe lag 2 = {sh2:.2f} เป็นบวก แต่หักความไม่แน่นอน ±{margin:.2f} แล้วคร่อมศูนย์ "
                         "→ ยังแยกจากโชคไม่ได้")
        if n_tr < MIN_TRADES:
            notes.append(f"มีแค่ {n_tr} ไม้ (น้อยกว่า {MIN_TRADES}) → ต่อให้ชนะทุกไม้ก็ยังแยกจากการโยนเหรียญไม่ได้")
        if n_jumps:
            notes.append(f"ข้อมูลมีราคากระโดด {n_jumps} จุด (สถานี 1) → ถ้าเป็น split หรือข้อมูลผิด "
                         "กำไรขาดทุนรอบจุดนั้นไม่ใช่ของจริง ตรวจก่อนเชื่อตารางนี้")
        status = WARN if notes else OK
        read = " · ".join(notes) if notes else (
            f"ในช่วงสอบ Sharpe lag 2 = {sh2:.2f} หักความไม่แน่นอน ±{margin:.2f} แล้วยังเกินศูนย์ "
            f"และช้าไปหนึ่งแท่งก็ยังรอด — แต่ทั้งหมดนี้มาจาก {n_tr} ไม้เท่านั้น")
    nan = float("nan")
    st = station(7, "เดินหน้า", "backtest แบบเดินหน้า (walk-forward) บนช่วงสอบ หลังหักต้นทุน", status, rows,
                   read, sharpe1=sh1, sharpe2=sh2, trades=n_tr, hit2=float(s2["hit_rate"]),
                   max_dd2=float(s2["max_dd"]), ann_return2=float(s2["ann_return"]),
                   avg_trade2=float(s2["avg_trade"]), z_sd=float(s1["z_sd"]), years=years, margin=margin,
                   n_test=n_test, exam_first_bar=start + 1, hit_noise=hit_noise, max_dd1=float(s1["max_dd"]),
                   hit1=float(s1["hit_rate"]), time_in_market2=float(s2["time_in_market"]),
                   open_at_end=bool(s2["open_at_end"]),
                   sharpe_study=float(study["sharpe"]) if study else nan,
                   trades_study=int(study["n_trades"]) if study else 0)
    st["exam_pnl"] = runs[2]["pnl"][opt.train:]      # กำไรขาดทุนรายแท่งของช่วงสอบ (lag 2) ไว้ให้ --pnl-out
    return st


def run_stations(y, x, opt, rep=None, dates=None):
    """พา y, x (log price) ผ่านเจ็ดสถานี → รายการผลของแต่ละสถานี
    สถานี 1 ไม่ผ่าน = ข้อมูลยังใช้ไม่ได้ จึงหยุดตรงนั้น (คืนสถานีเดียว)"""
    first = station_data(y, x, opt, rep, dates)
    if first["status"] == FAIL:
        return [first]
    f = fit_first_half(y, x)
    leash = station_leash(f, opt)
    return [first, station_beta(f), leash, station_rhythm(f, opt, leash["status"]),
            station_halves(f, opt, leash["status"]),
            station_cost(f, opt, leash["status"]), station_backtest(y, x, opt, first["m"]["jumps"])]


# ───────────────────────── คำตัดสิน และ "ลองอะไรต่อ" ─────────────────────────

HINTS = {
    1: "ซ่อมข้อมูลก่อนเชื่อผลของสถานีอื่น: ใช้ราคาที่ปรับ split/ปันผลแล้ว ให้วันที่ของสองขาตรงกัน "
       "ตัดช่วงที่หยุดซื้อขาย แล้วรัน check ใหม่",
    2: "β ไม่นิ่งหรือหลวม: อย่าเชื่อ backtest ที่ตรึง β ตัวเดียวทั้งช่วง ให้เชื่อสถานี 7 ที่ประมาณใหม่เป็นรอบ ๆ "
       "และดูสถานี 5 ว่าสายจูงยืดหรือขาด",
    3: "ไม่มีหลักฐานของสายจูง: อย่าปรับตัวเลขจนผ่าน — ถามก่อนว่าอะไรผูกสองตัวนี้ไว้ (ตอนที่ 7) "
       "ถ้าตอบไม่ได้ให้เปลี่ยนคู่ และจดว่าลองไปแล้วกี่คู่ (คำสั่ง scan นับให้)",
    4: "จังหวะไม่เข้ากับกฎ: เพิ่ม --train ให้ยาว ≥ 8 เท่าของ half-life หรือเปลี่ยนความถี่ของแท่ง "
       "(half-life สั้นกว่า 1 แท่งต้องใช้แท่งที่ถี่กว่า และระวัง bid-ask)",
    5: {WARN: "ไม้บรรทัดเลื่อน: อย่าใช้ α, β, σ ชุดเดียวตลอดไป ให้ประมาณใหม่เป็นรอบ ๆ แบบสถานี 7 "
              "และเขียนเงื่อนไขเลิกคู่นี้ไว้ล่วงหน้า",
        FAIL: "สายจูงหาย: หยุดคู่นี้ แล้วหาว่าเหตุการณ์อะไรทำให้ขาด (ตอนที่ 5 และ 7) — อย่าประมาณ β ใหม่"
              "เพื่อให้กลับมาดูดี"},
    6: "กำไรต่อรอบบาง: เข้าให้ไกลขึ้น (--entry) หาทางลดต้นทุน หรือหาคู่ที่ σ ของ ε กว้างกว่านี้",
    7: {WARN: "หลักฐานจาก backtest ยังบาง: อย่าลด --entry หรือแก้กฎเพื่อเพิ่มไม้หรือเพิ่ม Sharpe — "
              "เก็บข้อมูลเพิ่ม หรือเทรดกระดาษต่อ แล้วสอบซ้ำกับช่วงที่ยังไม่เคยเห็น",
        FAIL: "backtest ไม่รอด: กลับไปดูว่าสถานีไหนข้างบนเตือนไว้ (ตอนที่ 5) — อย่าแก้กฎจนเส้นกำไรสวย "
              "เพราะนั่นคือการสอบซ้ำด้วยข้อสอบชุดเดิม"},
}
HINTS_PASS = ["จดกฎลงสมุดวิจัยก่อนทำอะไรต่อ: คู่ · β · entry/exit · train · ต้นทุน · วันที่รัน",
              "ลองซ้ำด้วย --cost-bps สองเท่า ถ้ายังรอดจึงค่อยไปต่อ",
              "เทรดกระดาษ 30 วัน แล้วเทียบกับที่ backtest บอก — ยังไม่ต้องใช้เงินจริง"]
NO_LEASH_NOTE = "สถานีอื่นที่ไม่ผ่านเป็นผลตามมาจากการไม่มีสายจูง — แก้ที่ต้นเหตุ (สถานี 3) ก่อน"


def hint_for(s):
    """คำแนะนำ "ลองอะไรต่อ" ของสถานีที่ไม่ได้ ✅"""
    h = HINTS[s["no"]]
    return f"สถานี {s['no']}: " + (h[s["status"]] if isinstance(h, dict) else h)


def verdict(stations):
    """คำตัดสินรวม → (รหัส pass/warn/fail, ข้อความหนึ่งบรรทัด, รายการ "ลองอะไรต่อ")"""
    bad = [s for s in stations if s["status"] == FAIL]
    warn = [s for s in stations if s["status"] == WARN]
    if bad:
        text = f"{FAIL} ไม่ผ่าน — ติดที่สถานี {bad[0]['no']} ({bad[0]['short']})"
        if len(bad) > 1:
            text += " และสถานี " + ", ".join(str(s["no"]) for s in bad[1:])
        code = "fail"
    elif warn:
        text = (f"{WARN} ผ่านแบบมีข้อสังเกต — อ่านสถานี " + ", ".join(str(s["no"]) for s in warn)
                + " ให้เข้าใจก่อนไปต่อ")
        code = "warn"
    else:
        text = f"{OK} ผ่านครบ 7 สถานี — ควรค่าแก่การศึกษาต่อ (ยังไม่ใช่คำสัญญาว่าจะกำไร)"
        code = "pass"
    if stations and stations[0]["m"].get("dates_unparsed"):
        text += " · ตรวจลำดับวันที่ก่อนเชื่อผล"
    return code, text, next_steps(bad, warn)


def next_steps(bad, warn):
    """รายการ "ลองอะไรต่อ": ข้อมูลมาก่อนเสมอ · ไม่มีสายจูง = ต้นเหตุ ไม่ต้องไล่แก้ทีละสถานี"""
    hints = [hint_for(s) for s in bad + warn if s["no"] == 1]
    bad = [s for s in bad if s["no"] != 1]
    if any(s["no"] == 3 for s in bad):
        hints += [hint_for(s) for s in bad if s["no"] == 3] + ([NO_LEASH_NOTE] if len(bad) > 1 else [])
    else:
        hints += [hint_for(s) for s in (bad or warn) if s["no"] != 1]
    return hints or HINTS_PASS


def render_check(stations, head):
    """บรรทัดผลลัพธ์ของ check ทั้งหมด (ข้อความธรรมดา วางใน <pre> ได้) — ส่งต่อให้ emit()"""
    out = list(head) + [RULE]
    for s in stations:
        out.append(f"[{s['no']}] {s['status']} {s['title']}")
        out += ["      " + r for r in s["rows"]]
        out.append(("      อ่านว่า: " + s["read"], 15))
    if len(stations) < 7:
        out.append("[2]-[7] ข้าม — ต้องแก้ข้อมูลให้ผ่านสถานี 1 ก่อน")
    _, text, hints = verdict(stations)
    return out + [RULE, "คำตัดสิน: " + text, "ลองอะไรต่อ:"] + ["  - " + h for h in hints]


def date_span(dates, n):
    """ข้อความบอกช่วงเวลาของข้อมูล"""
    return f"{n:,} แท่ง ({dates[0]} ถึง {dates[-1]})" if dates else f"{n:,} แท่ง (ไฟล์ไม่มีคอลัมน์วันที่)"


def need_sims(sims):
    """จำนวนโลกจำลองต้องอยู่ในช่วงที่ใช้ได้จริง (น้อยไป = เส้นตัดแกว่ง · มากไป = รอเป็นชั่วโมง)"""
    if not MIN_SIMS <= sims <= MAX_SIMS:
        raise LabError(f"--sims ต้องอยู่ระหว่าง {MIN_SIMS:,} ถึง {MAX_SIMS:,} โลก (ค่าตั้งต้น {DEFAULT_SIMS:,})")


def need_half(n):
    """จำนวนแท่งของครึ่งแรก · ข้อมูลสั้นเกินไป → หยุดพร้อมคำอธิบาย"""
    if n // 2 < MIN_HALF_BARS:
        raise LabError(f"มีแค่ {n:,} แท่ง — ต้องมีอย่างน้อย {2 * MIN_HALF_BARS:,} แท่ง (ครึ่งละ {MIN_HALF_BARS})")
    return n // 2


# ───────────────────────── คำสั่ง ─────────────────────────

DEMO_KINDS = ("good", "drift", "break", "fake")


def demo_dates(n, start=datetime.date(2020, 1, 1)):
    """วันทำการสมมุติ n วัน (จันทร์–ศุกร์ ไม่มีวันหยุด) เริ่มที่ start"""
    day, dates = start, []
    while len(dates) < n:
        if day.weekday() < 5:
            dates.append(day.isoformat())
        day += datetime.timedelta(days=1)
    return dates


def cmd_make_demo(args):
    """เขียนคู่ตัวอย่างจำลองสี่คู่ของชุดนี้ลง CSV (ราคา = exp(log price) ทศนิยม 4 ตำแหน่ง)"""
    pairs = {k: C.demo_pair(k) for k in DEMO_KINDS}
    n = len(pairs["good"]["y"])
    dates = demo_dates(n)
    try:
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["date"] + [f"{leg}_{k}" for k in DEMO_KINDS for leg in ("Y", "X")])
            for t in range(n):
                w.writerow([dates[t]] + [f"{math.exp(pairs[k][leg][t]):.4f}"
                                         for k in DEMO_KINDS for leg in ("y", "x")])
    except OSError as e:
        raise LabError(f'เขียนไฟล์ "{args.out}" ไม่ได้: {e}') from None
    name = os.path.basename(args.out)
    emit([f"เขียน {name} แล้ว: {n:,} แถว (วันทำการสมมุติ {dates[0]} ถึง {dates[-1]}) x 8 คอลัมน์ราคา",
          "ข้อมูลจำลองทั้งหมด — สี่คู่ที่ 'รู้เฉลย' และถูกเลือกมาให้เห็นอาการชัด:",
          "  Y_good  / X_good    มีสายจูงจริง (ε กลับสู่ค่าเฉลี่ย half-life 12 แท่ง · σ 3%)",
          "  Y_drift / X_drift   สายจูงยืด (β ค่อย ๆ เลื่อนจาก 1.4 ไป 2.2)",
          "  Y_break / X_break   สายจูงขาดที่ 60% ของข้อมูล",
          "  Y_fake  / X_fake    ไม่มีสายจูง (แค่ขึ้นลงตามตลาดเดียวกัน)",
          f"ลองต่อ:  python3 tools/statarb_lab.py check {name} --y Y_good --x X_good"])
    return 0


def check_options(opt):
    """ตัวเลือกที่ไม่มีความหมายให้หยุดพร้อมคำอธิบาย (ก่อนไปถึงข้อความจากแกนคำนวณ)"""
    if not all(math.isfinite(v) for v in (opt.cost_bps, opt.entry, opt.exit)):
        raise LabError("--cost-bps, --entry และ --exit ต้องเป็นตัวเลขจริง (ไม่ใช่ nan หรือ inf)")
    if opt.train < 30:
        raise LabError("--train ต้องไม่น้อยกว่า 30 แท่ง (หน้าต่างสั้นกว่านี้ประมาณ β กับ σ ไม่ได้เรื่อง)")
    if not 0 <= opt.cost_bps < 1e4:
        raise LabError("--cost-bps ต้องไม่ติดลบ และเป็นหน่วย bps (5 = 0.05% ต่อขาต่อเที่ยว)")
    if opt.entry <= 0 or opt.exit >= opt.entry:
        raise LabError("--entry ต้องเป็นบวก และ --exit ต้องน้อยกว่า --entry (เข้าไกล ออกใกล้ค่าเฉลี่ย)")
    need_sims(opt.sims)


def cmd_check(args):
    """เจ็ดสถานีของคู่ Y, X"""
    opt = options(args.cost_bps, args.train, args.entry, args.exit, args.sims)
    check_options(opt)
    names, mat, dates, rep = load_columns(args.file, [args.y, args.x], args.prices)
    y, x = mat[:, 0], mat[:, 1]
    n, h = len(y), len(y) // 2
    head = [f"statarb_lab check · {rep['file']} · Y = {names[0]} · X = {names[1]}",
            f"ข้อมูล {date_span(dates, n)} · " + ("ราคาดิบ แปลงเป็น log ให้แล้ว" if args.prices == "raw"
                                                 else "ค่าในไฟล์เป็น log price"),
            f"ครึ่งแรก (แท่ง 1-{h:,}) = ช่วงศึกษา · ครึ่งหลัง (แท่ง {n - h + 1:,}-{n:,}) = ช่วงสอบ",
            f"กฎ: เข้าเมื่อ |z| >= {opt.entry:g} ออกเมื่อ z กลับถึง {opt.exit:g} · ต้นทุน {opt.cost_bps:g} bps "
            f"ต่อขาต่อเที่ยว · train {opt.train:,} แท่ง"]
    stations = run_stations(y, x, opt, rep, dates)
    emit(render_check(stations, head))
    if args.pnl_out:
        write_pnl(args.pnl_out, stations, names, dates, n)
    return 0 if verdict(stations)[0] != "fail" else 1


def write_pnl(path, stations, names, dates, n):
    """--pnl-out: กำไรขาดทุนรายแท่งของช่วงสอบ (สถานี 7 · lag 2 · หักต้นทุนแล้ว) เป็นสัดส่วนของทุน
    คอลัมน์ date (ค.ศ. YYYY-MM-DD) หรือ bar (ลำดับแท่ง ถ้าไม่มี/อ่านวันที่ไม่ออก) + หนึ่งคอลัมน์ชื่อ "Y-X"
    = รูปแบบที่ tools/sas_snippets/p6_breadth.py อ่าน (ใส่หลายไฟล์ได้ มันจับคู่กันตามวันที่ให้เอง)"""
    if len(stations) < 7:
        emit([f"{WARN} ไม่ได้เขียน {os.path.basename(path)} — สถานี 1 ไม่ผ่าน จึงไม่มี backtest ช่วงสอบ"])
        return
    pnl = stations[6]["exam_pnl"]
    stamps = parse_dates(dates) if dates else None
    keys = ([d.strftime("%Y-%m-%d") for d in stamps[n - len(pnl):]] if stamps
            else [str(t + 1) for t in range(n - len(pnl), n)])
    try:
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["date" if stamps else "bar", f"{names[0]}-{names[1]}"])
            w.writerows([k, f"{v + 0.0:.10g}"] for k, v in zip(keys, pnl))
    except OSError as e:
        raise LabError(f'เขียนไฟล์ "{path}" ไม่ได้: {e}') from None
    emit([f"เขียน {os.path.basename(path)} แล้ว: กำไรขาดทุนรายแท่งของช่วงสอบ {len(pnl):,} แถว "
          "(lag 2 · หักต้นทุนแล้ว · สัดส่วนของทุน) → รวมหลายคู่ด้วย  python3 tools/sas_snippets/p6_breadth.py "
          "pnl_a.csv pnl_b.csv ..."])


def scan_pairs(names, half, n_sim):
    """ทดสอบสายจูงของทุกคู่คอลัมน์ (y = คอลัมน์ที่มาก่อน)
    → (รายการ (p, EG, ชื่อคู่, β, half-life) เรียงจาก p น้อย, จำนวนคู่ที่ทดสอบไม่ได้)"""
    found, skipped = [], 0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            try:
                r = leash_test(half[:, i], half[:, j], n_sim)
            except ValueError:
                r = {"adf": float("nan")}                    # ทดสอบไม่ได้ (เช่น ราคาค้างทั้งช่วง)
            if math.isfinite(r["adf"]):
                hl = float(C.fit_ar1(r["resid"])["half_life"])
                found.append((r["p"], r["adf"], f"{names[i]} ~ {names[j]}", float(r["beta"][0]), hl))
            else:
                skipped += 1                                 # รวมคู่ที่ Y เขียนได้จาก X เป๊ะ (คอลัมน์ซ้ำกัน)
    return sorted(found), skipped


def cmd_scan(args):
    """ทดสอบสายจูงของทุกคู่คอลัมน์ ด้วยครึ่งแรกของข้อมูล (เก็บครึ่งหลังไว้สอบด้วย check)"""
    need_sims(args.sims)
    names, mat, dates, rep = load_columns(args.file, None, args.prices)
    n = len(mat)
    h = need_half(n)
    found, skipped = scan_pairs(names, mat[:h], args.sims)
    if not found:
        raise LabError("ไม่มีคู่ไหนทดสอบได้เลย (ราคาค้างทั้งช่วง หรือคอลัมน์ซ้ำกัน) — ตรวจข้อมูลด้วยคำสั่ง check ทีละคู่")
    n_pairs, top = len(found), max(1, args.top)
    strict = P_PASS / n_pairs
    n5 = sum(p < P_PASS for p, *_ in found)
    n_strict = sum(p < strict for p, *_ in found)
    cv5 = C.crit_values(null_eg(h, 2, args.sims))[0.05]
    width = max(12, max(len(nm) for _, _, nm, _, _ in found))
    dropped = rep["missing"] + rep["nonpos"] + rep["dup_dates"]
    out = [f"statarb_lab scan · {rep['file']} · {len(names)} คอลัมน์ · {date_span(dates, n)}",
           f"ใช้เฉพาะครึ่งแรก {h:,} แท่ง (ช่วงศึกษา) — ครึ่งหลังเก็บไว้ให้ check สอบ · y = คอลัมน์ที่มาก่อนในไฟล์"]
    if rep.get("scale_note"):
        out.append(f"{WARN} {rep['scale_note']}")
    if dropped or rep["skipped_cols"] or skipped:
        out.append(f"ทิ้ง {dropped:,} แถวที่มีค่าว่าง / ราคา ≤ 0 / วันที่ซ้ำ"
                   + (f" · ข้ามคอลัมน์ที่ไม่ใช่ตัวเลข: {', '.join(rep['skipped_cols'])}" if rep["skipped_cols"] else "")
                   + (f" · ข้าม {skipped} คู่ที่ทดสอบไม่ได้ (ราคาค้าง หรือคอลัมน์ซ้ำกัน)" if skipped else ""))
    out += [f"เส้นตัด 5% สำหรับ {h:,} แท่ง = {cv5:.2f} (จำลอง {args.sims:,} โลกที่ไม่มีสายจูง)", RULE,
            f"  #  {'pair (y ~ x)':<{width}}   EG stat   p-value     beta   half-life    5%   5%/{n_pairs}"]
    for rank, (p, adf, nm, beta, hl) in enumerate(found[:top], 1):
        hl_txt = f"{hl:9.1f}" if p < P_WARN and math.isfinite(hl) else "        -"
        out.append(f"{rank:3d}  {nm:<{width}}   {adf:7.2f}   {fmt_p(p):>7s}   {beta:6.2f}   {hl_txt}   "
                   f"{'yes' if p < P_PASS else ' no'}   {'yes' if p < strict else ' no'}")
    if n_pairs > top:
        out.append(f"     ... อีก {n_pairs - top} คู่ที่ p-value สูงกว่านี้ (ดูทั้งหมดด้วย --top {n_pairs})")
    out += [RULE,
            f"ทดสอบไป {n_pairs} คู่ · ถ้าไม่มีคู่ไหนมีสายจูงเลย ก็ยังคาดว่าจะ 'ผ่าน' เกณฑ์ 5% ด้วยโชคราว "
            f"{P_PASS * n_pairs:.1f} คู่",
            f"ผ่านเกณฑ์ 5%: {n5} คู่ · ผ่านเกณฑ์เข้มที่หารด้วยจำนวนคู่ที่ลอง (p < {P_PASS:g}/{n_pairs} = "
            f"{strict:.4f}): {n_strict} คู่",
            ("อ่านว่า: คู่ที่ผ่านแค่เกณฑ์ 5% ธรรมดายังแยกไม่ออกจากโชคของการลองหลายคู่ · half-life แสดงเฉพาะคู่ที่ "
             f"p < {P_WARN:.2f} (คู่ที่สอบไม่ผ่าน เลขนี้ไม่มีความหมาย) · เอาคู่ที่น่าสนใจไปเข้า check "
             "ซึ่งจะสอบกับครึ่งหลังที่ scan ยังไม่เคยเห็น", 9)]
    emit(out)
    return 0


def basket_fit(mat, n_sim):
    """ตัวเลขของตะกร้า: คอลัมน์แรกของ mat = Y ที่เหลือ = ขา · น้ำหนักและการทดสอบใช้ครึ่งแรก
    แล้วเอาน้ำหนักชุดนั้นไปวัดครึ่งหลัง (ค่าเฉลี่ยเลื่อนกี่ σ · sd กว้างขึ้นกี่เท่า)"""
    h = need_half(len(mat))
    r = leash_test(mat[:h, 0], mat[:h, 1:], n_sim)
    sd1 = float(np.std(r["resid"], ddof=1))
    eps2 = mat[-h:, 0] - r["alpha"] - mat[-h:, 1:] @ r["beta"]
    return {"h": h, "eg": r, "pair_cv": C.crit_values(null_eg(h, 2, n_sim)), "sd1": sd1,
            "shift": float(np.mean(eps2)) / sd1, "sd_ratio": float(np.std(eps2, ddof=1)) / sd1,
            "half_life": float(C.fit_ar1(r["resid"])["half_life"])}


def cmd_basket(args):
    """Y เทียบกับตะกร้าหลายขา: น้ำหนักจากครึ่งแรก + เส้นตัดของจำนวนสินทรัพย์นั้น + สอบกับครึ่งหลัง"""
    need_sims(args.sims)
    legs = [s.strip() for s in args.basket.split(",") if s.strip()]
    if not legs:
        raise LabError("--basket ต้องมีชื่อคอลัมน์อย่างน้อยหนึ่งตัว คั่นด้วยจุลภาค เช่น --basket AAA,BBB,CCC")
    if len(legs) > MAX_LEGS:
        raise LabError(f"--basket มี {len(legs)} ขา — ไม่เกิน {MAX_LEGS} ขา (ขายิ่งมาก น้ำหนักยิ่งพอดีกับอดีต)")
    names, mat, dates, rep = load_columns(args.file, [args.y] + legs, args.prices)
    n, n_assets = len(mat), len(names)
    b = basket_fit(mat, args.sims)
    r, pair_cv, shift, ratio = b["eg"], b["pair_cv"], b["shift"], b["sd_ratio"]
    width = max(8, max(len(nm) for nm in names[1:]))
    out = [f"statarb_lab basket · {rep['file']} · Y = {names[0]} · N = {n_assets} สินทรัพย์",
           f"ตะกร้า = {', '.join(names[1:])}",
           f"ข้อมูล {date_span(dates, n)} · ครึ่งแรก {b['h']:,} แท่ง = ช่วงศึกษา · ครึ่งหลัง = ช่วงสอบ"]
    if rep.get("scale_note"):
        out.append(f"{WARN} {rep['scale_note']}")
    out += [RULE, f"  {'leg':<{width}}   weight (beta)"]
    out += [f"  {nm:<{width}}   {w:8.3f}" for nm, w in zip(names[1:], r["beta"])]
    out += [f"  {'alpha':<{width}}   {r['alpha']:8.3f}       ε = Y - alpha - ผลรวมของ (weight x ขา)",
            f"EG statistic               = {r['adf']:.2f}",
            f"cut-offs for N = {n_assets} assets     {fmt_cv(r)}   <- ใช้ชุดนี้"]
    if n_assets > 2:
        out.append(f"cut-offs for N = 2 assets     1%: {pair_cv[0.01]:.2f}   5%: {pair_cv[0.05]:.2f}   "
                   f"10%: {pair_cv[0.1]:.2f}   (ของคู่ธรรมดา ไว้เทียบ)")
    out += [f"p-value (N = {n_assets})            {rel_p(r['p'])}   (จำลอง {args.sims:,} โลก · {b['h']:,} แท่ง)",
            f"half-life = {b['half_life']:.1f} แท่ง · σ ของ ε = {b['sd1']:.2%}",
            f"ครึ่งหลังวัดด้วยน้ำหนักของครึ่งแรก: ค่าเฉลี่ยของ ε เลื่อน {shift:+.2f}σ · sd ของ ε = {ratio:.2f} เท่า", RULE]
    ruler_ok = abs(shift) <= SHIFT_MAX_SIGMA and 1.0 / SD_RATIO_MAX <= ratio <= SD_RATIO_MAX
    passed = math.isfinite(r["p"]) and r["p"] < P_PASS
    if passed and ruler_ok:
        text = f"{OK} ผ่านเส้นตัดของ {n_assets} สินทรัพย์ และน้ำหนักของครึ่งแรกยังวัดครึ่งหลังได้"
    elif passed:
        text = (f"{WARN} ผ่านเส้นตัดในครึ่งแรก แต่น้ำหนักชุดนี้วัดครึ่งหลังไม่ได้ (เลื่อน {shift:+.1f}σ · "
                f"กว้าง {ratio:.1f} เท่า) → น้ำหนักพอดีกับอดีตเกินไป หรือสายจูงเปลี่ยน")
    elif n_assets > 2 and r["adf"] < pair_cv[0.05]:
        text = (f"{FAIL} ไม่ผ่านเส้นตัดของ {n_assets} สินทรัพย์ — ถ้าเผลอใช้เส้นตัดของคู่ธรรมดา "
                f"({pair_cv[0.05]:.2f}) จะเข้าใจผิดว่าผ่าน")
    else:
        text = f"{FAIL} ไม่ผ่านเส้นตัดของ {n_assets} สินทรัพย์ — ไม่มีหลักฐานว่าตะกร้านี้มีสายจูง"
    out += ["คำตัดสิน: " + text,
            ("อ่านว่า: ยิ่งเพิ่มขา ε ในอดีตยิ่งดูนิ่งขึ้นเอง เพราะมีน้ำหนักให้ปรับมากขึ้น เส้นตัดจึงต้องเข้มขึ้นตามจำนวน"
             "สินทรัพย์ · ขาที่น้ำหนักใกล้ศูนย์คือขาที่ไม่ได้ช่วยอะไร ตัดออกแล้วทดสอบใหม่ได้ "
             "(แต่นับเป็นการลองอีกหนึ่งครั้ง)", 9)]
    emit(out)
    return 0 if passed else 1


class ThaiParser(argparse.ArgumentParser):
    """argparse ที่บอกข้อผิดพลาดของตัวเลือกเป็นภาษาไทย (ข้อความเดิมของ argparse ต่อท้ายไว้ให้ค้นต่อได้)"""

    def error(self, message):
        sub = self.prog.split(" ", 1)[1] + " " if " " in self.prog else ""
        self.print_usage(sys.stdout)
        print(f"{FAIL} ตัวเลือกไม่ถูกต้อง ({message}) — ดูวิธีใช้ด้วย  python3 tools/statarb_lab.py {sub}--help")
        sys.exit(2)


def build_parser():
    ap = ThaiParser(
        prog="statarb_lab.py", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="ห้องทดลองเจ็ดสถานีสำหรับตรวจคู่ของคุณเอง (ชุด แกะสไลด์ Stat Arb ตอนที่ 8)",
        epilog="ตัวอย่าง:\n  python3 tools/statarb_lab.py make-demo demo.csv\n"
               "  python3 tools/statarb_lab.py check demo.csv --y Y_good --x X_good\n"
               "  python3 tools/statarb_lab.py scan demo.csv\n"
               "  python3 tools/statarb_lab.py basket demo.csv --y Y_good --basket X_good,X_drift,X_fake")
    ap.add_argument("--debug", action="store_true", help="แสดง traceback เต็มเมื่อเกิดข้อผิดพลาด (สำหรับคนแก้โค้ด)")
    sub = ap.add_subparsers(dest="cmd", metavar="คำสั่ง")

    def shared(p):
        p.add_argument("--prices", choices=("raw", "log"), default="raw",
                       help="ค่าในไฟล์เป็นราคาดิบ (raw ค่าตั้งต้น) หรือ log price อยู่แล้ว (log)")
        p.add_argument("--sims", type=int, default=DEFAULT_SIMS,
                       help=f"จำนวนโลกจำลองที่ใช้หาเส้นตัด (ค่าตั้งต้น {DEFAULT_SIMS:,})")

    p = sub.add_parser("make-demo", help="เขียนคู่ตัวอย่างจำลองสี่คู่ลง CSV")
    p.add_argument("out", metavar="OUT.csv")
    p.set_defaults(fn=cmd_make_demo)

    p = sub.add_parser("check", help="พาคู่ Y, X ผ่านเจ็ดสถานี")
    p.add_argument("file", metavar="FILE")
    p.add_argument("--y", required=True, metavar="COL", help="คอลัมน์ของ Y (ขาที่ซื้อเมื่อ long สเปรด)")
    p.add_argument("--x", required=True, metavar="COL", help="คอลัมน์ของ X (ขาที่ใช้ถ่วง)")
    p.add_argument("--cost-bps", type=float, default=DEFAULT_COST_BPS,
                   help=f"ต้นทุนเที่ยวเดียวต่อขา หน่วย bps (ค่าตั้งต้น {DEFAULT_COST_BPS:g})")
    p.add_argument("--train", type=int, default=DEFAULT_TRAIN,
                   help=f"หน้าต่างประมาณค่าของ walk-forward หน่วยแท่ง (ค่าตั้งต้น {DEFAULT_TRAIN})")
    p.add_argument("--entry", type=float, default=DEFAULT_ENTRY,
                   help=f"เข้าเมื่อ |z| ถึงค่านี้ (ค่าตั้งต้น {DEFAULT_ENTRY:g})")
    p.add_argument("--exit", type=float, default=DEFAULT_EXIT,
                   help=f"ออกเมื่อ z กลับถึงค่านี้ (ค่าตั้งต้น {DEFAULT_EXIT:g})")
    p.add_argument("--pnl-out", metavar="FILE",
                   help="เขียนกำไรขาดทุนรายวันของช่วงสอบ (สถานี 7 · lag 2 · หักต้นทุน · สัดส่วนของทุน) "
                        "เป็น CSV คอลัมน์ date (หรือ bar) กับ Y-X — ป้อนให้ p6_breadth.py ได้ทันที "
                        "(หลายคู่: ใส่หลายไฟล์ มันจับคู่ตามวันที่)")
    shared(p)
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("scan", help="ทดสอบสายจูงของทุกคู่ในไฟล์ พร้อมนับว่าลองไปกี่คู่")
    p.add_argument("file", metavar="FILE")
    p.add_argument("--top", type=int, default=15, help="จำนวนคู่ที่แสดง (ค่าตั้งต้น 15)")
    shared(p)
    p.set_defaults(fn=cmd_scan)

    p = sub.add_parser("basket", help="Y เทียบกับตะกร้าหลายขา ด้วยเส้นตัดของจำนวนสินทรัพย์นั้น")
    p.add_argument("file", metavar="FILE")
    p.add_argument("--y", required=True, metavar="COL", help="คอลัมน์ของ Y")
    p.add_argument("--basket", required=True, metavar="A,B,C", help="ชื่อคอลัมน์ของขาในตะกร้า คั่นด้วยจุลภาค")
    shared(p)
    p.set_defaults(fn=cmd_basket)
    return ap


def main(argv=None):
    """จุดเข้าของ CLI → รหัสออก (0 = ไม่ติด ❌ · 1 = ติด ❌ · 2 = รันไม่ได้) · ไม่ปล่อย traceback ให้ผู้ใช้"""
    ap = build_parser()
    args = ap.parse_args(argv)
    if not getattr(args, "fn", None):
        ap.print_help()
        return 2
    try:
        return args.fn(args)
    except KeyboardInterrupt:
        print(f"\n{FAIL} หยุดตามที่สั่ง (Ctrl+C)")
        return 130
    except BrokenPipeError:                     # เช่น ส่งผลต่อให้ head แล้ว head ปิดท่อก่อน — ไม่ใช่ความผิดพลาด
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 0
    except LabError as e:
        print(f"{FAIL} {e}")
    except ValueError as e:                     # ข้อความจาก sas_core (ข้อมูลเสีย/ตัวเลือกผิด) เป็นภาษาไทยอยู่แล้ว
        if args.debug:
            raise
        print(f"{FAIL} คำนวณต่อไม่ได้: {e}")
    except Exception as e:                      # noqa: BLE001 — ผู้ใช้ควรเห็นคำอธิบาย ไม่ใช่ traceback
        if args.debug:
            raise
        print(f"{FAIL} เกิดข้อผิดพลาดที่ไม่คาดคิด ({type(e).__name__}: {e}) — รันซ้ำด้วย --debug เพื่อดูรายละเอียด")
    return 2


if __name__ == "__main__":
    sys.exit(main())
