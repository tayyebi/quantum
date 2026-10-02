# Part III — Mathematical Foundations

Everything a quantum engineer needs from undergraduate mathematics, rebuilt for a programmer: complex numbers, linear algebra, tensor products, probability, and numerical computation — each with an implementation you can run today and a statement of where it breaks on real hardware.

## 3. Mathematical Language

> [!levels] Five levels of this chapter
> - **Intuition —** quantum states are vectors of complex numbers; all the "weirdness" is arithmetic on those vectors.
> - **Mathematics —** scalars, complex numbers, vector spaces, bases, and inner products: the vocabulary every later chapter assumes.
> - **Implementation —** every object here is a numpy array or a few lines of Python; you can verify each rule numerically.
> - **Engineering —** careless conventions (basis order, phase, normalization) cause silent bugs; the notation exists to prevent them.
> - **Research —** even the notation is still evolving: alternative formalisms (stabilizers, tensor networks) replace bras and kets at scale.

### 3.1 Notation

Mathematics in this book is written as a programmer would write it: every symbol denotes a concrete object with a type. Scalars (`float`, `complex`) are lowercase Greek letters α, β, θ; vectors are lowercase Latin letters with arrows or kets, u, |ψ⟩; matrices are uppercase letters, U, H. The ket |ψ⟩ is a column vector of complex amplitudes; ⟨ψ| is its conjugate-transposed row vector. Throughout the book, one symbol means one thing per context, and cross-references like (37.6) point to where an idea returns. The fastest way to read quantum papers is to translate every expression into "what numpy object is this?" — a ket is a shape-(2ⁿ,) array, a gate is a shape-(2ⁿ, 2ⁿ) array, and a density matrix is a shape-(2ⁿ, 2ⁿ) Hermitian array. Notation is an API; learn its signature once and stop re-deriving it.

### 3.2 Scalars

A scalar is a single number — the simplest mathematical object, and in quantum computing never quite as simple as `float`. Amplitudes are complex; probabilities are real and nonnegative; angles are real, usually in radians; counts of qubits and shots are integers. Each has different arithmetic rules and different failure modes, so the engineer's habit is to ask "scalar of what type?" before multiplying. Probabilities must sum to 1 (over all outcomes); amplitudes must instead satisfy a normalization constraint on the whole state vector. In code, keep probability-like quantities in floating point but track exact integers (shots, qubits) as Python ints. Watch out for the classic numerical trap: probabilities computed as |amplitude|² are always nonnegative in exact arithmetic, but floating-point rounding can produce values like −1e−17 that downstream code (a `np.random.choice` call, for instance) will reject.

### 3.3 Real numbers

Real numbers ℝ form a continuum: between any two, infinitely many others. Physically measurable quantities — probabilities, energies, times — are real. But computers store only a finite subset: IEEE 754 floating-point numbers, roughly 2⁶⁴ distinct values per `double`. The gap between the mathematical continuum and the stored subset is where much numerical trouble lives (7.1). Two habits to build now. First, never test floating-point results for exact equality; compare with a tolerance like `abs(a - b) < 1e-12`. Second, remember that "real" claims in physics — a probability is nonnegative, a Hamiltonian is Hermitian — are exactly the properties your numerics should preserve or verify, not assume. In quantum computing, measurement outcomes are real numbers, but the machinery producing them runs on complex arithmetic; the real numbers are the interface, the complex ones the engine.

### 3.4 Complex numbers

A complex number z = a + bi has a real part a and imaginary part b, with i² = −1. In Python this is a native type: `complex(3, 4)`, with `.real`, `.imag`, and `abs(z)` built in. Complex numbers add componentwise and multiply by the distributive rule; division is defined by multiplying by the conjugate. Geometrically, multiplication rotates and scales — this single fact explains why quantum amplitudes are complex: phases must be able to rotate continuously so that amplitudes can cancel (interference). Real amplitudes could only reinforce or attenuate, never cancel completely. Every amplitude in this book is a complex number; every probability is |z|², real by construction. There is nothing mystical here — numpy handles complex128 natively, and you will manipulate thousands of them per simulation without ever seeing i "in nature".

```python
import numpy as np
z1, z2 = 1 + 2j, 3 - 1j
print(z1 * z2)                      # (5+5j): multiply like polynomials in i
print(np.abs(z1), np.angle(z1))     # magnitude sqrt(5), phase atan2(2,1)
```

### 3.5 Complex conjugation

The conjugate of z = a + bi is z* = a − bi: flip the sign of the imaginary part, reflect across the real axis. Conjugation is the bridge between complex amplitudes and real probabilities: |z|² = z·z* = a² + b². In numpy, `np.conj(z)` or `z.conj()`. Three rules you will use constantly: the conjugate of a product is the product of conjugates, (zw)* = z*w*; the conjugate of a sum is the sum of conjugates; and a number equals its own conjugate exactly when it is real. Conjugation appears in quantum computing in two load-bearing places: the bra ⟨ψ| is the conjugate transpose of the ket |ψ⟩, and Hermitian matrices (4.9) — the quantum analogue of real symmetric matrices, used for observables and Hamiltonians — are defined by the condition H = H†, where † means conjugate transpose. Forgetting to conjugate is among the most common simulation bugs.

### 3.6 Magnitude and phase

Every nonzero complex number has a magnitude r = |z| = √(a² + b²) and a phase θ = atan2(b, a), the angle counterclockwise from the positive real axis. Magnitude is "how much", phase is "in which rotational direction". Quantum mechanics cares about this split precisely: the Born rule depends only on magnitudes (probability = |amplitude|²), yet interference depends entirely on relative phases — two amplitudes of equal magnitude can reinforce (phase difference 0) or cancel completely (phase difference π). This is why a global phase — multiplying the whole state by e^{iφ} — is unobservable, while relative phases between basis components are the actual payload of gates like S and T. In code, `np.abs` and `np.angle` extract the two parts; phases wrap at ±π, so compare phases modulo 2π, never directly.

### 3.7 Euler's formula

Euler's formula, e^{iθ} = cos θ + i·sin θ, states that the exponential of an imaginary number travels the unit circle. It is the single most useful identity in this book because it unifies the two previous sections: e^{iθ} has magnitude exactly 1 and phase exactly θ, so any complex number factors as z = r·e^{iθ} — a scaling times a rotation. Consequences used throughout: multiplying by e^{iθ} rotates a vector's phase without changing its length (this is what phase gates do physically); cos θ and sin θ are the even and odd parts of e^{iθ}; and e^{iπ} = −1, the famous identity, is just the point antipodal on the circle. When you later see U = e^{iHt} (time evolution under a Hamiltonian, 4.20), read it as "rotate phase continuously at a rate set by H". Euler's formula is the dictionary between algebra and geometry.

### 3.8 Polar representation

Combining magnitude and phase: z = r·e^{iθ}, with r ≥ 0 the radius and θ the angle. This is the complex plane's polar coordinates, and it is the natural representation for amplitudes because quantum operations act on the two parts separately — unitary gates preserve r (norm) and manipulate θ (phase). numpy exposes the round trip directly. Practical warnings from engineering: the phase θ is only defined modulo 2π, so "the" phase of an amplitude is a representative, not a unique value; `np.angle(0)` is undefined, matching the physical fact that a zero amplitude carries no phase; and accumulating many rotations numerically can let the magnitude drift off 1, which is why simulators re-normalize states periodically. When debugging a circuit, print amplitudes in polar form — a phase pattern is far more readable than raw real-and-imaginary pairs.

### 3.9 Vectors

A vector is an ordered list of numbers that can be added together and scaled: u + v adds componentwise; c·u scales every component. Geometrically an arrow; computationally a 1-D numpy array. In quantum computing, a state of n qubits is a vector of 2ⁿ complex amplitudes, so "the state" and "the vector" are the same object throughout this book. The operations that matter are few: linear combination (3.13), inner product (3.16), and matrix multiplication (4.4). Python gives you all three with numpy. Build the habit now of checking shapes before every operation — `psi.shape` should be `(2**n,)` for a state vector, and most "quantum" bugs are ordinary shape bugs underneath. A vector is normalized when the sum of squared magnitudes of its components equals 1; simulators must maintain this invariant explicitly, since floating-point drift erodes it slowly.

### 3.10 Vector spaces

A vector space is a set of vectors closed under addition and scalar multiplication: sums and scaled versions of members stay inside. This closure is what makes the abstraction useful — you can do algebra without leaving the space. The complex vector space ℂⁿ is n-tuples of complex numbers; a single qubit's states live in ℂ², two qubits in ℂ⁴ (via tensor products, chapter 5), and n qubits in ℂ^{2ⁿ}. Two subspaces matter constantly in quantum computing: the set of valid states (normalized vectors, the unit sphere) and the set spanned by a code's logical states in error correction (chapter 37). Note what "space" buys you: dimension (3.15) tells you the degrees of freedom, a basis (3.11) tells you the coordinate system, and the whole geometric vocabulary — lengths, angles, projections — transfers from ℝ² to ℂ^{2ⁿ} unchanged.

### 3.11 Bases

A basis is a minimal set of vectors from which every other vector in the space can be built as a linear combination. The standard basis of ℂ² is |0⟩ = (1, 0) and |1⟩ = (0, 1); any qubit state is α|0⟩ + β|1⟩. Bases are choices, not facts: the same state vector has different coordinates in different bases, and changing basis (4.14) is a central operation — the Hadamard gate is exactly a change of basis between the computational basis and the ± basis. In quantum computing, "measuring in a basis" means choosing which decomposition the measurement reads out, and algorithms work largely by choosing bases strategically. Rule to internalize: the vector is the reality; the basis is the description. Two engineers describing the same qubit in different bases are not disagreeing — they are printing the same array against different axes.

### 3.12 Coordinates

Given a basis, any vector v equals a unique linear combination c₁b₁ + c₂b₂ + … + cₙbₙ, and the coefficients (c₁, …, cₙ) are v's coordinates in that basis — the actual array you store and compute with. This is the deepest "just an array" statement in the chapter: `psi` in numpy is nothing but the coordinate list of an abstract vector in the computational basis. Coordinates are basis-dependent — the same qubit |+⟩ has coordinates (1/√2, 1/√2) in the computational basis and (1, 0) in the ± basis. Every time you extract coefficients with an inner product ⟨bᵢ|v⟩ (3.16), you are doing exactly what `np.vdot(basis_vector, psi)` does. The engineering discipline: every state array in your code should have a documented basis. Undocumented basis assumptions are the coordinate-system bugs of quantum software — silent, and found only when statistics come out wrong.

### 3.13 Linear combinations

A linear combination of vectors v₁, …, vₖ is c₁v₁ + … + cₖvₖ for scalar coefficients cᵢ. This is the only way quantum states are ever built from other states, so it is worth internalizing beyond the formula. A superposition (1.2) is a linear combination with complex coefficients, where |cᵢ|² is the probability of outcome i at measurement. The set of all linear combinations of some vectors is their span — a subspace — and "the state space is spanned by the computational basis" is the sentence every quantum operation ultimately manipulates. In numpy, one line: `c1*v1 + c2*v2`. For states, coefficients satisfy Σ|cᵢ|² = 1; gates update them all simultaneously by matrix multiplication. Everything visual — Bloch spheres, interference patterns, circuit diagrams — is a picture of coefficients moving under linear combinations.

### 3.14 Linear independence

Vectors are linearly independent when no one of them can be written as a linear combination of the others — equivalently, c₁v₁ + … + cₖvₖ = 0 forces all cᵢ = 0. Independence is the precise meaning of a basis being "minimal": a basis for an n-dimensional space is exactly a set of n independent vectors that spans it. Why an engineer cares: independent states carry independent information; redundant (dependent) states do not. In error correction, the logical codewords of a code must be linearly independent or the code cannot distinguish them. In machine learning on quantum data, a feature set of states that is linearly dependent has fewer degrees of freedom than it appears. Test numerically by checking that the matrix with the vectors as columns has full rank: `np.linalg.matrix_rank(A) == k`. Rank is the workhorse answer to "how many genuinely independent things do I have?"

### 3.15 Dimension

The dimension of a vector space is the number of vectors in any basis — a fixed property of the space, independent of which basis you pick. This count is the book's central exponential: one qubit lives in dimension 2, n qubits in dimension 2ⁿ (chapter 5), and every classical simulation of a quantum computer pays memory and time proportional to that dimension. Dimension counting is also a design tool. A single qubit's normalized state has dimension 2 but only 2 real degrees of freedom after normalization and global-phase removal (the Bloch sphere is 2-dimensional — a sphere's surface). Two qubits: dimension 4. Three hundred: dimension 2³⁰⁰, more than atoms in the observable universe — the sentence that explains why classical simulation (7.12) fails and why quantum hardware might matter. When you meet any new quantum object, the first question is always: what is its dimension?

### 3.16 Inner products

The inner product generalizes the dot product to complex vectors: for u and v it is ⟨u|v⟩ = Σᵢ uᵢ*·vᵢ — note the conjugate on the first vector, which makes ⟨v|v⟩ = Σ|vᵢ|² a nonnegative real number. This single number is the most-used operation in quantum computing: ⟨ψ|ψ⟩ tests normalization; ⟨φ|ψ⟩ is the amplitude of finding ψ's measurement outcome in φ's direction, and |⟨φ|ψ⟩|² is that outcome's probability; ⟨φ|ψ⟩ = 0 (orthogonality, 3.18) means perfectly distinguishable states. In numpy, `np.vdot(u, v)` implements the conjugating convention correctly — plain `u @ v` does not conjugate, a classic bug. Geometrically the inner product measures alignment: how much of v lies along u. Every fidelity computation, every overlap check, every Born-rule probability in this book is an inner product wearing different notation.

```python
import numpy as np
psi = np.array([1, 1j]) / np.sqrt(2)
phi = np.array([1, -1j]) / np.sqrt(2)
print(np.vdot(psi, psi))   # (1+0j): normalized
print(np.vdot(psi, phi))   # (0+1j): orthogonal, |overlap|^2 = 0
```

### 3.17 Norms

A norm measures a vector's length: ‖v‖ = √⟨v|v⟩ for the standard (Euclidean, or L2) norm — the square root of the sum of squared magnitudes. Norms obey the triangle inequality (‖u + v‖ ≤ ‖u‖ + ‖v‖) and scale linearly (‖c·v‖ = |c|·‖v‖). The state-normalization condition of quantum mechanics is exactly ‖ψ‖ = 1, so the entire state space is the unit sphere of ℂ^{2ⁿ}. Other norms appear in engineering contexts: the L1 norm (sum of absolute values) bounds total variation, and matrix norms (operator norm, Frobenius norm) measure gate errors — "this pulse implements U with error ≤ ε" means ‖U_actual − U_target‖ ≤ ε for a specific norm the paper must name. In code: `np.linalg.norm(psi)` for states, `np.linalg.norm(A, 2)` for the operator norm. Whenever a fidelity or error is quoted without a norm, the number is undefined.

### 3.18 Orthogonality

Vectors u and v are orthogonal when ⟨u|v⟩ = 0 — geometrically perpendicular, probabilistically decisive. In quantum mechanics, orthogonality is the mathematical form of distinguishability: two orthogonal states can be told apart by a measurement with certainty (⟨0|1⟩ = 0), while non-orthogonal states cannot, ever, by any measurement — the no-cloning theorem and quantum cryptography both rest on this. The computational basis states are mutually orthogonal, which is why they are classical, reliably readable outcomes; superposed states lean between them. Orthogonality also defines independence of measurement outcomes and underlies projection: the projector |φ⟩⟨φ| extracts the component of a state along φ, and annihilates everything orthogonal to it. Quick numerical check: `abs(np.vdot(u, v)) < 1e-12`. When an algorithm needs outcomes to be reliably separable, it is arranging orthogonality.

### 3.19 Orthonormal bases

An orthonormal basis is a basis whose vectors are mutually orthogonal and individually unit-length: ⟨bᵢ|bⱼ⟩ = δᵢⱼ (1 if i = j, else 0). The computational basis |0⟩, |1⟩, …, |2ⁿ−1⟩ is orthonormal, and orthonormality makes the formulas of this chapter collapse to their simplest forms: coordinates are just inner products, cᵢ = ⟨bᵢ|ψ⟩; norms are the sum of squared coordinates; and unitary matrices (4.10) are exactly the transformations that carry one orthonormal basis to another. This is why quantum formalism is written in orthonormal bases by default — every measurement in a basis, every gate, every code's logical states assumes it. Practical note: numerically, orthonormality drifts. Simulators periodically re-orthonormalize (e.g. via QR decomposition, `np.linalg.qr`) or re-normalize, because roundoff slowly rotates basis vectors off exact orthogonality.

### 3.20 Bra-ket notation

Dirac's bra-ket notation packages everything above into quantum computing's native syntax. A ket |ψ⟩ is a column vector; a bra ⟨φ| is the conjugate-transposed row vector; juxtaposition ⟨φ|ψ⟩ is the inner product, ⟨φ|ψ⟩ = Σᵢ φᵢ*·ψᵢ. The outer product |φ⟩⟨ψ| is a matrix — the projector |φ⟩⟨φ| being the special case that extracts the component along φ. The notation is deliberately self-documenting: ⟨bᵢ|ψ⟩ reads as "the i-th coordinate of ψ", and Σᵢ |bᵢ⟩⟨bᵢ| = I reads as "the basis tiles the identity". You can translate mechanically to numpy: ket → 1-D array, bra → `np.conj`, inner product → `np.vdot`, outer product → `np.outer(conj(b), a)`. Once bra-ket becomes "rows and columns with conjugation where the bar is", quantum papers stop being notation-heavy and start being readable.

> [!experiment] On your laptop — verify the vocabulary
> Every rule in this chapter is checkable in a few lines. Confirm inner products, orthogonality, and normalization numerically.
>
> ```python
> import numpy as np
>
> # two states and a measurement basis vector
> psi = np.array([3, 4j], dtype=complex); psi /= np.linalg.norm(psi)
> b0, b1 = np.eye(2, dtype=complex)          # computational basis
>
> print("norm:", np.linalg.norm(psi))                 # ~1.0
> print("<b0|b1>:", np.vdot(b0, b1))                  # 0: orthogonal
> p = abs(np.vdot(b0, psi))**2                        # Born rule
> shots = np.random.choice(2, size=100_000, p=[p, 1-p])
> print("predicted:", p, "measured:", np.mean(shots == 0))
> ```
>
> Change psi, rerun, and confirm the statistics follow |⟨b₀|ψ⟩|² every time. This loop — predict with linear algebra, check with sampling — is the working method of the whole book.

> [!research] Research frontier
> The linear-algebra language of this chapter is universal, but it is not the only useful one, and choosing a formalism is an active engineering decision. Stabilizer formalism (chapter 36) replaces 2ⁿ-dimensional vectors with a compact group description, simulating certain circuits in polynomial time; tensor networks (5.14) trade the full state vector for a network of small tensors, and simulators based on them now contest "supremacy" claims at 50+ qubits. Open question: for which circuit families does a compressed representation beat the raw state vector — and can that be decided before running? This is classical-simulation research you can do from a laptop.

---

## 4. Matrices

> [!levels] Five levels of this chapter
> - **Intuition —** a matrix is a machine that takes a vector in and hands a vector out; in quantum computing it is a gate or an evolution.
> - **Mathematics —** matrix algebra, the conjugate transpose, and the unitary and Hermitian conditions that define quantum operations and observables.
> - **Implementation —** numpy expresses every gate as a small array; multiplication, diagonalization, and the matrix exponential are library calls.
> - **Engineering —** unitarity drift, conditioning, and eigensolver cost are where simulations lie to you if unchecked.
> - **Research —** matrix functions of large sparse Hamiltonians, and simulating e^{iHt} at scale, remain active numerical-analysis problems.

### 4.1 Matrix representation

A matrix is a rectangular array of numbers with defined operations; a size-m×n matrix has m rows and n columns and maps n-dimensional vectors to m-dimensional ones. In this book matrices are almost always square (n×n) and complex: a gate acting on n qubits is a 2ⁿ×2ⁿ matrix. Element A[i, j] sits at row i, column j — row first, always, in math and in numpy. The matrix is not the operation, it is the operation's representation in a chosen basis; change basis and the same operation gets new entries (4.14). This mirrors software exactly: an interface and its implementation in a given coordinate system. Keep in mind the scale cliff from chapter 3: a two-qubit gate is 4×4 (trivial), a ten-qubit gate is 1024×1024 (16 MB), a thirty-qubit gate is unrepresentable. Matrices are the interface; size is the enemy.

### 4.2 Matrix addition

Matrices of identical shape add elementwise: (A + B)[i, j] = A[i, j] + B[i, j], with the familiar laws — commutative, associative, scalar-distributive, and A + 0 = A. In numpy, `A + B` and `3*A` just work, provided shapes match; mismatched shapes raise errors rather than guessing. Alone, addition is nearly trivial in quantum computing: adding two candidate gate matrices rarely means anything physical. It earns its keep in constructions — Hamiltonians are built as sums of simpler terms (H = H₁ + H₂ + …, each a tensor product, chapter 5), and projector decompositions write an observable as a weighted sum of projectors. The engineering takeaway is small but real: because Hamiltonians are sums of terms, you can often apply each term separately (Lie–Trotter splitting) instead of ever forming the full exponential — a trick the simulation chapters lean on hard.

### 4.3 Matrix multiplication

The product AB is defined when A's column count equals B's row count; entry (AB)[i, j] = Σₖ A[i, k]·B[k, j] — row i of A dotted with column j of B. Two properties separate this from ordinary arithmetic. First, it is generally not commutative: AB ≠ BA, and in quantum mechanics non-commutation is physical — measuring one observable then another is not the same in both orders (the commutator [A, B] = AB − BA quantifies it, and quantum error is largely the story of commuting versus non-commuting terms). Second, composition is the meaning: applying gate B then gate A to a state is the matrix product A·B, right-to-left like function composition — `A @ (B @ psi)`, or precomputed `A @ B`. The cost is cubic in dimension, O(n³) for n×n — the constant behind "simulation gets slow".

```python
import numpy as np
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
print(X @ Z)   # anticommuting: XZ = -ZX, the Pauli algebra
```

### 4.4 Matrix-vector multiplication

For square A and vector v, Av is the vector whose i-th component is Σⱼ A[i, j]·v[j] — each output component mixes all input components with weights from row i. This is the fundamental motion of quantum computing: a gate application is Av, updating all 2ⁿ amplitudes at once. In numpy, `A @ v` (note: `A * v` broadcasts elementwise and is a common, silent bug). Complexity: O(n²) multiply-adds for dense n×n, O(n²) memory for the matrix itself — for n = 2⁴⁰ qubit-dimension that is already impossible, which is why structured representations (sparse, tensor networks, stabilizers) exist. Two identities worth memorizing: (AB)v = A(Bv) (you can pre-compose gates), and ⟨u|A|v⟩ = ⟨u|(Av) — matrix-vector products and inner products interleave freely, which is how expectation values get computed.

### 4.5 Identity matrices

The identity matrix I has ones on the diagonal and zeros elsewhere: Iv = v for every v. It is the do-nothing operation, the 0 of multiplication, and it anchors every definition in this chapter: an inverse satisfies A·A⁻¹ = I; a unitary matrix satisfies U†U = I; a projector satisfies P² = P. In numpy, `np.eye(n)`. Identities appear in quantum computing in slightly surprising roles: adding a phase with a global factor e^{iφ}·I is physically unobservable (global phase); the decomposition Σᵢ |bᵢ⟩⟨bᵢ| = I (resolution of the identity in an orthonormal basis) is the workhorse step in derivations, letting you insert "a sum over all outcomes" anywhere; and identity on some qubits while others are acted on is the tensor-product construction I ⊗ U (5.11). Do-nothing, done formally, turns out to be a load-bearing object.

### 4.6 Inverse matrices

The inverse A⁻¹ is the matrix with A·A⁻¹ = A⁻¹·A = I; it exists exactly when A is square and full-rank (non-singular). numpy computes it with `np.linalg.inv`. But the engineering rule is blunt: almost never invert a matrix explicitly. Solving Ax = b as `np.linalg.solve(A, b)` (LU-based) is faster and numerically safer than computing A⁻¹ then multiplying — explicit inversion can cost an order of magnitude in accuracy for ill-conditioned systems. The deeper reason quantum computing sidesteps inverses: physical evolution is unitary, and unitary matrices are always invertible with U⁻¹ = U† — the conjugate transpose, computable without any factorization. So the general-matrix inverse machinery matters mostly in the classical numerics around your quantum code: fitting calibration models, solving linear systems in state tomography, regularizing least-squares. When you do need one, ask whether a solve would do instead.

### 4.7 Transpose

The transpose Aᵀ flips a matrix across its diagonal: (Aᵀ)[i, j] = A[j, i], turning rows into columns. Algebraic rules: (AB)ᵀ = BᵀAᵀ — order reverses, a pattern that repeats for every transpose-like operation and is worth drilling until automatic. In numpy, `A.T`. On its own, transpose is a minor player in quantum computing because the amplitudes are complex and conjugation-free transposition misses the essential operation; it appears mainly inside the definition of the conjugate transpose (4.8) and in real-valued classical computations where it costs nothing. One place to meet it early: symmetric real matrices (Aᵀ = A) are the classical cousins of Hermitian matrices, and every theorem you will later use about Hermitian operators — real eigenvalues, orthogonal eigenvectors — has this real-symmetric ancestor. Learn the complex version directly; the real one is the special case.

### 4.8 Conjugate transpose

The conjugate transpose (adjoint, dagger) A† = (Aᵀ)* transposes and conjugates every entry: (A†)[i, j] = A[j, i]*. In numpy, `A.conj().T` (order does not matter). This is quantum computing's central matrix operation. It defines the adjoint of a vector (the bra), the dagger of a gate (running the gate backwards — uncomputation, the inverse operation every algorithm needs), and the two classes that structure the whole field: unitary matrices (U†U = I, evolution, chapter 4's heart) and Hermitian matrices (H† = H, observables and Hamiltonians). The reversal rule carries over: (AB)† = B†A† — to undo a sequence of gates, undo them in reverse order, exactly like unwinding a call stack. In code, whenever you need "the reverse operation", the answer is almost always `.conj().T` rather than a numerical inverse.

### 4.9 Hermitian matrices

A matrix H is Hermitian when H† = H — each entry equals the conjugate of its mirror image; diagonal entries must be real. Hermitian matrices are quantum mechanics' real numbers: every observable (energy, spin, parity) is represented by one, because two theorems guarantee physical sanity. First, all eigenvalues are real — measurement outcomes cannot be complex. Second, eigenvectors of distinct eigenvalues are orthogonal — outcomes correspond to distinguishable alternatives. numpy's `np.linalg.eigvalsh` exploits Hermitian structure, running faster and more stably than the general `eig`. Two facts the engineer uses weekly: any Hermitian H decomposes as a weighted sum of projectors H = Σ λᵢ Pᵢ (the spectral theorem, 4.18), which is precisely how measurement statistics are computed; and Pauli matrices are the minimal Hermitian alphabet — any 2ⁿ-sized Hermitian is a sum of Pauli tensor products (5.11), the format chemistry Hamiltonians ship in.

### 4.10 Unitary matrices

A matrix U is unitary when U†U = I: it preserves inner products, hence lengths, hence probabilities. Unitarity is quantum mechanics' conservation law — time evolution cannot amplify or discard probability, and because U† = U⁻¹, every quantum operation is freely reversible. The columns (equivalently rows) of a unitary form an orthonormal basis (3.19): unitaries are exactly the transformations mapping one orthonormal basis to another. For the engineer, three consequences dominate. Validation: `np.allclose(U.conj().T @ U, np.eye(n))` is the unit test for any gate you construct — run it always. Composition: products and tensor products of unitaries are unitary, so circuits stay valid by construction. Numerics: a simulator that applies only unitaries should keep ‖ψ‖ = 1 forever; if the norm drifts, you have a bug or you have left unitary ground (open systems, noise channels — chapter 33).

### 4.11 Normal matrices

A matrix is normal when A†A = AA† — it commutes with its own adjoint. The class includes all unitary and all Hermitian matrices, plus others (skew-Hermitian, diagonal-with-complex-entries). Its importance is one theorem: a matrix is normal exactly when it is unitarily diagonalizable — there is an orthonormal eigenbasis, A = V·D·V† with V unitary and D diagonal. This is why quantum mechanics can be handled with the clean spectral machinery everywhere: observables (Hermitian) and evolution (unitary) are both normal, both diagonalizable in orthonormal bases, both expressible as "eigen-directions with eigen-values". Non-normal matrices exist in classical numerics (they can be violently transient — growing enormously before decaying) but essentially never as closed-system quantum evolution. The practical check `np.allclose(A.conj().T @ A, A @ A.conj().T)` tells you whether the cheap, stable eigensolvers apply to your matrix.

### 4.12 Projectors

A projector P satisfies P² = P: applying it twice changes nothing — it projects. The elementary projectors are the rank-1 outer products P = |φ⟩⟨φ| for a unit vector φ, which extract the component of a state along φ and zero out the rest. Hermitian by construction, they are the atoms of quantum measurement: a measurement with outcomes i and associated projectors Pᵢ satisfying Σ Pᵢ = I produces outcome i with probability ⟨ψ|Pᵢ|ψ⟩ and leaves the state Pᵢ|ψ⟩/√(that probability). This is the Born rule in operational form, and it covers computational-basis measurement (P₀ = |0⟩⟨0|, P₁ = |1⟩⟨1|), partial measurement of some qubits (tensor the local projectors with I, 5.12), and observables via the spectral decomposition. In numpy, `P = np.outer(phi, phi.conj())`. Post-selection — keeping only shots with a chosen outcome — is exactly applying a projector statistically.

### 4.13 Diagonal matrices

A diagonal matrix has nonzeros only on its diagonal: (Dv)[i] = dᵢ·v[i] — each component scaled independently, no mixing. This is the easiest matrix class to compute with: multiplication is O(n) not O(n³), powers are just powers of the entries, functions apply entrywise (4.19), and exponentials are `np.exp(d)` on the diagonal. Diagonal matrices are also the quantum operations you can actually afford at scale: phase gates, T and S, are diagonal; and any operator is diagonal in its own eigenbasis. The whole strategy of "diagonalize, then act" — change basis to the eigenbasis, scale entrywise, change back — works because conjugation preserves the class structure: V·D·V†. Know also the size trap: a diagonal matrix is still an object of its dimension; at 2ⁿ scale, store it as a length-2ⁿ vector of diagonal entries, never as a full array. Sparse-aware code (7.5) enforces this automatically.

### 4.14 Change of basis

If B is the matrix whose columns are a new orthonormal basis, the coordinates of a vector transform as v_new = B†·v, and operators transform as A_new = B†·A·B — a conjugation. For unitary B this is exact, stable, and reversible: the same vector, same operator, different coordinate description. This single operation explains several quantum-computing staples. The Hadamard gate is the change of basis between the computational basis and the ± basis — apply it, and "amplitudes" become "which-basis-amplitudes". The quantum Fourier transform (chapter 24) is a change of basis into the frequency domain, which is why period-finding sits at the heart of Shor's algorithm. Eigenbasis representation (4.17) is a change of basis that makes operators diagonal. In code: `A_new = B.conj().T @ A @ B`, with B unitary — verified, as always, by the unitarity check of 4.10.

### 4.15 Eigenvalues

An eigenvalue of A is a scalar λ with a nonzero vector satisfying Av = λv — the transformation stretches that special direction by λ without rotating it. Eigenvalues answer the questions engineers actually ask: what are the possible measurement outcomes (eigenvalues of the observable), at what rates does a system evolve (eigenvalues of the Hamiltonian become phases e^{iλt}), and is this circuit's behavior diagonalizable at all. For Hermitian and unitary matrices — the quantum classes — eigenvalues are real, or unit-magnitude complex respectively: outcomes are real numbers, evolution is pure phase. numpy exposes them via `np.linalg.eigvalsh` (Hermitian, preferred) and `np.linalg.eig` (general). The characteristic polynomial det(A − λI) = 0 defines them theoretically, but is numerically useless; production code finds eigenvalues iteratively (7.6). When a chapter later says "the energy levels are the eigenvalues", that sentence is the whole of spectroscopy.

### 4.16 Eigenvectors

Eigenvectors are the directions attached to eigenvalues: the nonzero solutions v of Av = λv, defined only up to scale (and, in quantum computing, fixed by normalization and an arbitrary phase). For a normal matrix, eigenvectors of distinct eigenvalues are orthogonal, so the full set forms an orthonormal eigenbasis — the coordinate system in which the operator becomes diagonal. Physically, eigenvectors are the states that are invariant under the operation: energy eigenstates accumulate only phase under time evolution, and measurement eigenstates are the definite outcomes. Numerically, `np.linalg.eigh` returns them orthonormalized for Hermitian input. Two habits: degenerate eigenvalues (multiplicity > 1) leave a subspace of valid eigenvectors, any orthonormal basis of which is equally correct — do not compare eigenvectors between runs, compare subspaces; and always check A @ v ≈ λ·v after solving. Eigen-decompositions you have not verified are guesses with formatting.

### 4.17 Eigendecomposition

Eigendecomposition writes a normal matrix as A = V·D·V†: V's columns are the orthonormal eigenvectors, D is diagonal with the eigenvalues. This is the master representation of the chapter because it makes every hard operation easy. Powers: Aᵏ = V·Dᵏ·V†. Exponentials: e^{A} = V·e^{D}·V†, the entrywise exponential of a diagonal matrix — which is exactly how quantum time evolution U(t) = e^{−iHt} is computed for a Hermitian Hamiltonian H, since eigenvalues of H become phases e^{−iλt}. Measurement: the spectral decomposition (4.18) of any observable. In numpy: `w, V = np.linalg.eigh(H)` (Hermitian) gives you both pieces; reconstruction `V @ np.diag(w) @ V.conj().T` should reproduce H to roundoff. Cost is O(n³) time and O(n²) memory — fine to a few thousand dimensions, impossible at 2ⁿ for n beyond ~15, which is precisely where chapter 7's iterative methods take over.

```python
import numpy as np
H = np.array([[1, 1j], [-1j, 1]], dtype=complex)   # Hermitian
w, V = np.linalg.eigh(H)                            # eigenvalues, eigenvectors
t = 0.7
U = V @ np.diag(np.exp(-1j * w * t)) @ V.conj().T   # U(t) = exp(-i H t)
print(np.allclose(U.conj().T @ U, np.eye(2)))       # True: evolution is unitary
```

### 4.18 Spectral decomposition

For any normal A, the spectral decomposition is A = Σᵢ λᵢ·Pᵢ: a weighted sum of projectors Pᵢ onto the eigenspaces — orthogonal, summing to identity. This is the bridge between chapter 3's linear algebra and quantum measurement, and it deserves to be read as an interface specification. Observable H = Σ λᵢ·Pᵢ means: possible outcomes are the λᵢ; probability of outcome i is ⟨ψ|Pᵢ|ψ⟩; post-measurement state is Pᵢ|ψ⟩ normalized. One formula, all of measurement. Functions likewise act spectrally: f(A) = Σ f(λᵢ)·Pᵢ for any scalar function f, which is how you apply a function to an operator without forming matrices (4.19). Degenerate eigenvalues merge into higher-rank projectors — the formula survives unchanged. Numerically, build Pᵢ from eigh's output by grouping eigenvectors with equal eigenvalues; then ⟨ψ|Pᵢ|ψ⟩ is just a couple of inner products — measurement statistics at O(n²) instead of O(n³).

### 4.19 Matrix functions

A matrix function f(A) extends a scalar function to matrices. For diagonalizable A = V·D·V†, the definition is f(A) = V·f(D)·V† — apply f to each eigenvalue. This is not a curiosity: the objects of quantum dynamics are all matrix functions. The time-evolution operator U(t) = e^{−iHt} is the exponential function of the Hamiltonian; e^{A} = Σ Aᵏ/k! converges for every matrix but is numerically treacherous as a naive series — production code uses Padé approximants with scaling-and-squaring (`scipy.linalg.expm`), or, for Hermitian H with known spectrum, the eigendecomposition route of 4.17. Square roots √A (of positive-definite matrices) appear in fidelity computations; logarithms appear in entropy and in decomposing unitaries into Hamiltonians (U = e^{iH}). The engineering rule: know which route your library takes, because ill-conditioned eigenvalues make one route accurate and another garbage.

### 4.20 Exponentials of matrices

The matrix exponential deserves its own section because e^{A} is the single most consequential matrix function in this book: Schrödinger evolution U(t) = e^{−iHt}, thermal states e^{−H/kT}, and continuous-time quantum walks are all matrix exponentials. Properties: e^{A} is always invertible with inverse e^{−A}; if H is Hermitian, e^{−iHt} is unitary — conservation of probability falls out of the algebra. The product formula e^{A+B} = e^{A}e^{B} holds only when A and B commute; when they do not, the discrepancy — captured by the Baker–Campbell–Hausdorff commutator series — is exactly the Trotter error that quantum simulation algorithms (chapter 30) must bound. Numerically: `scipy.linalg.expm` for small dense matrices; eigendecomposition when H is Hermitian and its spectrum is cheap; Krylov methods (7.6) for large sparse H. Every quantum simulation, on hardware or on your laptop, is an exercise in computing this object efficiently.

> [!experiment] On your laptop — diagonalize a Hamiltonian
> Build a small Hermitian matrix (a 3-site quantum walk), diagonalize it, and evolve. This five-line pattern computes the dynamics of any closed quantum system.
>
> ```python
> import numpy as np
>
> n = 3
> H = np.diag(np.ones(n-1), 1) + np.diag(np.ones(n-1), -1)  # hopping
> w, V = np.linalg.eigh(H)              # spectrum and eigenbasis
> psi0 = np.eye(n)[:, 0]                # start at site 0
> for t in (0.5, 1.0, 2.0):
>     U = V @ np.diag(np.exp(-1j*w*t)) @ V.conj().T
>     p = np.abs(U @ psi0)**2
>     print(f"t={t}: probs {np.round(p, 3)}, unitary={np.allclose(U.conj().T@U, np.eye(n))}")
> ```
>
> The probability mass spreads and interferes — the same computation chemists run for molecules, at a size where you can print every number.

> [!research] Research frontier
> Computing e^{−iHt} for large sparse Hamiltonians is a live numerical-analysis problem, not settled technology: Krylov and Lanczos methods, tensor-network time evolution (TEBD), and quantum signal processing all compete, with no single winner across regimes. On the quantum side, the central question of the simulation era — how short a circuit suffices to implement e^{−iHt} on fault-tolerant hardware — is bounded by Trotter error analysis (chapter 30) and improved by qubitization, and sharper bounds remain an open, publishable target. If you like numerical analysis more than physics, this is the rare frontier where classical and quantum research are literally the same problem.

---

## 5. Tensor Products

> [!levels] Five levels of this chapter
> - **Intuition —** combining two systems multiplies their possibility spaces; the tensor product is the arithmetic of "and" for quantum states.
> - **Mathematics —** Kronecker products, composite dimensions 2^{n+m}, separable versus entangled states, and partial traces.
> - **Implementation —** np.kron builds every multi-qubit object; one line, exponential cost.
> - **Engineering —** basis-ordering conventions and operator placement (which factor gets the gate) are the top source of silent multi-qubit bugs.
> - **Research —** entanglement structure is where tensor networks live; compressing states that Kronecker products cannot store is the open frontier.

### 5.1 Why ordinary vectors aren't enough

One qubit is a vector in ℂ². But two qubits are not a vector in ℂ² "somehow doubled" — they need four amplitudes (00, 01, 10, 11), three need eight, and n need 2ⁿ. No ordinary vector operation on the individual state vectors produces this: adding or concatenating would give 2 or 4 components, not 2². The mathematics needs one new operation whose dimension count multiplies, because physical composition multiplies outcomes: two coins have four joint outcomes, not two. The tensor product is that operation. Everything counterintuitive about quantum scale follows from it — the exponential state space, entanglement, and the impossibility of classical simulation (7.12) — and everything practical about multi-qubit software depends on getting its conventions right. This chapter is the point where the book's subject becomes genuinely many-body; read it slowly and run every snippet.

### 5.2 Composite systems

When two physical systems are considered jointly, the joint state space is the tensor product of the individual spaces: ℂ² ⊗ ℂ² ≅ ℂ⁴, and in general dim(A ⊗ B) = dim(A)·dim(B). The rule encodes a physical principle: joint outcomes are pairs (a, b), and there are dim(A)·dim(B) such pairs. For qubits: n qubits live in (ℂ²)^{⊗n} = ℂ^{2ⁿ} — the exponential that defines the field. Crucially, the composite space contains strictly more than the pairs of individual states: most vectors in ℂ⁴ are not expressible as (single state of qubit 1) ⊗ (single state of qubit 2). Those extra, un-factorizable vectors are entangled states (5.8) — correlations with no classical counterpart, the resource behind teleportation, superdense coding, and error-correcting codes. Composition is multiplication in dimensions and something genuinely new in content.

### 5.3 Tensor-product notation

The tensor product of vectors is written |a⟩ ⊗ |b⟩, usually abbreviated |a⟩|b⟩ or |ab⟩: for |a⟩ = (a₀, a₁) and |b⟩ = (b₀, b₁), the product is the four-component vector (a₀b₀, a₀b₁, a₁b₀, a₁b₁). The rule generalizes componentwise: every component of the first multiplies every component of the second. Properties that matter: the tensor product is bilinear — scalars pull out, and (a₁ + a₂) ⊗ b = a₁ ⊗ b + a₂ ⊗ b — but not commutative; |a⟩ ⊗ |b⟩ and |b⟩ ⊗ |a⟩ live in differently-labeled spaces (qubit 1 versus qubit 2), and conflating them is a bug. For basis states the notation doubles as labels: |0⟩ ⊗ |1⟩ = |01⟩, the two-qubit basis state reading "first qubit 0, second qubit 1". From here on, n-qubit states are written |b₁b₂…bₙ⟩ with each bᵢ a bit.

### 5.4 Kronecker products

The Kronecker product is the tensor product's implementation for matrices: A ⊗ B is the block matrix with block (i, j) equal to aᵢⱼ·B — every entry of A scaled into a copy of B. numpy ships it as `np.kron(A, B)`. The algebra you need: (A ⊗ B)(C ⊗ D) = (AC) ⊗ (BD) — mixed products combine pairwise, the identity that lets circuits of local gates be compiled into one big matrix; (A ⊗ B)† = A† ⊗ B†; and (A ⊗ B)(v ⊗ w) = (Av) ⊗ (Bw). Dimensions multiply: (m×n) ⊗ (p×q) is (mp×nq). One sharp edge: Kronecker is not commutative — `np.kron(A, B)` and `np.kron(B, A)` are different matrices related by a permutation of basis order (5.10). Every multi-qubit simulator you will ever read is, underneath, a disciplined bookkeeping system for np.kron calls.

```python
import numpy as np
I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
# CNOT from a classical truth table? No — but I⊗X is "X on qubit 2 only":
print(np.kron(I2, X))   # 4x4: applies X to the second qubit, leaves the first
```

### 5.5 Tensor-product dimensions

Dimensions multiply: (ℂ^{d₁}) ⊗ (ℂ^{d₂}) has dimension d₁·d₂, so n qubits give 2ⁿ amplitudes, n qutrits give 3ⁿ, and a hybrid system gives the product of its parts' dimensions. This multiplicative law is the engine of both the promise and the pain. Promise: 300 qubits span 2³⁰⁰ amplitudes — room to encode structures no classical memory can hold. Pain: every simulation object — state vector, gate, density matrix — scales with the product, so 30 qubits at 16 bytes per complex128 is 16 GB for one state vector and 2⁶⁰ entries for a dense operator (which is why even simulators avoid forming full multi-qubit operators, applying them factor-wise instead, 7.11). Dimension arithmetic is also a debugging tool: after building any composite object, assert its shape. `assert psi.shape == (2**n,)` catches the off-by-one-qubit errors that would otherwise surface as inexplicable statistics, much later.

### 5.6 Multi-qubit states

An n-qubit state is a unit vector in ℂ^{2ⁿ}: ψ = Σ_x c_x |x⟩, where x runs over all n-bit strings and Σ_x |c_x|² = 1. Each c_x is the amplitude of the classical bit pattern x; measuring in the computational basis yields pattern x with probability |c_x|². There is no separate "state of each qubit" in general — the joint vector is the full description, and individual-qubit descriptions exist only when the state is separable (5.7). Read concrete examples until they are reflexes: |00⟩ is the vector (1,0,0,0); (|00⟩ + |11⟩)/√2 has two nonzero amplitudes and is the Bell state, the canonical entangled pair; the state (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2 is two independent qubits each in |+⟩. The gap between four amplitudes and "two qubits each having a state" is exactly the content of the next two sections.

### 5.7 Separable states

A composite state is separable (a product state) when it can be written ψ = φ ⊗ ω — one vector for each subsystem. For such states, everything factors: probabilities of joint outcomes multiply, each subsystem has its own well-defined state vector, and the whole is no more than the parts. These are the quantum analogues of independent random variables, and they are what you get from preparing each qubit separately: `np.kron(psi1, psi2)`. Product states are also precisely the states classical simulation handles comfortably — memory for two n₁- and n₂-qubit factors is 2^{n₁} + 2^{n₂}, not 2^{n₁+n₂}. That observation is not a trick but a research program: represent states as networks of small factors wherever physics permits (5.14), and the exponential wall recedes as far as the correlations stay shallow. Sep-arability is therefore not a footnote — it is the boundary of the efficiently simulable world.

### 5.8 Non-separable states

An entangled state is a composite state that cannot be factored: ψ ≠ φ ⊗ ω for any choice of factors. The canonical case is the Bell state (|00⟩ + |11⟩)/√2: neither qubit has a state vector of its own, yet joint measurements are perfectly correlated — outcomes always agree, at distance, with no shared classical cause available in time. Entanglement is quantifiable (entropy of entanglement, negativity — chapter 34), generable by gates as ordinary as CNOT acting on |+0⟩, and consumed as a resource by teleportation, superdense coding, and error-correcting codes. For simulation, entanglement is the expense: Bell-type states across many qubits resist every compressed representation. The honest engineering summary: separability is cheap, entanglement is powerful, and the amount of entanglement your problem genuinely needs determines whether you can study it on a laptop or must queue for hardware.

```python
import numpy as np
plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
ket0 = np.array([1, 0], dtype=complex)
psi = np.kron(plus, ket0)              # |+0>: separable
M = psi.reshape(2, 2)                  # view as matrix
print("rank of coefficients:", np.linalg.matrix_rank(M))  # 1 => product state
bell = (np.kron(ket0, ket0) + np.kron(ket0, np.array([0, 1], dtype=complex))) / np.sqrt(2)
print("Bell rank:", np.linalg.matrix_rank(bell.reshape(2, 2)))  # 2 => entangled
```

### 5.9 Computational basis states

The computational basis of n qubits is the set {|x⟩ : x an n-bit string}, built by tensoring single-qubit basis states: |b₁b₂…bₙ⟩ = |b₁⟩ ⊗ |b₂⟩ ⊗ … ⊗ |bₙ⟩. There are 2ⁿ of them, mutually orthonormal, and they are the classical skeleton of the quantum space — the outcomes measurements return, the labels memory addresses would carry. Each basis state is a one-hot vector: |x⟩ has a single 1 among 2ⁿ entries, so as data it is maximally sparse, and simulators exploit this by representing many algorithms' starting states implicitly (index x means amplitude 1 at position x) rather than materializing the array. Every state is a linear combination of basis states with amplitudes c_x = ⟨x|ψ⟩. When a later chapter says "the state is peaked on basis state x", it means exactly one amplitude dominates — the interference choreography of all previous chapters, stated as a sentence about indices.

### 5.10 Basis ordering conventions

The same four numbers (c₀₀, c₀₁, c₁₀, c₁₁) can mean two different states, depending on which bit is "first". The dominant convention — big-endian in mathematics, and the source of endless Qiskit confusion — labels |q₁ q₂⟩ with q₁ the leftmost. numpy's `np.kron(A, B)` applies A to the leftmost (most significant) factor. Qiskit historically labels qubits little-endian: qubit 0 rightmost, so `kron(q1, q0)`-style ordering appears in statevector dumps. Neither is wrong; mixing them silently corrupts everything — CNOT control and target swap roles, statistics come out mirrored. Engineering defenses, all cheap: document the convention in one module-level comment; write a self-test that prepares a known asymmetric state like |01⟩ and asserts where its 1 sits (`np.argmax(psi) == index`); prefer round-trip tests over eyeballing. Convention bugs produce plausible, wrong physics — the worst bug class in this field.

### 5.11 Tensor-product operators

Operators on composite systems tensor the same way: (A ⊗ B)|a⟩|b⟩ = (A|a⟩) ⊗ (B|b⟩). The workhorse pattern is A applied to one qubit of many: I ⊗ I ⊗ A ⊗ I ⊗ …, padded with identities on untouched factors — `np.kron` chains, or in production code, application without materialization (7.11). Pauli tensor products deserve special status: any operator on n qubits expands in the Pauli basis {I, X, Y, Z}^{⊗n}, so Hamiltonians ship as weighted sums like 0.5·X⊗Z + 1.2·Z⊗I — the file format of quantum chemistry and of every Trotter-step simulator (chapter 30). The mixed-product identity (A⊗B)(C⊗D) = AC⊗BD lets whole circuits compile into single matrices when you can afford the exponential size — and reminds you why you usually cannot: two-qubit gates alone make a 2ⁿ×2ⁿ object no simulator should form explicitly beyond a dozen qubits.

### 5.12 Partial operations

A partial operation acts on some qubits and leaves others alone: to apply single-qubit gate G to qubit k of n, build G_k = I^{⊗(n−1−k)} ⊗ G ⊗ I^{⊗k} (in big-endian ordering) and multiply. For two-qubit gates like CNOT on non-adjacent qubits, insert SWAPs or index directly. This is the everyday construction of every circuit simulator, and it is where the conventions of 5.10 become code. Beyond gates, partial measurement works the same way: to measure qubit k in the computational basis, project with P₀^{(k)} = I ⊗ P₀ ⊗ I and P₁^{(k)}, with probabilities ⟨ψ|Pᵢ^{(k)}|ψ⟩, and renormalize the surviving branch. Two-qubit CNOT from primitives is worth deriving once by hand: CNOT = P₀ ⊗ I + P₁ ⊗ X — "if control is 0, do nothing; if 1, apply X" — the cleanest possible demonstration that projectors and tensor products already contain conditional logic.

### 5.13 Partial traces

The partial trace reverses composition in the only way quantum mechanics allows: it answers "what does subsystem A look like, ignoring B?" without pretending B has a definite state. Given a density matrix ρ on AB, the reduced state is ρ_A = Tr_B(ρ), computed blockwise: for ρ on A⊗B with B of dimension d, ρ_A[(i, i′), (j, j′)] sums ρ over the diagonal blocks of B: ρ_A[i·d + j, i′·d + j′] summed over j = j′. In numpy, reshape ρ to (d_A, d_B, d_A, d_B) and trace over the two B axes: `rho_A = np.einsum('ijkj->ik', rho.reshape(dA, dB, dA, dB))`. The result is the exact object needed when a subsystem is discarded or unobserved — the density-matrix formalism of chapter 33 exists because partial traces of pure states are generally mixed. For the Bell state, ρ_A is ½I: each qubit alone is maximally random; all the structure lives in the correlations.

### 5.14 Tensor networks — first encounter

The full state vector stores 2ⁿ amplitudes; a tensor network stores instead a mesh of small tensors connected by contracted indices, with size governed by a bond dimension χ that tracks how much entanglement crosses each cut. Product states are χ = 1 networks; matrix product states (MPS), the one-dimensional case, capture ground states of many physical systems with modest χ. This is the idea behind the classical simulators that contested quantum-supremacy claims: Google's 2019 Sycamore circuit was simulated classically by tensor-network methods at costs far below the naive exponential, and the game of "network versus state vector" continues with every new hardware announcement. The trade is precise: networks shine when entanglement is low or structured, and degrade toward the full exponential as χ grows. Chapter 45 develops the algorithms; here, hold the design lesson — representations that match the physics's correlation structure beat generic ones.

> [!experiment] On your laptop — watch entanglement appear
> Build |+0⟩, apply CNOT, and check that the result resists factorization. This is entanglement generation, verified by rank.
>
> ```python
> import numpy as np
>
> ket0 = np.array([1, 0], dtype=complex)
> ket1 = np.array([0, 1], dtype=complex)
> plus = (ket0 + ket1) / np.sqrt(2)
> psi = np.kron(plus, ket0)                 # |+0>: separable
> CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
> psi = CNOT @ psi                          # now (|00> + |11>)/sqrt(2)
> M = psi.reshape(2, 2)
> print("coefficient rank:", np.linalg.matrix_rank(M))   # 2 => entangled
> # measurement statistics: outcomes 00 and 11 only, perfectly correlated
> probs = np.abs(psi)**2
> shots = np.random.choice(4, size=10_000, p=probs)
> print("outcome counts:", np.bincount(shots, minlength=4))
> ```
>
> Rank 1 means product state, rank 2 means entangled. Change the input to |00⟩ and watch the rank stay 1: CNOT entangles only superposed controls.

> [!research] Research frontier
> The central quantitative question of this chapter is: how much entanglement does a given quantum state or computation actually contain? States useful for simulation (ground states of local Hamiltonians) obey area laws — entanglement scales with boundary, not volume — which is why tensor networks work; highly entangled circuits saturate the exponential, which is why they are hard. Characterizing which circuit families stay near area-law entanglement, and finding network geometries (PEPS, MERA, tree networks) matching higher-dimensional physics, are open problems with direct industrial consequences: every classical-simulation milestone in the supremacy debates was a tensor-network advance. This is quantum research performable entirely on a laptop, and it hires numerical programmers.

---

## 6. Probability and Statistics

> [!levels] Five levels of this chapter
> - **Intuition —** a quantum computer is a random-number generator with engineered biases; the engineer's job is to estimate those biases honestly.
> - **Mathematics —** distributions, expectation, variance, and the √(1/N) scaling that governs every measurement ever taken.
> - **Implementation —** numpy's random module and a hundred-line experiment harness cover everything this chapter asks.
> - **Engineering —** shots cost money and time; the discipline is deciding how many shots an answer is worth before running it.
> - **Research —** variance reduction (amplitude estimation) is the quantum analogue of Monte Carlo acceleration, and its overheads are still being fought over.

### 6.1 Classical probability

Probability theory formalizes randomness over a sample space: each outcome ω gets P(ω) ≥ 0 with Σ P(ω) = 1, and events get probabilities by addition. The two big theorems frame everything: the law of large numbers (sample frequencies converge to true probabilities as shots grow) and the central limit theorem (fluctuations shrink like 1/√N — the number behind every quantum experiment's error bars). Classical and quantum probability differ in exactly one axiom: in the classical (Kolmogorov) formalism, probabilities of disjoint events add directly, while quantum amplitudes add first and square after, enabling cancellation (interference). Everything else — random variables, expectation, variance, estimation — transfers unchanged. That is a genuinely useful statement for a programmer: your classical statistical toolkit applies to quantum data verbatim; only the mechanism generating the distribution differs.

### 6.2 Random variables

A random variable is a function from outcomes to numbers: it assigns a value to each result of a random process. The die is the process; the "number rolled" is the random variable. In quantum computing, every measurement is a random variable: the outcome distribution comes from the Born rule, but once sampled, the data is ordinary — you analyze counts of 0s and 1s with the classical machinery, no quantum theory required. Distinguish the object from its realizations: the random variable is the distribution (over infinitely many hypothetical repetitions); your 10,000 shots are one sample of it. numpy gives you the standard ones — `np.random.binomial`, `np.random.normal`, `np.random.poisson` — and the habit to build is thinking in the random variable's distribution first, data second. Quantum measurement outcomes are typically Bernoulli (single bit) or multinomial (bit strings) variables; both are classical.

### 6.3 Probability distributions

A distribution is the full description of a random variable: for discrete outcomes, the table of probabilities; for continuous ones, a density. Distributions have summaries — mean (center), variance (spread), shape (skew, tails) — and named families encode situations: Bernoulli for single bits, binomial for counts of successes in N trials, multinomial for bit-string counts, Poisson for rare events (dark counts, stray photons), normal for aggregated fluctuations. Quantum measurement in the computational basis produces exactly a multinomial distribution over 2ⁿ bit strings with probabilities |c_x|² — the state vector is a distribution you cannot read, and measurement is sampling from it. The engineering skill is matching summary to question: "did the circuit work?" is a question about one Bernoulli parameter; "what is the output distribution?" needs the multinomial, and far more shots. Print distributions, not single samples, whenever you can afford it.

### 6.4 Expectation

The expectation E[X] = Σ x·P(X = x) is the probability-weighted average of a random variable over infinitely many repetitions — the mean of the distribution, not of your sample. It is linear: E[aX + bY] = a·E[X] + b·E[Y] always, a property whole algorithms exploit. Quantum computing computes expectations by the same formula with Born-rule weights: ⟨ψ|H|ψ⟩ = Σ λᵢ·⟨ψ|Pᵢ|ψ⟩ (4.18) is the expected measurement outcome of observable H on state ψ — the number that variational algorithms (chapter 46) minimize and that every chemistry estimate targets. The gap between expectation and estimate is the working reality: E[X] is a property of the distribution; your experiment returns a sample mean x̄ that approaches it as shots accumulate, with error governed by variance (6.5). Whenever a paper reports ⟨H⟩ to five decimal places, the first question is: on how many shots?

### 6.5 Variance

Variance Var(X) = E[(X − E[X])²] measures spread around the mean; the standard deviation σ = √Var(X) is in the same units as X. Variance's crown property: for independent trials, variances add, so the sample mean of N shots has standard deviation σ/√N — the √N law that prices every quantum experiment. Measuring one observable with per-shot variance σ² and wanting accuracy ε costs N ≈ σ²/ε² shots: quadratic cost in precision, and the reason "just measure more precisely" is never cheap. Chebyshev's inequality turns variance into a guarantee: P(|X − E[X]| ≥ kσ) ≤ 1/k², distribution-free. For Bernoulli variables (a single bit outcome), Var = p(1−p) ≤ ¼, giving the universal floor N ≈ 1/(4ε²) shots for estimating any probability to accuracy ε. Budget experiments with this formula before running them; it is the difference between an estimate and a vibe.

### 6.6 Conditional probability

Conditional probability P(A|B) = P(A ∩ B)/P(B) re-weights the sample space under the knowledge that B occurred — a narrower world, renormalized. In quantum terms, conditioning is post-selection: keep only the shots where qubit 2 read 1, then look at the statistics of the rest; the resulting conditional distribution is exactly P(rest | qubit₂ = 1). Two classic results anchor careful use. Bayes' theorem, P(A|B) = P(B|A)·P(A)/P(B), is the engine of 6.7. And the law of total probability, P(A) = Σⱼ P(A|Bⱼ)·P(Bⱼ), is how simulators mix over branches. The standard error is confusing P(A|B) with P(B|A) — "probability of data given hypothesis" versus "probability of hypothesis given data" — a confusion that entire reams of bad quantum-ML benchmarking embody. Post-selected data is conditional data: report the conditioning event's frequency alongside every conditional statistic, or the numbers are uninterpretable.

### 6.7 Bayesian reasoning

Bayes' theorem upgrades beliefs with evidence: P(hypothesis|data) = P(data|hypothesis)·P(hypothesis)/P(data) — prior times likelihood, renormalized. For an engineer, Bayesian reasoning is the honest bookkeeping of how certainty accumulates: calibration of a qubit starts from a prior over pulse parameters, each experiment multiplies in a likelihood, and the posterior becomes the next prior. It is also the antidote to two failure modes of quantum-claims analysis: treating a single p-value as truth (6.12), and ignoring base rates — a spectacular result from a lab with a track record of spectacular results deserves different priors than one from an unvalidated source. Full Bayesian posteriors over quantum states or noise models are computationally heavy (the parameter spaces are large), which is why practice uses approximations — variational posteriors, Laplace approximations, or plain maximum-likelihood point estimates plus error bars. The discipline matters more than the machinery: state your prior, update on data, never reset it to suit a narrative.

### 6.8 Sampling

Sampling is drawing realizations from a distribution — and it is the only output a quantum computer ever gives. You do not read amplitudes; you run shots and count bit strings. So the skill of designing a sampling experiment is as fundamental as the circuits themselves. The machinery: independent, identically distributed shots; counts per outcome follow a multinomial; empirical frequencies are the natural estimator (6.9). numpy covers classical needs: `np.random.choice(2**n, size=shots, p=probs)` simulates a full measurement; seeding (`np.random.default_rng(seed)`) makes experiments reproducible, which in a stochastic field is not optional — an unreproducible histogram is not a result. Watch for the two classic sampling sins: sampling until the result looks right (optional stopping biases estimates) and discarding samples without reporting how many were dropped (post-selection without reporting breaks every estimator downstream). Both are, statistically, self-deception with extra steps.

### 6.9 Estimators

An estimator is a recipe that turns data into a guess about a distribution parameter; the estimate is its output on actual data. The sample mean x̄ = (1/N)·Σ xᵢ estimates E[X]; the sample variance estimates Var(X); empirical frequencies estimate Bernoulli p. Three properties grade estimators: bias (does the recipe target the right quantity on average — unbiased estimators are correct under repetition), consistency (does it converge to truth as data grows), and efficiency (how much data does it need for a given accuracy). The sample mean of independent shots is unbiased and consistent, with standard error σ/√N — quantified, not vibes. In quantum work, estimators appear wherever raw sampling is indirect: state tomography fits a density matrix to counts, randomized benchmarking fits an exponential decay to extract gate error, and variance-reduced estimators (amplitude estimation) trade extra circuit depth for fewer shots. Always report estimator and shot count together; an estimate without them is decoration.

```python
import numpy as np
rng = np.random.default_rng(42)
p_true = 0.37                                  # unknown "quantum" success probability
shots = 10_000
data = rng.random(shots) < p_true              # Bernoulli samples
p_hat = data.mean()
se = np.sqrt(p_hat * (1 - p_hat) / shots)      # standard error of the mean
print(f"estimate {p_hat:.4f} ± {se:.4f}")      # honest error bar, ~±0.005
```

### 6.10 Statistical uncertainty

Statistical uncertainty is the spread of an estimate caused by finite sampling — distinct from systematic error, which is a biased apparatus or model, and from numerical roundoff. The three must never be conflated: more shots shrink only the first. The tool is the standard error: for N independent samples with per-shot standard deviation σ, the sample mean's uncertainty is σ/√N. Halving your error bar quadruples your shots; a 10× tighter estimate costs 100× the runtime — the brutal economics behind every quantum experiment's precision claims. Confidence statements come from the same arithmetic (6.11). The engineering habit: attach an uncertainty to every number you report, propagate uncertainties through derived quantities (errors add in quadrature for products of independent estimates), and treat any quantum result quoted without error bars as unverified. In this field, the error bar is the result; the point estimate is just its center.

### 6.11 Confidence intervals

A confidence interval turns an estimate plus its uncertainty into a calibrated claim: "the true p lies in [p̂ − 1.96·SE, p̂ + 1.96·SE] with 95% coverage" — meaning the recipe captures the truth in 95% of repeated experiments, not that this particular interval has a 95% metaphysical grip on p. The normal-approximation interval (±1.96·σ/√N) is standard for means with enough samples; for small counts or probabilities near 0 or 1, use exact binomial intervals (`scipy.stats.binomtest`) or the Wilson interval, because the normal approximation fails exactly where quantum experiments live — rare success events from deep circuits. In quantum computing, confidence intervals are the honesty layer: "fidelity 0.998 ± 0.001" and "fidelity 0.998 ± 0.05" are different universes of claim, and benchmark tables that omit intervals are hiding the second kind. Build the habit early: no number leaves your notebook without an interval.

### 6.12 Hypothesis testing

Hypothesis testing asks a yes/no question of data: define a null hypothesis H₀ (no effect), compute how surprising the observed data would be under H₀ — the p-value — and reject H₀ when the surprise crosses a pre-chosen threshold α (typically 0.05). The machinery matters in quantum engineering for A/B comparisons: is gate set A's fidelity actually better than B's, or is the difference within noise? A two-sample test on per-shot outcomes answers it with a calibrated error rate. Two disciplines prevent the classic abuses. Fix the threshold and the analysis plan before looking — switching tests or endpoints after seeing data inflates false positives (the multiple-comparisons problem: run 20 benchmarks, expect one "significant" result by chance). And interpret p-values correctly: a p-value is P(data this extreme | H₀), not P(H₀ | data) — the Bayesian frame of 6.7 is the correct home for the question people usually mean to ask.

### 6.13 Monte Carlo methods

Monte Carlo methods estimate intractable quantities by random sampling: to estimate an average, sample it; accuracy improves as 1/√N regardless of dimension — the property that makes Monte Carlo the only general tool in high-dimensional spaces, quantum state spaces emphatically included. The recipe family: direct sampling when you can draw from the target distribution (simulating a circuit's measurement outcomes); rejection sampling and importance sampling when you cannot, re-weighting draws from an easier distribution; and Markov chain Monte Carlo (MCMC) when even that fails, wandering the distribution with a random walk whose stationary state is the target. Applications you will meet: sampling from Born distributions to validate simulators, Bayesian posteriors over noise parameters (6.7), and estimating partition-function-like quantities in physics-inspired problems. The universal caveat is variance: naive Monte Carlo on a rare event wastes shots; importance sampling that shifts probability mass onto the rare region is the difference between 10⁶ and 10³ shots.

### 6.14 Why quantum experiments are statistical

The closing synthesis: quantum mechanics makes statistics unavoidable, not incidental. Measurement is destructive and probabilistic — the Born rule hands you samples, never the amplitudes — so a quantum computation's output is a distribution you must estimate, with error bars, from repeated runs. Compounding this, no-cloning forbids re-measuring one copy; every shot consumes a fresh preparation, so information-per-shot is bounded by design. And hardware noise adds drift on top of sampling noise: your 10,000 shots embed both statistical uncertainty and a device state that may have shifted during them. The practical doctrine, used in every later chapter: define the observable, budget shots from the √N law (6.5), attach confidence intervals (6.11), and separate statistical from systematic error explicitly. A quantum engineer who cannot state an uncertainty is not doing quantum engineering — they are watching a slot machine.

> [!experiment] On your laptop — the √N law, felt not memorized
> Estimate a Born-rule probability at increasing shot counts and watch the error bars shrink exactly as theory predicts.
>
> ```python
> import numpy as np
> rng = np.random.default_rng(7)
> psi = np.array([1, 1j]) / np.sqrt(2)
> p = abs(psi[1])**2                     # true P(outcome 1) = 0.5
> for N in (100, 1_000, 10_000, 100_000):
>     shots = (rng.random(N) < p).mean() # sample mean
>     se = np.sqrt(shots * (1 - shots) / N)
>     print(f"N={N:7d}: {shots:.4f} ± {se:.4f}")
> ```
>
> Each 10× in shots buys roughly 3.2× (i.e. √10) tighter error — the √N law pricing every experiment in this book. Re-run with different seeds to see the intervals wobble around the truth.

> [!research] Research frontier
> Estimating expectation values from samples is expensive — Θ(1/ε²) shots for accuracy ε — and that quadratic scaling is the statistical bottleneck of variational quantum algorithms and chemistry estimates alike. Quantum amplitude estimation achieves the theoretically optimal Θ(1/ε) scaling using phase estimation, but its fault-tolerant overhead is enormous; the open game is interpolation — maximum-likelihood amplitude estimation, Bayesian estimators, and randomized measurement schemes (classical shadows) that extract many observables from one dataset. Which estimator wins at realistic shot budgets and noise levels is unresolved and highly publishable, and the baselines are classical statistics you already know how to run.

---

## 7. Numerical Computation

> [!levels] Five levels of this chapter
> - **Intuition —** computers approximate mathematics; every simulation result is an answer to a slightly different question than you asked.
> - **Mathematics —** floating-point representation, error accumulation, conditioning, and the algorithms of numerical linear algebra.
> - **Implementation —** numpy and scipy are the workbenches; knowing which routine to call and when to distrust it is the skill.
> - **Engineering —** a quantum simulator's answers are only as good as its numerical hygiene: norm checks, tolerances, and dtype discipline.
> - **Research —** simulating quantum systems classically at the edge of feasibility is a living field, and it needs numerical software engineers.

### 7.1 Floating-point arithmetic

Floating-point numbers are scientific notation in binary: a sign, a mantissa, and an exponent, giving about 15–16 significant decimal digits for float64. They are not real numbers: most values (0.1 among them) have no exact representation, arithmetic rounds at every step, and familiar algebra partially fails — addition is not associative, `(a + b) + c ≠ a + (b + c)` in general. The constants of the craft: machine epsilon (≈ 2.2×10⁻¹⁶ for float64, `np.finfo(float).eps`) is the relative granularity; comparisons use tolerances (`np.allclose`, `np.isclose` — never `==`); catastrophic cancellation amplifies relative error when subtracting nearly equal numbers (compute |⟨φ|ψ⟩|² as the squared modulus, not as ⟨φ|ψ⟩·⟨φ|ψ⟩ with a separately-computed phase). Quantum states compound this by the million: 2ⁿ amplitudes each rounding per gate. Nothing here is exotic — it is the same arithmetic every spreadsheet runs — but quantum simulation multiplies its failures by 2ⁿ.

### 7.2 Numerical error

Every numerical result carries two error layers: roundoff (representation and arithmetic granularity) and truncation (approximation built into an algorithm — a truncated series, an iterative solve stopped early). Engineering means budgeting both. Roundoff accumulates gradually: a circuit of 10⁴ gates on float64 amplitudes accumulates relative error around 10⁴·10⁻¹⁶ ≈ 10⁻¹² — negligible per gate, visible in aggregate, and the reason simulators re-normalize states periodically rather than trusting the algebra to keep ‖ψ‖ = 1. Truncation error is algorithmic and usually dominant: a Krylov exponential stopped at m steps, a Trotter split of order Δt², a finite-difference derivative with step h. The discipline: for every approximation, know its order — how error scales with the knob (steps, threshold, h) — and verify empirically by halving the knob and watching the error fall by the predicted factor. An error estimate you have not validated by convergence testing is decoration.

### 7.3 Conditioning

Conditioning measures how violently a problem's answer responds to small input perturbations — a property of the problem, not the algorithm. The condition number κ(A) = σ_max/σ_min (ratio of largest to smallest singular value) prices linear solves: relative error in x of Ax = b can reach κ times the relative error in the inputs, so κ = 10¹⁰ on float64 data means you may retain only ~6 correct digits no matter how good the solver. Check it: `np.linalg.cond(A)`; act when it warns — rescale variables, regularize, or reformulate. Quantum instances: density matrices near pure states are rank-deficient and ill-conditioned (regularize before inverting covariance matrices in tomography); eigenvectors of nearly degenerate eigenvalues are individually unstable even though the invariant subspace is fine (compare subspaces, not vectors, 4.16); and least-squares fits of noisy calibration data need ridge regularization or they chase noise. Rule: ill-conditioning is a property to be designed around, never merely endured.

### 7.4 Numerical linear algebra

Numerical linear algebra is the discipline of computing matrix answers stably and fast, and it is the load-bearing wall of every quantum simulator. The core decompositions, each with a specialty: LU (with pivoting) for general solves — `np.linalg.solve`; Cholesky for symmetric/Hermitian positive-definite systems, cheaper and stable; QR for orthonormalization and least squares — also how simulators re-orthonormalize state batches (3.19); SVD, the most informative, giving singular values, ranks, conditioning, and best low-rank approximation in one call — `np.linalg.svd`; and eigendecompositions `eigh`/`eig` for spectra (4.17). Cost is O(n³) for dense n×n across the board, which sets the practical ceiling: dense state-vector simulation tops out near n ≈ 25–28 qubits on a laptop, n ≈ 40 on a large machine. The engineering habit: pick the decomposition matching your matrix's structure (Hermitian? positive-definite? sparse?) — the wrong generic routine costs accuracy and an order of magnitude in time.

### 7.5 Sparse matrices

A matrix is sparse when most entries are zero, and quantum operators are sparsity royalty: an n-qubit Hamiltonian with local interactions has O(n·polylog) nonzero entries in a 2ⁿ×2ⁿ matrix — storing it densely is malpractice past ~15 qubits. scipy.sparse (`csr_matrix`, `csc_matrix`) stores (row, column, value) triples and computes with them: sparse matvec costs O(nnz), not O(n²), and applying I⊗…⊗G⊗…⊗I to a state vector touches only the entries the gate couples — the trick that pushes laptop simulation to 30+ qubits. Sparse-aware eigensolvers (`scipy.sparse.linalg.eigsh`, Lanczos-based) extract a few extremal eigenvalues of huge matrices without forming them. Two caveats: sparsity is per-operator and degrades under multiplication — products of sparse matrices fill in, so Trotter steps apply factors sequentially instead of composing them; and indices remain 64-bit, so 2ⁿ exceeding 2⁶³ is a wall even sparse code cannot pass. Structure beats size; exploit both.

### 7.6 Eigenvalue algorithms

Production eigenvalue computation is iterative: dense solvers (LAPACK behind numpy's `eigh`) reduce to tridiagonal form then iterate (QR algorithm) — robust, O(n³), all eigenvalues at once. But quantum problems usually want a few eigenvalues of a huge matrix, and for that the iterative family rules. Lanczos (Hermitian case) and Arnoldi (general) build a small Krylov subspace from repeated matrix-vector products — needing only the ability to apply A, never to store it — and extract Ritz-value approximations of extremal eigenpairs; `scipy.sparse.linalg.eigsh(A, k=6, which='SA')` is the workhorse. Convergence is fastest for well-separated extremal eigenvalues and slow inside spectra clusters; preconditioning and shift-invert strategies (which do need solves, hence good conditioning) fix the hard cases. The same Krylov machinery computes e^{A}v for large sparse A — matrix exponentials of Hamiltonians without diagonalization, the standard method for quantum dynamics at sizes where eigh is impossible.

### 7.7 Optimization

Optimization — minimizing a scalar function f(θ) over parameters — powers the classical half of variational quantum algorithms (chapter 46): the parameters θ of a parameterized circuit are tuned by a classical optimizer that only sees sampled costs. The landscape of methods: gradient descent and its momentum/adaptive variants (Adam) when gradients exist — on quantum hardware, gradients come from parameter-shift rules, exact but costing two circuit evaluations per parameter; derivative-free methods (Nelder–Mead, COBYLA) when noise makes gradients meaningless; and global/heuristic methods (SPSA — perturb-and-difference, famously robust to noisy cost evaluations) for barren, flat, or deceptive landscapes. Every method carries tuning folklore: learning rates, initial points, stopping criteria — and every noisy quantum cost function adds variance on top (6.5), so optimizer convergence must itself be assessed statistically. The unifying discipline from calculus: check gradients numerically (`scipy.optimize.check_grad`-style finite differences) before trusting any optimizer's complaints about them.

### 7.8 Automatic differentiation

Automatic differentiation (AD) computes exact derivatives of code: not symbolic expansion, not finite-difference approximation, but the chain rule applied mechanically to every elementary operation, giving gradients to machine precision at a small constant factor of runtime. Two modes: reverse mode (backpropagation) computes all partial derivatives of one output in one sweep — cost roughly independent of parameter count, hence deep learning's engine; forward mode is cheaper for few inputs, many outputs. The quantum connection is direct: autodiff simulators differentiate entire circuits, making hybrid quantum-classical training gradient-based end to end; and the parameter-shift rule (7.7) is AD's hardware analogue — for gates of the form e^{iθP}, ∂f/∂θ = [f(θ + π/2) − f(θ − π/2)]/2 exactly, sampled on real devices. Tooling: JAX and PyTorch for classical graphs, qiskit's and PennyLane's built-in AD for hybrid workflows. The engineer's rule: if your loss is differentiable, hand-rolled finite differences are waste — and usually wrong.

### 7.9 Monte Carlo simulation

Monte Carlo reappears here as a numerical method with engineering teeth: when a quantity has no closed form — an integral over configurations, a noise-averaged observable, a tail probability — simulate the underlying randomness N times and average. The machinery is chapter 6's (sampling, √N convergence, error bars), applied to physics: simulate noisy circuits shot-by-shot with stochastic gate errors and decoherence events; estimate detection probabilities of rare error syndromes by importance sampling that forces syndrome events and re-weights; average observable estimates over draws of unknown noise parameters. Variance reduction is the craft: importance sampling (sample the rare, reweight), control variates (subtract a correlated quantity with known mean), and antithetic draws (pair each sample with its mirror) routinely buy one to three orders of magnitude in shots. In error-correction research (chapter 37), Monte Carlo over syndrome histories is the standard evaluation of decoders — and it is embarrassingly parallel, so your laptop's cores and a `concurrent.futures` map go a long way.

### 7.10 Performance considerations

Simulation performance is mostly memory bandwidth and algorithm choice, rarely raw FLOPS. The hierarchy of wins, in order of leverage: algorithmic (avoid forming 2ⁿ×2ⁿ operators — apply gates factor-wise, 7.11; exploit sparsity, 7.5; use stabilizer or tensor-network representations when the circuit permits, 5.14); precision (float32 halves memory and doubles throughput versus float64, tolerable for sampling experiments though not for phase-sensitive accumulation — know which your experiment is); vectorization (numpy applies gates to whole state batches per call — a Python loop over amplitudes is a 100× self-inflicted tax); parallelism (multicore via vectorized BLAS threads or `multiprocessing`, since state updates parallelize trivially across amplitudes); and memory layout (contiguous complex128 arrays, minimal copies — `np.kron` chains allocate massively; build operators in-place where you can). Profile before optimizing — `cProfile` plus a stopwatch on the hot gate-application loop — and expect the answer to be "you materialized something you should have applied on the fly".

### 7.11 Classical simulation of quantum systems

This is the chapter's summit: the techniques above assemble into a working n-qubit simulator, the tool you will use more than any other in this book. The dense state-vector engine is 200 lines: states as complex128 arrays of length 2ⁿ; gates as small matrices applied via reshape-and-broadcast (apply single-qubit G on qubit k by reshaping the state to shape (2, 2, …, 2) and tensordoting along axis k — no np.kron, no 2ⁿ×2ⁿ operator ever formed); measurements by sampling from |amplitudes|²; noise by density matrices (memory ×2², halving your qubit budget) or by stochastic trajectories (sample which error occurred, evolve the state vector — Monte Carlo over noise realizations, 7.9). Beyond dense: stabilizer simulators run certain circuits (Clifford gates, Pauli measurements) in polynomial time and simulate error-correction experiments at hundreds of qubits; tensor networks buy entanglement-limited sizes. Chapter 14 builds the engine properly; this section is its numerical foundation.

### 7.12 Why simulation becomes exponentially difficult

The closing honesty: no cleverness removes the exponential, because the exponential is the information. A generic n-qubit state has 2ⁿ complex amplitudes of independent content; any representation that stores fewer must be discarding structure, and works exactly where that structure is absent or shallow. The escape hatches are all structure-conditional: product and low-entanglement states compress (5.7, 5.14); Clifford circuits simulate in polynomial time but are efficiently classically simulable precisely because they cannot do universal computation; sparse operators tame gates but not generic states. Random deep circuits — the very ones used for supremacy claims — are designed to evade all of these, which is why simulating 50+ qubits of them strains the world's best machines and why each quantum announcement is followed by a classical counterattack with better networks. For your practice: know which regime a problem sits in before choosing a tool, and treat "simulate it" as a research decision, not a default.

> [!experiment] On your laptop — simulate 25 qubits, honestly
> A minimal but real benchmark: apply a random single-qubit gate to a 25-qubit state via reshape, and time it. No kron, no giant matrices.
>
> ```python
> import numpy as np, time
>
> n = 25
> psi = np.zeros(2**n, dtype=np.complex128); psi[0] = 1.0
> G = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2)  # Hadamard
>
> t0 = time.perf_counter()
> psi = psi.reshape([2] * n)                     # one axis per qubit
> psi = np.tensordot(G, psi, axes=(1, 0))        # apply G on qubit 0
> psi = np.moveaxis(psi, 0, 0)                   # (result axis is qubit 0)
> psi = psi.reshape(-1)
> dt = time.perf_counter() - t0
> print(f"one gate on {n} qubits: {dt*1e3:.1f} ms, norm {np.linalg.norm(psi):.6f}")
> ```
>
> ~33 MB per state, milliseconds per gate. Now extrapolate: n = 30 is ~17 GB; n = 40 is ~19 TB. The wall is real, structural, and the reason chapters 5 and 45 exist.

> [!research] Research frontier
> The boundary of classical simulation is a moving research front, and it is fought with numerical software engineering. State vectors held the line at ~50 qubits for a decade; tensor networks pushed circuit simulation past 60 qubits for structured families; stabilizer methods handle hundreds of qubits for restricted gates; and the interplay with quantum hardware claims — each supremacy or advantage announcement triggering classical counter-simulations within months — is now a standing dynamic of the field. Open problems with engineering shape: adaptive tensor-network topologies chosen by the circuit itself, GPU-native contraction ordering, and rigorous error bounds for truncated simulations. If your joy is high-performance numerical code, this frontier hires you without a physics PhD — the simulators themselves are the product.
