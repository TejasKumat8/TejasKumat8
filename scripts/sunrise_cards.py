"""Build the two data-driven profile cards.

contribution-city.svg: every building is a week of the last year, every
window is a day; lit windows are days with contributions.
ratings.svg: profile views drawn as TV viewer ratings, with a history chart.

Runs in GitHub Actions on a schedule. Uses only the standard library.
"""

import datetime as dt
import json
import os
import pathlib
import random
import re
import urllib.request

from fontkit import embed

USER = os.environ.get("PROFILE_USER", "TejasKumat8")
TOKEN = os.environ["GITHUB_TOKEN"]
ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
HISTORY = ROOT / "data" / "history.json"

EASE = 'calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1" fill="freeze"'
SANS = "font-family=\"'Rounded','Segoe UI',Arial,sans-serif\""


def fetch_calendar():
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount } }
          }
        }
      }
    }"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def fetch_views():
    # One read a day from the workflow may count as one extra view; close enough.
    url = f"https://komarev.com/ghpvc/?username={USER}&style=for-the-badge"
    req = urllib.request.Request(url, headers={"User-Agent": "sunrise-cards"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        svg = resp.read().decode()
    return int(re.search(r'aria-label="[^"]*?:\s*([\d,]+)"', svg).group(1).replace(",", ""))


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"]:
            current += 1
        elif i == 0:
            continue  # today isn't over yet
        else:
            break
    return current, longest


def protagonist(x, y, s):
    # the same rooftop character as the hero, sitting with laptop and chai
    return f'''<g transform="translate({x - 150 * s:.1f} {y - 318 * s:.1f}) scale({s})" fill="#1a0b1e">
    <ellipse cx="190" cy="294" rx="34" ry="26" fill="url(#screen)"/>
    <path d="M136 258 L131 245 L141 250 L142 237 L150 248 L157 236 L159 249 L168 243 L164 257Z"/>
    <circle cx="150" cy="262" r="13"/>
    <path d="M139 276 Q150 270 161 276 L165 320 L135 320Z"/>
    <path d="M158 283 L182 302" stroke="#1a0b1e" stroke-width="7" stroke-linecap="round"/>
    <path d="M140 310 L176 310 L176 322 L140 322Z"/>
    <path d="M166 318 L162 352 L171 352 L176 320Z"/><path d="M176 318 L178 350 L187 350 L186 318Z"/>
    <rect x="164" y="306" width="36" height="4" rx="1"/>
    <path d="M198 306 L207 283 L211 284 L202 307Z" fill="#ffd27a"/>
    <rect x="112" y="304" width="13" height="14" rx="2" fill="#e8a46a"/>
  </g>'''


def city_svg(cal):
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    totals = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    peak = max(totals) or 1
    best = totals.index(max(totals))
    nonzero = sorted(d["contributionCount"] for d in days if d["contributionCount"])
    q = [nonzero[int(len(nonzero) * f)] if nonzero else 1 for f in (0.25, 0.5, 0.75)]
    cur, longest = streaks(days)

    W, H, ground = 1000, 380, 318
    left, span = 40, 920
    step = span / len(weeks)
    bw = min(14, step - 3)
    rnd = random.Random(len(days))
    parts, wins = [], []
    roof_best = None
    for i, w in enumerate(weeks):
        x = left + i * step
        h = 58 + (totals[i] / peak) * 150
        top = ground - h
        t = 0.4 + i * 0.035
        parts.append(f'<rect x="{x:.1f}" y="{ground}" width="{bw:.1f}" height="0" fill="#2b1430">'
                     f'<animate attributeName="y" from="{ground}" to="{top:.1f}" begin="{t:.2f}s" dur="0.9s" {EASE}/>'
                     f'<animate attributeName="height" from="0" to="{h:.1f}" begin="{t:.2f}s" dur="0.9s" {EASE}/></rect>')
        wins.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{t + 0.8:.2f}s" dur="0.4s" fill="freeze"/>')
        if totals[i] and totals[i] >= sorted(totals)[-5]:
            wins.append(f'<rect x="{x + bw / 2 - 1:.1f}" y="{top - 12:.1f}" width="2" height="12" fill="#2b1430"/>')
            wins.append(f'<circle cx="{x + bw / 2:.1f}" cy="{top - 13:.1f}" r="2" fill="#ff5a5a">'
                         f'<animate attributeName="opacity" values="1;0.2;1" dur="{rnd.uniform(1.5, 3):.1f}s" repeatCount="indefinite"/></circle>')
        if i == best:
            roof_best = (x + bw / 2, top)
        for d_i, d in enumerate(w["contributionDays"]):
            c = d["contributionCount"]
            wy = ground - 6 - (7 - d_i) * 7
            if c == 0:
                fill, op = "#4a2446", 1
            elif c <= q[0]:
                fill, op = "#ffb066", 0.55
            elif c <= q[1]:
                fill, op = "#ffb066", 0.8
            elif c <= q[2]:
                fill, op = "#ffd27a", 1
            else:
                fill, op = "#fff1b8", 1
            anim = ""
            if c and rnd.random() < 0.25:
                anim = (f'<animate attributeName="opacity" values="{op};{op * 0.35:.2f};{op}" '
                        f'dur="{rnd.uniform(2.5, 6):.1f}s" begin="-{rnd.uniform(0, 5):.1f}s" repeatCount="indefinite"/>')
            wins.append(f'<rect x="{x + (bw - 8) / 2:.1f}" y="{wy}" width="8" height="5" fill="{fill}" opacity="{op}">{anim}</rect>')
        wins.append('</g>')
    landed = 0.4 + len(weeks) * 0.035 + 1.0
    stars = "".join(
        f'<circle cx="{rnd.randint(20, 980)}" cy="{rnd.randint(250, 370)}" r="{rnd.choice([1.5, 2])}" fill="#ffd9a0">'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;{rnd.randint(-30, 30)} -200" dur="{rnd.uniform(7, 12):.1f}s" begin="-{rnd.uniform(0, 10):.1f}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;0.9;0" dur="{rnd.uniform(7, 12):.1f}s" begin="-{rnd.uniform(0, 10):.1f}s" repeatCount="indefinite"/></circle>'
        for _ in range(12))

    if cur >= 7:
        caption = f"streak: {cur} days. the city never sleeps. neither does its mayor."
    elif cur >= 1:
        caption = "lights are on. someone's home. (it's me. I'm debugging.)"
    else:
        caption = "the city is quiet today. the mayor is reading docs. probably."

    bx, by = roof_best
    hero = protagonist(bx, by + 1, 0.42)
    first = dt.date.fromisoformat(weeks[best]["contributionDays"][0]["date"]).strftime("%b %d")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2a1840"/><stop offset="0.45" stop-color="#7a2f5e"/>
      <stop offset="0.75" stop-color="#e0595a"/><stop offset="1" stop-color="#ff9447"/>
    </linearGradient>
    <radialGradient id="sun" cx="50%" cy="45%" r="55%">
      <stop offset="0" stop-color="#fff6d5"/><stop offset="0.55" stop-color="#ffcf73"/><stop offset="1" stop-color="#ff8a3d"/>
    </radialGradient>
    <radialGradient id="halo" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#ffd38a" stop-opacity="0.6"/><stop offset="1" stop-color="#ff8a3d" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="screen" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#ffe3a3" stop-opacity="0.8"/><stop offset="1" stop-color="#ffb35c" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="comet" x1="1" x2="0"><stop offset="0" stop-color="#fff6d5"/><stop offset="1" stop-color="#fff6d5" stop-opacity="0"/></linearGradient>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  </defs>
  <g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#sky)"/>
  <g>
    <animateTransform attributeName="transform" type="translate" from="0 140" to="0 0" dur="3s" {EASE}/>
    <circle cx="800" cy="{ground}" r="170" fill="url(#halo)"><animate attributeName="r" values="160;185;160" dur="6s" repeatCount="indefinite"/></circle>
    <circle cx="800" cy="{ground}" r="92" fill="url(#sun)"/>
  </g>
  <g stroke="url(#comet)" stroke-width="2" stroke-linecap="round" opacity="0">
    <animate attributeName="opacity" values="0;1;0;0" keyTimes="0;0.05;0.12;1" dur="9s" begin="2s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="0 0;260 90;260 90" keyTimes="0;0.12;1" dur="9s" begin="2s" repeatCount="indefinite"/>
    <path d="M300 30 l-70 -24"/>
  </g>
  {stars}
  <path d="M0 {ground - 40} L120 {ground - 75} L260 {ground - 45} L400 {ground - 90} L560 {ground - 50} L700 {ground - 85} L860 {ground - 48} L1000 {ground - 70} V{ground} H0Z" fill="#8a3459" opacity="0.7"/>
  {''.join(parts)}
  {''.join(wins)}
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="{landed:.2f}s" dur="0.5s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" from="0 -40" to="0 0" begin="{landed:.2f}s" dur="0.7s" {EASE}/>
  {hero}
  <g {SANS}>
    <text x="{bx + (16 if bx < 600 else -16):.1f}" y="{by + 40:.1f}" text-anchor="{'start' if bx < 600 else 'end'}" font-size="12" fill="#fff0dc">{'← ' if bx < 600 else ''}best week ({first}): <tspan font-weight="800" fill="#ffc977">{max(totals)}</tspan>{'' if bx < 600 else ' →'}</text>
  </g>
  </g>
  <rect x="0" y="{ground}" width="{W}" height="{H - ground}" fill="#1c0b20"/>
  <g stroke="#ffb066" stroke-width="2" stroke-dasharray="18 14" opacity="0.5">
    <path d="M-40 {ground + 16} H1040"><animateTransform attributeName="transform" type="translate" values="0 0;-32 0" dur="1.2s" repeatCount="indefinite"/></path>
  </g>
  <g>
    <animateTransform attributeName="transform" type="translate" values="-60 0;1060 0" dur="14s" repeatCount="indefinite"/>
    <rect x="0" y="{ground + 6}" width="26" height="9" rx="3" fill="#ffb066"/>
    <rect x="5" y="{ground + 2}" width="14" height="6" rx="2" fill="#ffb066"/>
    <circle cx="27" cy="{ground + 10}" r="2" fill="#fff1b8"/>
  </g>
  <g {SANS} opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.8s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" from="-20 0" to="0 0" dur="0.8s" {EASE}/>
    <text x="40" y="52" font-size="22" font-weight="800" fill="#fff4e6">「contribution city」</text>
    <text x="44" y="76" font-size="13" fill="#ffd9b0" font-style="italic">every building is a week. every lit window is a day I shipped.</text>
    <text x="960" y="52" text-anchor="end" font-size="13" fill="#fff0dc"><tspan font-size="20" font-weight="800" fill="#ffc977">{cal["totalContributions"]}</tspan> contributions this year</text>
    <text x="960" y="76" text-anchor="end" font-size="13" fill="#ffd9b0">current streak <tspan font-weight="800" fill="#ffc977">{cur}d</tspan> · longest <tspan font-weight="800" fill="#ffc977">{longest}d</tspan></text>
    <text x="500" y="{H - 14}" text-anchor="middle" font-size="12" font-style="italic" fill="#c9a08a">{caption}</text>
  </g>
  </g>
</svg>
'''


TIERS = [
    (0, "indie pilot", "my mom watched. twice."),
    (100, "cult following", "small, loyal, slightly concerning."),
    (250, "seasonal hit", "renewed for another season."),
    (500, "prime time", "sponsors are calling. (they are not.)"),
    (1000, "legendary arc", "fans are writing theories about my commits."),
    (5000, "final form", "this README has its own fandom now."),
]


def ratings_svg(history):
    views = history["points"][-1]["views"]
    tier = [t for t in TIERS if views >= t[0]][-1]
    nxt = next((t for t in TIERS if t[0] > views), None)
    week_ago = (dt.date.fromisoformat(history["points"][-1]["date"]) - dt.timedelta(days=7)).isoformat()
    base = next((p["views"] for p in history["points"] if p["date"] >= week_ago), views)
    delta = views - base
    weekly = f"+{delta} this week" if len(history["points"]) > 1 else "premiere week"

    pts = history["points"][-30:]
    x0, x1, y0, y1 = 590, 950, 70, 170
    if len(pts) > 1:
        lo = min(p["views"] for p in pts)
        hi = max(p["views"] for p in pts)
        rng = (hi - lo) or 1
        coords = [(x0 + (x1 - x0) * i / (len(pts) - 1), y1 - (y1 - y0) * (p["views"] - lo) / rng) for i, p in enumerate(pts)]
        line = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
        chart = (f'<polygon points="{x0},{y1} {line} {x1},{y1}" fill="url(#area)" opacity="0">'
                 f'<animate attributeName="opacity" from="0" to="1" begin="2.2s" dur="0.8s" fill="freeze"/></polygon>'
                 f'<polyline points="{line}" fill="none" stroke="#ffc977" stroke-width="2.5" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
                 f'<animate attributeName="stroke-dashoffset" from="1" to="0" begin="0.6s" dur="1.8s" {EASE}/></polyline>'
                 f'<circle cx="{coords[-1][0]:.1f}" cy="{coords[-1][1]:.1f}" r="0" fill="#fff1b8">'
                 f'<animate attributeName="r" values="4;7;4" dur="2s" begin="2.4s" repeatCount="indefinite"/></circle>')
        note = f"ratings, last {len(pts)} readings"
    else:
        chart = (f'<path d="M{x0} {y1 - 20} H{x1}" stroke="#ffc977" stroke-width="2.5" stroke-dasharray="6 6">'
                 f'<animate attributeName="stroke-dashoffset" from="0" to="-24" dur="1s" repeatCount="indefinite"/></path>'
                 f'<circle cx="{x1}" cy="{y1 - 20}" r="5" fill="#fff1b8"><animate attributeName="r" values="4;7;4" dur="2s" repeatCount="indefinite"/></circle>')
        note = "the ratings chart premieres after the next broadcast"

    eq = "".join(
        f'<rect x="{306 + k * 7}" y="36" width="4" height="14" rx="1">'
        f'<animate attributeName="height" values="{a};14;{b};4;{a}" dur="{d}s" repeatCount="indefinite"/>'
        f'<animate attributeName="y" values="{50 - a};36;{50 - b};46;{50 - a}" dur="{d}s" repeatCount="indefinite"/></rect>'
        for k, (a, b, d) in enumerate([(6, 10, 0.9), (12, 5, 1.1), (4, 12, 0.8), (9, 6, 1.3), (11, 3, 1.0)]))
    to_next = f"{nxt[0] - views} more viewers until: {nxt[1]}" if nxt else "no higher tier exists. you broke the scale."

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="230" viewBox="0 0 1000 230">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#2a1520"/><stop offset="1" stop-color="#5a2340"/>
    </linearGradient>
    <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ff8a3d" stop-opacity="0.55"/><stop offset="1" stop-color="#ff8a3d" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
      <feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="band" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="card"><rect width="1000" height="230" rx="18"/></clipPath>
  </defs>
  <rect width="1000" height="230" rx="18" fill="url(#bg)"/>
  <rect width="1000" height="60" fill="url(#band)" clip-path="url(#card)">
    <animate attributeName="y" from="-60" to="230" dur="4.5s" repeatCount="indefinite"/>
  </rect>
  <g fill="none" stroke="#fff" stroke-width="1.5">
    <circle cx="58" cy="43" r="5"><animate attributeName="r" from="5" to="26" dur="1.8s" repeatCount="indefinite"/><animate attributeName="opacity" from="0.6" to="0" dur="1.8s" repeatCount="indefinite"/></circle>
    <circle cx="58" cy="43" r="5"><animate attributeName="r" from="5" to="26" dur="1.8s" begin="0.9s" repeatCount="indefinite"/><animate attributeName="opacity" from="0.6" to="0" dur="1.8s" begin="0.9s" repeatCount="indefinite"/></circle>
  </g>
  <g fill="#ffb066">{eq}</g>
  <g {SANS}>
    <rect x="40" y="30" width="92" height="26" rx="13" fill="#e0405a"/>
    <circle cx="58" cy="43" r="5" fill="#fff"><animate attributeName="opacity" values="1;0.2;1" dur="1.2s" repeatCount="indefinite"/></circle>
    <text x="70" y="48" font-size="13" font-weight="800" fill="#fff" letter-spacing="2">ON AIR</text>
    <text x="146" y="48" font-size="13" fill="#ffd9b0" letter-spacing="3">VIEWER RATINGS</text>
    <g opacity="0">
      <animate attributeName="opacity" from="0" to="1" begin="0.2s" dur="0.6s" fill="freeze"/>
      <animateTransform attributeName="transform" type="translate" from="0 26" to="0 0" begin="0.2s" dur="0.8s" {EASE}/>
      <text x="38" y="128" font-size="72" font-weight="800" fill="#fff4e6" filter="url(#glow)">{views:,}<animate attributeName="opacity" values="1;0.85;1;0.92;1" dur="3s" repeatCount="indefinite"/></text>
    </g>
    <text x="42" y="156" font-size="14" fill="#ffd9b0">people watched the pilot · <tspan fill="#ffc977" font-weight="700">{weekly}</tspan></text>
    <text x="42" y="190" font-size="13" fill="#fff0dc">status: <tspan font-weight="800" fill="#ffb066">{tier[1]}</tspan> <tspan font-style="italic" fill="#c9a08a">· {tier[2]}</tspan></text>
    <text x="42" y="210" font-size="11" fill="#b58a7c">{to_next}</text>
    <path d="M{x0} {y1} H{x1}" stroke="#7a3d55" stroke-width="1"/>
    {chart}
    <text x="{x1}" y="{y1 + 26}" text-anchor="end" font-size="11" font-style="italic" fill="#b58a7c">{note}</text>
  </g>
</svg>
'''


def main():
    cal = fetch_calendar()
    history = json.loads(HISTORY.read_text()) if HISTORY.exists() else {"points": []}
    views = fetch_views()
    today = dt.date.today().isoformat()
    point = {"date": today, "views": views, "contributions": cal["totalContributions"]}
    if history["points"] and history["points"][-1]["date"] == today:
        history["points"][-1] = point
    else:
        history["points"].append(point)
    history["points"] = history["points"][-120:]

    ASSETS.mkdir(exist_ok=True)
    HISTORY.parent.mkdir(exist_ok=True)
    HISTORY.write_text(json.dumps(history, indent=1))
    (ASSETS / "contribution-city.svg").write_text(embed(city_svg(cal)), encoding="utf-8")
    (ASSETS / "ratings.svg").write_text(embed(ratings_svg(history)), encoding="utf-8")
    print(f"views={point['views']} contributions={cal['totalContributions']}")


if __name__ == "__main__":
    main()
