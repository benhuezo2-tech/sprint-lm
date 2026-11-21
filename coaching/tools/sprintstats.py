#!/usr/bin/env python3
"""sprintstats: small, dependency-free statistics for single-athlete sprint testing.

Standard library only (Python 3.9+). Subcommands:
  te        typical error (noise floor) from repeated fly times
  cuetest   alternating-treatments cue test decision (A = usual, B = cue)
  stoprule  two consecutive reps >= 3% slower than the session best
  fly       time and speed from frame counts or timestamps
  race      100 m velocity-curve model: time, splits, sensitivity, or vmax for a target
  shuffle   copy clips under random IDs for blind scoring (+ key file)
  unblind   join blind scores back to the original clip names
  selftest  run known-answer checks

Every output is a decision aid, not a verdict. Numbers from small samples are estimates.
"""
import argparse
import csv
import math
import os
import secrets
import shutil
import statistics
import sys
from collections import OrderedDict

# Two-sided 95% critical values of Student's t, df = 1..30.
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306,
       9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
       16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080, 22: 2.074,
       23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042}

# 95% limits for a single change between two trials: 1.96 * sqrt(2) * TE (Hopkins 2000).
CHANGE_LIMIT_MULT = 1.96 * math.sqrt(2)


def t95(df):
    if df < 1:
        raise ValueError("need at least 2 days/observations")
    return T95.get(df, 1.96)


def read_rows(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit(f"{path}: no rows")
    return rows


def group_times(rows, key, value="time_s"):
    groups = OrderedDict()
    for r in rows:
        k = r[key].strip()
        v = r[value].strip()
        if v == "":
            continue
        groups.setdefault(k, []).append(float(v))
    return groups


# ---------- typical error ----------
def typical_error(groups):
    """Pooled within-session SD (typical error per rep) and related quantities."""
    ss, df = 0.0, 0
    for times in groups.values():
        if len(times) >= 2:
            m = statistics.mean(times)
            ss += sum((t - m) ** 2 for t in times)
            df += len(times) - 1
    if df == 0:
        raise ValueError("need >= 2 reps in at least one session")
    te = math.sqrt(ss / df)
    all_times = [t for ts in groups.values() for t in ts]
    grand = statistics.mean(all_times)
    means = [statistics.mean(ts) for ts in groups.values()]
    between_sd = statistics.stdev(means) if len(means) >= 2 else float("nan")
    n_typ = statistics.median([len(ts) for ts in groups.values()])
    return {
        "sessions": len(groups),
        "reps_total": len(all_times),
        "df": df,
        "te_rep": te,
        "cv_pct": 100 * te / grand,
        "te_session_mean": te / math.sqrt(n_typ),
        "reps_per_session_median": n_typ,
        "between_session_sd_of_means": between_sd,
        "change_limit_rep": CHANGE_LIMIT_MULT * te,
        "change_limit_session_mean": CHANGE_LIMIT_MULT * te / math.sqrt(n_typ),
        "grand_mean": grand,
    }


def cmd_te(a):
    groups = group_times(read_rows(a.csv), a.session_col)
    r = typical_error(groups)
    print(f"Sessions: {r['sessions']}  reps: {r['reps_total']}  (within-session df = {r['df']})")
    print(f"Typical error per rep (pooled within-session SD): {r['te_rep']:.4f} s  (CV {r['cv_pct']:.2f}%)")
    print(f"Typical error of a session mean (n = {r['reps_per_session_median']:g}): {r['te_session_mean']:.4f} s")
    if not math.isnan(r['between_session_sd_of_means']):
        print(f"SD of session means across days: {r['between_session_sd_of_means']:.4f} s "
              "(includes real day-to-day change as well as noise)")
    print(f"95% noise band for one rep vs one rep: +/-{r['change_limit_rep']:.4f} s (= 2.77 x TE)")
    print(f"95% noise band for one session mean vs another: +/-{r['change_limit_session_mean']:.4f} s")
    if r['df'] < 10:
        print("Caution: fewer than 10 degrees of freedom. Label this ESTIMATED and re-estimate as data accumulate.")


# ---------- cue test ----------
def cue_test(day_diffs, threshold=0.010):
    k = len(day_diffs)
    if k < 2:
        raise ValueError("need >= 2 comparison days")
    md = statistics.mean(day_diffs)
    sd = statistics.stdev(day_diffs)
    se = sd / math.sqrt(k)
    t = t95(k - 1)
    lo, hi = md - t * se, md + t * se
    if md >= threshold and lo > 0:
        decision = "KEEP (provisional)"
    elif hi < 0:
        decision = "HARMFUL (the cue made you slower)"
    else:
        decision = "INCONCLUSIVE (not proven useless; the evidence just isn't strong enough)"
    return {"days": k, "mean_d": md, "sd_d": sd, "se": se, "t": t, "lower": lo, "upper": hi,
            "threshold": threshold, "decision": decision}


def cmd_cuetest(a):
    rows = read_rows(a.csv)
    by_day = OrderedDict()
    for r in rows:
        day = r[a.session_col].strip()
        cond = r["condition"].strip().upper()
        if r["time_s"].strip() == "":
            continue
        by_day.setdefault(day, {"A": [], "B": []})
        if cond not in ("A", "B"):
            sys.exit(f"condition must be A (usual) or B (cue), got {cond!r}")
        by_day[day][cond].append(float(r["time_s"]))
    diffs = []
    print("day, mean A (usual), mean B (cue), d = A - B (positive = cue faster)")
    for day, c in by_day.items():
        if not c["A"] or not c["B"]:
            print(f"  {day}: skipped (needs both A and B reps)")
            continue
        d = statistics.mean(c["A"]) - statistics.mean(c["B"])
        diffs.append(d)
        print(f"  {day}: {statistics.mean(c['A']):.3f}  {statistics.mean(c['B']):.3f}  {d:+.4f}")
    r = cue_test(diffs, a.threshold)
    print(f"Comparison days: {r['days']}  mean d = {r['mean_d']:+.4f} s  SD = {r['sd_d']:.4f}")
    print(f"95% interval for the cue effect: {r['lower']:+.4f} to {r['upper']:+.4f} s (t = {r['t']})")
    print(f"Rule: keep if mean d >= {r['threshold']:.3f} s AND lower limit > 0, with no symptom worsening.")
    print(f"Decision: {r['decision']}")
    print("Note: this estimates the cue's acute effect; retention sessions can't fully separate learning from carry-over.")


# ---------- stop rule ----------
def stop_rule(times, pct=3.0):
    best = None
    slow_streak = 0
    for i, t in enumerate(times, 1):
        best = t if best is None else min(best, t)
        if t >= best * (1 + pct / 100) and t != best:
            slow_streak += 1
            if slow_streak >= 2:
                return i, best
        else:
            slow_streak = 0
    return None, best


def cmd_stoprule(a):
    i, best = stop_rule(a.times, a.pct)
    if i:
        print(f"STOP after rep {i}: two consecutive reps >= {a.pct:g}% slower than the session best ({best:.3f} s).")
    else:
        print(f"No stop triggered. Session best {best:.3f} s; threshold {best * (1 + a.pct / 100):.3f} s.")


# ---------- fly timing ----------
def fly(dist, seconds, frame_s=None):
    v = dist / seconds
    out = {"time_s": seconds, "speed_ms": v, "speed_kmh": v * 3.6}
    if frame_s:
        lo_t, hi_t = seconds - frame_s, seconds + frame_s
        out["time_range"] = (lo_t, hi_t)
        out["speed_range"] = (dist / hi_t, dist / lo_t)
    return out


def cmd_fly(a):
    if a.t0 is not None and a.t1 is not None:
        seconds = a.t1 - a.t0
        frame_s = 1 / a.fps if a.fps else None
    elif a.frames is not None and a.fps:
        seconds = a.frames / a.fps
        frame_s = 1 / a.fps
    else:
        sys.exit("give --t0 and --t1 (seconds, from sprintvid timestamps) or --frames with --fps")
    r = fly(a.dist, seconds, frame_s)
    print(f"{a.dist:g} m in {r['time_s']:.4f} s = {r['speed_ms']:.3f} m/s ({r['speed_kmh']:.2f} km/h)")
    if "time_range" in r:
        print(f"+/- 1 frame: {r['time_range'][0]:.4f}-{r['time_range'][1]:.4f} s, "
              f"{r['speed_range'][0]:.3f}-{r['speed_range'][1]:.3f} m/s")
    print("Take t0/t1 from the media_time_s column of `sprintvid timestamps` (the capture clock). Never use playback time from slow motion.")


# ---------- blind scoring ----------
VIDEO_EXT = {".mov", ".mp4", ".m4v"}


def cmd_shuffle(a):
    src = os.path.expanduser(a.src)
    dst = os.path.expanduser(a.dst)
    os.makedirs(dst, exist_ok=True)
    clips = sorted(f for f in os.listdir(src) if os.path.splitext(f)[1].lower() in VIDEO_EXT)
    if not clips:
        sys.exit("no .mov/.mp4/.m4v files found")
    key_path = os.path.abspath(os.path.expanduser(a.key))
    if os.path.exists(key_path):
        sys.exit(f"{key_path} exists; refusing to overwrite a key")
    if os.path.commonpath([key_path, os.path.abspath(dst)]) == os.path.abspath(dst):
        sys.exit("put the key outside the blind folder, or the scorer will see it")
    # Prepare and test the key location BEFORE copying anything, so a failure can't leave keyless copies.
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    with open(key_path, "w", newline="") as fh:
        fh.write("")
    rows = []
    for f in clips:
        cid = secrets.token_hex(3)
        ext = os.path.splitext(f)[1].lower()
        shutil.copy2(os.path.join(src, f), os.path.join(dst, cid + ext))
        rows.append({"id": cid, "original": f})
    secrets.SystemRandom().shuffle(rows)
    with open(key_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "original"])
        w.writeheader()
        w.writerows(rows)
    print(f"Copied {len(rows)} clips to {dst} under random IDs (originals untouched).")
    print(f"Key saved to {key_path}. Have someone else keep it; don't open it until scoring is done.")


def cmd_unblind(a):
    key = {r["id"]: r["original"] for r in read_rows(a.key)}
    scores = read_rows(a.scores)
    w = csv.writer(sys.stdout)
    cols = list(scores[0].keys())
    w.writerow(["original"] + cols)
    for r in scores:
        w.writerow([key.get(r["id"], "?")] + [r[c] for c in cols])


# ---------- race model ----------
# Mono-exponential acceleration v(t) = vmax(1 - e^(-t/tau)) (Furusawa/Hill 1927; field form in
# Samozino 2016), then a linear-in-distance velocity loss from decel_start to the finish.
# A SIMULATION for ranking levers in race-time currency, not a measurement or a prediction.
def _x_exp(t, vmax, tau):
    return vmax * (t - tau * (1.0 - math.exp(-t / tau)))


def _t_at_x_exp(x, vmax, tau):
    lo, hi = 0.0, x / vmax + 10.0 * tau
    for _ in range(200):
        mid = (lo + hi) / 2
        if _x_exp(mid, vmax, tau) < x:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def race_model(vmax, tau, rt=0.15, decel_start=60.0, decel_pct=0.0, dist=100.0):
    """Return total time (incl. reaction) and cumulative splits every 10 m."""
    xd = min(decel_start, dist)
    t_d = _t_at_x_exp(xd, vmax, tau)
    v_d = vmax * (1.0 - math.exp(-t_d / tau))
    seg = dist - xd
    v_end = v_d * (1.0 - decel_pct / 100.0)
    slope = (v_d - v_end) / seg if seg > 0 else 0.0

    def t_at(x):
        if x <= xd:
            return _t_at_x_exp(x, vmax, tau)
        dx = x - xd
        if slope == 0:
            return t_d + dx / v_d
        return t_d + math.log(v_d / (v_d - slope * dx)) / slope

    splits = OrderedDict()
    for m in range(10, int(dist) + 1, 10):
        splits[m] = rt + t_at(float(m))
    return {"total": rt + t_at(dist), "splits": splits, "v_at_decel": v_d, "v_finish": v_end}


def vmax_for_target(target, tau, rt, decel_start, decel_pct, dist=100.0):
    lo, hi = 3.0, 15.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if race_model(mid, tau, rt, decel_start, decel_pct, dist)["total"] > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def cmd_race(a):
    lab = "placeholder" if a.label == "placeholder" else a.label
    if a.target is not None:
        v = vmax_for_target(a.target, a.tau, a.rt, a.decel_start, a.decel_pct, a.dist)
        print(f"target {a.target:.2f} s needs vmax ~ {v:.2f} m/s "
              f"(tau {a.tau} s, RT {a.rt} s, {a.decel_pct}% loss from {a.decel_start:g} m) [simulation; inputs {lab}]")
        vmax = v
    else:
        if a.vmax is None:
            sys.exit("give --vmax (e.g. fly speed in m/s) or --target")
        vmax = a.vmax
    base = race_model(vmax, a.tau, a.rt, a.decel_start, a.decel_pct, a.dist)
    print(f"model {a.dist:g} m: {base['total']:.2f} s  (vmax {vmax:.2f}, v at {a.decel_start:g} m "
          f"{base['v_at_decel']:.2f}, finish {base['v_finish']:.2f} m/s) [simulation; inputs {lab}]")
    print("splits: " + "  ".join(f"{m}m {t:.2f}" for m, t in base["splits"].items()))
    levers = [
        ("vmax +1%", dict(vmax=vmax * 1.01)),
        ("tau -5% (faster rise)", dict(tau=a.tau * 0.95)),
        ("speed loss -1 pt", dict(decel_pct=max(0.0, a.decel_pct - 1.0))),
        ("reaction -0.01 s", dict(rt=a.rt - 0.01)),
    ]
    print("lever (one at a time)        gain in s")
    for name, ch in levers:
        kw = dict(vmax=vmax, tau=a.tau, rt=a.rt, decel_start=a.decel_start, decel_pct=a.decel_pct, dist=a.dist)
        kw.update(ch)
        print(f"  {name:<27}{base['total'] - race_model(**kw)['total']:+.3f}")
    print("Ranks levers in race-time currency. Real levers interact (raising vmax lengthens acceleration).")


# ---------- self test ----------
def cmd_selftest(_a):
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    check("2.77 multiplier", abs(CHANGE_LIMIT_MULT - 2.7719) < 1e-3)
    check("t(5) = 2.571", t95(5) == 2.571)
    g = OrderedDict([("d1", [1.00, 1.02]), ("d2", [0.98, 1.00])])  # within SD = 0.01414
    r = typical_error(g)
    check("TE pooled", abs(r["te_rep"] - 0.014142) < 1e-5)
    check("change limit = 2.77 x TE", abs(r["change_limit_rep"] - 0.0392) < 1e-3)
    c = cue_test([0.020, 0.015, 0.018, 0.012, 0.020, 0.016])
    check("cue test KEEP", c["decision"].startswith("KEEP") and abs(c["lower"] - 0.01355) < 2e-4)
    c2 = cue_test([0.010, -0.012, 0.004, -0.006, 0.008, 0.001])
    check("cue test INCONCLUSIVE", c2["decision"].startswith("INCONCLUSIVE"))
    c3 = cue_test([-0.020, -0.015, -0.018, -0.012, -0.020, -0.016])
    check("cue test HARMFUL", c3["decision"].startswith("HARMFUL"))
    i, best = stop_rule([1.02, 1.00, 0.99, 1.03, 1.04])
    check("stop rule triggers at rep 5", i == 5 and best == 0.99)
    i2, _ = stop_rule([1.00, 1.01, 1.02, 1.00])
    check("stop rule not triggered", i2 is None)
    f = fly(9.14, 0.95)
    check("fly 9.14 m / 0.95 s = 9.621 m/s", abs(f["speed_ms"] - 9.6211) < 1e-3)
    r0 = race_model(10.0, 1.0, rt=0.0, decel_start=100.0, decel_pct=0.0)
    check("race closed form (vmax 10, tau 1) = 10.99998 s", abs(r0["total"] - 10.99998) < 1e-4)
    r1 = race_model(10.0, 1.0, rt=0.0, decel_start=60.0, decel_pct=10.0)
    tn, n = _t_at_x_exp(60.0, 10.0, 1.0), 40000
    vd = 10.0 * (1 - math.exp(-tn))
    tn += sum(0.001 / (vd - (vd * 0.1 / 40.0) * ((k + 0.5) * 0.001)) for k in range(n))
    check("race decel integral matches numeric", abs(r1["total"] - tn) < 1e-6)
    vt = vmax_for_target(10.22, 1.3, 0.15, 60.0, 3.0)
    check("race inverse recovers target", abs(race_model(vt, 1.3, 0.15, 60.0, 3.0)["total"] - 10.22) < 1e-6)
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)

    q = s.add_parser("te", help="typical error from CSV with columns date,time_s")
    q.add_argument("csv")
    q.add_argument("--session-col", default="date")
    q.set_defaults(fn=cmd_te)

    q = s.add_parser("cuetest", help="CSV with columns date,condition(A/B),time_s")
    q.add_argument("csv")
    q.add_argument("--session-col", default="date")
    q.add_argument("--threshold", type=float, default=0.010)
    q.set_defaults(fn=cmd_cuetest)

    q = s.add_parser("stoprule", help="rep times in order")
    q.add_argument("times", type=float, nargs="+")
    q.add_argument("--pct", type=float, default=3.0)
    q.set_defaults(fn=cmd_stoprule)

    q = s.add_parser("fly", help="time/speed over a fly zone")
    q.add_argument("--dist", type=float, default=9.14)
    q.add_argument("--frames", type=float)
    q.add_argument("--fps", type=float)
    q.add_argument("--t0", type=float, help="media_time_s of the first gate frame")
    q.add_argument("--t1", type=float, help="media_time_s of the second gate frame")
    q.set_defaults(fn=cmd_fly)

    q = s.add_parser("race", help="100 m velocity-curve model (simulation)")
    q.add_argument("--vmax", type=float, help="top speed in m/s (e.g. from fly)")
    q.add_argument("--target", type=float, help="solve vmax for this race time instead")
    q.add_argument("--tau", type=float, default=1.3, help="acceleration time constant, s (placeholder 1.3)")
    q.add_argument("--rt", type=float, default=0.15, help="reaction time, s (placeholder 0.15)")
    q.add_argument("--decel-start", type=float, default=60.0)
    q.add_argument("--decel-pct", type=float, default=3.0, help="%% of speed lost from decel-start to finish")
    q.add_argument("--dist", type=float, default=100.0)
    q.add_argument("--label", default="placeholder", help="measured / estimated / placeholder")
    q.set_defaults(fn=cmd_race)

    q = s.add_parser("shuffle", help="copy clips under random IDs for blind scoring")
    q.add_argument("src")
    q.add_argument("dst")
    q.add_argument("--key", required=True, help="where to write the key CSV (keep it away from the scorer)")
    q.set_defaults(fn=cmd_shuffle)

    q = s.add_parser("unblind", help="join scores (id,...) back to original names")
    q.add_argument("key")
    q.add_argument("scores")
    q.set_defaults(fn=cmd_unblind)

    q = s.add_parser("selftest")
    q.set_defaults(fn=cmd_selftest)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
