# Part XVIII — Serious Projects

*Author: GLM-5.3*

Knowledge you can't defend with code is a rumor about yourself. This part is the book's forge: seven projects, escalating in ambition, that convert everything you've read into artifacts — the portfolio Chapter 62 told you to build, the evidence Chapter 63 told you to document, the apprenticeship Chapter 59 told you to complete. Projects 1–5 you have already *studied* (Parts VI, VII, IX, X, XII designed them); here they get full build specifications with milestones and acceptance criteria. Project 6 is your first research act. Project 7 is the real one: something nobody told you to build.

## 66. Project 1 — Quantum Simulator

*Author: GLM-5.3*

> [!levels] In this project
> **Lv1** you build a working state-vector engine with gates and measurement. **Lv2** you make it fast (tensor contraction) and complete (parser, sampling, CLI). **Lv3** you verify it against Qiskit and against hand-computed physics. **Lv4** you characterize its limits — memory, time, the exponential wall — empirically. **Lv5** you extend it beyond spec: sparse or stabilizer engines, noise channels — and know exactly why each extension is hard.

**Build:** state vector, gate engine, measurement, sampling, circuit parser. (Chapter 17 is the full design document — this page is the contract.)

**Specification.** A Python package `qsim` with: (1) a state-vector core holding complex amplitudes for n qubits; (2) a gate engine applying H, X, Y, Z, S, T, RX/RY/RZ(θ), CX, CZ, SWAP, and arbitrary 1-qubit unitaries, implemented with tensor contraction (tensordot/moveaxis) — *not* kron-per-gate; (3) measurement: full-register sampling from |amplitudes|², plus single-qubit mid-circuit measurement with renormalization; (4) a batch sampler with seeded reproducibility; (5) a text circuit parser (`H 0`, `CX 0 1`, `RZ 1.5708 2`, `M 0 1`) with validation; (6) a CLI: `python -m qsim circuit.txt --shots 4096 --seed 42` printing a histogram.

**Milestones.** M1: single-qubit gates correct (test: each gate's application matches its 2×2 matrix on hand-worked examples). M2: CX, CZ, SWAP; Bell state |Φ⁺⟩ gives 50/50 on 4096 shots (±2σ). M3: tensor-contraction rewrite passes all M1–M2 tests; ≥100× faster than kron version at n=20. M4: parser + CLI + seeded sampling. M5: GHZ-n (n=8) and QFT-4 distributions match Aer same-seed.

**Acceptance criteria.** Bell, GHZ-8, QFT-4 match Qiskit Aer within statistical bounds at 4096 shots; n=26 gate application < 1 s on a laptop; all tests pass from a clean clone (`pip install -e . && pytest`); README states complexity (time O(2ⁿ) per gate, memory 16·2ⁿ bytes) with a benchmark table you measured, not quoted.

**What it proves.** You understand the circuit model at the implementation level — Part VI is no longer notation. Estimated effort: 2–3 weekends.

## 67. Project 2 — Quantum Algorithm Laboratory

*Author: GLM-5.3*

> [!levels] In this project
> **Lv1** you implement the early algorithms correctly and verify their guarantees. **Lv2** you implement QFT, phase estimation, and Shor end-to-end with correct statistics. **Lv3** you validate every algorithm against theory — deterministic, probabilistic, and scaling behavior. **Lv4** you study noise impact: which algorithms survive, which die, at what error rate. **Lv5** you understand each algorithm's resource structure well enough to estimate costs for bigger instances than you can run.

**Implement:** Deutsch, Deutsch–Jozsa, Bernstein–Vazirani, Simon, Grover, QFT, phase estimation, Shor. (Chapter-by-chapter: 19–26.)

**Specification.** A package `qalgo` built on *your* Project 1 simulator (primary) and Qiskit (cross-check), with one module per algorithm, each exposing: the oracle interface it needs, the circuit constructor, a `run(shots)` method, and a *verifier* — code that checks the guarantee (Deutsch: one query, correct f(0)⊕f(1) every shot; DJ: deterministic constant/balanced answer; BV: exact a; Simon: linear-algebra post-processing recovering s from ~2n samples; Grover: marked-state probability peaking at the theoretical ⌊(π/4)√(2ⁿ/η)⌋ iterations — plot the oscillation; QFT: verify against exact DFT matrix on random states; PEP: eigenphase recovery to k bits with the right success probability; Shor: full pipeline on N=15 and N=21 — modular exponentiation circuits, QFT, continued-fraction post-processing, factor found in ≥ some fraction of runs).

**Milestones.** M1: the four oracle algorithms with verifiers green. M2: QFT exact-matrix validation + approximate-QFT (dropped rotations) error vs. savings. M3: phase estimation with success-probability curve. M4: Shor N=15 factoring end-to-end (both coprime bases), then N=21. M5: noise module — run each algorithm under depolarizing noise swept 0.1–5%, chart failure thresholds.

**Acceptance criteria.** Every algorithm reproduces its theoretical behavior in an automated test (deterministic exactness where promised, correct success probabilities where probabilistic); Shor factors 15 and 21 with documented success rates; the noise-threshold figure exists and its ordering (Grover fragile vs. DJ robust, etc.) is explained in the README from the mathematics.

**What it proves.** Part VII internalized at the level where you could debug someone else's algorithm implementation. Effort: 3–4 weekends.

## 68. Project 3 — Noisy Quantum Simulator

*Author: GLM-5.3*

> [!levels] In this project
> **Lv1** you implement the canonical noise channels as Kraus operators and apply them correctly. **Lv2** you build density-matrix evolution and verify mixed-state physics. **Lv3** you validate against theory: decay curves, depolarization rates, measurement-error matrices. **Lv4** you match real-device behavior using published calibration data. **Lv5** you understand the boundary — what your channel models can and cannot capture about real hardware.

**Implement:** bit flip, phase flip, depolarizing noise, amplitude damping, measurement errors. (Chapters 29–31.)

**Specification.** Extend `qsim` (or new package `qnoise`) with: (1) channel framework `apply_channel(state, kraus_ops)` — pure-state stochastic (sample one Kraus per application, tracking the outcome) *and* density-matrix evolution `ρ → Σ K ρ K†`; (2) the named channels with tunable probabilities: bit flip (X with p), phase flip (Z with p), depolarizing (Ch. 29's mixture), amplitude damping (Kraus pair with γ — T1 physics), measurement error (confusion matrix per qubit, applied at readout); (3) T1/T2 modeling: idling as thermal-relaxation channels parameterized by real device numbers (T1=200 µs, T2=100 µs, gate times from Ch. 15); (4) validation experiments — amplitude-damping |1⟩ population decays as (1−γ)ᵗ exactly; depolarizing shrinks Bloch vectors toward origin isotropically; measurement-error matrix recovered by prepare-and-measure calibration.

**Milestones.** M1: Kraus framework, bit/phase flip verified. M2: depolarizing + Bloch-vector shrinkage plot. M3: amplitude damping + T1 decay curve matched to theory. M4: measurement error + calibration inversion. M5: a full noisy run — Grover-4 under a composite noise model, compared to ideal, gap explained quantitatively; then Aer's `NoiseModel.from_backend` on the same circuit, three-way comparison (yours/Aer/ideal).

**Acceptance criteria.** Every channel's action verified against closed-form predictions in tests; density-matrix and stochastic-sampling evolution agree statistically; the composite-noise Grover analysis quantitatively attributes the fidelity loss to channels (gate error vs. damping vs. readout — a decomposition table, not a vibe).

**What it proves.** Part IX is real to you: noise is no longer a black box called "decoherence" but an operator algebra you have implemented and measured. Effort: 2–3 weekends.

## 69. Project 4 — Error Correction Laboratory

*Author: GLM-5.3*

> [!levels] In this project
> **Lv1** you implement the repetition and small codes with correct syndrome extraction. **Lv2** you build decoders and measure logical error rates. **Lv3** you demonstrate the threshold effect — logical error falling with code distance under circuit noise. **Lv4** you implement surface-code memory experiments at d=3,5 with real decoding. **Lv5** you can design syndrome-extraction circuits and diagnose decoder failures — the working skills of Ch. 60.5's hottest job.

**Implement:** three-qubit code, five-qubit code, Steane code, surface code, syndrome extraction, decoder, logical error measurement. (Chapters 32–37; Ch. 37's project spec is the deep version.)

**Specification.** A package `qec` with: (1) stabilizer formalism utilities (Pauli strings, tableau or commutation checks); (2) the codes — 3-qubit repetition (bit-flip), 5-qubit perfect code, Steane [[7,1,3]], and rotated surface code at d=3 and d=5 (distance-3 buildable by hand; d=5 via stim-generated circuits); (3) syndrome extraction circuits — ancilla-measure blocks per stabilizer (verify: measuring the syndrome doesn't disturb the encoded logical state beyond the correctable subspace); (4) decoders: lookup table for the small codes, and MWPM (minimum-weight perfect matching — via PyMatching or your own blossom-lite, plus a maximum-likelihood decoder for d=3 where brute-force works) for the surface code; (5) logical error measurement: prepare |0⟩_L or |+⟩_L, run memory rounds under circuit-level noise, decode, measure logical failure rate vs. distance and physical error rate.

**Milestones.** M1: 3-qubit code corrects all single bit flips; logical error measured, matches theory (p_L ≈ 3p²). M2: 5-qubit and Steane codes encode/decode correctly; distance-3 error correction verified exhaustively (all 1-qubit Paulis). M3: surface-code d=3 syndrome circuits correct; MWPM decoding above break-even. M4: d=3 vs. d=5 logical-error curves under depolarizing circuit noise — *threshold behavior visible or its absence explained*. M5: performance — 10⁴+ shots per point in minutes (numpy-vectorized or stim-backed), and the Λ factor (error suppression ratio per distance step) computed.

**Acceptance criteria.** Every code passes its distance-based guarantee test; logical-vs-physical error plots exist with ≥4 physical-error values × 2 distances, error bars, and fitted threshold estimate (expect ~0.5–1% for circuit-level depolarizing with your setup — and your README explains any deviation from literature values honestly); decoders benchmarked (accuracy vs. speed).

**What it proves.** Part X operationalized — you have personally measured error correction working and failing, the experience entire roadmaps are built on. Effort: 4–6 weekends; the most valuable project in this part.

## 70. Project 5 — Quantum Compiler

*Author: GLM-5.3*

> [!levels] In this project
> **Lv1** you build parser → DAG → native-gate output, correct by construction. **Lv2** you implement optimization passes with measured improvements. **Lv3** you implement routing on a real coupling map with layout tracking. **Lv4** you benchmark against Qiskit honestly — distributions, seeds, and a written comparison. **Lv5** you extend into the open territory: noise-aware passes, commutation analysis, ZX rewrites — one research-grade pass of your own.

**Build:** parser, intermediate representation, gate decomposition, qubit mapping, routing, optimization, scheduling. (Chapter 46's project spec is the full version.)

**Specification.** A package `qcc` (see Ch. 46's deliverables list): text/OpenQASM-lite parser with parameters; DAG IR with node/edge operations and topological iteration; passes — inverse-pair cancellation, rotation merging, commutation-aware sliding, SWAP-based routing (SABRE-style heuristic) on a 7-qubit heavy-hex coupling map, direction fixing, Euler resynthesis of 1-qubit strings; a scheduler producing per-qubit timelines with gate durations; a cost module (gate counts, depth, Σ per-gate error from a calibration file); a benchmark harness running your corpus with seeds.

**Milestones.** M1: parser + DAG + `Operator`-equivalence harness — the correctness foundation, built first. M2: cancellation + merging; ≥10% gate reduction on QFT-5. M3: routing with correct output-permutation tracking (measurements included — Ch. 46.2's named bug, tested by name). M4: full pipeline vs. Qiskit O0–O3 on a 4-circuit corpus (QFT-5, Grover-3, 4-bit adder, GHZ-7), ≥20 seeds, medians and IQR. M5 (research-grade): one novel or adapted pass — noise-adaptive layout from a calibration snapshot, or Pauli-commutation reordering — with its own benchmarked win on a workload class.

**Acceptance criteria.** Pipeline output unitary-equivalent to input on all tests; benchmark report with honest error bars (Ch. 46.8's protocol, followed literally); README documents each pass with its complexity and one before/after circuit diagram; the M5 pass's improvement is real, isolated (ablation shown), and honestly scoped ("wins on X, loses on Y").

**What it proves.** Part XII plus the systems-engineering maturity to build a tool *stack*, verified at every layer. This project plus Project 4 is a complete entry-level portfolio for Ch. 60.4 and 60.5 roles. Effort: 4–6 weekends.

## 71. Project 6 — Reproduce a Research Paper

*Author: GLM-5.3*

> [!levels] In this project
> **Lv1** you extract a paper's algorithm into a written specification. **Lv2** you implement it from your spec, not their code. **Lv3** you reproduce the key figure within honest statistical bounds. **Lv4** you document deviations rigorously — the deviation ledger as a scientific artifact. **Lv5** you publish the reproduction and engage the authors — your first act inside the research community.

**The pipeline** (Chapter 53 is the method; this is the execution):

```text
paper → mathematical model → implementation → simulation → experiment → comparison → technical report
```

**Specification.** Choose *one* recent (last 3 years) paper with a simulator-reproducible core claim — the sweet spots: a transpiler/routing benchmark, a decoder evaluation, a variational-algorithm study, a resource-estimate improvement. Constraints from Ch. 53.2: code-adjacent (their repo exists for checking, *after* your attempt), bounded (one figure), verifiable (numbers to match). Build the reproduction as a public repo: `spec.md` (the Ch. 53.3 extraction — every equation instanced at small n, every parameter listed, UNSPECIFIED markers where silent), implementation from spec (their code consulted only after your version runs, differences logged), the target figure reproduced with fresh seeds and error bars, the comparison (their number vs. yours, within-joint-uncertainty verdict), and the deviation ledger (Ch. 53.7's format — paper's value, yours, why, measured impact).

**Milestones.** M1: paper chosen, three-pass read done (Ch. 52), spec written. M2: implementation complete from spec; property tests green. M3: target figure reproduced (or the failure investigated to root cause — both are M3-complete). M4: deviation ledger finalized; comparison written with statistics (Ch. 53.6's standards). M5: published — repo finalized, blog post or ReScience-style write-up (Ch. 53.8), email to the authors with your findings.

**Acceptance criteria.** A stranger could regenerate your figure with one command; every deviation has a measured impact; the verdict (confirmed / refined / could-not-reproduce) is stated with its statistical basis; the write-up is neutral in tone (Ch. 53.7's discipline) and public.

**What it proves.** Chapter 53's pipeline executed end-to-end — you have done research-cycle work: extraction, independent implementation, statistical comparison, and public, accountable communication. This is the project that converts "knows quantum computing" into "does quantum research." Effort: 3–5 weekends.

## 72. Project 7 — Find Something Nobody Told You to Build

*Author: GLM-5.3*

> [!levels] In this project
> There are no levels. This is the level.

**The final project. Not a tutorial. Not a course assignment. Not an implementation of somebody else's algorithm. Your own question.**

**Specification.** There is none. The constraints are the book's whole argument: it must originate from *your* question — found in your friction journal (Ch. 55.3), your claims matrix (55.2), your surprises file (59.6), the empty cell only you noticed; it must be honestly sized (55.9's filter — laptop-tractable, or cloud-hardware-scaled); it must be executed with Ch. 54's discipline (hypothesis first, baselines strong, statistics real); and it must produce a public artifact (62's standards) — code, a write-up, a figure that shows something nobody had shown, even if the something is small.

**Candidate shapes**, to prime not prescribe: a measurement nobody has published (seed-variance of routed circuits; drift in cloud calibration data analyzed longitudinally — you have free longitudinal access nobody exploits); a tool that closes a friction you hit (your Ch. 46.8 benchmark harness, generalized; a Bell-test statistics playground); a negative result worth knowing (does error-mitigation technique X actually help workload class Y? the honest sweep); a small theory instantiation (measuring barren-plateau onset constants for an ansatz family); an educational artifact of unusual quality (the interactive explainer this book couldn't be in print). The test of a good Project 7: you can't find it assigned anywhere, and you can explain in three sentences why *you* cared.

**Acceptance criteria.** One: you asked it. Two: you answered it with evidence. Three: it's public. Whether it's "significant" is not yours to judge and is the wrong metric — the apprenticeship ends not when you produce significance but when you can *originate*: notice a question, size it, pursue it, and report honestly what you found. That capability, compounded over years, is the entire difference between someone who knows the field and someone in it.

**What it proves.** Chapter 59.8's checklist, final line: capable of independent research. The next part is logistics.

> [!research] The portfolio, assembled
> Projects 1–5 form one coherent story a hiring manager or admissions committee can read in an hour: you built the stack from simulator to compiler, verified everything, and measured what you built. Project 6 proves you can engage the literature. Project 7 proves you can originate. Together: the strongest credential a self-taught quantum engineer can hold in 2026 — stronger than most coursework, weaker than nothing except doing it. Estimated total calendar time at weekend pace: 18–24 months, interleaved with Part XIX's schedule — which is exactly where the projects are placed.
