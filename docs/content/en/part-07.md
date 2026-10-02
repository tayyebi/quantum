# Part VII — Quantum Algorithms

The algorithms that justify the field. Nine chapters: the shared paradigm (18), the four oracle algorithms that built it (19–22), the Fourier machinery that makes it scale (23–24), and the two headline results (25–26). Every algorithm gets the same treatment: the problem, the interference story in words, the circuit, a runnable simulation, and the honest cost.

## 18. The Algorithmic Paradigm

> [!levels] Five levels of this chapter
> - **Intuition —** a quantum algorithm does not try all answers; it choreographs amplitudes so wrong answers cancel and the right one dominates.
> - **Mathematics —** an algorithm is a unitary circuit followed by measurement; analysis happens in Hilbert space and in query complexity.
> - **Implementation —** every algorithm in this part runs in well under 60 lines of numpy on the state-vector simulator of Part V.
> - **Engineering —** asymptotic wins survive only if the oracle and the gate count survive; error correction is what turns O(√N) or O(n³) into a feasible run.
> - **Research —** which oracle separations instantiate into real problems (versus dequantization), and tight lower bounds, remain open.

### 18.1 What makes an algorithm quantum?

Not the use of superposition — every naive "try all inputs in parallel" idea dies at measurement (1.7). An algorithm earns the name when interference does logical work: the circuit maps the input to a state where amplitudes for wrong answers point in different phases and cancel, while amplitudes for right answers align. Three ingredients recur throughout this part: a coherent encoding of structure (parity, period, marking) into *phases* via an oracle; a basis change — Hadamards or a Fourier transform — that converts those phases into measurable amplitude concentration; and a classical post-processing step (linear algebra, continued fractions, gcd) that extracts the answer from samples. Remove any one and the algorithm stops working; the rest of Part VII is these three ingredients, recombined.

### 18.2 Oracle-based algorithms

Most provable quantum speedups live in the **oracle model**: a function f is available only as a black-box unitary `Uf: |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩`, and we count *queries* — calls to `Uf` — rather than raw time. This isolates the algorithmic idea from data-loading questions and makes lower bounds provable (the polynomial and adversary methods, Part VIII). Deutsch, Deutsch–Jozsa, Bernstein–Vazirani, Simon, and Grover all live here:

| Algorithm | Problem | Quantum queries | Classical queries |
|---|---|---|---|
| Deutsch | constant vs balanced, 1 bit | 1 | 2 |
| Deutsch–Jozsa | constant vs balanced, n bits | 1 | 2ⁿ⁻¹+1 (deterministic) |
| Bernstein–Vazirani | hidden string a | 1 | n |
| Simon | hidden period s | O(n) | Θ(2^{n/2}) |
| Grover | find marked item among N | Θ(√N) | Θ(N) |

The honesty clause: an oracle is a promise that `Uf` is cheap to implement coherently. If building it costs more than the classical algorithm, the "speedup" is fiction — the topic of 28.9 and the dequantization results.

### 18.3 Interference as computation

The recurring mechanism is **phase kickback**: prepare an ancilla in `|−⟩ = (|0⟩−|1⟩)/√2`, and the oracle turns function values into phases — `Uf|x⟩|−⟩ = (−1)^{f(x)}|x⟩|−⟩`. Phases are invisible to measurement; they are relative, structural information. The algorithm's job is to rotate phases into amplitudes: apply Hadamards (or a QFT) so that `(−1)^{f(x)}` terms add constructively for some outcomes and destructively for others. You never learn f(x) for any particular x; you learn a *global* property that no single query reveals. This one trick, scaled up, is Deutsch (one bit), Bernstein–Vazirani (a linear form), Simon (a period), and the phase oracle of Grover. Learn it once here and every circuit in chapters 19–26 decomposes into phases plus basis changes.

### 18.4 Amplitude amplification

A template worth naming early. Suppose a probabilistic classical procedure A succeeds with probability p; repeating it k times boosts success to about 1−(1−p)^k, so error ε costs O(1/ε) repetitions. **Amplitude amplification** (Brassard–Høyer–Mosca–Tapp, 2000) runs a quantum version — apply A, reflect about the success subspace, reflect about the initial state — and reaches success ≈ 1 with O(1/√p) applications. That is a *quadratic* speedup over the best possible classical repetition, and it applies to almost any probabilistic algorithm: Monte Carlo estimation, sampling, backtracking search. Grover's algorithm is the special case where A is the Hadamard layer; the full machinery is 25.6.

### 18.5 Phase estimation

The second template: given a unitary U, one of its eigenvectors |u⟩, and the ability to apply controlled-U, estimate φ where `U|u⟩ = e^{2πiφ}|u⟩` to m bits of precision. The circuit writes e^{2πi·2^k·φ} phases into a counting register and reads them out with an inverse QFT. Phase estimation is the engine inside Shor's algorithm (order finding is phase estimation on a modular-multiplication unitary) and the accepted route to ground-state energies in chemistry. It costs t = m + O(log(1/ε)) qubits and t applications of controlled powers of U; the hard part is always U itself. Chapter 24 gives it a full treatment.

### 18.6 Quantum walks

The analog of random walks: a walker moves on a graph by unitary steps, in discrete time (coin or Szegedy walks) or continuous time (e^{−iHt}). On unstructured problems they reproduce Grover's quadratic speedup. On structured problems they can do more: element distinctness falls to O(N^{2/3}) queries (Ambainis), and Childs exhibited an oracle problem where a continuous-time walk is exponentially faster than any classical algorithm on the same graph. Quantum walks also underlie practical Hamiltonian simulation on sparse graphs. They are less central to this part than the QFT/QPE machinery, but they share its philosophy: turn graph or spectral structure into interference, then sample.

### 18.7 Quantum Fourier transforms

The extraction primitive behind the big results: a state whose amplitudes are *periodic* becomes, after a QFT, a state concentrated on a few basis states — periods become peaks you can sample. The circuit costs only O(n²) gates for N = 2ⁿ dimensions, against O(N log N) for the classical FFT — but read the fine print in 23.7: the QFT consumes a quantum state, not a list of numbers, and returns a state you sample rather than a table. It is the shared skeleton of Simon's algorithm, Shor's period finding, and phase estimation, which is why it gets its own chapter (23) before the algorithms that depend on it.

## 19. Deutsch's Algorithm

> [!levels] Five levels of this chapter
> - **Intuition —** one query decides a global property of a 1-bit function because the two possible answers interfere.
> - **Mathematics —** the amplitude of |0⟩ after the circuit is ((−1)^{f(0)}+(−1)^{f(1)})/2, which is exactly 0 for balanced f.
> - **Implementation —** ~20 lines of numpy; run all four possible oracles and check the deterministic answers.
> - **Engineering —** a 2-qubit, depth-3 benchmark; on hardware the failure modes are dephasing of the |−⟩ ancilla and readout error.
> - **Research —** pedagogically tiny, historically huge: it introduced the query-oracle framework everything else builds on.

### 19.1 The problem

You are given a one-bit function f: {0,1} → {0,1} as a black box. The function is *promised* to be either **constant** (f(0) = f(1)) or **balanced** (f(0) ≠ f(1)). Question: which is it? The problem looks trivial and is — that is the point. It is the smallest setting in which "a global property of f" can be separated from "the values of f", so it is the cleanest place to watch interference perform a query-computational feat. Deutsch posed it and solved it in 1985, in the first quantum algorithm ever written down; everything in this part is a descendant.

### 19.2 Classical solution

Deterministically you must query f twice: f(0) alone is consistent with both cases, and so is f(1) alone. Two queries always decide it — if the answers agree, constant; else balanced. Randomization cannot help: with one query you see f(x) for one x, and that single bit is compatible with both a constant and a balanced function, so no strategy beats a coin flip. Classical query complexity: exactly 2. The quantum algorithm, we will see, needs exactly 1. A factor of 2 — the smallest possible separation — but a separation with a mechanism, not an accident.

### 19.3 Quantum circuit

```text
q0: |0> ──H──■──H──M        outcome 0 → constant
            │               outcome 1 → balanced
q1: |1> ──H──Uf──            Uf: |x>|y> ↦ |x>|y ⊕ f(x)>
```

Two qubits. The input register q0 starts in |0⟩; the ancilla q1 starts in |1⟩. Apply H to both, apply the oracle once (control q0, target q1), apply H to q0 again, and measure q0 only. The ancilla is never measured — its job, explained next, is to be in |−⟩ so the oracle acts as a phase. One oracle query, one measurement, a deterministic answer.

### 19.4 Interference

After the Hadamards the state is `(|0⟩+|1⟩)/√2 ⊗ |−⟩`. Since `|−⟩` is an eigenstate of every X-flip, the oracle kicks f back as phase: `Uf(|x⟩|−⟩) = (−1)^{f(x)}|x⟩|−⟩`. The input register now holds `((−1)^{f(0)}|0⟩ + (−1)^{f(1)}|1⟩)/√2`. The final H maps that to amplitudes — for |0⟩: `((−1)^{f(0)}+(−1)^{f(1)})/2`, and for |1⟩: `((−1)^{f(0)}−(−1)^{f(1)})/2`. If f is constant the two terms *add* to ±1: you measure 0 with certainty. If f is balanced they *cancel* to exactly 0: you measure 1 with certainty. Destructive interference between the two queries is the entire computation; the ancilla made it possible by converting values into phases.

### 19.5 Implementation

Build the state vector of two qubits as a length-4 numpy array (index = `2·x + y`), the oracle as a permutation matrix, and Hadamards as the 2×2 matrix you already know. The whole algorithm:

```python
import numpy as np

H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)

def deutsch(f):
    psi = np.array([0, 1, 0, 0], dtype=complex)      # |0>|1>
    psi = np.kron(H, H) @ psi                        # H on both qubits
    U = np.zeros((4, 4))                             # oracle permutation
    for x in (0, 1):
        for y in (0, 1):
            U[(x << 1) | (y ^ f(x)), (x << 1) | y] = 1
    psi = U @ psi
    psi = np.kron(H, np.eye(2)) @ psi                # final H on q0
    p0 = abs(psi[0]) ** 2 + abs(psi[1]) ** 2         # P(q0 = 0)
    return "constant" if p0 > 0.5 else "balanced"
```

The permutation matrix is symmetric because `y ↦ y ⊕ f(x)` is its own inverse — a small mercy you will not get with general oracles.

### 19.6 Experimental verification

> [!experiment] On your laptop — all four oracles
> There are exactly four functions {0,1} → {0,1}. Run the algorithm on each and compare with the truth:

```python
oracles = {"f=0": lambda x: 0, "f=1": lambda x: 1,
           "f=x": lambda x: x, "f=1-x": lambda x: 1 - x}
for name, f in oracles.items():
    answer = deutsch(f)                    # from 19.5
    truth = "constant" if name in ("f=0", "f=1") else "balanced"
    print(name, "->", answer, "| expected:", truth)
```

> The output is deterministic — no shots, no histograms; a nice change from Born-rule statistics. On real hardware the answer does become statistical: dephasing of the ancilla (which must stay in |−⟩) and readout errors flip outcomes, so you run ~1000 shots and look at the majority. Historically, Deutsch's 1985 version succeeded only with probability ½; the deterministic circuit here is the 1992 Deutsch–Jozsa construction specialized to one bit — the first repair job in quantum algorithm history.

## 20. Deutsch–Jozsa

> [!levels] Five levels of this chapter
> - **Intuition —** Deutsch scaled to n bits: 2ⁿ input paths interfere, and all-zeros survives only if f is constant.
> - **Mathematics —** the amplitude of |0…0⟩ after the circuit is (1/2ⁿ)·Σ_x (−1)^{f(x)}, which is ±1 under the constant case and 0 under the balanced case.
> - **Implementation —** the same simulator with n+1 qubits; verify the deterministic outcome for random promised functions.
> - **Engineering —** depth 3 plus one oracle call; still a promise problem with no natural instances to run it on.
> - **Research —** the first exponential oracle separation; superseded by Bernstein–Vazirani and Simon for bounded-error separations.

### 20.1 Problem definition

Now f: {0,1}ⁿ → {0,1}, promised to be either **constant** on all 2ⁿ inputs or **balanced** — exactly 2ⁿ⁻¹ inputs map to 1. Decide which. The problem was posed and solved by Deutsch and Jozsa in 1992 and was the first *exponential* separation between classical and quantum query complexity: classically you may need to look at 2ⁿ⁻¹+1 inputs, quantum needs one oracle call, with certainty. Like Deutsch's original, it is a promise problem: on functions outside the promise the algorithm's output is meaningless. Keep that asterisk in view for 20.6.

### 20.2 Oracle model

The black box is `Uf: |x⟩|y⟩ ↦ |x⟩|y ⊕ f(x)⟩` on n+1 qubits — the same oracle convention as Deutsch, one unitary per query, and exactly one query is granted. As before, feeding the ancilla `|−⟩ = (|0⟩−|1⟩)/√2` converts the oracle into a diagonal phase operator `(−1)^{f(x)}` on the input register: the *phase oracle*. Nothing about the construction depends on what f computes internally — that is the strength and (20.6) the weakness of the model.

### 20.3 Circuit construction

```text
q0 … q(n-1):  |0> ─H─●─H─M     read 0…0 ⟺ f constant (deterministic)
                  │
q_n:          |1> ─H─Uf──      Uf: |x>|y> ↦ |x>|y ⊕ f(x)>
```

Hadamards on all n+1 qubits, one oracle call, Hadamards on the n input qubits, measure the inputs. In pseudocode, against the state-vector simulator you already have:

```text
psi = |0…0>|1>
apply H to all n+1 qubits
psi = Uf @ psi              # the single query
apply H to the n input qubits
answer = "constant" if measured(input register) == 0…0 else "balanced"
```

### 20.4 Interference

Work through the amplitude of the all-zeros outcome. After the oracle and final Hadamards it is `(1/2ⁿ)·Σ_x (−1)^{f(x)}` — the average of (−1)^{f(x)} over all inputs. If f is constant, every term is +1 or every term is −1: the sum is ±2ⁿ, the amplitude is ±1, and you measure all-zeros with certainty. If f is balanced, exactly half the terms are +1 and half are −1: the sum is 0. All 2ⁿ computational paths interfere to destroy that one outcome — and since the state has norm 1, the probability mass must sit somewhere else, on strings that certify *balanced*. One query, 2ⁿ constructive/destructive terms, zero probabilities computed numerically.

### 20.5 Complexity

Quantum: 1 query, O(n) Hadamard gates plus the oracle, success probability exactly 1. Classical deterministic: 2ⁿ⁻¹+1 queries in the worst case — query inputs until you see both values (balanced) or have queried 2ⁿ⁻¹+1 equal ones (constant, because a balanced function only has 2ⁿ⁻¹ zeros). Classical randomized: 2 queries suffice for success probability ≈ 3/4, and O(log(1/δ)) queries for error δ — so the exponential gap is against *deterministic* classical algorithms, and a fair reading puts the honest gap at one query versus a constant number. That is still a separation with a proof; it is just not the headline the 1992 paper suggested.

### 20.6 Limitations of the result

Three limitations, all structural. **The promise**: real functions are neither constant nor balanced, and off-promise the output is arbitrary — no natural computational task arrives in this form. **The oracle**: the speedup assumes Uf costs one "unit"; for any specific promised f you might write down, the classical algorithm could inspect its circuit definition instead of querying it. **The separation type**: it vanishes against randomized classical algorithms (20.5), so the result's lasting value is pedagogical — it introduced the phase-oracle-plus-Hadamards template and the notion of query complexity, which Bernstein–Vazirani and Simon immediately pushed to separations that survive randomization. Treat Deutsch–Jozsa as the field's first exercise, not its first result.

## 21. Bernstein–Vazirani

> [!levels] Five levels of this chapter
> - **Intuition —** f(x) = a·x ⊕ b hides a bit string a as a linear form; one quantum query reads a out exactly.
> - **Mathematics —** H^{⊗n}·oracle·H^{⊗n} maps the phase pattern (−1)^{a·x} onto the basis state |a⟩ with amplitude 1.
> - **Implementation —** numpy with the Walsh–Hadamard transform; exact recovery for any n that fits in memory.
> - **Engineering —** same resources as Deutsch–Jozsa (n+1 qubits, one oracle call); the oracle is a chain of CNOTs.
> - **Research —** quantum parity learning and Fourier sampling start here; noisy-oracle variants remain instructive open ground.

### 21.1 Hidden strings

Bernstein and Vazirani (1993) hid a string instead of a predicate: `f(x) = a·x ⊕ b = (a₁x₁ ⊕ … ⊕ aₙxₙ) ⊕ b`, and the task is to recover the hidden string a. The constant b is folded into the oracle and, as we will see, made irrelevant by the ancilla convention. The result matters historically because it was the first separation against *bounded-error* classical algorithms — BQP versus BPP in the oracle world — closing the randomized loophole left open by Deutsch–Jozsa. It is also the first algorithm whose output is a *string* rather than a one-bit verdict.

### 21.2 Oracle construction

`Uf: |x⟩|y⟩ ↦ |x⟩|y ⊕ a·x ⊕ b⟩` is buildable from classical reversible gates: for each i with aᵢ = 1, a CNOT from input qubit i into the ancilla computes the parity, plus one X on the ancilla if b = 1. Now run the ancilla in `|−⟩`. Each CNOT then contributes a phase: `CNOT_{i→a}|x⟩|−⟩ = (−1)^{aᵢxᵢ}|x⟩|−⟩` — phase kickback again — so the whole oracle acts as `(−1)^{a·x ⊕ b} = (−1)^b·(−1)^{a·x}` on the input register. The global factor (−1)^b is unobservable; b has been erased by the ancilla convention, and only the phase pattern of a remains.

### 21.3 Quantum solution

```text
q0 … q(n-1):  |0> ─H─●─H─M     readout = a, with certainty
                 │
q_n:          |1> ─H─Uf──      Uf: |x>|y> ↦ |x>|y ⊕ (a·x ⊕ b)>
```

The circuit is *identical* to Deutsch–Jozsa — only the promised structure of f changed. After the oracle the input register holds `(1/√2ⁿ)·Σ_x (−1)^{a·x}|x⟩`. Applying H^{⊗n} (which maps `|x⟩ → (1/√2ⁿ)·Σ_y (−1)^{x·y}|y⟩`) gives the amplitude of basis state y: `(1/2ⁿ)·Σ_x (−1)^{x·(a⊕y)}` — a sum of ±1 over 2ⁿ terms that equals 1 if y = a and 0 otherwise, by the same cancellation as 20.4. Measurement returns a exactly, every run, no shots needed.

### 21.4 Classical comparison

Each classical query returns one linear equation `a·x = c` in unknown bits a₁…aₙ; n linearly independent queries are needed before a is pinned down — an information-theoretic lower bound, not an artifact of algorithm design. The quantum algorithm extracts all n bits in a single query. The honest explanation is *not* "it queried all 2ⁿ inputs in parallel": it queried once, but on a superposition, and the oracle's action on all inputs simultaneously is what lets one global measurement reveal the linear functional. This was the first BQP-versus-BPP oracle separation, and it convinced the field that randomized classical lower bounds would not dissolve quantum advantage.

### 21.5 Implementation

```python
import numpy as np
n, a, b = 4, 0b1011, 1
N = 2 ** n
H1 = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
Hn = H1
for _ in range(n - 1):
    Hn = np.kron(Hn, H1)                       # Walsh–Hadamard on n qubits
f = np.array([(bin(x & a).count("1") + b) % 2 for x in range(N)])
psi = np.ones(N, dtype=complex) / np.sqrt(N)   # H on all inputs
psi *= (-1.0) ** f                             # oracle as phase (ancilla |->)
psi = Hn @ psi                                 # final Hadamards
y = int(np.argmax(np.abs(psi)))
print(f"recovered a = {y:04b}   expected a = {a:04b}   exact: {y == a}")
```

Note the shortcut: with the ancilla tracked analytically as |−⟩, the oracle *is* the diagonal phase `(−1)^{f(x)}` — no 2n-dimensional simulation needed. `Hn` built from kroneckered 2×2 blocks is the Walsh–Hadamard transform, not the FFT; for `f(x) = a·x` over the *bitwise* inner product they differ.

## 22. Simon's Algorithm

> [!levels] Five levels of this chapter
> - **Intuition —** find the secret period s of a 2-to-1 function; interference leaves exactly the strings orthogonal to s.
> - **Mathematics —** each measurement yields y with y·s = 0 (mod 2); n−1 independent samples determine s by linear algebra over GF(2).
> - **Implementation —** a full 6-qubit simulation plus Gaussian elimination over GF(2).
> - **Engineering —** the oracle must genuinely be 2-to-1; post-processing is trivial; noise smears the orthogonality structure.
> - **Research —** abelian hidden subgroup problems are solved; nonabelian ones (graph isomorphism) have resisted 30 years of attack.

### 22.1 The hidden-period problem

Simon (1994) defined the problem that finally made exponential separation concrete. Given a black box f: {0,1}ⁿ → {0,1}ⁿ promised to be **2-to-1 with a hidden period s ≠ 0** — meaning f(x) = f(y) if and only if y = x ⊕ s — find s. There is no promise of linearity, balance, or anything else; the entire input space is paired up by XOR with s. Classically this looks hard: to find s you essentially need to *find a collision*, two inputs mapping to the same value.

### 22.2 Why the problem matters

Three reasons. **The separation is exponential against bounded-error classical algorithms**: finding a collision among 2ⁿ values needs Θ(2^{n/2}) queries by the birthday bound, and matching lower bounds hold — versus O(n) quantum queries. **The historical trigger**: Simon's preprint reached Peter Shor in 1994 and directly became the template for factoring; without Simon there is a good chance Shor's algorithm is discovered a decade later. **The template**: Simon is the first instance of the *hidden subgroup problem* — recover the subgroup H from a function constant and distinct on cosets of H — and its solution pattern (superposition, oracle, Fourier sampling, classical algebra) is exactly Shor's pattern.

### 22.3 Quantum interference

Prepare the uniform superposition, query the oracle, and the input register entangles into pairs: `(1/√2ⁿ)·Σ_x |x⟩|f(x)⟩ = (1/√2ⁿ)·Σ_c (|c⟩ + |c⊕s⟩)|f(c)⟩`. Apply H^{⊗n} to the input register. The amplitude of outcome y carries the factor `1 + (−1)^{s·y}` — the two terms of each pair interfere constructively when `s·y = 0` (mod 2) and cancel completely otherwise. So the measurement distribution is *uniform over the subspace* {y : y·s = 0}, a set of size 2^{n−1}, and zero outside it. One query has converted the hidden period into a system of linear equations over GF(2) — each sampled y is one equation `s·y = 0`.

### 22.4 Linear algebra extraction

Collect outcomes y₁, …, y_k; each satisfies `s·yᵢ = 0` (mod 2). Stack them into a k×n bit matrix and solve for the kernel by Gaussian elimination over GF(2) — XOR swaps and row XORs, arithmetic mod 2. When the collected equations have rank n−1, the kernel is exactly {0, s} and s is recovered. Drawing n−1 samples gives full rank with probability Π_{j=1}^{n−1}(1−2^{−j}) ≈ 0.29; drawing a few extra samples pushes it near 1, so batch-and-repeat is the standard strategy. Total: O(n) oracle queries, O(n³) classical post-processing — against Θ(2^{n/2}) classical queries. The post-processing is the part you should implement carefully; it is where most homemade Simon implementations fail.

### 22.5 Implementation

The full quantum step, honestly simulated for n = 3 (a 6-qubit state vector, 64 amplitudes):

```python
import numpy as np
from functools import reduce
rng = np.random.default_rng(7)
n, s = 3, 0b101                              # hidden string s = 101
lab = rng.permutation(2 ** n)                # random value per pair {x, x^s}
f = np.array([lab[min(x, x ^ s)] for x in range(2 ** n)])
H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
Hn = reduce(np.kron, [H] * n)                # H on the input register
psi = np.zeros(2 ** (2 * n), dtype=complex)
for x in range(2 ** n):
    psi[(x << n) | f[x]] = 1                 # |x>|f(x)> after the oracle
psi = np.kron(Hn, np.eye(2 ** n)) @ psi      # final H on the input register
p = (np.abs(psi.reshape(2 ** n, 2 ** n)) ** 2).sum(axis=1)
sup = np.where(p > 1e-12)[0]
print("support:", sup)
print("all satisfy y·s = 0:",
      all(bin(y & s).count("1") % 2 == 0 for y in sup))
```

Run it: the support is {0, 2, 5, 7} and every element satisfies `y·s = 0` — the interference claim of 22.3, verified numerically rather than trusted.

> [!experiment] On your laptop — the classical half of Simon
> Sample outcomes from the support above and recover s by GF(2) elimination — the part that makes Simon an *algorithm* and not just an interference curiosity:

```python
import numpy as np
Y = np.array([[0, 0, 0], [0, 1, 0], [1, 0, 1], [1, 1, 1]])  # sampled y's (y·s = 0)
n = 3
M, piv, r = Y.copy() % 2, [], 0
for c in range(n):
    pr = next((i for i in range(r, len(M)) if M[i, c]), None)
    if pr is None:
        continue
    M[[r, pr]] = M[[pr, r]]
    for i in range(len(M)):
        if i != r and M[i, c]:
            M[i] = (M[i] + M[r]) % 2
    piv.append(c); r += 1
basis = []
for c in range(n):
    if c not in piv:                          # free column -> kernel vector
        v = np.zeros(n, dtype=int); v[c] = 1
        for i, pc in enumerate(piv):
            if M[i, c]:
                v[pc] = 1
        basis.append(v)
print(basis)    # [array([1, 0, 1])]  ->  s = 101
```

> Replace the sampled rows with fresh draws from the distribution in 22.5 and watch the rank climb toward n−1; with only n−1 samples the batch fails about 71% of the time — repeat the batch.

### 22.6 Connection to Shor

Frame both algorithms as the **hidden subgroup problem**: given f constant and distinct on cosets of a hidden subgroup H, find H. Simon solves it for H = {0, s} in the group (Z₂)ⁿ; Fourier sampling over (Z₂)ⁿ is Hadamard sampling, and the classical step is linear algebra. Shor solves it for H = rZ (multiples of the order r) in the group of integers — Fourier sampling is the QFT over a cyclic group, and the classical step is continued fractions. Same skeleton: superposition, one oracle family, Fourier sampling, algebra. Simon's algorithm appeared in October 1994; Shor's, built on its spine, weeks later.

> [!research] The hidden subgroup problem
> The abelian case is solved (Simon, Shor, Kitaev), and that is essentially where it ends. For nonabelian groups — most famously the symmetric group, where a quantum solution would yield a subexponential algorithm for **graph isomorphism** — Fourier sampling provably fails to be sufficient, and no replacement technique is known. Thirty years of work have produced partial results and strong evidence that the nonabelian HSP needs genuinely new ideas. Any honest claim that "quantum computers break graph isomorphism" should be measured against this open problem.

## 23. Quantum Fourier Transform

> [!levels] Five levels of this chapter
> - **Intuition —** the quantum DFT: rewrites amplitudes in the frequency basis, so periodic states collapse onto a few sharp peaks.
> - **Mathematics —** `QFT_N|j⟩ = (1/√N)·Σ_k e^{2πi jk/N}|k⟩`; a unitary built from n Hadamards, n(n+1)/2 controlled rotations, and a swap network.
> - **Implementation —** build the matrix, check unitarity, compare against numpy's FFT; then simulate the textbook circuit.
> - **Engineering —** small-angle controlled rotations dominate the cost; the approximate QFT trades them away for O(n log n) depth.
> - **Research —** exact and approximate rotation synthesis over Clifford+T, and semiclassical (qubit-by-qubit) QFT variants.

### 23.1 The classical Fourier transform

The Fourier transform decomposes a signal into frequencies: given N samples, it reports the amplitude and phase of each of the N possible periodic components. After Cooley and Tukey's 1965 FFT, it costs O(N log N) — the most-used algorithm in numerical software, from audio codecs to solving PDEs to multiplying integers. The property that matters for this part: a sequence with period r has a Fourier transform concentrated near multiples of N/r. Peaks in the frequency domain reveal periods in the data. Hold that thought; it is the entire bridge to Shor's algorithm.

### 23.2 The discrete Fourier transform

Formally, the DFT of a vector v of length N is `V_k = Σ_j v_j·e^{−2πi jk/N}`, equivalently the matrix-vector product `V = F·v` with `F_{kj} = ω^{kj}`, ω = e^{−2πi/N}. Normalize F by 1/√N and it is unitary — a change of basis between the "position" basis and the "frequency" basis. Two properties carry over to the quantum setting: unitarity (the transform is reversible) and the convolution theorem (periodic structure maps to sparse support). The one property that does *not* carry over: classically you read all N outputs; quantum mechanically you get one sample of the transformed amplitudes.

### 23.3 The quantum Fourier transform

Apply that unitary to a quantum state: `QFT_N|j⟩ = (1/√N)·Σ_{k=0}^{N−1} e^{2πi jk/N}|k⟩`, extended linearly to arbitrary states — it is the DFT matrix acting on amplitudes. On a computational basis state |j⟩ the output is a uniform superposition whose *phases* encode j; on a state with periodic amplitudes, the output concentrates where the classical DFT would. The caveats are the fine print of the entire chapter: the input must already *be* a quantum state (loading classical data is often the real cost, 50.6), and the output must be *sampled*, not read — one measurement, not a table of N numbers. QFT is powerful exactly when you want one sample of a sharply peaked distribution.

### 23.4 Circuit decomposition

No black-box N×N matrix is applied; the QFT decomposes into O(n²) one- and two-qubit gates. For n = 3 (q0 = most significant bit of j):

```text
H on q0; controlled-R2 between q0,q1; controlled-R3 between q0,q2;
H on q1; controlled-R2 between q1,q2; H on q2;  then SWAP(q0,q2)

q0: |j1> ──H────●────●────────────────
                │    │
q1: |j2> ───────R2───●────H────●──────
                     │         │
q2: |j3> ────────────R3────────R2──H──
```

The controlled-Rk gates are diagonal (they only phase the |11⟩ branch), so their control/target labels are conventional. The final swaps reverse the qubit order — the circuit naturally produces the bit-reversed output, and implementations either insert swaps or track the relabeling. General n: H, then controlled rotations from every later qubit, per qubit.

### 23.5 Controlled rotations

The workhorse is `Rk = diag(1, e^{2πi/2^k})` — a phase rotation by 2π/2^k, so each successive k *halves* the angle. Between the H on qubit i and the next, qubit i collects controlled rotations R2, R3, … from all lower-order qubits: the accumulated phase on the |1⟩ branch becomes e^{2πi·0.jᵢjᵢ₊₁…}, the binary fraction of j starting at position i. Total count: n Hadamards, n(n+1)/2 controlled rotations, ⌊n/2⌋ swaps — O(n²) gates, all diagonal except the Hadamards. On hardware each controlled rotation is a native two-qubit interaction (or an approximated sequence — synthesis over Clifford+T costs O(log(1/ε)) T gates per rotation), which is why QFT-heavy circuits are rotation-count-bound.

### 23.6 Approximate QFT

The rotations with small k have tiny angles — R20 rotates by less than a milliradian. Drop all controlled-Rk with k > m: each discarded phase is at most 2π/2^{m+1}, and with at most n² drops the worst-case accumulated phase error is about πn²/2^{m+1}. Choosing m ≈ log₂(n²/ε) bounds the error by ε while cutting the gate count from O(n²) to O(n log n). On error-corrected hardware rotations cost real T-gates, so the approximate QFT is what serious Shor/QPE implementations actually compile to. The lesson generalizes: high-precision phases are the first place to spend accuracy budget — and the first place to reclaim it.

### 23.7 Complexity

The honest comparison. Classical FFT: O(N log N) = O(n·2ⁿ) arithmetic operations on a vector of N = 2ⁿ numbers you already hold in memory. Quantum QFT: O(n²) gates — exponentially fewer *gates* — but on a state that (a) took something else to prepare and (b) yields one sample, not N coefficients. If your task is "transform this array of data", the FFT wins, permanently. If your task is "I have a quantum state with periodic structure and I want to sample its frequency content", the QFT is essentially free. Every claimed QFT speedup must state which side of that line it lives on — the same discipline as 1.9.

### 23.8 Applications

Four, in increasing depth. **Period finding**: Simon-style and Shor-style — a periodic state goes in, a peak comes out (26.6). **Phase estimation**: the inverse QFT is the readout of QPE, the workhorse of chemistry and of Shor itself (24). **Arithmetic**: the Draper QFT adder performs addition by phase accumulation, and QFT-based multiplication underlies several modular-arithmetic pipelines. **Fourier sampling** as a primitive: any hidden-subgroup-flavored problem starts here. Notice the pattern: the QFT is never the algorithm; it is the readout layer of an algorithm whose real work happens in state preparation and in the classical post-processing.

> [!experiment] On your laptop — QFT matrix versus numpy FFT
> Build the QFT matrix, check unitarity, and verify it matches numpy's FFT (up to normalization and exponent sign — numpy's `fft` uses e^{−2πi…}, `ifft` uses e^{+2πi…}):

```python
import numpy as np
n, N = 3, 8
j = np.arange(N)
F = np.exp(2j * np.pi * np.outer(j, j) / N) / np.sqrt(N)   # QFT matrix
print("unitary:", np.allclose(F @ F.conj().T, np.eye(N)))  # True
v = np.array([1, 1, 0, 0, 0, 0, 0, 0], dtype=complex)      # |0> + |1>
print("matches np.fft.ifft * sqrt(N):",
      np.allclose(F @ v, np.sqrt(N) * np.fft.ifft(v)))     # True
```

> Then feed it a periodic amplitude vector — ones every 2 positions — and print `|F@v|`: the output concentrates on multiples of N/r = 4. That peak is the phenomenon Shor's algorithm exploits.

## 24. Phase Estimation

> [!levels] Five levels of this chapter
> - **Intuition —** let the eigenphase wind a clock up by powers of two, then read the clock with an inverse QFT.
> - **Mathematics —** controlled-U^{2^k} writes e^{2πi·2^k·φ} into a counting register; QFT† concentrates it on the integer nearest 2^t·φ.
> - **Implementation —** a numpy simulation recovering an 8-bit eigenphase in one shot.
> - **Engineering —** cost = t controlled applications of U; precision t = m + ⌈log₂(2+1/(2ε))⌉; U is always the hard part.
> - **Research —** ground-state preparation is the real bottleneck; iterative and semiclassical QPE trade qubits for coherence time.

### 24.1 Eigenvalues

Phase estimation solves: given a unitary U and an eigenvector |u⟩, estimate the eigenvalue. Because U is unitary, all eigenvalues lie on the unit circle — `U|u⟩ = λ|u⟩` with |λ| = 1 — so every eigenvalue is `λ = e^{2πiφ}` for some phase φ ∈ [0, 1). Estimating λ is therefore estimating one real number φ, a fraction of a full turn. The restriction to unitary operators is not a limitation in practice: any Hermitian operator H can be exponentiated, `e^{−iHt}` is unitary, and its phases carry H's eigenvalues — that is exactly how chemistry applications reach Hamiltonians.

### 24.2 Eigenphases

The phase φ is where the physics and the algorithms live. In chemistry, `e^{−iHt}` has eigenphase φ = −E·t/(2π) for energy E, so a phase estimate at known evolution time t yields E. In Shor's algorithm, the multiplication-by-a map on the period states has eigenphases s/r — rational, with the order r in the denominator, which is why continued fractions can dig r back out. Eigenphases are also what interferometers measure in quantum metrology, where QPE is the algorithmic version of the phase readout. In every case the same bookkeeping: phases are fractions of a turn, and turns are countable.

### 24.3 Controlled unitaries

The circuit needs, for each counting qubit k, a controlled application of `U^{2^k}`. The powers are built by **repeated squaring**: U² = U·U, U⁴ = (U²)², and so on — so U^{2^k} costs one extra "squaring" beyond U^{2^{k−1}}, and for structured U (like modular multiplication) the whole family shares work. The counting register holds t qubits, each controlling one power; the eigenstate register holds |u⟩ throughout. In Shor's algorithm this block — modular exponentiation — is essentially the entire circuit cost: O(n³) gates naively, O(n²·polylog n) with fast multiplication. Everything else in QPE is cheap.

### 24.4 The inverse QFT

After the controlled powers, the counting register holds `(1/√2^t)·Σ_k e^{2πi·k·φ}|k⟩` — exactly the state whose QFT is a single peak at 2^t·φ. Apply the inverse QFT to the counting register and measure it:

```text
counting:    |0>^t ──H^⊗t───●────────●────⋯────●───[QFT†]───measure: m ≈ 2^t·φ
                           │        │         │
eigenstate:   |u⟩ ─────────U^(2^0)──U^(2^1)──⋯──U^(2^(t-1))──    U|u⟩ = e^{2πiφ}|u⟩
```

If φ is exactly k/2^t for some integer k, the outcome is k with certainty. If not — the realistic case — the probability concentrates on the nearest integers to 2^t·φ, with tails described by 24.5. One measurement of t bits buys m ≈ t bits of the phase.

### 24.5 Precision

The standard bound: to obtain φ accurate to 2^{−m} with probability at least 1−ε, use `t = m + ⌈log₂(2 + 1/(2ε))⌉` counting qubits — the O(log(1/ε)) extra qubits suppress the tails of the peak. When φ is exactly representable in t bits, success probability is 1; when not, each shot lands on the nearest integer with probability ≈ 4/π² in the worst case (offset by half a bin), and a few shots with majority vote fix it. Alternatively spend shots instead of qubits: repeat the estimation and take the median. Precision, as always, is a budget line — you choose where to pay.

### 24.6 Resource requirements

Count for a t-qubit, m-bit estimate: t counting qubits plus the eigenstate register; t applications of controlled `U^{2^k}`, which share structure so the total is close to t times the cost of one U; an inverse QFT, O(t²) gates, negligible; and O(1/ε) repetitions if you spend shots rather than qubits. The dominant line item is always U. In Shor, U is modular multiplication (24.3). In chemistry, U is `e^{−iHΔt}` Trotterized, with hundreds to millions of Pauli rotations per step, and the real bottleneck is not U but *preparing an overlap-1 eigenvector* — bad state preparation costs you repetitions proportional to 1/|⟨ψ|u⟩|². Plan resources around the eigenvector, not the QFT.

### 24.7 Applications

**Order finding** (Shor, 26): estimate the eigenphase s/r of a modular-multiplication unitary, recover r by continued fractions. **Chemistry**: ground- and excited-state energies from `e^{−iHt}` — the most-cited path to useful quantum advantage, gated on state preparation. **Quantum metrology**: QPE is the optimal phase readout, reaching the Heisenberg limit 1/t rather than the standard quantum limit 1/√t. **Linear algebra**: eigenvalue estimation is the core of HHL-type algorithms for linear systems. **Quantum counting**: run QPE on the Grover operator to *count* marked items (25.6). A primitive this reusable is what "engineering-grade" means in algorithm design.

> [!experiment] On your laptop — an 8-bit phase estimate
> Simulate the whole QPE pipeline for U = diag(1, e^{2πi·φ}) with φ = 0.685 — not on the 8-bit grid, so you will see realistic rounding:

```python
import numpy as np
t, phi = 8, 0.685
T = 2 ** t
k = np.arange(T)
cnt = np.exp(2j * np.pi * k * phi) / np.sqrt(T)           # after U^(2^k) chain
F = np.exp(2j * np.pi * np.outer(k, k) / T) / np.sqrt(T)  # QFT matrix
p = np.abs(np.conj(F) @ cnt) ** 2                          # inverse QFT, Born rule
top = np.argsort(p)[::-1][:2]
print([(m, round(p[m], 3)) for m in top], "-> phi ≈", top[0] / T)
```

> Expect roughly 64% on 175 and 20% on 176 — the nearest integer to 2⁸·0.685 = 175.36 wins but does not dominate. Raise t to 12 and watch the estimate sharpen; that is 24.5's rule working.

## 25. Grover's Algorithm

> [!levels] Five levels of this chapter
> - **Intuition —** each iteration rotates the state 2θ toward the marked item; about π/4·√N rotations suffice.
> - **Mathematics —** G = (2|s⟩⟨s| − I)·O is a rotation by 2θ in a plane, sinθ = √(M/N); success after k iterations is sin²((2k+1)θ).
> - **Implementation —** two reflection matrices and a loop; watch N=16 peak at 96% after 3 iterations and then collapse.
> - **Engineering —** depth ≈ √N iterations; the noise budget (per-gate error × total gates ≪ 1) is what kills uncorrected Grover.
> - **Research —** optimality is proven (BBBV); fixed-point and unknown-M variants, and where √N actually beats classical heuristics, stay live.

### 25.1 Unstructured search

The problem: given a boolean predicate P on N = 2ⁿ items with the promise that M items satisfy it, find one — with P available only as a black box. "Unstructured" is the operative word: no ordering, no gradient, no locality to exploit; the only operation is "test item x". This is the right model for inverting hash functions, for search spaces where checking is cheap but constructing is impossible, and as the worst-case backbone for constraint satisfaction. It is deliberately the *most pessimistic* model of search — which is what makes the quadratic speedup credible: if you cannot beat √N here, no cleverness was assumed anywhere.

### 25.2 Classical complexity

Classically, testing items one at a time needs, on average, N/2 queries to find a marked item (N in the worst case), and no classical algorithm does better — for unstructured search the birthday-style tricks do not apply because the answers are independent bits. Grover (1996) needs Θ(√N) quantum queries, and Bennett–Bernstein–Brassard–Vazirani (1997) proved that is *optimal*: no quantum algorithm beats the quadratic factor for black-box search. Two consequences worth internalizing: the speedup is quadratic, never exponential — a 128-bit key loses to Grover like a 64-bit key to classical brute force — and NP-complete problems inherit only this quadratic improvement (Part VIII).

### 25.3 The oracle

The black box enters as a **phase oracle**: `O|x⟩ = (−1)^{P(x)}|x⟩` — flip the sign of marked states, leave the rest. Realizing it from a classical circuit for P is mechanical: compute P(x) into an ancilla and uncompute, with the ancilla prepared in |−⟩ so the CNOTs kick back phases (21.2). That construction costs one application of the predicate circuit per oracle call — and this is Grover's hidden constant: for a hard predicate (a full SAT instance, say) the oracle is the size of the whole problem, evaluated once per iteration, √N times. Budget it before believing any "Grover solves X" claim.

### 25.4 Phase inversion

The oracle is a reflection. For M = 1 it is `O = I − 2|w⟩⟨w|`: geometrically, every amplitude component along |w⟩ flips sign while the orthogonal complement is untouched — a mirror through the plane orthogonal to the marked state. For M marked items it is `I − 2·Σ_w|w⟩⟨w|`. Reflections are unitary and their composition is a rotation — the fact the whole algorithm rides on. A useful sanity check: the oracle alone does nothing measurable (a global-sign-visible operation applied to a real superposition changes only phases), which is exactly why a second operation is needed before anything can be read out.

### 25.5 The diffusion operator

The second reflection is `D = 2|s⟩⟨s| − I`, where |s⟩ is the uniform superposition — **inversion about the mean**: every amplitude aᵢ becomes 2μ − aᵢ (μ = average amplitude), so below-average amplitudes (marked items, just sign-flipped) end up further above the mean. Implementation: `D = H^{⊗n}·(2|0⟩⟨0| − I)·H^{⊗n}`, and the middle piece is a phase flip on |0…0⟩ built from X gates and a multi-controlled Z with the ancilla trick — O(n) gates. One Grover iteration is `G = D·O`: reflect about |w⟩'s orthogonal complement, then about |s⟩.

```text
one iteration G = D·O:

|x> ──O───H^⊗n───●───H^⊗n──      O: flip sign of marked |w>
                 Z               middle: phase flip on |0…0>
```

### 25.6 Amplitude amplification

Grover generalizes beyond uniform starts: given any preparation A with `A|0⟩ = |ψ⟩` succeeding (having overlap √p with good states) with probability p, the operator `Q = (2|ψ⟩⟨ψ| − I)·A·O·A†` amplifies success to ≈ 1 in O(1/√p) applications — versus O(1/p) classical repetitions. This is **amplitude amplification** (Brassard–Høyer–Mosca–Tapp), and it converts *any* probabilistic algorithm's success probability into a quadratic gain: Monte Carlo estimation becomes amplitude estimation (QPE on Q, 24.7), backtracking search gets walk-based speedups. When M is unknown, QPE on G doubles as a counter — quantum counting — and BBHT's randomized schedules replace the fixed iteration count. Grover is the name; amplitude amplification is the technology.

### 25.7 Geometric interpretation

Everything above happens in a plane. Write the state as a component on the marked subspace and one on the rest: `|ψ⟩ = sin(θ)|w⟩ + cos(θ)|r⟩` with `sinθ = √(M/N)`. The starting uniform state sits at angle θ; each Grover iteration rotates by exactly 2θ toward |w⟩; success probability after k iterations is `sin²((2k+1)θ)`.

```text
state plane spanned by |r> (unmarked) and |w> (marked):

start:   |s> = cosθ·|r> + sinθ·|w>          angle θ above |r>
each G:  rotate by 2θ toward |w>
after k: angle (2k+1)θ,  P(success) = sin²((2k+1)θ)
stop at k ≈ π/(4θ):  angle ≈ π/2  →  all amplitude on |w>
```

Search as a rotation problem: the oracle tilts, the diffusion turns, and you stop when the rotation has swept the amplitude onto the answer. Overshooting keeps rotating — past π/2 the success probability falls again.

### 25.8 The optimal iteration count

Set `(2k+1)θ ≈ π/2`: the optimum is `k* ≈ π/(4θ) − 1/2 ≈ (π/4)·√(N/M)` iterations for M ≪ N. For N = 16, M = 1: θ = arcsin(1/4) ≈ 0.2527, so k* ≈ 2.6 — three iterations give sin²(7θ) ≈ 96%. Past the optimum the sine keeps oscillating: 4 iterations drop to ≈ 58%, 5 to ≈ 13%. Two boundary facts: if M = N/2, θ = π/4 and there is no speedup at all (one iteration, 50% — you could have guessed); and the √(N/M) scaling means knowing M matters, hence quantum counting or BBHT schedules when it is unknown. Grover is a precise timing problem, not an iterative refinement.

> [!experiment] On your laptop — Grover at N = 16
> Two reflections, one loop. Watch the probability climb, peak, and collapse:

```python
import numpy as np
n, N = 4, 16
w = 0b1010                                   # marked item
s = np.ones(N, dtype=complex) / np.sqrt(N)   # uniform start
O = np.eye(N); O[w, w] = -1                  # oracle: phase inversion
D = 2 * np.outer(s, s) - np.eye(N)           # diffusion: inversion about mean
for k in range(6):
    print(f"k={k}  P(find)={abs(s[w])**2:.3f}")
    s = D @ O @ s
```

> Output: 0.062, 0.473, 0.907, 0.962, 0.581, 0.126. The peak at k = 3 matches sin²(7θ); iterating "a few more times for safety" actively destroys the answer — the most common bug in first implementations.

### 25.9 Noise sensitivity

Count the exposure: one iteration costs the oracle plus O(n) gates; √N iterations means roughly 4n·√N gate applications total. At a physical error rate p per gate, the failure budget 4n·√N·p must stay well below 1. For n = 20 (N ≈ 10⁶): 4·20·1024·10⁻³ ≈ 82 — five orders of magnitude over budget at p = 10⁻³. The quadratic speedup hurts twice: more iterations means more accumulated noise, and the narrow sin² peak means angle errors (over/under-rotation from imperfect gates) shift the optimum. This is why Grover on today's hardware is a 3-to-6-qubit demonstration, and why the fault-tolerant crossover is a genuine engineering milestone, not a formality.

### 25.10 Practical implementation

Rules of thumb from the people who run this. First, exploit classical structure before reaching for Grover — real SAT solvers beat √(2ⁿ) on real instances; Grover is the worst-case guarantee, not the average-case winner. Second, when you do run it, the oracle dominates: co-design the predicate circuit with the diffusion (cancel adjacent H layers, merge rotations, 46.8). Third, prefer amplitude-amplification framings with known p — they compose into larger algorithms. Fourth, if M is unknown, count first (24.7). Fifth, for composability use fixed-point search (Yoder–Low–Chuang), which cannot overshoot, at a modest constant-factor cost. Hardware demonstrations today: a handful of qubits, meaningful as system benchmarks — not as search.

## 26. Shor's Algorithm

> [!levels] Five levels of this chapter
> - **Intuition —** factoring reduces to period finding, and quantum interference finds periods of 2ⁿ-sized tables in one shot.
> - **Mathematics —** QFT over Q ≈ N² samples y ≈ k·Q/r; continued fractions recover r; gcd(a^{r/2} ± 1, N) splits N.
> - **Implementation —** a complete toy run at N = 15, a = 7: table, simulation, continued fractions, factors 3 and 5.
> - **Engineering —** modular exponentiation is ≈ 99% of the circuit; RSA-2048 estimates run ~10⁶ noisy qubits — still 3 orders past hardware.
> - **Research —** arithmetic-circuit optimization drives the resource counts; post-quantum migration is the societal deadline.

### 26.1 Integer factorization

Given an odd composite N, find a nontrivial factor (then recurse). This is the problem behind RSA: multiplying two large primes is instant, factoring the product is (as far as anyone knows) hard, and every internet key exchange of the last four decades has bet on that asymmetry. Shor's 1994 algorithm factors N in polynomial time — O(n³)-class gates for n-bit N on a quantum computer — and remains the single most consequential result in the field: it converted quantum computing from a curiosity into a cryptographic deadline. Note what Shor does *not* do: it does not search for factors; it finds periods, and factors fall out.

### 26.2 Classical difficulty

The best classical algorithm, the general number field sieve, runs in `exp(((64/9)^{1/3} + o(1))·(ln N)^{1/3}·(ln ln N)^{2/3})` — subexponential, superpolynomial. RSA-2048 sits beyond it by an enormous margin (records: RSA-250 in 2020 took ~2700 core-years). No polynomial classical factoring algorithm is known despite centuries of work, which is why the problem is a trustworthy hardness assumption — and why Shor's polynomial-time quantum algorithm is a genuine complexity-theoretic event, not an incremental speedup. The number-theoretic detour through *periods* is what makes it work: factoring and period finding are, it turns out, the same problem wearing different clothes.

### 26.3 Modular arithmetic

Pick a random a with `gcd(a, N) = 1` (if the gcd is bigger, you already found a factor — lucky draw). Work in the multiplicative group Z*_N of residues coprime to N, which has size φ(N) (Euler's totient). By Lagrange's theorem, every element has a finite **order**: the smallest r with `a^r ≡ 1 (mod N)`, and r divides φ(N). The powers `a^0, a^1, a^2, …` therefore cycle with period r. For N = pq with distinct odd primes, a random a has even order with a^{r/2} ≢ −1 (mod N) with probability ≥ 1/2 — the condition that makes the final gcd step split N.

### 26.4 Period finding

The reduction: if you can find the order r of a random a mod N, you can factor. When r is even and `a^{r/2} ≢ −1 (mod N)`, write `x = a^{r/2}`; then x² ≡ 1 (mod N) while x ≢ ±1, so N divides x²−1 = (x−1)(x+1) without dividing either factor — and `gcd(x−1, N)` and `gcd(x+1, N)` are nontrivial factors. Classically, finding r means computing powers until one hits 1: O(r) ≤ O(N) multiplications, or O(√r) with baby-step giant-step. For RSA-scale N, r is astronomically large — period finding is the exponential wall, and it is exactly the wall the QFT dismantles.

### 26.5 Quantum period finding

The quantum core. Choose Q = 2^t with N² ≤ Q < 2N² (t ≈ 2n+1). Prepare `(1/√Q)·Σ_{x=0}^{Q−1}|x⟩|1⟩`, and apply the modular-exponentiation unitary `|x⟩|y⟩ ↦ |x⟩|y·a^x mod N⟩` — built from repeated squaring along the binary digits of x, the O(n³)-gate behemoth:

```text
reg 1 (t ≈ 2n qubits):  |0> ──H^⊗t────────[QFT over Q]──measure y
                                  │
reg 2 (n qubits):       |1> ──────U_pow──          U_pow: |y> ↦ |y·a^x mod N>
```

Now register 2 holds `a^x mod N` — periodic with period r — entangled with register 1. The entanglement is the point: register 1 is a coherent superposition of all x, tagged by the period structure of their images.

### 26.6 QFT connection

Apply the QFT over Q to register 1. The periodic train in the entangled state diffracts: amplitude concentrates on integers y with `|y/Q − k/r| ≤ 1/(2Q)` for some k — multiples of Q/r, up to rounding. Measure: y/Q is a fraction within 1/(2Q) of k/r. Now the classical step — the **continued fraction** expansion of y/Q with denominators bounded by N recovers k/r whenever gcd(k, r) = 1, which happens for a constant fraction of shots (the peaks carry probability ≥ 4/π²·φ(r)/r in total). Verify `a^r ≡ 1 (mod N)`; if verification fails (you caught r/gcd(k,r), or an odd r), resample — a constant expected number of rounds. This is Simon's skeleton with (Z, +) in place of (Z₂)ⁿ.

### 26.7 The complete algorithm

Everything assembled — the quantum part is one boxed line:

```python
import math, random

def shor(N):                                   # classical driver
    if N % 2 == 0:
        return 2
    while True:
        a = random.randrange(2, N - 1)
        g = math.gcd(a, N)
        if g > 1:
            return g                           # lucky draw: factor for free
        r = quantum_order(a, N)                # QFT period finding (26.5-26.6)
        if r % 2 != 0:
            continue                           # odd order: retry with new a
        x = pow(a, r // 2, N)
        if x == N - 1:
            continue                           # a^(r/2) = -1: retry
        f1, f2 = math.gcd(x - 1, N), math.gcd(x + 1, N)
        if 1 < f1 < N:
            return f1                          # recurse on f1 and N // f1
```

`quantum_order(a, N)` runs the 26.5–26.6 circuit a constant number of times. Total cost: O(n³) gates naively (O(n²·polylog n) with fast arithmetic), O(1) expected repetitions — each repetition factors N with probability ≥ 1/2.

### 26.8 Toy implementation

N = 15, a = 7 — the standard end-to-end example. The powers cycle with period 4; the toy uses Q = 16 (smaller than the required Q ≥ N², but exact here because r = 4 divides 16):

```text
x          : 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
7^x mod 15 : 1  7  4 13  1  7  4 13  1  7  4 13  1  7  4 13
                                             └── period r = 4 ──┘

QFT over Q = 16 → peaks at y ∈ {0, 4, 8, 12}   (each with probability 1/4)
y/Q = 4/16, 8/16, 12/16 = 1/4, 1/2, 3/4  →  continued fractions → r = 4
7^(r/2) = 7^2 = 49 ≡ 4 (mod 15), 4 ≢ −1 ≡ 14  →  condition satisfied
gcd(4 − 1, 15) = 3   and   gcd(4 + 1, 15) = 5   →   15 = 3 × 5
```

And the full simulation — oracle, QFT, measurement, continued fractions, gcd:

```python
import numpy as np
from fractions import Fraction
rng = np.random.default_rng(3)
N, a, Q = 15, 7, 16
f = np.array([pow(a, x, N) for x in range(Q)])        # 7^x mod 15
psi = np.zeros(Q * N, dtype=complex)
for x in range(Q):
    psi[x * N + f[x]] = 1                             # |x>|a^x mod N>
H = np.exp(2j * np.pi * np.outer(np.arange(Q), np.arange(Q)) / Q) / np.sqrt(Q)
psi = np.kron(H, np.eye(N)) @ psi                     # QFT over Q on register 1
p = (np.abs(psi.reshape(Q, N)) ** 2).sum(axis=1)
y = rng.choice(Q, p=p)                                # measure register 1
r = Fraction(y, Q).limit_denominator(N).denominator   # continued fractions
print("y =", y, " r candidate =", r)
if r % 2 == 0 and pow(a, r, N) == 1:
    print("factors:", np.gcd(pow(a, r // 2, N) - 1, N), np.gcd(pow(a, r // 2, N) + 1, N))
else:
    print("unusable shot (y=0 or k shares a factor with r) — rerun")
```

The `else` branch is not decoration: y = 0 (probability ¼) and y = 8 (which yields 1/2, i.e. r/gcd(k,r) = 2) both land there, exactly as 26.6 promised.

> [!experiment] On your laptop — the continued-fraction step
> `Fraction.limit_denominator` performs the continued-fraction recovery. Check it against all three useful shots of the toy run, including the collision case:

```python
from fractions import Fraction
for y in (4, 8, 12):                     # measured peaks, Q = 16, true r = 4
    fr = Fraction(y, 16).limit_denominator(15)
    print(f"{y}/16 -> {fr}   r-candidate = {fr.denominator}")
```

> You get 1/4 (r = 4, correct), 1/2 (k = 2 shares a factor with r = 4 — the collision), and 3/4 (r = 4). Always verify `pow(a, r, N) == 1` before trusting a recovered order; the classical post-processing is where the algorithm actually lives.

### 26.9 Resource requirements

Logical circuit: t ≈ 2n+1 counting qubits, n-qubit arithmetic registers, QFT O(n²) gates, and modular exponentiation dominating at O(n³) gates naively — O(n²·polylog n) with advanced multiplication circuits. End-to-end estimates for RSA-2048: Gidney–Ekerå (2019) — about 20 million noisy physical qubits running 8 hours; Gidney (2025) — under 1 million noisy qubits running under a week, thanks to better arithmetic and error-correction layouts. Both assume surface-code fault tolerance at physical error rates near 10⁻³. Against today's machines — hundreds to a few thousand physical qubits — the gap is roughly three orders of magnitude in qubit count. That is the honest planning horizon: reachable, but not imminent, engineering.

### 26.10 Implications for cryptography

Shor breaks RSA, finite-field Diffie–Hellman, and elliptic-curve cryptography once fault-tolerant machines at the 26.9 scale exist. Symmetric primitives survive: Grover costs only a factor of 2 in effective key length, so AES-256 remains sound. The operative threat is **harvest now, decrypt later** — adversaries recording encrypted traffic today to decrypt after a CRQC exists — which makes migration urgent for long-lived secrets. NIST standardized the replacements in 2024: ML-KEM (FIPS 203, lattices), ML-DSA (FIPS 204), SLH-DSA (FIPS 205, hash-based). The migration is a decade-scale program touching every protocol you have ever shipped — and, closer to home, it is where cryptanalysis careers meet quantum computing (51.9). The algorithm is 30 years old; its consequences are still being built.

> [!research] Factoring at cryptographic scale
> The open engineering problem is the constant factor in front of the polynomial: how many Toffoli and T gates, how many logical qubits, how many hours — for RSA-4096 and beyond. Every improvement in modular multiplication circuits, windowed exponentiation, approximate QFT, and surface-code layout shrinks the estimate; the 2019→2025 resource drop (20 million → under 1 million noisy qubits) shows how much headroom remains. On the theory side, no superpolynomial classical factoring algorithm is proven absent, and BQP's exact boundary — what else shares Shor's structure — is still being mapped.
