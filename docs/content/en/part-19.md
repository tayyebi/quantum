# Part XIX — The 5-Year Trajectory

*Author: GLM-5.3*

Everything in this book converges here: a five-year schedule from where you sit — working software engineer, Iran, laptop, no quantum background — to contributing quantum researcher with access to serious hardware and research infrastructure. The plan is aggressive but not heroic: it assumes disciplined part-time study (10–15 hours weekly) plus your existing engineering job, and it front-loads everything location-independent so that geography never gates the early years. Each year has a theme, a curriculum, and one non-negotiable deliverable. Adjust the pace; do not adjust the deliverables — they are the plan.

## 73. Year 0–1 — Foundations

*Author: GLM-5.3*

> [!levels] In this chapter
> **Lv1** you follow the year's curriculum: mathematics, quantum information, Qiskit, algorithms, simulation. **Lv2** you complete it at working pace alongside a job. **Lv3** the study converts into running code and passing tests. **Lv4** the year's projects meet professional standards and are public. **Lv5** the year-1 exit audit — read papers, debug circuits, predict distributions — passes honestly.

**Theme:** the mathematics becomes native, the circuit model becomes reflex, and your first serious artifacts exist in public.

**Mathematics** (months 0–4): Parts III in full — linear algebra to the eigendecomposition, complex numbers to comfort, probability to distributions-over-amplitudes. Working method: every concept instantiated at n=2 in numpy; the Ch. 52.5 discipline from day one. Milestone check: you can compute a tensor product, check unitarity, and diagonalize a Hamiltonian without notes.

**Quantum information** (months 3–6): Parts II, IV, V — postulates, qubits, entanglement, the measurement statistics that make everything else sensible. You are not learning philosophy; you are building the object model in your head (Ch. 2.18–2.21's thinking modes).

**Qiskit** (months 4–6): Part VI's chapters 15–16 — circuit construction, transpilation, simulators, the debugging and testing discipline. By month 6, the Ch. 16.15 test-first workflow is your default.

**Algorithms** (months 6–9): Part VII — every algorithm implemented by hand on your simulator as you read; Project 2's early milestones run concurrently.

**Simulation** (months 9–12): Chapter 17, executed as **Project 1** — your quantum simulator, built, benchmarked, tested against Aer, public.

**Deliverable: 3–5 serious GitHub projects.** By month 12: the simulator (Project 1), the algorithm laboratory (Project 2, at least M1–M4), the noisy simulator (Project 3) begun or complete, plus two smaller public artifacts (reproducible notebooks, blog posts with code). All at Ch. 62.1's standards: they run, they're tested, they're documented. Year-1 exit self-audit: Ch. 59.8's first boxes ticked — can you read a paper's circuit (Ch. 52)? Can you debug someone's quantum code? Can you predict distributions before running? If yes, the foundation holds.

## 74. Year 1–2 — Specialization

*Author: GLM-5.3*

> [!levels] In this chapter
> **Lv1** you survey the five specialization options and their target roles. **Lv2** you run the two-month informed exploration of each candidate. **Lv3** you commit to a spike with a written rationale and review date. **Lv4** the year produces one research-quality project in the spike. **Lv5** your specialization is legible to strangers from your GitHub alone.

**Theme:** converge (Ch. 61) — choose the spike, go deep, and produce one research-quality build in it.

**Choose:**

- **Algorithms** — Part VII/VIII depth, resource estimation craft (Ch. 28.9), the theory-mathematics track; target roles: Ch. 60.2/60.3; best if Ch. 61.2's evidence points you mathematical.
- **Error correction** — Part X depth, stim mastery, decoder engineering; target: Ch. 60.5 — the 2026-hot path, artifact-meritocratic, hiring now.
- **Compilers** — Part XII depth, Project 5 pushed to research grade, benchmark craft; target: Ch. 60.4 — the software-engineer-native path.
- **Quantum simulation** — Parts XIII's 47–48 depth, chemistry stack (Qiskit Nature, PySCF), Trotter/qubitization numerics; target: Ch. 60.9/60.2-chemistry — the application path.
- **Cryptography** — Ch. 51 depth plus classical crypto (the real prerequisite — a parallel study track); target: Ch. 60.10 — the immediately-monetizable path.

The choosing method is Ch. 61.6's evidence audit, not preference: artifact record, energy audit, reality feedback. The year's structure: two months of *informed* exploration (try each candidate's project-tier work for two weekends), then commit with Ch. 61.7's annual review date.

**Deliverable: first research-quality project.** In your chosen spike, one artifact that a practitioner in that subfield would take seriously: the QEC laboratory (Project 4) with threshold curves for compilers-turned-QEC; the compiler (Project 5) with its novel pass for the compiler path; a resource-estimation study for algorithms; a small-molecule benchmark suite for simulation; a PQC migration analysis of a real system for crypto. "Research-quality" = Ch. 54's discipline visible (seeds, error bars, baselines) + public + written up (Ch. 62.2). Year-2 exit: your specialization is legible to strangers from your GitHub alone.

## 75. Year 2–3 — Research

*Author: GLM-5.3*

> [!levels] In this chapter
> **Lv1** you establish the two-papers-weekly reading practice with a claims matrix. **Lv2** you execute Project 6 reproductions with deviation ledgers. **Lv3** your OSS ladder reaches recognized contributor status. **Lv4** correspondence converts into real collaboration. **Lv5** the year delivers one research contribution that did not exist before you.

**Theme:** enter the community — from consumer of research to contributor.

**Papers** (the reading practice, now load-bearing): two papers weekly through Ch. 52's three-pass; maintain the claims matrix in your niche; by year-end you have the field map (Ch. 55.2) that makes gaps visible.

**Reproduction** (months 24–30): **Project 6** — two or three careful reproductions in your specialization, deviation ledgers and all, published (Ch. 53.8). This is the year's engine: reproduction builds every downstream capability simultaneously.

**Open-source** (continuous): the Ch. 62.5 ladder — from docs-and-examples through component ownership toward committership in your specialization's flagship project (stim or PyMatching for QEC; Qiskit/PyZX for compilers; Cirq/PennyLane for algorithms...). By month 36: you are a known contributor somewhere.

**Research collaborations** (months 30–36): Ch. 62.7's correspondence, now converting — remote collaborations arranged with groups whose work you've reproduced or extended; the undersung version (contributing to a group's repo, co-developing a tool) counts fully and starts easier than co-authorship.

**Technical writing** (cadence): the blog at biweekly-or-better, increasingly in your specialization; one write-up per reproduction; your Year-2 project written as a proper technical report.

**Deliverable: research contribution.** One thing that did not exist before you: an extension of a reproduced paper, a tool adopted by others, a negative-result study with clean methodology, a benchmark finding — small is fine; *new and public* is mandatory. Ideal form: a workshop-paper-grade write-up or a merged, substantial OSS contribution that practitioners use. Year-3 exit audit: Ch. 59.8's checklist — all boxes except laboratory access; Ch. 63.11's dossier — thick with dated evidence; Ch. 63.12's network — real, with names. You are employable/contributable now; the remaining year is transition.

## 76. Year 3–5 — International Transition

*Author: GLM-5.3*

> [!levels] In this chapter
> **Lv1** you map the two transition branches — degree path and industry path. **Lv2** you prepare applications and the evidence dossier. **Lv3** you execute the transition — admission or offer. **Lv4** you gain laboratory access and research infrastructure. **Lv5** the founding constraint is dissolved: daily work on real machines inside a research community.

**Theme:** close the last gaps — credentials, hardware access, location — via the paths Ch. 63 mapped, choosing the branch that fits your evidence.

**Path A — master's / PhD / research position.** Months 36–42: applications (Ch. 63.3–63.7) — target ecosystems, not just rankings (Ch. 63.4's Germany/Netherlands/Nordics/Canada cluster; program deadlines 12–15 months before start); the artifact portfolio is your application's spine, Ch. 63.11's dossier its evidence annex. Months 42–60: the program itself — and its real payload: *laboratory access* (physical labs, research hardware, the supervision that Ch. 63.8 said artifacts can't fully substitute), credential, location, and the first institutionally-supported research. In-program strategy: your Parts XIV–XVIII head start means you arrive as the student who reproduces, builds, and ships — spend the surplus on the lab craft and depth that need institutions.

**Path B — quantum industry.** Months 36–48: targeted entry via your specialization's meritocratic channels — the QEC/compiler/application roles of Ch. 60.4–60.9 where public artifacts + OSS committership + the Year-3 contribution are the actual hiring bar; internships and trial-projects (Ch. 63.6) as the wedge; remote-first and EU-based employers first (Ch. 63.1's geography). Months 48–60: the role, converting to the on-site/visa transition (Ch. 63.9's skilled-worker and talent routes — your dossier serves both). Industry's payload is the same as academia's by different means: serious hardware (production systems, not cloud queues), research infrastructure (engineering teams, real constraints), and compensation that funds the whole enterprise.

**Path A/B is a real fork but not a wall** — the artifact-first strategy makes you credible on both; apply to both if uncertain; the paths recombine after (industry→PhD and PhD→industry are both routine in this field).

**Deliverable: access to serious hardware and research infrastructure.** The book's founding constraint — starting from a laptop in a country whose access is complicated — is dissolved: you work daily on or around real machines, inside a research community, with the credentials to stay. The five-year exit audit is short: you are doing, institutionally, what Parts XVII–XVIII had you doing at home — but at the frontier's scale, with collaborators, and with the trajectory's next decade visibly open (Part XX is your map of it).

> [!tip] The schedule's operating rules
> (1) **Deliverables over hours** — the year's output is the artifact, not the study-time; if a month produces no public thing, replan. (2) **Never study without running code** — every concept instantiated (Ch. 52.5) or it didn't happen. (3) **Front-load the location-independent** — years 0–3 are deliberately 100% laptop+cloud; geography never gates them. (4) **Public by default** — everything from week 1; the dossier builds itself. (5) **The review dates are sacred** — Ch. 61.7's annual specialization review and a quarterly pace review; plans that can't change are fantasies. (6) **Life happens** — the plan absorbs 6-month slips without structural damage; it does not absorb silent abandonment. If you stop, restart visibly.
