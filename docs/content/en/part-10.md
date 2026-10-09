# Part X — Quantum Error Correction

*Author: GLM-5.3*

This is the part where quantum computing stops being a physics curiosity and becomes an engineering discipline. Error correction is why fault-tolerant machines are possible at all, why they are so expensive, and — for a software engineer — where the field's most hirable problems live. Everything here is buildable on a laptop.

## 32. The Fundamental Problem

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** quantum information is too fragile to store in one place and too slippery to copy; the only defense is to spread it out and watch for disturbances.
> - **Mathematics —** errors are detected by measuring observables that reveal the error but not the data; the outcome pattern is called the syndrome.
> - **Implementation —** a 3-qubit code fits in 8 amplitudes; syndrome measurement is a few lines of numpy.
> - **Engineering —** with physical error rates near 10⁻³, every long circuit is useless unencoded; correction must run faster than errors accumulate.
> - **Research —** the limits of what codes can achieve and how fast decoding can run are both open problems.

### 32.1 Why classical redundancy works

Classical redundancy works because bits can be copied, measured, and processed by nonlinear logic. Store one bit three times and decode by majority vote: if each copy flips independently with probability p, the value fails only when two or more copies flip, so `p_L = 3p^2 - 2p^3`, which is below p for every p < ½. Shannon generalized this into a full theory of reliable communication over noisy channels. Notice the three ingredients: unlimited copying, direct measurement of the stored value, and a nonlinear decoding rule. Quantum mechanics will deny the first two and constrain the third. Everything in this part is a way to recover them indirectly.

### 32.2 Why copying a qubit doesn't work

The obvious move — copy the unknown state — fails immediately. Apply CNOT with the unknown qubit as control and a fresh |0⟩ as target: α|0⟩ + β|1⟩ ⊗ |0⟩ → α|00⟩ + β|11⟩. That is an entangled state, not two copies (α|0⟩ + β|1⟩) ⊗ (α|0⟩ + β|1⟩). Measuring to learn α and β does not help either: the Born rule gives one sample per copy, the amplitudes are continuous numbers, and the measurement disturbs the state it reads. So redundancy cannot be added by inspection. It must be added by a unitary that never looks at the amplitudes at all — which is what encoding is.

### 32.3 No-cloning theorem

The no-cloning theorem (Wootters, Zurek, and Dieks, 1982) makes the failure general: no unitary copies an arbitrary unknown quantum state. The proof is two lines of linearity. Suppose U|0⟩|0⟩ = |0⟩|0⟩ and U|1⟩|1⟩ = |1⟩|1⟩. Then on a superposition, U(α|0⟩ + β|1⟩)|0⟩ = α|00⟩ + β|11⟩, but a true clone would be (α|0⟩ + β|1⟩) ⊗ (α|0⟩ + β|1⟩), which contains cross terms αβ|01⟩ and αβ|10⟩. Since U is linear, both cannot hold. Consequences: no checkpointing a quantum process, no amplifying a quantum signal without destroying it, and — constructively — error correction must work on states it never learns.

### 32.4 Encoding quantum information

The fix is to encode into a larger Hilbert space with a unitary that depends only on the basis, not the amplitudes:

```text
encoding  |psi> = a|0> + b|1>  into the 3-qubit bit-flip code

q0: |psi> --●----●--
q1: |0>  ---⊕----|-        result:  a|000> + b|111>
q2: |0>  --------⊕--
```

The information now lives in the *correlations* between qubits; no single qubit carries α or β. If an X error hits qubit 1, the state becomes α|010⟩ + β|101⟩ — a different pair of orthogonal basis vectors, but the same two-dimensional structure. An operation exists that maps it back, without ever knowing α or β. Classically, information is *in* the bits; quantumly, it is in the pattern of entanglement. That reframing is the entire conceptual leap of quantum error correction.

### 32.5 Detecting errors without measuring the state

How do you learn *which* error occurred without learning α and β? Measure an observable whose eigenvectors do not distinguish the codewords. For the encoded state above, the operator Z0Z1 works: |000⟩ and |111⟩ are both +1 eigenstates of Z0Z1 (each has an even number of 1s on qubits 0 and 1), so any superposition α|000⟩ + β|111⟩ is also a +1 eigenstate — the outcome is +1 regardless of the amplitudes. After an X error on qubit 0, both components move entirely into the −1 eigenspace, so the outcome is −1. The measurement reveals the error's fingerprint and nothing about the data. "Measure the parity, not the state" is the design principle behind every code in this part.

### 32.6 Syndrome measurement

Measuring the two parities gives a pair of classical bits — the **syndrome** (syndrome):

```text
syndrome (Z0Z1, Z1Z2)   outcome   implied error          correction
      (+1, +1)            00       none (or Z-type)       do nothing
      (-1, +1)            10       X on qubit 0           X on qubit 0
      (-1, -1)            11       X on qubit 1           X on qubit 1
      (+1, -1)            01       X on qubit 2           X on qubit 2
```

Correction is then a conditional Pauli. Two subtleties matter. First, the syndrome identifies the error only up to multiplication by a stabilizer (34.3): errors E and E·S produce identical syndromes and identical effects on the codespace, so "which error occurred" is only defined modulo equivalence. Second, the (+1, +1) row also covers uncorrectable errors: a triple flip acts as the logical operator X⊗X⊗X and a Z error is invisible to Z-parities. A distance-3 code corrects any single-qubit error; that is all it promises.

> [!experiment] On your laptop — syndrome measurement by simulation
> The 3-qubit code fits in 8 amplitudes. Watch the syndrome flip without the state being read.
>
> ```python
> import numpy as np
>
> # 3-qubit code in the computational basis (bit q of the index = qubit q)
> psi = np.zeros(8, dtype=complex)
> psi[0b000], psi[0b111] = 0.6, 0.8          # a|000> + b|111>
>
> def apply_x(state, q):                      # bit-flip error on qubit q
>     out = np.zeros_like(state)
>     for i in range(len(state)):
>         out[i ^ (1 << q)] = state[i]
>     return out
>
> def z_parity_probs(state, qubits):
>     # distribution of the eigenvalue (-1)^(bit parity) of Z on these qubits
>     p = np.zeros(2)
>     for i, a in enumerate(state):
>         par = sum((i >> q) & 1 for q in qubits) % 2
>         p[par] += abs(a) ** 2               # p[0]: +1 outcome, p[1]: -1
>     return p
>
> state = apply_x(psi, 1)                     # X error lands on qubit 1
> print("Z0Z1:", z_parity_probs(state, [0, 1]))   # [0, 1] -> outcome -1
> print("Z1Z2:", z_parity_probs(state, [1, 2]))   # [0, 1] -> outcome -1
> ```
>
> Both parities report −1 regardless of α and β: the syndrome is deterministic and carries zero information about the encoded amplitudes. Change the error qubit and confirm the table of 32.6.

## 33. Simple Quantum Codes

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** spread one qubit over several, measure only parities, undo what the parities blame.
> - **Mathematics —** codes are specified by their stabilizer generators and codewords; the notation [[n, k, d]] counts qubits, logical qubits, and correctable errors.
> - **Implementation —** encode, inject noise, measure the syndrome, and correct — all in a 20-line Monte Carlo loop.
> - **Engineering —** the 3-qubit codes handle one error class each; Shor and Steane handle arbitrary single-qubit errors at 9 and 7 qubits.
> - **Research —** the question these toy codes pose — which gates can run without decoding — is still open (Eastin–Knill).

### 33.1 Three-qubit bit-flip code

The code from 32.4 gets a name: |0_L⟩ = |000⟩, |1_L⟩ = |111⟩, with stabilizer generators `Z0 Z1` and `Z1 Z2`. It corrects any single X (bit-flip) error. With independent flips at rate p and perfect syndrome extraction, the logical error rate is `p_L = 3p^2 - 2p^3` — the same majority-vote formula as 32.1, because the syndrome table plus conditional correction *is* majority vote. The limitation is equally clear: the stabilizers contain only Z, so Z errors commute with everything and are invisible, and a triple flip looks like no error at all while being a logical flip. This code protects against one error class; real hardware flips bits *and* phases.

> [!experiment] On your laptop — encode, corrupt, decode
> A Monte Carlo loop over the syndrome table measures `p_L` directly.
>
> ```python
> import numpy as np
> rng = np.random.default_rng(0)
>
> def logical_error_rate(p, shots=50_000):
>     fails = 0
>     for _ in range(shots):
>         q = [0, 0, 0]                          # encoded |0>_L
>         flips = rng.random(3) < p              # independent bit-flip noise
>         q = [b ^ int(f) for b, f in zip(q, flips)]
>         s1, s2 = q[0] ^ q[1], q[1] ^ q[2]      # measure Z0Z1, Z1Z2
>         fix = {0: None, 1: 2, 2: 0, 3: 1}[2 * s1 + s2]
>         if fix is not None:
>             q[fix] ^= 1                        # conditional correction
>         fails += any(q)                        # any 1 left = logical fail
>     return fails / shots
>
> for p in (0.05, 0.10, 0.15):
>     print(f"p={p:.2f}  p_L={logical_error_rate(p):.4f}")
> ```
>
> Compare with the analytic `3p^2 - 2p^3`: 0.0073, 0.0280, 0.0608. The code helps while p < ½ — the repetition-code threshold.

### 33.2 Three-qubit phase-flip code

Phase errors (Z flips) are just as physical as bit flips: Z|+⟩ = |−⟩, so a phase flip corrupts superpositions in the Hadamard basis. The fix is the same code with every operator conjugated by H: encode in the |±⟩ basis as α|+++⟩ + β|−−−⟩, with stabilizers `X0 X1` and `X1 X2`. The syndrome table is identical, with X and Z exchanged and the basis states relabeled. This is the first instance of a pattern that recurs throughout coding theory: applying a basis change to every qubit maps one code to a dual code protecting the complementary error class. Still nothing protects against X and Z simultaneously — that takes more structure.

### 33.3 Shor code

Shor's 1995 code was the first to correct an *arbitrary* single-qubit error. The construction is concatenation: an outer 3-qubit phase-flip code whose three "qubits" are each a 3-qubit bit-flip code — 9 physical qubits, one logical. The stabilizer has 8 generators:

- `Z0 Z1`
- `Z1 Z2`
- `Z3 Z4`
- `Z4 Z5`
- `Z6 Z7`
- `Z7 Z8`
- `X0 X1 X2 X3 X4 X5`
- `X3 X4 X5 X6 X7 X8`

The within-block Z-parities catch bit flips; the two six-qubit X operators compare the signs of the three blocks and catch phase flips. Since any single-qubit error is a linear combination of I, X, Z (and Y = iXZ), and correction is linear, correcting X and Z errors corrects everything: this is the standard argument that discrete syndromes suffice for continuous error space (34.1).

### 33.4 Steane code

The Steane code, [[7,1,3]], gets the same protection with fewer qubits via the CSS construction: take a classical code closed under transposition — the [7,4,3] Hamming code — and use its parity-check matrix rows as both X-type and Z-type stabilizers:

- `X0 X1 X2 X4`
- `X0 X1 X3 X5`
- `X0 X2 X3 X6`
- `Z0 Z1 Z2 Z4`
- `Z0 Z1 Z3 Z5`
- `Z0 Z2 Z3 Z6`

|0_L⟩ is the uniform superposition of the 8 even-weight Hamming codewords; |1_L⟩ covers the odd-weight ones. Bit and phase errors are handled by separate, independent classical decoders — CSS codes split the problem cleanly. Historically, Steane's code mattered because its full Clifford gate set (H, S, CNOT) is transversal (33.6), making it the first practical substrate for fault-tolerant logic.

### 33.5 Logical qubits

Everything above defines a **logical qubit** (logical qubit): a two-dimensional subspace, the codespace, spanned by |0_L⟩ and |1_L⟩, maintained by ongoing measurement and correction. The general notation is [[n, k, d]]: n physical qubits, k logical qubits, distance d (35.10). The bit-flip code is [[3,1,3]], Shor is [[9,1,3]], Steane is [[7,1,3]]. Two properties matter in practice. The logical qubit is not a "stronger physical qubit" — it is an actively maintained subspace whose quality is defined operationally by measured logical error rates (35.11). And codes are typically *degenerate*: different physical errors can act identically on the codespace, so more physical events are correctable than there are distinct syndromes.

### 33.6 Logical gates

Computing on encoded data means applying unitaries that map the codespace to itself. For the bit-flip code, the logical Paulis are products: logical X̄ = `X0 X1 X2` swaps |000⟩ and |111⟩; logical Z̄ = `Z0 Z1 Z2` phases |111⟩ by −1. Either can be multiplied by stabilizers to give equivalent implementations — a freedom called gauge. The engineering question is which gates run *without decoding*. A **transversal gate** (transversal gate) applies a single-qubit gate to each physical qubit in the block, so a physical fault cannot spread between qubits — fault tolerance comes free. Steane's code implements the entire Clifford group transversally; but no code has a universal transversal set (Eastin–Knill theorem), which is why 36.6 exists.

## 34. Stabilizer Formalism

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** a quantum code is a club: the stabilizers are membership tests, the errors are things that fail exactly those tests.
> - **Mathematics —** commuting Pauli subgroups define codespaces; the whole theory is linear algebra over 2×2 binary vectors.
> - **Implementation —** a Pauli string is two bit-vectors; commutation is one dot product mod 2.
> - **Engineering —** this is the representation running inside every stabilizer simulator and every real-time decoder firmware.
> - **Research —** beyond-Pauli noise, leakage, and coherent errors all break the formalism's assumptions — quantifying that is open.

### 34.1 Pauli group

The n-qubit **Pauli group** (Pauli group) P_n is the set of all tensor products of I, X, Y, Z with overall phases ±1, ±i, where Y = iXZ. It is the right language for errors for three reasons. First, completeness: any 2×2 matrix is a complex linear combination of I, X, Y, Z, so correcting the discrete set of Pauli errors corrects any error — the linearity argument from 33.3 made rigorous. Second, measurability: Paulis (with I,X,Y,Z Hermitian cores) are observables. Third, structure: the group is closed under multiplication up to phase, and any two elements either commute or anticommute — no third option. The Pauli group turns error correction into finite group theory, which means it can be programmed.

### 34.2 Commutation

Two Pauli strings commute if and only if they disagree in an even number of positions where both are non-identity and anticommute (X against Z, X against Y, Y against Z). The computational form: represent a Pauli string as a pair of bit-vectors (x, z) ∈ F₂^{2n}, meaning X^x Z^z per qubit. Then strings P = (x, z) and Q = (x′, z′) commute exactly when x·z′ + z·x′ ≡ 0 (mod 2). This binary symplectic representation is what stabilizer simulators (37.9) and decoder firmware actually store and manipulate — n-qubit Pauli algebra becomes bitset arithmetic. Pauli strings are written in this book as code spans like `Z0 Z1` to keep them unambiguous.

> [!experiment] On your laptop — Pauli algebra in 15 lines
> Commutation, stabilizers, and logical operators, all reduced to bit-vector dot products.
>
> ```python
> import numpy as np
>
> def pauli(x_bits, z_bits):        # Pauli string: X^x Z^z per qubit
>     return (np.array(x_bits), np.array(z_bits))
>
> def commutes(p, q):               # commute iff x1.z2 + z1.x2 is even
>     (x1, z1), (x2, z2) = p, q
>     return (x1 @ z2 + z1 @ x2) % 2 == 0
>
> n = 3
> Z01 = pauli([0, 0, 0], [1, 1, 0])   # stabilizer Z0 Z1
> Z12 = pauli([0, 0, 0], [0, 1, 1])   # stabilizer Z1 Z2
> Xbar = pauli([1, 1, 1], [0, 0, 0])  # logical X of the bit-flip code
> X0 = pauli([1, 0, 0], [0, 0, 0])    # single-qubit error
>
> print([commutes(Z01, g) for g in (Z12, Xbar, X0)])   # [True, True, False]
> ```
>
> Stabilizers commute with each other and with logical operators; errors anticommute with some generator — that asymmetry *is* the code.

### 34.3 Stabilizers

A **stabilizer** (stabilizer) is an abelian subgroup S ⊂ P_n that does not contain −I, specified by r independent commuting generators. The codespace is the simultaneous +1 eigenspace of all generators, of dimension 2^(n−r), encoding k = n − r logical qubits. The bit-flip code: S = ⟨`Z0 Z1`, `Z1 Z2`⟩, so n = 3, r = 2, k = 1. Errors act by conjugation: if E anticommutes with some generator, E|ψ⟩ leaves the codespace and the violated generator names the error's location information. The entire code — its encoding, its correcting power, its gates — is nothing but the choice of S. This reduction is the stabilizer formalism's gift to engineers: codes become data structures.

### 34.4 Stabilizer states

The k = 0 case is worth its own section: a **stabilizer state** (stabilizer state) is the unique +1 eigenstate of a maximal stabilizer — |000⟩ (S = ⟨`Z0`, `Z1`, `Z2`⟩), |+⟩^⊗n (all X), and everything reachable from |0…0⟩ using only Clifford gates (H, S, CNOT) are examples. The Gottesman–Knill theorem says circuits built from Cliffords, Pauli measurements, and Pauli corrections are classically simulable in polynomial time — no matter how entangled they get. Two implications. Entanglement alone is not computational power. And the reason every QEC pipeline runs on stabilizer simulators (37.9) rather than full state vectors is precisely that error correction itself is a Clifford-only process.

### 34.5 Stabilizer measurements

Measuring a Pauli generator g is a projective measurement with outcomes ±1, projectors (I ± g)/2. On a valid codespace, every generator returns +1 by construction — that is what "being in the code" means. After an error E, each generator anticommuting with E returns −1; the resulting ±1 pattern is the syndrome of 32.6, generalized. Two properties matter. Measuring g reveals one bit about *which error occurred*, never the encoded amplitudes — the measurement commutes with the logical information. And a single round of measuring r generators yields r bits, so a code with n physical qubits produces exponentially less syndrome data than the state itself: this compression is what makes real-time decoding conceivable at all.

### 34.6 Syndrome extraction

Hardware reads single qubits, not four-qubit Paulis, so generators are measured through an ancilla. For a Z-type generator: prepare an ancilla in |0⟩, CNOT from each data qubit (controls) into the ancilla, measure the ancilla — its value is the parity of the target Z eigenvalues. For an X-type generator, conjugate with H on the ancilla around the same fan-out. The data qubits are never measured; their superposition survives. The subtleties are engineering, not mathematics: the *order* of the four CNOTs determines how a single ancilla fault propagates (36.4); the measurement itself is noisy, so rounds repeat (37.1); and every cycle burns time against decoherence. Syndrome extraction circuits are the innermost loop of a fault-tolerant computer.

### 34.7 Logical operators

The **normalizer** N(S) — Pauli strings commuting with every generator — contains S and, crucially, more: strings that act nontrivially on the codespace. These are the logical operators. Logical X̄ and Z̄ form an anticommuting pair per encoded qubit; multiplying them by stabilizers gives equivalent representatives. The **code distance** (code distance) d is the minimum weight (number of non-identity factors) of any element of N(S) \ S: the cheapest operator that acts as a logical gate yet looks like no error to the syndrome. It equals the number of errors the code can correct (⌊(d−1)/2⌋). Code design is now a precise optimization: maximize d per physical qubit while keeping generators local.

## 35. Surface Codes

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** qubits on a grid's edges, parity checks on its corners and squares; errors are little chains, and only chains that stretch across the whole grid hurt.
> - **Mathematics —** a CSS code whose stabilizers are weight-4 products of X and Z on a 2D lattice; distance equals the shortest spanning chain.
> - **Implementation —** syndrome extraction is one CNOT fan-out per check per round; everything reduces to repetition-code ideas in two dimensions plus time.
> - **Engineering —** nearest-neighbor layout, ~1% threshold, ~2d² qubits per logical qubit — the design every hardware roadmap standardized on.
> - **Research —** below-threshold operation was demonstrated in 2024; the frontier is now rate (qLDPC), decoding speed, and real-time operation.

### 35.1 Motivation

Why did one code family win the industry? Constraints of real hardware. Qubits live on a 2D chip and interact only with neighbors, so checks must be local. Control is imperfect, so checks should be small (weight 4) and the code should tolerate imperfect two-qubit gates. And the margin must be wide: the surface-code **threshold** (threshold) near 1% sits about ten times above today's best two-qubit gate error rates (~10⁻³), so corrections outpace damage. The costs are real — one logical qubit per ~2d² physical qubits is a poor rate — but every alternative (color codes, qLDPC) buys rate by demanding longer-range interactions. Kitaev's 1997 toric code, planarized, became the default because it matched the machine.

### 35.2 Lattice construction

The surface code places data qubits on the edges of a square lattice. Two families of checks live on it: star operators at vertices and plaquette operators on faces (35.5, 35.6). On a closed torus this is the toric code with two logical qubits; cut the torus open into a planar patch and you get the surface code with one. Hardware implements the *rotated* layout — the same checks folded into a d×d grid of data qubits with interleaved measure qubits — but the edge-and-face picture is the cleaner mental model:

```text
      *-----0-----*-----1-----*         *  vertex: star check
      |           |           |            = X on incident edges
      2     []    3     []    4         [] face: plaquette check
      |           |           |            = Z on bounding edges
      *-----5-----*-----6-----*         -,|  data qubits (one per edge)
      |           |           |
      7     []    8     []    9         on a torus there are no
      |           |           |         boundaries; a planar patch
      *----10-----*----11-----*         has two kinds (35.8)
```

### 35.3 Data qubits

The data qubits — d² of them in the rotated layout — are the physical qubits that actually store the logical state. During a memory experiment they are never measured directly; they are only ever entangled with checks and left alone. Their errors are the object of the whole exercise, and each error class talks to exactly one check family: an X error on a data qubit flips the plaquette (Z-type) checks adjacent to its edge, while a Z error flips the star (X-type) checks at its endpoints. This complementary response is what lets a single syndrome history localize both error types independently — the two-dimensional generalization of the parity logic of 32.5.

### 35.4 Syndrome qubits

Between the data qubits sit d²−1 **measure qubits** (measure qubits, ancillas), checkerboard-assigned to either X-type or Z-type duty. Each round, every ancilla is reset, entangled with its (up to) four neighboring data qubits, and measured. Ancillas are not passive probes: their reset errors, gate errors, and especially *measurement errors* corrupt the syndrome itself. A flipped measurement is indistinguishable, locally, from a real data error — which is why the decoding problem lives in space-time (35.9) and why memory experiments repeat the round at least d times, so that measurement noise shows up as defects separated along the time axis.

### 35.5 Star operators

A star operator A_s is the product of X on the (up to) four data qubits incident to vertex s — for an interior vertex of the lattice above, `X0 X1 X2 X3`. Stars are X-type checks: they detect Z errors on their incident edges and are blind to X errors. All stars mutually commute, because any two vertices share 0 or 2 edges — an even overlap (34.2) — and stars commute with all plaquettes by the same even-overlap argument across the two Pauli types. At boundaries, stars truncate to weight 2 or vanish (35.8). Measuring all stars once per round costs one ancilla each and four CNOTs — the cheapest possible local check.

### 35.6 Plaquette operators

A plaquette operator B_p is the product of Z on the four data qubits bounding face p — for the first face of the lattice above, `Z0 Z2 Z3 Z5`. Plaquettes are Z-type checks detecting X errors, mirror images of the stars in every respect: weight 4 in the bulk, mutually commuting, weight ≤ 2 at boundaries. Together, (d²−1)/2 stars and (d²−1)/2 plaquettes form the stabilizer group of the rotated surface code; measuring all of them once constitutes one syndrome round. The code's full stabilizer description is thus a list of weight-4 Pauli strings on a grid — small enough to fit in a header file, which is roughly how you should think of it.

### 35.7 Logical qubits

On the torus, two independent logical qubits live in the topology: logical operators are non-contractible loops of Paulis winding around the torus, and no local error can create or destroy one. On a planar patch, one logical qubit remains, and its operators are *open strings*: an X-type string ending on the two boundaries where plaquette checks terminate (call them Z-boundaries) creates no plaquette defects and acts as logical X̄; dually, a Z-string between the two X-boundaries is Z̄. A string of length below d creates detectable defects; one of length d spans boundary to boundary and is undetectable. The logical qubit is stored in topology, not in geometry — deform the string freely, it stays the same operator.

### 35.8 Boundaries

The boundaries are what make a planar code workable — and are the part most often glossed over. Two kinds exist. At an X-boundary, star checks terminate (some literature: "rough"); at a Z-boundary, plaquette checks terminate ("smooth"). Checks never straddle a boundary, and each logical string type must end on its own kind: X̄ spans the two Z-boundaries, Z̄ spans the two X-boundaries. This matching of operator type to boundary type is what makes one of the two logical directions undetectable while the other stays protected. The rotated layout arranges alternating boundaries around a square patch, which is why its picture in papers looks like a diamond — same code, tighter geometry, one fewer qubit row than the unrotated drawing.

### 35.9 Decoding

Errors are chains: an X-error chain flips the plaquette checks at its two endpoints, creating a pair of defects; a measurement error flips one check in two consecutive rounds, creating defects separated in time. The decoder's input is this 3D defect pattern (2D space plus rounds); its output is the most likely correction. The canonical approach, **minimum-weight perfect matching** (37.3), treats defects as nodes in a graph whose edge weights encode the probability of the connecting chain, then pairs them up minimizing total weight. Union-find decoders trade a little accuracy for near-linear speed. Every one of these ideas already works in one dimension:

> [!experiment] On your laptop — a tiny matching decoder
> The repetition code is the 1D surface code. Exactly two error patterns explain any syndrome; min-weight decoding picks the lighter one.
>
> ```python
> import numpy as np
> rng = np.random.default_rng(42)
>
> def decode(s, d):
>     # two patterns match the syndrome; they differ by the logical flip.
>     # min-weight (matching) decoding: keep the lighter cumulative one
>     cands = []
>     for b in (0, 1):
>         e, par = [], b
>         for i in range(d):
>             par ^= s[i - 1] if i else 0
>             e.append(par)
>         cands.append((sum(e), e))
>     return min(cands)[1]
>
> def logical_error_rate(p, d, shots=20_000):
>     fails = 0
>     for _ in range(shots):
>         e = (rng.random(d) < p).astype(int)   # sampled error chain
>         s = e[:-1] ^ e[1:]                    # syndrome: neighbor parity
>         r = e ^ np.array(decode(s, d))        # residual after correction
>         fails += r.sum() % 2                  # odd residual = logical flip
>     return fails / shots
>
> for p in (0.35, 0.45, 0.55):
>     print(p, [round(logical_error_rate(p, d), 3) for d in (3, 5, 7, 9)])
> ```
>
> Below p = 0.5 the rates fall as d grows; above, they rise. You have just reproduced a threshold — in one dimension.

### 35.10 Code distance

The distance d is the length of the shortest logical operator — the shortest chain of errors connecting two same-type boundaries — and the code corrects any ⌊(d−1)/2⌋ errors. Resources scale as d² plus the same again in measure qubits, and catching measurement errors requires running at least d rounds. The standard resource table, with the heuristic per-cycle logical error rate of 35.11 at p = 10⁻³:

| distance | data qubits | measure qubits | total | logical error per cycle at p = 10⁻³ |
|---|---|---|---|---|
| 3 | 9 | 8 | 17 | ≈10⁻³ |
| 5 | 25 | 24 | 49 | ≈10⁻⁴ |
| 7 | 49 | 48 | 97 | ≈10⁻⁵ |

Read the last column as the price list of error correction: one more unit of distance buys one more decimal digit of reliability, at the cost of roughly 30 more physical qubits.

### 35.11 Logical error rates

Below threshold, logical error per cycle follows a heuristic that decades of simulation and now hardware confirm:

```text
p_L(d)  ≈  A * (p / p_th)^((d+1)/2)        A ≈ 0.1 for the surface code
```

Each step in distance squares-and-a-half's the error. At p = 10⁻³ against p_th ≈ 10⁻²: d = 3 gives ~10⁻³, d = 5 gives ~10⁻⁴, d = 7 gives ~10⁻⁵ per cycle — the table of 35.10. Above threshold the curves invert: bigger codes are *worse*, and the crossing point defines p_th ≈ 1% (idealized) or 0.5–0.7% (realistic circuit-level noise). The 2024–2025 landmark: Google's Willow chip ran d = 3, 5, 7 patches and measured suppression by Λ ≈ 2.14 per distance step, logical error ≈ 0.1% per cycle at d = 7, and a logical qubit outliving the best physical qubit on the chip — the first unambiguous below-threshold demonstration.

> [!experiment] On your laptop — see the threshold scaling
> Extend the 35.9 decoder into a distance sweep and fit the exponential suppression.
>
> ```python
> import numpy as np
> import matplotlib.pyplot as plt
> # reuse decode() and logical_error_rate() from the previous experiment
>
> ps = np.linspace(0.30, 0.48, 7)
> for d in (3, 5, 7):
>     rates = [logical_error_rate(p, d, shots=10_000) for p in ps]
>     plt.plot(ps, rates, "o-", label=f"d={d}")
> plt.yscale("log")
> plt.xlabel("physical error rate p")
> plt.ylabel("logical error rate p_L")
> plt.legend()
> plt.show()
> ```
>
> The three curves separate exponentially below p = 0.5 and cross near it: on a log scale the vertical gaps between d values give Λ directly. Fitting the slope against (d+1)/2 is the same analysis hardware papers publish.

## 36. Fault-Tolerant Quantum Computing

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** a correctable error is fine; a *spreading* error is not. Fault tolerance is the discipline of keeping errors from cascading while you compute.
> - **Mathematics —** the threshold theorem: below a critical error rate, arbitrary precision costs only polylogarithmic overhead.
> - **Implementation —** every gadget is simulable with the stabilizer tools of chapter 37; the threshold curve is a laptop experiment.
> - **Engineering —** the gap between physical (10⁻³) and useful (10⁻¹⁰) error rates is bridged by factor of 100–1000 qubit overheads, mostly spent on magic-state factories.
> - **Research —** cutting that overhead — better codes, distillation, cultivation — is the single most consequential open engineering problem in the field.

### 36.1 Physical vs logical qubits

Keep two numbers in your head. Best physical two-qubit gates today: error rate ~10⁻³ (superconducting), ~10⁻⁴ (trapped ions, at slower speed). What algorithms need: logical error rates of 10⁻⁹ to 10⁻¹² per operation — factoring RSA-2048 or running deep chemistry circuits fails at anything looser. The gap is six to nine orders of magnitude, and no physical qubit roadmap closes it directly. Error correction closes it by spending qubit count: 2d² physical qubits per logical qubit at distance d, with d chosen so the logical error rate meets the algorithm's budget. The ratio of physical to logical qubits is the master cost metric of the industry, and every plot in every roadmap is ultimately about driving it down.

### 36.2 Fault tolerance

**Fault tolerance** (fault tolerance) is a property of *constructions*, not of codes: a gadget (preparation, gate, or measurement on encoded data) is fault-tolerant when any single component fault produces at most one correctable error per code block. Without this discipline, a physical fault inside a logical gate propagates into a multi-qubit error that no distance-3 code can absorb, and correction becomes the source of failure. The definition has teeth because faults and errors differ: faults are physical events (a bad pulse, a stray photon); errors are Pauli operators on the encoded state. Fault-tolerant design bounds what one fault can do. This constraint — not the codes themselves — is what multiplies resource counts, and it is non-negotiable at every scale.

### 36.3 Threshold theorem

The threshold theorem (Aharonov–Ben-Or, Kitaev, Knill–Laflamme–Zurek, 1996–1998) is the result that makes the field possible: if the physical error rate p is below a threshold p_th, and noise is local and weakly correlated, then arbitrarily long quantum computation is possible, with overhead growing only polylogarithmically in the target accuracy. It converts "quantum computing is physically impossible" into "quantum computing is an engineering budget". For the surface code, p_th ≈ 1% under idealized noise models and roughly 0.5–0.7% under realistic circuit-level noise — which is why the community's ~10⁻³ gate fidelities matter so much. The theorem's assumptions (locality, below-threshold operation at scale) are exactly what 2024–2025 experiments began testing on real hardware.

### 36.4 Error propagation

Two-qubit gates spread errors, and the spreading is directional. Through CNOT, X on the control propagates to both qubits and Z on the target propagates to both: X⊗I → X⊗X, I⊗Z → Z⊗Z. Inside a syndrome-extraction circuit this creates **hook errors**: one ancilla fault, propagated through the check's four CNOTs, can flip a line of data qubits if the gate order is naive. Fault-tolerant constructions order each check's CNOTs so that a single propagated fault stays within the correctable weight. This is why real syndrome circuits look over-constrained and why copying a circuit diagram from a paper without its gate ordering silently destroys the code's distance. Error propagation analysis is a core skill of QEC engineers.

### 36.5 Fault-tolerant gates

A transversal gate — one single-qubit gate per physical qubit, no interaction between qubits of the same block — is automatically fault-tolerant, since one fault stays on one qubit. The Steane code famously implements H, S, and CNOT (between blocks) transversally: a full fault-tolerant Clifford group. The surface code is stingier: CNOT between two aligned patches is transversal, H comes from lattice rotation, and S costs a round of patch deformation. The real workhorse is **lattice surgery**: merging and splitting patches of the code surface to induce logical measurements and CNOTs, spending space and time instead of extra structure. With these, all Clifford gates run on encoded data; the T gate does not — which forces 36.6.

### 36.6 Magic states

The Eastin–Knill theorem (2009) forbids any code from having a universal transversal gate set, so non-Clifford gates must come from somewhere else. The answer is **magic states** (magic states): special resource states prepared and purified offline, consumed online. The canonical one is |T⟩ = T|+⟩ = (|0⟩ + e^(iπ/4)|1⟩)/√2. Injected through a gate-teleportation circuit built from Clifford operations and measurements, one copy implements one logical T gate on encoded data. The economics are brutal: algorithms consume T gates by the millions (Shor-scale circuits are T-gate dominated), each requiring a fresh high-quality state, and the state's infidelity must sit *below* the code's logical error rate or it poisons every computation it touches.

### 36.7 Magic-state distillation

No physical process prepares |T⟩ well enough, so states are purified: **distillation** (distillation) consumes many noisy magic states and emits few clean ones. The Bravyi–Kitaev 15-to-1 protocol uses the [[15,1,3]] Reed–Muller code: fifteen input states, distillation circuits, one output with error squared; iterate to reach 10⁻¹². These distillation factories are typically the majority of a fault-tolerant machine's physical qubit budget. The 2024–2025 movement is aggressive cost reduction: **cultivation** — growing a T state inside a small surface-code patch, checking it, and discarding failures — plus new distillation protocols cut the per-T cost by roughly an order of magnitude. This is where much of the field's current resource-count progress comes from.

### 36.8 Resource overhead

Concrete anchor: factoring RSA-2048. Gidney and Ekerå's 2019 estimate: ~20 million physical qubits running 8 hours. Gidney's 2025 revision: under 1 million qubits running about a week — a 20× overhead reduction from cheaper logical qubits, cultivation, and arithmetic reorganization, at surface-code distances in the mid-20s (so ~1,200+ physical qubits per logical qubit for memory). These numbers come from simulation, but from validated, open-source simulation (37.9), and their trajectory is the honest summary of the field's progress: the estimate keeps falling, it remains enormous, and every sub-quarter of it — codes, decoders, distillation, compilation (Part XII) — is an active engineering front with hiring behind it.

> [!research] Research frontier
> The overhead war has three open fronts. First, **qLDPC codes**: IBM's [[144,12,12]] "gross code" stores 12 logical qubits in 144 physical ones — roughly a tenth of the surface-code footprint — and IBM demonstrated its memory experimentally in 2025; but such codes need long-range couplers and their decoders are harder. Second, **magic-state cost**: cultivation and new distillation protocols keep falling, yet no one knows the true floor. Third, **decoding co-design**: every overhead number assumes a decoder that exists, meets the latency budget, and scales — an assumption that is itself research (37.5–37.7).

### 36.9 Why fault tolerance is so expensive

Sum the costs. Qubit count: 2d² per logical qubit with d in the 20s–30s for serious algorithms. Factories: distillation and cultivation can consume the large majority of the machine. Time: every logical operation is interleaved with syndrome rounds, so the ~1 μs cycle time of superconducting hardware sets the wall clock; a week-long computation is ~10¹² rounds, each needing decode. I/O: every physical qubit wants its own control and readout line at millikelvin temperatures — wiring, not qubits, is often the harder systems problem. None of these is a single big fix; all are compounding constants. That is why "error-correction overhead" is named in Part I as the field's defining engineering problem, and why it hires.

## 37. Quantum Error Correction Engineering

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** QEC in the field is a real-time classical pipeline bolted to a quantum one: measure fast, decode faster, never fall behind.
> - **Mathematics —** decoding is statistical inference on a graphical model; benchmark numbers come from Monte Carlo over noise models.
> - **Implementation —** every piece here is reproducible on a laptop: stim for circuits, your own decoders, matplotlib for the curves.
> - **Engineering —** syndrome circuits at ~1 μs/round, decoders on FPGA with hard latency bounds, benchmarking discipline borrowed from HPC.
> - **Research —** decoders that are simultaneously accurate, fast, and general remain unsolved; this chapter's sections are hiring categories.

### 37.1 Syndrome extraction circuits

One syndrome round, in code: for each check, reset the ancilla, apply its four CNOTs in the fault-tolerant order, measure the ancilla. A full memory experiment wraps rounds in preparation and final data measurement: prepare |0_L⟩ or |+_L⟩, run d or more rounds, measure all data qubits. The noise model that matters is circuit-level: every reset, gate, and measurement fails with small probability. The saving grace of measurement errors is that they repeat: a bad measurement shows up as the same defect in two consecutive rounds, which decodes like a data error chain in time (35.9). Leakage — population escaping the two-level subspace — is the practical enemy, handled with leakage-reduction units inserted periodically.

### 37.2 Decoding algorithms

The decoder landscape sorts by a three-way trade: accuracy, throughput, latency. Minimum-weight perfect matching (37.3) is the accurate, mature default for surface codes. Union-find (Delfosse–Nickerson) runs in near-linear time with slightly worse accuracy — the real-time favorite. Belief propagation plus ordered-statistics post-processing (37.4) handles general parity-check codes where matching does not apply. Neural decoders (37.5) hold the accuracy record but miss real-time budgets. Every choice is a per-platform decision: a trapped-ion machine with millisecond cycles can afford what a 1-μs superconducting cycle cannot. Writing and benchmarking these decoders is software engineering through and through — graph algorithms, streaming data, hard real-time constraints.

### 37.3 Minimum-weight perfect matching

MWPM models the syndrome as a graph problem. Nodes are defect events (changed measurement outcomes); edges are candidate error chains, weighted by −log(probability) of the chain that connects the pair; the decoder finds the minimum-weight *perfect matching* — pairing every defect exactly once — and outputs the union of the matched chains as the correction. Edmonds' blossom algorithm makes this polynomial (O(v³) worst case), and modern implementations (pymatching's sparse blossom) reach millions of decodes per second per core. Matching is exactly optimal for graphlike noise — repetition codes, phenomenological noise — and merely near-optimal for full circuit-level surface-code noise, where error mechanisms like the hooks of 36.4 create correlations the graph model approximates. In practice it loses little; hence its dominance.

### 37.4 Belief propagation

Belief propagation (BP) is the general-purpose inference algorithm for codes described by a parity-check (Tanner) graph: variable nodes carry error probabilities, check nodes carry constraints, and messages pass between them each iteration until beliefs converge. Its virtue is generality — any parity-check matrix, including the dense, high-rate structures of qLDPC codes where matching is useless. Its vices are known: oscillation and non-convergence on quantum codes (loops in the Tanner graph), and blindness to degeneracy. The standard patch is BP + OSD (ordered-statistics post-processing): when BP fails to converge decisively, OSD re-solves a small linear system around BP's answer. Accuracy is strong; throughput is the open problem, since iteration counts are data-dependent — a real-time hazard.

### 37.5 Neural decoders

Neural decoders learn the syndrome-to-correction mapping from simulated or real data. The benchmark result: Google DeepMind's AlphaQubit (Nature, 2024), a transformer-based decoder, outperformed the best matching-based decoder on real Sycamore surface-code data — roughly 6% fewer logical errors — by exploiting correlations and device-specific noise that graph decoders model poorly. The catch is speed: at publication it was orders of magnitude too slow for real-time decoding, and its accuracy degrades on noise distributions it was not trained on. Current research splits between compressing accurate models onto FPGA-scale hardware and training small recurrent decoders that stream. For a software engineer, this is one of the cleanest intersections of ML systems and quantum hardware.

### 37.6 Real-time decoding

A superconducting surface-code round takes ~1 μs; the decoder must sustain that rate indefinitely or the backlog grows until the experiment drowns in undecoded syndromes. This is a hard real-time systems problem: worst-case latency matters, not average. The standard architecture is sliding-window decoding — decode rounds in overlapping windows with a lag of a few cycles, refining decisions as more context arrives. The difficulty is platform-dependent: trapped-ion cycles (~ms) leave room for heavier decoders, which is why real-time-decoded logical qubits were demonstrated on trapped ions (Quantinuum, 2024) before superconducting chips closed the gap. Any "logical qubit" claim that decoded offline should be read with this in mind.

### 37.7 Decoding hardware

The decoder is a classical computer co-designed with the quantum one, and its hardware is an embedded-systems discipline: fixed function, deterministic latency, streaming I/O (raw detector bits in, correction frames out, every cycle, forever). FPGA pipelines are the workhorse — union-find decoders map naturally to parallel hardware; ASICs have been proposed for production machines. GPU clusters dominate offline high-throughput work (benchmarking, training neural decoders). The interface contract matters as much as the core: a decoder that cannot absorb a burst of defects after a cosmic-ray hit will stall the machine. If you want a classical engineering role inside quantum computing with no physics degree required, this is the most direct one.

> [!research] Research frontier
> The decoding problem in its full generality is unsolved. For surface codes the question is throughput: matching decoders are near-optimal but approach hardware limits at large d, and neural decoders that beat their accuracy are too slow — closing that gap on FPGA is open. For qLDPC codes it is worse: BP+OSD is neither fast enough nor accurate enough for real-time use, and no decoder with provable performance guarantees exists for good finite-rate qLDPC codes. A general, fast, accurate decoder — or a proof that the trade-offs are fundamental — would reshape the resource estimates of all of 36.8.

### 37.8 Benchmarking codes

The standard benchmark is the memory experiment: prepare a logical state, run n syndrome rounds, decode, and extract the logical error *per cycle* ε_c(d). Report Λ = ε_c(d)/ε_c(d+2), the suppression factor per distance step: Λ > 1 means below threshold, and Λ ≈ 2.1 was Willow's headline number. Honest comparison requires fixing three things: the noise model (circuit-level depolarizing at stated rates), the decoder (name it and its settings), and the resource count (physical qubits per logical qubit). Benchmarks that omit any of the three are marketing. The same discipline generalizes to logical gate benchmarks (spot checks, randomized benchmarking on logical qubits) and to comparing code families — which is exactly what your project will practice.

### 37.9 Simulation with stim

stim (Gidney, 2021) is the field's standard stabilizer-circuit simulator: it generates surface-code circuits at any distance, samples detector events at millions of shots per second, and emits the *detector error model* that decoders consume. Paired with pymatching (decoder) and sinter (Monte Carlo driver), it reproduces every curve in this part on a laptop:

```python
import stim

circuit = stim.Circuit.generated(   # d=3 rotated surface-code memory experiment
    "surface_code:rotated_memory_z",
    distance=3, rounds=3,
    after_clifford_depolarization=0.001,
    after_reset_flip_probability=0.001,
    before_measure_flip_probability=0.001,
    before_round_data_depolarization=0.001,
)
sampler = circuit.compile_detector_sampler()
dets, obs = sampler.sample(shots=1000, separate_observables=True)
print(dets.shape, obs.shape)   # detector events and logical observables per shot
```

Use stim as your reference oracle: build first with it, then replace components with your own implementations and check agreement shot by shot.

### 37.10 Logical error experiments

The experiment behind every figure in this part: sweep physical error rate p and code distance d ∈ {3, 5, 7}; for each point run the memory experiment with a Monte Carlo loop of 10⁴–10⁶ shots; extract logical error per cycle; fit Λ and check the scaling against `A * (p/p_th)^((d+1)/2)`. Three things to look for in the data: the crossing point where curves for different d intersect (the threshold estimate), the vertical spacing between curves (Λ), and deviations at low p (the floor set by cosmic rays and bias — real experiments see it, simulations usually do not). Reproducing a Willow-style Λ ≈ 2 suppression plot from simulated data is a one-to-two-week laptop project and a legitimate portfolio piece — which is precisely the assignment below.

## Project — Implement a Surface-Code Simulator and Decoder

*Author: GLM-5.3*

Build the full QEC pipeline yourself, from noise to logical error curves, in Python with numpy only. External tools — stim, pymatching, sinter — are permitted *as oracles for validation and comparison*, never as the core: the point is that every number in your README is produced by code you understand line by line. This project is the level-3 (implementation) and level-4 (engineering) destination of Part X, and the strongest single piece of evidence you can put in a portfolio aimed at QEC roles.

#### Scope and architecture

A command-line tool with three layers, kept strictly separated:

- `noise.py` — circuit-level noise model: per-gate depolarizing, per-reset and per-measurement flip probabilities.
- `code.py` — the rotated surface code at distance d: data and measure qubit layout, check-to-qubit adjacency, one syndrome-extraction round.
- `decode.py` — decoders operating on a detector-event history (a 3D array: space × space × time).

The simulator tracks Pauli frame only (bitset algebra, 34.2) — never state vectors. That is not a shortcut; it is the same design decision production simulators make, and it is what lets you run 10⁵ shots for d = 7 on a laptop.

#### Milestones

1. **M1 — Repetition code end to end.** 1D chain, perfect measurements, min-weight decoding (35.9 experiment generalized to any d). *Acceptance:* measured `p_L` matches `3p^2 - 2p^3` at d = 3 within Monte Carlo error; curves for d = 3, 5, 7, 9 cross at p = 0.5.
2. **M2 — Surface-code layout and syndrome rounds.** Rotated d = 3 and d = 5: build the check adjacency, simulate one memory experiment with phenomenological noise (data errors + measurement flips). *Acceptance:* with noise off, zero defects; with measurement noise only, defects appear in time pairs; logical operator verification by construction (the two boundary-spanning strings of 35.8).
3. **M3 — Matching decoder.** Implement the min-weight pairing for the 2D per-round graph, then extend to space-time matching across rounds (pairing defects including time-separated pairs). Core must be yours: a blossom implementation or, acceptably, union-find with a documented accuracy trade-off. *Acceptance:* on d = 3, your decoder's `p_L` agrees with pymatching within error bars on 10⁵ shared shots.
4. **M4 — Threshold scan.** Sweep p from 0.5% to 2% at circuit-level noise, d ∈ {3, 5, 7}, ≥ 10⁴ shots per point. *Acceptance:* curves cross between 0.5% and 1.5% (your threshold estimate, with error bars); below the crossing, Λ > 1 and the spacing fits `A(p/p_th)^((d+1)/2)` within a factor of 2.
5. **M5 — Report.** README with plots (logical vs physical error, Λ fit), runtime table (shots/second per d), and an honest limitations section. *Acceptance:* a reader can reproduce every figure from the repo in under 30 minutes.

#### Validation protocol

After each milestone, run the same experiment through stim + pymatching and diff the outputs: detector counts per shot, matching weights, logical outcomes. Any unexplained discrepancy is a bug in your code or in your mental model — both worth their weight in gold. Document three such discrepancies and their root causes in the README; that section will teach an interviewer more than the plots.

#### Stretch goals

- Circuit-level hook errors: show the logical error rate *worsen* with naive CNOT ordering at fixed distance — the 36.4 lesson made visible.
- Lattice surgery: implement a logical CNOT between two patches and measure its logical error rate against the memory baseline.
- A trained neural decoder (small MLP on detector histories) compared against matching on accuracy, with an honest latency measurement.
- A qLDPC comparison: decode the same syndrome data with BP+OSD and discuss where matching fails structurally.
- Scale test: d = 11 with the union-find decoder; report where your implementation stops being real-time and why.

Time budget: 3–6 weeks part-time. The deliverable is a public repository with tests, plots, and the validation log — the artifact that turns "I read Part X" into "I built Part X".
