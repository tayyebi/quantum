# Appendices

Reference material for the whole book: notation, gate tables, checklists, and reading lists. These are working pages — skim once, then return as needed. Where a table cell would need structure (matrices, multi-line facts), the appendix uses text blocks instead.

## Appendix A — Linear Algebra Reference

The working minimum, in the book's notation. **Vectors**: a state of n qubits is a vector ψ in ℂ²ⁿ; column by convention; ⟨ψ| is the conjugate-transpose (row). **Inner product** ⟨φ|ψ⟩ = Σ φᵢ*ψᵢ — measures overlap; states are normalized ⟨ψ|ψ⟩=1; orthogonal states are perfectly distinguishable. **Outer product** |φ⟩⟨ψ| is an operator (maps |ψ⟩-direction into |φ⟩-direction). **Matrices as operators**: (AB)|ψ⟩ = A(B|ψ⟩); non-commutative AB≠BA in general — the source of uncertainty and much else. **Unitary**: U†U = I — preserves inner products (lengths, angles, probabilities); all quantum gates. **Hermitian**: A = A† — real eigenvalues; all observables. **Eigen-decomposition**: A|vᵢ⟩ = λᵢ|vᵢ⟩; for Hermitian A the eigenvectors form an orthonormal basis — measurement returns eigenvalues, collapses onto eigenvectors. **Tensor product**: (A⊗B)(|φ⟩⊗|ψ⟩) = A|φ⟩⊗B|ψ⟩; dimension multiplies: n-qubit operators are 2ⁿ×2ⁿ. **Trace**: tr(A) = Σ Aᵢᵢ; tr(|φ⟩⟨ψ|) = ⟨ψ|φ⟩; density matrices live on traces (Appendix H). **Spectral norm / fidelity**: ‖A‖ = max eigenvalue of √(A†A); used in error bounds. A one-line numpy check for every claim above: instantiate at dimension 2–4 and assert.

## Appendix B — Complex-Number Reference

Complex numbers in one page. **Form**: z = a+bi, i²=−1; conjugate z* = a−bi; modulus |z| = √(zz*) = √(a²+b²); argument arg(z) = atan2(b,a). **Polar**: z = |z|e^{iθ} — the amplitude's phase θ is what interference machinery manipulates; |z|² is what measurement sees. **Euler**: e^{iθ} = cos θ + i sin θ; the global phase e^{iθ}|ψ⟩ is physically identical to |ψ⟩; *relative* phases between components are physical. **Arithmetic**: multiply → moduli multiply, arguments add ((|z₁|e^{iθ₁})(|z₂|e^{iθ₂}) = |z₁z₂|e^{i(θ₁+θ₂)}) — the entire mechanism of phase kickback and QFT. **Born rule**: probability of outcome k = |αₖ|² — modulus squared, killing the phase; phases matter only through interference before measurement. numpy: `np.angle(z)`, `np.abs(z)**2`, complex128 everywhere; silent dtype bugs are 90% of first-week quantum-coding errors.

## Appendix C — Bra-Ket Notation Reference

Dirac notation, decoded. **Ket** |ψ⟩: a column vector — a state. **Bra** ⟨φ|: its conjugate transpose — a row vector, an unfired question. **Bra-ket** ⟨φ|ψ⟩: inner product — "how much φ in ψ"; 0 ⇒ orthogonal (perfectly distinguishable); 1 ⇒ identical. **Ket-bra** |φ⟩⟨ψ|: outer product — an operator; |φ⟩⟨φ| is the projector onto φ (measurement's mathematical action: ρ → |φ⟩⟨φ|ρ|φ⟩⟨φ|). **Computational basis**: |0⟩=(1,0)ᵀ, |1⟩=(0,1)ᵀ; n-qubit |bₙ₋₁…b₀⟩ = tensor of bits; index = the integer the bits encode. **Common named states**: |+⟩ = (|0⟩+|1⟩)/√2, |−⟩ = (|0⟩−|1⟩)/√2, |i⟩=(|0⟩+i|1⟩)/√2, Bell states (|00⟩±|11⟩)/√2, GHZ (|0…0⟩+|1…1⟩)/√2. **Operator elements**: ⟨φ|A|ψ⟩ — "the amplitude of φ after A acts on ψ"; ⟨0|X|1⟩ = 1 reads "X maps 1 into 0, amplitude 1." **Subtleties**: ⟨ψ|ψ⟩ ≠ |ψ⟩⟨ψ| (number vs. operator); tensor order is convention (Ch. 16.11's endianness); phases: |ψ⟩ and −|ψ⟩ identical, |0⟩+|1⟩ vs |0⟩−|1⟩ maximally different.

## Appendix D — Probability Reference

The quantum-relevant subset. **Distributions**: pᵢ ≥ 0, Σpᵢ = 1; quantum outcome distributions are pᵢ = |αᵢ|². **Expectation**: ⟨O⟩ = Σ pᵢoᵢ; quantum version ⟨ψ|O|ψ⟩ for observable O with eigenvalues oᵢ. **Variance** σ² = ⟨O²⟩−⟨O⟩²; standard error of an N-shot mean: σ/√N — the shot-budget formula (Ch. 16.10): to estimate a probability to ±δ needs N ≈ p(1−p)/δ² shots. **Conditional**: P(A|B) = P(A∩B)/P(B); measurement collapse is conditioning in disguise. **Bayes**: P(H|E) ∝ P(E|H)P(H) — decoder belief updating (Ch. 36) is Bayes on syndromes. **Correlation vs. causation, quantum edition**: entangled correlations exceed classical bounds (Bell) yet signal nothing (Ch. 2.10) — the one place naive probability fails and quantum probability takes over. **Sampling**: multinomial for shot outcomes; bootstrapping over seeds for error bars on benchmarks (Ch. 46.8). **Distributions you'll meet**: binomial (k successes in n shots), Gaussian (CLT limit), exponential (T1 decay), Poisson (rare-event counts — dark counts in Ch. 65 detectors).

## Appendix E — Common Quantum Gates

The working gate table — symbol, matrix, action, and notes. Single-qubit:

```text
I    = [[1,0],[0,1]]                     identity / idle (still decoheres)
X    = [[0,1],[1,0]]                     bit flip; X|0⟩=|1⟩; NOT
Y    = [[0,−i],[i,0]]                    bit+phase flip
Z    = [[1,0],[0,−1]]                    phase flip; Z|1⟩=−|1⟩
H    = (1/√2)[[1,1],[1,−1]]              basis change Z↔X; H|0⟩=|+⟩
S    = [[1,0],[0,i]]                     phase gate; S=S†† (Clifford)
T    = [[1,0],[0,e^{iπ/4}]]              π/8 gate; NON-Clifford — the costly one
RX(θ), RY(θ), RZ(θ)                      axis rotations; RZ(θ)=e^{−iθZ/2}
```

Two-qubit:

```text
CX   = |0⟩⟨0|⊗I + |1⟩⟨1|⊗X    control-not; entangles; universal with 1q gates
CZ   = |0⟩⟨0|⊗I + |1⟩⟨1|⊗Z    symmetric; CX = (I⊗H)CZ(I⊗H)
SWAP = exchanges two qubits    = 3 CX; physical in some platforms
ECR, iSWAP, √X-variants        native on specific hardware (Ch. 44.5)
```

Three-qubit: Toffoli/CCX (universal reversible classical logic; 6 CX); CSWAP/Fredkin. Universality: {H,S,CX,T} suffices; any dense 1q-pair + entangling 2q gate suffices (Ch. 7). Costs to memorize: 1q ≈ free, CX ≈ 10× a 1q error, T ≈ 10³× under FTQ (Ch. 79.3).

## Appendix F — Common Quantum Algorithms

The canon, one line each (details in Part VII chapters cited): **Deutsch** (Ch. 19) — one query decides f(0)⊕f(1); first quantum win. **Deutsch–Jozsa** (20) — constant vs. balanced, one query, deterministic. **Bernstein–Vazirani** (21) — recovers hidden string a exactly, one query. **Simon** (22) — hidden XOR mask via QFT-period structure; Shor's direct ancestor. **QFT** (23) — quantum Fourier transform, O(n²) vs classical FFT's O(n2ⁿ); periodicity extractor. **Phase estimation** (24) — eigenphases to k bits; simulation and Shor's engine. **Grover** (25) — √ search speedup, provably optimal (BBBV). **Shor** (26) — factoring/discrete-log in quantum polynomial time; the applications-world earthquake (Ch. 51). **VQE** (49) — variational ground states; NISQ's hello-world. **QAOA** (49) — variational combinatorial optimization. **HHL** (49.5-adjacent) — linear systems under heavy caveats. **Quantum walks, amplitude amplification/estimation, QSVT/qubitization** (28.7–28.8, 79) — the modern primitive layer. Selection rule from Ch. 28: structural (exponential) vs. generic (quadratic) vs. sampling vs. simulation — classify before quoting.

## Appendix G — Pauli Matrices

The four letters everything is written in:

```text
I = [[1,0],[0,0+1]]    X = [[0,1],[1,0]]    Y = [[0,−i],[i,0]]    Z = [[1,0],[0,−1]]
```

**Algebra**: X²=Y²=Z²=I; XY=iZ (and cyclic: YZ=iX, ZX=iY); anticommute: XY=−YX. **Observables**: Z measures computational basis (eigen ±1), X measures {|+⟩,|−⟩}, Y the imaginary-axis basis. **Hamiltonians**: H = Σₖ hₖ Pₖ with Pauli *strings* Pₖ ∈ {I,X,Y,Z}⊗ⁿ — the universal decomposition (Ch. 47.2). **Commutation rule for strings**: P, Q commute iff they anticommute on an even number of positions — O(1) check, the engine of Ch. 46.5's optimization. **Clifford group**: maps Paulis to Paulis under conjugation (UPU† ∈ Paulis) — generated by {H,S,CX}; stabilizer formalism (Ch. 32) is Pauli-string bookkeeping; Gottesman–Knill (Ch. 17.14) makes Clifford circuits classical. **QEC**: errors *are* Paulis; syndromes *are* stabilizer measurements; decoding is Pauli inference (Ch. 36). **Stabilizer states**: unique +1-eigenstates of maximal commuting Pauli groups — the states QEC can hold. If you internalize one algebra deeply, make it this one.

## Appendix H — Quantum Channels

Noise, formalized (Ch. 29–31's dictionary). A channel ℰ is a completely-positive trace-preserving map; three equivalent pictures: **Kraus** ℰ(ρ) = Σₖ KₖρKₖ† (ΣK†ₖKₖ=I) — the implementation view; **Stinespring** ℰ(ρ) = tr_E[V ρ V†] — the physics view (unitary on a bigger system, discard environment — noise is entanglement leakage, Ch. 2.12); **Chi/χ process matrix** — the tomography view. The canon, with Kraus structure:

```text
Bit flip p:        {√(1−p)I, √p X}
Phase flip p:      {√(1−p)I, √p Z}
Depolarizing p:    p ρ → I/2 mixtures; Kraus {√(1−3p/4)I, √(p/4)X, √(p/4)Y, √(p/4)Z}
Amplitude damping: {K₀=[[1,0],[0,√(1−γ)]], K₁=[[0,√γ],[0,0]]}  T1 physics; not unital
Phase damping/dephasing: diagonal decay of off-diagonals; T2 physics
Readout error:     classical confusion matrix per qubit (not Kraus on ρ; post-processing)
```

Key properties: unital (ℰ(I)∝I) vs. non-unital (amplitude damping relaxes toward |0⟩); composition = concatenating noise; channel fidelity measures worst/best state survival. Estimation: randomized benchmarking (Ch. 31) estimates gate-channel quality without process tomography's exponential cost. In code (Ch. 68's project): `apply_channel` with Kraus sampling, verified against density-matrix evolution.

## Appendix I — Error-Correcting Codes

The QEC dictionary (Part X's chapters in table form). Codes by [[n,k,d]] — n physical, k logical, distance d (corrects ⌊(d−1)/2⌋ errors):

```text
3-qubit repetition     [[3,1,1(-ish)]]  bit flips only; the concept demo (Ch. 32)
Shor 9-qubit           [[9,1,3]]        first full code; concatenation of the two
5-qubit (Laflamme)     [[5,1,3]]        smallest possible distance-3; deep code
Steane                 [[7,1,3]]        CSS; classical [7,4,3] Hamming doubled
Surface code (rotated) [[2d²,1,d]]      topological; local check; threshold ~1%;
                                        the industrial choice (Ch. 35, Willow)
Color codes            triangular       CSS, transversal gates; layout-hungry
qLDPC                  [[n,k,d]], k>1   high rate; IBM's bet; decoding race (Ch. 79.2)
Bosonic/cat codes      cavity-level     hardware QEC; Alice&Bob, Ocelot (Ch. 80.4)
```

Concepts: **stabilizer group** (abelian Pauli subgroup, −I excluded); **syndrome** (commutation pattern with generators — tells *which* subspace, not *which* state); **logical operators** (Paulis commuting with all stabilizers — the code's vulnerabilities, string-like for surface codes — hence distance from size); **threshold** (physical error below which distance wins — the theorem making everything possible); **decoders** (lookup → MWPM → ML → neural; Ch. 37); **logical gates** (transversal where possible; lattice surgery + magic states where not — Ch. 79). Key numbers to carry: surface-code threshold ~0.5–1% circuit-level; Λ ≈ 10 per distance step at p≈10⁻³; overhead 2d² per logical; T via distillation ≈ 10³–10⁴ physical per logical op.

## Appendix J — Quantum Circuit Notation

The drawing rules, one place (Ch. 15's reference card). Wires horizontal, one per qubit, time →. Gates: labeled boxes (1q), vertical-line-and-symbol (2q: ● = control, ⊕ = X-target, ●—● = CZ), boxed controls over multi-targets for fan-outs. Measurement: meter-gauge symbol → double classical line (or arc-arrow). Barrier: dashed vertical — "do not reorder." Classical control: box on the classical wire with an arrow to the conditioned gate. Special notations: SWAP as ×-crossing; virtual-Z as a tick; reset as a gate-boxed ↦0. Reading discipline (Ch. 15.1): paper diagrams are informal — always reconcile against the text's matrix or code. Text formats: this book's `H 0 / CX 0 1 / M` (Ch. 17.10); OpenQASM 2/3 (the interop standard — `h q[0]; cx q[0], q[1]; measure q → c;`). Qiskit drawing: `qc.draw('text')` terminal-safe, `'mpl'` publication, timeline view for schedules (Ch. 44.7).

## Appendix K — Qiskit Reference

The 10% of the API you use 90% of the time (Qiskit ≥1.0 — pin versions; 0.x code from older tutorials will not run unchanged). Setup: `pip install qiskit qiskit-aer matplotlib`.

```python
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, Operator
from qiskit.primitives import StatevectorSampler
from qiskit_aer import AerSimulator
from qiskit.providers.fake_provider import GenericBackendV2

qc = QuantumCircuit(2, 2)                 # quantum + classical registers
qc.h(0); qc.cx(0, 1)                      # build
qc.measure([0, 1], [0, 1])                # measure (basis-change first for X-basis)

sv = Statevector(qc.remove_final_measurements(inplace=False))
print(sv.probabilities_dict())            # exact, no shots

sim = AerSimulator()
tqc = transpile(qc, sim)
counts = sim.run(tqc, shots=4096, seed_simulator=42).result().get_counts()

backend = GenericBackendV2(7)              # fake heavy-hex device
tqc = transpile(qc, backend, optimization_level=3,
                initial_layout=[0, 1], seed_transpiler=42)
print(tqc.count_ops(), tqc.depth())        # the honest cost report
```

Debugging gold: `Operator(qc).equiv(Operator(target))` (unitary equality up to phase); `plot_histogram`, `plot_bloch_multivector` (Ch. 16.12–16.14). Docs: qiskit.org/documentation — prefer version-pinned tutorials.

## Appendix L — Python Numerical-Computing Reference

Quantum-specific numpy habits (Ch. 17's lessons compressed). dtype: `complex128` everywhere, declared (`np.zeros(2**n, dtype=complex)`); silent upcasting is bug #1. Tensor products: `np.kron(A, B)` — decide endianness once, test it, document it (Ch. 17.6). Fast gate application: reshape state to `(2,)*n`, `np.tensordot(gate, state, axes=([1],[k]))` + `np.moveaxis` (Ch. 17.7). Measurement: `probs = np.abs(state)**2; np.random.default_rng(seed).choice(2**n, p=probs)`. Linear algebra: `np.linalg.eigh` (Hermitian — sorted real eigenvalues; use for observables), `eigvalsh` (values only), `norm`, `vdot` (conjugates first arg — `np.vdot(state, O @ state)` is ⟨ψ|O|ψ⟩). Sparse: `scipy.sparse` for Pauli-string Hamiltonians (n ≤ ~16 dense, sparse beyond); `SparsePauliOp` in Qiskit for the same. Performance: profile first (`cProfile`); the bottleneck is never where intuition says (Ch. 17.11); vectorize over shots, batch over circuits. Reproducibility: `rng = np.random.default_rng(seed)` objects passed explicitly, never global `np.random`. Testing: `np.allclose(a, b)` (and `rtol/atol` set consciously); property tests with fixed seeds.

## Appendix M — Useful Quantum Software

The toolbox, laptop-first (all free; all local unless noted). **SDKs**: Qiskit (this book's default; IBM ecosystem), Cirq (Google), PennyLane (Xanadu — quantum-ML oriented), Braket SDK (AWS). **Simulators**: qiskit-aer (your workhorse), **stim** (Clifford/QEC — thousands of qubits; the Part X engine), Qiskit's stabilizer/MPS methods, **quimb** / ITensor (tensor networks, Ch. 64.2), qsim (Google's fast statevector). **QEC toolchain**: stim (circuit-level noise + sampling), **PyMatching** (MWPM decoder), pymatching/panqec/fault-painter adjacent tools. **Compilers/research**: PyZX (ZX-calculus — Ch. 45.4), Boulder Opal-adjacent open tools (control), OpenQASM 3 tooling. **Chemistry**: Qiskit Nature, **PySCF** (classical integrals — 48.6's pipeline), OpenFermion. **Hardware access**: IBM Quantum platform (free open tier — Ch. 64.7), AWS Braket / Azure Quantum (paid, credits). **Reference/resource estimation**: Azure Quantum Resource Estimator (Ch. 79.4). **Benchmarks**: QASMBench, BenchPress corpora (Ch. 46.8). Selection rule: default to Qiskit+stim+numpy; add per specialization (Ch. 74's list).

## Appendix N — Quantum Hardware Providers

The 2026 landscape (Ch. 38–43 detailed it; this is the who's-who card). **IBM**: superconducting; Heron/Flamingo-class processors, heavy-hex; largest cloud ecosystem; Starling FTQ roadmap (~200 logical by 2029); free open access tier. **Google**: superconducting; Willow lineage — below-threshold QEC demonstrated (2024); research-first access. **Quantinuum**: trapped-ion (H2-class): highest 2q fidelities (99.9%+), all-to-all; premium/commercial access. **IonQ**: trapped-ion; cloud-commercial via Braket/Azure. **QuEra**: neutral atoms; 256-atom Aquila-class; analog + digital; strong Harvard-lineage research program. **Rigetti**: superconducting; modular multi-chip bet. **Pasqal**: neutral atoms (European program). **PsiQuantum**: photonic FTQ — no public access, foundry strategy. **Atom Computing**: neutral atoms. **Xanadu**: photonic (Borealis sampling). Access reality for the Iran-based reader (Ch. 63.10): IBM's free tier is the frictionless channel; paid platforms need payment-rail workarounds with compliance care; all vendors' *published calibration data and papers* are open — benchmark from literature even where queues are closed.

## Appendix O — Important Quantum Papers

A starter shelf, ~thirty papers, book-part by part. Foundations: Einstein–Podolsky–Rosen (1935); Bell (1964, inequalities); Feynman (1982, simulating physics); Deutsch (1985, quantum Turing machine); Shor (1995, code); Grover (1996); Lloyd (1996, universality of simulation). Algorithms: Shor (1994, factoring); Coppersmith (1994, QFT); Kitaev (1995-96, phase estimation/arithmetic); Farhi–Goldstone–Gutmann (2014, QAOA); Peruzzo et al. (2014, VQE); Harrow–Hassidim–Lloyd (2009, HHL); Tang (2019, dequantization). Error correction: Shor (1995); Steane (1996); Knill–Laflamme (1997, conditions); Aharonov–Ben-Or–Kitaev (1997, threshold theorem); Fowler et al. (2012, surface codes practical); Google Quantum AI (2024, Willow below-threshold); Bravyi et al. (2024, qLDPC). Algorithms-era: Gidney–Ekerå (2019) and Gidney (2025) (factoring resources); McClean et al. (2018, barren plateaus). Simulating/verification: Arute et al. (2019, supremacy); Havlíček et al. (2019, kernels); Aaronson–Gunn (2019-20, XEB caveats). Reading method: Ch. 52's three passes; start with the ones your reproduction targets (Ch. 53.2), not chronological order.

## Appendix P — Important Researchers and Research Groups

Orientation, not a leaderboard — the names attached to the ideas this book cited, so literature search has handles. Theory/algorithms: **Peter Shor** (factoring, codes), **Lov Grover** (search), **Umesh Vazirani** (complexity; BV, Simon lineage), **Scott Aaronson** (complexity, dequantization-era criticism, complexity zoo), **Dorit Aharonov** (fault tolerance, verification), **Emanuel Knill** (conditions, bounds, Gottesman–Knill), **Daniel Gottesman** (stabilizer formalism), **Peter Zoller** & **Ignacio Cirac** (theoretical foundations of trapped-ion and repeater physics), **John Preskill** (NISQ, QEC theory, the field's great communicator), **Ronald de Wolf** (quantum querying/learning theory). QEC/decoding: **Austin Fowler** (surface code engineering), **David Poulin**, **Barbara Terhal** (thresholds, bosonic codes), **Earl Campbell** (qLDPC decoding). Experimental: **John Martinis** (superconducting lineage), **John Clarke**, **Michelle Simmons** (silicon), **Christopher Monroe** & **Rainer Blatt** (trapped ions), **Mikhail Lukin** & **Markus Greiner** (neutral atoms), **Anton Zeilinger** & **Alain Aspect** & **John Clauser** (Bell tests, Nobel 2022). Groups: Google Quantum AI, IBM Quantum, NIST Boulder, QuTech (Delft), IQOQI (Innsbruck), MIT/Harvard quantum centers, Oxford/Cambridge groups, Weizmann, IHEP-adjacent (USTC Hefei — China's hub). Ch. 62.7's method applies to all of them: read three papers, write one good email.

## Appendix Q — Quantum Computing Terminology

Working glossary (FA readers: Farsi equivalents in the FA edition). **Amplitude** — complex weight of a basis state; squared → probability. **Ancilla** — workspace qubit, must return to |0⟩. **BQP** — polynomial-time quantum with bounded error. **Barren plateau** — vanishing gradients in variational circuits. **Bell state / Bell test** — maximal entanglement / inequality violation certifying nonclassicality. **Bloch sphere** — single-qubit state geometry. **Clifford / non-Clifford** — Pauli-normalizing gates (cheap, classically simulable) / T and beyond (expensive, universal). **Coherence (T1, T2)** — relaxation / dephasing time. **Coupling map** — hardware connectivity graph. **Decoherence** — environment-induced information leakage. **Density matrix** — mixed-state description. **Depolarizing** — maximally-unbiased noise. **Entanglement** — inseparable joint state. **Fidelity** — closeness of states/operations. **Logical qubit** — error-corrected register. **Magic state** — distilled non-Clifford resource. **MWPM** — minimum-weight perfect matching (decoder). **NISQ** — pre-correction era. **Oracle** — black-box subcircuit. **Phase kickback** — eigenphase-to-register trick. **QEC** — quantum error correction. **qLDPC** — high-rate quantum low-density parity-check codes. **Qubit** — two-level quantum system. **Shots** — circuit repetitions. **Stabilizer** — Pauli string whose +1 eigenspace contains the code space. **Statevector** — full amplitude description. **Superposition** — weighted basis combination. **Syndrome** — error-location signature. **Threshold** — critical physical error rate enabling correction. **Transpilation** — circuit-to-hardware compilation. **Trotterization** — product-formula simulation. **Unitary** — norm-preserving operation. **XEB** — cross-entropy benchmarking. **Λ (lambda)** — logical-error suppression factor per distance step.

## Appendix R — Research-Paper Reading Checklist

Printable — one per paper (Ch. 52 distilled). **Before reading**: why am I reading this — target claim or survey? **Pass 1 (10 min)**: title/abstract → one-sentence claim ("X, demonstrated on Y, vs Z, with statistical strength W"); figures' axes and ranges; conclusion vs. abstract — consistent? **Pass 2 (40 min)**: contribution sentence (delete-from-history test); method extracted; baselines named and judged honest (equal tuning? classical competitor?); regime: theory / ideal sim / noisy sim (which model?) / hardware (which, when — calibration age?); statistical standards: error bars? seeds? pre-registration? **Pass 3 (if it matters)**: math instantiated at n=2; algorithm sketched in code/simulator; supplementary methods + limitations read twice. **Red flags**: missing baselines; "up to N"; best-of-k as mean; log-axis hiding asymptotics; undefined "quantum advantage"; QRAM assumed silently. **Log entry (mandatory)**: claim; contribution; evidence grade (A: reproduced by you; B: verified vs. independent source; C: trusted on reputation; D: unverified); open questions it leaves; relation to your claims matrix. **Follow-up?** → Ch. 53 (reproduce), Ch. 55.2 (gap), or done.

## Appendix S — Project Evaluation Checklist

For every project you build — Part XVIII's and beyond (Ch. 46.8 + 54 + 62's standards in one card). **Correctness**: does a one-command run reproduce the headline result? property tests green (unitaries, oracles, ancilla-cleanliness)? differential tests vs. an independent implementation? **Honesty**: seeds fixed or swept — reported either way; error bars on every claimed number; baselines at equal effort; negative results included, not hidden. **Engineering**: pinned dependencies; tests in CI; README states claim, cost, complexity, and how to verify; code review-clean (another engineer could take it over). **Benchmarks (if performance claims)**: standard corpus; ≥20 seeds; medians + IQR; ablations isolating each contribution; comparison to the strongest available alternative, not the weakest. **Science (if research claims)**: hypothesis pre-registered; regime named; noise model justified with falsifier; statistics per Ch. 54.8. **Portfolio (public-facing)**: figures self-contained (regime, shots, error bars in caption); write-up tells a stranger why it matters in three sentences; license present; the 6-month test — will this still run? **The final question**: if this project's headline number were wrong, would I know? If not, that's the next task.

## Appendix T — Mathematical Prerequisites Checklist

Self-assess before Part III; revisit at Part X and Part XVIII starts. **Linear algebra** (the load-bearing 80%): vector spaces over ℂ; inner products with conjugation; basis and change of basis; linear maps as matrices; matrix multiplication as composition; transpose vs. conjugate-transpose; eigenvalues/eigenvectors; Hermitian and unitary definitions and their consequences; tensor products; trace; projections. Test yourself: compute ⟨ψ|φ⟩ for complex vectors; diagonalize a 2×2 Hermitian by hand; explain why unitary preserves probabilities in one sentence. **Complex numbers** (Appendix B): polar form, Euler's formula, modulus-and-argument arithmetic. Test: compute |e^{iπ/4}|² and (1+i)·e^{−iπ/2}. **Probability** (Appendix D): distributions, expectation, variance, conditional, Bayes, sampling error. Test: how many shots to estimate p=0.5 to ±0.01? (~10⁴ — derive it.) **Trigonometry/exponentials**: sin/cos as circle parameterization; e^{iθ} rotation; small-angle. **Logic/proof literacy**: implication, contrapositive, induction, proof by contradiction — read Ch. 52.5 with these. **Numerics**: floating-point roundoff, absolute vs. relative tolerance, why `allclose` over `==`. Gaps found: Part III covers the quantum-relevant versions of all of the above — the checklist tells you which sections to slow down for, not whether you're allowed to continue. Everyone's checklist has gaps; engineers close them en route.
