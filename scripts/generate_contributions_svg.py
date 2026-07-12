import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "..", "data", "contributions.json")
OUT_FILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets", "contributions.svg")

# Styling
BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TEXT_COLOR = "#c9d1d9"
TEXT_MUTED = "#8b949e"
COLORS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

BOX_SIZE = 10
GAP = 4
CELL = BOX_SIZE + GAP

def main():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found. Run fetch_contributions.py first.")
        sys.exit(1)
        
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        
    try:
        calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        total = calendar["totalContributions"]
        weeks = calendar["weeks"]
    except KeyError as e:
        print(f"Invalid data format: missing {e}")
        sys.exit(1)
        
    num_weeks = len(weeks)
    width = num_weeks * CELL + 40
    height = 7 * CELL + 80
    
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="-apple-system, BlinkMacSystemFont, '
        f'Segoe UI, Helvetica, Arial, sans-serif">'
    )
    
    # CSS Keyframes for diagonal slide-down reveal
    parts.append("""
    <style>
      .box {
        opacity: 0;
        transform: translateY(-10px);
        animation: slideDown 0.5s ease-out forwards;
      }
      @keyframes slideDown {
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
    </style>
    """)
    
    parts.append('<defs>'
                 f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
                 f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
                 f'</linearGradient></defs>')
                 
    # Background
    parts.append(f'<rect width="{width}" height="{height}" rx="6" fill="url(#bg)"/>')
    parts.append(f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="6" '
                 f'fill="none" stroke="{FRAME}" stroke-width="1"/>')
                 
    # Title
    parts.append(f'<text x="20" y="25" fill="{TEXT_COLOR}" font-size="14" font-weight="600">'
                 f'{total} contributions in the last year</text>')
                 
    # Grid
    grid_x = 20
    grid_y = 40
    
    parts.append(f'<g transform="translate({grid_x}, {grid_y})">')
    
    for w_idx, week in enumerate(weeks):
        for d_idx, day in enumerate(week["contributionDays"]):
            # Get actual day of week from date to correctly position (0 = Sunday)
            # Or just use the array index since GitHub returns them in order
            color = day["color"]
            
            x = w_idx * CELL
            y = d_idx * CELL
            
            # Diagonal stagger based on x + y
            delay = (w_idx + d_idx) * 0.02
            
            parts.append(
                f'<rect class="box" x="{x}" y="{y}" width="{BOX_SIZE}" height="{BOX_SIZE}" '
                f'rx="2" fill="{color}" style="animation-delay: {delay:.2f}s" />'
            )
    
    parts.append('</g>')
    
    # Footer (Legend)
    footer_y = grid_y + 7 * CELL + 15
    legend_x = width - 150
    
    parts.append(f'<text x="{legend_x - 35}" y="{footer_y + 9}" fill="{TEXT_MUTED}" font-size="12">Less</text>')
    
    for i, color in enumerate(COLORS):
        parts.append(
            f'<rect x="{legend_x + i * CELL}" y="{footer_y}" width="{BOX_SIZE}" height="{BOX_SIZE}" '
            f'rx="2" fill="{color}" />'
        )
        
    parts.append(f'<text x="{legend_x + len(COLORS) * CELL + 5}" y="{footer_y + 9}" fill="{TEXT_MUTED}" font-size="12">More</text>')
                 
    parts.append("</svg>")
    
    svg_data = "".join(parts)
    
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w") as f:
        f.write(svg_data)
        
    print(f"wrote {OUT_FILE} {len(svg_data)} bytes; {width} x {height}")

if __name__ == "__main__":
    main()
