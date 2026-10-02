# Content Specification — The Quantum Engineer

Every part of the book is a **pair of Markdown files**:

- `content/en/part-NN.md` (English)
- `content/fa/part-NN.md` (Persian)

plus `content/en/appendices.md` / `content/fa/appendices.md`. The site (`docs/index.html`) parses these files directly — there is no build step, so the structure below is a hard contract.

## File structure (STRICT)

```text
# Part III — Mathematical Foundations        ← exactly one H1 per file
## 3. Mathematical Language                  ← chapter:  ## <chapter-number>. <Title>
### 3.1 Notation                             ← section:  ### <n.m> <Title>
```

- Chapter numbers are the **global book chapter numbers (1–80)**.
- One `##` per chapter; sections numbered `<chapter>.<section>`.
- Multi-chapter parts simply repeat the pattern.
- Unnumbered special chapters (e.g. `## Project — Build a Small Quantum Simulator from Scratch`) are allowed; the parser shows them without a number.
- Appendix chapters use: `## Appendix A — Linear Algebra Reference`.
- You may add `####` sub-headings inside a section body.

## Markdown features allowed

- Paragraphs, `**bold**`, `*italic*`, `` `inline code` ``, `[text](url)`
- Fenced code blocks with a language: ```python or ```text
- Lists (`-` and `1.`), one nesting level
- Blockquote callouts (below), GFM tables, `---` rules
- **Unicode math only**: |ψ⟩, ⟨φ|χ⟩, ⊗, †, √, ≈, ×, α β γ θ φ λ π ω, ½, superscripts like 2ⁿ or `2^n` inside code spans.
- NO LaTeX, NO `$...$`, NO images, NO external resources. External links (arxiv, docs) are fine as plain links — they are never loaded by the page.

## Callouts

```text
> [!note] Optional title
> body line
```

Types: `[!note]`, `[!tip]`, `[!experiment]`, `[!research]`, `[!warning]`, `[!levels]`.

- `[!experiment]` — "On your laptop": a concrete, runnable local experiment (Python 3 + numpy, qiskit ≥ 1.0 where relevant) with a short code block (≤ 25 lines, actually correct). Use 1–3 per chapter where meaningful.
- `[!research]` — open problems / what remains unsolved. 0–2 per chapter.
- `[!levels]` — **REQUIRED as the first block of every chapter**:

```text
> [!levels] Five levels of this chapter
> - **Intuition —** one line
> - **Mathematics —** one line
> - **Implementation —** one line
> - **Engineering —** one line
> - **Research —** one line
```

## Coverage (CRITICAL)

Cover **every** subsection PLAN.md lists for your chapters. You may group 2–4 closely related subsections under one `###` heading, but every listed topic must be addressed by name in the prose. Target: 80–160 words per H3 section; a 20-section chapter ≈ 1,800–2,600 words. Never pad; when a topic is thin, say precisely why it is thin.

## Voice

Direct, concrete, engineering-first. The reader is a professional software engineer: no dumbing down, no hype, no inspiration-speak. Prefer "here is the mechanism, here is the limitation, here is what to build" over adjectives. Use short code examples over long ones. State quantities and units when claiming things.

## Persian file (`fa`)

- A faithful, natural translation of the EN file — same structure, same callouts, same code blocks (code comments may stay English).
- Use ZWNJ (نیم‌فاصله, U+200C) correctly: می‌شود، برهم‌نهی، کیوبیت‌ها، رایانهٔ.
- Persian punctuation: ، ؛ « » and Persian question mark ؟.
- On first use of a technical term, give the English in parentheses: برهم‌نهی (superposition).
- Keep code, gate names (H, CNOT, T), and well-known algorithm names in Latin script; transliterate person names (شور، گروور) with the Latin name in parentheses on first use.
- Numbers inside formulas stay Western digits; Persian digits are fine in prose.

## Verification before you finish

1. Exactly one H1; every PLAN subsection topic of your part appears in the prose.
2. Every chapter starts with a `[!levels]` callout.
3. Python snippets are short and actually correct.
4. Both files saved at the exact paths you were given.
