"""Generate weekly RPM + mean-latency charts for the on-call handover doc.

Reads 4 CubeAPM range-query JSON dumps, filters out internal/health endpoints,
picks top 10 real endpoints by mean RPM per region, plots small-multiples PNGs
(one subplot per endpoint), and prints a markdown stub to stdout.

CLI:
  python3 generate_oncall_charts.py \\
      --ksa-rpm /tmp/ksa-rpm.json \\
      --ksa-latency /tmp/ksa-latency.json \\
      --ind-rpm /tmp/ind-rpm.json \\
      --ind-latency /tmp/ind-latency.json \\
      --week-start 2026-04-27 \\
      --out-dir /Users/vashistha.garg/metrics/2026-04-27
"""
import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

IST = timezone(timedelta(hours=5, minutes=30))

EXCLUDE_PATTERNS = [
    re.compile(r"OperationHandler/handle"),
    re.compile(r"/ping\b|/ping \("),
    re.compile(r"actuator/"),
    re.compile(r"/metrics$|Uri/metrics"),
]


def is_internal(span_name: str) -> bool:
    return any(p.search(span_name) for p in EXCLUDE_PATTERNS)


def short_label(span_name: str) -> str:
    s = re.sub(r"^WebTransaction/SpringController/", "", span_name)
    s = re.sub(r"^WebTransaction/Uri/", "", s)
    return s


def load(path: str):
    """Returns [(span_name, [(ts_unix, value_float), ...])].

    Accepts either:
    - MCP tool wrapped:    {"result": "<stringified-json>"}
    - CubeAPM API native:  {"status": "...", "data": {"result": [...]}}
    """
    with open(path) as f:
        outer = json.load(f)
    if "result" in outer and isinstance(outer["result"], str):
        inner = json.loads(outer["result"])
    else:
        inner = outer
    series = []
    for item in inner["data"]["result"]:
        name = item["metric"].get("span_name", "<no_span_name>")
        if is_internal(name):
            continue
        values = []
        for ts, v in item["values"]:
            try:
                fv = float(v)
                if math.isfinite(fv):
                    values.append((int(ts), fv))
            except (ValueError, TypeError):
                continue
        series.append((name, values))
    return series


def top_n(series, n=10):
    def mean(vs):
        if not vs:
            return 0.0
        return sum(v for _, v in vs) / len(vs)
    return sorted(series, key=lambda s: mean(s[1]), reverse=True)[:n]


def stats(values):
    if not values:
        return None
    vs = [v for _, v in values]
    return {
        "min": min(vs),
        "max": max(vs),
        "mean": sum(vs) / len(vs),
        "min_ts": values[vs.index(min(vs))][0],
        "max_ts": values[vs.index(max(vs))][0],
    }


def plot_small_multiples(series, suptitle, ylabel, out_path):
    n = len(series)
    fig_h = max(8.5, n * 1.6 + 1.0)
    fig, axes = plt.subplots(n, 1, figsize=(15, fig_h), sharex=True)
    if n == 1:
        axes = [axes]
    cmap = plt.get_cmap("tab10")

    for i, (name, values) in enumerate(series):
        ax = axes[i]
        if not values:
            ax.text(0.5, 0.5, "no data", ha="center", va="center", transform=ax.transAxes)
            ax.set_title(short_label(name), fontsize=10, loc="left")
            continue
        ts = [datetime.fromtimestamp(t, tz=IST) for t, _ in values]
        ys = [v for _, v in values]
        color = cmap(i % 10)
        ax.plot(ts, ys, color=color, linewidth=1.4, alpha=0.95)
        ax.fill_between(ts, ys, 0, color=color, alpha=0.12)

        ymin, ymax = min(ys), max(ys)
        ymin_ts = ts[ys.index(ymin)]
        ymax_ts = ts[ys.index(ymax)]
        ax.scatter([ymax_ts], [ymax], color="red", marker="^", s=80, zorder=5,
                   edgecolors="black", linewidths=0.6)
        ax.scatter([ymin_ts], [ymin], color="blue", marker="v", s=80, zorder=5,
                   edgecolors="black", linewidths=0.6)
        ax.annotate(f"max {ymax:,.0f}\n{ymax_ts.strftime('%a %H:%M')}",
                    xy=(ymax_ts, ymax), xytext=(8, -2), textcoords="offset points",
                    fontsize=8, color="red", va="top")
        ax.annotate(f"min {ymin:,.0f}\n{ymin_ts.strftime('%a %H:%M')}",
                    xy=(ymin_ts, ymin), xytext=(8, 2), textcoords="offset points",
                    fontsize=8, color="blue", va="bottom")

        mean_v = sum(ys) / len(ys)
        ax.axhline(mean_v, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
        ax.set_title(f"{short_label(name)} — mean {mean_v:,.0f}", fontsize=10, loc="left")
        ax.set_ylabel(ylabel, fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis="y", labelsize=8)

    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%a %d %H:%M", tz=IST))
    axes[-1].xaxis.set_major_locator(mdates.DayLocator(tz=IST))
    plt.setp(axes[-1].get_xticklabels(), rotation=30, ha="right", fontsize=9)
    axes[-1].set_xlabel("Time (IST)")

    fig.suptitle(suptitle, fontsize=13, fontweight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def fmt_ts(ts_unix):
    return datetime.fromtimestamp(ts_unix, tz=IST).strftime("%a %b %d %H:%M IST")


def render_table(top, label_unit, title):
    rows = [f"### {title}", "",
            f"| # | Endpoint | Min ({label_unit}) | Min @ | Max ({label_unit}) | Max @ | Mean |",
            "|---|---|---:|---|---:|---|---:|"]
    for i, (name, values) in enumerate(top, 1):
        st = stats(values)
        if st is None:
            rows.append(f"| {i} | `{short_label(name)}` | — | — | — | — | — |")
            continue
        rows.append(
            f"| {i} | `{short_label(name)}` "
            f"| {st['min']:,.2f} | {fmt_ts(st['min_ts'])} "
            f"| {st['max']:,.2f} | {fmt_ts(st['max_ts'])} "
            f"| {st['mean']:,.2f} |"
        )
    rows.append("")
    return "\n".join(rows)


TOP_N = 5


def render_region(rpm_path, lat_path, region, week_start, out_dir, rel_path):
    rpm_all = load(rpm_path)
    lat_all = load(lat_path)
    rpm_top = top_n(rpm_all, TOP_N)
    lat_ordered = []
    for n, _ in rpm_top:
        match = next((s for s in lat_all if s[0] == n), None)
        lat_ordered.append(match if match else (n, []))

    rpm_png = out_dir / f"{region.lower()}-rpm.png"
    lat_png = out_dir / f"{region.lower()}-latency.png"

    plot_small_multiples(
        rpm_top,
        f"{region} — Top {TOP_N} endpoints by RPM (15-min step, week of {week_start})",
        "RPM",
        rpm_png,
    )
    lat_ms = [(n, [(t, v * 1000) for t, v in vs]) for n, vs in lat_ordered]
    plot_small_multiples(
        lat_ms,
        f"{region} — Mean latency for the same top {TOP_N} (ms, 15-min step)",
        "ms",
        lat_png,
    )

    out = []
    out.append(f"### {region} — RPM (top {TOP_N} endpoints)")
    out.append("")
    out.append(f"![{region} RPM]({rel_path}/{region.lower()}-rpm.png)")
    out.append("")
    out.append(render_table(rpm_top, "RPM", f"{region} — Top {TOP_N} by RPM"))
    out.append(f"### {region} — Mean Latency (same {TOP_N} endpoints)")
    out.append("")
    out.append(f"![{region} Latency]({rel_path}/{region.lower()}-latency.png)")
    out.append("")
    out.append(render_table(lat_ms, "ms", f"{region} — Mean latency for the same top {TOP_N}"))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ksa-rpm", required=True)
    ap.add_argument("--ksa-latency", required=True)
    ap.add_argument("--ind-rpm", required=True)
    ap.add_argument("--ind-latency", required=True)
    ap.add_argument("--week-start", required=True, help="YYYY-MM-DD (Monday IST)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--rel-path", default=None,
                    help="Relative path to chart dir from doc (default: metrics/<week-start>)")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rel_path = args.rel_path or f"metrics/{args.week_start}"

    print(f"## Weekly Metrics — RPM and Mean Latency (top {TOP_N} endpoints by RPM, 15-min windows)")
    print()
    print(f"Source: CubeAPM `cube_apm_calls_total` (RPM) and `cube_apm_latency_{{sum,count}}` (mean latency). "
          f"Window: {args.week_start} 00:00 IST → +7d (Mon → Sun). Step: 15 min. "
          f"Internal/health endpoints (`OperationHandler/handle`, `ping`, `actuator/metrics`, `metrics`) excluded.")
    print()
    print("Each chart is small-multiples — one panel per endpoint, vertically stacked, shared X-axis. "
          "Red ▲ = global max, blue ▽ = global min, gray dashed line = weekly mean.")
    print()
    print(render_region(args.ksa_rpm, args.ksa_latency, "KSA",
                        args.week_start, out_dir, rel_path))
    print()
    print(render_region(args.ind_rpm, args.ind_latency, "IND",
                        args.week_start, out_dir, rel_path))


if __name__ == "__main__":
    main()
