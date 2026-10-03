# The Quantum Engineer — From a Laptop to the Quantum Frontier

A bilingual (English / فارسی) online book: a practical path from classical software
engineering to quantum computing, quantum information, and research — written for an
engineer starting from Iran, with no quantum hardware, aimed at serious international
quantum research and engineering.

**Contents:** 20 parts, 80 chapters, 20 appendices (A–T) — mathematics → physical
intuition → quantum information → computation → engineering → research → frontier.
Every chapter moves through five levels (intuition → mathematics → implementation →
engineering → research) and every experiment runs on a laptop.

## Run it

### Docker (single command)

```bash
docker compose up
```

Then open <http://localhost:8080> — English at `/en/`, Farsi at `/fa/`.
No custom image is built: the compose file mounts this repository into the stock
`python:3.12-alpine` base image and runs the stdlib-only server (`runtime/app.py`).
No pip dependencies.

### Plain Python (no Docker)

```bash
python3 runtime/app.py        # serves on :8080 (override with PORT=...)
```

### Static / offline (no server needed for hosting)

The `docs/` folder is a self-contained static reader (vanilla HTML/CSS/JS, zero
dependencies, no internet required) used for GitHub Pages:

```bash
cd docs && python3 -m http.server 8080
```

## Layout

- `runtime/app.py` — Python server: server-side rendering of the whole book,
  bilingual with RTL, search, dark/light theme. Standard library only.
- `docs/content/{en,fa}/` — the book itself (Markdown, one file per part).
- `docs/content/manifest.json` — catalog of parts and titles.
- `docs/assets/` — shared stylesheet, the static (client-side) reader, and the
  bundled Farsi font.
- `docs/content/SPEC.md` — the content contract for contributors.
- `PLAN.md` — the book's complete table of contents.

**Fonts — fully local, no internet needed:** no webfont is ever fetched from a
CDN. Latin text uses local system font stacks; Farsi text uses the **Sahel**
font bundled at `docs/assets/fonts/` (SIL Open Font License 1.1 — see
`docs/assets/fonts/OFL.txt`), served by the site itself.

Both runtimes read the same content and stylesheet: the Python server renders pages
server-side (pretty URLs like `/en/ch33`, form-based search); the static reader parses
the same Markdown client-side (hash URLs like `#/en/ch33`) for GitHub Pages and
fully-offline use.

## URLs (Python runtime)

- `/{lang}/` — home (`en` | `fa`)
- `/{lang}/p05` — part V
- `/{lang}/ch33` — chapter 33 (global numbering; `ch33.2` scrolls to section 2)
- `/{lang}/search?q=bloch` — search

© 2026 Tayyebi · [github.com/tayyebi/quantum](https://github.com/tayyebi/quantum)
