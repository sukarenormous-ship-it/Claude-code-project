#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ห้องทดลองตอนที่ 7 — ตารางเจ็ดแถว = สายจูงเจ็ดแบบ  (สไลด์แผ่นที่ 8)
ข้อมูลทั้งหมดเป็น "ข้อมูลจำลอง" ที่เรารู้เฉลย · ตัวอย่างเงินใน 7b เป็น "ตัวเลขสมมติ" ไม่ใช่ราคาตลาด

รัน:   python3 tools/sas_exp7.py        (พิมพ์สรุปตัวเลขหลักเป็นภาษาไทย · ใช้เวลาราว 30 วินาที)

คำถามของตอนนี้: ตลาดแบบไหน "มีสายจูงจริง" และสายจูงแต่ละชั้นต่างกันตรงไหน
มีสามการทดลอง

7a  บันไดสายจูง (leash ladder) — ε สี่แบบ วัดด้วยกติกาเดียวกันทุกแบบ
    ตัวสร้าง ε (แบบละหนึ่งประโยค — อะไรทำให้มันอยู่ชั้นนั้น)
      contractual  สัญญา     : ε เดินสุ่มได้ระหว่างอายุสัญญา แต่ "สัญญาบังคับ" ให้ ε = 0 พอดีในวันหมดอายุ
                               (ทุก 63 แท่ง แล้วสัญญาใหม่เริ่มที่ระดับสุ่ม) — สะพานบราวน์ต่อกันเป็นลูกโซ่
      mechanical   กลไก      : กลไกของตลาด (funding · การสร้าง/ไถ่ถอนหน่วย) ดึง ε กลับ "ทุกแท่ง" จึงเป็น AR(1)
                               ที่เร็ว half-life 3 แท่ง
      economic     เศรษฐกิจ  : ธุรกิจที่ทดแทนกันได้ดึง ε กลับช้า ๆ (AR(1) half-life 12 แท่ง) แต่นาน ๆ ครั้ง
                               ข่าวเปลี่ยนพื้นฐานจนค่าเฉลี่ยกระโดดถาวร (เฉลี่ยทุก 250 แท่ง ขนาด N(0, (2σ)²))
      statistical  สถิติล้วน : random walk อิสระสองเส้นที่ไม่มีอะไรผูกกันเลย แต่ 500 แท่งแรก "บังเอิญ" ผ่าน
                               Engle-Granger ที่เส้นตัด 5% จากการจำลอง แล้ววัดผลใน 500 แท่งถัดไป
    สามแบบแรกมี σ = 3% · แบบสถิติล้วนตั้งความผันผวนของ random walk ให้ σ̂ ของส่วนเหลือในช่วง train
    มีค่ากลางราว 3% เท่ากัน (ตัวเลขทุกตัวเป็นหน่วย σ̂ อยู่แล้ว สเกลนี้จึงมีไว้ให้กราฟเทียบกันได้เท่านั้น)
    กติกาเดียวกันทุกแบบ (ไม่มีการมองอนาคต)
      1) ไม้บรรทัด: μ̂, σ̂ ของ ε จาก 500 แท่งแรก (train) → z_t = (ε_t − μ̂)/σ̂   (แบบ statistical ใช้ α̂, β̂
         จาก 500 แท่งแรกด้วย) — z จึงเป็นหน่วย "σ ที่ประมาณจากช่วง train" ไม่ใช่ σ จริง
      2) เหตุการณ์ "แตะ": ใน 500 แท่งถัดไป (test) ถ้ายังไม่มีไม้ค้างและ |z_t| ≥ 2 → เปิดเหตุการณ์ที่แท่ง t
      3) "กลับ": แท่งแรกหลังจากนั้น (t+1 เป็นต้นไป) ที่ z กลับมาถึง 0.5 ฝั่งเดียวกับที่แตะ (หรือเลยไป)
         ตามดูได้นานสุด 250 แท่ง · เกินนั้นนับว่า "ไม่กลับ" แล้วพักจนกว่า |z| < 2 จึงเปิดเหตุการณ์ใหม่ได้
         เหตุการณ์เปิดได้เฉพาะในช่วง test แต่ตามดูต่อได้ถึง 250 แท่งหลังจุดเปิด (เลยแท่งที่ 1,000 ได้)
         เฉพาะแบบ contractual: ถ้าถึงแท่งหมดอายุแล้วยังไม่กลับ สัญญาชำระที่ ε = 0 → นับว่ากลับ ณ แท่งนั้น
      4) วัดต่อเหตุการณ์: จำนวนแท่งจนกลับ · หลุดไกลสุดระหว่างรอ (หน่วย σ̂) · กำไรก่อนต้นทุน (หน่วย σ̂)
         กำไร = z ตอนแตะ − z ตอนจบ (เท่ากับได้ราคาปิดของแท่งที่ให้สัญญาณ = lag 1) และรายงานแบบได้ราคา
         ช้าไปหนึ่งแท่งทั้งขาเข้าและขาออก (lag 2) คู่กันเสมอ — ยกเว้นไม้ที่จบในวันหมดอายุ ซึ่งชำระ ณ วันนั้น
    ผลหลัก: % ที่กลับภายใน 30 แท่ง · เวลากลับค่ากลาง (ไม้ที่ไม่กลับนับเป็น "นานกว่า 250") · เปอร์เซ็นไทล์ที่ 95
            ของระยะหลุดไกลสุด · % ที่ไม่กลับใน 250 แท่ง · กำไรเฉลี่ยต่อเหตุการณ์
    ตรวจความยุติธรรม (same_filter): แบบสถิติล้วนถูก "คัด" ด้วย EG แต่สามแบบแรกไม่ได้ถูกคัด — จึงลองให้ทั้งสามแบบ
    ผ่านขั้นตอนเดียวกับแบบสถิติล้วนทุกประการ: สร้าง x เป็น random walk, y = x + ε, ประมาณ α̂, β̂ และทดสอบ EG
    บน 500 แท่งแรก แล้ววัดเฉพาะโลกที่ผ่าน (โลกชุดเดียวกับการทดลองหลัก)

7b  สมการกำไร  P&L = convergence + carry − costs  คิดให้ดูทีละบรรทัด (ตัวเลขสมมติทั้งหมด)
    ผลสุทธิทุกตัวหัก "ต้นทุนเงิน" 4% ต่อปีของเงินที่จมอยู่ในขา spot แล้ว ทั้งสองตัวอย่าง (= ส่วนที่ได้เกินการฝากเงิน)
    carry    cash-and-carry: ราคายุติธรรมของ future เทียบกับราคาที่เสนอ → กำไรที่ล็อกได้หลังหักต้นทุนเงิน
             และค่าซื้อขาย 4 ขา · จุดคุ้มทุน · ผลต่อทุนเมื่อต้องวางหลักประกัน
    funding  ถือ spot + short perpetual: จำลองอัตรา funding ราย 8 ชั่วโมง ที่มี "ช่วงติดลบ"
             → carry ต่อปี · สัดส่วนงวดที่ติดลบ · 30 วันที่แย่ที่สุด · ต้องถือนานเท่าไรจึงคุ้มค่าซื้อขายและต้นทุนเงิน
    identity แยกกำไร 90 วันของสองตัวอย่างออกเป็น convergence / carry / ต้นทุน บนฐานเดียวกัน
             (ค่ากลางของ funding = ค่าคาดหมายของแบบจำลอง คิดด้วยเลขคณิต · ช่วง 5–95% มาจากการจำลอง)

7c  ตารางเจ็ดแถวของสไลด์ 8 แบบที่เครื่องอ่านได้ — เฉพาะ "ข้อเท็จจริงเชิงโครงสร้าง" (ไม่มีตัวเลข):
    Y, X, ชื่อกลยุทธ์, Arbitrage Driver ตามสไลด์, ได้เงินจากอะไร (convergence / carry), ชั้นของสายจูง

ความแม่นของตัวเลข: จำนวนทศนิยมเลือกให้ตัวเลขหลักสุดท้ายไม่เปลี่ยนเมื่อเปลี่ยน seed (ตรวจแล้ว) —
  % ปัดเป็นจำนวนเต็ม (ใกล้ 0/100 ไม่ถึง 1 จุด: หนึ่งตำแหน่ง) · z และกำไรหน่วย σ̂ หนึ่งตำแหน่ง · ระยะหลุดไกลสุด
  2 หลักสำคัญ · ค่ากลางของ bps funding ปัดทีละ 5 และหาง (5%, 95%) ทีละ 10 · จำนวนวันเป็นจำนวนเต็ม
  ตัวเลขที่เป็นเลขคณิตบนค่าสมมติ (7b cash-and-carry, headline, ค่าคาดหมาย) เก็บสองตำแหน่งตามที่คำนวณได้จริง

คีย์ใน figures()  (ทุกค่าปัดแล้ว · หน่วยอยู่ในชื่อคีย์: _pct, _bps, _bars, _sigma, _baht, _days)
  about.*                         คำอธิบายสั้น ๆ ของแต่ละการทดลองและค่าที่ตั้งไว้
  ladder.settings.*               train_bars, test_bars, follow_bars, entry_z, exit_z, window_bars, worlds,
                                  candidates, selected, pass_rate_pct, eg_crit5, eg_null_worlds, boot_resamples
  ladder.assumptions.*            พารามิเตอร์ของตัวสร้างทั้งสี่ (+ statistical_train_sd_pct ที่วัดได้จริง)
  ladder.<type>.*                 type = contractual | mechanical | economic | statistical
      worlds, events, events_per_world, worlds_with_event_pct,
      z_sd_test (sd ของ z ในช่วง test), z_rms_test (รากของค่าเฉลี่ย z² — 1.0 = ไม้บรรทัดยังใช้ได้),
      p30_pct (+ p30_lo_pct, p30_hi_pct = ช่วง 5–95% จากการสุ่มโลกซ้ำ = ความแม่น), back10_pct, back63_pct,
      back125_pct, back250_pct, never250_pct, median_return_bars, worst_median_sigma, worst_p05_sigma,
      worst_p95_sigma, worst_ge4_pct, avg_pnl_sigma (+ avg_pnl_lo_sigma, avg_pnl_hi_sigma), avg_pnl_lag2_sigma
  ladder.contractual.*            เพิ่ม ended_at_expiry_pct, median_bars_to_expiry_at_touch,
                                  near_expiry_events, near_expiry_p30_pct, far_expiry_events, far_expiry_p30_pct
  ladder.economic.*               เพิ่ม events_with_jump_pct, p30_no_jump_pct, p30_with_jump_pct
  ladder.same_filter.<type>.*     contractual | mechanical | economic: eg_pass_pct, worlds, events, p30_pct,
                                  never250_pct, median_return_bars, worst_p95_sigma, avg_pnl_sigma
  ladder.sensitivity.contract.life21 | life63 | life126          ลองเปลี่ยนอายุสัญญา
  ladder.sensitivity.economic.every125 | every250 | every500 | no_jump   ลองเปลี่ยนความถี่ที่ค่าเฉลี่ยกระโดด
      แต่ละตัวมี worlds, events, p30_pct, never250_pct, median_return_bars, worst_p95_sigma, avg_pnl_sigma
  carry_example.assumptions.* · carry_example.*     ตัวอย่าง cash-and-carry (ตัวเลขสมมติ · บาทต่อ spot 100 บาท)
      รวม carry_example.with_margin.* (เมื่อคิดหลักประกันของ future)
  funding_example.assumptions.* · .settings.* · .*  ตัวอย่าง funding (อัตราจำลอง ไม่ใช่ข้อมูลตลาด)
      headline_* / longrun_* / carry_* / negative_* / worst30_* = funding ล้วน ๆ (ยังไม่หักอะไร)
      net_* / hold<d>.net_* / breakeven_days_* = หลังหักค่าซื้อขายและต้นทุนเงิน 4% (= ส่วนที่ได้เกินการฝากเงิน)
      breakeven_costs_only_days_median = หักค่าซื้อขายอย่างเดียว (แบบที่ตลาดคริปโตมักคิด)
      hold<d>.loss_pct = % ของโลกที่ "แพ้การฝากเงิน 4%" · hold<d>.loss_before_financing_pct = ขาดทุนเป็นเงินจริง
  identity.cash_carry.* · identity.funding.*        convergence_baht, carry_baht (หลังหักต้นทุนเงิน), costs_baht,
                                                    net_baht + ส่วนประกอบของ carry (basis_interest / funding, financing)
  rows.row1 … rows.row7            id, label, y, x, strategy, driver (ตามสไลด์), paid_by (convergence | carry),
                                   leash (ชั้นหลัก), leash_also (ชั้นอื่นที่เป็นได้ คั่นด้วย ", ") — ข้อความล้วน
  classes.*                        ชื่อไทยของชั้นสายจูง เรียงจากแน่นที่สุด: contractual, mechanical, economic,
                                   statistical, speed

กราฟ: sas-p7-leash-types · sas-p7-leash-ladder · sas-p7-leash-excursion · sas-p7-pnl-identity ·
      sas-p7-funding-path · sas-p7-funding-horizon · sas-p7-rows-ladder
"""
import functools
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sas_core as C  # noqa: E402
import sas_svg as V  # noqa: E402

# ─────────────────────────────── ค่าที่ตั้งไว้: 7a ───────────────────────────────
N_TRAIN = 500            # แท่งที่ใช้วัดไม้บรรทัด (μ̂, σ̂ และ α̂, β̂ ของแบบ statistical)
N_TEST = 500             # แท่งที่ "เปิดเหตุการณ์ได้"
FOLLOW = 250             # ตามดูเหตุการณ์ได้นานสุดกี่แท่ง
N_BARS = N_TRAIN + N_TEST + FOLLOW + 1   # +1 แท่ง: ให้ไม้ที่ออกช้าไปหนึ่งแท่ง (lag 2) มีราคาให้ใช้
ENTRY_Z = 2.0            # แตะ: |z| ≥ 2
EXIT_Z = 0.5             # กลับ: z มาถึง 0.5 ฝั่งเดียวกับที่แตะ
WINDOW = 30              # "กลับภายใน 30 แท่ง"
WORLDS = 8000            # จำนวนโลกของแบบ contractual / mechanical / economic (พอให้ % จำนวนเต็มนิ่ง)
CANDIDATES = 100000      # จำนวนคู่ random walk ที่นำมาสแกน (ผ่านราว 5% ≈ 5,000 คู่)
EG_NULL_WORLDS = 100000  # จำนวนโลกที่ใช้หาเส้นตัด 5% ของ Engle-Granger
BOOT = 400               # จำนวนรอบของการสุ่มโลกซ้ำ (bootstrap) เพื่อบอกความแม่นของตัวเลข

SIGMA = 0.03             # สเกล σ ของ ε (เท่ากับคู่ good ของทั้งชุด)
LIFE = 63                # อายุสัญญา (แท่ง) ≈ หนึ่งไตรมาส
START_SD = 0.035         # sd ของระดับ ε ตอนสัญญาใหม่เริ่ม
NOISE_SD = 0.007         # sd ของการเดินสุ่มต่อแท่งระหว่างอายุสัญญา  (รวมแล้ว sd ตลอดอายุ ≈ 3%)
HL_MECH = 3.0            # half-life ของแบบกลไก
HL_ECON = 12.0           # half-life ของแบบเศรษฐกิจ (เท่ากับคู่ good)
JUMP_EVERY = 250         # ค่าเฉลี่ยของ ε แบบเศรษฐกิจกระโดดเฉลี่ยทุกกี่แท่ง
JUMP_SD = 2.0            # ขนาดการกระโดด = N(0, (JUMP_SD·σ)²)
RW_SIGMA = 0.008         # ความผันผวนต่อแท่งของ random walk แต่ละเส้น — ตั้งให้ σ̂ ของคู่ที่ผ่านการสแกนราว 3%
SENS_LIFE = (21, 63, 126)        # ลองอายุสัญญา: หนึ่งเดือน · หนึ่งไตรมาส (ค่าหลัก) · ครึ่งปี
SENS_JUMP = (125, 250, 500, 0)   # ลองความถี่การกระโดด: ทุก 125 · 250 (ค่าหลัก) · 500 แท่ง · 0 = ไม่กระโดดเลย

TYPES = ("contractual", "mechanical", "economic", "statistical")
TYPE_TH = {
    "contractual": "สัญญา (หมดอายุทุก 63 แท่ง)",
    "mechanical": "กลไก (ดึงทุกแท่ง · half-life 3)",
    "economic": "เศรษฐกิจ (half-life 12 + ค่าเฉลี่ยกระโดด)",
    "statistical": "สถิติล้วน (random walk ที่ผ่านการสแกน)",
}
TYPE_SHORT = {"contractual": "สัญญา", "mechanical": "กลไก", "economic": "เศรษฐกิจ", "statistical": "สถิติล้วน"}
TYPE_COLOR = {"contractual": V.GREEN, "mechanical": V.BLUE, "economic": V.AMBER, "statistical": V.RED}

# ─────────────────────────────── ค่าที่ตั้งไว้: 7b (ตัวเลขสมมติทั้งหมด) ───────────────────────────────
CARRY = {
    "spot": 100.0,            # ราคา spot วันนี้ (บาท)
    "future": 102.5,          # ราคา future ที่ตลาดเสนอ (บาท)
    "days": 90,               # จำนวนวันถึงวันหมดอายุ
    "rate": 0.04,             # ต้นทุนเงินต่อปี (ดอกเบี้ยอย่างง่าย · ปีละ 365 วัน)
    "cost": 0.0005,           # ต้นทุนเที่ยวเดียวต่อขา (5 bps ของมูลค่าที่ซื้อขาย)
    "legs": 4,                # ซื้อ spot · ขาย future · (วันหมดอายุ) ขาย spot · ปิด future
    "margin": 0.10,           # หลักประกันของ future เป็นสัดส่วนของมูลค่าสัญญา (ไม่ได้ดอกเบี้ย)
}
FUND = {
    "per_day": 3,             # funding จ่ายทุก 8 ชั่วโมง
    "days": 365,              # ถือหนึ่งปี (ตลาดเปิดทุกวัน)
    "mean_normal": 1.0,       # ค่าเฉลี่ยของ funding ช่วงปกติ (bps ต่อ 8 ชม. = 0.01%)
    "mean_negative": -1.5,    # ค่าเฉลี่ยช่วงติดลบ (bps ต่อ 8 ชม.)
    "persistence": 0.9,       # φ ของ funding ต่องวด (ค่างวดนี้เกาะค่างวดก่อนแค่ไหน)
    "shock": 0.3,             # sd ของสิ่งที่เข้ามาใหม่ในแต่ละงวด (bps)
    "p_enter": 1.0 / 270,     # โอกาสต่องวดที่ช่วงปกติจะพลิกเป็นช่วงติดลบ (เฉลี่ย 90 วันครั้ง)
    "p_exit": 1.0 / 45,       # โอกาสต่องวดที่ช่วงติดลบจะจบ (ช่วงติดลบยาวเฉลี่ย 15 วัน)
    "cost": 0.0005,           # ต้นทุนเที่ยวเดียวต่อขา (5 bps)
    "legs": 4,                # ซื้อ spot · short perp · (ตอนเลิก) ขาย spot · ปิด perp
    "rate": CARRY["rate"],    # ต้นทุนเงินของขา spot — เท่ากับตัวอย่าง cash-and-carry เพื่อเทียบบนฐานเดียวกัน
    "worlds": 8000,
    "horizons": (7, 30, 90, 365),
}

# ─────────────────────────────── 7c: ตารางเจ็ดแถวของสไลด์ 8 (โครงสร้างล้วน) ───────────────────────────────
CLASSES = (  # เรียงจากสายจูงที่ "แน่นอนที่สุด" ไปหา "ไม่มีอะไรรับประกัน" · speed แยกไว้ท้ายสุด
    ("contractual", "สัญญา"),
    ("mechanical", "กลไก"),
    ("economic", "เศรษฐกิจ"),
    ("statistical", "สถิติล้วน"),
    ("speed", "ความเร็ว"),
)
CLASS_WHY = {  # อะไรดึง ε กลับ (ใช้เป็นหัวคอลัมน์ของกราฟเท่านั้น)
    "contractual": "วันหมดอายุบังคับ",
    "mechanical": "กลไกดึงทุกงวด",
    "economic": "ธุรกิจทดแทนกัน",
    "statistical": "เจอจากการสแกน",
    "speed": "ใครเร็วกว่าได้",
}
ROWS = (  # (id, Y, X, ชื่อกลยุทธ์ตามสไลด์, Arbitrage Driver ตามสไลด์, ได้เงินจาก, ชั้นหลัก, ชั้นอื่นที่เป็นได้)
    ("pairs", "Stock", "Stock", "Standard Pairs Trading", "Mispricing & Fundamental",
     "convergence", "economic", ("statistical",)),
    ("basket", "Stock", "Portfolio", "Multi-Asset Pairs Trading", "Mispricing",
     "convergence", "statistical", ("mechanical", "economic")),
    ("funding", "Spot", "Perpetual Future", "Funding Rate Arbitrage", "Interest Rate",
     "carry", "mechanical", ()),
    ("cash_carry", "Spot", "Future", "Cash-and-Carry", "Mispricing",
     "convergence", "contractual", ()),
    ("swap", "Spot", "CFD", "Swap Arbitrage", "Interest Rate",
     "carry", "mechanical", ()),
    ("vol", "Spot", "Option", "Volatility Arbitrage", "Mispricing",
     "convergence", "economic", ("contractual",)),
    ("latency", "Spot at t", "Spot at t−1", "Latency Arbitrage", "Mispricing",
     "convergence", "speed", ()),
)


# ═══════════════════════════════ 7a: ตัวสร้าง ε สี่แบบ ═══════════════════════════════
def gen_contractual(g, worlds, n, life=LIFE):
    """สายจูงแบบสัญญา: ε เดินสุ่มได้ระหว่างทาง แต่สัญญาบังคับให้เป็น 0 พอดีในวันหมดอายุ แล้วสัญญาใหม่
    เริ่มที่ระดับสุ่ม ε₀ ~ N(0, START_SD²) (สะพานบราวน์ต่อกันเป็นลูกโซ่) → (ε, แท่งที่เป็นวันหมดอายุ)"""
    steps = life - 1
    k = -(-n // life)                                         # จำนวนสัญญาที่ต้องใช้ (ปัดขึ้น)
    start = START_SD * g.standard_normal((worlds, k, 1))
    walk = np.cumsum(NOISE_SD * g.standard_normal((worlds, k, steps)), axis=2)
    walk = np.concatenate([np.zeros((worlds, k, 1)), walk], axis=2)
    u = np.arange(life) / steps                               # 0 = วันแรกของสัญญา · 1 = วันหมดอายุ
    eps = start * (1.0 - u) + walk - u * walk[:, :, -1:]      # ที่ u = 1 ได้ 0 พอดี
    expiry = (np.arange(n) % life) == life - 1
    return eps.reshape(worlds, k * life)[:, :n], expiry


def gen_mechanical(g, worlds, n):
    """สายจูงแบบกลไก: กลไกของตลาดดึง ε กลับทุกแท่ง จึงเป็น AR(1) ที่เร็ว (half-life 3 แท่ง)"""
    return C.ar1_batch(worlds, n, HL_MECH, SIGMA, g)


def gen_economic(g, worlds, n, every=JUMP_EVERY):
    """สายจูงแบบเศรษฐกิจ: ธุรกิจทดแทนกันดึง ε กลับช้า ๆ (AR(1) half-life 12) แต่นาน ๆ ครั้งพื้นฐานเปลี่ยน
    จนค่าเฉลี่ยกระโดดถาวร → (ε, แท่งที่กระโดด)
    every = กระโดดเฉลี่ยทุกกี่แท่ง · 0 = ไม่กระโดดเลย (สายจูงเศรษฐกิจที่ไม่เคยขาด)"""
    base = C.ar1_batch(worlds, n, HL_ECON, SIGMA, g)
    jumped = g.random((worlds, n)) < (1.0 / every if every else 0.0)
    size = JUMP_SD * SIGMA * g.standard_normal((worlds, n))
    return base + np.cumsum(jumped * size, axis=1), jumped


@functools.lru_cache(maxsize=1)
def eg_cutoff():
    """เส้นตัด 5% ของ Engle-Granger สำหรับ 500 แท่ง 2 สินทรัพย์ lags=1 — จำลองเอง 100,000 โลก"""
    null = C.mc_null_eg(N_TRAIN, 2, n_sim=EG_NULL_WORLDS, lags=1, g=C.rng(701))
    return float(C.crit_values(null)[0.05])


def eg_screen(y, x, crit5):
    """สิ่งที่นักเทรดที่ "ไม่รู้เฉลย" ทำ: Engle-Granger บน 500 แท่งแรก (ถดถอย y บน x แล้ว ADF ของส่วนเหลือ)
    → (ผ่านเส้นตัด 5% หรือไม่, ε̂ ทั้งเส้นของคู่ที่ผ่าน) · ε̂ ใช้ α̂, β̂ จาก 500 แท่งแรกเท่านั้น ลากต่อไปจนจบ"""
    ytr, xtr = y[:, :N_TRAIN], x[:, :N_TRAIN]
    resid = C.resid_batch(ytr, xtr[:, :, None])               # ขั้นที่ 1 ของ EG: ถดถอย y บน x
    ok = C.adf_stat_batch(resid, lags=1, const=False) < crit5  # ขั้นที่ 2: ADF ของส่วนเหลือ
    xm = xtr[ok].mean(axis=1, keepdims=True)
    ym = ytr[ok].mean(axis=1, keepdims=True)
    beta = ((xtr[ok] - xm) * (ytr[ok] - ym)).sum(axis=1, keepdims=True) / ((xtr[ok] - xm) ** 2).sum(axis=1, keepdims=True)
    eps = y[ok] - ym - beta * (x[ok] - xm)
    assert np.allclose(eps[:, :N_TRAIN], resid[ok], atol=1e-9), "α̂, β̂ ไม่ตรงกับ resid_batch"
    return ok, eps


def gen_statistical(g, candidates, n, crit5, chunk=4000):
    """สายจูงแบบสถิติล้วน: random walk อิสระสองเส้นที่ไม่มีอะไรผูกกัน แต่ 500 แท่งแรกบังเอิญผ่าน EG 5%
    → (ε̂ ของคู่ที่ผ่าน, จำนวนที่สแกน)"""
    kept = []
    for _ in range(candidates // chunk):
        y = np.cumsum(RW_SIGMA * g.standard_normal((chunk, n)), axis=1)
        x = np.cumsum(RW_SIGMA * g.standard_normal((chunk, n)), axis=1)
        kept.append(eg_screen(y, x, crit5)[1])
    return np.concatenate(kept), (candidates // chunk) * chunk


# ═══════════════════════════════ 7a: กติกาเดียวกันทุกแบบ ═══════════════════════════════
def train_ruler(eps):
    """z ของทั้งเส้น วัดด้วย μ̂, σ̂ ของ 500 แท่งแรกเท่านั้น (ไม้บรรทัดไม่เห็นช่วง test)"""
    mu = eps[:, :N_TRAIN].mean(axis=1, keepdims=True)
    sd = eps[:, :N_TRAIN].std(axis=1, ddof=1, keepdims=True)
    return (eps - mu) / sd


def scan_events(z, expiry=None):
    """ไล่ทีละแท่ง (ทุกโลกพร้อมกัน) ตามกติกา แตะ |z| ≥ 2 → รอจน z กลับถึง 0.5
    คืนอาร์เรย์ต่อเหตุการณ์: world, t0, dur (จำนวนแท่งจนกลับ · inf = ไม่กลับใน 250 แท่ง),
    t_end (แท่งที่จบ), sign (ฝั่งที่แตะ), worst (หลุดไกลสุด), z0 (ระดับตอนแตะ), z_end (ระดับตอนจบ),
    settled (จบเพราะสัญญาหมดอายุ) · worst, z0, z_end ถูกพลิกเครื่องหมายให้ "ฝั่งที่แตะ" เป็นบวกเสมอ"""
    worlds, n = z.shape
    side = np.zeros(worlds)                 # +1 = แตะฝั่งบน · −1 = แตะฝั่งล่าง · 0 = ไม่มีเหตุการณ์ค้าง
    t0 = np.zeros(worlds, dtype=int)
    z0 = np.zeros(worlds)
    worst = np.zeros(worlds)
    resting = np.zeros(worlds, dtype=bool)  # หลังหมดเวลา 250 แท่ง ต้องรอ |z| < 2 ก่อนเปิดใหม่
    out = {k: [] for k in ("world", "t0", "t_end", "sign", "dur", "worst", "z0", "z_end", "settled")}
    for t in range(N_TRAIN, n):
        zt = z[:, t]
        sz = side * zt
        is_open = side != 0
        worst = np.where(is_open, np.maximum(worst, sz), worst)
        back = is_open & (sz <= EXIT_Z)
        settled = is_open & ~back & (expiry is not None and bool(expiry[t]))
        timeout = is_open & ~back & ~settled & (t - t0 >= FOLLOW)
        done = np.flatnonzero(back | settled | timeout)
        if done.size:
            out["world"].append(done)
            out["t0"].append(t0[done])
            out["t_end"].append(np.full(done.size, t))
            out["sign"].append(side[done])
            out["dur"].append(np.where(timeout[done], np.inf, (t - t0[done]).astype(float)))
            out["worst"].append(worst[done])
            out["z0"].append(z0[done])
            out["z_end"].append(sz[done])
            out["settled"].append(settled[done])
            side[done] = 0
            resting |= timeout
        resting &= np.abs(zt) >= ENTRY_Z
        if t < N_TRAIN + N_TEST:
            new = (side == 0) & ~resting & (np.abs(zt) >= ENTRY_Z)
            side[new] = np.sign(zt[new])
            t0[new] = t
            z0[new] = np.abs(zt[new])
            worst[new] = np.abs(zt[new])
    assert not side.any(), "ยังมีเหตุการณ์ค้าง — FOLLOW ต้องไม่เกินจำนวนแท่งหลังช่วง test"
    return {k: np.concatenate(v) if v else np.zeros(0) for k, v in out.items()}


def boot_range(num, den, g):
    """ช่วง 5–95% ของอัตราส่วน Σnum/Σden เมื่อ "สุ่มโลกซ้ำ" (เหตุการณ์ในโลกเดียวกันไม่อิสระกัน)"""
    idx = g.integers(0, len(num), size=(BOOT, len(num)))
    ratio = num[idx].sum(axis=1) / np.maximum(den[idx].sum(axis=1), 1)
    return float(np.percentile(ratio, 5)), float(np.percentile(ratio, 95))


def lag2_pnl(z, ev, expiry=None):
    """กำไรต่อเหตุการณ์ (หน่วย σ̂) ถ้าได้ราคาช้าไปหนึ่งแท่งทั้งตอนเข้าและตอนออก (lag 2)
    ไม้ที่จบในวันหมดอายุถูกชำระ ณ วันนั้น — ถือสัญญาที่หมดอายุแล้วต่อไม่ได้"""
    w, t0, t1 = ev["world"].astype(int), ev["t0"].astype(int), ev["t_end"].astype(int)
    out_bar = t1 + 1 if expiry is None else np.where(expiry[t1], t1, t1 + 1)
    return ev["sign"] * (z[w, t0 + 1] - z[w, out_bar])


def summarize(z, ev, g, expiry=None):
    """ตัวเลขสรุปของ ε หนึ่งแบบ จากเหตุการณ์ทั้งหมดของทุกโลก"""
    worlds = z.shape[0]
    n_ev = len(ev["dur"])
    dur, worst = ev["dur"], ev["worst"]
    pnl = ev["z0"] - ev["z_end"]                            # กำไรก่อนต้นทุน หน่วย σ̂ (เข้า z0 ออก z_end)
    w = ev["world"].astype(int)
    per_world = np.bincount(w, minlength=worlds).astype(float)
    back30 = np.bincount(w, weights=(dur <= WINDOW).astype(float), minlength=worlds)
    pnl_w = np.bincount(w, weights=pnl, minlength=worlds)
    p30_lo, p30_hi = boot_range(back30, per_world, g)
    pnl_lo, pnl_hi = boot_range(pnl_w, per_world, g)
    curve = np.searchsorted(np.sort(dur), np.arange(FOLLOW + 1), side="right") / n_ev   # กลับแล้วภายใน k แท่ง
    test = z[:, N_TRAIN:N_TRAIN + N_TEST]
    return {
        "worlds": worlds, "events": n_ev,
        "events_per_world": n_ev / worlds,
        "worlds_with_event": float((per_world > 0).mean()),
        "z_sd_test": float(np.median(test.std(axis=1, ddof=1))),
        "z_rms_test": float(np.median(np.sqrt((test ** 2).mean(axis=1)))),
        "p30": float((dur <= WINDOW).mean()), "p30_lo": p30_lo, "p30_hi": p30_hi,
        "curve": curve,
        "never": float(np.isinf(dur).mean()),
        "median_return": float(np.median(dur)),             # ไม้ที่ไม่กลับ (inf) นับเป็น "นานกว่า 250 แท่ง"
        "worst_median": float(np.median(worst)),
        "worst_p05": float(np.percentile(worst, 5)),
        "worst_p95": float(np.percentile(worst, 95)),
        "worst_ge4": float((worst >= 2 * ENTRY_Z).mean()),
        "avg_pnl": float(pnl.mean()), "avg_pnl_lo": pnl_lo, "avg_pnl_hi": pnl_hi,
        "avg_pnl_lag2": float(lag2_pnl(z, ev, expiry).mean()),
        "demo_z": z[typical_world(test), :N_TRAIN + N_TEST].copy(),
    }


def typical_world(test_z):
    """โลกตัวอย่างสำหรับวาดกราฟ: โลกที่ค่า |z| สูงสุดในช่วง test ใกล้ "ค่ากลางของทุกโลก" ที่สุด
    (เลือกตัวแทนแบบกลาง ๆ ไม่ได้เลือกโลกที่สวยหรือแย่ที่สุด)"""
    peak = np.abs(test_z).max(axis=1)
    return int(np.argmin(np.abs(peak - np.median(peak))))


def measure(eps, boot_seed, expiry=None):
    """ไม้บรรทัด → เหตุการณ์ → ตัวเลขสรุป (กติกาเดียวกันทุกแบบ) → (ตัวเลขสรุป, เหตุการณ์)"""
    z = train_ruler(eps)
    ev = scan_events(z, expiry)
    return summarize(z, ev, C.rng(boot_seed), expiry), ev


def brief(s):
    return {k: s[k] for k in ("worlds", "events", "p30", "never", "median_return", "worst_p95", "avg_pnl")}


def same_filter(eps, expiry, x_seed, boot_seed, crit5, chunk=2000):
    """ให้ ε ที่มีสายจูงจริงผ่านขั้นตอนเดียวกับแบบสถิติล้วน: x = random walk, y = x + ε, ประมาณ α̂, β̂ และทดสอบ EG
    บน 500 แท่งแรก แล้ววัดเฉพาะโลกที่ผ่าน (ส่วนเหลือของ y บน x = ส่วนเหลือของ ε บน x — α, β จริงไม่มีผล)"""
    g = C.rng(x_seed)
    ok, kept = [], []
    for s in range(0, eps.shape[0], chunk):
        e = eps[s:s + chunk]
        x = np.cumsum(RW_SIGMA * g.standard_normal(e.shape), axis=1)
        passed, e_hat = eg_screen(x + e, x, crit5)
        ok.append(passed)
        kept.append(e_hat)
    out = brief(measure(np.concatenate(kept), boot_seed, expiry)[0])
    out["eg_pass"] = float(np.concatenate(ok).mean())
    return out


def exp_ladder():
    crit5 = eg_cutoff()
    out = {"crit5": crit5}
    filt = {}

    eps, expiry = gen_contractual(C.rng(710), WORLDS, N_BARS)
    s, ev = measure(eps, 790, expiry)
    left = (LIFE - 1) - ev["t0"].astype(int) % LIFE          # แท่งที่เหลือถึงวันหมดอายุ ณ ตอนแตะ
    near = left <= WINDOW
    s.update({
        "ended_at_expiry": float(expiry[ev["t_end"].astype(int)].mean()),   # สัญญาเป็นคนปิดเกมให้
        "median_left": float(np.median(left)),
        "near_events": int(near.sum()), "near_p30": float((ev["dur"][near] <= WINDOW).mean()),
        "far_events": int((~near).sum()), "far_p30": float((ev["dur"][~near] <= WINDOW).mean()),
        "pooled_sd": float(eps[:, :N_TRAIN].std()),
    })
    out["contractual"] = s
    filt["contractual"] = same_filter(eps, expiry, 715, 796, crit5)

    eps = gen_mechanical(C.rng(720), WORLDS, N_BARS)
    out["mechanical"] = measure(eps, 791)[0]
    filt["mechanical"] = same_filter(eps, None, 725, 797, crit5)

    eps, jumped = gen_economic(C.rng(730), WORLDS, N_BARS)
    s, ev = measure(eps, 792)
    csum = np.concatenate([np.zeros((WORLDS, 1)), np.cumsum(jumped, axis=1)], axis=1)
    w, a = ev["world"].astype(int), ev["t0"].astype(int)
    b = a + np.where(np.isinf(ev["dur"]), FOLLOW, ev["dur"]).astype(int)
    hit = (csum[w, b + 1] - csum[w, a]) > 0                  # มีการกระโดดตั้งแต่แท่งที่แตะถึงแท่งที่จบ
    s.update({
        "with_jump": float(hit.mean()),
        "p30_no_jump": float((ev["dur"][~hit] <= WINDOW).mean()),
        "p30_with_jump": float((ev["dur"][hit] <= WINDOW).mean()),
    })
    out["economic"] = s
    filt["economic"] = same_filter(eps, None, 735, 798, crit5)
    del eps, jumped, csum

    eps, scanned = gen_statistical(C.rng(740), CANDIDATES, N_BARS, crit5)
    s = measure(eps, 793)[0]
    s.update({"candidates": scanned, "pass_rate": eps.shape[0] / scanned,
              "train_sd": float(np.median(eps[:, :N_TRAIN].std(axis=1, ddof=1)))})
    out["statistical"] = s
    out["same_filter"] = filt
    out["sensitivity"] = exp_sensitivity(out)
    return out


def exp_sensitivity(main):
    """สองปุ่มที่ผลของ 7a ขึ้นกับมันมากที่สุด: อายุสัญญา (แบบสัญญา) และความถี่ของการกระโดด (แบบเศรษฐกิจ)
    แถวที่ตรงกับค่าหลักใช้ผลของการทดลองหลักตรง ๆ (ไม่จำลองซ้ำ)"""
    out = {"contract": {}, "economic": {}}
    for i, life in enumerate(SENS_LIFE):
        if life == LIFE:
            out["contract"][f"life{life}"] = brief(main["contractual"])
        else:
            eps, expiry = gen_contractual(C.rng(711 + i), WORLDS, N_BARS, life)
            out["contract"][f"life{life}"] = brief(measure(eps, 794, expiry)[0])
    for i, every in enumerate(SENS_JUMP):
        key = f"every{every}" if every else "no_jump"
        out["economic"][key] = brief(main["economic"]) if every == JUMP_EVERY else brief(measure(
            gen_economic(C.rng(731 + i), WORLDS, N_BARS, every)[0], 795)[0])
    return out


# ═══════════════════════════════ 7b: cash-and-carry ═══════════════════════════════
def exp_carry():
    """ซื้อ spot + ขาย future แล้วถือจนหมดอายุ — ทุกบรรทัดเป็นเลขคณิตบนค่าสมมติใน CARRY (บาทต่อ spot 100 บาท)"""
    a = CARRY
    s, f, c = a["spot"], a["future"], a["cost"]
    t = a["days"] / 365.0
    financing = s * a["rate"] * t                 # ดอกเบี้ยของเงินที่ใช้ซื้อ spot
    fair = s + financing                          # ราคายุติธรรมของ future (ไม่มีปันผล/ผลตอบแทนจากการถือ spot)
    mispricing = f - fair                         # ε ของแถวนี้: ส่วนที่ future แพงเกินราคายุติธรรม
    basis = f - s                                 # ส่วนต่างที่ "ล็อก" ได้ เพราะวันหมดอายุ future = spot
    cost_in = c * (s + f)                         # ซื้อ spot + ขาย future
    cost_out = c * 2 * s                          # ขาย spot + ปิด future ที่ราคาวันหมดอายุ (ประมาณด้วยราคาวันนี้)
    costs = cost_in + cost_out
    net = basis - financing - costs               # = ส่วนที่ได้เกินการฝากเงินไว้ที่อัตรา rate
    margin = a["margin"] * f
    margin_fin = margin * a["rate"] * t           # ต้นทุนเงินของหลักประกันที่วางทิ้งไว้
    net_m = net - margin_fin
    capital = s + margin
    # ราคา future ต่ำสุดที่ยังคุ้ม: แก้ (F − S) − S·r·T − c(S + F) − 2cS = 0  (และแบบมีต้นทุนเงินของหลักประกัน)
    breakeven = s * (1 + a["rate"] * t + 3 * c) / (1 - c)
    breakeven_m = s * (1 + a["rate"] * t + 3 * c) / (1 - c - a["margin"] * a["rate"] * t)
    return {
        "t": t, "financing": financing, "fair": fair, "mispricing": mispricing,
        "mispricing_log": math.log(f / fair), "basis": basis,
        "cost_in": cost_in, "cost_out": cost_out, "costs": costs, "net": net,
        "net_per_year": net / s / t,
        "margin": margin, "margin_fin": margin_fin, "net_m": net_m, "capital": capital,
        "net_on_capital": net_m / capital, "net_on_capital_per_year": net_m / capital / t,
        "breakeven": breakeven, "breakeven_mispricing": breakeven - fair,
        "breakeven_m": breakeven_m, "breakeven_m_mispricing": breakeven_m - fair,
    }


# ═══════════════════════════════ 7b: funding ═══════════════════════════════
def simulate_funding(g, worlds, periods):
    """อัตรา funding ราย 8 ชม. (bps): AR(1) รอบค่าเฉลี่ยของ "ช่วง" ปัจจุบัน
    ช่วงมีสองแบบ (ปกติ / ติดลบ) สลับกันแบบสุ่มด้วยโอกาสคงที่ต่องวด → (funding, อยู่ช่วงติดลบหรือไม่)"""
    a = FUND
    phi, shock = a["persistence"], a["shock"]
    share_neg = a["p_enter"] / (a["p_enter"] + a["p_exit"])
    neg = g.random(worlds) < share_neg                       # เริ่มจากสัดส่วนระยะยาวของสองช่วง
    mean = np.where(neg, a["mean_negative"], a["mean_normal"])
    f = mean + shock / math.sqrt(1 - phi * phi) * g.standard_normal(worlds)
    rates = np.empty((worlds, periods))
    regime = np.empty((worlds, periods), dtype=bool)
    for t in range(periods):
        if t:
            u = g.random(worlds)
            neg = np.where(neg, u >= a["p_exit"], u < a["p_enter"])
            mean = np.where(neg, a["mean_negative"], a["mean_normal"])
            f = mean + phi * (f - mean) + shock * g.standard_normal(worlds)
        rates[:, t] = f
        regime[:, t] = neg
    return rates, regime


def funding_expectation():
    """ค่าคาดหมายของ funding ต่องวดตามแบบจำลอง (เลขคณิตล้วน): สัดส่วนเวลาของช่วงติดลบ × ค่าเฉลี่ยช่วงติดลบ
    + สัดส่วนเวลาของช่วงปกติ × ค่าเฉลี่ยช่วงปกติ (เริ่มจากสัดส่วนระยะยาว ค่าคาดหมายจึงเท่านี้ทุกงวด)"""
    a = FUND
    share_neg = a["p_enter"] / (a["p_enter"] + a["p_exit"])
    return share_neg, share_neg * a["mean_negative"] + (1 - share_neg) * a["mean_normal"]


def first_day(paid, per_day):
    """วันแรกที่ "ถ้าปิดตอนนี้จะไม่ขาดทุน" (inf = ไม่ถึงเลยภายในปี)"""
    return np.where(paid.any(axis=1), paid.argmax(axis=1) + 1.0, np.inf) / per_day


def exp_funding():
    """ถือ spot + short perp หนึ่งปี: รับ funding เมื่อเป็นบวก จ่ายเมื่อเป็นลบ · หน่วย bps ของมูลค่าหนึ่งขา
    เงินในขา spot มีต้นทุน (หรือเสียโอกาสฝาก) rate ต่อปี เท่ากับตัวอย่าง cash-and-carry"""
    a = FUND
    per_day = a["per_day"]
    periods = per_day * a["days"]
    rates, regime = simulate_funding(C.rng(750), a["worlds"], periods)
    cum = np.cumsum(rates, axis=1)                           # funding สะสม (bps) ที่ได้เมื่อถือถึงสิ้นงวดนั้น
    costs = a["legs"] * a["cost"] * 1e4                      # ค่าเข้า + ค่าออก (bps ของมูลค่าหนึ่งขา)
    fin_per = a["rate"] / 365.0 / per_day * 1e4              # ต้นทุนเงินต่องวด (bps · ดอกเบี้ยอย่างง่าย)
    fin = fin_per * np.arange(1, periods + 1)                # ต้นทุนเงินสะสมถึงสิ้นงวดนั้น
    w30 = 30 * per_day
    roll = cum[:, w30 - 1:] - np.concatenate([np.zeros((a["worlds"], 1)), cum[:, :-w30]], axis=1)
    share_neg, expected = funding_expectation()
    year = cum[:, -1]
    demo = int(np.argmin(np.abs(year - np.median(year))))    # โลกตัวอย่าง: funding ทั้งปีใกล้ค่ากลางที่สุด
    hz = {}
    for d in a["horizons"]:
        i = d * per_day - 1
        hz[d] = {"net": cum[:, i] - costs - fin[i], "before_fin": cum[:, i] - costs}
    return {
        "periods": periods, "costs": costs, "fin_per": fin_per, "year": year,
        "year_net": year - costs - fin[-1],
        "worst30": roll.min(axis=1),                         # 30 วันติดกันที่ funding รวมแย่ที่สุดของปี
        "first": first_day(cum - fin >= costs, per_day),     # คุ้มค่าซื้อขาย + ต้นทุนเงินครั้งแรก
        "first_costs_only": first_day(cum >= costs, per_day),
        "neg_share": (rates < 0).mean(axis=1), "regime_share": float(regime.mean()),
        "share_neg_longrun": share_neg, "longrun": expected, "horizons": hz,
        "gross90": cum[:, 90 * per_day - 1],
        "demo_rates": rates[demo].copy(), "demo_regime": regime[demo].copy(),
        "demo_net": cum[demo] - costs - fin, "demo_before_fin": cum[demo] - costs,
    }


def exp_identity(carry, funding):
    """P&L = convergence + carry − costs ของสองตัวอย่าง ถือ 90 วันเท่ากัน บาทต่อเงิน 100 บาทในขา spot
    ทั้งสองฝั่งหักต้นทุนเงินของขา spot เท่ากัน (carry = รายได้ระหว่างถือ − ต้นทุนเงิน)"""
    days = CARRY["days"]
    fin = carry["financing"]
    basis_interest = carry["fair"] - CARRY["spot"]           # ส่วนของ basis ที่เป็น "ดอกเบี้ยยุติธรรม"
    cc = {"convergence": carry["mispricing"], "basis_interest": basis_interest, "financing": fin,
          "carry": basis_interest - fin, "costs": carry["costs"], "net": carry["net"]}
    expected = funding["longrun"] * days * FUND["per_day"] / 100.0   # bps → บาทต่อ 100 บาท (ค่าคาดหมาย)
    costs = funding["costs"] / 100.0
    carry_mc = funding["gross90"] / 100.0 - fin               # carry ของแต่ละโลก (หลังหักต้นทุนเงิน)
    fu = {"convergence": 0.0, "funding": expected, "financing": fin, "carry": expected - fin,
          "costs": costs, "net": expected - fin - costs,
          "funding_mc_mean": float((funding["gross90"] / 100.0).mean()),
          "carry_lo": float(np.percentile(carry_mc, 5)), "carry_hi": float(np.percentile(carry_mc, 95)),
          "net_lo": float(np.percentile(carry_mc - costs, 5)), "net_hi": float(np.percentile(carry_mc - costs, 95)),
          "loss": float((carry_mc - costs < 0).mean())}
    return {"cash_carry": cc, "funding": fu}


# ═══════════════════════════════ run ═══════════════════════════════
@functools.lru_cache(maxsize=1)
def run():
    ladder = exp_ladder()
    carry = exp_carry()
    funding = exp_funding()
    return {"ladder": ladder, "carry": carry, "funding": funding,
            "identity": exp_identity(carry, funding)}


# ═══════════════════════════════ figures: การปัดเลข ═══════════════════════════════
def _whole(v, d=1):
    """เก็บเป็น int ถ้าปัดแล้วเป็นจำนวนเต็มพอดี (fill จะได้ไม่พิมพ์ '12.0')"""
    r = C.rd(v, d)
    return int(r) if r is not None and float(r).is_integer() else r


def _ipct(v):
    """สัดส่วน → % จำนวนเต็ม (ความแม่นของ Monte Carlo ในตอนนี้ไม่พอสำหรับทศนิยม)
    ยกเว้นค่าที่ห่างจาก 0 หรือ 100 ไม่ถึง 1 จุด เก็บทศนิยมหนึ่งตำแหน่ง — ไม่ให้ 99.8 กลายเป็น "100" """
    return _whole(v * 100.0, 1 if (0 < v < 0.01 or 0.99 < v < 1) else 0)


def _rn(v, step=5):
    """ปัดทีละ step (bps หรือแท่ง/วัน ที่หลักหน่วยยังแกว่งตาม seed)"""
    return None if v is None or not math.isfinite(v) else int(step * round(v / step))


def _sig2(v):
    """สองหลักสำคัญ: 3.28 → 3.3 · 11.18 → 11"""
    return C.rd(v, 1) if abs(v) < 10 else _whole(v, 0)


def _p(arr, q):
    return float(np.percentile(arr, q))


# ═══════════════════════════════ figures ═══════════════════════════════
def _fig_type(s):
    cv = s["curve"]
    return {
        "worlds": int(s["worlds"]), "events": int(s["events"]),
        "events_per_world": C.rd(s["events_per_world"], 1),
        "worlds_with_event_pct": _ipct(s["worlds_with_event"]),
        "z_sd_test": C.rd(s["z_sd_test"], 1), "z_rms_test": C.rd(s["z_rms_test"], 1),
        "p30_pct": _ipct(s["p30"]), "p30_lo_pct": _ipct(s["p30_lo"]), "p30_hi_pct": _ipct(s["p30_hi"]),
        "back10_pct": _ipct(cv[10]), "back63_pct": _ipct(cv[63]),
        "back125_pct": _ipct(cv[125]), "back250_pct": _ipct(cv[FOLLOW]),
        "never250_pct": _ipct(s["never"]),
        "median_return_bars": _median_bars(s["median_return"]),
        "worst_median_sigma": C.rd(s["worst_median"], 1),
        "worst_p05_sigma": C.rd(s["worst_p05"], 1),
        "worst_p95_sigma": _sig2(s["worst_p95"]),
        "worst_ge4_pct": _ipct(s["worst_ge4"]),
        "avg_pnl_sigma": C.rd(s["avg_pnl"], 1),
        "avg_pnl_lo_sigma": C.rd(s["avg_pnl_lo"], 1), "avg_pnl_hi_sigma": C.rd(s["avg_pnl_hi"], 1),
        "avg_pnl_lag2_sigma": C.rd(s["avg_pnl_lag2"], 1),
    }


def _median_bars(v):
    """เวลากลับค่ากลาง: จำนวนเต็มเมื่อไม่เกิน 50 แท่ง · ทีละ 5 เมื่อยาวกว่านั้น (หางยาว ค่ากลางแกว่งตาม seed)"""
    return _whole(v, 0) if v <= 50 else _rn(v, 5)


def _fig_brief(v):
    return {"worlds": int(v["worlds"]), "events": int(v["events"]), "p30_pct": _ipct(v["p30"]),
            "never250_pct": _ipct(v["never"]), "median_return_bars": _median_bars(v["median_return"]),
            "worst_p95_sigma": _sig2(v["worst_p95"]), "avg_pnl_sigma": C.rd(v["avg_pnl"], 1)}


def _fig_ladder(la):
    st = la["statistical"]
    out = {
        "settings": {
            "train_bars": N_TRAIN, "test_bars": N_TEST, "follow_bars": FOLLOW,
            "entry_z": int(ENTRY_Z), "exit_z": EXIT_Z, "window_bars": WINDOW,
            "worlds": WORLDS, "candidates": int(st["candidates"]), "selected": int(st["worlds"]),
            "pass_rate_pct": _ipct(st["pass_rate"]),
            "eg_crit5": C.rd(la["crit5"], 2), "eg_null_worlds": EG_NULL_WORLDS, "boot_resamples": BOOT,
        },
        "assumptions": {
            "sigma_pct": _whole(SIGMA * 100),
            "contract_life_bars": LIFE,
            "contract_start_sd_pct": C.pct(START_SD, 1), "contract_noise_sd_pct": C.pct(NOISE_SD, 1),
            "contract_pooled_sd_pct": C.pct(la["contractual"]["pooled_sd"], 1),
            "mechanical_half_life_bars": int(HL_MECH), "economic_half_life_bars": int(HL_ECON),
            "jump_every_bars": JUMP_EVERY, "jump_sd_sigma": int(JUMP_SD),
            "rw_sigma_pct": C.pct(RW_SIGMA, 1),
            "statistical_train_sd_pct": C.pct(st["train_sd"], 1),
        },
    }
    for k in TYPES:
        out[k] = _fig_type(la[k])
    c, e = la["contractual"], la["economic"]
    out["contractual"].update({
        "ended_at_expiry_pct": _ipct(c["ended_at_expiry"]),
        "median_bars_to_expiry_at_touch": _whole(c["median_left"], 0),
        "near_expiry_events": int(c["near_events"]), "near_expiry_p30_pct": _ipct(c["near_p30"]),
        "far_expiry_events": int(c["far_events"]), "far_expiry_p30_pct": _ipct(c["far_p30"]),
    })
    out["economic"].update({
        "events_with_jump_pct": _ipct(e["with_jump"]),
        "p30_no_jump_pct": _ipct(e["p30_no_jump"]), "p30_with_jump_pct": _ipct(e["p30_with_jump"]),
    })
    out["same_filter"] = {k: {"eg_pass_pct": _ipct(v["eg_pass"]), **_fig_brief(v)}
                          for k, v in la["same_filter"].items()}
    out["sensitivity"] = {group: {key: _fig_brief(v) for key, v in rows.items()}
                          for group, rows in la["sensitivity"].items()}
    return out


def _fig_carry(ca):
    a = CARRY
    return {
        "assumptions": {
            "spot_baht": int(a["spot"]), "quoted_future_baht": a["future"], "days_to_expiry": a["days"],
            "financing_rate_pct_per_year": _whole(a["rate"] * 100), "cost_per_leg_bps": _whole(a["cost"] * 1e4),
            "legs": a["legs"], "futures_margin_pct": _whole(a["margin"] * 100), "spot_yield_pct": 0,
            "day_count": "actual/365",
        },
        "year_fraction": C.rd(ca["t"], 4),
        "financing_baht": C.rd(ca["financing"], 2),
        "fair_future_baht": C.rd(ca["fair"], 2),
        "mispricing_baht": C.rd(ca["mispricing"], 2),
        "mispricing_bps": _whole(ca["mispricing"] / a["spot"] * 1e4, 0),
        "mispricing_log_pct": C.pct(ca["mispricing_log"], 2),
        "basis_baht": C.rd(ca["basis"], 2),
        "cost_entry_baht": C.rd(ca["cost_in"], 3), "cost_exit_baht": C.rd(ca["cost_out"], 3),
        "costs_baht": C.rd(ca["costs"], 2), "costs_bps": C.bps(ca["costs"] / a["spot"], 1),
        "locked_net_baht": C.rd(ca["net"], 2),
        "locked_net_pct": C.pct(ca["net"] / a["spot"], 2),
        "locked_net_pct_per_year": C.pct(ca["net_per_year"], 2),
        "with_margin": {
            "margin_baht": C.rd(ca["margin"], 2), "margin_financing_baht": C.rd(ca["margin_fin"], 2),
            "net_baht": C.rd(ca["net_m"], 2), "capital_baht": C.rd(ca["capital"], 2),
            "net_on_capital_pct": C.pct(ca["net_on_capital"], 2),
            "net_on_capital_pct_per_year": C.pct(ca["net_on_capital_per_year"], 2),
            "breakeven_future_baht": C.rd(ca["breakeven_m"], 2),
            "breakeven_mispricing_bps": _whole(ca["breakeven_m_mispricing"] / a["spot"] * 1e4, 0),
        },
        "breakeven_future_baht": C.rd(ca["breakeven"], 2),
        "breakeven_mispricing_bps": _whole(ca["breakeven_mispricing"] / a["spot"] * 1e4, 0),
    }


def _fig_funding(fu):
    a = FUND
    per_year = a["per_day"] * 365
    yr = fu["year"] / 100.0                                  # bps → % ของมูลค่าหนึ่งขา
    net_yr = fu["year_net"] / 100.0
    fin_year = a["rate"] * 100.0
    out = {
        "assumptions": {
            "periods_per_day": a["per_day"], "hold_days": a["days"],
            "mean_normal_bps_per_8h": _whole(a["mean_normal"]), "mean_negative_bps_per_8h": _whole(a["mean_negative"]),
            "persistence": a["persistence"], "shock_bps": a["shock"],
            "enter_negative_prob_pct_per_8h": C.pct(a["p_enter"], 2),
            "exit_negative_prob_pct_per_8h": C.pct(a["p_exit"], 2),
            "enter_negative_every_days": int(round(1 / a["p_enter"] / a["per_day"])),
            "negative_spell_days": int(round(1 / a["p_exit"] / a["per_day"])),
            "negative_regime_share_pct": C.pct(fu["share_neg_longrun"], 1),
            "cost_per_leg_bps": _whole(a["cost"] * 1e4), "legs": a["legs"],
            "financing_rate_pct_per_year": _whole(fin_year),
            "basis_change_bps": 0,
        },
        "settings": {"worlds": a["worlds"], "periods": int(fu["periods"])},
        "costs_bps": _whole(fu["costs"]),
        "financing_bps_per_8h": C.rd(fu["fin_per"], 3),
        # เลขคณิตบนค่าสมมติ (ไม่ใช่ Monte Carlo)
        "headline_carry_pct_per_year": C.rd(a["mean_normal"] * per_year / 100.0, 2),
        "longrun_mean_bps_per_8h": C.rd(fu["longrun"], 3),
        "longrun_carry_pct_per_year": C.rd(fu["longrun"] * per_year / 100.0, 2),
        "net_expected_pct_per_year": C.rd(fu["longrun"] * per_year / 100.0 - fin_year - fu["costs"] / 100.0, 2),
        # Monte Carlo
        "carry_mean_pct_per_year": C.rd(yr.mean(), 1),
        "carry_median_pct_per_year": C.rd(np.median(yr), 1),
        "carry_p05_pct_per_year": _whole(_p(yr, 5), 0), "carry_p95_pct_per_year": _whole(_p(yr, 95), 0),
        "net_mean_pct_per_year": C.rd(net_yr.mean(), 1),
        "net_p05_pct_per_year": _whole(_p(net_yr, 5), 0), "net_p95_pct_per_year": _whole(_p(net_yr, 95), 0),
        "negative_periods_pct": _ipct(fu["neg_share"].mean()),
        "negative_periods_p05_pct": _ipct(_p(fu["neg_share"], 5)),
        "negative_periods_p95_pct": _ipct(_p(fu["neg_share"], 95)),
        "negative_regime_time_pct": _ipct(fu["regime_share"]),
        "worst30_median_bps": _rn(np.median(fu["worst30"]), 10),
        "worst30_p05_bps": _rn(_p(fu["worst30"], 5), 10), "worst30_p95_bps": _rn(_p(fu["worst30"], 95), 10),
        "worst30_negative_pct": _ipct((fu["worst30"] < 0).mean()),
        # เลขคณิต: ถ้า funding เท่ากับค่าเฉลี่ยตลอด ต้องถือกี่วันจึงคุ้ม (ค่าซื้อขาย + ต้นทุนเงิน)
        "breakeven_days_at_normal": C.rd(fu["costs"] / (a["mean_normal"] - fu["fin_per"]) / a["per_day"], 1),
        "breakeven_days_at_longrun": C.rd(fu["costs"] / (fu["longrun"] - fu["fin_per"]) / a["per_day"], 1),
        # Monte Carlo: วันแรกที่ปิดแล้วไม่แพ้การฝากเงิน
        "breakeven_days_median": _whole(np.median(fu["first"]), 0),
        "breakeven_days_p05": _whole(_p(fu["first"], 5), 0), "breakeven_days_p95": _rn(_p(fu["first"], 95), 10),
        "never_breakeven_pct": _ipct(np.isinf(fu["first"]).mean()),
        "breakeven_costs_only_days_median": _whole(np.median(fu["first_costs_only"]), 0),
    }
    for d, h in fu["horizons"].items():
        net = h["net"]
        out[f"hold{d}"] = {
            "net_median_bps": _rn(np.median(net), 5), "net_p05_bps": _rn(_p(net, 5), 10),
            "net_p95_bps": _rn(_p(net, 95), 10), "loss_pct": _ipct((net < 0).mean()),
            "loss_before_financing_pct": _ipct((h["before_fin"] < 0).mean()),
        }
    return out


def _fig_identity(idn):
    cc, fu = idn["cash_carry"], idn["funding"]
    out = {"hold_days": CARRY["days"]}
    out["cash_carry"] = {k + "_baht": C.rd(cc[k], 2)
                         for k in ("convergence", "basis_interest", "financing", "carry", "costs", "net")}
    out["funding"] = {k + "_baht": C.rd(fu[k], 2)
                      for k in ("convergence", "funding", "financing", "carry", "costs", "net")}
    out["funding"].update({
        "funding_mc_mean_baht": C.rd(fu["funding_mc_mean"], 1),
        "carry_p05_baht": C.rd(fu["carry_lo"], 1), "carry_p95_baht": C.rd(fu["carry_hi"], 1),
        "net_p05_baht": C.rd(fu["net_lo"], 1), "net_p95_baht": C.rd(fu["net_hi"], 1),
        "loss_pct": _ipct(fu["loss"]),
    })
    return out


def _fig_rows():
    rows = {}
    for i, (rid, y, x, strategy, driver, paid_by, leash, also) in enumerate(ROWS, 1):
        rows[f"row{i}"] = {"id": rid, "label": f"{y} – {x}", "y": y, "x": x,
                           "strategy": strategy, "driver": driver,
                           "paid_by": paid_by, "leash": leash, "leash_also": ", ".join(also)}
    return rows


def _about(fg):
    st, fa = fg["ladder"]["settings"], fg["funding_example"]["assumptions"]
    fs, ca = fg["funding_example"]["settings"], fg["carry_example"]["assumptions"]
    return {
        "data": "ข้อมูลจำลองทั้งหมด · ตัวอย่างเงินใน 7b เป็นตัวเลขสมมติ ไม่ใช่ราคาตลาด",
        "ladder": (f"7a บันไดสายจูง: ε สี่แบบ วัดด้วยกติกาเดียวกัน — ไม้บรรทัด μ̂, σ̂ จาก {st['train_bars']} แท่งแรก · "
                   f"เปิดเหตุการณ์เมื่อ |z| ≥ {st['entry_z']} ใน {st['test_bars']} แท่งถัดไป · กลับ = z มาถึง "
                   f"{st['exit_z']} · ตามดูนานสุด {st['follow_bars']} แท่ง · ไม่คิดต้นทุน"),
        "ladder_worlds": (f"สัญญา/กลไก/เศรษฐกิจ แบบละ {st['worlds']:,} โลก · สถิติล้วน: สแกน random walk "
                          f"{st['candidates']:,} คู่ ผ่าน EG 5% (เส้นตัด {V.num(st['eg_crit5'])} จากการจำลอง "
                          f"{st['eg_null_worlds']:,} โลก) {st['selected']:,} คู่"),
        "ladder_range": (f"ช่วงในวงเล็บของ % ที่กลับภายใน 30 แท่ง และกำไรเฉลี่ย คือช่วง 5–95% จากการสุ่มโลกซ้ำ "
                         f"{st['boot_resamples']} รอบ (บอกความแม่นของตัวเลข ไม่ใช่การกระจายของแต่ละไม้) · "
                         "ช่วงของระยะหลุดไกลสุด (worst_p05/p95) คือการกระจายของแต่ละเหตุการณ์"),
        "ladder_median": "เวลากลับค่ากลางนับไม้ที่ไม่กลับใน 250 แท่งเป็น \"นานกว่า 250\" · ค่าที่ยาวกว่า 50 แท่งปัดทีละ 5",
        "ladder_same_filter": ("same_filter: ให้สามแบบที่มีสายจูงจริงผ่านขั้นตอนเดียวกับแบบสถิติล้วน (ประมาณ α̂, β̂ "
                               "และทดสอบ EG 5% บน 500 แท่งแรก แล้ววัดเฉพาะโลกที่ผ่าน) · eg_pass_pct = % ของโลกที่ผ่าน"),
        "ladder_sensitivity": (f"ลองเปลี่ยนสองปุ่ม แบบละ {st['worlds']:,} โลก กติกาเดิม: อายุสัญญา 21 / 63 / 126 แท่ง "
                               "และค่าเฉลี่ยของแบบเศรษฐกิจกระโดดทุก 125 / 250 / 500 แท่ง หรือไม่กระโดดเลย "
                               "(life63 และ every250 คือการทดลองหลัก)"),
        "ladder_z": ("z ทุกตัววัดด้วย σ ที่ประมาณจากช่วง train ไม่ใช่ σ จริง — z_rms_test คือขนาดของ z ที่เกิดจริง"
                     "ในช่วง test (ค่ากลางของทุกโลก) ถ้าไม้บรรทัดยังใช้ได้ต้องใกล้ 1"),
        "ladder_pnl": ("กำไรเฉลี่ยต่อเหตุการณ์เป็นหน่วย σ̂ ก่อนต้นทุน: avg_pnl = ได้ราคาปิดของแท่งที่แตะ (lag 1) · "
                       "avg_pnl_lag2 = ได้ราคาช้าไปหนึ่งแท่งทั้งขาเข้าและขาออก · เทียบสเกลต้นทุน: ครบรอบ 2c(1+β) "
                       "ต่อสเปรด 1 หน่วย = 20 bps เมื่อ c = 5 bps, β = 1 ≈ 0.07σ เมื่อ σ = 3%"),
        "carry": (f"7b cash-and-carry: เลขคณิตบนค่าสมมติ (spot {ca['spot_baht']} · future {ca['quoted_future_baht']} · "
                  f"{ca['days_to_expiry']} วัน · ต้นทุนเงิน {ca['financing_rate_pct_per_year']}% ต่อปี ดอกเบี้ยอย่างง่าย · "
                  f"{ca['cost_per_leg_bps']} bps ต่อขา × {ca['legs']} ขา · หลักประกัน {ca['futures_margin_pct']}% · "
                  "spot ไม่มีปันผล) หน่วยบาทต่อ spot 100 บาท · ไม่ใช่ราคาตลาด"),
        "net_basis": (f"ผลสุทธิทุกตัวใน 7b หักต้นทุนเงิน {ca['financing_rate_pct_per_year']}% ต่อปีของเงินในขา spot แล้ว "
                      "(กู้มาซื้อ หรือเสียโอกาสฝาก) = ส่วนที่ได้ \"เกินการฝากเงิน\" — ทั้ง cash-and-carry และ funding ใช้ฐานเดียวกัน"),
        "funding": (f"7b funding: จำลอง {fs['worlds']:,} โลก โลกละ "
                    f"{fs['periods']:,} งวด (8 ชม. × 365 วัน) · ช่วงปกติเฉลี่ย "
                    f"{fa['mean_normal_bps_per_8h']} bps ช่วงติดลบเฉลี่ย {V.num(fa['mean_negative_bps_per_8h'])} bps ต่องวด "
                    f"(เกิดเฉลี่ยทุก {fa['enter_negative_every_days']} วัน ยาวเฉลี่ย {fa['negative_spell_days']} วัน) · "
                    f"φ {fa['persistence']} · shock {fa['shock_bps']} bps · "
                    f"ต้นทุน {fa['cost_per_leg_bps']} bps × {fa['legs']} ขา · ต้นทุนเงิน {fa['financing_rate_pct_per_year']}% ต่อปี · "
                    "สมมติว่าส่วนต่าง perp–spot ตอนเข้ากับตอนออกเท่ากัน · ไม่คิดหลักประกันของ perp"),
        "funding_unit": ("ตัวเลข funding เป็น bps หรือ % ของมูลค่าหนึ่งขา · ต่อเงินรวมสองขา (gross) ให้หารสอง · "
                         "headline/longrun/net_expected เป็นเลขคณิตบนค่าสมมติ ตัวอื่นมาจากการจำลอง"),
        "identity": ("P&L = convergence + carry − costs ของสองตัวอย่าง ถือ 90 วัน บาทต่อเงิน 100 บาทในขา spot · "
                     "carry = รายได้ระหว่างถือ − ต้นทุนเงิน · ค่ากลางของ funding เป็นค่าคาดหมายของแบบจำลอง "
                     "ช่วง 5–95% มาจากการจำลอง"),
        "rows": "7c ตารางเจ็ดแถวของสไลด์ 8: เฉพาะข้อเท็จจริงเชิงโครงสร้าง (ไม่มีตัวเลขจากการจำลอง)",
    }


def figures(res=None):
    res = res or run()
    fg = {
        "ladder": _fig_ladder(res["ladder"]),
        "carry_example": _fig_carry(res["carry"]),
        "funding_example": _fig_funding(res["funding"]),
        "identity": _fig_identity(res["identity"]),
        "rows": _fig_rows(),
        "classes": {cid: label for cid, label in CLASSES},
    }
    return {"about": _about(fg), **fg}


# ═══════════════════════════════ charts ═══════════════════════════════
def _n(v, d=1):
    return V.num(v, d)


def _chart_types(la, fg):
    panels = []
    for i, k in enumerate(TYPES):
        panels.append({
            "y": la[k]["demo_z"], "color": TYPE_COLOR[k], "zero": True,
            "title": TYPE_TH[k],
            "sub": f"ขนาดของ z ในช่วงวัดผล = {_n(fg[k]['z_rms_test'])} เท่าของช่วงวัดไม้บรรทัด (ค่ากลางทุกโลก)",
            "hlines": [(ENTRY_Z, "z = +2" if i == 0 else ""), (-ENTRY_Z, "z = −2" if i == 0 else "")],
        })
    return V.stacked_panels(
        "sas-p7-leash-types", panels,
        "สี่กรอบเรียงกัน แสดง z ของ ε สี่แบบบนสเกลเดียวกัน: สามแบบแรกแกว่งรอบศูนย์ แบบสถิติล้วนเดินออกนอกแถบหลังพ้นช่วงวัดไม้บรรทัด",
        "ข้อมูลจำลอง · แบบละหนึ่งโลกที่ “กลาง ๆ” (ค่า |z| สูงสุดในช่วงวัดผลใกล้ค่ากลางของทุกโลก) · ทุกกรอบใช้แกน z เดียวกัน "
        "และวัดด้วยไม้บรรทัดจาก 500 แท่งแรกของตัวเอง — ใน 500 แท่งแรก z ของทุกแบบมีค่าเฉลี่ย 0 และ sd 1 พอดี "
        "(เพราะไม้บรรทัดวัดจากช่วงนี้เอง) แต่พอพ้นช่วงนั้น z ของแบบสถิติล้วนใหญ่ขึ้นเป็น "
        f"{_n(fg['statistical']['z_rms_test'])} เท่า (กลไก {_n(fg['mechanical']['z_rms_test'])} · "
        f"สัญญา {_n(fg['contractual']['z_rms_test'])} · เศรษฐกิจ {_n(fg['economic']['z_rms_test'])}) — "
        "ไม้บรรทัดเดิมใช้ไม่ได้แล้ว",
        xlabel="แท่งที่ (วัน)", share_y=True, panel_h=104,
        xbands=[(0, N_TRAIN, "ช่วงวัดไม้บรรทัด (500 แท่งแรก)"),
                (N_TRAIN, N_TRAIN + N_TEST, "ช่วงวัดผล (500 แท่งถัดไป)", V.AMBER)])


def _chart_ladder(la, fg):
    x = np.arange(FOLLOW + 1)
    series = [{"name": f"{TYPE_SHORT[k]} {fg[k]['p30_pct']}%", "y": la[k]["curve"] * 100,
               "color": TYPE_COLOR[k], "dash": "7 4" if k == "statistical" else None} for k in TYPES]
    c, m, e, s = (fg[k] for k in TYPES)
    return V.line_chart(
        "sas-p7-leash-ladder", x, series,
        "กราฟเส้นสี่เส้น: สัดส่วนของเหตุการณ์ที่ z กลับถึง 0.5 แล้ว ตามจำนวนแท่งหลังแตะ 2 — กลไกขึ้นเร็วที่สุด "
        "สัญญาถึง 100% ที่วันหมดอายุ เศรษฐกิจค้างต่ำกว่า 100% สถิติล้วนต่ำที่สุด",
        f"ข้อมูลจำลอง · เลขในคำอธิบายเส้น = % ที่กลับภายใน 30 แท่ง · แบบกลไกกลับเร็วที่สุด (ค่ากลาง {m['median_return_bars']} แท่ง) "
        f"· แบบสัญญาช้ากว่าแต่ “ครบ 100% ไม่เกินวันหมดอายุ” · ที่ 250 แท่ง แบบเศรษฐกิจยังไม่กลับ {e['never250_pct']}% "
        f"· แบบสถิติล้วนยังไม่กลับ {s['never250_pct']}% — ชั้นของสายจูงบอก “ความแน่นอนว่าจะกลับ” ไม่ใช่ความเร็ว "
        f"(จำนวนเหตุการณ์ตามลำดับเส้น: {c['events']:,} / {m['events']:,} / {e['events']:,} / {s['events']:,})",
        xlabel="จำนวนแท่งหลังจาก |z| แตะ 2", ylabel="% ของเหตุการณ์ที่กลับถึง z = 0.5 แล้ว",
        ylim=(0, 100), xticks=[0, 30, 63, 125, 250], markers=False,
        vlines=[(WINDOW, "30 แท่ง"), (LIFE, "อายุสัญญา 63 แท่ง")])


def _chart_excursion(la, fg):
    rows = [{"label": TYPE_SHORT[k], "mid": la[k]["worst_median"], "lo": la[k]["worst_p05"],
             "hi": la[k]["worst_p95"], "color": TYPE_COLOR[k]} for k in TYPES]
    return V.dot_interval(
        "sas-p7-leash-excursion", rows,
        "จุดและช่วงของระยะที่ z หลุดไกลสุดระหว่างรอกลับ ของ ε สี่แบบ: สามแบบแรกจบไม่ไกลจากจุดเข้า แบบสถิติล้วนลากยาวไปไกลมาก",
        "ข้อมูลจำลอง · หลังเข้าที่ z = 2 แล้ว ระหว่างรอ z “หลุดต่อไปได้ไกลแค่ไหน” (ไม้บรรทัดจากช่วง train · ช่วง = การกระจาย"
        "ของแต่ละเหตุการณ์) · เปอร์เซ็นไทล์ที่ 95: "
        f"สัญญา {_n(fg['contractual']['worst_p95_sigma'])} · กลไก {_n(fg['mechanical']['worst_p95_sigma'])} · "
        f"เศรษฐกิจ {_n(fg['economic']['worst_p95_sigma'])} · สถิติล้วน {_n(fg['statistical']['worst_p95_sigma'], 0)} — "
        "ยิ่งสายจูงอ่อน หางยิ่งยาว และหางนี้เองที่กินกำไรของไม้ที่กลับ",
        zero=False, xlabel="z ที่หลุดไกลสุดระหว่างรอ (ฝั่งที่แตะเป็นบวก)",
        fmt=lambda v: _n(v, 1 if abs(v) < 10 else 0), vlines=[(ENTRY_Z, "จุดเข้า z = 2")])


def _bars_with_ranges(cid, groups, series, ranges, range_name, alt, cap, ylabel, fmt, w=760, h=340):
    """แท่งเป็นกลุ่มแบบเดียวกับ V.grouped_bars แต่มี "ขีดช่วง" ให้แท่งที่ไม่ได้ล็อก
    ranges = [(ลำดับชุด, ลำดับกลุ่ม, ต่ำ, สูง)] — V.grouped_bars ยังวาดขีดช่วงไม่ได้ จึงประกอบเองด้วย Fig/Panel
    (จัดหน้าตามตรรกะเดียวกับ V.grouped_bars ทุกอย่าง)"""
    cols = [x["color"] for x in series]
    items = [(x["name"], cols[k], "rect") for k, x in enumerate(series)] + [(range_name, V.INK, "line")]
    L, R = 58, 18
    rows = V._flow(items, w - L - R - 8)
    T = 14 + 17 * max(V._head_rows(w - L - R, V.text_w(ylabel, 11), rows), 1)
    B = 30 + V.LINE_H * (max(len(V._lines(g)) for g in groups) - 1)
    fig = V.Fig(cid, w, h)
    allv = [v for x in series for v in x["values"]] + [v for r in ranges for v in r[2:]]
    p = fig.panel((0.0, float(len(groups))), V.auto_lim(allv, include=[0.0], pad=0.12),
                  x=L, y=T, w=w - L - R, h=h - T - B)
    p.grid().yaxis(title=ylabel)
    p.legend(items)
    gw = p.w / len(groups)
    bw = min(46.0, (gw * 0.78 - 3 * (len(series) - 1)) / len(series))
    cx = lambda k, g: g + 0.5 + (k - (len(series) - 1) / 2) * (bw + 3) / gw   # noqa: E731
    cap_w = 7.0 * len(groups) / p.w                       # ขีดหัวท้ายกว้าง 7 px ต่อข้าง (หน่วยข้อมูล)
    for k, g, lo, hi in ranges:                           # วาดก่อนแท่ง: ป้ายตัวเลขที่มีขอบขาวจะอยู่ด้านบน
        x = cx(k, g)
        p.line([x, x], [lo, hi], color=V.INK, width=1.5)
        for v in (lo, hi):
            p.line([x - cap_w, x + cap_w], [v, v], color=V.INK, width=1.5)
    for k, x in enumerate(series):
        p.bars([cx(k, g) for g in range(len(groups))], [float(v) for v in x["values"]], cols[k],
               width=bw, fmt=fmt, labels=True)
    p.hline(0.0, color="#94a3b8", dash=None)
    p.xaxis(ticks=[g + 0.5 for g in range(len(groups))], labels=list(groups), line=False)
    return fig.svg(alt, cap)


def _chart_identity(fg):
    cc, fu = fg["cash_carry"], fg["funding"]
    groups = ["convergence\n(ε วิ่งกลับ)", "carry\n(รายได้ − ต้นทุนเงิน)", "ต้นทุน\nซื้อขาย 4 ขา", "สุทธิ"]
    series = [
        {"name": "Cash-and-carry (driver: Mispricing) · ล็อกแล้ว", "color": V.GREEN,
         "values": [cc["convergence_baht"], cc["carry_baht"], -cc["costs_baht"], cc["net_baht"]]},
        {"name": "Funding (driver: Interest Rate) · ค่าคาดหมาย ไม่ได้ล็อก", "color": V.BLUE,
         "values": [fu["convergence_baht"], fu["carry_baht"], -fu["costs_baht"], fu["net_baht"]]},
    ]
    ranges = [(1, 1, fu["carry_p05_baht"], fu["carry_p95_baht"]), (1, 3, fu["net_p05_baht"], fu["net_p95_baht"])]
    return _bars_with_ranges(
        "sas-p7-pnl-identity", groups, series, ranges, f"ช่วง 5–95% ของ funding ({FUND['worlds']:,} โลก)",
        "แท่งเทียบสองกลยุทธ์บนฐานเดียวกัน: cash-and-carry ได้เงินจาก convergence ทั้งหมด ส่วน funding ได้จาก carry ทั้งหมด "
        "ทั้งคู่เสียค่าซื้อขายเท่ากันและหักต้นทุนเงินเท่ากัน ขีดช่วงของ funding กว้างจากติดลบถึงบวก",
        f"ตัวเลขสมมติ ถือ 90 วัน บาทต่อเงิน 100 บาทในขา spot · ทั้งสองฝั่งหักต้นทุนเงิน 4% ต่อปี "
        f"({_n(cc['financing_baht'], 2)} บาท) · cash-and-carry: ดอกเบี้ยที่แฝงใน basis {_n(cc['basis_interest_baht'], 2)} "
        f"จ่ายต้นทุนเงินพอดี carry จึงเป็น 0 กำไรทั้งหมดมาจาก ε วิ่งกลับ {_n(cc['convergence_baht'], 2)} (ล็อกไว้ตั้งแต่วันเข้า) · "
        f"funding: ได้ funding คาดหมาย {_n(fu['funding_baht'], 2)} หักต้นทุนเงินเหลือ carry {_n(fu['carry_baht'], 2)} "
        f"และไม่ได้ล็อก — ขีดดำคือช่วง 5–95% จากการจำลอง: ผลสุทธิ {_n(fu['net_p05_baht'])} ถึง "
        f"{_n(fu['net_p95_baht'])} บาท (แพ้การฝากเงินใน {fu['loss_pct']}% ของโลก)",
        "บาท ต่อเงิน 100 บาทในขา spot (ถือ 90 วัน)", lambda v: V.num(v, 2, sign=True))


def _spells(flag):
    """ช่วงที่ flag เป็นจริงติดกัน → [(เริ่ม, จบ)] เป็นดัชนี"""
    edge = np.diff(np.concatenate([[0], flag.astype(int), [0]]))
    return list(zip(np.flatnonzero(edge == 1), np.flatnonzero(edge == -1)))


def _chart_funding_path(fu, fg):
    per_day = FUND["per_day"]
    days = (np.arange(fu["periods"]) + 1) / per_day
    bands = [(a / per_day, b / per_day, "ช่วงโหมดติดลบ" if i == 0 else "", V.RED)
             for i, (a, b) in enumerate(_spells(fu["demo_regime"]))]
    panels = [
        {"y": fu["demo_rates"], "title": "อัตรา funding ต่องวด 8 ชม. (bps)", "color": V.BLUE, "zero": True,
         "sub": f"ติดลบ {fg['negative_periods_pct']}% ของงวด (เฉลี่ยทุกโลก)"},
        {"y": [fu["demo_before_fin"] / 100.0, fu["demo_net"] / 100.0],
         "names": ["หักค่าซื้อขาย", "หักค่าซื้อขาย + ต้นทุนเงิน 4%"],
         "title": "ผลสะสม (% ของมูลค่าหนึ่งขา)", "color": [V.MUTED, V.GREEN], "zero": True},
    ]
    return V.stacked_panels(
        "sas-p7-funding-path", panels,
        "สองกรอบ: บนคืออัตรา funding ราย 8 ชั่วโมงที่ส่วนใหญ่เป็นบวกแต่มีช่วงติดลบ ล่างคือผลสะสมหลังหักค่าซื้อขาย "
        "และหลังหักต้นทุนเงินด้วย ซึ่งไต่ขึ้นช้ากว่าและถอยลงในช่วงติดลบ",
        f"ข้อมูลจำลอง · หนึ่งโลกที่ funding ทั้งปีใกล้ค่ากลาง · ทั้งสองเส้นเริ่มที่ −{_n(fg['costs_bps'] / 100.0, 2)}% "
        f"(ค่าเข้า+ออก {fg['costs_bps']} bps) · เส้นเขียวหักต้นทุนเงิน 4% ต่อปีด้วย จึงไต่ช้ากว่า — "
        f"ต้องถือค่ากลาง {_n(fg['breakeven_days_median'], 0)} วันกว่าจะไม่แพ้การฝากเงิน "
        f"(ถ้าไม่คิดต้นทุนเงิน {_n(fg['breakeven_costs_only_days_median'], 0)} วัน) และถอยลงทุกครั้งที่ funding ติดลบ · "
        f"30 วันที่แย่ที่สุดของปี ค่ากลาง {_n(fg['worst30_median_bps'], 0)} bps",
        x=days, xlabel="วันที่ถือ", panel_h=128, xbands=bands)


def _chart_funding_horizon(fu, fg):
    rows = []
    for d in FUND["horizons"]:
        net = fu["horizons"][d]["net"] / 100.0
        rows.append({"label": f"ถือ {d} วัน\nแพ้การฝากเงินใน {fg[f'hold{d}']['loss_pct']}% ของโลก",
                     "mid": float(np.median(net)), "lo": _p(net, 5), "hi": _p(net, 95)})
    return V.dot_interval(
        "sas-p7-funding-horizon", rows,
        "ผลสุทธิของการถือ spot กับ short perp หลังหักค่าซื้อขายและต้นทุนเงิน ตามระยะถือ 7 30 90 และ 365 วัน: "
        "ถือสั้นยังติดลบ ถือนานขึ้นค่ากลางเป็นบวกแต่ช่วงกว้างขึ้นและยังติดลบได้",
        f"ข้อมูลจำลอง {FUND['worlds']:,} โลก · ผลสุทธิหลังหักค่าซื้อขาย {fg['costs_bps']} bps และต้นทุนเงิน 4% ต่อปี "
        f"(ยังไม่ปรับเป็นต่อปี) = ส่วนที่ได้เกินการฝากเงิน · ถือ 7 วันค่ากลางยังไม่คุ้ม · ทั้งปี funding เฉลี่ย "
        f"{_n(fg['carry_mean_pct_per_year'])}% (ตัวเลขโฆษณาที่คิดจากช่วงปกติอย่างเดียว "
        f"{_n(fg['headline_carry_pct_per_year'], 2)}%) เหลือเกินการฝากเงินเฉลี่ย {_n(fg['net_mean_pct_per_year'])}% "
        f"และยังแพ้การฝากเงินใน {fg['hold365']['loss_pct']}% ของโลก "
        f"(ขาดทุนเป็นเงินจริง {fg['hold365']['loss_before_financing_pct']}%)",
        zero=True, xlabel="ผลสุทธิเกินการฝากเงิน (% ของมูลค่าหนึ่งขา)",
        fmt=lambda v: V.num(v, 1, sign=True) + "%")


def _chart_rows():
    ids = [cid for cid, _ in CLASSES]
    labels, values = [], []
    for i, (rid, y, x, strategy, driver, paid_by, leash, also) in enumerate(ROWS, 1):
        labels.append(f"{i}. {y} – {x}\n{strategy}")
        values.append([1.0 if c == leash else 0.45 if c in also else None for c in ids])
    cols = [f"{name}\n({CLASS_WHY[cid]})" for cid, name in CLASSES]
    return V.heat_table(
        "sas-p7-rows-ladder", labels, cols, values,
        "ตารางเจ็ดแถวของสไลด์ 8 วางบนชั้นของสายจูงห้าแบบ: cash-and-carry อยู่ชั้นสัญญา funding และ swap อยู่ชั้นกลไก "
        "pairs และ volatility อยู่ชั้นเศรษฐกิจ ตะกร้าหลายตัวอยู่ชั้นสถิติล้วน latency อยู่ชั้นความเร็ว",
        "เจ็ดแถวของสไลด์ 8 จัดตามชั้นของสายจูง · ช่องเข้ม = ชั้นหลัก · ช่องจาง = เป็นชั้นนี้ได้ ขึ้นกับว่า ε ถูกสร้างอย่างไร "
        "(เช่น หุ้นคู่ที่ได้จากการสแกนล้วน ๆ ตกไปอยู่ชั้นสถิติล้วน) · ชั้นเรียงจากสายจูงที่แน่นที่สุด (สัญญา) "
        "ไปหาที่ไม่มีอะไรรับประกัน (สถิติล้วน) · ชั้นความเร็วแยกไว้ท้ายสุดเพราะสิ่งที่ต้องชนะคือเวลา ไม่ใช่การรอ",
        fmt=lambda v: "หลัก" if v >= 1 else "เป็นได้", row_title="แถวในสไลด์ 8", col_title="ชั้นของสายจูง",
        lo=0.0, hi=1.6, legend=False, cell_h=40)


def charts(res=None):
    res = res or run()
    fg = figures(res)
    return {
        "sas-p7-leash-types": _chart_types(res["ladder"], fg["ladder"]),
        "sas-p7-leash-ladder": _chart_ladder(res["ladder"], fg["ladder"]),
        "sas-p7-leash-excursion": _chart_excursion(res["ladder"], fg["ladder"]),
        "sas-p7-pnl-identity": _chart_identity(fg["identity"]),
        "sas-p7-funding-path": _chart_funding_path(res["funding"], fg["funding_example"]),
        "sas-p7-funding-horizon": _chart_funding_horizon(res["funding"], fg["funding_example"]),
        "sas-p7-rows-ladder": _chart_rows(),
    }


# ═══════════════════════════════ สรุปเมื่อรันตรง ๆ ═══════════════════════════════
def _print_ladder(la):
    st = la["settings"]
    print("7a  บันไดสายจูง: ε สี่แบบ กติกาเดียวกัน")
    print(f"    ไม้บรรทัดจาก {st['train_bars']} แท่งแรก · แตะ |z| ≥ {st['entry_z']} ใน {st['test_bars']} แท่งถัดไป · "
          f"กลับ = z ถึง {st['exit_z']} · ตามดูนานสุด {st['follow_bars']} แท่ง")
    print(f"    สัญญา/กลไก/เศรษฐกิจ แบบละ {st['worlds']:,} โลก · สถิติล้วน: สแกน {st['candidates']:,} คู่ "
          f"ผ่าน EG 5% (เส้นตัด {st['eg_crit5']}) {st['selected']:,} คู่ = {st['pass_rate_pct']}%")
    print()
    print(f"    {'':12s}{'events':>8s}{'back<=30':>10s}{'(5-95%)':>12s}{'median':>8s}{'never250':>10s}"
          f"{'worst p95':>11s}{'avg pnl':>9s}{'lag 2':>7s}{'z_rms':>7s}")
    for k in TYPES:
        f = la[k]
        rng = f"({f['p30_lo_pct']}-{f['p30_hi_pct']})"
        print(f"    {k:12s}{f['events']:>8,d}{f['p30_pct']:>9}%{rng:>12s}{f['median_return_bars']:>8}"
              f"{f['never250_pct']:>9}%{f['worst_p95_sigma']:>11}{f['avg_pnl_sigma']:>9.1f}"
              f"{f['avg_pnl_lag2_sigma']:>7.1f}{f['z_rms_test']:>7.1f}")
    print("    (back<=30 = % ที่กลับภายใน 30 แท่ง · median = จำนวนแท่งจนกลับ ค่ากลาง · never250 = % ที่ไม่กลับใน 250 แท่ง")
    print("     worst p95 = เปอร์เซ็นไทล์ที่ 95 ของ z ที่หลุดไกลสุด · avg pnl = กำไรเฉลี่ยต่อเหตุการณ์ก่อนต้นทุน หน่วย σ̂")
    print("     lag 2 = กำไรเฉลี่ยถ้าได้ราคาช้าไปหนึ่งแท่งทั้งขาเข้าและออก · z_rms = ขนาดของ z ในช่วงวัดผล เทียบกับไม้บรรทัด (ควรใกล้ 1))")
    c, e, s = la["contractual"], la["economic"], la["statistical"]
    print(f"    สัญญา: ตอนแตะเหลือ ≤ 30 แท่งก่อนหมดอายุ → กลับใน 30 แท่ง {c['near_expiry_p30_pct']}% "
          f"({c['near_expiry_events']:,} เหตุการณ์) · เหลือมากกว่านั้น {c['far_expiry_p30_pct']}% "
          f"({c['far_expiry_events']:,}) · กลับครบ {c['back63_pct']}% ภายใน 63 แท่ง · "
          f"จบพอดีวันหมดอายุ {c['ended_at_expiry_pct']}%")
    print(f"    เศรษฐกิจ: เหตุการณ์ที่มีค่าเฉลี่ยกระโดดระหว่างทาง {e['events_with_jump_pct']}% → กลับใน 30 แท่ง "
          f"{e['p30_with_jump_pct']}% · ไม่มีกระโดด {e['p30_no_jump_pct']}%")
    print(f"    สถิติล้วน: กำไรเฉลี่ยต่อเหตุการณ์ {s['avg_pnl_sigma']} σ̂ (ช่วง {s['avg_pnl_lo_sigma']} ถึง "
          f"{s['avg_pnl_hi_sigma']}) ทั้งที่ {s['back250_pct']}% ของเหตุการณ์กลับได้ใน 250 แท่ง")
    print("    ถ้าให้สามแบบแรกผ่านการคัดแบบเดียวกับสถิติล้วน (ประมาณ β̂ + EG 5% บน 500 แท่งแรก):")
    for k, v in la["same_filter"].items():
        print(f"      {k:12s} ผ่าน EG {v['eg_pass_pct']}% ของโลก → กลับใน 30 แท่ง {v['p30_pct']}% · "
              f"ไม่กลับ {v['never250_pct']}% · ค่ากลาง {v['median_return_bars']} แท่ง · worst p95 {v['worst_p95_sigma']} · "
              f"กำไร {v['avg_pnl_sigma']} σ̂")
    print("    ลองเปลี่ยนปุ่ม (กลับใน 30 แท่ง / ไม่กลับใน 250 แท่ง / เวลากลับค่ากลาง):")
    for group, title in (("contract", "อายุสัญญา"), ("economic", "ค่าเฉลี่ยกระโดด")):
        cells = [f"{key} {v['p30_pct']}% / {v['never250_pct']}% / {v['median_return_bars']} แท่ง"
                 for key, v in la["sensitivity"][group].items()]
        print(f"      {title}: " + " · ".join(cells))


def _print_money(ca, fu, idn):
    a = ca["assumptions"]
    print("7b  cash-and-carry (ตัวเลขสมมติ · บาทต่อ spot 100 บาท · สุทธิ = หลังหักต้นทุนเงิน 4% แล้ว)")
    print(f"    spot {a['spot_baht']} · future ที่เสนอ {a['quoted_future_baht']} · {a['days_to_expiry']} วัน · "
          f"ต้นทุนเงิน {a['financing_rate_pct_per_year']}% ต่อปี · {a['cost_per_leg_bps']} bps × {a['legs']} ขา")
    print(f"    ราคายุติธรรม {ca['fair_future_baht']} → future แพงเกิน (ε) {ca['mispricing_baht']} บาท "
          f"= {ca['mispricing_bps']} bps")
    print(f"    ล็อกส่วนต่าง {ca['basis_baht']} − ต้นทุนเงิน {ca['financing_baht']} − ค่าซื้อขาย {ca['costs_baht']} "
          f"= กำไรสุทธิ {ca['locked_net_baht']} บาท ({ca['locked_net_pct_per_year']}% ต่อปี เกินการฝากเงิน)")
    wm = ca["with_margin"]
    print(f"    ถ้าวางหลักประกัน {a['futures_margin_pct']}%: ทุน {wm['capital_baht']} · กำไร {wm['net_baht']} "
          f"= {wm['net_on_capital_pct_per_year']}% ต่อปีของทุน (เกินการฝากเงิน)")
    print(f"    จุดคุ้มทุน: future ต้องสูงกว่า {ca['breakeven_future_baht']} (ε > {ca['breakeven_mispricing_bps']} bps) · "
          f"รวมต้นทุนเงินของหลักประกัน {wm['breakeven_future_baht']} (ε > {wm['breakeven_mispricing_bps']} bps)")
    print()
    fa = fu["assumptions"]
    print(f"7b  funding (ข้อมูลจำลอง {fu['settings']['worlds']:,} โลก × {fu['settings']['periods']:,} งวด · % ของมูลค่าหนึ่งขา)")
    print(f"    ช่วงปกติ {fa['mean_normal_bps_per_8h']} bps/8ชม. · ช่วงติดลบ {fa['mean_negative_bps_per_8h']} bps "
          f"(เกิดเฉลี่ยทุก {fa['enter_negative_every_days']} วัน ยาว {fa['negative_spell_days']} วัน) · "
          f"φ {fa['persistence']} · shock {fa['shock_bps']} bps · ต้นทุนเงิน {fa['financing_rate_pct_per_year']}% ต่อปี")
    print(f"    funding ต่อปี: โฆษณา {fu['headline_carry_pct_per_year']}% · ค่าคาดหมาย {fu['longrun_carry_pct_per_year']}% · "
          f"จำลอง เฉลี่ย {fu['carry_mean_pct_per_year']}% (5–95%: {fu['carry_p05_pct_per_year']} ถึง "
          f"{fu['carry_p95_pct_per_year']})")
    print(f"    หลังหักค่าซื้อขายและต้นทุนเงิน (เกินการฝากเงิน): คาดหมาย {fu['net_expected_pct_per_year']}% · จำลอง เฉลี่ย "
          f"{fu['net_mean_pct_per_year']}% (5–95%: {fu['net_p05_pct_per_year']} ถึง {fu['net_p95_pct_per_year']})")
    print(f"    งวดที่ติดลบ {fu['negative_periods_pct']}% · 30 วันที่แย่ที่สุด ค่ากลาง {fu['worst30_median_bps']} bps "
          f"(5–95%: {fu['worst30_p05_bps']} ถึง {fu['worst30_p95_bps']})")
    print(f"    ไม่แพ้การฝากเงินครั้งแรก: ค่ากลาง {fu['breakeven_days_median']} วัน (5–95%: {fu['breakeven_days_p05']} ถึง "
          f"{fu['breakeven_days_p95']} · ไม่ถึงเลยในหนึ่งปี {fu['never_breakeven_pct']}%) · ถ้าไม่คิดต้นทุนเงิน "
          f"{fu['breakeven_costs_only_days_median']} วัน")
    for d in FUND["horizons"]:
        h = fu[f"hold{d}"]
        print(f"      ถือ {d:>3d} วัน: เกินการฝากเงิน ค่ากลาง {h['net_median_bps']:>5} bps (5–95%: {h['net_p05_bps']} ถึง "
              f"{h['net_p95_bps']}) · แพ้การฝากเงิน {h['loss_pct']}% ของโลก · ขาดทุนเป็นเงิน {h['loss_before_financing_pct']}%")
    print()
    print("7b  P&L = convergence + carry − costs (ถือ 90 วัน · บาทต่อเงิน 100 บาทในขา spot · carry หลังหักต้นทุนเงิน)")
    for k, name in (("cash_carry", "cash-and-carry"), ("funding", "funding")):
        d = idn[k]
        print(f"    {name:15s} {d['convergence_baht']:>5.2f} + {d['carry_baht']:>5.2f} − {d['costs_baht']:.2f} "
              f"= {d['net_baht']:.2f}")
    cc, f = idn["cash_carry"], idn["funding"]
    print(f"    (carry ของ cash-and-carry = ดอกเบี้ยใน basis {cc['basis_interest_baht']} − ต้นทุนเงิน {cc['financing_baht']} · "
          f"ของ funding = funding คาดหมาย {f['funding_baht']} − {f['financing_baht']}; จำลองได้เฉลี่ย {f['funding_mc_mean_baht']})")
    print(f"    funding ไม่ได้ล็อก: ผลสุทธิ 5–95% = {f['net_p05_baht']} ถึง {f['net_p95_baht']} บาท · "
          f"แพ้การฝากเงิน {f['loss_pct']}% ของโลก")


def main():
    fg = figures()
    line = "─" * 96
    print("ห้องทดลองตอนที่ 7 — ตารางเจ็ดแถว = สายจูงเจ็ดแบบ  (ข้อมูลจำลอง · ตัวอย่างเงินเป็นตัวเลขสมมติ)")
    print(line)
    _print_ladder(fg["ladder"])
    print(line)
    _print_money(fg["carry_example"], fg["funding_example"], fg["identity"])
    print(line)
    print("7c  เจ็ดแถวของสไลด์ 8 กับชั้นของสายจูง")
    for i, r in enumerate(fg["rows"].values(), 1):
        also = f" (เป็นได้: {r['leash_also']})" if r["leash_also"] else ""
        print(f"    {i}. {r['label']:29s} {r['strategy']:27s} ได้เงินจาก {r['paid_by']:12s} "
              f"สายจูง: {r['leash']}{also}")
    print(line)
    print("กราฟ: " + " · ".join(charts()))


if __name__ == "__main__":
    main()
