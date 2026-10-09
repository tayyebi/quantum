# Part XII — Quantum Computer Engineering

*Author: GLM-5.3*

Everything so far treated the quantum computer as an ideal machine. It is not, and the discipline of turning elegant circuits into instructions that survive real hardware is *quantum computer engineering* — compiler construction, scheduling, and optimization over a substrate with constraints no classical compiler has ever faced. This part is the natural home for a software engineer: the tools are the ones you already own (parsing, IRs, graph algorithms, cost functions, test suites), applied to the most interesting target architecture in computing. It ends with the part's defining project: your own toy quantum compiler.

## 44. From Algorithm to Hardware

*Author: GLM-5.3*

> [!levels] In this chapter
> **Lv1** you learn what stands between a circuit diagram and machine execution: gate sets, connectivity, scheduling. **Lv2** you can name each constraint quantitatively (gate fidelity, coherence budget, coupling degree). **Lv3** you can decompose abstract gates into native ones and estimate the cost inflation. **Lv4** you understand pulse-level control as the layer beneath gates, and when it matters. **Lv5** you see the whole pipeline as a systems-design problem with interfaces — and know where its open research seams are.

### 44.1 Logical Circuit

The pipeline's front door: the algorithm-level circuit as written in Part VII — arbitrary gate sets, all-to-all connectivity, no noise. This "logical circuit" is a fiction, but a load-bearing one: it is the interface between algorithm designers and everything below. Its units of account are abstract (T gates, Toffolis, arbitrary rotations); its assumptions (uniform connectivity) are exactly what hardware violates. The compiler's job, formally stated: transform the fiction into a schedule of native operations on physical qubits, minimizing a cost function (depth, two-qubit count, T-count, expected error) while preserving the unitary (up to global phase) — and later, in fault-tolerant machines, doing all of it at the logical layer instead.

### 44.2 Hardware Constraints

The non-negotiables a compiler must respect. Finite coherence: T1/T2 of tens–hundreds of microseconds cap total circuit duration. Gate errors: ~0.1% one-qubit, ~0.3–1% two-qubit — error *budgets*, not absolutes: a 1,000-gate circuit on 0.5% two-qubit errors has almost no signal left. Limited connectivity: degree 2–3 per qubit on superconducting lattices. No mid-circuit branching (mostly): control flow is classical-post or limited dynamic circuits. Calibration drift: today's optimal schedule is tomorrow's mediocre one. And the meta-constraint: *all constraints bind simultaneously* — optimizing depth into a fidelity cliff is a classic beginner pass.

### 44.3 Gate Sets

Every backend exposes a native gate set: IBM's {RZ, SX, X, ECR/CZ}, ion traps' {arbitrary R rotations, MS gates}, Google's {sqrt(X), CZ}. Universal sets (Part III) guarantee expressiveness; *efficiency* differs hugely — circuits on ion traps compile with fewer two-qubit gates (all-to-all helps) but slower gate clock. The compiler's basis-translation pass maps your gates onto natives, and the choice among equivalent decompositions (two CX vs three CZ equivalents, rotation merging) is where real depth is won. T-gates deserve special billing: in fault-tolerant machines they are the expensive non-Clifford resource, so *T-count* is the metric algorithm optimizers chase (28.7's qubitization is the champion).

### 44.4 Connectivity

The coupling graph is a hardware fact: IBM heavy-hex (degree 2–3), Google square grid, trapped-ion all-to-all (within a trap), neutral-atom reconfigurable (atoms moved optically!). Compiler consequence: any gate between non-adjacent qubits needs routing — SWAP insertion or state teleportation — and on heavy-hex, routing overhead routinely doubles–triples circuit depth. The *mapping* problem (44.7/45.7): which logical qubit lands on which physical qubit — is NP-hard, heuristic-solved (SABRE in Qiskit), and sensitive enough that good mapping alone can halve your error rates. For ion traps the problem inverts: routing is free, but the linear trap makes two-qubit gates queue.

### 44.5 Native Gates

Native gates are what the control electronics actually implement — shaped microwave or laser pulses calibrated per qubit, per gate, per day. Everything else is a lie the compiler tells in their language. Properties to track: fidelity (per-qubit, per-gate), duration (35 ns X gates, ~300–600 ns two-qubit, ~600 ns measurement on transmons), and *spectator errors* (gates on neighbors perturb idling qubits — real compilers increasingly schedule around it). The abstraction is leaky in both directions: below it, optimal-control research designs better pulses; above it, circuit optimization must not destroy patterns the pulse layer implements well (e.g. echoed cross-resonance).

### 44.6 Circuit Decomposition

Turning abstract gates into native ones, optimally. Known results: any n-qubit unitary needs O(4ⁿ) two-qubit gates in general (Shende–Markov–Bullock), so *structure* is everything — controlled rotations, multi-controlled Toffolis (L-method, ~100 basic decompositions in Qiskit's library each with different gate-count/depth/ancilla tradeoffs), Pauli exponential rotations (the workhorse of chemistry circuits, Ch. 48), and ZX-calculus-based synthesis (the 2020s' sharpest tool — PyZX rewrites circuits as graph-like diagrams and synthesizes back with provably near-optimal two-qubit counts). Decomposition is where math meets compiler engineering most directly; ZX-calculus fluency is a differentiator for anyone entering compiler research.

### 44.7 Scheduling

Given a routed, native-gate circuit, produce a timeline: which gate starts when, on which control channel, respecting dependencies and hardware timing rules. ASAP/ALAP schedules give depth bounds; insertion of *delays* is unavoidable because parallelism is imperfect — and every delay is decoherence time bought and paid for. Advanced scheduling is noise-aware: align idle qubits with dynamical decoupling sequences (44.8), respect crosstalk groups, order gates to keep fragile states short-lived. Timing on real hardware is measured in nanoseconds against a shared reference clock — a domain where quantum engineering collides head-on with classical digital design, and the skill transfer for RTL-background engineers is nearly total.

### 44.8 Pulse-Level Control

Below gates live pulses: the actual waveforms (Gaussian-square flux tones, DRAG-corrected microwave envelopes) whose area and phase implement rotations. Qiskit exposes this layer (`pulse` schedules, now folding into the Qiskit Dynamics ecosystem), and it matters in three places: calibration (Rabi/Ramsey experiments *are* pulse experiments — Part XI), optimization (shorter/better pulses directly raise fidelity), and dynamical decoupling (XY4/CPMG pulse sequences inserted into idle periods cancel low-frequency noise — a compiler pass that runs physics, not algebra). You cannot touch hardware pulses from a laptop without an account, but Aer models their imperfection, and Chapter 17's simulator can, too. Pulse literacy separates serious compiler work from toy compilers.

## 45. Quantum Compilation

*Author: GLM-5.3*

> [!levels] In this chapter
> **Lv1** you see a quantum compiler as the same animal as clang or rustc: front end → IR → passes → backend. **Lv2** you know the standard passes and their order. **Lv3** you understand the optimization passes' mathematics — cancellation, commutation, peephole rules — well enough to implement them. **Lv4** you can build a compiler with a pluggable pass manager and measure it (cost functions, 45.10). **Lv5** you know the research frontier: noise-adaptive compilation, ZX-based synthesis, compiler-correctness proofs for quantum code.

### 45.1 What a Quantum Compiler Does

One sentence: transform a logical circuit into a hardware schedule, preserving semantics (the unitary, up to global phase), minimizing a cost function under hardware constraints. Same contract as classical compilers, three twists: semantics is a *matrix*, not a program behavior (correctness = unitary equivalence, checkable by simulation at small n — a gift); the cost function is *physical* (error probability ≈ Σ per-gate errors, plus decoherence ∝ depth); and the hardware description itself is mutable data (calibration drift means the backend "target" is a snapshot, and compiling twice a day apart can differ). Qiskit's `PassManager` is the reference architecture; QIR (LLVM-based) and OpenQASM 3 are the interop layers.

### 45.2 Parsing

Front end: read circuits in OpenQASM 2/3 (the field's lingua franca — human-readable, hardware-honest with its `gate` definitions), Qiskit's Python API (the de facto authoring format), QIR (LLVM bitcode for the LLVM-generation tools), or vendor formats. A parser must handle: gate *definitions* (user-defined macros expanding to primitives), parameter expressions (θ/2 arithmetic — symbolic, resolved at compile time), barriers (scheduling fences), and classical registers + control flow (OpenQASM 3's `if`/`while` — dynamic circuits). Your toy compiler (end of part) parses the 17.10 format, extended with parameters; parsing well-designed input formats is 20% of compiler effort and 80% of interop pain.

### 45.3 Intermediate Representations

The IR is where passes live. Options, honestly compared: DAG circuits (Qiskit's `DAGCircuit` — nodes are operations, edges are data dependencies; the workhorse, since gate commutation and cancellation become graph operations), ZX-diagrams (category-theory-flavored graphs; rewrites are sound local moves; the most powerful *optimizing* IR), tensor networks (compilation-as-contraction, niche but growing), and QIR's SSA-flavored form (for embedding in classical toolchains). Design lesson from classical compilers, fully applicable: passes should be small, composable, individually testable, and the IR should make invalid circuits unrepresentable. You will implement a DAG IR in the project; the exercise generalizes.

### 45.4 Gate Decomposition

The algebraic core (44.6 made practical): basis translation via KAK/Cartan decomposition (any two-qubit gate → ≤3 CX + singles; Qiskit `TwoQubitBasisDecomposer`), Euler-angle decomp for single-qubit gates (ZXZ is native-friendly for IBM, XYX elsewhere), rotation merging (`RZ(a)·RZ(b) → RZ(a+b)` — free depth), and multi-controlled gate synthesis choosing among tradeoffs (no ancilla = more gates; ancillas = fewer but wider). The pass must be *conservative*: decompositions differ in noise profile, and the "shortest" decomposition is not always the best-echoed. Test every decomposition with `Operator(equivalence)` checks — matrix equality up to global phase is a one-liner, and it is your proof of correctness.

### 45.5 Optimization

The peephole heart. Rules worth implementing: adjacent-gate cancellation (X·X = I; H·H = I; CX·CX = I — pattern-match on the DAG), rotation merging across barriers' absence, commutation-gated cancellation (slide X past a control it commutes with, then cancel — the classic `Optimize1qGatesDecomposition` win), identity deletion of zero-angle rotations, and template matching (precomputed small-circuit equivalences, rewrote-in-place). Yield on real circuits: 20–40% depth reduction before routing; more after, since routing creates adjacent-gate garbage. All rules are mathematically justified equivalences — implement each with its own unit test (matrix equality), because one unsound peephole rule silently corrupts every downstream computation.

### 45.6 Routing

Making the circuit fit the coupling graph. The standard: SWAP insertion — to run a two-qubit gate between non-adjacent qubits, insert SWAPs along the shortest path, then track the accumulating permutation of logical→physical mapping. The search space is huge (which qubits to swap, in what order), so heuristics rule: SABRE (swap-map bidirectional heuristic — Qiskit's default) scores candidate swaps by look-ahead decayed distance. Smarter variants: bridge gates (4 CX emulate a remote CX without full swap), remote CNOT via teleportation (needs entanglement budget — real in fault-tolerant machines), and Pauli-network routing (commute CX-rich chemistry circuits into routable order first — enormous wins, see 46.5). Measure routing by SWAP count *and* resulting depth; they disagree.

### 45.7 Qubit Mapping

Where each logical qubit initially lands — chosen before routing, tuned with it. The optimizer's information: per-qubit T1/T2, per-gate fidelities (calibration data varies 2–3× across a chip!), coupling quality. Layout scoring heuristics: noise-adaptive layout (Qiskit's `VF2Layout`/`NoiseAdaptiveLayout`) picks the best-error-rate subgraph matching your circuit's interaction shape; mapping a line-shaped circuit onto a line-shaped subgraph of heavy-hex avoids most routing. The underappreciated lever: identical circuits on different layouts differ 2–5× in success probability — free performance, no algorithm change, just a better `initial_layout`. Always benchmark layout choice on your actual workload; defaults are averages, and your circuit is not average.

### 45.8 Scheduling

From gate list to timeline (44.7's engineering view, here the compiler's): compute ASAP/ALAP times over the DAG with real gate durations; insert delays on idle qubits; optionally schedule *deliberately* — align independent layers to enable dynamical decoupling insertion (46.6's cousin), batch two-qubit gates within crosstalk constraints, respect measurement windows. Output formats: the scheduled DAG, or `pulse` schedules at the bottom layer. The metric is not just depth but *idling time distribution* — a circuit can be depth-optimal and still die because one qubit idles 2 µs. Scheduling against decoherence is where quantum compilation most plainly becomes systems engineering; Gantt-chart your circuits (Qiskit's timeline drawer) at least once to feel it.

### 45.9 Noise-Aware Compilation

The modern frontier: compile *for the noise*, not just against it. Ingredients: a noise model (from calibration: per-gate error, T1/T2, readout error per qubit — or learned, see Ch. 61), cost functions that estimate *total circuit error* (not gate count), and passes that use it: noise-adaptive layout (45.7), fidelity-aware routing (prefer swaps through clean couplers), dynamical decoupling tailored to the noise spectrum, and echo/pulse-stretching choices per gate instance. The 2020s research wave — including ML-based compilation policies — lives here. Honest caveat: calibration data is a snapshot of a drifting machine; noise-aware gains are real but must be re-earned each run. Your benchmark harness should re-pull calibration data every experiment.

### 45.10 Compilation Cost Functions

You cannot optimize what you cannot score. The menu, from cheap to honest: gate count (fast, dumb), depth (better, still physical-fiction), two-qubit gate count (the standard proxy — dominates error), Σ per-gate error over the schedule (needs calibration data; the practical standard), full noisy simulation of the compiled circuit (small n only), and expected logical error under a code model (fault-tolerant era). Benchmarking discipline (46.8): fix the metric, fix the input set (a standard circuit zoo: QFT, adders, Grover instances, chemistry ansätze), report distributions over seeds (routing heuristics are randomized!), and always compile with *your* cost function in mind — compilers game any metric they're given, including yours.

## 46. Quantum Transpilation

*Author: GLM-5.3*

> [!levels] In this chapter
> **Lv1** you know transpilation as compilation specialized to re-targeting hardware. **Lv2** you can walk a circuit through Qiskit's preset pass managers and predict each stage's output. **Lv3** you implement the key algorithms yourself: SWAP routing, commutation analysis, peephole rewriting. **Lv4** you benchmark transpilers properly — same metric, same circuits, distributions not point estimates. **Lv5** you can evaluate the frontier: machine-learned pass selection, ZX-native compilation, and the fault-tolerant compiler stack (magic-state scheduling, lattice surgery compilation).

### 46.1 Hardware Topology

The transpiler's model of the machine: `Target` objects encoding the coupling map, native gate set with per-qubit (gate, qubits) → (error, duration) entries, timing constraints, and measurement properties. Building topology-aware intuition: draw heavy-hex for n=7,127; find its degree-2 rim; check which qubit pairs share a coupler with good ECR fidelity. Topology decides everything downstream: a circuit is "shallow" only relative to a topology. Also model the *dynamics*: topologies differ across vendors (lattice vs all-to-all vs reconfigurable neutral atoms), and Part XI's platform chapter explains why — the transpiler sees only the graph, but choosing *which* graph to buy is a strategic decision made with it.

### 46.2 Swap Insertion

The routing workhorse, implemented honestly: given coupling graph G and a two-qubit gate on non-adjacent (a,b): compute shortest paths, choose a swap sequence minimizing (swaps so far + distance lookahead), apply swaps to the running layout, emit the gate, update the layout map. Beware the classic bugs: forgetting to permute *measurements* along with the layout (your histogram comes out permuted — always test with output-bit-sensitive circuits), double-swapping (SWAP = 3 CX; adjacent swaps cancel — a peephole pass catches it), and direction-fixing (some couplers are directional; CX(a,b) may need Hadamard-conjugation to CX(b,a) — 1 H on each side, free, and easily forgotten). Benchmark SABRE vs naive shortest-path: the gap is why Qiskit ships the former.

### 46.3 Circuit Depth

Depth as the transpiler's observable: measure before/after each pass; regressions localize broken passes instantly. Depth-reducing passes worth knowing by name: gate parallelism across layers (the layered `depth()` model), direction-fixing fused with commutation, single-qubit gate resynthesis after routing (routed circuits accumulate串 strings of rotations on each qubit — resynthesize each string as one Euler triple), and Pauli-evolution reordering for chemistry-style circuits (commuting-Pauli blocks can execute in any intra-block order — schedule greedily by topology). Report depth *and* two-qubit depth separately: on hardware, only the latter costs real error.

### 46.4 Gate Cancellation

The safest optimization class: removing adjacent inverse pairs, sound by inspection. Implementation on the DAG: scan for `op; op⁻¹` on the same qubits (X, H, S†·S, CX(a,b)·CX(a,b)), remove, iterate to fixpoint. Power comes from commutation pre-passes: X commutes with CX controls and with Z-rotations — slide it through, meet its twin, cancel both. Self-inverse patterns recur after every routing pass (SWAP·SWAP = I, CX pairs from direction fixing), so run cancellation *after* routing, not only before — the preset pass managers encode this order, and now you know why. Each rule gets a two-circuit test: input, expected output, `Operator` equivalence assertion. Boring, sound, and worth 15–30% of real circuits.

### 46.5 Commutation

The algebraic engine under optimization. Two gates commute if their matrices do — then they may be reordered, enabling cancellation, parallel scheduling, and routing freedoms. Implementable pragmatically: Pauli-word gates (Z-rotations, CX, CZ) have clean commutation rules computable in O(1) from their Pauli labels (anticommute on an odd number of overlapping non-I positions ⇒ commute on even); general gates fall back to matrix checks at small width. The payoff ceiling is Pauli-network compilation for quantum chemistry: commuting-block ordering + diagonalization turns naive L-but-deep chemistry circuits into topology-native ones, often 5–10× two-qubit-count reductions (a 2020s result your laptop can reproduce on small ansätze). Commutation is the difference between pattern-matching compilers and algebra-aware ones.

### 46.6 Peephole Optimization

Local rewrite rules, compiler-classic style: match a small subcircuit pattern, replace with an equivalent cheaper one. The quantum twist: equivalence checks are *free* (matrix equality at width ≤ 3), so a peephole engine can *verify its own rules at load time* — build the rule table, assert every rewrite's Operator equality in CI, and the unsound-rule bug class vanishes. Rule sources: hand-written (the cancellations of 46.4), enumerated (search all k-gate circuits on ≤2 qubits for equivalences — an afternoon project that finds real rules), or mined from synthesis (46.7's optimal small-block tables). Guard rails: peepholes must respect barriers and measurement boundaries, and only rewrite within the same qubit set.

### 46.7 Synthesis

Bottom-up construction: build optimal small blocks once, reuse everywhere. Optimal 1q runs: every 1-qubit string resynthesizes to ≤ 3 rotations (Euler); optimal 2q blocks: enumerate minimal-CX implementations per target unitary (KAK gives the lower bound; lookup tables make it fast); Toffoli synthesis: 6 CX (3 with ancilla, if clean ancillas are free — the evergreen tradeoff); state preparation: O(2ⁿ) in general but poly for sparse/real-amplitude states (relevant to chemistry initial states). Synthesis tables double as peephole *oracles*: any subcircuit matching a table key gets the optimal rewrite — the route by which "optimal" propagates upward through a compiler. This is also exactly how the fault-tolerant era compiles (lattice-surgery scheduling = synthesis at the logical layer).

### 46.8 Benchmarking Transpilers

Make claims falsifiable. Protocol: fix a circuit corpus (BenchPress/QASMBench are public), fix hardware targets (real backend snapshots — pin the calibration date), fix the metric stack (two-qubit count, depth, estimated error Σ, and *sampled success rate* on noisy simulation for n ≤ 20), run each compiler configuration over ≥ 20 seeds, report median and interquartile range — routing and layout are randomized algorithms, and single-run comparisons are noise. Then ablate: your routing vs Qiskit's, your peepholes on/off, level 3 vs your pipeline. You will discover what every compiler engineer learns: default presets are strong, and your wins will be *situational* — usually topology- or workload-specific. That's fine: situational wins are exactly what production compilation needs.

> [!research] Compilers in the fault-tolerant era
> Today's transpilation targets noisy physical qubits; the 2030 target is compilers for *logical* circuits running on error-corrected machines — a different beast: gates become lattice-surgery operations or magic-state injections (routed through distillation factories with their own traffic patterns), the "gate set" is {Cliffords, T via distillation, measurements}, and the cost function is spacetime volume of the code plus factory throughput. Open problems: compiling large T-count circuits into factory schedules without deadlock, ZX-calculus as the native IR for lattice surgery, and verifiable compilation — machine-checked proofs that the compiled logical circuit equals the source (Lean/Coq efforts are young). A compiler engineer entering now has a rare luxury: the classical-compiler playbook exists, the quantum targets are new, and almost nothing is settled.

## Project — Build a Toy Quantum Compiler

*Author: GLM-5.3*

**Goal.** An end-to-end compiler pipeline — parse → DAG IR → optimize → route to a coupling map → synthesize to a native gate set → benchmark — that measurably improves real circuits and is verifiably correct at every pass.

**Deliverables.**
1. `qcc/` package: `parser.py` (17.10 format + parameter expressions θ/2), `dag.py` (DAGCircuit: nodes, edges, topological iteration), `passes/` (`cancel_inverse.py`, `commute.py`, `merge_rotations.py`, `route_sabre.py`, `direction_fix.py`, `euler_resynth.py`), `target.py` (coupling map + gate set + per-gate error model), `cost.py`, `benchmark.py`.
2. Pipeline driver with pluggable pass list and per-pass stats (gates, depth, 2q-count, est. error).
3. Test suite: per-pass `Operator`-equivalence tests (correctness), differential tests vs Qiskit `transpile` on 10 circuits, property test "output unitary ≡ input unitary up to global phase" for the whole pipeline.
4. `REPORT.md`: benchmarks on QFT-n4/5, Grover-3-qubit, 4-bit adder, GHZ chains — your pipeline vs Qiskit O0–O3, ≥20 seeds, medians + IQR, two figures.

**Milestones.**
- M1: parser + DAG + equivalence checking harness (the correctness foundation — build it first).
- M2: cancellation + rotation merging (46.4) passing equivalence tests, ≥10% gate reduction on QFT.
- M3: routing on a 7-qubit heavy-hex map with layout permutation tracking, measurements permuted correctly (46.2's classic bug — test it by name).
- M4: commutation + resynthesis (46.5–46.7), parity or better with Qiskit O1 on the corpus.
- M5: benchmark report with honest error bars (46.8).

**Acceptance criteria.** Pipeline output is unitary-equivalent to input on all tests; measured-layout histograms match expected permutations; report shows your compiler beating O0 and being honestly compared to O2/O3; every pass independently unit-testable via a documented interface.
