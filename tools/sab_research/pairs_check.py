#!/usr/bin/env python3
"""Empirical check for the practitioner memo: which formation-period pair filters predict validation profit?
Uses only formation + validation splits (never final_test). Book cost basis: 0.05% per fill per leg (sab2_engine.FEE).
Run:  python3 pairs_check.py  (from anywhere; adds repo tools/ to sys.path)
"""
import itertools
import json
import math
import sys

sys.path.insert(0, "/home/user/Claude-code-project/tools")
from sab2_realdata import load_closes  # noqa: E402
import sab2_stats as S  # noqa: E402
import sab2_engine as E  # noqa: E402

fd, F = load_closes("formation")
vd, V = load_closes("validation")
coins = list(F.keys())
RT = 4 * E.FEE  # round trip, as a fraction of ONE leg's notional, when both legs have equal notional: 2 legs x 2 fills


def crossings(x):
    m = S.mean(x)
    s = [1 if v > m else -1 for v in x]
    return sum(1 for a, b in zip(s, s[1:]) if a != b)


def hurst(x, lags=range(2, 61)):
    # simple "std of lagged differences" estimator: sd(x[t+L]-x[t]) ~ L^H  (log-log slope)
    lx, ly = [], []
    for L in lags:
        d = [x[i + L] - x[i] for i in range(len(x) - L)]
        lx.append(math.log(L))
        ly.append(math.log(S.sd(d)))
    return S.ols(lx, ly)["slope"]


def spearman(a, b):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for k, i in enumerate(o):
            r[i] = k
        return r
    return S.corr(rank(a), rank(b))


def ggr_rule(z, held):
    # Gatev et al.: open when normalised-price gap >= 2 formation SD, close when the gap crosses zero
    if held == 0 and abs(z) >= 2.0:
        return -1 if z > 0 else 1
    if held != 0 and held * z >= 0:
        return 0
    return held


rows = []
for a, b in itertools.combinations(coins, 2):
    la, lb = S.logs(F[a]), S.logs(F[b])
    ra, rb = S.diff(la), S.diff(lb)
    eg1, eg2 = S.engle_granger(la, lb), S.engle_granger(lb, la)
    if eg2["stat"] < eg1["stat"]:  # keep the direction with the stronger statistic (note: an extra test)
        A, B, eg, lA, lB = b, a, eg2, lb, la
    else:
        A, B, eg, lA, lB = a, b, eg1, la, lb
    h = eg["h"]
    X = [p - h * q for p, q in zip(lA, lB)]
    mX, sX = S.mean(X), S.sd(X)
    ar = S.ar1(X)
    n = len(X)
    hA = S.ols(lB[: n // 2], lA[: n // 2])["slope"]
    hB = S.ols(lB[n // 2:], lA[n // 2:])["slope"]
    # distance (GGR) metric: normalised price indices from formation start
    na = [p / F[A][0] for p in F[A]]
    nb = [p / F[B][0] for p in F[B]]
    gap = [p - q for p, q in zip(na, nb)]
    ssd = math.fsum(g * g for g in gap)
    sgap = S.sd(gap)  # GGR use the formation SD of the gap as the trigger unit

    # ---------- validation ----------
    vA, vB = V[A], V[B]
    A0, B0 = F[A][-1], F[B][-1]
    # Z rule (book defaults): log spread, fixed formation ruler; fixed units set at formation end so A leg = $500
    sets = 500.0 / A0
    h_units = h * A0 / B0  # log hedge ratio -> units of B per unit of A at the formation-end prices
    zv = [(math.log(p) - h * math.log(q) - mX) / sX for p, q in zip(vA, vB)]
    rz = E.run(vA, vB, h_units, zv, sets=sets, enter=2.0, leave=0.5, hold=30)
    # same rule without the 30-day time stop
    rz_nostop = E.run(vA, vB, h_units, zv, sets=sets, enter=2.0, leave=0.5, hold=None)
    # GGR distance rule: dollar-neutral $500/$500 at validation start, normalised at validation start
    a0, b0 = vA[0], vB[0]
    zg = [((p / a0) - (q / b0)) / sgap for p, q in zip(vA, vB)]
    rg = E.run(vA, vB, a0 / b0, zg, sets=500.0 / a0, rule=ggr_rule, hold=None)
    # gross (fee 0) to separate signal from cost
    rz0 = E.run(vA, vB, h_units, zv, sets=sets, enter=2.0, leave=0.5, hold=30, fee=0.0)
    # persistence: ADF (no const, EG critical values) of the formation-h spread on validation; EG re-estimated on validation
    Xv = [math.log(p) - h * math.log(q) for p, q in zip(vA, vB)]
    adf_fixed = S.adf([x - mX for x in Xv], const=False, n_vars=2)
    egv = S.engle_granger(S.logs(vA), S.logs(vB))
    rows.append({
        "pair": f"{A}/{B}", "rho_ret": S.corr(ra, rb), "rho_lvl": S.corr(la, lb),
        "rho_ret_val": S.corr(S.diff(S.logs(vA)), S.diff(S.logs(vB))),
        "eg_stat": eg["stat"], "eg_p": eg["pvalue"], "eg_pass5": eg["reject5"], "h": h,
        "h_drift": abs(hB - hA) / abs(h) if h else float("nan"),
        "phi": ar["phi"], "half_life": S.half_life(ar["phi"]), "cross_per_yr": crossings(X) / (n / 365.0),
        "spread_sd": sX, "sd_over_rt": sX / RT, "hurst": hurst(X), "ssd": ssd,
        "z_net": rz["net"], "z_gross": rz0["net"], "z_trades": rz["trades"], "z_costs": rz["costs"],
        "z_wins": rz["wins"], "z_mdd": rz["max_drawdown"], "z_net_nostop": rz_nostop["net"],
        "z_time_exits": sum(1 for t in rz["trade_list"] if t["reason"] == "time"),
        "g_net": rg["net"], "g_trades": rg["trades"], "g_costs": rg["costs"], "g_mdd": rg["max_drawdown"],
        "val_adf_fixed_h": adf_fixed["stat"], "val_fixed_pass5": adf_fixed["reject5"],
        "val_eg_stat": egv["stat"], "val_eg_pass5": egv["reject5"],
        "z_open_end": rz["open"],
    })

json.dump(rows, open(__file__.replace(".py", "_rows.json"), "w"), indent=1)

f = lambda v, d=2: ("inf" if v == float("inf") else f"{v:.{d}f}")
print("RT cost (fraction of one-leg notional):", RT)
print("\nTABLE: all 45 pairs sorted by return correlation (formation)")
hdr = "pair      rhoRet rhoLvl  EGstat  EGp  pass hl(d) cross/yr sd/RT hurst hDrift | Znet  Zgross Ztr ZnoStop | Gnet  Gtr | vADF(fixed h) vEGpass"
print(hdr)
for r in sorted(rows, key=lambda r: -r["rho_ret"]):
    print(f"{r['pair']:9} {f(r['rho_ret'])}  {f(r['rho_lvl'])}  {f(r['eg_stat'])}  {f(r['eg_p'])} {'Y' if r['eg_pass5'] else '.'}  "
          f"{f(r['half_life'],0):>5} {f(r['cross_per_yr'],1):>6} {f(r['sd_over_rt'],0):>5} {f(r['hurst'])} {f(r['h_drift'])} | "
          f"{r['z_net']:6.1f} {r['z_gross']:6.1f} {r['z_trades']:3d} {r['z_net_nostop']:6.1f} | {r['g_net']:6.1f} {r['g_trades']:3d} | "
          f"{f(r['val_adf_fixed_h'])} {'Y' if r['val_eg_pass5'] else '.'}")

print("\nSPEARMAN rank correlation of formation metric with validation net PnL (n=45)")
metrics = [("rho_ret", +1), ("rho_lvl", +1), ("eg_stat", -1), ("half_life", -1), ("cross_per_yr", +1),
           ("sd_over_rt", +1), ("hurst", -1), ("h_drift", -1), ("ssd", -1)]
for m, sign in metrics:
    xs = [r[m] if r[m] != float("inf") else 1e9 for r in rows]
    print(f"  {m:13} vs Z-rule net {spearman(xs, [r['z_net'] for r in rows]):+.2f}   vs GGR net {spearman(xs, [r['g_net'] for r in rows]):+.2f}"
          f"   (sign that 'should' help: {'+' if sign > 0 else '-'})")

print("\nTOP-5 / BOTTOM-5 by each selection criterion: mean validation net (Z rule; GGR rule)")
for m, sign in metrics:
    key = lambda r: -sign * (r[m] if r[m] != float("inf") else 1e9)
    o = sorted(rows, key=key)
    top, bot = o[:5], o[-5:]
    mz = lambda g, k: S.mean([r[k] for r in g])
    print(f"  {m:13} top5 Z {mz(top,'z_net'):7.1f} GGR {mz(top,'g_net'):7.1f} | bottom5 Z {mz(bot,'z_net'):7.1f} GGR {mz(bot,'g_net'):7.1f}"
          f" | top5: {', '.join(r['pair'] for r in top)}")

print("\nGROUPS")
def grp(name, g):
    if not g:
        print(f"  {name}: none"); return
    print(f"  {name:45} n={len(g):2d}  Z net mean {S.mean([r['z_net'] for r in g]):7.1f}  "
          f"profitable {sum(r['z_net']>0 for r in g)}/{len(g)}  | GGR mean {S.mean([r['g_net'] for r in g]):7.1f} "
          f"profitable {sum(r['g_net']>0 for r in g)}/{len(g)} | Z gross mean {S.mean([r['z_gross'] for r in g]):7.1f}")
grp("all 45", rows)
grp("EG pass 5% (formation)", [r for r in rows if r["eg_pass5"]])
grp("EG p<0.10", [r for r in rows if r["eg_p"] < 0.10])
grp("rho_ret >= 0.80", [r for r in rows if r["rho_ret"] >= 0.80])
grp("rho_ret < 0.70", [r for r in rows if r["rho_ret"] < 0.70])
grp("rho_lvl >= 0.90", [r for r in rows if r["rho_lvl"] >= 0.90])
grp("half-life <= 30d", [r for r in rows if r["half_life"] <= 30])
grp("EG p<0.10 and HL<=30 and cross>=12/yr", [r for r in rows if r["eg_p"] < 0.10 and r["half_life"] <= 30 and r["cross_per_yr"] >= 12])
grp("hurst < 0.5", [r for r in rows if r["hurst"] < 0.5])

print("\nPERSISTENCE: formation EG pass vs validation")
fp = [r for r in rows if r["eg_pass5"]]
print(f"  formation passes: {len(fp)} -> fixed-h spread passes ADF(EG crit) on validation: {sum(r['val_fixed_pass5'] for r in fp)}"
      f"; re-estimated EG passes on validation: {sum(r['val_eg_pass5'] for r in fp)}")
print(f"  all 45: validation re-estimated EG passes: {sum(r['val_eg_pass5'] for r in rows)}; fixed-h ADF passes: {sum(r['val_fixed_pass5'] for r in rows)}")
print(f"  pairs passing on BOTH formation and validation (re-estimated): {[r['pair'] for r in rows if r['eg_pass5'] and r['val_eg_pass5']]}")
print(f"  return-corr stability: corr(formation rho_ret, validation rho_ret) = {S.corr([r['rho_ret'] for r in rows],[r['rho_ret_val'] for r in rows]):.2f}")

print("\nCOST vs GROSS (Z rule)")
print(f"  total gross {sum(r['z_gross'] for r in rows):.1f}  total costs {sum(r['z_costs'] for r in rows):.1f}  total net {sum(r['z_net'] for r in rows):.1f}"
      f"  trades {sum(r['z_trades'] for r in rows)}  time-stop exits {sum(r['z_time_exits'] for r in rows)}")
print(f"  GGR: total net {sum(r['g_net'] for r in rows):.1f} costs {sum(r['g_costs'] for r in rows):.1f} trades {sum(r['g_trades'] for r in rows)}")
print(f"  no time stop: total net {sum(r['z_net_nostop'] for r in rows):.1f}")
print(f"  pairs with zero Z trades: {sum(r['z_trades']==0 for r in rows)}")


# ======================= PART 2: practitioner-style variants =======================
print("\n\n===== PART 2 =====")
dates_all = fd + vd
P = {c: F[c] + V[c] for c in coins}
nF = len(fd)


def close_all(r_list):
    return r_list


def ggr_window(form_lo, form_hi, tr_lo, tr_hi, top=5):
    """GGR: normalised prices over [form_lo, form_hi); SSD rank; trade [tr_lo, tr_hi) normalised at tr_lo,
    open at 2 formation-SD of the gap, close at crossing; force-close at window end (we append a z=0 at the end)."""
    out = []
    for a, b in itertools.combinations(coins, 2):
        pa, pb = P[a][form_lo:form_hi], P[b][form_lo:form_hi]
        gap = [x / pa[0] - y / pb[0] for x, y in zip(pa, pb)]
        ssd = math.fsum(g * g for g in gap)
        s = S.sd(gap)
        ta, tb = P[a][tr_lo:tr_hi], P[b][tr_lo:tr_hi]
        z = [(x / ta[0] - y / tb[0]) / s for x, y in zip(ta, tb)]
        z[-2] = 0.0  # signal on the second-last day = 0 -> close filled on the last day (forced window-end exit)
        r = E.run(ta, tb, ta[0] / tb[0], z, sets=500.0 / ta[0], rule=ggr_rule, hold=None)
        out.append({"pair": f"{a}/{b}", "ssd": ssd, "net": r["net"], "trades": r["trades"], "costs": r["costs"],
                    "rho_ret": S.corr(S.diff(S.logs(pa)), S.diff(S.logs(pb)))})
    out.sort(key=lambda r: r["ssd"])
    return out


half = 183
w1 = ggr_window(nF - 365, nF, nF, nF + half)
w2 = ggr_window(nF + half - 365, nF + half, nF + half, nF + 365)
for name, w in (("GGR window 1 (form: last 365d of formation; trade val d0-182)", w1),
                ("GGR window 2 (form: 365d ending val d182; trade val d183-364)", w2)):
    print(f"\n{name}")
    print("  top-5 by SSD:", ", ".join(f"{r['pair']} net {r['net']:.1f} tr {r['trades']} rhoRet {r['rho_ret']:.2f}" for r in w[:5]))
    print(f"  top-5 mean net {S.mean([r['net'] for r in w[:5]]):.1f} | all-45 mean net {S.mean([r['net'] for r in w]):.1f}"
          f" | bottom-5-SSD mean {S.mean([r['net'] for r in w[-5:]]):.1f} | trades all {sum(r['trades'] for r in w)}")
    print(f"  spearman(SSD, net) = {spearman([r['ssd'] for r in w], [r['net'] for r in w]):+.2f};"
          f" spearman(rho_ret, net) = {spearman([r['rho_ret'] for r in w], [r['net'] for r in w]):+.2f}")
    o = sorted(w, key=lambda r: -r["rho_ret"])
    print(f"  top-5 by return corr: mean net {S.mean([r['net'] for r in o[:5]]):.1f} ({', '.join(r['pair'] for r in o[:5])})")

# Rolling-ruler Z rule (book ch.5 style): formation h, but mean/SD from the trailing 60 days known at t
print("\nROLLING-RULER Z rule (60d trailing mean/SD of the log spread, formation h, enter 2 / leave 0.5 / hold 30)")
rr = []
for r in rows:
    A, B = r["pair"].split("/")
    h = r["h"]
    Xall = [math.log(p) - h * math.log(q) for p, q in zip(P[A], P[B])]
    z = []
    for t in range(nF, nF + 365):
        w = Xall[t - 59:t + 1]
        z.append((Xall[t] - S.mean(w)) / S.sd(w))
    vA, vB = V[A], V[B]
    A0, B0 = F[A][-1], F[B][-1]
    res = E.run(vA, vB, h * A0 / B0, z, sets=500.0 / A0, enter=2.0, leave=0.5, hold=30)
    res0 = E.run(vA, vB, h * A0 / B0, z, sets=500.0 / A0, enter=2.0, leave=0.5, hold=30, fee=0.0)
    rr.append({**r, "rz_net": res["net"], "rz_gross": res0["net"], "rz_trades": res["trades"], "rz_costs": res["costs"],
               "rz_mdd": res["max_drawdown"]})
print(f"  total net {sum(x['rz_net'] for x in rr):.1f} gross {sum(x['rz_gross'] for x in rr):.1f} costs {sum(x['rz_costs'] for x in rr):.1f}"
      f" trades {sum(x['rz_trades'] for x in rr)} profitable {sum(x['rz_net']>0 for x in rr)}/45")
for m, sign in metrics:
    xs = [x[m] if x[m] != float("inf") else 1e9 for x in rr]
    print(f"  spearman({m}, rolling net) {spearman(xs, [x['rz_net'] for x in rr]):+.2f}")
def g2(name, g):
    print(f"  {name:40} n={len(g):2d} mean net {S.mean([x['rz_net'] for x in g]):7.1f} mean gross {S.mean([x['rz_gross'] for x in g]):7.1f}"
          f" mean costs {S.mean([x['rz_costs'] for x in g]):6.1f} mean trades {S.mean([x['rz_trades'] for x in g]):5.1f} profitable {sum(x['rz_net']>0 for x in g)}/{len(g)}")
g2("all", rr)
g2("EG pass 5%", [x for x in rr if x["eg_pass5"]])
g2("rho_ret top 5", sorted(rr, key=lambda x: -x["rho_ret"])[:5])
g2("rho_lvl top 5", sorted(rr, key=lambda x: -x["rho_lvl"])[:5])
g2("rho_ret bottom 5", sorted(rr, key=lambda x: x["rho_ret"])[:5])
print("  per pair (sorted by rho_ret): " + "; ".join(f"{x['pair']} {x['rz_net']:.0f}/{x['rz_trades']}" for x in sorted(rr, key=lambda x: -x['rho_ret'])))

# The "0.98 correlation" arithmetic on our data: daily volatility of the hedged log spread vs return correlation
print("\nSPREAD DAILY VOL vs RETURN CORRELATION (formation)")
for r in sorted(rows, key=lambda r: -r["rho_ret"])[:6] + sorted(rows, key=lambda r: r["rho_ret"])[:3]:
    A, B = r["pair"].split("/")
    X = [math.log(p) - r["h"] * math.log(q) for p, q in zip(F[A], F[B])]
    print(f"  {r['pair']:9} rho_ret {r['rho_ret']:.2f}  sd(daily dX) {100*S.sd(S.diff(X)):.2f}%  level SD of spread {100*r['spread_sd']:.1f}%"
          f"  1.5 SD move / RT cost = {1.5*r['spread_sd']/RT:.0f}x")
sa = sb = 0.035
for rho in (0.5, 0.8, 0.9, 0.95, 0.98, 0.99):
    print(f"  theory: two coins with 3.5%/day vol, h=1, rho={rho}: daily spread vol {100*math.sqrt(sa*sa+sb*sb-2*rho*sa*sb):.2f}%")

# LTC concentration
ltc = [r for r in rows if r["pair"].startswith("LTC/")]
print(f"\nLTC concentration: formation EG passes {sum(r['eg_pass5'] for r in rows)} of which LTC pairs {sum(r['eg_pass5'] for r in ltc)}")
xrp = [r for r in rows if 'XRP' in r['pair']]
print(f"XRP pairs (9): fixed-ruler Z net mean {S.mean([r['z_net'] for r in xrp]):.1f}; all 9 negative? {all(r['z_net']<0 for r in xrp if not r['pair'].startswith('LTC'))}")
print(f"Without XRP pairs (36): fixed Z mean net {S.mean([r['z_net'] for r in rows if 'XRP' not in r['pair']]):.1f};"
      f" EG-pass mean {S.mean([r['z_net'] for r in rows if 'XRP' not in r['pair'] and r['eg_pass5']]):.1f};"
      f" non-pass mean {S.mean([r['z_net'] for r in rows if 'XRP' not in r['pair'] and not r['eg_pass5']]):.1f}")


# ======================= PART 3: dependence, placebo, cost arithmetic =======================
print("\n\n===== PART 3 =====")
import random
eq = {}
for r in rows:
    A, B = r["pair"].split("/")
    h = r["h"]
    Xf = [math.log(p) - h * math.log(q) for p, q in zip(F[A], F[B])]
    mX, sX = S.mean(Xf), S.sd(Xf)
    zv = [(math.log(p) - h * math.log(q) - mX) / sX for p, q in zip(V[A], V[B])]
    res = E.run(V[A], V[B], h * F[A][-1] / F[B][-1], zv, sets=500.0 / F[A][-1], hold=30)
    assert abs(res["net"] - r["z_net"]) < 1e-9
    eq[r["pair"]] = S.diff(res["equity"])
def avg_corr(names):
    cs = []
    for x, y in itertools.combinations(names, 2):
        if S.sd(eq[x]) > 0 and S.sd(eq[y]) > 0:
            cs.append(S.corr(eq[x], eq[y]))
    return S.mean(cs), len(cs)
passn = [r["pair"] for r in rows if r["eg_pass5"]]
xrpn = [r["pair"] for r in rows if "XRP" in r["pair"] and not r["pair"].startswith("LTC")]
print(f"avg pairwise corr of daily PnL, 8 EG-pass (all LTC) pairs: {avg_corr(passn)[0]:.2f}")
print(f"avg pairwise corr of daily PnL, 8 XRP pairs (excl LTC/XRP): {avg_corr(xrpn)[0]:.2f}")
print(f"avg pairwise corr of daily PnL, all 45 pairs: {avg_corr([r['pair'] for r in rows])[0]:.2f}")
rng = random.Random(7)
nets = [r["z_net"] for r in rows]
draws = sorted(S.mean(rng.sample(nets, 8)) for _ in range(20000))
obs = S.mean([r["z_net"] for r in rows if r["eg_pass5"]])
print(f"placebo: random 8 of 45 pairs, mean fixed-Z net: median {draws[10000]:.1f}, 95th pct {draws[19000]:.1f}; EG-pass mean {obs:.1f} at pct {100*sum(d < obs for d in draws)/20000:.1f}")
# LTC alone: is the EG-pass result just 'LTC beat the others in validation'?
print("validation return LTC vs others:", ", ".join(f"{c} {100*(V[c][-1]/V[c][0]-1):+.0f}%" for c in coins))
print("formation-end Z of the 8 LTC pairs (sign: + means LTC rich vs partner):",
      ", ".join(f"{r['pair']} {((math.log(F[r['pair'].split('/')[0]][-1]) - r['h']*math.log(F[r['pair'].split('/')[1]][-1])) - S.mean([math.log(p)-r['h']*math.log(q) for p,q in zip(F[r['pair'].split('/')[0]],F[r['pair'].split('/')[1]])]))/r['spread_sd']:+.2f}" for r in rows if r['eg_pass5']))

# cost arithmetic for the owner's "0.98 correlation" example (two coins, 3.5%/day each, h = 1)
print("\nCOST ARITHMETIC: profit per round trip ~ (enter - leave) x stationary SD of spread, enter 2 / leave 0.5")
for rho in (0.80, 0.90, 0.95, 0.98, 0.995):
    sd_day = math.sqrt(2 * 0.035 ** 2 * (1 - rho))
    for hl in (2, 5, 20):
        phi = 0.5 ** (1 / hl)
        sd_stat = sd_day / math.sqrt(1 - phi * phi)  # AR(1): daily shock sd / sqrt(1-phi^2) (treat daily spread change sd as shock sd)
        gross = 1.5 * sd_stat
        print(f"  rho {rho:5.3f} HL {hl:2d}d: daily spread sd {100*sd_day:.2f}%  stationary sd {100*sd_stat:.2f}%  gross/trade {100*gross:.2f}%"
              f"  / book RT cost 0.20% = {gross/0.002:4.1f}x  / retail RT 0.60% (0.1% fee + 0.05% slip per fill) = {gross/0.006:4.1f}x")
