#!/usr/bin/env python3
"""The Quantum Engineer — bilingual book server.

Python standard library only: renders the book server-side (no client-side
parsing), bilingual EN/FA with RTL, search, dark/light theme. Serves the same
content files and stylesheet as the static GitHub Pages build in docs/.

Run:  python3 runtime/app.py          (defaults to port 8080, PORT to override)
"""

import html
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CONTENT = DOCS / "content"
PORT = int(os.environ.get("PORT", "8080"))

MANIFEST = json.loads((CONTENT / "manifest.json").read_text(encoding="utf-8"))
LANGS = ("en", "fa")

UI = {
    "en": dict(
        toc_label="Table of contents", home_link="· Home", contents="Contents",
        chapter="Chapter", appendix="Appendix", sections="Sections",
        prev="Previous", nxt="Next", search_results="Search results",
        nothing="Nothing found for", indexing="",
    ),
    "fa": dict(
        toc_label="فهرست مطالب", home_link="· خانه", contents="مقدمهٔ بخش",
        chapter="فصل", appendix="پیوست", sections="بخش‌ها",
        prev="قبلی", nxt="بعدی", search_results="نتایج جست‌وجو",
        nothing="چیزی یافت نشد برای", indexing="",
    ),
}

FAVICON = ("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0"
           "%200%2032%2032'%3E%3Ccircle%20cx='16'%20cy='16'%20r='12'%20fill='none'%20str"
           "oke='%235b4fd6'%20stroke-width='3'%20/%3E%3Ccircle%20cx='16'%20cy='4.5'%20r="
           "'4'%20fill='%235b4fd6'%20/%3E%3C/svg%3E")

# ---------------------------------------------------------------- markdown

CH_RE = re.compile(r"^(\d+)\.\s*(.+)$")
APPX_RE = re.compile(r"^(?:Appendix|پیوست)\s+([A-Z])\s*[—–-]\s*(.+)$", re.I)
SEC_RE = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+)$")
FENCE_RE = re.compile(r"^\s*```")
CELL_ROW_RE = re.compile(r"^\|.*\|\s*$")
SEP_ROW_RE = re.compile(r"^\|[\s:|-]+\|\s*$")
HEAD_RE = re.compile(r"^(#{1,6})\s+(.+)$")
HR_RE = re.compile(r"^\s*(-{3,}|\*{3,})\s*$")
QUOTE_RE = re.compile(r"^>\s?")
CALLOUT_RE = re.compile(r"^\[!(\w+)\]\s*(.*)$")
UL_RE = re.compile(r"^\s*[-*]\s+")
OL_RE = re.compile(r"^\s*\d+[.)]\s+")
PARA_STOP_RE = re.compile(r"^\s*(```|>|#{1,6}\s|[-*]\s|\d+[.)]\s)")

CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
EM_RE = re.compile(r"(^|[\s(])\*([^*\n]+)\*(?=[\s).,!?:;]|$)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")

CALLOUT_TITLES = {
    "note": "Note", "tip": "Tip", "experiment": "On your laptop",
    "research": "Research frontier", "warning": "Warning", "levels": "Five levels",
}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def inline(s: str) -> str:
    def link_repl(m):
        url = m.group(2)
        extra = "" if url.startswith("#") else ' target="_blank" rel="noopener"'
        return f'<a href="{esc(url)}"{extra}>{m.group(1)}</a>'
    s = CODE_RE.sub(lambda m: "<code>" + m.group(1) + "</code>", s)
    s = BOLD_RE.sub(r"<strong>\1</strong>", s)
    s = EM_RE.sub(r"\1<em>\2</em>", s)
    s = LINK_RE.sub(link_repl, s)
    return s


def md_to_html(md: str) -> str:
    """Line-oriented renderer over RAW lines; content is escaped at emission."""
    lines = md.split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if FENCE_RE.match(line):
            lang = line.strip()[3:]
            body, i = [], i + 1
            while i < n and not FENCE_RE.match(lines[i]):
                body.append(lines[i]); i += 1
            i += 1
            attr = f' data-lang="{esc(lang)}"' if lang else ""
            out.append(f"<pre{attr}><code>{esc(chr(10).join(body))}</code></pre>")
            continue
        if CELL_ROW_RE.match(line) and SEP_ROW_RE.match(lines[i + 1] if i + 1 < n else ""):
            def cells(row):
                return [c.strip() for c in row.strip().strip("|").split("|")]
            head, i = cells(line), i + 2
            rows = []
            while i < n and CELL_ROW_RE.match(lines[i]):
                rows.append(cells(lines[i])); i += 1
            thead = "".join("<th>" + inline(esc(c)) + "</th>" for c in head)
            tbody = "".join(
                "<tr>" + "".join("<td>" + inline(esc(c)) + "</td>" for c in r) + "</tr>"
                for r in rows)
            out.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>")
            continue
        m = HEAD_RE.match(line)
        if m:
            lvl = min(len(m.group(1)) + 2, 6)  # ### -> h4 inside a section
            out.append(f"<h{lvl}>{inline(esc(m.group(2)))}</h{lvl}>")
            i += 1
            continue
        if HR_RE.match(line):
            out.append("<hr>"); i += 1; continue
        if QUOTE_RE.match(line):
            body = []
            i += 1
            while i < n and QUOTE_RE.match(lines[i]):
                body.append(QUOTE_RE.sub("", lines[i])); i += 1
            out.append(render_callout(body))
            continue
        if UL_RE.match(line):
            items, i = [], i
            while i < n and UL_RE.match(lines[i]):
                items.append(UL_RE.sub("", lines[i])); i += 1
            out.append("<ul>" + "".join(
                "<li>" + inline(esc(t)) + "</li>" for t in items) + "</ul>")
            continue
        if OL_RE.match(line):
            items, i = [], i
            while i < n and OL_RE.match(lines[i]):
                items.append(OL_RE.sub("", lines[i])); i += 1
            out.append("<ol>" + "".join(
                "<li>" + inline(esc(t)) + "</li>" for t in items) + "</ol>")
            continue
        if not line.strip():
            i += 1; continue
        body, i = [], i
        while (i < n and lines[i].strip() and not PARA_STOP_RE.match(lines[i])
               and not CELL_ROW_RE.match(lines[i])):
            body.append(lines[i]); i += 1
        if not body and i < n:  # always make progress
            body.append(lines[i]); i += 1
        out.append("<p>" + inline(esc(" ".join(body))) + "</p>")
    return "\n".join(out)


def render_callout(body_lines):
    first = body_lines[0] if body_lines else ""
    m = CALLOUT_RE.match(first)
    ctype = m.group(1).lower() if m else "note"
    title = m.group(2) if m else ""
    rest = body_lines[1:] if m else body_lines
    cls = "callout callout-" + ctype + (" levels" if ctype == "levels" else "")
    head = esc(title) if title else CALLOUT_TITLES.get(ctype, "Note")
    return (f'<aside class="{cls}"><strong class="co-title">{head}</strong>'
            + md_to_html("\n".join(rest)) + "</aside>")


def plain_text(md: str) -> str:
    txt = re.sub(r"```[\s\S]*?```", " ", md)
    txt = re.sub(r"[`*_[\]()>#|-]", " ", txt)
    return re.sub(r"\s+", " ", txt).strip()


# ---------------------------------------------------------------- parsing

def parse_part(raw: str) -> dict:
    lines = raw.lstrip("\ufeff").split("\n")
    part = {"title": "", "intro": [], "chapters": []}
    cur, bucket = None, part["intro"]
    for line in lines:
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            part["title"] = m.group(1).strip(); bucket = part["intro"]; continue
        m = re.match(r"^##\s+(.+)$", line)
        if m:
            cur = {"title": m.group(1).strip(), "num": None, "intro": [], "sections": []}
            nm = CH_RE.match(m.group(1))
            if nm:
                cur["num"], cur["title"] = nm.group(1), nm.group(2).strip()
            else:
                am = APPX_RE.match(m.group(1))
                if am:
                    cur["num"], cur["title"] = am.group(1), am.group(2).strip()
            part["chapters"].append(cur); bucket = cur["intro"]; continue
        m = re.match(r"^###\s+(.+)$", line)
        if m:
            sec = {"label": "", "title": m.group(1).strip(), "md": []}
            sm = SEC_RE.match(m.group(1))
            if sm:
                sec["label"], sec["title"] = sm.group(1), sm.group(2).strip()
            cur["sections"].append(sec); bucket = sec["md"]; continue
        bucket.append(line)
    part["intro_md"] = "\n".join(part["intro"]).strip()
    for ch in part["chapters"]:
        ch["intro_md"] = "\n".join(ch["intro"]).strip()
        for s in ch["sections"]:
            s["md_text"] = "\n".join(s["md"]).strip()
            s["text"] = plain_text((s["label"] + " " + s["title"] + " " + s["md_text"]).strip())
    return part


# ---------------------------------------------------------------- catalog

_parts = {}  # (lang, part_id) -> parsed part


def load_part(lang: str, part_id: str) -> dict:
    key = (lang, part_id)
    if key not in _parts:
        meta = next(p for p in MANIFEST["parts"] if p["id"] == part_id)
        _parts[key] = parse_part((CONTENT / lang / meta["file"]).read_text(encoding="utf-8"))
    return _parts[key]


def all_chapters(lang: str):
    out = []
    for meta in MANIFEST["parts"]:
        part = _parts.get((lang, meta["id"]))
        if not part:
            continue
        for ci, ch in enumerate(part["chapters"]):
            out.append({"meta": meta, "part": part, "ch": ch, "ordinal": len(out)})
    return out


def load_all(lang: str):
    for meta in MANIFEST["parts"]:
        load_part(lang, meta["id"])
    return all_chapters(lang)


def ch_url(lang: str, ordinal: int) -> str:
    return f"/{lang}/ch{ordinal + 1}"


# ---------------------------------------------------------------- pages

def shell(lang: str, content: str, title: str, *, route=None, q: str = "") -> str:
    rtl = ' dir="rtl"' if lang == "fa" else ""
    lang_meta = MANIFEST
    # language toggle keeps the same route in the other language
    other = "fa" if lang == "en" else "en"
    if route:
        kind, val = route
        if kind == "part":
            toggle_href = f"/{other}/{val}"
        elif kind == "chapter":
            toggle_href = f"/{other}/ch{val}"
        else:
            toggle_href = f"/{other}/"
    else:
        toggle_href = f"/{other}/"
    toggle_label = "فا" if lang == "en" else "EN"
    toc = toc_html(lang, route)
    brand = lang_meta["title"]["en"]
    return f"""<!doctype html>
<html lang="{lang}"{rtl}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="/assets/style.css">
<script>try{{var t=localStorage.getItem('tqe:theme');if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
</head>
<body>
<div id="app">
  <div id="scrim" hidden></div>
  <aside id="sidebar" aria-label="{esc(UI[lang]['toc_label'])}">
    <div class="side-head">
      <a class="brand" href="/{lang}/">
        <span class="brand-mark">◎</span>
        <span class="brand-text">{esc(brand.replace(' The ', ' The<br>'))}</span>
      </a>
      <div class="side-controls">
        <a id="lang-btn" class="ctl" href="{toggle_href}" title="Switch language / تغییر زبان">{toggle_label}</a>
        <button id="theme-btn" class="ctl" title="Theme" onclick="var h=document.documentElement;h.dataset.theme=h.dataset.theme==='dark'?'light':'dark';try{{localStorage.setItem('tqe:theme',h.dataset.theme)}}catch(e){{}}">◐</button>
      </div>
    </div>
    <div class="search-wrap">
      <form action="/{lang}/search" method="get">
      <input id="search" type="search" name="q" autocomplete="off" spellcheck="false"
             placeholder="Search… جست‌وجو" value="{esc(q)}">
      </form>
    </div>
    <nav id="toc">{toc}</nav>
    <div class="side-foot">
      <a href="https://github.com/tayyebi/quantum" target="_blank" rel="noopener">GitHub</a>
      <span>·</span><span>© 2026 Tayyebi</span>
    </div>
  </aside>
  <main id="main">
    <header id="topbar">
      <button id="menu-btn" class="ctl" aria-label="Menu">☰</button>
      <span id="topbar-title">{esc(lang_meta['title'][lang])}</span>
    </header>
    <article id="content" tabindex="-1">{content}</article>
  </main>
</div>
<script>
var mb=document.getElementById('menu-btn'),sc=document.getElementById('scrim');
if(mb){{mb.onclick=function(){{document.body.classList.toggle('nav-open')}}}};
if(sc){{sc.onclick=function(){{document.body.classList.remove('nav-open')}}}};
document.querySelectorAll('#toc .toc-part>button').forEach(function(b){{
  b.onclick=function(){{
    var w=b.parentElement,open=w.classList.contains('open');
    document.querySelectorAll('#toc .toc-part.open').forEach(function(x){{x.classList.remove('open')}});
    if(!open)w.classList.add('open');
  }};
}});
</script>
</body>
</html>"""


def toc_html(lang: str, route) -> str:
    kind = route[0] if route else None
    cur_part = route[1] if kind == "part" else None
    cur_ordinal = route[1] if kind == "chapter" else None
    cur_ch_part = None
    if kind == "chapter":
        flat = all_chapters(lang)
        if cur_ordinal is not None and 0 <= cur_ordinal - 1 < len(flat):
            cur_ch_part = flat[cur_ordinal - 1]["meta"]["id"]
    html_out = [f'<a class="toc-home" href="/{lang}/">{esc(UI[lang]["home_link"])}</a>']
    for meta in MANIFEST["parts"]:
        open_cls = " open" if meta["id"] in (cur_part, cur_ch_part) else ""
        num = meta["num"] or "¶"
        html_out.append(
            f'<div class="toc-part{open_cls}" data-part="{meta["id"]}">'
            f'<button type="button"><span class="pnum">{esc(num)}</span>'
            f"<span>{esc(meta['title'][lang])}</span></button>"
            f'<div class="toc-chs">')
        part = _parts.get((lang, meta["id"]))
        if part:
            active = ' class="active"' if kind == "part" and cur_part == meta["id"] else ""
            if part["intro_md"]:
                html_out.append(f'<a href="/{lang}/{meta["id"]}"{active}>· {esc(UI[lang]["contents"])}</a>')
            flat = all_chapters(lang)
            for entry in flat:
                if entry["meta"]["id"] != meta["id"]:
                    continue
                ch = entry["ch"]
                act = ' class="active"' if (kind == "chapter"
                                            and entry["ordinal"] + 1 == cur_ordinal) else ""
                label = (esc(ch["num"]) + ". " if ch["num"] else "") + esc(ch["title"])
                html_out.append(f'<a href="{ch_url(lang, entry["ordinal"])}"{act}>{label}</a>')
        html_out.append("</div></div>")
    return "".join(html_out)


def crumb(lang: str, items) -> str:
    sep = '<span class="sep">›</span>'
    parts = []
    for t, href in items:
        if href:
            parts.append(f'<a href="{href}">{esc(t)}</a>')
        else:
            parts.append(f"<span>{esc(t)}</span>")
    return f'<div class="crumb">{sep.join(parts)}</div>'


def page_home(lang: str) -> str:
    load_all(lang)
    home_md = ""
    p = CONTENT / lang / "home.md"
    if p.exists():
        home_md = p.read_text(encoding="utf-8")
    cards = "".join(
        f'<a href="/{lang}/{m["id"]}"><span class="pnum">{esc(m["num"] or "¶")}</span>'
        f"<span>{esc(m['title'][lang])}</span></a>"
        for m in MANIFEST["parts"])
    content = md_to_html(home_md) + f'<h2>{esc(UI[lang]["contents"])}</h2>' \
             f'<div class="part-cards">{cards}</div>'
    title = f"{MANIFEST['title'][lang]} — {MANIFEST['subtitle'][lang]}"
    return shell(lang, content, title)


def page_part(lang: str, part_id: str) -> str:
    meta = next((m for m in MANIFEST["parts"] if m["id"] == part_id), None)
    if not meta:
        return None
    load_all(lang)
    part = load_part(lang, part_id)
    items = [(MANIFEST["title"][lang], f"/{lang}/"), (meta["title"][lang], None)]
    ch_items = []
    for entry in all_chapters(lang):
        if entry["meta"]["id"] != part_id:
            continue
        ch = entry["ch"]
        num = esc(ch["num"]) if ch["num"] else "¶"
        ch_items.append(
            f'<li><a href="{ch_url(lang, entry["ordinal"])}">'
            f'<span class="cnum">{num}</span><span>{esc(ch["title"])}</span></a></li>')
    content = (crumb(lang, items)
               + f'<h1>{esc(part["title"] or meta["title"][lang])}</h1>'
               + (md_to_html(part["intro_md"]) if part["intro_md"] else "")
               + f'<h2>{esc(UI[lang]["contents"])}</h2>'
               + '<ul class="ch-cards">' + "".join(ch_items) + "</ul>")
    return shell(lang, content, part["title"] + " — " + MANIFEST["title"][lang],
                 route=("part", part_id))


def page_chapter(lang: str, ordinal: int) -> str:
    flat = load_all(lang)
    if not (1 <= ordinal <= len(flat)):
        return None
    entry = flat[ordinal - 1]
    meta, ch = entry["meta"], entry["ch"]
    ui = UI[lang]
    label = ""
    if ch["num"] and ch["num"].isdigit():
        label = f'{ui["chapter"]} {ch["num"]}'
    elif ch["num"]:
        label = f'{ui["appendix"]} {ch["num"]}'
    items = [(MANIFEST["title"][lang], f"/{lang}/"),
             (meta["title"][lang], f"/{lang}/{meta['id']}")]
    if label:
        items.append((label, ch_url(lang, entry["ordinal"])))
    out = [crumb(lang, items)]
    num_html = f'<span style="color:var(--accent)">{esc(ch["num"])}.</span> ' if ch["num"] else ""
    out.append(f'<h1>{num_html}{esc(ch["title"])}</h1>')
    if ch["intro_md"]:
        out.append(md_to_html(ch["intro_md"]))
    if len(ch["sections"]) > 1:
        links = " ".join(
            f'<a href="{ch_url(lang, entry["ordinal"])}.{si}">{esc(s["label"] or str(si + 1))}</a>'
            for si, s in enumerate(ch["sections"]))
        out.append(f'<nav class="sec-nav">{esc(ui["sections"])}: {links}</nav>')
    for si, s in enumerate(ch["sections"]):
        num2 = f'<span class="secnum">{esc(s["label"])}</span>' if s["label"] else ""
        out.append(f'<section class="sec" id="sec-{si}"><h3>{num2}{esc(s["title"])}</h3>'
                   + md_to_html(s["md_text"]) + "</section>")
    prev = flat[entry["ordinal"] - 1] if entry["ordinal"] > 0 else None
    nxt = flat[entry["ordinal"] + 1] if entry["ordinal"] + 1 < len(flat) else None
    out.append('<nav class="pager">')
    if prev:
        pn = esc(prev["ch"]["num"]) + ". " if prev["ch"]["num"] else ""
        out.append(f'<a class="prev" href="{ch_url(lang, prev["ordinal"])}">'
                   f'<span class="pg-label">{esc(ui["prev"])}</span>'
                   f'<span class="pg-title">{pn}{esc(prev["ch"]["title"])}</span></a>')
    else:
        out.append('<span style="flex:1"></span>')
    if nxt:
        nn = esc(nxt["ch"]["num"]) + ". " if nxt["ch"]["num"] else ""
        out.append(f'<a class="next" href="{ch_url(lang, nxt["ordinal"])}">'
                   f'<span class="pg-label">{esc(ui["nxt"])}</span>'
                   f'<span class="pg-title">{nn}{esc(nxt["ch"]["title"])}</span></a>')
    else:
        out.append('<span style="flex:1"></span>')
    out.append("</nav>")
    title = (ch["num"] + ". " if ch["num"] else "") + ch["title"] + " — " + MANIFEST["title"][lang]
    return shell(lang, "".join(out), title, route=("chapter", ordinal))


def page_search(lang: str, q: str) -> str:
    flat = load_all(lang)
    ui = UI[lang]
    ql = q.strip().lower()
    out = [crumb(lang, [(MANIFEST["title"][lang], f"/{lang}/"), (ui["search_results"], None)])]
    out.append(f"<h1>{esc(ui['search_results'])}: “{esc(q)}”</h1>")
    if len(ql) < 2:
        out.append(f'<div class="search-results"><p>{esc(ui["nothing"])} “{esc(q)}”</p></div>')
    else:
        results = []
        for entry in flat:
            ch = entry["ch"]
            where = (ch["num"] + ". " if ch["num"] else "") + ch["title"]
            for si, s in enumerate(ch["sections"]):
                low = s["text"].lower()
                pos = low.find(ql)
                if pos == -1:
                    continue
                start = max(0, pos - 60)
                snip = s["text"][start:pos + len(q) + 90]
                snip = esc(snip).replace(
                    esc(q), "<mark>" + esc(q) + "</mark>", 1)
                href = ch_url(lang, entry["ordinal"]) + (f".{si}" if si else "")
                results.append(
                    f'<a class="sr" href="{href}"><span class="sr-where">{esc(where)}'
                    f' — {esc(s["label"] or s["title"])}</span>'
                    f'<span class="sr-snip">…{snip}…</span></a>')
                if len(results) >= 40:
                    break
            if len(results) >= 40:
                break
        if results:
            out.append('<div class="search-results">' + "".join(results) + "</div>")
        else:
            out.append(f'<div class="search-results"><p>{esc(ui["nothing"])} “{esc(q)}”</p></div>')
    return shell(lang, "".join(out),
                 ui["search_results"] + " — " + MANIFEST["title"][lang],
                 route=("search", None), q=q)


def page_404(lang: str) -> str:
    content = ('<h1>404</h1><p><a href="/' + lang + '/">← ' +
               esc(UI[lang]["home_link"].lstrip("· ")) + "</a></p>")
    return shell(lang, content, "404 — " + MANIFEST["title"][lang])


# ---------------------------------------------------------------- server

PART_IDS = {m["id"] for m in MANIFEST["parts"]}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def do_GET(self):
        url = urlparse(self.path)
        path = quote(url.path)
        try:
            if path == "/assets/style.css":
                self._send((DOCS / "assets" / "style.css").read_bytes(), "text/css; charset=utf-8")
                return
            if path == "/favicon.ico":
                self._send(b"", "text/plain")
                return
            segs = [s for s in path.split("/") if s]
            lang = segs[0] if segs and segs[0] in LANGS else None
            if not lang:
                self._redirect("/en/")
                return
            rest = segs[1:]
            if not rest or rest == ["home"]:
                self._html(page_home(lang))
                return
            if rest == ["search"]:
                qs = parse_qs(url.query)
                self._html(page_search(lang, (qs.get("q") or [""])[0]))
                return
            pid = rest[0]
            if pid in PART_IDS:
                self._html(page_part(lang, pid))
                return
            m = re.match(r"^ch(\d+)(?:\.(\d+))?$", pid)
            if m:
                ordinal, sec = int(m.group(1)), m.group(2)
                if sec is not None:
                    self._redirect(f"/{lang}/ch{ordinal}#sec-{sec}")
                    return
                page = page_chapter(lang, ordinal)
                if page:
                    self._html(page)
                    return
            self._not_found(lang)
        except Exception as e:  # keep the server alive on any render error
            body = f"<h1>render error</h1><pre>{esc(repr(e))}</pre>"
            self._send(shell("en", body, "error").encode(), "text/html; charset=utf-8", 500)

    def _html(self, page, status=200):
        self._send(page.encode(), "text/html; charset=utf-8", status)

    def _not_found(self, lang):
        self._html(page_404(lang), 404)

    def _redirect(self, to):
        self.send_response(302)
        self.send_header("Location", to)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _send(self, body: bytes, ctype: str, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)


def main():
    addr = ("0.0.0.0", PORT)
    print(f"The Quantum Engineer — serving on http://{addr[0]}:{addr[0] and PORT}/", flush=True)
    print("EN: /en/   FA: /fa/", flush=True)
    ThreadingHTTPServer(addr, Handler).serve_forever()


if __name__ == "__main__":
    main()
