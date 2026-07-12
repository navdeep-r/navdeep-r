"""
Generate a GitHub-style contribution heatmap SVG matching the terminal aesthetic.
Reads data/contributions.json and outputs a polished SVG with:
  - Terminal window chrome (dots + title bar)
  - Month labels, day-of-week labels (Mon, Wed, Fri)
  - 53x7 grid of rounded green boxes on dark bg
  - Less→More legend
  - Stats footer (total, date range, streaks, best day)
  - Diagonal slide-down CSS animation (plays once, freezes)
"""
import os
import sys
import json
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "..", "data", "contributions.json")
OUT_FILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets", "contributions.svg")

# ── Colors ──────────────────────────────────────────────────────────
BG        = "#0d1117"
BG2       = "#111722"
FRAME     = "#30363d"
TEXT_DIM  = "#8b949e"
TEXT_MAIN = "#c9d1d9"
GREEN_0   = "#161b22"   # no contributions (empty box, still visible)
GREEN_1   = "#0e4429"
GREEN_2   = "#006d32"
GREEN_3   = "#26a641"
GREEN_4   = "#39d353"
COLOR_GREEN  = "#3fb950"   # total contributions
COLOR_YELLOW = "#e3b341"   # streak numbers
COLOR_RED    = "#f97583"   # best day count
COLOR_CYAN   = "#79c0ff"   # date range

# ── Layout constants ───────────────────────────────────────────────
BOX       = 11
GAP       = 3
CELL      = BOX + GAP
TITLEBAR  = 30
LEFT_PAD  = 50          # space for day labels
TOP_PAD   = 22          # space for month labels
GRID_X    = 20 + LEFT_PAD
GRID_Y    = TITLEBAR + 12 + TOP_PAD
MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]


def color_for_count(count):
    """Map contribution count → green shade."""
    if count == 0:  return GREEN_0
    if count <= 3:  return GREEN_1
    if count <= 6:  return GREEN_2
    if count <= 9:  return GREEN_3
    return GREEN_4


def compute_stats(weeks):
    """Derive streak / best-day stats from the week data."""
    all_days = []
    for w in weeks:
        for d in w["contributionDays"]:
            all_days.append(d)

    total = sum(d["contributionCount"] for d in all_days)

    # best day
    best = max(all_days, key=lambda d: d["contributionCount"])
    best_count = best["contributionCount"]
    best_date  = best["date"]

    # streaks (current + longest)
    longest_streak = 0
    current_streak = 0
    streak = 0
    for d in all_days:
        if d["contributionCount"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0
    # current streak = count back from the last day
    current_streak = 0
    for d in reversed(all_days):
        if d["contributionCount"] > 0:
            current_streak += 1
        else:
            break

    date_start = all_days[0]["date"]
    date_end   = all_days[-1]["date"]

    return {
        "total": total,
        "best_count": best_count,
        "best_date": best_date,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "date_start": date_start,
        "date_end": date_end,
    }


def month_labels(weeks):
    """Return list of (week_index, month_name) for the first week of each month."""
    labels = []
    prev_month = None
    for i, w in enumerate(weeks):
        first_day = w["contributionDays"][0]["date"]
        m = int(first_day.split("-")[1])
        if m != prev_month:
            labels.append((i, MONTH_NAMES[m - 1]))
            prev_month = m
    return labels


def main():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found. Run fetch_contributions.py first.")
        sys.exit(1)

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks    = calendar["weeks"]
    stats    = compute_stats(weeks)
    m_labels = month_labels(weeks)

    num_weeks = len(weeks)
    canvas_w  = GRID_X + num_weeks * CELL + 20
    canvas_h  = GRID_Y + 7 * CELL + 90       # extra room for legend + separator + footer

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
    )

    # ── CSS animations ──────────────────────────────────────────────
    svg.append("""<style>
      .cell {
        opacity: 0;
        animation: pop .4s ease forwards;
      }
      @keyframes pop {
        0%   { opacity: 0; transform: scale(0); }
        70%  { opacity: 1; transform: scale(1.15); }
        100% { opacity: 1; transform: scale(1); }
      }
      .fade { opacity: 0; animation: fadeIn .6s ease forwards; }
      @keyframes fadeIn { to { opacity: 1; } }
    </style>""")

    # ── Background ──────────────────────────────────────────────────
    svg.append(f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
               f'<stop offset="0" stop-color="{BG2}"/>'
               f'<stop offset="1" stop-color="{BG}"/></linearGradient></defs>')
    svg.append(f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg)"/>')
    svg.append(f'<rect x=".5" y=".5" width="{canvas_w-1}" height="{canvas_h-1}" '
               f'rx="12" fill="none" stroke="{FRAME}"/>')

    # ── Title bar ───────────────────────────────────────────────────
    svg.append(f'<line x1="0" y1="{TITLEBAR}" x2="{canvas_w}" y2="{TITLEBAR}" stroke="{FRAME}"/>')
    for i, c in enumerate(["#ff5f56","#ffbd2e","#27c93f"]):
        svg.append(f'<circle cx="{20+i*16}" cy="{TITLEBAR//2}" r="5" fill="{c}"/>')
    svg.append(f'<text x="{canvas_w//2}" y="{TITLEBAR//2+4}" fill="{TEXT_DIM}" '
               f'font-size="12" text-anchor="middle">'
               f'navdeep-r@github: ~/contributions --graph</text>')

    # ── Month labels ────────────────────────────────────────────────
    for w_idx, name in m_labels:
        x = GRID_X + w_idx * CELL
        y = GRID_Y - 8
        svg.append(f'<text x="{x}" y="{y}" fill="{TEXT_DIM}" font-size="11">{name}</text>')

    # ── Day-of-week labels ──────────────────────────────────────────
    day_labels = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    for d_idx, label in day_labels:
        y = GRID_Y + d_idx * CELL + BOX * 0.8
        svg.append(f'<text x="{GRID_X - 8}" y="{y}" fill="{TEXT_DIM}" '
                   f'font-size="11" text-anchor="end">{label}</text>')

    # ── Contribution grid ───────────────────────────────────────────
    for w_idx, week in enumerate(weeks):
        for d_idx, day in enumerate(week["contributionDays"]):
            count = day["contributionCount"]
            color = color_for_count(count)
            x = GRID_X + w_idx * CELL
            y = GRID_Y + d_idx * CELL

            # diagonal stagger: column + row
            delay = (w_idx + d_idx) * 0.018

            svg.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{BOX}" height="{BOX}" '
                f'rx="2" fill="{color}" style="animation-delay:{delay:.3f}s"/>'
            )

    # ── Legend (Less → More) ────────────────────────────────────────
    legend_y  = GRID_Y + 7 * CELL + 12
    legend_x  = GRID_X + (num_weeks - 8) * CELL
    total_anim_time = (num_weeks + 7) * 0.018 + 0.4  # after all boxes land

    svg.append(f'<g class="fade" style="animation-delay:{total_anim_time:.1f}s">')
    svg.append(f'<text x="{legend_x - 30}" y="{legend_y + 9}" fill="{TEXT_DIM}" '
               f'font-size="11">Less</text>')
    for i, c in enumerate([GREEN_0, GREEN_1, GREEN_2, GREEN_3, GREEN_4]):
        svg.append(f'<rect x="{legend_x + i * (BOX + 3)}" y="{legend_y}" '
                   f'width="{BOX}" height="{BOX}" rx="2" fill="{c}"/>')
    svg.append(f'<text x="{legend_x + 5 * (BOX + 3) + 4}" y="{legend_y + 9}" '
               f'fill="{TEXT_DIM}" font-size="11">More</text>')
    svg.append('</g>')

    # ── Separator line ──────────────────────────────────────────────
    sep_y = legend_y + 22
    svg.append(f'<line x1="{GRID_X}" y1="{sep_y}" x2="{GRID_X + num_weeks * CELL}" '
               f'y2="{sep_y}" stroke="{FRAME}" class="fade" '
               f'style="animation-delay:{total_anim_time + 0.2:.1f}s"/>')

    # ── Stats footer ────────────────────────────────────────────────
    footer_y1 = sep_y + 20
    footer_y2 = footer_y1 + 20
    right_x   = GRID_X + num_weeks * CELL

    svg.append(f'<g class="fade" style="animation-delay:{total_anim_time + 0.3:.1f}s">')

    # Row 1: total contributions (green) + date range (cyan)
    svg.append(f'<text x="{GRID_X}" y="{footer_y1}" fill="{TEXT_DIM}" font-size="13">'
               f'<tspan fill="{COLOR_GREEN}" font-weight="bold">{stats["total"]:,}</tspan>'
               f' contributions in the last year</text>')
    svg.append(f'<text x="{right_x}" y="{footer_y1}" fill="{TEXT_DIM}" '
               f'font-size="13" text-anchor="end">'
               f'<tspan fill="{COLOR_CYAN}">{stats["date_start"]}</tspan>'
               f' \u2192 '
               f'<tspan fill="{COLOR_CYAN}">{stats["date_end"]}</tspan></text>')

    # Row 2: streaks (yellow) + best day (red)
    svg.append(f'<text x="{GRID_X}" y="{footer_y2}" fill="{TEXT_DIM}" font-size="13">'
               f'current streak <tspan fill="{COLOR_YELLOW}" font-weight="bold">'
               f'{stats["current_streak"]}</tspan> days \u00b7 longest '
               f'<tspan fill="{COLOR_YELLOW}" font-weight="bold">'
               f'{stats["longest_streak"]}</tspan> days</text>')
    svg.append(f'<text x="{right_x}" y="{footer_y2}" fill="{TEXT_DIM}" '
               f'font-size="13" text-anchor="end">'
               f'best day <tspan fill="{COLOR_RED}" font-weight="bold">'
               f'{stats["best_count"]}</tspan> on {stats["best_date"]}</text>')

    svg.append('</g>')

    svg.append("</svg>")

    out = "".join(svg)
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {OUT_FILE}  {len(out)} bytes  {canvas_w}×{canvas_h}")


if __name__ == "__main__":
    main()
