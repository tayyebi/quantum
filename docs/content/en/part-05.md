# Part V — Many Qubits

*Author: GLM-5.3*

Composite systems, entanglement, and multi-qubit gates: where the exponential state space appears, where the classical simulators start dying, and where quantum computing starts earning the word "quantum".

## 12. Composite Quantum Systems

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** combining qubits multiplies their possibilities; some combined states have no description "per qubit" at all.
> - **Mathematics —** state spaces combine by tensor product: 2ⁿ dimensions, and separability is the exception, not the rule.
> - **Implementation —** build two-qubit states with np.kron, prepare Bell states, and test separability numerically.
> - **Engineering —** the 2ⁿ wall starts here: 30 qubits is a 16 GB state vector, which is why error correction and hardware exist.
> - **Research —** quantifying entanglement in high-dimensional and noisy systems is an active topic touching physics and complexity theory.

### 12.1 Two-qubit states and the four-dimensional state space

The fourth postulate says composite systems combine by tensor product: a two-qubit state lives in the 4-dimensional space ℂ² ⊗ ℂ², with computational basis |00⟩, |01⟩, |10⟩, |11⟩ — that is, "first qubit, second qubit", not a binary number you can interpret freely. A general state is α|00⟩ + β|01⟩ + γ|10⟩ + δ|11⟩ with four complex amplitudes, Σ|·|² = 1. In numpy, a state vector for qubits ordered q0, q1 is `np.kron(psi_q0, psi_q1)`. Note the bookkeeping shock: one extra qubit doubles the amplitudes you store, while the *classical* description of two bits still needs two bits. The four amplitudes are not four bits of information — measurement still returns two bits total — but they are four numbers your simulator must carry and evolve.

### 12.2 n-qubit state space and exponential growth

Iterating: n qubits span a 2ⁿ-dimensional complex space with 2ⁿ amplitudes. The growth is brutal and worth feeling numerically: 10 qubits → 1,024 amplitudes (16 KB as complex128); 20 → 1 M (16 MB); 26 → 67 M (1 GB); 30 → 16 GB; 40 → 16 TB; 50 → beyond any laptop. This exponential is not a "trick" quantum computers do — it is simply the size of the *description*, and it cuts both ways: it is why classical simulation is a supercomputer-class task past ~45 qubits (yet state-of-the-art tensor-network methods push specific structured circuits far further, Part XIV), and it is the headroom quantum algorithms spend. You have already felt the wall in Part I's memory experiment. From this point on, every algorithm is judged by how it maneuvers inside this space without ever writing it down.

```text
n qubits  ->  2^n complex amplitudes (complex128 = 16 bytes each)

   10 ->     1,024          16 KB      trivial
   20 -> 1,048,576          16 MB      fine
   26 -> 67,108,864           1 GB      laptop limit
   30 -> 1,073,741,824       16 GB      desktop limit
   40 -> ~1.1e12             16 TB      cluster
   50 -> ~1.1e15             16 PB      simulation frontier
```

### 12.3 Product states

The clean case: a **product state** is one whose state vector factors as |ψ⟩₁ ⊗ |ψ⟩₂ — each qubit has a state of its own. |00⟩, |+−⟩ = |+⟩⊗|−⟩, and (α|0⟩+β|1⟩)⊗(γ|0⟩+δ|1⟩) are all product states. Everything you learned for one qubit applies per-qubit: probabilities multiply, gates apply blockwise, entanglement is zero. Product states are also exactly what a classical computer handles cheaply: instead of 2ⁿ amplitudes, you store n two-component vectors — polynomial cost. This is why *structured* circuits (those that keep the state near a product or mildly correlated form) remain simulable at scales far beyond naive limits. The interesting question, then, is precise: which states are *not* of this form, and what can they do? That question is entanglement, next.

### 12.4 Entangled states

An **entangled state** is a multi-qubit state that cannot be written as a tensor product, even after trying every split and every basis: |ψ⟩ ≠ |φ⟩₁ ⊗ |χ⟩₂ for any choices. The canonical example: (|00⟩ + |11⟩)/√2. Neither qubit individually has a state vector at all — each is maximally random alone (50/50 in every basis), yet outcomes are perfectly correlated. This is a genuinely new object, not classical correlation with extra steps: no probabilistic recipe of "pre-agreed instructions" reproduces all of its statistics (13.3 makes that a theorem). Engineering consequence: entanglement is a resource that consumes qubits irreversibly during preparation but then links them with correlations no classical channel provides. Almost everything valuable in this book — teleportation, error-correcting codes, quantum chemistry states — is built from non-product states.

### 12.5 Bell states and Bell-state preparation

The four **Bell states** are the maximally entangled two-qubit states, named after John Bell: Φ⁺ = (|00⟩+|11⟩)/√2, Φ⁻ = (|00⟩−|11⟩)/√2, Ψ⁺ = (|01⟩+|10⟩)/√2, Ψ⁻ = (|01⟩−|10⟩)/√2. They form an orthonormal basis of the 4-dimensional space — a complete alternative "entangled basis". Preparing Φ⁺ is a two-gate recipe you will write a thousand times: apply H to qubit 0, then CNOT from qubit 0 to qubit 1. Read it mechanically: H creates qubit 0's superposition; CNOT copies the *correlation*, not the amplitude (no-cloning survives). The three other Bell states follow by a Z or X (or both) on one qubit. In circuit diagrams this recipe is the standard warm-up, and in hardware it is the first benchmark any two-qubit link must pass.

```text
Bell-state preparation circuit:

  q0:  ──H────●──
              │
  q1:  ───────X──

  |00> -> (|00> + |11>)/sqrt(2) = |Phi+>
```

### 12.6 Bell-state measurement

A **Bell-state measurement** asks "which of the four Bell states am I in?" — projecting two qubits onto the Bell basis. It cannot be done by measuring each qubit separately (that reads the computational basis and destroys the entanglement), but it *is* achievable with gates: apply CNOT(q0→q1) then H on q0, then measure both in the computational basis. That circuit is the inverse of the preparation circuit, which is no accident — basis changes are unitary, and this one maps the Bell basis onto the computational basis. Two applications to hold onto: teleportation (13.5) *is* a Bell measurement whose classical outcome steers a correction; and Bell-state measurements between photons are the workhorse of quantum networking (entanglement swapping, 13.7). On today's hardware it succeeds probabilistically with linear optics; deterministic versions need matter qubits.

### 12.7 Classical versus quantum correlations

Sharpen the distinction with numbers, because it is the conceptual heart of Part V. Classical correlated bits: a source outputs 00 half the time, 11 half the time. Outcomes are correlated, yet each bit has a definite value before you look — the randomness is ignorance about a pre-existing fact. Bell's Φ⁺ looks identical for Z-measurements: 00 and 11 with equal probability. The difference appears when you rotate the measurement basis: measuring both qubits in the X basis also gives perfect correlation, and correlations across *mixed* bases (one X, one Z) violate the bounds any pre-agreed-values model must obey (13.4). A handy numerical signature you can compute tonight: for Φ⁺, the correlation matrix ⟨σᵢ ⊗ σⱼ⟩ over axes i, j ∈ {x, y, z} is diag(1, −1, 1) — a pattern no classical mixture of definite spin directions matches.

> [!experiment] On your laptop — separability and Bell correlations
> ```python
> import numpy as np
>
> ket = [np.array(v, dtype=complex) for v in ([1,0],[0,1])]
> H = np.array([[1,1],[1,-1]], dtype=complex)/np.sqrt(2)
> CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
>
> bell = CNOT @ np.kron(H, np.eye(2)) @ np.kron(ket[0], ket[0])   # (|00>+|11>)/sqrt2
>
> # separability test for 2 qubits: reshape 4-vector into 2x2, single SVD value
> M = bell.reshape(2, 2)
> print("singular values:", np.round(np.linalg.svd(M, compute_uv=False), 3))
> # two nonzero values -> not a product state (a product state has exactly one)
>
> # X-basis correlation: measure both qubits via H
> H2 = np.kron(H, H)
> p = np.abs(H2 @ bell)**2
> print("X-basis outcomes (|00>,|01>,|10>,|11>):", np.round(p, 3))  # perfect correlation
> ```
> The SVD test is your general separability detector: one singular value means product, more means entangled.

> [!research] Research frontier
> **Entanglement quantification**: for two qubits there is one entropy measure; for three or more, entanglement splits into inequivalent classes (GHZ-type versus W-type) with no single agreed measure, and for mixed states the classification is largely open — this matters because noisy hardware only produces mixed states (13.9). Related open problem: certifying entanglement and randomness in devices you do not trust — device-independent certification — the foundation of commercial quantum-randomness services running today.

## 13. Entanglement

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** entangled systems share one joint description; measuring one shapes the statistics of the other, and no local recipe explains it.
> - **Mathematics —** Schmidt decomposition, the CHSH inequality, and entanglement entropy give entanglement exact numeric measures.
> - **Implementation —** simulate teleportation, superdense coding, and an entanglement-entropy computation from scratch.
> - **Engineering —** entanglement is consumed, monogamous, and fragile: budgets for it drive routing and code design.
> - **Research —** efficient entanglement manipulation, distribution over networks, and device-independent certification are open problems.

### 13.1 What entanglement actually means

State it without mysticism: **entanglement** means the joint state contains information about *correlations* that is not contained in any individual subsystem. For Φ⁺, each qubit's reduced state (trace out the other — 13.9) is I/2, maximally random, yet the pair is in a pure, fully determined state. The information lives only in the joint description. Three clarifications matter. Entanglement is basis-independent — if a state factors in one basis it factors in all. Entanglement is between subsystems, not particles — the same math applies to modes, ions, or halves of a chip. And it does *not* allow signaling (13.3): the local statistics of each side are I/2 no matter what the other side does. What it enables is correlations-with-structure that classical channels cannot supply without shared pre-existing randomness.

### 13.2 Detecting entanglement

Given a two-qubit density matrix, how do you know it is entangled? Tools, in increasing power. **Purity of reduced states**: for a pure two-qubit state, entangled exactly when either reduced state is mixed (Tr(ρ₁²) < 1). **Schmidt decomposition**: reshape the 4-vector into a 2×2 matrix and take singular values — product states have exactly one nonzero singular value (used in 12.4's experiment). **PPT criterion**: transpose one subsystem's part of ρ; for two qubits, negative eigenvalues prove entanglement — necessary and sufficient in this dimension. **Bell-inequality violation**: a sufficient (not necessary) certificate with the strongest physical meaning. In the wild, hardware tomography (Part XI) reconstructs ρ from measurements, and the first thing experimentalists compute is one of these tests. Note the honest caveat: above two qubits, full detection is computationally hard — entanglement is cheap to create, expensive to certify.

### 13.3 Bell's theorem

In 1964 John Bell asked a question with a yes/no answer: can the correlations of entangled states be explained by **local hidden variables** — pre-agreed values carried by each particle, set at emission, with no faster-than-light influence? He proved mathematically that any such model satisfies quantitative bounds (**Bell inequalities**) that quantum mechanics predicts can be violated. Nature's verdict, across experiments from Aspect (1982) to the loophole-free tests of 2015 and the 2022 Nobel work: quantum mechanics wins; local hidden variables are dead. The engineering reading matters more than the metaphysics: Bell's theorem turns "entanglement is weird" into "entanglement's correlations are a *certified, testable, non-classical resource*" — the resource behind device-independent cryptography and certified randomness. No signaling theorem stands alongside it: violating an inequality requires comparing outcomes classically; neither party alone can send a message.

### 13.4 Bell inequalities

The workhorse is the **CHSH inequality**: for two parties each choosing between two measurement settings (A₀, A₁ and B₀, B₁), any local hidden-variable model obeys S = |⟨A₀B₀⟩ + ⟨A₀B₁⟩ + ⟨A₁B₀⟩ − ⟨A₁B₁⟩| ≤ 2. Quantum mechanics allows up to 2√2 (the Tsirelson bound), reached by Φ⁺ with measurement angles 45° apart. The settings for a maximally entangled pair: A₀ = Z, A₁ = X, B₀ = (Z+X)/√2, B₁ = (Z−X)/√2 — each expectation computed by measuring in the rotated basis (11.4). Real experiments must close the detection loophole (high-efficiency detectors) and the locality loophole (space-like separation of the parties); the 2015 Delft, NIST, and Vienna experiments did both. Expect S ≈ 2.6–2.8 on noisy lab hardware rather than 2.83 — the deficit is a two-qubit fidelity meter, used exactly that way in benchmarks.

> [!experiment] On your laptop — run the CHSH test
> ```python
> import numpy as np
>
> H = np.array([[1,1],[1,-1]], dtype=complex)/np.sqrt(2)
> bell = np.array([1,0,0,1], dtype=complex)/np.sqrt(2)
>
> def basis2(theta):                    # single-qubit basis rotated by theta in X-Z plane
>     return np.array([[np.cos(theta/2), np.sin(theta/2)],
>                      [np.sin(theta/2), -np.cos(theta/2)]], dtype=complex)
> def corr(theta1, theta2):
>     B = np.kron(basis2(theta1), basis2(theta2))
>     p = np.abs(B @ bell)**2
>     return p[0] - p[1] + p[2] - p[3]  # +1 for equal outcomes, -1 otherwise
>
> S = corr(0, np.pi/4) + corr(0, -np.pi/4) + corr(np.pi/2, np.pi/4) - corr(np.pi/2, -np.pi/4)
> print(f"S = {S:.3f}   (classical bound 2, quantum max {2*np.sqrt(2):.3f})")  # S = 2.828
> ```
> You just falsified local hidden variables in 15 lines. The same estimator runs on real hardware via basis rotations.

### 13.5 Quantum teleportation

**Teleportation** moves an unknown state |ψ⟩ = α|0⟩ + β|1⟩ from Alice to Bob using one shared Bell pair plus two classical bits — and it transfers the state without either party learning it. Protocol: (1) Alice Bell-measures |ψ⟩ together with her half of Φ⁺; (2) she gets one of four outcomes, each equally likely, and sends the 2-bit label to Bob; (3) Bob's qubit is now |ψ⟩ up to one Pauli correction — I, X, Z, or XZ — determined by Alice's bits; (4) Bob applies the inverse Pauli. Read the resource accounting: no matter or energy transported, no state cloned (the original is destroyed by the Bell measurement — no-cloning enforced), no faster-than-light signaling (the correction needs the classical bits). Teleportation is not a curiosity; it is the *routing primitive*: quantum networks, module-to-module links in modular hardware, and gate teleportation in fault tolerance all run this protocol.

```text
Teleportation:

  psi:    ──●─────────M────────── 2 classical bits ──┐
           │         │                               │  X or Z
  alice:  ──H───●────M──────────                       ▼
                │                                  bob: ──apply correction──> |psi>
  bob:   ───────X──────────────────────────
```

### 13.6 Superdense coding

The mirror protocol: **superdense coding** sends two classical bits using one qubit of transmission plus one shared Bell pair. Alice applies I, Z, X, or ZX to her half of Φ⁺ — four options, one per 2-bit message — then sends the qubit to Bob, who performs a Bell-state measurement (12.6) and reads both bits. The accounting is exact: two classical bits of capacity from one transmitted qubit, *because* the pre-shared entanglement was established earlier and counted separately. This is the cleanest demonstration that entanglement is a communication resource with quantifiable value. Both directions are real: teleportation trades entanglement + classical bits to move quantum states; dense coding trades entanglement + a quantum channel to double classical capacity. Hardware demos are routine with photons and ions; the capacity advantage requires a noiseless qubit channel, so classical engineering keeps dense coding mostly a benchmark.

### 13.7 Entanglement swapping and monogamy

Two structural facts govern how entanglement behaves at scale. **Entanglement swapping**: Alice and Bob share no entanglement, but Alice and Carol share a Bell pair, as do Carol and David; Carol Bell-measures her two qubits and — conditioned on her classical outcome — Alice and David are entangled, never having interacted. This is how quantum repeaters will chain short links into long-distance networks: entanglement is built up segment by segment, swapped at nodes, purified against noise. **Monogamy of entanglement**: if qubits A and B are maximally entangled, B cannot be entangled with C at all — maximal correlation with A excludes any correlation-with-structure toward C. Monogamy is why entanglement cannot be freely shared or copied, why eavesdroppers measurably damage QKD links, and why error-correcting codes can separate logical information from the environment. Structure: share it pairwise, spend it deliberately.

### 13.8 Entanglement entropy

To measure entanglement in a mixed or multi-partite world you need a number. Split a pure state into subsystems A and B; the reduced density matrix ρ_A = Tr_B(|ψ⟩⟨ψ|) (trace out B) carries A's statistics alone. The **entanglement entropy** is the von Neumann entropy S(ρ_A) = −Tr(ρ_A log₂ ρ_A) = −Σ λᵢ log₂ λᵢ over eigenvalues λᵢ. Zero means product state; 1 bit means a qubit of A is maximally entangled with B (as for all Bell states). Computationally this is a two-liner via SVD: singular values of the reshaped amplitude matrix are √λᵢ — the Schmidt decomposition of 13.2. Beyond two qubits, entanglement entropy measures bipartite entanglement only; the full multi-partite structure is richer and partly unclassified (research frontier below). In Part XIV, entanglement entropy becomes the diagnostic for whether a quantum state is classically simulable.

> [!experiment] On your laptop — entanglement entropy via SVD
> ```python
> import numpy as np
>
> def ent_entropy(psi, cut):                 # psi: 2^n amplitudes, cut qubits on side A
>     n = int(np.log2(len(psi)))
>     M = psi.reshape(2**cut, 2**(n-cut))
>     lam = np.linalg.svd(M, compute_uv=False)**2
>     lam = lam[lam > 1e-12]
>     return float(-np.sum(lam*np.log2(lam)))
>
> bell  = np.array([1,0,0,1], dtype=complex)/np.sqrt(2)
> ghz3  = np.zeros(8, dtype=complex); ghz3[[0, 7]] = 1/np.sqrt(2)   # (|000>+|111>)/sqrt2
> print(ent_entropy(bell, 1))   # 1.0  maximally entangled pair
> print(ent_entropy(ghz3, 1))   # 1.0  GHZ: any one qubit vs the other two
> print(ent_entropy(ghz3, 2))   # 1.0  still 1 bit across the 2|1 split
> ```
> Reshape-and-SVD is the single most useful state-analysis tool you will own; tensor-network simulators (Part XIV) are built from exactly it.

### 13.9 Entanglement as a computational resource

Is entanglement *necessary* for quantum speedup? Mostly yes, with a famous exception. Jozsa–Linden proved that pure-state circuits with vanishing multi-qubit entanglement are efficiently classically simulable — so exponential speedups require entanglement. The exception: the Gottesman–Knill theorem (Part X) shows a class of heavily entangling Clifford circuits that *is* simulable, so entanglement alone does not guarantee advantage — the entanglement must be of a classically-hard structure (volume-law scaling, high complexity). The engineering synthesis: entanglement is a necessary fuel with a quality requirement, and "how entangled is my state, in a simulability-relevant sense?" is a live measurement problem — answered numerically by the entropy of 13.8 and by tensor-network bond dimensions. Error-corrected computing is, from this angle, the discipline of maintaining a very specific, very robust entangled state for the duration of a computation.

> [!research] Research frontier
> Open and active: **entanglement distillation** — converting many noisy pairs into fewer clean ones, with known protocols needing 10²–10⁴ raw pairs per clean pair at realistic fidelities; **quantum networks** — repeaters with quantum memories whose storage times remain seconds-to-minutes against needed hours; and the **complexity-entanglement connection** — exactly which entanglement structures separate simulable from hard states, the boundary tensor-network methods (MPS, PEPS) walk along. This is one of the few frontiers where a laptop experiment can genuinely contribute (Part XIX).

## 14. Multi-Qubit Gates

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** multi-qubit gates create and move entanglement; the controlled-NOT is the "if-then" of quantum logic.
> - **Mathematics —** controlled-U blocks, SWAP networks, and the decomposition of any n-qubit unitary into a gate library.
> - **Implementation —** build CNOT, CZ, SWAP, Toffoli with np.kron; verify circuit identities and count depth.
> - **Engineering —** hardware connects neighbors, not all pairs: routing (SWAP insertion) dominates depth, and depth dominates error.
> - **Research —** optimal synthesis of unitaries and SWAP routing under hardware constraints are NP-hard problems with active tooling.

### 14.1 Controlled operations and CNOT

A **controlled-U** applies U to the target qubit only when the control qubit is |1⟩: it is quantum conditional logic, and it is *the* entanglement-making operation. The canonical case is **CNOT** (controlled-NOT, controlled-X): control unchanged, target flipped if control is |1⟩. Its 4×4 matrix is block-diagonal: I for the control-0 rows, X for the control-1 rows. Crucial semantics: CNOT does *not* copy the control — applied to |+⟩⊗|0⟩ it produces (|00⟩+|11⟩)/√2, entanglement, not a clone (no-cloning is encoded in linearity itself). Also notable: CNOT is its own inverse, and control/target roles can be swapped by conjugating with H (H⊗H·CNOT·H⊗H = reversed CNOT) — a routing trick hardware compilers use constantly. In numpy, CNOT is the first 4×4 matrix worth typing by hand.

```python
import numpy as np

CNOT = np.array([[1,0,0,0],
                 [0,1,0,0],
                 [0,0,0,1],
                 [0,0,1,0]], dtype=complex)

H = np.array([[1,1],[1,-1]], dtype=complex)/np.sqrt(2)
plus0 = np.kron(H @ np.array([1,0], dtype=complex), np.array([1,0], dtype=complex))
print(np.round(CNOT @ plus0, 3))   # [0.707, 0, 0, 0.707]  -> Bell state, not a copy
```

### 14.2 Controlled-Z and controlled phase

**CZ** (controlled-Z) applies Z to the target when the control is |1⟩; as a diagonal matrix diag(1,1,1,−1) it adds a −1 phase only to |11⟩. Two engineering reasons CZ is beloved. First, it is **symmetric**: either qubit can be called the control — a real convenience when hardware connectivity is fixed. Second, on many platforms (superconducting, photonic) it is *native or near-native*, sometimes as a bus-mediated conditional phase. The identity CZ = (I⊗H)·CNOT·(I⊗H) means CNOT and CZ are interchangeable at the cost of two Hadamards, so gate libraries choose freely. Generalizing, the **controlled-phase gate** CRz(θ) = diag(1,1,1,e^{iθ}) gives an arbitrary conditional phase; two-qubit interactions in nature (couplers, collisions, cross-resonance drives) are naturally of this entangling-phase form, which is why synthesis tooling treats CRz as the primitive.

### 14.3 SWAP

**SWAP** exchanges two qubits' states: |ψ⟩⊗|φ⟩ → |φ⟩⊗|ψ⟩, matrix form a 4×4 permutation with ones on the anti-diagonal. It does not create entanglement and is composed of three CNOTs (CNOT(a,b)·CNOT(b,a)·CNOT(a,b) — order matters, all three directions). Why care about a gate that "does nothing" computationally? **Routing**. Hardware gives you an interaction graph — superconducting chips connect neighbors; trapped ions connect more broadly but not freely — and when a two-qubit gate targets non-adjacent qubits, the compiler inserts SWAPs to bring them together, or moves states along the graph. On IBM-style heavy-hex layouts, routing overhead routinely multiplies circuit depth several-fold, and since every gate layer accumulates ~10⁻³ error, SWAP insertion is a first-order driver of whether an algorithm works at all (45.9). Depth counting below makes this cost visible.

### 14.4 Toffoli and Fredkin

The **Toffoli gate** (CCNOT) flips the target iff *both* controls are |1⟩ — classical AND-with-uncompute, and the backbone of reversible classical logic: any Boolean circuit can be built from Toffoli plus X, with the garbage-output trick of uncomputing ancillas. Quantum mechanically it maps |a⟩|b⟩|c⟩ → |a⟩|b⟩|c⊕(a·b)⟩. The **Fredkin gate** (controlled-SWAP) swaps targets iff the control is |1⟩, used in reversible computing and in comparison/routing subroutines. Neither is native on any major platform: Toffoli decomposes into 6 CNOTs plus single-qubit gates (fewer with relative-phase Toffoli tricks, at the cost of a Z-on-phase-kickback ancilla), and arithmetic built from them inherits that multiplier. This is the honest cost of quantum arithmetic: Shor's modular exponentiation is thousands of Toffolis, each six-ish CNOTs, each error-prone — resource counts (Part VIII) add up exactly this way.

```text
Toffoli = 6 CNOTs (standard decomposition, plus single-qubit gates):

  c0: ──●────────────●──────────●──────
        │            │          │
  c1: ──┼────●───────┼────●─────┼──●───
        │    │       │    │     │  │
  t : ──X────X───H───X────H──X──X──H───     (exact up to global phase)
```

### 14.5 Controlled rotations

A **controlled rotation** CRθ applies Ry(θ) or Rz(θ) to the target conditioned on the control — the continuously-tunable cousin of CNOT, and the literal building block of the QFT and many variational ansätze. The construction generalizes a pattern you should internalize: any single-qubit U = e^{iα}·A·X·B·X·C (with A·X·B·X·C = I) converts into controlled-U by controlling only the middle X — meaning *any* controlled-U costs just two CNOTs plus the single-qubit A, B, C. That is a theorem worth knowing by name (Barenco et al. 1995). In circuits like QFT the rotations are multiply-controlled in later stages; the general rule is that a k-controlled U needs O(k) CNOTs with ancillas or O(2ᵏ) without — the constant factor that makes big controlled operations expensive, and the target of ongoing synthesis improvements.

### 14.6 Universal gate sets

What is the minimal toolkit for arbitrary quantum computation? The standard answer: **{H, T, CNOT}** — one Clifford, one non-Clifford, one entangler — is universal, meaning any n-qubit unitary can be approximated to accuracy ε by a circuit over this set (with size polylogarithmic in 1/ε). Practical variants: {Rz(π/4), √X, CNOT} matches hardware pulses; ion traps use {Rx(π/2), Rz(θ), Mølmer–Sørensen}; and any single *entangling* two-qubit gate plus arbitrary one-qubit gates is universal (Brylinski's theorem) — even exotic ones like √SWAP or iSWAP. Note the negative space: the Clifford group alone is classically simulable (Gottesman–Knill), so universality hinges on one non-Clifford ingredient — precisely why T gates dominate fault-tolerance cost and why magic-state distillation exists (Part X). Choose your gate set like you choose an instruction set: by native support, not elegance.

### 14.7 Gate synthesis

**Gate synthesis** is the compiler pass turning an arbitrary target unitary into a sequence of library gates. Single-qubit: exact ZYZ decomposition (10.5), three rotations. Two-qubit: any two-qubit unitary needs exactly 3 CNOTs plus single-qubit gates (worse, 14 for special classes; the number is a proven bound, not folklore). General n-qubit unitaries need O(4ⁿ) CNOTs — exponential, as they must be, since the unitary itself has 4ⁿ real parameters. The engineering reality: *approximate* synthesis. Because physical gates err at ~10⁻³ anyway, circuits are synthesized to accuracy ε over the native set, trading gate count against approximation error; Solovay–Kitaev gives O(log^c(1/ε)) overhead and modern number-theoretic methods do far better for the {H,T} set. Total error budget = synthesis error + gate errors + readout error; compilers (Part XII) exist to balance that equation automatically.

### 14.8 Circuit depth and width

Two numbers characterize a circuit's cost. **Width**: qubits used. **Depth**: the longest chain of sequential gate layers, where a layer holds gates acting on disjoint qubits — depth is what determines runtime on hardware, since layers execute one after another, and it bounds how much decoherence accumulates before the measurement. A useful mental model from classical computing: width is memory, depth is critical-path latency. The tension is real: shrinking depth by parallelizing may cost ancilla width, and hardware limits both (≈10²–10⁴ qubits; coherence times of microseconds to seconds). The quantity to watch in any benchmark plot is **depth × error rate** — circuits deeper than ~1/(gate error) ≈ 1,000 layers at 10⁻³ error drown in noise before error correction exists. When this book says an algorithm "fits on current hardware", it is a claim about depth after routing, not about qubit count.

> [!experiment] On your laptop — build a gate library and count depth
> ```python
> import numpy as np
>
> I2 = np.eye(2, dtype=complex)
> X  = np.array([[0, 1], [1, 0]], dtype=complex)
> H  = np.array([[1, 1], [1, -1]], dtype=complex)/np.sqrt(2)
> CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
>
> # gate on qubit k of n: I...U...I via kron
> def embed(U, n, k):
>     ops = [I2]*n; ops[k] = U
>     out = np.array([[1]], dtype=complex)
>     for op in ops: out = np.kron(out, op)
>     return out
>
> # CZ = (I (x) H) CNOT (I (x) H)   -- verify the identity numerically
> CZ = embed(H, 2, 1) @ CNOT @ embed(H, 2, 1)
> print(np.round(CZ, 3).tolist())          # diag(1, 1, 1, -1)
>
> # SWAP = CNOT . CNOT-reversed . CNOT
> CNOT_rev = np.array([[1,0,0,0],[0,0,0,1],[0,0,1,0],[0,1,0,0]], dtype=complex)
> SWAP = CNOT @ CNOT_rev @ CNOT
> print(np.allclose(SWAP, np.eye(4)[::-1]))  # True
> ```
> Depth is graph theory on this library: make gates on disjoint qubits parallel layers and count layers (Part XII builds the scheduler).

> [!research] Research frontier
> Two compiler-grade open problems. **Optimal synthesis**: given a unitary and a hardware gate set, produce a circuit of provably minimal gate count or depth — solved only for tiny cases; even optimal 3-qubit synthesis over {CNOT, T, H} has results less than a decade old. **SWAP routing**: inserting swaps under connectivity constraints while minimizing depth is NP-hard in general, so practical compilers (Qiskit, tket, Staq) use heuristics whose gap from optimal is unmeasured on large circuits. Better routing directly buys working algorithms on near-term hardware — a concrete, benchmarkable way to contribute from a laptop.
