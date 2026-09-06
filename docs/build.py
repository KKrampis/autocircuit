#!/usr/bin/env python3
"""
build.py — Convert docs/content.md into docs/index.html and docs/presentation.html.
Run: python3 docs/build.py   (from repo root)
"""
import re, sys, textwrap
from pathlib import Path
try:
    import yaml
    import markdown as md_lib
except ImportError:
    print("Installing dependencies…")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "markdown"])
    import yaml
    import markdown as md_lib

HERE   = Path(__file__).parent          # docs/
ROOT   = HERE.parent                    # repo root
SRC    = HERE / "content.md"
SITE   = HERE / "index.html"
PRES   = HERE / "presentation.html"

# ─────────────────────────────────────────────────────────────────────────────
# SVG / HTML figure fragments (keyed by figure id in content.md)
# ─────────────────────────────────────────────────────────────────────────────
FIGURES = {}

FIGURES["fig-analogy-task"] = """
<svg viewBox="0 0 680 200" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:680px;display:block;margin:0 auto;">
  <defs><marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L0,6 L6,3 z" class="svg-arrow"/></marker></defs>
  <rect x="10" y="60" width="100" height="40" rx="6" class="svg-box-blue"/>
  <text x="60" y="85" text-anchor="middle" font-family="DM Mono,monospace" font-size="13" class="svg-text-main">Paris</text>
  <line x1="110" y1="80" x2="170" y2="80" stroke-width="1.5" class="svg-divider" marker-end="url(#arr)"/>
  <rect x="170" y="60" width="110" height="40" rx="6" class="svg-box-blue"/>
  <text x="225" y="80" text-anchor="middle" font-family="DM Mono,monospace" font-size="13" class="svg-text-main">France</text>
  <text x="140" y="72" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="10" class="svg-text-muted">capital-of</text>
  <text x="160" y="140" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="11" font-style="italic" class="svg-text-muted">Known pair</text>
  <line x1="340" y1="40" x2="340" y2="160" stroke-width="1" stroke-dasharray="4,3" class="svg-divider"/>
  <rect x="370" y="60" width="100" height="40" rx="6" class="svg-box-blue"/>
  <text x="420" y="85" text-anchor="middle" font-family="DM Mono,monospace" font-size="13" class="svg-text-main">Berlin</text>
  <line x1="470" y1="80" x2="530" y2="80" stroke-width="1.5" stroke-dasharray="5,3" class="svg-divider" marker-end="url(#arr)"/>
  <rect x="530" y="60" width="120" height="40" rx="6" class="svg-box-orange"/>
  <text x="590" y="85" text-anchor="middle" font-family="DM Mono,monospace" font-size="13" class="svg-text-orange">Germany?</text>
  <text x="500" y="72" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="10" class="svg-text-muted">capital-of?</text>
  <text x="520" y="140" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="11" font-style="italic" class="svg-text-muted">To complete</text>
  <text x="60" y="20" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="11" class="svg-text-blue">GIVEN</text>
  <text x="520" y="20" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="11" class="svg-text-orange">QUERY</text>
</svg>"""

FIGURES["fig-layer-distribution"] = """
<svg viewBox="0 0 600 160" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:600px;display:block;margin:0 auto;">
  <text x="10" y="20" font-family="DM Sans,sans-serif" font-size="12" font-weight="600" class="svg-text-muted">Core features by layer group (all 5/5 graphs)</text>
  <text x="60" y="50" text-anchor="end" font-family="DM Mono,monospace" font-size="10" class="svg-bar-label">L0</text>
  <rect x="65" y="38" width="192" height="18" rx="3" class="svg-bar-blue" opacity="0.8"/>
  <text x="262" y="50" font-family="DM Mono,monospace" font-size="10" class="svg-text-muted">12</text>
  <text x="60" y="78" text-anchor="end" font-family="DM Mono,monospace" font-size="10" class="svg-bar-label">L1-L4</text>
  <rect x="65" y="66" width="304" height="18" rx="3" class="svg-bar-blue" opacity="0.8"/>
  <text x="374" y="78" font-family="DM Mono,monospace" font-size="10" class="svg-text-muted">19</text>
  <text x="60" y="106" text-anchor="end" font-family="DM Mono,monospace" font-size="10" class="svg-bar-label">L5-L6</text>
  <rect x="65" y="94" width="192" height="18" rx="3" class="svg-bar-orange" opacity="0.9"/>
  <text x="262" y="106" font-family="DM Mono,monospace" font-size="10" class="svg-text-muted">12</text>
  <text x="60" y="134" text-anchor="end" font-family="DM Mono,monospace" font-size="10" class="svg-bar-label">L8-L13</text>
  <rect x="65" y="122" width="112" height="18" rx="3" class="svg-bar-purple" opacity="0.9"/>
  <text x="182" y="134" font-family="DM Mono,monospace" font-size="10" class="svg-text-muted">7</text>
</svg>"""

FIGURES["fig-circuit-flow"] = """
<div style="max-width:560px;margin:0 auto;">
  <div class="phase-input">Representative recurring SAE features</div>
  <div class="phase-box phase-1">
    <div class="phase-label phase-label-1">Group 1 &middot; Concentrated at layers 0&#x2013;4 &middot; Template-word labels</div>
    <div class="phase-feature"><strong>SAE L0/F11651</strong> &mdash; <em>"the word 'to'"</em></div>
    <div class="phase-feature"><strong>SAE L1/F11356</strong> &mdash; <em>"the word 'to' followed by a verb"</em></div>
    <div class="phase-feature"><strong>SAE L4/F10752</strong> &mdash; <em>"uses of the verb 'to be' preceded by 'to'"</em></div>
    <div class="phase-feature"><strong>SAE L5/F9672</strong> &mdash; <em>"the phrase 'it is to'"</em></div>
  </div>
  <div class="phase-box phase-2">
    <div class="phase-label phase-label-2">Group 2 &middot; Concentrated at layers 5&#x2013;9 &middot; Analogy-related labels</div>
    <div class="phase-feature"><strong>SAE L5/F5793</strong> &mdash; <em><span class="smoking-gun">"analogies"</span></em></div>
    <div class="phase-feature"><strong>SAE L5/F2141</strong> &mdash; <em>"comparisons of well-known figures"</em></div>
    <div class="phase-feature"><strong>SAE L8/F13766</strong> &mdash; <em>"analogies or comparisons"</em></div>
    <div class="phase-feature"><strong>SAE L9/F13344</strong> &mdash; <em>"comparison between two things"</em></div>
  </div>
  <div class="phase-box phase-3">
    <div class="phase-label phase-label-3">Group 3 &middot; Concentrated at layers 10&#x2013;13 &middot; Relationship-related labels</div>
    <div class="phase-feature"><strong>SAE L13/F10969</strong> &mdash; <em>"comparisons between disciplines and relationships between concepts"</em></div>
  </div>
</div>"""

FIGURES["fig-venn"] = """
<svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:640px;display:block;margin:1em auto;">
  <!-- outer ring: 510 features active in ≥3/5 graphs -->
  <ellipse cx="220" cy="130" rx="165" ry="110" class="svg-circle-blue" opacity="0.18"/>
  <ellipse cx="420" cy="130" rx="165" ry="110" class="svg-circle-purple" opacity="0.18"/>
  <!-- mid ring: 277 features active in ≥4/5 graphs -->
  <ellipse cx="220" cy="130" rx="118" ry="78" class="svg-circle-blue" opacity="0.28"/>
  <ellipse cx="420" cy="130" rx="118" ry="78" class="svg-circle-purple" opacity="0.28"/>
  <!-- inner core: 180 features active in all 5/5 graphs -->
  <ellipse cx="320" cy="130" rx="72" ry="58" style="fill:var(--green)" opacity="0.55"/>
  <!-- circle outlines -->
  <ellipse cx="220" cy="130" rx="165" ry="110" fill="none" stroke-width="1.5" class="svg-divider" opacity="0.5"/>
  <ellipse cx="420" cy="130" rx="165" ry="110" fill="none" stroke-width="1.5" class="svg-divider" opacity="0.5"/>
  <!-- Labels: circle titles -->
  <text x="110" y="55" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="12" font-weight="700" class="svg-text-blue">Capital</text>
  <text x="110" y="70" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="12" font-weight="700" class="svg-text-blue">Analogies</text>
  <text x="110" y="86" text-anchor="middle" font-family="DM Mono,monospace" font-size="9" class="svg-text-muted">Berlin · Rome · Tokyo</text>
  <text x="530" y="55" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="12" font-weight="700" class="svg-text-purple">Semantic Role</text>
  <text x="530" y="70" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="12" font-weight="700" class="svg-text-purple">Analogies</text>
  <text x="530" y="86" text-anchor="middle" font-family="DM Mono,monospace" font-size="9" class="svg-text-muted">Teacher · Bird</text>
  <!-- ≥3/5 label (outer) -->
  <text x="150" y="215" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="10" class="svg-text-blue" opacity="0.85">510 features</text>
  <text x="150" y="228" text-anchor="middle" font-family="DM Mono,monospace" font-size="9" class="svg-text-muted">active in ≥3/5 graphs</text>
  <!-- ≥4/5 label -->
  <text x="320" y="222" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="10" class="svg-text-purple" opacity="0.85">277 features</text>
  <text x="320" y="235" text-anchor="middle" font-family="DM Mono,monospace" font-size="9" class="svg-text-muted">active in ≥4/5 graphs</text>
  <!-- Core 180 label -->
  <text x="320" y="116" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="13" font-weight="700" class="svg-text-green">180 features</text>
  <text x="320" y="131" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="10" class="svg-text-green">active in all 5/5 graphs</text>
  <text x="320" y="147" text-anchor="middle" font-family="DM Mono,monospace" font-size="8" class="svg-text-muted">incl. L5#5793 "analogies"</text>
  <text x="320" y="159" text-anchor="middle" font-family="DM Mono,monospace" font-size="8" class="svg-text-muted">L8#13766 "analogies or comparisons"</text>
</svg>"""

FIGURES["fig-activation"] = """
<svg viewBox="0 0 580 110" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:580px;display:block;margin:0 auto;">
  <text x="5"   y="22"  font-family="DM Mono,monospace" font-size="9" class="svg-bar-label">L0 structural</text>
  <rect x="115" y="10"  width="130" height="15" rx="3" class="svg-bar-blue" opacity="0.8"/>
  <text x="250" y="22"  font-family="DM Mono,monospace" font-size="9" class="svg-text-muted">1.5&#x2013;6.4</text>
  <text x="5"   y="48"  font-family="DM Mono,monospace" font-size="9" class="svg-bar-label">L5 analogy hub</text>
  <rect x="115" y="36"  width="230" height="15" rx="3" class="svg-bar-orange" opacity="0.85"/>
  <text x="350" y="48"  font-family="DM Mono,monospace" font-size="9" class="svg-text-muted">7.4&#x2013;11.1</text>
  <text x="5"   y="74"  font-family="DM Mono,monospace" font-size="9" class="svg-bar-label">L8&#x2013;L9 detectors</text>
  <rect x="115" y="62"  width="275" height="15" rx="3" style="fill:var(--green)" opacity="0.85"/>
  <text x="395" y="74"  font-family="DM Mono,monospace" font-size="9" class="svg-text-muted">~13.4</text>
  <text x="5"   y="100" font-family="DM Mono,monospace" font-size="9" class="svg-bar-label">L10&#x2013;L13 integr.</text>
  <rect x="115" y="88"  width="340" height="15" rx="3" class="svg-bar-purple" opacity="0.85"/>
  <text x="460" y="100" font-family="DM Mono,monospace" font-size="9" class="svg-text-muted">9.1&#x2013;16.3</text>
</svg>"""


# ─────────────────────────────────────────────────────────────────────────────
# Parsing helpers
# ─────────────────────────────────────────────────────────────────────────────

def parse_frontmatter(text):
    """Split YAML frontmatter from body. Returns (meta_dict, body_str)."""
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)), text[m.end():]


def md_to_html(text):
    """Convert markdown to HTML. Protects $$...$$ math blocks from markdown mangling."""
    placeholders = {}
    def save_math(m):
        key = f'MATHBLOCK{len(placeholders)}ENDMATH'
        placeholders[key] = f'<div class="math-display">\\[{m.group(1)}\\]</div>'
        return f'\n\n{key}\n\n'
    text = re.sub(r'\$\$(.+?)\$\$', save_math, text, flags=re.DOTALL)

    html = md_lib.markdown(text, extensions=["tables", "fenced_code", "nl2br", "attr_list"])

    for key, val in placeholders.items():
        html = html.replace(f'<p>{key}</p>', val)
        html = html.replace(key, val)
    return html


def resolve_figures(html):
    """Replace <!-- figure:id --> placeholders with the actual SVG/HTML."""
    def replace(m):
        fig_id = m.group(1).strip()
        if fig_id in FIGURES:
            return f'<div class="max-width-content figure-block">{FIGURES[fig_id]}'
        return m.group(0)
    # Match both HTML-comment and blockquote-style figure refs the md parser may produce
    html = re.sub(r'<!-- figure:([\w-]+) -->', replace, html)
    # The markdown renderer may turn <!-- figure:x --> into a paragraph; handle that too
    html = re.sub(r'<p><!-- figure:([\w-]+) --></p>', replace, html)
    # Close the wrapping div after the next paragraph (the caption)
    html = re.sub(r'(</div>)\s*(<p><strong>Figure)', r'\1\n</div>\2', html)
    html = re.sub(r'(<div class="max-width-content figure-block">.*?</p>)',
                  lambda x: x.group(0) + '\n</div>' if '</div>' not in x.group(0) else x.group(0),
                  html, flags=re.DOTALL)
    return html


def split_slides(body):
    """
    Split body on <!-- slide: Title --> markers.
    Returns list of (title, markdown_content) tuples.
    The first item has title=None (pre-slide content, used for abstract etc.).
    """
    pattern = re.compile(r'<!-- slide:\s*(.*?)\s*-->', re.IGNORECASE)
    parts = pattern.split(body)
    # parts alternates: [pre, title1, content1, title2, content2, ...]
    slides = [(None, parts[0])]
    it = iter(parts[1:])
    for title in it:
        content = next(it, "")
        slides.append((title, content))
    return slides


# ─────────────────────────────────────────────────────────────────────────────
# Website generator
# ─────────────────────────────────────────────────────────────────────────────

SITE_CSS = """
<style>
:root {
  --bg:#0d1117;--bg2:#161b22;--bg3:#21262d;--border:#30363d;
  --text:#c9d1d9;--text-muted:#8b949e;--link:#58a6ff;
  --green:#3fb950;--orange:#e67e22;--purple:#8854d0;
  --phase1-bg:rgba(230,126,34,0.10);--phase2-bg:rgba(88,166,255,0.10);
  --phase3-bg:rgba(136,84,208,0.10);--finding-bg:rgba(63,185,80,0.10);
  --finding-bdr:#3fb950;--smoking-bg:rgba(249,168,37,0.15);
  --smoking-bdr:#d29922;--code-bg:#161b22;
  --svg-box-blue-fill:rgba(88,166,255,0.12);--svg-box-blue-stroke:#58a6ff;
  --svg-box-orange-fill:rgba(230,126,34,0.12);--svg-box-orange-stroke:#e67e22;
  --svg-text:var(--text);--svg-text-muted:var(--text-muted);
  --svg-text-blue:var(--link);--svg-text-orange:var(--orange);
  --svg-bar-blue:var(--link);--svg-bar-orange:var(--orange);
  --svg-bar-purple:var(--purple);--svg-bar-label:var(--text-muted);
}
[data-theme="light"] {
  --bg:#fff;--bg2:#f6f8fa;--bg3:#eaeef2;--border:#d0d7de;
  --text:#1f2328;--text-muted:#57606a;--link:#0969da;
  --green:#1a7f37;--orange:#bc4c00;--purple:#6639ba;
  --phase1-bg:#fff9f5;--phase2-bg:#f5f9ff;--phase3-bg:#f9f5ff;
  --finding-bg:#f6fff8;--finding-bdr:#1a7f37;
  --smoking-bg:#fffde7;--smoking-bdr:#f9a825;--code-bg:#eaeef2;
  --svg-box-blue-fill:#f0f4ff;--svg-box-blue-stroke:#3273dc;
  --svg-box-orange-fill:#fff9e6;--svg-box-orange-stroke:#e67e22;
  --svg-text:#1a1a1a;--svg-text-muted:#555;
  --svg-text-blue:#3273dc;--svg-text-orange:#bc4c00;
  --svg-bar-blue:#3273dc;--svg-bar-orange:#e67e22;
  --svg-bar-purple:#8854d0;--svg-bar-label:#555;
}
html{font-size:12pt;}
body{font-family:'DM Sans',sans-serif!important;color:var(--text);background:var(--bg);transition:background .2s,color .2s;}
a{color:var(--link);}
code,pre{font-family:'DM Mono',monospace!important;background:var(--code-bg)!important;color:var(--link)!important;}
.hero{background:var(--bg)!important;}
.section{background:var(--bg)!important;}
.footer{background:var(--bg2)!important;color:var(--text-muted);}
.footer a{color:var(--link);}
.title{color:var(--text)!important;}
.content{color:var(--text);}
.content h2,.content h3,.content h4{color:var(--text)!important;}
.content p,.content li{color:var(--text);}
.content strong{color:var(--text);}
.content blockquote{border-left:4px solid var(--finding-bdr);background:var(--finding-bg);padding:12px 16px;margin:12px 0;border-radius:0 6px 6px 0;}
.content blockquote p{margin:0;color:var(--text);}
.table{background:var(--bg2)!important;color:var(--text)!important;border-color:var(--border)!important;}
.table thead th{background:var(--bg3)!important;color:var(--text-muted)!important;border-color:var(--border)!important;}
.table td,.table th{border-color:var(--border)!important;color:var(--text)!important;}
.table.is-hoverable tbody tr:hover{background:var(--bg3)!important;}
hr.section-divider{background-color:var(--border);height:1px;border:none;width:90vw;margin:0 auto;}
.max-width-content{max-width:70vw;margin:0 auto;}
.figure-block{margin:20px auto;}
.figure-caption{color:var(--text-muted);font-size:.9em;margin-top:10px;line-height:1.5;}
.figure-number{font-weight:700;color:var(--text);}
.publication-links .link-block{margin:5px;display:inline-block;}
#theme-toggle{position:fixed;top:14px;right:18px;z-index:9999;background:var(--bg2);border:1px solid var(--border);color:var(--text);border-radius:20px;padding:5px 14px;font-family:'DM Sans',sans-serif;font-size:.78em;cursor:pointer;display:flex;align-items:center;gap:6px;transition:background .2s,border-color .2s;}
#theme-toggle:hover{border-color:var(--link);color:var(--link);}
.phase-box{border-radius:6px;padding:14px 18px;margin:8px 0;}
.phase-input{background:var(--bg3);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:12px 18px;font-family:'DM Mono',monospace;font-size:.9em;text-align:center;}
.phase-output{background:var(--bg3);color:var(--green);border:1px solid var(--border);border-radius:6px;padding:12px 18px;font-family:'DM Mono',monospace;font-size:.9em;text-align:center;}
.phase-1{border-left:4px solid var(--orange);background:var(--phase1-bg);}
.phase-2{border-left:4px solid var(--link);background:var(--phase2-bg);}
.phase-3{border-left:4px solid var(--purple);background:var(--phase3-bg);}
.phase-label{font-size:.75em;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;}
.phase-label-1{color:var(--orange);}
.phase-label-2{color:var(--link);}
.phase-label-3{color:var(--purple);}
.phase-feature{font-family:'DM Mono',monospace;font-size:.8em;color:var(--text);margin:2px 0;}
.phase-arrow{text-align:center;font-size:1.8em;color:var(--text-muted);line-height:1.2;margin:2px 0;}
.smoking-gun{background:var(--smoking-bg);border:2px solid var(--smoking-bdr);border-radius:4px;padding:2px 6px;font-weight:700;color:var(--text);}
.svg-box-blue{fill:var(--svg-box-blue-fill);stroke:var(--svg-box-blue-stroke);stroke-width:1.5;}
.svg-box-orange{fill:var(--svg-box-orange-fill);stroke:var(--svg-box-orange-stroke);stroke-width:1.5;}
.svg-text-main{fill:var(--svg-text);}
.svg-text-muted{fill:var(--svg-text-muted);}
.svg-text-blue{fill:var(--svg-text-blue);font-weight:600;}
.svg-text-orange{fill:var(--svg-text-orange);font-weight:600;}
.svg-text-green{fill:var(--green);font-weight:700;}
.svg-text-purple{fill:var(--purple);font-weight:600;}
.svg-divider{stroke:var(--border);}
.svg-arrow{fill:var(--text-muted);}
.svg-bar-blue{fill:var(--svg-bar-blue);}
.svg-bar-orange{fill:var(--svg-bar-orange);}
.svg-bar-purple{fill:var(--svg-bar-purple);}
.svg-bar-label{fill:var(--svg-bar-label);}
.svg-circle-blue{fill:rgba(88,166,255,0.12);stroke:#58a6ff;stroke-width:2;}
.svg-circle-purple{fill:rgba(136,84,208,0.12);stroke:#8854d0;stroke-width:2;}
[data-theme="light"] .svg-circle-blue{fill:rgba(50,115,220,0.12);stroke:#3273dc;}
[data-theme="light"] .svg-circle-purple{fill:rgba(136,84,208,0.12);stroke:#8854d0;}
.supp-card{border:1px solid var(--border);border-radius:8px;padding:20px;background:var(--bg2);}
.supp-card p{color:var(--text-muted);}
</style>"""


def build_hero(meta):
    authors_html = " &nbsp;<span style='color:var(--text-muted)'>·</span>&nbsp; ".join(
        f'<span class="author-block" style="margin:0 8px;">'
        f'<a href="{a["url"]}" target="_blank" style="color:var(--link);">{a["name"]}</a></span>'
        for a in meta.get("authors", [])
    )
    link_items = []
    for l in meta.get("links", []):
        is_external = not l["url"].startswith("#") and not l["url"].endswith(".html")
        target = ' target="_blank"' if is_external else ""
        link_items.append(
            f'<span class="link-block"><a href="{l["url"]}" class="external-link button is-normal is-rounded is-dark"{target}>'
            f'<span class="icon"><i class="{l["icon"]}"></i></span><span>{l["label"]}</span></a></span>'
        )
    links_html = "\n".join(link_items)
    return f"""
<section class="hero">
  <div class="hero-body" style="padding:3rem 1.5rem 0.5rem 1.5rem;">
    <div class="container is-max-desktop">
      <div class="columns is-centered">
        <div class="column has-text-centered">
          <h1 class="title is-2">{meta.get('title','')}</h1>
          <div class="is-size-5 publication-authors">{authors_html}</div>
          <div class="is-size-5" style="margin-top:4px;color:var(--text-muted);">
            {meta.get('date','')} &nbsp;·&nbsp; Mechanistic Interpretability
          </div>
          <div class="column has-text-centered" style="margin-top:16px;">
            <div class="publication-links">{links_html}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
<hr class="section-divider">"""


def build_abstract(meta, body_html):
    # Extract just the Abstract section HTML
    m = re.search(r'<h2[^>]*>Abstract</h2>(.*?)(?=<h2|\Z)', body_html, re.DOTALL)
    content = m.group(1).strip() if m else ""
    tldr = meta.get("tldr", "")
    tldr_html = md_to_html(tldr) if tldr else ""
    return f"""
<section class="section" style="padding-top:1.5rem;">
  <div class="container is-max-desktop">
    <div class="columns is-centered has-text-centered">
      <div class="column is-four-fifths">
        <div class="content has-text-left"><p><b>TLDR:</b> {tldr_html.replace('<p>','').replace('</p>','')}</p></div>
        <br>
        <h2 class="title is-4">Abstract</h2>
        <div class="content has-text-left">{content}</div>
      </div>
    </div>
  </div>
</section>
<hr class="section-divider">"""


def build_sections(body_html):
    """Wrap each top-level section (## heading) in a <section> block."""
    # Split on <h2> tags
    chunks = re.split(r'(<h2[^>]*>.*?</h2>)', body_html, flags=re.DOTALL)
    out = []
    i = 0
    skip_titles = {"Abstract", "Supplementary Materials", "BibTeX"}
    while i < len(chunks):
        chunk = chunks[i]
        if re.match(r'<h2', chunk):
            title_text = re.sub(r'<[^>]+>', '', chunk)
            if title_text.strip() in skip_titles:
                i += 2
                continue
            content = chunks[i+1] if i+1 < len(chunks) else ""
            out.append(f"""
<section class="section" style="padding-top:1rem;">
  <div class="container is-max-desktop">
    <div class="content">
      {chunk}
      {content}
    </div>
  </div>
</section>
<hr class="section-divider">""")
            i += 2
        else:
            i += 1
    return "\n".join(out)


def build_supplementary(meta):
    cards = []
    for s in meta.get("supplementary", []):
        sublinks = ""
        if "sublinks" in s:
            items = "\n".join(
                f'<li style="margin:4px 0;"><a href="{sl["url"]}" target="_blank"><code>{sl["label"]}</code></a> &mdash; {sl["desc"]}</li>'
                for sl in s["sublinks"]
            )
            sublinks = f'<ul style="font-size:.85em;list-style:none;padding:0;margin:8px 0;">{items}</ul>'
        cards.append(f"""
    <div class="column">
      <div class="supp-card">
        <p style="font-size:1em;font-weight:700;margin-bottom:8px;color:var(--text);"><i class="{s['icon']}" style="margin-right:8px;"></i>{s['label']}</p>
        <p style="font-size:.9em;">{s['description']}</p>
        {sublinks}
        <a href="{s['url']}" class="button is-normal is-rounded is-dark" style="margin-top:12px;"{'  target="_blank"' if not s['url'].endswith('.html') else ''}>
          <span class="icon"><i class="{s['icon']}"></i></span><span>{s['label']}</span>
        </a>
      </div>
    </div>""")
    return f"""
<section class="section" style="padding-top:1rem;">
  <div class="container is-max-desktop">
    <h2 class="title is-4">Supplementary Materials</h2>
    <div class="content">
      <div class="columns">{''.join(cards)}</div>
    </div>
  </div>
</section>
<hr class="section-divider">"""


def build_bibtex(meta):
    bib = meta.get("bibtex", "")
    return f"""
<section class="section" style="padding-top:1rem;">
  <div class="container is-max-desktop content">
    <h2 class="title is-4">BibTeX</h2>
    <pre><code>{bib.strip()}</code></pre>
  </div>
</section>"""


def render_site(meta, body):
    body_html = md_to_html(body)
    body_html = resolve_figures(body_html)
    # Make tables Bulma-styled
    body_html = body_html.replace('<table>', '<table class="table is-bordered is-hoverable has-text-left">')

    toggle_js = """
<button id="theme-toggle" onclick="toggleTheme()" title="Toggle light/dark mode">
  <span id="theme-icon">&#9728;&#65039;</span>
  <span id="theme-label">Light mode</span>
</button>
<script>
function toggleTheme(){
  var h=document.documentElement,d=h.getAttribute('data-theme')==='dark';
  h.setAttribute('data-theme',d?'light':'dark');
  document.getElementById('theme-icon').textContent=d?'🌙':'☀️';
  document.getElementById('theme-label').textContent=d?'Dark mode':'Light mode';
  localStorage.setItem('theme',d?'light':'dark');
}
(function(){
  var s=localStorage.getItem('theme')||'dark';
  document.documentElement.setAttribute('data-theme',s);
  document.addEventListener('DOMContentLoaded',function(){
    var d=s==='dark';
    document.getElementById('theme-icon').textContent=d?'☀️':'🌙';
    document.getElementById('theme-label').textContent=d?'Light mode':'Dark mode';
  });
})();
</script>"""

    parts = [
        '<!DOCTYPE html>',
        '<html lang="en" data-theme="dark">',
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{meta.get("title","")}</title>',
        f'<meta name="description" content="{meta.get("tldr","").strip()}">',
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">',
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">',
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/jpswalsh/academicons@1/css/academicons.min.css">',
        '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">',
        SITE_CSS,
        '<style>.math-display{overflow-x:auto;padding:0.5em 0;text-align:center;}</style>',
        '<script>MathJax={tex:{inlineMath:[["$","$"],["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]]},svg:{fontCache:"global"}};</script>',
        '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>',
        '</head>',
        '<body>',
        toggle_js,
        build_hero(meta),
        build_abstract(meta, body_html),
        build_sections(body_html),
        build_supplementary(meta),
        build_bibtex(meta),
        '<footer class="footer"><div class="container"><div class="columns is-centered"><div class="column is-8"><div class="content has-text-centered">',
        '<p>Website template based on the <a href="https://nerfies.github.io" target="_blank">Nerfies</a> and <a href="https://latentqa.github.io" target="_blank">LatentQA</a> project pages.</p>',
        '</div></div></div></div></footer>',
        '</body></html>',
    ]
    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Presentation generator
# ─────────────────────────────────────────────────────────────────────────────

PRES_CSS = """
<style>
:root{--gh-bg:#0d1117;--gh-bg2:#161b22;--gh-border:#30363d;--gh-text:#c9d1d9;
--gh-muted:#8b949e;--gh-blue:#58a6ff;--gh-green:#3fb950;--gh-orange:#d29922;
--gh-purple:#bc8cff;--gh-red:#f85149;}
.reveal-viewport{background:var(--gh-bg)!important;}
.reveal{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:var(--gh-text);font-size:22px;}
.reveal h1,.reveal h2,.reveal h3{color:var(--gh-text);text-transform:none;letter-spacing:-.5px;}
.reveal h1{color:var(--gh-blue);font-size:1.6em;}
.reveal h2{color:var(--gh-blue);font-size:1.15em;border-bottom:1px solid var(--gh-border);padding-bottom:.25em;margin-bottom:.5em;}
.reveal h3{color:var(--gh-purple);font-size:.95em;}
.reveal section{background:var(--gh-bg);}
.reveal .slides section{padding:16px 36px;}
.card{background:var(--gh-bg2);border:1px solid var(--gh-border);border-radius:6px;padding:10px 14px;margin:6px 0;}
.tag{display:inline-block;padding:2px 8px;border-radius:12px;font-size:.7em;font-weight:600;font-family:monospace;margin:2px;}
.tag-blue{background:rgba(88,166,255,.15);color:var(--gh-blue);border:1px solid rgba(88,166,255,.3);}
.tag-green{background:rgba(63,185,80,.15);color:var(--gh-green);border:1px solid rgba(63,185,80,.3);}
.tag-orange{background:rgba(210,153,34,.15);color:var(--gh-orange);border:1px solid rgba(210,153,34,.3);}
.tag-purple{background:rgba(188,140,255,.15);color:var(--gh-purple);border:1px solid rgba(188,140,255,.3);}
table{width:100%;border-collapse:collapse;font-size:.68em;}
th{background:var(--gh-bg2);color:var(--gh-muted);padding:5px 8px;border:1px solid var(--gh-border);text-align:left;font-weight:600;text-transform:uppercase;letter-spacing:.5px;}
td{padding:5px 8px;border:1px solid var(--gh-border);color:var(--gh-text);}
tr:nth-child(even) td{background:rgba(22,27,34,.5);}
code,.mono{font-family:'SFMono-Regular',Consolas,monospace;font-size:.82em;background:var(--gh-bg2);padding:1px 4px;border-radius:3px;color:var(--gh-blue);}
.flow-box{background:var(--gh-bg2);border:1px solid var(--gh-border);border-radius:6px;padding:8px 12px;margin:3px 0;text-align:center;}
.flow-box.phase1{border-color:var(--gh-orange);background:rgba(210,153,34,.06);}
.flow-box.phase2{border-color:var(--gh-blue);background:rgba(88,166,255,.06);}
.flow-box.phase3{border-color:var(--gh-purple);background:rgba(188,140,255,.06);}
.flow-arrow{text-align:center;color:var(--gh-muted);font-size:1em;margin:1px 0;line-height:1;}
.highlight{color:var(--gh-blue);font-weight:600;}
.muted{color:var(--gh-muted);font-size:.8em;}
.finding{border-left:3px solid var(--gh-green);padding-left:10px;margin:6px 0;font-size:.78em;}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:10px;}
.three-col{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;}
.big-number{font-size:2em;font-weight:700;color:var(--gh-blue);display:block;}
.big-label{font-size:.65em;color:var(--gh-muted);}
ul{margin:0;padding-left:1.1em;}
li{margin:3px 0;font-size:.78em;}
.reveal .progress{color:var(--gh-blue);}
.reveal .slide-number{color:var(--gh-muted);font-size:.75em;}
.phase-label{font-size:.6em;font-weight:700;letter-spacing:1px;text-transform:uppercase;}
.pres-svg{width:100%;max-height:180px;display:block;margin:6px auto;}
/* SVG tokens (same variables reused) */
.svg-box-blue{fill:rgba(88,166,255,.12);stroke:#58a6ff;stroke-width:1.5;}
.svg-box-orange{fill:rgba(210,153,34,.12);stroke:#d29922;stroke-width:1.5;}
.svg-text-main{fill:#c9d1d9;}.svg-text-muted{fill:#8b949e;}
.svg-text-blue{fill:#58a6ff;font-weight:600;}.svg-text-orange{fill:#d29922;font-weight:600;}
.svg-text-green{fill:#3fb950;font-weight:700;}.svg-text-purple{fill:#bc8cff;font-weight:600;}.svg-divider{stroke:#30363d;}
.svg-arrow{fill:#8b949e;}.svg-bar-blue{fill:#3273dc;}.svg-bar-orange{fill:#d29922;}
.svg-bar-purple{fill:#bc8cff;}.svg-bar-label{fill:#8b949e;}
.svg-circle-blue{fill:rgba(88,166,255,.12);stroke:#58a6ff;stroke-width:1.8;}
.svg-circle-purple{fill:rgba(188,140,255,.12);stroke:#bc8cff;stroke-width:1.8;}
</style>"""


def slide_title_slide(meta):
    tags = " ".join([
        '<span class="tag tag-blue">Gemma-2-2B</span>',
        '<span class="tag tag-green">gemmascope-transcoder-16k</span>',
        '<span class="tag tag-purple">Neuronpedia API</span>',
        '<span class="tag tag-orange">5 Attribution Graphs</span>',
    ])
    authors = " &nbsp;·&nbsp; ".join(
        f'<a href="{a["url"]}" target="_blank" style="color:#58a6ff;">{a["name"]}</a>'
        for a in meta.get("authors", [])
    )
    return f"""
<section data-background-color="#0d1117">
  <div style="padding:30px 20px;">
    <div class="tag tag-blue" style="font-size:.8em;margin-bottom:16px;">Mechanistic Interpretability &middot; {meta.get('date','')}</div>
    <h1 style="font-size:1.5em;line-height:1.2;margin:12px 0 16px;">{meta.get('title','')}<br>
    <span style="color:#c9d1d9;font-size:.7em;">{meta.get('subtitle','')}</span></h1>
    <p style="color:#8b949e;font-size:.85em;margin:8px 0;">{authors}</p>
    <div style="margin-top:20px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap;">{tags}</div>
  </div>
</section>"""


def md_chunk_to_slide_html(title, content):
    """Convert a slide's markdown content to reveal-friendly HTML."""
    # Convert markdown
    html = md_to_html(content)
    html = resolve_figures(html)
    # Style tables
    html = html.replace('<table>', '<table>')
    # Add pres-svg class to SVGs
    html = html.replace('<svg ', '<svg class="pres-svg" ')
    # Wrap blockquotes as finding boxes
    html = html.replace('<blockquote>', '<div class="finding">')
    html = html.replace('</blockquote>', '</div>')
    return f"""
<section data-background-color="#0d1117">
  <h2>{title}</h2>
  <div style="overflow:auto;max-height:85vh;">
    {html}
  </div>
</section>"""


def render_presentation(meta, body):
    slides_raw = split_slides(body)
    sections = [slide_title_slide(meta)]

    for title, content in slides_raw:
        content = content.strip()
        if not content:
            continue
        if title is None:
            # Pre-slide content — render as "Key Findings" summary slide
            # Extract first blockquote or bullet list as the highlight
            html = md_to_html(content)
            html = resolve_figures(html)
            html = html.replace('<blockquote>', '<div class="finding">').replace('</blockquote>', '</div>')
            sections.append(f"""
<section data-background-color="#0d1117">
  <h2>Overview</h2>
  <div style="overflow:auto;max-height:85vh;">{html}</div>
</section>""")
        else:
            sections.append(md_chunk_to_slide_html(title, content))

    slides_html = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta.get('title','')} — Presentation</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/black.css">
{PRES_CSS}
</head>
<body>
<div class="reveal"><div class="slides">
{slides_html}
</div></div>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
<script>
Reveal.initialize({{hash:true,slideNumber:true,progress:true,transition:'slide',
  center:false,width:1200,height:700,margin:0.04,plugins:[]}});
</script>
</body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    text = SRC.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    site_html = render_site(meta, body)
    SITE.write_text(site_html, encoding="utf-8")
    print(f"  ✓  {SITE}  ({len(site_html):,} bytes)")

    pres_html = render_presentation(meta, body)
    PRES.write_text(pres_html, encoding="utf-8")
    print(f"  ✓  {PRES}  ({len(pres_html):,} bytes)")


if __name__ == "__main__":
    main()
