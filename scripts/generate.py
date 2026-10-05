#!/usr/bin/env python3
"""Generate the animated SVG visuals for the GitHub profile README.

Run from the repository root (stdlib only, no installs):
    python scripts/generate.py

Reads profile.json and writes, for both the dark and the light theme:
    assets/banner-<theme>.svg
    assets/whoami-<theme>.svg
    assets/<radar.file>-<theme>.svg

The README swaps themes with <picture> + prefers-color-scheme.
"""

from __future__ import annotations

import json
import math
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

MONO = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, monospace"
SANS = "'Segoe UI', Inter, -apple-system, Helvetica, Arial, sans-serif"

THEMES = {
    "dark": {
        "bg": "#0B1020",
        "panel": "#10172B",
        "panel2": "#151E38",
        "line": "#24304D",
        "grid": "#1A2442",
        "muted": "#7D8AA8",
        "text": "#E6ECF8",
        "cyan": "#61DAFB",
        "violet": "#A78BFA",
        "mint": "#34D399",
        "amber": "#FBBF24",
        "pink": "#F472B6",
    },
    "light": {
        "bg": "#F7F9FC",
        "panel": "#FFFFFF",
        "panel2": "#EEF3FA",
        "line": "#D5DEEB",
        "grid": "#E6ECF5",
        "muted": "#5E6B85",
        "text": "#0F172A",
        "cyan": "#0891B2",
        "violet": "#7C3AED",
        "mint": "#059669",
        "amber": "#B45309",
        "pink": "#DB2777",
    },
}

# Shared CSS: one-shot reveal for lines, infinite blink for the cursor.
BASE_CSS = """
.reveal{opacity:0;animation:reveal .55s cubic-bezier(.22,1,.36,1) forwards}
@keyframes reveal{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}
.cursor{animation:blink 1.05s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.pulse{animation:pulse 2.4s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
"""


def svg_open(w: int, h: int, title: str, desc: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
        f'height="{h}" role="img" aria-labelledby="t d">'
        f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
    )


def frame(w: int, h: int, c: dict) -> str:
    """Rounded card with a faint dot grid and a gradient border."""
    return (
        "<defs>"
        f'<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">'
        f'<stop stop-color="{c["cyan"]}"/><stop offset="1" stop-color="{c["violet"]}"/>'
        "</linearGradient>"
        f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{c["grid"]}"/></pattern>'
        "</defs>"
        f'<rect width="{w}" height="{h}" rx="18" fill="{c["bg"]}"/>'
        f'<rect width="{w}" height="{h}" rx="18" fill="url(#dots)"/>'
        f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="17" fill="none" '
        f'stroke="url(#edge)" stroke-width="2" opacity=".85"/>'
    )


def text(x, y, s, fill, size, family=MONO, weight=400, extra="") -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" {extra}>{escape(s)}</text>'
    )


def tokens(x, y, parts, c, size=15, cls="", delay=0.0) -> str:
    """One line of syntax-coloured code from (text, colour-key) pairs."""
    spans = "".join(f'<tspan fill="{c[k]}">{escape(s)}</tspan>' for s, k in parts)
    style = f' class="{cls}" style="animation-delay:{delay:.2f}s"' if cls else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" '
        f'xml:space="preserve"{style}>{spans}</text>'
    )


# --------------------------------------------------------------------------- #
# Banner


def platform_icon(kind: str, x: float, y: float, color: str) -> str:
    s = f'fill="none" stroke="{color}" stroke-width="1.6" stroke-linejoin="round"'
    if kind == "web":
        return (f'<rect x="{x}" y="{y}" width="18" height="14" rx="2.5" {s}/>'
                f'<path d="M{x} {y + 4}h18" {s}/>')
    if kind == "mobile":
        return (f'<rect x="{x + 4}" y="{y - 1}" width="10" height="16" rx="2.5" {s}/>'
                f'<path d="M{x + 7.5} {y + 12}h3" {s}/>')
    return (f'<rect x="{x}" y="{y}" width="18" height="11" rx="2" {s}/>'
            f'<path d="M{x + 6} {y + 15}h6M{x + 9} {y + 11}v4" {s}/>')


def banner(p: dict, c: dict) -> str:
    W, H = 960, 320
    out = [svg_open(W, H, f'{p["name"]} — {p["role"]}',
                    "Animated banner: name, role, a code snippet and a React atom "
                    "connected to web, mobile and desktop."),
           f"<style>{BASE_CSS}</style>", frame(W, H, c)]

    out.append(
        f'<defs><linearGradient id="name" x1="0" x2="1">'
        f'<stop stop-color="{c["cyan"]}"/><stop offset="1" stop-color="{c["violet"]}"/>'
        f"</linearGradient></defs>"
    )
    out.append(text(48, 62, "// hola, soy", c["muted"], 15,
                    extra='class="reveal"'))
    out.append(text(46, 114, p["name"], "url(#name)", 50, SANS, 800,
                    'letter-spacing="-1" class="reveal" style="animation-delay:.15s"'))
    out.append(text(48, 148, f'{p["role"]}  ·  {p["tagline"]}', c["text"], 18, SANS, 500,
                    'class="reveal" style="animation-delay:.3s"'))
    out.append(f'<path d="M48 172H560" stroke="{c["line"]}"/>')

    code = [
        [("const ", "violet"), ("engineer", "cyan"), (" = {", "text")],
        [("  stack", "text"), (": [", "muted"), ("'React'", "mint"), (", ", "muted"),
         ("'React Native'", "mint"), (", ", "muted"), ("'TypeScript'", "mint"), ("],", "muted")],
        [("  ships", "text"), (": [", "muted"), ("'web'", "amber"), (", ", "muted"),
         ("'mobile'", "amber"), (", ", "muted"), ("'desktop'", "amber"), ("],", "muted")],
        [("  focus", "text"), (": ", "muted"), ("'scalable frontend architecture'", "pink"),
         (",", "muted")],
        [("};", "text")],
    ]
    for i, parts in enumerate(code):
        out.append(tokens(48, 204 + i * 22, parts, c, 15, "reveal", 0.6 + i * 0.28))
    out.append(f'<rect class="cursor" x="74" y="279" width="9" height="18" fill="{c["cyan"]}"/>')

    # React atom wired to the three platforms; dots travel along each wire.
    cx, cy = 790, 168
    nodes = [("web", 676, 58, "cyan"), ("mobile", 904, 58, "violet"),
             ("desktop", 790, 284, "mint")]
    for i, (label, nx, ny, key) in enumerate(nodes):
        out.append(
            f'<path id="w{i}" d="M{cx} {cy}L{nx} {ny}" stroke="{c[key]}" stroke-width="1.4" '
            f'stroke-dasharray="4 6" opacity=".55">'
            f'<animate attributeName="stroke-dashoffset" from="20" to="0" dur="1s" '
            f'repeatCount="indefinite"/></path>'
        )
        out.append(
            f'<circle r="3.2" fill="{c[key]}"><animateMotion dur="2.4s" '
            f'begin="{i * 0.8:.1f}s" repeatCount="indefinite"><mpath href="#w{i}"/>'
            f"</animateMotion></circle>"
        )
    out.append(f'<g><animateTransform attributeName="transform" type="rotate" '
               f'from="0 {cx} {cy}" to="360 {cx} {cy}" dur="22s" repeatCount="indefinite"/>')
    for angle in (0, 60, 120):
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="74" ry="27" fill="none" '
                   f'stroke="{c["cyan"]}" stroke-width="2.2" '
                   f'transform="rotate({angle} {cx} {cy})"/>')
    out.append("</g>")
    out.append(f'<circle cx="{cx}" cy="{cy}" r="34" fill="{c["bg"]}" opacity=".7"/>')
    out.append(f'<circle class="pulse" cx="{cx}" cy="{cy}" r="9" fill="{c["cyan"]}"/>')

    for label, nx, ny, key in nodes:
        w = 52 + len(label) * 8.4
        x0 = nx - w / 2
        out.append(f'<rect x="{x0:.1f}" y="{ny - 16}" width="{w:.1f}" height="32" rx="16" '
                   f'fill="{c["panel2"]}" stroke="{c[key]}" stroke-width="1.4"/>')
        out.append(platform_icon(label, x0 + 14, ny - 7, c[key]))
        out.append(text(round(x0 + 40, 1), ny + 5, label, c["text"], 14))
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------- #
# whoami terminal card


def whoami(p: dict, c: dict) -> str:
    W, H = 960, 360
    out = [svg_open(W, H, f'{p["name"]} — whoami',
                    "Terminal card with location, current role, mission, focus areas "
                    "and headline metrics."),
           f"<style>{BASE_CSS}</style>", frame(W, H, c)]
    for i, col in enumerate(("pink", "amber", "mint")):
        out.append(f'<circle cx="{32 + i * 19}" cy="32" r="5.5" fill="{c[col]}"/>')
    out.append(text(102, 37, f'~/{p["handle"]}  ·  zsh', c["muted"], 14))
    out.append(f'<path d="M24 56H936" stroke="{c["line"]}"/>')

    # left: shell session
    d = 0.2
    rows = [
        (90, [("❯ ", "mint"), ("whoami", "cyan")], 18),
        (122, [(p["handle"], "text"), ("  —  ", "muted"), (p["role"], "amber")], 17),
        (162, [("location ", "muted"), (p["location"], "violet")], 15),
        (188, [("now      ", "muted"), (p["current"], "text")], 15),
        (214, [("mission  ", "muted"), (p["mission"], "mint")], 15),
        (256, [("❯ ", "mint"), ("ls ", "cyan"), ("focus/", "text")], 18),
    ]
    for y, parts, size in rows:
        out.append(tokens(44, y, parts, c, size, "reveal", d))
        d += 0.22
    palette = ("cyan", "violet", "pink", "amber", "mint", "cyan")
    for i, item in enumerate(p["focus"]):
        x = 44 + (i % 3) * 210
        y = 290 + (i // 3) * 28
        out.append(tokens(x, y, [(item, palette[i % len(palette)])], c, 15, "reveal",
                          d + i * 0.08))
    out.append(f'<rect class="cursor" x="44" y="{290 + 2 * 28 - 6}" width="9" height="17" '
               f'fill="{c["cyan"]}"/>')

    # right: metrics panel
    px, py, pw, ph = 664, 76, 272, 262
    out.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" '
               f'fill="{c["panel"]}" stroke="{c["line"]}"/>')
    out.append(text(px + 20, py + 30, "status", c["muted"], 13))
    out.append(f'<circle class="pulse" cx="{px + 26}" cy="{py + 52}" r="5" fill="{c["mint"]}"/>')
    out.append(text(px + 40, py + 57, "open to connect", c["mint"], 15, weight=600))
    out.append(f'<path d="M{px + 20} {py + 76}H{px + pw - 20}" stroke="{c["line"]}"/>')
    accents = ("cyan", "violet", "amber")
    for i, m in enumerate(p["metrics"]):
        y = py + 116 + i * 52
        out.append(text(px + 20, y, m["value"], c[accents[i % 3]], 30, SANS, 800,
                        f'class="reveal" style="animation-delay:{1.2 + i * 0.2:.1f}s"'))
        anim = f'class="reveal" style="animation-delay:{1.3 + i * 0.2:.1f}s"'
        out.append(text(px + 84, y - 12, m["label"], c["text"], 14, SANS, 600, anim))
        out.append(text(px + 84, y + 6, m.get("sub", ""), c["muted"], 12, SANS, 400, anim))
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------- #
# Radar


def radar(title: str, axes: list[dict], c: dict, size: int = 440) -> str:
    n = len(axes)
    r = size * 0.30
    cx, cy = size / 2, size / 2 + 18
    W, H = size, size + 24

    def pt(i: int, radius: float) -> tuple[float, float]:
        a = math.radians(-90 + i * 360 / n)
        return cx + radius * math.cos(a), cy + radius * math.sin(a)

    out = [svg_open(W, H, title, f"Radar chart: {title}"), frame(W, H, c)]
    out.append(text(W / 2, 40, title, c["text"], 16, SANS, 700, 'text-anchor="middle"'))
    for k in range(4, 0, -1):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, r * k / 4) for i in range(n)))
        out.append(f'<polygon points="{pts}" fill="none" stroke="{c["line"]}" '
                   f'opacity="{0.4 + 0.15 * k:.2f}"/>')
    for i in range(n):
        x, y = pt(i, r)
        out.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{y:.1f}" '
                   f'stroke="{c["line"]}"/>')

    shape = [pt(i, r * a["value"] / 100) for i, a in enumerate(axes)]
    local = " ".join(f"{x - cx:.1f},{y - cy:.1f}" for x, y in shape)
    out.append(
        f'<defs><linearGradient id="fill" x1="0" y1="0" x2="1" y2="1">'
        f'<stop stop-color="{c["cyan"]}"/><stop offset="1" stop-color="{c["violet"]}"/>'
        f"</linearGradient></defs>"
        f'<g transform="translate({cx:.1f},{cy:.1f})"><g>'
        f'<animateTransform attributeName="transform" type="scale" values="0.05;1" dur="1.1s" '
        f'calcMode="spline" keyTimes="0;1" keySplines="0.22 1 0.36 1" fill="freeze"/>'
        f'<polygon points="{local}" fill="url(#fill)" fill-opacity=".25" stroke="{c["cyan"]}" '
        f'stroke-width="2.4" stroke-linejoin="round"/>'
    )
    for x, y in shape:
        out.append(f'<circle cx="{x - cx:.1f}" cy="{y - cy:.1f}" r="3.8" fill="{c["bg"]}" '
                   f'stroke="{c["cyan"]}" stroke-width="2"/>')
    out.append("</g></g>")

    for i, a in enumerate(axes):
        x, y = pt(i, r + 22)
        dx = x - cx
        anchor = "middle" if abs(dx) < 8 else ("start" if dx > 0 else "end")
        y += 4 if y > cy else 0
        out.append(text(round(x, 1), round(y, 1), a["label"], c["text"], 13, SANS, 600,
                        f'text-anchor="{anchor}"'))
        out.append(text(round(x, 1), round(y + 16, 1), str(a["value"]), c["muted"], 12,
                        extra=f'text-anchor="{anchor}"'))
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------- #


def main() -> None:
    profile = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
    ASSETS.mkdir(exist_ok=True)
    for theme, c in THEMES.items():
        files = {
            f"banner-{theme}.svg": banner(profile, c),
            f"whoami-{theme}.svg": whoami(profile, c),
        }
        for rd in profile["radars"]:
            files[f'{rd["file"]}-{theme}.svg'] = radar(rd["title"], rd["axes"], c)
        for name, svg in files.items():
            (ASSETS / name).write_text(svg, encoding="utf-8")
            print(f"wrote assets/{name}")


if __name__ == "__main__":
    main()
