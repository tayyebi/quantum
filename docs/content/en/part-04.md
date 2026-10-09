# Part IV — Quantum Mechanics Without Drowning in Physics

*Author: GLM-5.3*

Everything a quantum engineer needs of quantum mechanics, expressed as postulates, a qubit, gates, and measurement — with numpy instead of derivations.

## 8. The Postulates

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** quantum mechanics is a small set of rules for storing, changing, and reading information in a system.
> - **Mathematics —** states are vectors, observables are Hermitian operators, evolution is unitary, measurement follows the Born rule.
> - **Implementation —** build states and density matrices in numpy, apply channels, verify probabilities and expectation values numerically.
> - **Engineering —** real devices are never in pure states; density matrices and quantum channels are how noise actually enters your models.
> - **Research —** what lies outside the standard postulates (collapse dynamics, measurement back-action models) is still an active physics debate.

### 8.1 Physical states and state vectors

The first postulate: the state of an isolated physical system is completely described by a state vector — a vector in a complex vector space, normalized to length 1. The word *completely* is doing heavy lifting: the vector holds everything that can be known about the system. For a qubit the space is two-dimensional and a general state is written α|0⟩ + β|1⟩ with complex α, β. Two engineering habits follow. First, normalization is a constraint your code must enforce or check: np.linalg.norm(psi) must equal 1 (up to floating-point slack). Second, the state vector is not a property you can read out; it is a bookkeeping device from which measurement statistics are derived. Chapters 9–11 unpack exactly that machinery.

### 8.2 Observables and measurement

The second postulate: every measurable quantity — energy, spin, parity — corresponds to an **observable**, a Hermitian operator A. Hermitian means A = A† (equal to its conjugate transpose), which guarantees real eigenvalues: you never measure a complex number. The possible measurement outcomes are exactly the eigenvalues of A. If the system is in state |ψ⟩, the probability of obtaining eigenvalue aᵢ is |⟨aᵢ|ψ⟩|², where |aᵢ⟩ is the matching eigenvector. For qubits the observables that matter are the Pauli operators X, Y, Z — every hardware readout in this book reduces to measuring one of them. Keep the sequence in mind: choose an observable, project the state onto its eigenbasis, square the amplitudes. That is the whole measurement model.

### 8.3 Unitary evolution and composite systems

The third postulate: while a system evolves unmeasured, its state changes by a **unitary** operator U, giving |ψ⟩ → U|ψ⟩. Unitary means U†U = I: the operation preserves vector norms, hence total probability, and is invertible — quantum evolution never loses information on its own. This is why quantum gates must be reversible and why you cannot "just copy" a state (no-cloning, 13.1). The fourth postulate covers **composite systems**: the state space of two systems is the tensor product of the individual spaces. A two-qubit state lives in a 4-dimensional space, n qubits in 2ⁿ dimensions. Critically, the combined space also contains vectors that are *not* tensor products — entangled states — which is the single most consequential fact in this book. Parts V builds directly on it.

```text
Postulates as a pipeline:

  state  |ψ⟩ ──(unitary U)──▶ U|ψ⟩ ──(measure A)──▶ eigenvalue aᵢ  with probability |⟨aᵢ|ψ⟩|²
                                                     │
                                                     ▼
                                          state collapses to |aᵢ⟩

  composite: state space = space₁ ⊗ space₂  (dimensions multiply, not add)
```

### 8.4 The Born rule and expectation values

The **Born rule** is the bridge between amplitudes and data: measuring observable A on state |ψ⟩ yields outcome aᵢ with probability pᵢ = |⟨aᵢ|ψ⟩|². The **expectation value** ⟨A⟩ = ⟨ψ|A|ψ⟩ = Σᵢ pᵢ·aᵢ is the average over infinitely many repetitions — it is what a finite-shot experiment estimates. Two facts engineers use daily. First, ⟨A⟩² ≤ ⟨A²⟩, with equality only for eigenstates; the gap tells you how noisy your readout is. Second, expectation values are linear in the state but not in the probabilities, which is why interference can move averages in ways classical randomness cannot. Every histogram in this book is an empirical Born rule: sample outcomes, count frequencies, compare against computed probabilities.

### 8.5 Pure states, mixed states, and density matrices

A **pure state** is one state vector; a **mixed state** is a classical probabilistic mixture of pure states — "the device prepared |0⟩ half the time and |1⟩ half the time" — and no single vector describes it. The **density matrix** ρ unifies both: for a pure state ρ = |ψ⟩⟨ψ| (an outer product, a 2×2 matrix for one qubit); for a mixture ρ = Σⱼ pⱼ|ψⱼ⟩⟨ψⱼ|. Measurement statistics are then ⟨A⟩ = Tr(ρA), always. A quick diagnostic you will use constantly: a state is pure exactly when ρ² = ρ, i.e. Tr(ρ²) = 1; mixed states have Tr(ρ²) < 1. Real hardware prepares pure states imperfectly, so after Part XI every "state" in this book quietly becomes a density matrix. Learn ρ now and noise stops being mysterious later.

### 8.6 Quantum channels

A **quantum channel** is the most general physically allowed evolution of a density matrix: a linear, completely positive, trace-preserving map ρ → E(ρ). Unitary evolution is the special case E(ρ) = UρU†; everything else is noise. The workhorse is the **depolarizing channel**: with probability p replace the state by the maximally mixed matrix I/2, otherwise apply the intended unitary. Its effect on one-qubit gate fidelity is exactly p = 1 − F. Channels compose like functions: apply a depolarizing channel after every gate and you have a crude but honest circuit-noise model, the kind Part X error correction assumes. Writing your own channel in numpy is ten lines and permanently demystifies phrases like "amplitude damping" and "readout error" in hardware papers.

> [!experiment] On your laptop — density matrices and a depolarizing channel
> ```python
> import numpy as np
>
> ket0 = np.array([1, 0], dtype=complex)
> ket1 = np.array([0, 1], dtype=complex)
>
> # pure state |+> = (|0> + |1>)/sqrt(2) as a density matrix
> plus = (ket0 + ket1) / np.sqrt(2)
> rho = np.outer(plus, plus.conj())
>
> # mixture: half |0>, half |1>
> rho_mix = 0.5*np.outer(ket0, ket0) + 0.5*np.outer(ket1, ket1)
>
> def purity(r): return np.real(np.trace(r @ r))
> print(purity(rho), purity(rho_mix))          # 1.0  vs  0.5
>
> # depolarizing channel: with prob p, replace by I/2
> def depolarize(r, p):
>     return (1-p)*r + p*np.eye(2)/2
> print(purity(depolarize(rho, 0.3)))          # < 1: noise makes states mixed
> ```
> The purity readout is your first noise meter; Part X upgrades it to logical error rates.

> [!research] Research frontier
> The measurement postulate is the least settled part of the theory: why do unitary evolution and probabilistic collapse coexist, and can the transition be modeled dynamically? Decoherence theory (Zurek's environment-induced selection) explains the *appearance* of collapse for open systems, and interpretations from many-worlds to QBism agree on all laboratory predictions. As an engineer you can stay agnostic — the density-matrix/channel formalism is interpretation-independent — but adaptive-measurement and back-action-evading schemes (11.11) make the question practically relevant.

## 9. A Qubit

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** a qubit is a unit vector with two complex components; direction on a sphere is the state, and phases encode information length cannot.
> - **Mathematics —** |ψ⟩ = α|0⟩ + β|1⟩ with |α|² + |β|² = 1; global phase is invisible, relative phase is physical.
> - **Implementation —** map amplitudes to Bloch sphere coordinates in numpy and animate rotations with real 2×2 matrices.
> - **Engineering —** hardware qubits are analog objects: calibration errors appear as small angle miscalibrations on the Bloch sphere.
> - **Research —** higher-dimensional qudits and continuous-variable encodings trade the two-level abstraction for denser state spaces.

### 9.1 The classical bit and its physical implementations

Start with what you know. A **classical bit** holds one of two values, and its meaning is independent of its physical carrier: a 5 V wire, a magnetic domain, a charge trap, a "3 nm" transistor with a few hundred atoms of channel. Engineering has driven bit error rates to roughly 10⁻¹⁸ per operation by burying physics under abstraction: voltage margins, ECC in DRAM, and CMOS's nonlinear restoration of logic levels make a noisy physical device behave like a clean mathematical symbol. Two properties matter for the contrast ahead: you can *copy* a bit freely, and you can *read* it without changing it. Both feel like birthrights of information. Quantum mechanics revokes both, and the next sections show exactly how much survives.

### 9.2 The qubit and its basis states |0⟩, |1⟩

A **qubit** (quantum bit) is a two-level quantum system: an electron's spin, a superconducting circuit's two lowest energy levels, an ion's two internal states. Its state is a unit vector in a two-dimensional complex space, written in the computational basis as |ψ⟩ = α|0⟩ + β|1⟩. The basis states are the ground and excited levels — the quantum analogs of 0 and 1 — and they are perfectly good classical states: a qubit prepared in |0⟩ or |1⟩ behaves like a bit. The generalization is that α and β may both be nonzero. Note what a qubit is *not*: not a bit that is "0 and 1 at once" in any readable sense. It is a vector; reading it (measurement, chapter 11) collapses the description to one outcome with probabilities |α|² and |β|².

### 9.3 Superposition and amplitudes

**Superposition** means the state is a weighted combination α|0⟩ + β|1⟩; the weights α, β are **amplitudes** — complex numbers, not probabilities. The Born rule converts them: measuring in the computational basis yields 0 with probability |α|² and 1 with probability |β|². Why complex numbers? Because amplitudes add and interfere: two paths to the same outcome can cancel like waves, which classical probabilities can never do. That interference is the engine of every quantum algorithm (Part VII). A useful sanity bound: |α|² + |β|² = 1 always, so nothing about superposition increases information capacity — one qubit answers one yes/no question per measurement. Superposition is not "more information stored"; it is a richer *dynamics* for computing with.

### 9.4 Normalization and global phase

Two subtleties, both cheap to handle in code. **Normalization**: |α|² + |β|² = 1, so a state vector has one redundant real degree of freedom; simulators enforce it explicitly — `psi /= np.linalg.norm(psi)` — because gates like H are only norm-preserving on normalized inputs, and unnormalized states quietly produce probabilities that sum to 0.97 and other nonsense. **Global phase**: multiplying the entire state by any unit-modulus complex number, e.g. e^{iπ/4}|ψ⟩, changes nothing observable: every probability and expectation value involves ⟨ψ|ψ⟩-type contractions where the phase cancels. So states with a common global phase are *the same physical state*. In simulators this is harmless; in hardware it means calibration can ignore the overall phase entirely — a real simplification the phase gate family (10.6) exploits.

### 9.5 Relative phase

What *is* physical is the **relative phase** between amplitudes: the angle of β/α, a complex number's argument. |0⟩ + |1⟩ and |0⟩ − |1⟩ have identical measurement statistics in the computational basis — both give 50/50 — yet they are different states, distinguishable by measuring in the X basis (11.6), where they are eigenstates with eigenvalues +1 and −1. Relative phase is where quantum information hides from casual observation, and it is the control surface for interference: algorithms steer relative phases with gates (Z, S, T, Rz), then convert phase differences into outcome-probability differences using H. In the Bloch picture below, relative phase is the longitude; you will manipulate longitudes constantly and measure latitudes. That asymmetry is the daily texture of quantum programming.

### 9.6 Measurement probabilities

For state α|0⟩ + β|1⟩, computational-basis measurement gives p(0) = |α|², p(1) = |β|². Worked examples you should internalize until they are reflexes: |0⟩ → (1, 0); (|0⟩+|1⟩)/√2 → (½, ½); (|0⟩+i|1⟩)/√2 → (½, ½) — same probabilities as the previous state, different state, as 9.5 promised; (√3|0⟩ + |1⟩)/2 → (¾, ¼). One measurement returns one bit and destroys the superposition; the probabilities only reveal themselves over many identical preparations and measurements — **shots**. This is why quantum benchmarks are statistical and why 1,000 shots give you roughly ±1.5% resolution per probability (11.10). Every hardware readout in this book — IBM, Google, ion traps — produces exactly this: many shots, one histogram.

```python
import numpy as np

def probs(psi):
    return np.abs(psi)**2

states = {
    "|0>":        np.array([1, 0], dtype=complex),
    "|+>":        np.array([1, 1], dtype=complex) / np.sqrt(2),
    "|+i>":       np.array([1, 1j], dtype=complex) / np.sqrt(2),
    "(3|0>+|1>)/2": np.array([np.sqrt(3), 1], dtype=complex) / 2,
}
for name, psi in states.items():
    psi = psi / np.linalg.norm(psi)
    p = probs(psi)
    print(f"{name:12s}  p(0)={p[0]:.3f}  p(1)={p[1]:.3f}")
```

### 9.7 The Bloch sphere

Because global phase is irrelevant, a qubit's state has two real degrees of freedom, and every pure state maps to a point on the **Bloch sphere** — a unit sphere with |0⟩ at the north pole, |1⟩ at the south pole, and equatorial points (|0⟩ ± |1⟩)/√2 and (|0⟩ ± i|1⟩)/√2 at the cardinal longitudes. For state α|0⟩ + β|1⟩, write the vector as cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩; the Bloch coordinates are (sin θ cos φ, sin θ sin φ, cos θ). The mapping is the engineer's microscope: superposition is latitude away from the poles, relative phase is longitude, and measurement in the Z basis returns 0 with probability cos²(θ/2). Mixed states live *inside* the sphere, at radius Tr(ρ²) — noise shrinks the vector toward the center, called depolarization.

```text
            z
            |    |0>  (theta = 0)
            |   /
            |  /  theta
            | /         |psi> = cos(theta/2)|0> + e^{i phi} sin(theta/2)|1>
            |/_____ y
           / \    |+i> at phi = +90
          /   \
         x    |+> at phi = 0      |1> at theta = pi (south pole)
```

### 9.8 Rotations and geometric intuition

Every single-qubit gate is a **rotation** of the Bloch vector about some axis (up to an invisible global phase) — this is the geometric reading of chapter 10. The rotation gates Rx(θ), Ry(θ), Rz(θ) rotate the Bloch vector by angle θ about the x, y, z axes respectively. Two intuitions to build now. First, the Hadamard gate, which looks algebraic as a matrix of ½'s, is geometrically a 180° rotation about the diagonal axis (x+z)/√2: it swaps the poles with the equator, exactly why it converts between Z-basis and X-basis states. Second, two rotations about non-parallel axes generate *every* possible rotation — which is why some minimal pair like Rz and √X suffices as a hardware gate set (10.11). Calibration engineers literally think in angles: a mis-tuned pulse is "rotation off by 3°".

> [!experiment] On your laptop — Bloch coordinates and a rotation movie
> ```python
> import numpy as np
>
> # H, Rz, and Bloch coordinates of the resulting state
> H  = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
> def Rz(t):
>     return np.array([[np.exp(-1j*t/2), 0],
>                      [0, np.exp(1j*t/2)]], dtype=complex)
>
> ket0 = np.array([1, 0], dtype=complex)
> psi = Rz(np.pi/4) @ H @ ket0            # prepare, then rotate about z
>
> a, b = psi
> x = 2*np.real(np.conj(a)*b)             # Bloch components
> y = 2*np.imag(np.conj(a)*b)
> z = abs(a)**2 - abs(b)**2
> print(np.round([x, y, z], 3))           # [0.707, 0.707, 0.0]
> ```
> Change the Rz angle and watch the point sweep the equator: longitude is relative phase, exactly as 9.5 said.

> [!research] Research frontier
> The two-level qubit is a choice, not a law. **Qudits** (d-level systems) pack log₂ d bits of basis per carrier; **continuous-variable encodings** use oscillator modes with infinite-dimensional state spaces, and **cat qubits** engineer a two-level subspace inside an oscillator to suppress one error type. Each trades the clean 2×2 algebra of this chapter for denser, noisier structure. The open question — which encoding wins the full stack contest of overhead, control fidelity, and decodability — is unresolved and platform-dependent (Part XI).

## 10. Single-Qubit Gates

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** gates are rotations of the Bloch sphere; a handful of them, sequenced, reach any qubit state.
> - **Mathematics —** gates are 2×2 unitary matrices; arbitrary rotations are exponentials of the Pauli matrices.
> - **Implementation —** apply X, H, S, T, and rotations in numpy; verify algebra like HXH = Z numerically.
> - **Engineering —** hardware exposes a small native set (Rz, √X); everything else is synthesized, and each extra gate adds error.
> - **Research —** optimal gate synthesis — fewest pulses for a target unitary within a fidelity budget — remains an active compilation problem.

### 10.1 The Pauli gates: I, X, Y, Z

Four 2×2 matrices do most of the algebra of one qubit. **I** leaves the state alone. **X** = [[0,1],[1,0]] is the quantum NOT: it swaps |0⟩ and |1⟩, a 180° rotation about the x-axis. **Z** = [[1,0],[0,−1]] leaves |0⟩ and |1⟩ fixed but flips the relative phase of superpositions — a 180° rotation about z, so it maps |+⟩ to |−⟩. **Y** = [[0,−i],[i,0]] is the x-rotation and z-rotation composed; it maps |+⟩ to −i|−⟩'s orthogonal partner and differs from XZ by a factor of i — a global phase, physically irrelevant (10.12). They satisfy the multiplication table X·Y = iZ (and cyclic), plus X² = Y² = Z² = I. Their eigenvectors are exactly the cardinal points of the Bloch sphere: X's are |±⟩, Z's are |0⟩, |1⟩.

```python
import numpy as np

I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.diag([1, -1]).astype(complex)

# the Pauli multiplication table, numerically
for name, M in [("XY", X @ Y), ("YZ", Y @ Z), ("ZX", Z @ X)]:
    print(name, "->", np.round(M, 2).tolist())    # each equals i times the third Pauli

H = np.array([[1, 1], [1, -1]], dtype=complex)/np.sqrt(2)
print(np.allclose(H @ X @ H, Z))                  # H X H = Z  ->  True
```

### 10.2 The Hadamard gate

**H** = (1/√2)[[1,1],[1,−1]] is the single most used gate in quantum computing. It maps |0⟩ → |+⟩ = (|0⟩+|1⟩)/√2, |1⟩ → |−⟩ = (|0⟩−|1⟩)/√2, and — being its own inverse (H² = I) — maps |+⟩ → |0⟩ and |−⟩ → |1⟩. Two readings. Geometrically: a 180° rotation about the (x+z)/√2 axis, exchanging the poles with two equatorial points. Algebraically: the Z-basis to X-basis change of basis, which is why "measure in the X basis" is universally implemented as H-then-measure-Z (11.6). Algorithmically: H is the interference engine — it creates superposition uniformly (part of every "spread the amplitudes" step) and, applied again, recombines paths so amplitudes can cancel. Grover, the QFT sampler, and every random circuit benchmark start with H.

### 10.3 Phase gates: S and T

Phase gates act only on the amplitude of |1⟩, leaving |0⟩ untouched. **S** = diag(1, i) adds 90° to the relative phase; **T** = diag(1, e^{iπ/4}) adds 45°. Powers of Z: S² = Z, T² = S, T⁴ = Z. Why care about tiny angle tweaks? Because relative phase is invisible to Z-measurement but *is* visible after a Hadamard (or any X-basis rotation), and it is the raw material of interference. Concretely: H T H = a rotation about x by 45°, so combining T, H, and X you can synthesize rotations of arbitrary small angle — and T is the gate that makes the common hardware set {Rz, √X, T-ish pulses} universal for one qubit. On error-corrected hardware, T is famously expensive (it leaves the Clifford subgroup, Part X), so compilers hoard and distill it.

```text
Effect on the equator (relative phase of |1> added by each gate):

  T: +45°   S: +90°   Z: +180°        S = T·T,  Z = S·S

  |+>  --T-->  phase 45°  --H-->  rotated Bloch vector, tilted off the equator
```

### 10.4 Rotation gates

For any axis â in the Bloch picture, the rotation by angle θ is U = e^{−iθ(â·σ)/2}, where σ is the relevant Pauli matrix. Explicitly: **Rx(θ)** = cos(θ/2)I − i sin(θ/2)X, and similarly **Ry**, **Rz** with Y and Z. Three practical notes. First, the half-angle: a "π rotation" changes the Bloch vector by 180°, which surprises everyone once. Second, Rx and Ry mix amplitudes (they move the pole), while Rz only changes relative phase — hardware implements Rz as a cheap frame update, essentially free. Third, rotations compose like angles about the same axis: Rx(α)·Rx(β) = Rx(α+β), which makes arbitrary-angle pulses natural for analog control. In numpy these are one line each and are the gates you will reach for when building geometric intuition or calibrating a toy simulator.

### 10.5 Arbitrary single-qubit rotations and gate decomposition

The gate decomposition theorem: *any* 2×2 unitary U equals a product Rz(α)·Ry(β)·Rz(γ) (up to global phase) — the ZYZ decomposition, with three real parameters matching the Bloch sphere's two angles plus the invisible phase. In circuit terms: any single-qubit operation is three rotation gates. Real hardware goes further with Euler-angle scheduling: IBM machines natively implement U(θ, φ, λ) in one pulse, and compilers rewrite every gate into that native form. The engineering lesson generalizes beyond one qubit: decomposition is how an abstract circuit becomes a device schedule, and the cost metric is *count of native gates*, because each native gate carries error ≈ 10⁻³ (Part XI). Chapter 14 repeats this theme with two-qubit synthesis, where the arithmetic is harsher.

> [!experiment] On your laptop — decompose and verify a random unitary
> ```python
> import numpy as np
>
> def Rz(t): return np.diag([np.exp(-1j*t/2), np.exp(1j*t/2)])
> def Ry(t): return np.array([[np.cos(t/2), -np.sin(t/2)],
>                             [np.sin(t/2),  np.cos(t/2)]], dtype=complex)
>
> rng = np.random.default_rng(7)
> U = np.linalg.qr(rng.normal(size=(2, 2)) + 1j*rng.normal(size=(2, 2)))[0]
> # ZYZ angles from U (standard textbook formulas)
> beta = 2*np.arctan2(abs(U[1, 0]), abs(U[0, 0]))
> print("recovered beta/2 =", beta/2)
> # full check: solve for alpha, gamma, then test U ≈ Rz(alpha) Ry(beta) Rz(gamma)
> ```
> Fill in the angle extraction — it is a five-line algebra exercise that makes the decomposition theorem yours.

### 10.6 Universality

A gate set is **universal** if arbitrary unitaries can be approximated to any accuracy by products of its members. The classic result: {H, T, CNOT} is universal for all quantum computation; among single-qubit sets, {H, T} suffices because H plus a 45° phase generates a dense group of rotations (the angles produced are irrational multiples of π, so products never close up — they approximate everything). Contrast with the Clifford group {H, S, CNOT}, which is *not* universal and — deeper — is classically simulable via the Gottesman–Knill theorem (Part X): exactly the boundary that makes T gates precious. Universality is an asymptotic statement; the engineering question is always *at what cost*, which is where synthesis (14.10) and error budgets take over.

### 10.7 Global phase vs observable phase

One distinction, stated sharply because it causes real bugs. **Global phase**: |ψ⟩ and e^{iθ}|ψ⟩ are the same physical state; no measurement distinguishes them. In code, this means comparing states requires comparing projectors or checking inner products up to a phase: `abs(np.vdot(psi1, psi2)) ≈ 1`, never elementwise equality. **Relative (observable) phase**: the phase *between* superposed components is physical — |+⟩ and |−⟩ differ measurably in the X basis, and interference in every algorithm depends on it. The rule of thumb: operations that multiply the *whole* vector by a phase are free and unobservable; operations that multiply *one component* by a phase (Z, S, T) are gates that do work. Simulation frameworks differ in whether they preserve global phase; do not diff circuits by their raw state vectors.

> [!experiment] On your laptop — the full single-qubit toolchain
> ```python
> import numpy as np
>
> ket0 = np.array([1, 0], dtype=complex)
> ket1 = np.array([0, 1], dtype=complex)
> H = np.array([[1, 1], [1, -1]], dtype=complex)/np.sqrt(2)
> S = np.diag([1, 1j]).astype(complex)
>
> psi = S @ H @ ket0                       # |+> shifted 90 degrees in phase
> p = np.abs(psi)**2                       # Z-measurement probabilities
> psi_x = H @ psi                          # rotate to measure in X basis
> px = np.abs(psi_x)**2
> print("Z basis:", p, " X basis:", px)    # X basis shows the S gate's work
> ```
> The S gate is invisible to a Z-measurement and fully visible in X. Every "hidden phase" experiment in hardware works exactly like this.

> [!research] Research frontier
> **Optimal gate synthesis**: given a target unitary and a fidelity budget, what is the shortest native-pulse sequence? Exact optimal synthesis over continuous sets is solved for one qubit, but with realistic constraints — leakage levels, pulse bandwidth, crosstalk, calibration drift — pulse-level compilation is open and platform-specific. Machine-learning pulse shapers and closed-loop optimization (GRAPE-family methods) compete with analytic constructions; neither dominates yet (Part XII).

## 11. Measurement

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** measurement is the only way information leaves the quantum system, and it disturbs what it reads.
> - **Mathematics —** projectors Pᵢ give probabilities pᵢ = ⟨ψ|Pᵢ|ψ⟩; the state after outcome i is Pᵢ|ψ⟩/√pᵢ.
> - **Implementation —** simulate shots, collapse states, estimate ⟨Z⟩ and ⟨X⟩ from samples with error bars.
> - **Engineering —** readout is a physical, noisy, slow channel: ~1% error, microseconds, and it is often the experiment's bottleneck.
> - **Research —** weak measurement, back-action steering, and the quantum-classical boundary remain actively debated and experimentally refined.

### 11.1 Projective measurement and measurement probabilities

Formally, measuring observable A means applying the **projective measurement** {Pᵢ}, where Pᵢ projects onto the eigenspace of eigenvalue aᵢ and Σᵢ Pᵢ = I. Outcome i occurs with probability pᵢ = ⟨ψ|Pᵢ|ψ⟩. For one qubit measuring Z: P₀ = |0⟩⟨0⟩, P₁ = |1⟩⟨1⟩, and p₀, p₁ are the |α|², |β|² of chapter 9. The projector formulation is worth the notation because it generalizes cleanly: multi-qubit measurement, partial measurement (measure qubit 2 only), and error-syndrome extraction (Part X) are all the same formula with bigger projectors. In numpy, pᵢ is just `np.real(np.vdot(psi, P_i @ psi))`. One caution: projectors for degenerate (repeated) eigenvalues sum over the whole eigenspace — a detail that matters from chapter 13 onward.

### 11.2 State collapse

When outcome i occurs, the state becomes |ψ′⟩ = Pᵢ|ψ⟩/√pᵢ — renormalized, because the outcome carried probability pᵢ and the vector must have norm 1 again. This is **collapse**: measurement is destructive and nonlinear, the one non-unitary step in the theory. Two consequences programmers must internalize. First, you cannot observe a state and continue computing on what you saw — hardware gives you one classical bit, and the quantum state is gone (or replaced by the eigenstate). Second, conditioning matters: after measuring qubit 0 and getting 1, the state of qubit 1 must be updated to the conditional state — teleportation (13.5) and error correction are built entirely on this rule. In simulators, collapse is one line: mask the amplitudes, renormalize.

```python
import numpy as np

psi = np.array([1, 1, 1, 1], dtype=complex) / 2   # two-qubit |++>

# measure qubit 0, outcome |1>: amplitudes where bit0 == 1 survive
mask = np.array([0, 1, 0, 1], dtype=bool)         # order: |00>,|01>,|10>,|11>
psi_post = np.where(mask, psi, 0)
psi_post /= np.linalg.norm(psi_post)
print(np.round(psi_post, 3))                      # [0, 0.707, 0, 0.707] -> qubit1 still |+>
```

### 11.3 Measurement in different bases: computational, X, and Y

Measurement is always *in some basis*, and choosing the basis is choosing what question you ask. The **computational (Z) basis** {|0⟩, |1⟩} is what hardware physically reads. The **X basis** {|+⟩, |−⟩} asks the other pole: to measure it, apply H then read Z, since H converts X-eigenstates into Z-eigenstates. The **Y basis** {|+i⟩, |−i⟩} needs S† before the H: measuring Y on (|0⟩+i|1⟩)/√2 deterministically gives +1. Nothing mystical distinguishes the bases — they are three orthogonal coordinate systems on the same Bloch sphere, and any two non-parallel bases yield genuinely incompatible information (measuring X after preparing |+⟩ is deterministic; measuring Z after it is a coin flip). Algorithm design is largely the art of choosing which basis to interrogate at which moment.

```text
Measure in basis B  =  rotate B to Z, then read Z:

  X basis:   --H-- --Z-read--        Y basis:   --S†-- --H-- --Z-read--
```

### 11.4 Expectation values from data

For observable A with eigenvalues aᵢ and outcome probabilities pᵢ, the expectation value ⟨A⟩ = Σ pᵢ aᵢ is estimated from N shots by the sample mean, and that is what hardware experiments actually compute: Z-measurement gives ⟨Z⟩ = p(0) − p(1) ∈ [−1, +1]; ⟨X⟩ comes from H-then-read as p(+) − p(−). ⟨Z⟩ = +1 means deterministically |0⟩; ⟨Z⟩ = 0 means maximum uncertainty — for |+⟩ exactly. Expectation values are the *observable* outputs of every algorithm in this book: variational algorithms (Part VII) optimize them directly, and Bell-inequality tests (13.4) combine four of them. When a paper claims a result, the claim lives in these averages plus their confidence intervals — never in a single shot. Learn to read ⟨A⟩ ± δ⟨A⟩ as the native currency of experimental quantum computing.

### 11.5 Repeated measurements and statistical estimation

Identical preparations, repeated measurements, counted frequencies — this is **shots**-based testing, and it obeys ordinary statistics. For N shots, the standard error of an estimated probability p is √(p(1−p)/N): 100 shots give ~±5%, 10,000 give ~±0.5%. The estimate is a binomial proportion, so confidence intervals come from the standard toolbox (or bootstrap). Two engineering habits. First, budget shots like budgeting test runs: estimation cost multiplies fast when a circuit has many expectation values or when hardware time is scarce and queued. Second, distinguish statistical noise from systematic noise: more shots tighten the *statistical* bar, but readout bias or drift moves the mean itself and no amount of repetition fixes it (Part XI). Simulators, unlike hardware, give you the exact probabilities too — use them to validate your sampling code.

> [!experiment] On your laptop — estimate ⟨X⟩, ⟨Y⟩, ⟨Z⟩ with error bars
> ```python
> import numpy as np
>
> rng = np.random.default_rng(1)
> psi = np.array([1, 1j], dtype=complex); psi /= np.linalg.norm(psi)  # |+i>
>
> # measurement bases: rows are the two outcomes' rotated |0>,|1>
> bases = {"Z": np.eye(2, dtype=complex),
>          "X": np.array([[1, 1], [1, -1]], dtype=complex)/np.sqrt(2),
>          "Y": np.array([[1, -1j], [1, 1j]], dtype=complex)/np.sqrt(2)}
> for name, B in bases.items():
>     probs = np.abs(B @ psi)**2; probs /= probs.sum()
>     shots = rng.choice(2, size=10_000, p=probs)
>     exp = (shots == 0).mean() - (shots == 1).mean()
>     print(f"<{name}> = {exp:+.3f}  (theory: {np.real(np.vdot(psi, {'Z':np.diag([1,-1]),'X':np.array([[0,1],[1,0]]),'Y':np.array([[0,-1j],[1j,0]])}[name]) @ psi):+.3f})")
> ```
> Expect ⟨Y⟩ ≈ +1 and the others ≈ 0: the state is the Y-eigenstate |+i⟩, exactly as 11.3 predicted.

### 11.6 Weak measurement

**Weak measurement** relaxes the measurement interaction so little information is extracted that the state is barely disturbed — collapse becomes a small, probabilistic nudge of the Bloch vector toward the measured eigenstate. Gaining partial information p about the state costs partial disturbance, quantified by measurement-disturbance tradeoffs. Engineering uses: qubit state tracking during computation, calibration readout that does not destroy the data qubit, and — in hardware labs — the feedback signal for real-time control. Formalism: measurement operators Mₘ with Σ Mₘ†Mₘ = I, weaker than projectors; the post-measurement state is Mₘ|ψ⟩/√pₘ, where Mₘ ≈ I ± εP for small ε. Weak measurements accumulate: many of them, averaged, reconstruct the state ensemble without collapsing any single run — genuinely different from strong measurement, and experimentally routine since ~2008.

### 11.7 Measurement as information extraction

The unifying view: measurement is a **channel with classical output** — quantum state in, classical bits out, with back-action on the state. This framing dissolves two confusions. First, "observation" is not special: a readout is just a physical interaction whose result is recorded irreversibly in a classical system; the irreversibility (the record) is what makes it a measurement. Second, information and disturbance are two ends of one budget: extract one bit about the state and you disturb it by at least the amount the tradeoff relations dictate. Every architecture in this book routes information this way — circuits end in measurement, error correction extracts syndromes without touching logical data (Part X), and hardware calibrates by interleaving weak and strong readout. When you design an experiment, first ask: what information leaves the quantum system, and what does extracting it cost the state?

> [!experiment] On your laptop — collapse and conditional states, end to end
> ```python
> import numpy as np
>
> # entangled pair; measure qubit 0, watch qubit 1 follow
> bell = np.array([1, 0, 0, 1], dtype=complex)/np.sqrt(2)   # (|00>+|11>)/sqrt(2)
> rng = np.random.default_rng(3)
> outcome = rng.choice([0, 1], p=np.abs(bell[[0, 3]])**2 / 1.0)  # p(0)=p(1)=1/2 on qubit 0
> keep = [0, 3] if outcome == 0 else [1, 2]                 # amplitudes consistent with outcome
> post = np.array([bell[i] if i in keep else 0 for i in range(4)], dtype=complex)
> post /= np.linalg.norm(post)
> print("outcome:", outcome, " qubit 1 state:", np.round(post, 3))
> ```
> Whichever outcome you get, qubit 1 is found in the *matching* computational state with certainty — your first look at entanglement's signature, ahead of Part V.

> [!research] Research frontier
> The quantum-classical boundary: where and how does an interaction become a measurement? Modern experiments push coherent superpositions to ever-larger objects and test collapse models (GRW, Diósi–Penrose) that predict tiny deviations from unitary quantum mechanics — so far, none observed. Practically adjacent open problems: near-quantum-limited readout for superconducting qubits, and real-time decoders that must extract syndrome information in under a microsecond without disturbing logical qubits (37.6) — measurement theory as a hard systems-engineering deadline.
