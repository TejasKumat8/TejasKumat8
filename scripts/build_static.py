"""Build the static sunrise assets: hero, episode headers, footer."""

import pathlib
import random

from fontkit import embed

random.seed(7)
out = pathlib.Path(__file__).resolve().parent.parent / "assets"
out.mkdir(parents=True, exist_ok=True)
W, H = 1000, 380

# skyline buildings with twinkling windows
bld, win = [], []
x = 300
while x < W:
    w = random.choice([34, 42, 50, 58, 66])
    h = random.randint(40, 105)
    y = H - h
    bld.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#2b1430"/>')
    if random.random() < 0.3:
        bld.append(f'<rect x="{x + w//2 - 1}" y="{y-14}" width="2" height="14" fill="#2b1430"/>')
    for wy in range(y + 8, H - 6, 12):
        for wx in range(x + 6, x + w - 8, 10):
            if random.random() < 0.22:
                d = round(random.uniform(2.5, 6), 1)
                b = round(random.uniform(0, 5), 1)
                win.append(f'<rect x="{wx}" y="{wy}" width="4" height="5" fill="#ffc46b" opacity="0.85">'
                           f'<animate attributeName="opacity" values="0.85;0.2;0.85" dur="{d}s" begin="-{b}s" repeatCount="indefinite"/></rect>')
    x += w + random.choice([0, 2, 4])

# embers drifting up
emb = []
for i in range(16):
    ex = random.randint(20, 980); ey = random.randint(250, 380)
    dx = random.randint(-40, 40); dur = round(random.uniform(7, 13), 1); b = round(random.uniform(0, 12), 1)
    r = random.choice([1.5, 2, 2.5])
    emb.append(f'<circle cx="{ex}" cy="{ey}" r="{r}" fill="#ffd9a0">'
               f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} -220" dur="{dur}s" begin="-{b}s" repeatCount="indefinite"/>'
               f'<animate attributeName="opacity" values="0;0.9;0" dur="{dur}s" begin="-{b}s" repeatCount="indefinite"/></circle>')

rays = "".join(f'<path d="M760 300 L{760-14} -200 L{760+14} -200Z" transform="rotate({a} 760 300)"/>' for a in range(-80, 81, 16))

hero = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2a1840"/>
      <stop offset="0.35" stop-color="#7a2f5e"/>
      <stop offset="0.62" stop-color="#e0595a"/>
      <stop offset="0.82" stop-color="#ff9447"/>
      <stop offset="1" stop-color="#ffc977"/>
    </linearGradient>
    <radialGradient id="sun" cx="50%" cy="45%" r="55%">
      <stop offset="0" stop-color="#fff6d5"/>
      <stop offset="0.55" stop-color="#ffcf73"/>
      <stop offset="1" stop-color="#ff8a3d"/>
    </radialGradient>
    <radialGradient id="halo" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#ffd38a" stop-opacity="0.75"/>
      <stop offset="1" stop-color="#ff8a3d" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="screen" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#ffe3a3" stop-opacity="0.8"/>
      <stop offset="1" stop-color="#ffb35c" stop-opacity="0"/>
    </radialGradient>
    <mask id="stripes">
      <rect width="{W}" height="{H}" fill="#fff"/>
      <rect x="600" y="248" width="320" height="4" fill="#000"/>
      <rect x="600" y="262" width="320" height="6" fill="#000"/>
      <rect x="600" y="278" width="320" height="8" fill="#000"/>
    </mask>
    <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="soft"><feGaussianBlur stdDeviation="6"/></filter>
    <clipPath id="typeClip">
      <rect x="40" y="186" height="24" width="0">
        <animate attributeName="width" values="0;520;520;0" keyTimes="0;0.45;0.92;1" dur="10s" repeatCount="indefinite"/>
      </rect>
    </clipPath>
    <style>
      .sans {{ font-family: 'Rounded','Rounded','Segoe UI',Arial,sans-serif; }}
      .mono {{ font-family: 'Code','JetBrains Mono',Consolas,monospace; }}
    </style>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#sky)"/>

  <g fill="#fff1c9" opacity="0.07">
    <animateTransform attributeName="transform" type="rotate" from="0 760 300" to="16 760 300" dur="12s" repeatCount="indefinite"/>
    {rays}
  </g>

  <g>
  <animateTransform attributeName="transform" type="translate" from="0 120" to="0 0" dur="3.5s" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1" fill="freeze"/>
  <circle cx="760" cy="300" r="190" fill="url(#halo)">
    <animate attributeName="r" values="180;205;180" dur="6s" repeatCount="indefinite"/>
  </circle>
  <circle cx="760" cy="300" r="105" fill="url(#sun)" mask="url(#stripes)"/>
  </g>
  <g stroke="#fff6d5" stroke-width="2" stroke-linecap="round" opacity="0">
    <animate attributeName="opacity" values="0;1;0;0" keyTimes="0;0.04;0.1;1" dur="11s" begin="3s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="0 0;240 80;240 80" keyTimes="0;0.1;1" dur="11s" begin="3s" repeatCount="indefinite"/>
    <path d="M560 40 l-60 -20" opacity="0.8"/>
  </g>

  <g fill="#ffd9b8" opacity="0.55" filter="url(#soft)">
    <g>
      <animateTransform attributeName="transform" type="translate" values="-260 0;1100 0" dur="70s" begin="-25s" repeatCount="indefinite"/>
      <ellipse cx="0" cy="92" rx="80" ry="14"/><ellipse cx="40" cy="84" rx="44" ry="14"/>
    </g>
    <g>
      <animateTransform attributeName="transform" type="translate" values="-200 0;1100 0" dur="90s" begin="-60s" repeatCount="indefinite"/>
      <ellipse cx="0" cy="150" rx="110" ry="12"/><ellipse cx="-30" cy="143" rx="50" ry="11"/>
    </g>
    <g>
      <animateTransform attributeName="transform" type="translate" values="-200 0;1100 0" dur="80s" begin="-5s" repeatCount="indefinite"/>
      <ellipse cx="0" cy="210" rx="90" ry="10"/>
    </g>
  </g>

  <g fill="none" stroke="#3a1a3a" stroke-width="2" stroke-linecap="round">
    <g>
      <animateTransform attributeName="transform" type="translate" values="560 120;1060 70" dur="22s" repeatCount="indefinite"/>
      <path d="M0 0q6 -6 12 0q6 -6 12 0"/><path d="M22 12q5 -5 10 0q5 -5 10 0"/><path d="M-14 14q5 -5 10 0q5 -5 10 0"/>
    </g>
  </g>

  <path d="M0 290 L80 250 L170 280 L260 232 L360 275 L470 240 L560 280 L650 252 L760 287 L860 246 L1000 282 V380 H0Z" fill="#c9566f" opacity="0.75"/>
  <path d="M0 322 L120 292 L220 316 L340 288 L450 318 L590 293 L700 322 L820 298 L930 318 L1000 306 V380 H0Z" fill="#8a3459"/>

  {''.join(bld)}
  {''.join(win)}

  <rect x="0" y="322" width="290" height="58" fill="#3b1a3d"/>
  <rect x="0" y="318" width="290" height="6" fill="#1c0b20"/>

  <g fill="#1a0b1e">
    <ellipse cx="190" cy="294" rx="34" ry="26" fill="url(#screen)">
      <animate attributeName="opacity" values="1;0.7;1" dur="3s" repeatCount="indefinite"/>
    </ellipse>
    <path d="M136 258 L131 245 L141 250 L142 237 L150 248 L157 236 L159 249 L168 243 L164 257Z"/>
    <circle cx="150" cy="262" r="13"/>
    <path d="M139 276 Q150 270 161 276 L165 320 L135 320Z"/>
    <path d="M158 283 L182 302" stroke="#1a0b1e" stroke-width="7" stroke-linecap="round"/>
    <path d="M140 310 L176 310 L176 322 L140 322Z"/>
    <path d="M166 318 L162 352 L171 352 L176 320Z"/><path d="M176 318 L178 350 L187 350 L186 318Z"/>
    <rect x="164" y="306" width="36" height="4" rx="1"/>
    <path d="M198 306 L207 283 L211 284 L202 307Z" fill="#ffd27a"/>
    <rect x="102" y="304" width="13" height="14" rx="2" fill="#e8a46a"/>
    <path d="M115 307 q6 3 0 7" fill="none" stroke="#e8a46a" stroke-width="2"/>
  </g>
  <g fill="none" stroke="#fff0dc" stroke-width="1.6" stroke-linecap="round">
    <path d="M106 298 q-4 -6 0 -12 q4 -6 0 -12">
      <animate attributeName="opacity" values="0;0.8;0" dur="3s" repeatCount="indefinite"/>
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -8" dur="3s" repeatCount="indefinite"/>
    </path>
    <path d="M111 296 q-4 -6 0 -12 q4 -6 0 -12">
      <animate attributeName="opacity" values="0;0.8;0" dur="3s" begin="-1.5s" repeatCount="indefinite"/>
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -8" dur="3s" begin="-1.5s" repeatCount="indefinite"/>
    </path>
  </g>

  {''.join(emb)}

  <text x="42" y="66" class="sans" font-size="15" fill="#ffd9b0" letter-spacing="3">おはよう, world ☀</text>
  <text x="38" y="132" class="sans" font-size="60" font-weight="800" fill="#fff4e6" letter-spacing="2" filter="url(#glow)">Tejas Kumat</text>
  <text x="42" y="164" class="sans" font-size="16" fill="#ffe3c7" letter-spacing="3">backend &amp; AI engineer · Bengaluru</text>
  <g clip-path="url(#typeClip)">
    <text x="42" y="203" class="mono" font-size="13" fill="#fff0dc">&gt; up at 5am. not for the grind. the build was failing.</text>
  </g>
</svg>
'''
(out / "hero.svg").write_text(embed(hero), encoding="utf-8")

sections = [
    ("EP.01", "the protagonist", "a backend dev who refuses to write bad code"),
    ("EP.02", "side quests", "that accidentally became main quests"),
    ("EP.03", "training arc", "power-ups collected so far"),
    ("EP.04", "world building", "I build a city every year. one commit at a time."),
    ("EP.00", "the ratings", "live audience numbers. no bots. (probably.)"),
]
EASE = 'calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1" fill="freeze"'
FONT = "font-family=\"'Rounded','Segoe UI',Arial,sans-serif\""
for i, (ep, title, sub) in enumerate(sections):
    tw = 30 + len(title) * 15.5
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="104" viewBox="0 0 1000 104">
  <defs>
    <linearGradient id="card" x1="0" x2="1">
      <stop offset="0" stop-color="#4a1d3a"/><stop offset="0.45" stop-color="#2a1520"/><stop offset="1" stop-color="#2a1520" stop-opacity="0.6"/>
    </linearGradient>
    <linearGradient id="tag" x1="0" x2="1">
      <stop offset="0" stop-color="#ffb347"/><stop offset="1" stop-color="#e0595a"/>
    </linearGradient>
    <linearGradient id="brush" x1="0" x2="1">
      <stop offset="0" stop-color="#ffc977"/><stop offset="0.6" stop-color="#ff8a3d"/><stop offset="1" stop-color="#e0595a" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="shine" x1="0" x2="1">
      <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#ffe3c7" stop-opacity="0.12"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="frame"><rect x="0" y="6" width="1000" height="92" rx="20"/></clipPath>
  </defs>
  <rect x="0" y="6" width="1000" height="92" rx="20" fill="url(#card)"/>
  <rect x="-260" y="6" width="220" height="92" fill="url(#shine)" clip-path="url(#frame)">
    <animate attributeName="x" values="-260;1040;1040" keyTimes="0;0.55;1" dur="6s" begin="{i * 0.8}s" repeatCount="indefinite"/>
  </rect>

  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.6s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" from="-30 0" to="0 0" dur="0.8s" {EASE}/>
    <path d="M28 30 H128 L116 74 H16 Z" fill="url(#tag)"/>
    <path d="M28 30 H128 L126 36 H26 Z" fill="#fff" opacity="0.25"/>
    <text x="72" y="60" text-anchor="middle" {FONT} font-size="19" font-weight="800" font-style="italic" fill="#fff8ee" letter-spacing="1">{ep}</text>
  </g>

  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="0.15s" dur="0.6s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" begin="0.15s" dur="0.8s" {EASE}/>
    <text x="150" y="52" {FONT} font-size="28" font-weight="800" fill="#fff4e6"><tspan fill="#ff9a4d">「</tspan>{title}<tspan fill="#ff9a4d">」</tspan></text>
    <text x="154" y="82" {FONT} font-size="14" fill="#d9b3a0">{sub}</text>
  </g>
  <path d="M156 62 Q{150 + tw / 2:.0f} 66 {150 + tw:.0f} 60" fill="none" stroke="url(#brush)" stroke-width="4" stroke-linecap="round"
        pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">
    <animate attributeName="stroke-dashoffset" from="1" to="0" begin="0.5s" dur="0.9s" {EASE}/>
  </path>

  <g transform="translate(944 52)">
    <circle r="22" fill="#ffb347" opacity="0.18"><animate attributeName="r" values="18;26;18" dur="4s" repeatCount="indefinite"/></circle>
    <circle r="13" fill="#ffc977"/>
    <rect x="-14" y="3" width="28" height="2" fill="#2a1520"/>
    <rect x="-14" y="8" width="28" height="3" fill="#2a1520"/>
  </g>
  <g fill="#fff1c9">
    <path d="M894 30 l2 6 6 2 -6 2 -2 6 -2 -6 -6 -2 6 -2z"><animate attributeName="opacity" values="0;1;0" dur="2.6s" begin="{i * 0.3}s" repeatCount="indefinite"/></path>
    <path d="M980 78 l1.5 4 4 1.5 -4 1.5 -1.5 4 -1.5 -4 -4 -1.5 4 -1.5z"><animate attributeName="opacity" values="0;1;0" dur="3.1s" begin="{1 + i * 0.3}s" repeatCount="indefinite"/></path>
    <path d="M912 80 l1 3 3 1 -3 1 -1 3 -1 -3 -3 -1 3 -1z"><animate attributeName="opacity" values="0;1;0" dur="2.2s" begin="{0.5 + i * 0.3}s" repeatCount="indefinite"/></path>
  </g>
</svg>
"""
    (out / f"ep{int(ep[3:])}.svg").write_text(embed(svg), encoding="utf-8")

footer = '''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="140" viewBox="0 0 1000 140">
  <defs>
    <linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2a1520"/><stop offset="1" stop-color="#5a2340"/>
    </linearGradient>
  </defs>
  <rect width="1000" height="140" rx="12" fill="url(#dusk)"/>
  <g font-family="'Rounded','Segoe UI',Arial,sans-serif">
    <text x="480" y="62" text-anchor="middle" font-size="30" font-weight="800" font-style="italic" fill="#ffb066" letter-spacing="2">to be continued<animate attributeName="opacity" values="1;0.6;1" dur="2.5s" repeatCount="indefinite"/></text>
    <path d="M610 40 h30 l12 12 l-12 12 h-30z" fill="#ffb066">
      <animateTransform attributeName="transform" type="translate" values="0 0;10 0;0 0" dur="1.2s" repeatCount="indefinite"/>
    </path>
    <text x="500" y="98" text-anchor="middle" font-size="14" fill="#f3d5c0">next episode: <tspan font-style="italic" fill="#ffc977">"the PR gets merged."</tspan></text>
    <text x="500" y="122" text-anchor="middle" font-size="11" fill="#b58a7c" letter-spacing="1">(no filler episodes. only commits.)</text>
  </g>
</svg>
'''
(out / "footer.svg").write_text(embed(footer), encoding="utf-8")
print("ok")
