#!/usr/bin/env python3
"""Reproduce the three benchmark charts from raw-data.json.

Usage:  cd benchmarks && python3 make_charts.py
Needs:  matplotlib (plus the standard-library json module).
Output: ../docs/img/chart-scores.svg, chart-time.svg, chart-tokens.svg

Every number in the charts is computed from raw-data.json.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
DATA = HERE / "raw-data.json"
OUT = (HERE / ".." / "docs" / "img").resolve()

# Short English names, in the order of the data file.
CASE_NAMES = {
    "recherche-team-mit-modellen": "Research team",
    "entwicklung-orchestrator-review": "Dev team",
    "modell-nicht-angegeben": "Bulk sorting",
}

# Same palette as docs/img/architecture.svg. One fixed colour per model.
MODEL_COLORS = {"haiku": "#2a9d8f", "sonnet": "#e76f51", "opus": "#6d597a"}
MODEL_TEXT = {"haiku": "white", "sonnet": "white", "opus": "white"}
BASELINE = "#8C8C8C"
TEAM = "#264653"        # team total / critical path
TEAM_LIGHT = "#9fb6bf"  # team sequential sum
INK = "#222222"
MUTED = "#555555"
GRID = "#E3E3E3"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "svg.fonttype": "path",
    "figure.facecolor": "#fbf8f3",
    "axes.facecolor": "#fbf8f3",
    "savefig.facecolor": "#fbf8f3",
    "svg.hashsalt": "agent-teams",
    "text.color": INK,
    "axes.labelcolor": MUTED,
    "xtick.color": INK,
    "ytick.color": MUTED,
    "axes.edgecolor": "#BBBBBB",
    "font.size": 10,
})

# 900 x 420 px when the SVG is displayed (SVG units are pt, 1pt = 4/3 px).
FIGSIZE = (900 / 96, 420 / 96)


def load():
    with open(DATA, encoding="utf-8") as f:
        raw = json.load(f)
    return raw["cases"]


def metrics(case):
    team = case["team"]
    phases = sorted({m["phase"] for m in team})
    critical_ms = sum(
        max(m["duration_ms"] for m in team if m["phase"] == p) for p in phases
    )
    sequential_ms = sum(m["duration_ms"] for m in team)
    tokens_by_model = {k: 0 for k in MODEL_COLORS}
    for m in team:
        tokens_by_model[m["model"]] += m["tokens"]
    return {
        "critical_s": critical_ms / 1000,
        "sequential_s": sequential_ms / 1000,
        "baseline_s": case["baseline"]["duration_ms"] / 1000,
        "tokens_by_model": tokens_by_model,
        "team_tokens": sum(tokens_by_model.values()),
        "baseline_tokens": case["baseline"]["tokens"],
        "skill_pass": sum(a["passed"] for a in case["grading"]["with_skill_orchestrator"]),
        "skill_total": len(case["grading"]["with_skill_orchestrator"]),
        "base_pass": sum(a["passed"] for a in case["grading"]["baseline_single_agent"]),
        "base_total": len(case["grading"]["baseline_single_agent"]),
    }


def style_axes(ax, ylabel, title):
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", color=INK, pad=12)
    ax.set_ylabel(ylabel)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="x", length=0, labelsize=10.5)
    ax.tick_params(axis="y", length=0)


def legend(ax, handles, labels, ncol):
    ax.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, -0.12),
              ncol=ncol, frameon=False, fontsize=9.5, handlelength=1.2,
              columnspacing=1.8)


def swatch(color):
    return plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor="none")


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, format="svg", metadata={"Date": None})
    plt.close(fig)
    print("wrote", path)


def chart_scores(names, ms):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    w = 0.34
    for i, m in enumerate(ms):
        for dx, key, color in ((-w / 2 - 0.01, "skill", TEAM), (w / 2 + 0.01, "base", BASELINE)):
            p, t = m[f"{key}_pass"], m[f"{key}_total"]
            ax.bar(i + dx, 100 * p / t, w, color=color, linewidth=0)
            ax.text(i + dx, 100 * p / t + 2, f"{p}/{t}", ha="center", va="bottom",
                    fontsize=11, fontweight="bold", color=INK)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names)
    ax.set_ylim(0, 115)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels([f"{v}%" for v in (0, 25, 50, 75, 100)])
    style_axes(ax, "Criteria passed",
               "Criteria passed per test case (mostly team-behaviour checks)")
    legend(ax, [swatch(TEAM), swatch(BASELINE)],
           ["With skill (orchestrator)", "Baseline (single agent)"], 2)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.88, bottom=0.22)
    save(fig, "chart-scores.svg")


def chart_time(names, ms):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    w = 0.26
    series = (
        ("baseline_s", BASELINE, -w - 0.01),
        ("critical_s", TEAM, 0),
        ("sequential_s", TEAM_LIGHT, w + 0.01),
    )
    top = max(m["sequential_s"] for m in ms)
    for i, m in enumerate(ms):
        for key, color, dx in series:
            ax.bar(i + dx, m[key], w, color=color, linewidth=0)
            ax.text(i + dx, m[key] + top * 0.012, f"{m[key]:.1f}", ha="center",
                    va="bottom", fontsize=10, color=INK)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names)
    ax.set_ylim(0, top * 1.12)
    style_axes(ax, "Wall-clock time (seconds)",
               "Time: team vs. single-agent baseline (lower is faster)")
    legend(ax, [swatch(c) for _, c, _ in series],
           ["Baseline single agent", "Team critical path",
            "Team sequential sum"], 3)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.88, bottom=0.22)
    save(fig, "chart-time.svg")


def chart_tokens(names, ms):
    fig, ax = plt.subplots(figsize=FIGSIZE)
    w = 0.34
    top = max(m["team_tokens"] for m in ms)
    for i, m in enumerate(ms):
        x = i - w / 2 - 0.01
        bottom = 0
        for model in ("haiku", "sonnet", "opus"):
            v = m["tokens_by_model"][model]
            if v == 0:
                continue
            # 2 px surface gap between stacked segments via a white edge.
            ax.bar(x, v, w, bottom=bottom, color=MODEL_COLORS[model],
                   edgecolor="#fbf8f3", linewidth=1.5)
            ax.text(x, bottom + v / 2, f"{v / 1000:.0f}k", ha="center", va="center",
                    fontsize=9.5, color=MODEL_TEXT[model])
            bottom += v
        ax.text(x, bottom + top * 0.012, f"{bottom / 1000:.0f}k", ha="center",
                va="bottom", fontsize=10.5, fontweight="bold", color=INK)
        xb = i + w / 2 + 0.01
        b = m["baseline_tokens"]
        ax.bar(xb, b, w, color=BASELINE, linewidth=0)
        ax.text(xb, b + top * 0.012, f"{b / 1000:.0f}k", ha="center", va="bottom",
                fontsize=10.5, fontweight="bold", color=INK)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names)
    ax.set_ylim(0, top * 1.12)
    ticks = ax.get_yticks()
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{int(t / 1000)}k" for t in ticks])
    ax.set_ylim(0, top * 1.12)
    style_axes(ax, "Tokens (harness-reported)",
               "Tokens: team by model (stacked) next to single-agent baseline")
    legend(ax, [swatch(MODEL_COLORS[k]) for k in ("haiku", "sonnet", "opus")]
           + [swatch(BASELINE)],
           ["Team: haiku", "Team: sonnet", "Team: opus", "Baseline single agent"], 4)
    fig.subplots_adjust(left=0.10, right=0.98, top=0.88, bottom=0.22)
    save(fig, "chart-tokens.svg")


def main():
    cases = load()
    names = [CASE_NAMES[k] for k in cases]
    ms = [metrics(c) for c in cases.values()]
    for n, m in zip(names, ms):
        print(f"{n}: score {m['skill_pass']}/{m['skill_total']} vs {m['base_pass']}/{m['base_total']}; "
              f"time base {m['baseline_s']:.1f}s, critical {m['critical_s']:.1f}s, "
              f"sum {m['sequential_s']:.1f}s; tokens team {m['team_tokens']} "
              f"vs base {m['baseline_tokens']} ({m['team_tokens'] / m['baseline_tokens']:.2f}x)")
    chart_scores(names, ms)
    chart_time(names, ms)
    chart_tokens(names, ms)


if __name__ == "__main__":
    main()
