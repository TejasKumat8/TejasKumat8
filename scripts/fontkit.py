"""Embed web fonts into an SVG.

GitHub shows README SVGs as images, and images can't load external fonts,
so the font files go inside the SVG as data URIs. Google Fonts' `text=`
parameter returns only the glyphs we use, which keeps each file small.
"""

import base64
import html
import re
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")

FAMILIES = {
    "Rounded": ("M PLUS Rounded 1c", "400;800"),
    "Code": ("M PLUS 1 Code", "500"),
}


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def _faces(alias, family, weights, text):
    query = urllib.parse.urlencode({"family": f"{family}:wght@{weights}", "text": text})
    css = _get(f"https://fonts.googleapis.com/css2?{query}").decode()
    faces = []
    for weight, url, fmt in re.findall(
            r"font-weight:\s*(\d+);\s*src:\s*url\(([^)]+)\)\s*format\('([^']+)'\)", css):
        data = base64.b64encode(_get(url)).decode()
        mime = "font/woff2" if fmt == "woff2" else "font/ttf"
        faces.append(f"@font-face{{font-family:'{alias}';font-weight:{weight};"
                     f"src:url(data:{mime};base64,{data}) format('{fmt}');}}")
    return faces


def embed(svg):
    text = html.unescape("".join(re.findall(r">([^<]+)<", svg)))
    text = "".join(sorted(set(text + "0123456789")))
    faces = []
    for alias, (family, weights) in FAMILIES.items():
        if f"'{alias}'" in svg:
            faces += _faces(alias, family, weights, text)
    style = f"<style>{''.join(faces)}</style>"
    if "<defs>" in svg:
        return svg.replace("<defs>", "<defs>" + style, 1)
    return re.sub(r"(<svg[^>]*>)", r"\1<defs>" + style + "</defs>", svg, count=1)
