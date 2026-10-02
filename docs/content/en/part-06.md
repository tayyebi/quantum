# Part VI — Quantum Circuits

With the mental model (Part II), the mathematics (Part III), the physics (Part IV), and multi-qubit states (Part V) in place, we can finally speak the working language of the field: the quantum circuit. Circuits are to quantum computing what assembly is to classical machines — low-level, universal, and the lingua franca of every paper, SDK, and hardware manual. This part has three movements: the notation itself (Ch. 15), the practice of programming with it in Qiskit (Ch. 16), and the rite of passage every serious quantum engineer should complete — building a state-vector simulator from scratch (Ch. 17). Everything in Parts VII–XIII assumes fluency here.

## 15. The Circuit Model

> [!levels] In this chapter
> **Lv1** you learn to read a circuit diagram: wires, boxes, meter symbols. **Lv2** you learn the vocabulary of circuits — depth, gate count, connectivity, ancillas — the quantities resource estimates are written in. **Lv3** you can translate between a circuit picture, its unitary matrix, and code. **Lv4** you can design a circuit for a stated goal (a reversible function, a known unitary) and reason about its cost. **Lv5** you understand the circuit model's limits — why it is an abstraction over pulses and topological braids, and where research tries to replace it.

### 15.1 Circuit Notation

A quantum circuit is a left-to-right timeline. Horizontal lines are qubits; boxes on the lines are gates; time flows left to right; the right edge is always measurement. Two-qubit gates are drawn as a dot (control) connected by a vertical line to the gate (target). Barriers (`||`) forbid reordering; double lines after measurement carry classical bits. The notation is gloriously informal across papers — that is a feature to be aware of, not a bug: always reconstruct a paper's circuit from its accompanying matrix or code. Our parser (17.10) will accept a text form of this notation, so you will internalize it twice: visually and programmatically.

```text
q0 ──■────H──M
     │       ║
q1 ──X───────M
             ║
c0 ─────────╩═
c1 ───────────
```

### 15.2 Wires

A wire is a qubit's entire life: prepared, operated on, and measured. Wires are not physical wires — on superconducting chips a "wire" is a resonator-mediated coupling, on trapped ions it is the shared motional mode — but the abstraction is precise: a wire carries quantum state, and touching it is the only way to affect it. Two truths to internalize early. First, identity is not idleness: a wire with nothing on it still decoheres. Second, wires can be *swapped* logically (SWAP gate) at a cost, which is why connectivity (15.10) dominates real circuit costs.

### 15.3 Gates

Gates are unitary operators drawn as boxes. The standard table you must know cold: X (bit flip), Y, Z (phase flip), H (Hadamard, basis change), S, T (phase gates), RX/RY/RZ (rotations by angle θ), and the two-qubit CX/CZ plus SWAP. From Part V you know H, CX on |00⟩ makes entanglement; the circuit model packages that fact as a drawing. Gates do not exist physically — they are calibrations of shaped pulses (Part XI) — so "the same" gate on different hardware differs in fidelity and duration. Gate fidelity numbers (99.9% single, 99.5% two-qubit, best-in-class 2025) are the currency of every cost estimate in Part VII.

### 15.4 Measurements

Measurement is drawn as a meter (or an arc with an arrow) and is *not* a gate: it is non-unitary, irreversible, and it produces a classical bit. Mid-circuit measurement — measuring a qubit and continuing to use it — is supported on modern hardware and is the enabling primitive for QEC (Part X), teleportation, and dynamic circuits. Measure in bases other than Z by conjugating: H then measure is an X-basis readout. The measurement layer is where quantum meets classical control flow: `if c0: apply X` — real-time classical feedback — is the seed of every fault-tolerant protocol.

### 15.5 Initialization

Every wire starts somewhere, and the somewhere is |0⟩ — prepared by cooling qubits to their ground state (tens of millikelvin for superconducting, near-absolute-zero ions, room-temperature photons with caveats). Initialization fidelity is usually the best number on any hardware datasheet (99.99%), and it matters more than beginners assume: garbage in, garbage out, at exponential amplitude-blowup cost. Reset operations — mid-circuit returns to |0⟩ — exist in Qiskit and on hardware, enabling qubit reuse. Building |ψ⟩ states beyond |0⟩ is itself a circuit-design task: state preparation is a real cost (O(2ⁿ) gates in the general case) that naive resource estimates forget.

### 15.6 Circuit Execution

Executing a circuit means: initialize, apply gates in time order (in parallel where wires are independent), measure, repeat N times ("shots"), and histogram the outcomes. Between "circuit as written" and "circuit as executed" sits the whole compilation pipeline (Part XII): transpile to the backend's gate set, route around connectivity limits, schedule against decoherence. Execution on hardware is remote (cloud queues), slow (minutes per job), and noisy — which is why 90% of your work will use simulators, with hardware reserved for validating that your noise model isn't lying to you. Part VII's experiments follow exactly that discipline.

### 15.7 Circuit Depth

Depth is the length of the longest path through the circuit — the number of sequential time steps assuming unlimited parallelism. Depth × gate time ≈ how long the circuit runs, and since coherence is finite, *depth is the enemy*: T1/T2 budgets (tens to hundreds of microseconds for superconducting) cap the depth you can afford, which caps the algorithms you can run. Two circuits with identical gate counts can differ 10× in depth depending on scheduling. When papers quote complexity, they quote depth (usually in two-qubit gates); when you design circuits, you minimize it: parallelize, commute gates past each other, and let the compiler (Part XII) do the rest.

### 15.8 Gate Count

Gate count is total operations — usually reported separately for one-qubit and two-qubit gates, because two-qubit gates are 5–10× slower and noisier. Shor for RSA-2048: ~5 trillion Toffoli-class gates in early estimates, under 1 million with modern optimizations; Grover for AES-128: ~2⁶⁴ iterations (huge). Gate count is what algorithmic complexity theory actually counts; depth is what hardware cares about; the ratio depends on scheduling and connectivity. Learn to read resource-estimate papers with both eyes: "2⁹⁶ T gates" and "T factory + logical qubits" (Part X) tell you what machine the estimate assumes.

### 15.9 Qubit Count

How many wires does the problem need? Three numbers usually quoted: *data* qubits (the register), *ancilla* qubits (workspace, 15.11), and *physical-per-logical* overhead (100–1000+ in surface codes, Part X). IBM's Starling targets ~200 logical qubits from ~200,000 physical ones by 2029 — that overhead factor (~10³) is the single most important number in the field's roadmap, and it is why "we need a million qubits" headlines translate to "we need a few hundred useful ones." Resource estimates stack all three: algorithm qubits × overhead + routing + magic-state distillation. Practice reconstructing that arithmetic; it is how you read every roadmap announcement critically.

### 15.10 Connectivity

Real hardware has a coupling map: qubit i can entangle only with its neighbors (heavy-hex lattice for IBM, square lattices for Google, all-to-all within an ion trap). Algorithms assume all-to-all; hardware does not provide it; therefore *routing* — inserting SWAPs to move states next to their gates — is a major compiler pass (Part XII), and SWAP overhead can dominate circuit cost on sparse lattices. Depth 10 all-to-all can become depth 100 on heavy-hex. When choosing a backend, check its coupling map first; when reading a benchmark, ask what connectivity it assumed. Cloud backends in Qiskit expose this as `backend.coupling_map`.

### 15.11 Ancilla Qubits

Ancillas are workspace qubits: not the answer, but essential to the computation. Uses: computing a function reversibly (compute-copy-uncompute pattern, Ch. 18), phase kickback (Ch. 24), syndrome extraction in QEC (Part X), magic-state distillation, and qubit reuse (measure-and-reset). Clean ancillas — returned to |0⟩ after use — are a contract; leaving them entangled with your data register is a classic bug (your simulator's probabilities will look wrong in a way that's hard to diagnose). Distinguishing "data," "clean ancilla," and "dirty ancilla" in circuit comments is a habit worth starting now, before Part X makes it survival-critical.

### 15.12 Reversible Computation

Since all quantum gates are unitary, all quantum computation is reversible — so classical logic must be *compiled* into reversible form to run on a quantum computer. The recipe: compute f(x) into an ancilla with Toffoli networks (f AND-gates), then either measure the ancilla (phase oracle) or uncompute it back (phase-free). The overhead: one ancilla per AND, plus uncomputation, roughly 2× the classical gate count and +1 qubit per intermediate bit. Bennett's 1973 construction founded this field; today it is the bread-and-butter of oracle construction for Grover and of arithmetic for Shor (Ch. 26). You will build reversible adders in Chapter 17's project extension.

> [!experiment] Count what matters
> Take Qiskit's `qiskit.circuit.library` for a 4-bit adder. Transpile it to a fake backend with heavy-hex connectivity (`qiskit.providers.fake_provider.GenericBackendV2(7)`). Print the original vs. transpiled gate counts and depth. Then generate the coupling map drawing. You should see the gate count grow (SWAP insertion) and depth grow. Vary which physical qubits the circuit is placed on and watch the cost change. This 20-line experiment teaches connectivity economics better than any prose.

## 16. Quantum Programming

> [!levels] In this chapter
> **Lv1** you write and run your first Qiskit circuits with the simulator. **Lv2** you master the SDK workflow: build, transpile, execute, analyze. **Lv3** you debug quantum programs — with simulators, assertions, and visualization. **Lv4** you can structure quantum code the way you'd structure classical code: testable, layered, honest about noise. **Lv5** you understand where Qiskit ends and the research frontier (pulse control, dynamic circuits, error mitigation frameworks) begins — and what the competing stacks (Cirq, PennyLane, Braket) trade off.

### 16.1 Why Quantum Programming Is Different

Three differences reshape everything. One: *no variables* — state lives in a register you cannot read mid-flight, so classical control flow (`if`, `while` on data) is mostly unavailable; you pre-compute the whole circuit statically. Two: *no copying* — the same qubit can't be cloned into parallel branches, so algorithms are written as one fixed interference schedule. Three: *results are distributions* — every run returns a histogram, and your program's job is to make the histogram interpretable. The consequence: quantum "code" is mostly declarative circuit construction plus classical post-processing, and testing looks like statistical hypothesis testing, not unit tests. This chapter builds habits for all three.

### 16.2 Qiskit

Qiskit (≥1.0, IBM, Python) is this book's SDK: the most widely deployed, best documented, and the one the biggest hardware fleet exposes. Install locally: `pip install qiskit qiskit-aer matplotlib` — no account needed for simulators. The object model is small: `QuantumCircuit` (your program), `Primitive` layers (`SamplerV2` for distributions, `EstimatorV2` for expectation values), `BackendV2` (a target machine or simulator), and `transpile` (the compiler entry point). Cirq (Google), PennyLane (Xanadu, ML-oriented), and Amazon Braket are the other major stacks; the concepts here transfer — only the spelling changes. Version discipline matters: Qiskit 0.x→1.0 broke APIs; pin your versions.

### 16.3 Circuit Construction

```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)      # 2 qubits, 2 classical bits
qc.h(0)                        # H on q0
qc.cx(0, 1)                    # CNOT: control q0, target q1
qc.measure([0, 1], [0, 1])
print(qc)                      # text drawing
```

Construction is method calls in circuit order — the object is a list of instructions, and you can build circuits compositionally: `qc.compose(other, qubits=[2,3])`, `qc.to_gate()`, parameterized circuits `QuantumCircuit(2); qc.rz(θ, 0)` with `Parameter` objects for variational work (Ch. 59). Idiom: build small named circuits, compose them, and keep a `make_circuit(**params) -> QuantumCircuit` factory function rather than a mutable global — you will thank yourself in Part XIII.

### 16.4 Registers

Qubits and clbits live in named registers: `QuantumRegister(4, 'data')`, `ClassicalRegister(4, 'result')`, passed to `QuantumCircuit(data, result)`. Registers are addressing sugar — they let you write `qc.measure(data, result)` and keep circuits composable across width changes. Convention worth adopting from day one: separate registers by *role* — `data`, `ancilla`, `syndrome` — because Part X will have you managing hundreds of each, and "qubit 37" is meaningless while "syndrome[3]" is self-documenting. Under the hood, flat indexing still works and transpilation permutes it, which is why 16.11's result handling needs care.

### 16.5 Measurements

`qc.measure(qubit, clbit)` records Z-basis results into classical bits; `qc.measure_all()` adds a barrier and measures everything into one register. Basis changes: apply H (or `qc.barrier()` then H) before measuring to read the X basis — a pattern you will use constantly (Deutsch–Jozsa, QFT, stabilizer checks). Mid-circuit measurement and classical feedback: `with qc.if_test((creg, value)):` branches on measured bits — dynamic circuits, supported on modern IBM hardware and essential to QEC decoders running in the loop. Measurement is not free either: it takes time (~600 ns on fixed-frequency transmons) that depth budgets must include.

### 16.6 Simulators

Your main instrument. Aer (`qiskit-aer`) provides: `AerSimulator()` — exact state-vector simulation to ~30 qubits, with configurable noise models; `method="statevector"`, `"density_matrix"` (mixed states), `"stabilizer"` (Clifford circuits, hundreds of qubits), `"matrix_product_state"` (low-entanglement circuits, 100+ qubits). Separately, `Statevector.from_instruction(qc)` gives you the exact amplitudes *without* sampling — the debugging goldmine (16.14). Noise models: `NoiseModel.from_backend(backend)` imports a real machine's calibration data, so your laptop experiments can preview hardware behavior. Rule of thumb: exact sim for logic bugs, noisy sim for statistics, hardware for truth.

### 16.7 Transpilation

`transpiled = transpile(qc, backend, optimization_level=3)` is where your beautiful abstract circuit gets mangled into hardware reality: basis translation (your H becomes RZ–SX–RZ), routing (SWAP insertion for connectivity), optimization (gate cancellation, commutation analysis, ~20–40% depth reduction at level 3), and scheduling. Read the transpiled circuit — `transpiled.count_ops()`, `transpiled.depth()` — before running; it is the honest statement of what the machine will do. The pass manager is user-extensible (PassManager with custom passes), which is the gateway to the compiler engineering of Part XII. Optimization level 3 is slow but worth it for anything you publish.

### 16.8 Backend Selection

Backends differ in: qubit count, gate fidelities, coherence times, connectivity, and queue times. Query them programmatically: `backend.target` exposes per-gate error rates and durations; `backend.properties()` (for real machines) gives the calibration snapshot. Selection heuristics that actually matter: pick the device whose *two-qubit* errors are lowest on the qubits your circuit will land on (not the device with the most qubits); check the coupling map against your circuit's interaction graph; and for serious work, run a calibration-age check — data older than a day is stale. Fake backends (`GenericBackendV2(n)`) snapshot real device properties for offline work — this book's default.

### 16.9 Execution

The primitive workflow (Qiskit ≥1.0):

```python
from qiskit.primitives import StatevectorSampler

sampler = StatevectorSampler()          # or runtime SamplerV2 for hardware
job = sampler.run([transpiled], shots=4096)
result = job.result()[0]
counts = result.data.meas.get_counts()  # {'00': 2041, '11': 2055, ...}
```

Execution is asynchronous (job submission → queue → results), batchable (many circuits per job — always batch), and shot-limited (hardware time is expensive; 4096 shots per circuit is a typical budget). The `Sampler`/`Estimator` split is the field's convergence point: distributions vs. expectation values, with error-mitigation options (ZNE, PEC — Ch. 31) attached at this layer. Wrap execution in your own functions with retry and logging from day one.

### 16.10 Shot-Based Experiments

Everything measurable on a quantum computer is a sampling statistic over shots. Design experiments accordingly: choose shots from the statistics you need — estimating a probability to ±1% needs ~10⁴ shots (standard error √(p(1−p)/N)); distinguishing 0.500 from 0.505 needs ~10⁵. Vary one parameter per experiment (rotation angle, iteration count), record metadata (backend, calibration date, transpilation seed), and always run the ideal-simulator version alongside the noisy one — the delta *is* the noise, and studying it is Part IX in miniature. Keep a results log from your very first experiment; you are building a lab notebook, not running scripts.

### 16.11 Retrieving Results

`counts` maps bit-strings to occurrences — with one subtlety that bites everyone: bit-string order. Qiskit prints `q_{n-1}...q_0`, little-endian: in `'11'` after the Bell circuit, the leftmost bit is q1. Your register layout and the printed order are transposed from what you'd expect; verify once with an asymmetric circuit (H on q0 only) and never guess again. Post-processing lives here: histogram → probabilities → whatever your application needs (expectation values, parity checks, maximum-likelihood decoding). Keep post-processing in *separate, unit-tested* functions from circuit construction — mixing them makes quantum bugs unfalsifiable.

### 16.12 Visualizing Circuits

`qc.draw('mpl')` (matplotlib, publication-quality), `qc.draw('text')` (terminal), `qc.draw('latex')` (papers). For transpiled circuits, `qc.draw('mpl', idle_wires=False)` shows the physical layout, and `plot_circuit_layout(transpiled, backend)` overlays the coupling map — after which routing decisions become visible. Diagrams are debugging tools: if your H–CX–H doesn't look symmetric where you expected symmetry, you have a control/target bug. Parameterized circuits draw with `θ` labels. Make "draw before run" a hard rule: 30 seconds of eyes-on beats 30 minutes of confused counts.

### 16.13 Visualizing Distributions

`plot_histogram(counts)` for shot data; for state insight, the Bloch vector (`plot_bloch_multivector(Statevector(qc))`) and the QSphere for multi-qubit amplitude-and-phase structure. The cityscape plot (bar chart over bit-strings) is your default, but sort and threshold it: `dict(filter(lambda kv: kv[1] > 10, counts.items()))`. For parameter sweeps, plot the measured probability against the parameter — the interference fringes that emerge (Rabi oscillations, Ramsey fringes) are the signature that your circuit does what you think. Every figure in this book's experiments is reproducible with these three functions; make your own the same way.

### 16.14 Debugging Quantum Programs

Your toolkit, in escalation order. One: `Statevector(qc_without_measurements)` — exact amplitudes; compare against hand-computed expectations for small n. Two: `Operator(qc)` — the full unitary matrix; compare with `Operator(target)` using `np.allclose`. Three: partial simulation — run the circuit in pieces, checking state after each stage. Four: assertions mid-circuit (simulator-only) and `save_statevector` in Aer for snapshots. Five: for probabilistic bugs, fix the seed (`seed_simulator=42`) to make failures reproducible before you debug them. The cardinal rule: never debug on hardware. Hardware debugging is called "error mitigation" and it is a research field, not a workflow.

### 16.15 Testing Quantum Programs

Quantum code can have real tests. Property-based: your adder oracle satisfies `f(a,b) = a+b mod 16` for *all* inputs — test exhaustively on the simulator (4-bit: 256 cases, milliseconds). Invariants: ancillas return to |0⟩ (test via `Statevector` marginalization); your circuit is unitary (`Operator(qc).is_unitary()`); probabilities sum to 1. Regression: snapshot gate counts and depth — a change that doubles depth should fail review. Statistical: acceptance thresholds with known shot noise ("P(1) within 0.5±3σ"). pytest wraps all of it. Part XVIII's projects come with test suites in this style; adopt them for everything you build, starting with Chapter 17's simulator.

> [!tip] The simulator-first workflow
> 1. Write the circuit + a property test for its *mathematical* contract (unitary, oracle correctness).
> 2. Run ideal simulation; verify the distribution analytically.
> 3. Add a noise model; verify the result degrades the way theory predicts.
> 4. Only then touch hardware — and run the ideal sim alongside, same shots, same day.
> Every skipped step converts a logic bug into a "quantum is weird" misdiagnosis.

## 17. Building a Quantum Simulator

> [!levels] In this chapter
> **Lv1** you understand what a simulator must do: apply gates to a state vector, sample outcomes. **Lv2** you build one — single-qubit gates, then controlled gates, then measurement, then a circuit parser. **Lv3** you optimize it: avoid full matrix multiplication, exploit tensor structure, vectorize with numpy. **Lv4** you understand the algorithmic landscape — sparse, stabilizer, tensor networks — and when each wins. **Lv5** you know the frontier: Clifford+T simulation, Pauli propagation, and why simulating 50 good qubits is out of reach *for every computer on Earth*.

### 17.1 Why Build One Yourself

You will use Aer for everything real, so why write 300 lines of simulator? Because a simulator is the one quantum system you can see *all the way into* — every amplitude, every phase — and building one converts Part V's mathematics from notation into muscle memory. The exercise is the field's equivalent of writing an interpreter: after it, "the simulator applies the gate" is no longer a black box, and Aer's method flags (16.6) become engineering choices you understand. Budget: one focused weekend. Requirements: numpy, nothing else. The project spec at this chapter's end defines acceptance tests — write them first.

### 17.2 State-Vector Simulation

The core loop: maintain the state as a complex numpy array of shape (2ⁿ,), apply each gate by updating amplitudes, and at the end sample from |amplitudes|². For n qubits, index i = Σ bₖ·2ᵏ encodes the computational basis state |bₙ₋₁…b₀⟩. A gate on qubit k mixes only pairs of amplitudes differing in bit k — the observation that makes simulation O(2ⁿ) per gate instead of O(4ⁿ). Memory is the binding constraint: 128 bytes per amplitude (complex128) means 30 qubits = 137 GB. Everything else in this chapter elaborates this loop.

### 17.3 Single-Qubit Simulation

```python
import numpy as np

I2 = np.eye(2, dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)

def apply_1q(state, gate, k, n):
    """Apply `gate` to qubit k of an n-qubit state vector."""
    gk = np.kron(np.kron(np.eye(2**k), gate), np.eye(2**(n-k-1)))
    return gk @ state
```

This is correct and pedagogically honest — and hopelessly slow (O(4ⁿ) per gate). Run it for n=2..20, time it, and keep the numbers; 17.7 will beat them by orders of magnitude, and you should understand exactly why the first version dies: it multiplies by a mostly-identity 2ⁿ×2ⁿ matrix.

### 17.4 Matrix Multiplication

The naive approach treats the whole circuit as one matrix: U_total = U_m···U_2·U_1, then U_total @ state. Full 2ⁿ×2ⁿ matrices are infeasible past n≈13 (a 27 GB dense matrix), so serious simulators never build them. But the *composition* view is worth keeping for n≤10 as a ground truth: build U_total with np.kron and single products, apply once, and use the result to unit-test the fast implementation (17.7). Differential testing against the naive version is the single most effective bug-catcher in this project — keep both implementations in the test suite forever.

### 17.5 Multi-Qubit Simulation

Controlled gates are the first real challenge. CX on (control c, target t): for each pair of amplitudes (i, i XOR 2ᵗ) where bit c of i is 1, swap-mix them: (a_i, a_j) → (a_j, a_i) for X; more generally apply the 2×2 gate to pairs conditioned on the control bit. The mask idiom: `mask_c = 1 << c; for i in range(2**n): if i & mask_c: pair with j = i ^ (1 << t)`. Watch for double-counting — iterate over pairs, not all indices. This loop, vectorized correctly, is 90% of the project.

### 17.6 Tensor Products

np.kron is how operators on subsystems become operators on the whole: H on qubit 0 of a 3-qubit system is kron(H, I, I) — with the convention question: does qubit 0 get the leftmost factor? Decide once (numpy row-major favors leftmost = most significant bit; Qiskit's little-endian favors the opposite) and write a test that documents your choice, because a transposed endianness bug produces plausible-looking wrong answers. Tensor products also give you product-state initialization and the marginalization needed for measurement simulation. Part V's math becomes concrete here.

### 17.7 Applying Gates Efficiently

The production-grade approach: reshape + einsum. View the state as an n-dimensional tensor of shape (2,)*n with axis k = qubit k (choose your convention), then apply a 2×2 gate to axis k via `np.tensordot(gate, state, axes=([1],[k]))` and move the axis back with `np.moveaxis`. Cost: O(2ⁿ) per gate — optimal — with numpy doing the inner loops in C. Two-qubit gates: tensordot with a 4×4 matrix over two axes, or decompose into O(1) single-axis ops. Benchmark: your n=26 simulation should apply gates in well under a second; if not, you are still materializing 2ⁿ×2ⁿ matrices somewhere.

### 17.8 Measurement Simulation

Given final amplitudes, probabilities are `np.abs(state)**2` (your Born-rule implementation, already built in Chapter 1 — reuse it). Sampling one shot: `np.random.choice(2**n, p=probs)`; N shots: vectorize or loop. Post-measurement state (needed for mid-circuit measurement): zero out amplitudes inconsistent with the outcome and renormalize. Decide your convention for mapping the sampled integer to a bit-string (and test it!). Measurement is also where memory pressure spikes: precompute probabilities once, sample many times, and never materialize the full 2ⁿ probability array more than once per measurement point.

### 17.9 Random Sampling

Simulators owe you two kinds of randomness, done right. Outcome sampling: use a seeded `np.random.Generator` (PCG64) for reproducibility — your property tests (16.15) depend on it. And honest noise: a plain state-vector simulator is *ideal*; adding realistic noise means Kraus-channel sampling (Part IX will build this on top of your engine — design the API for it now: `apply_channel(state, kraus_ops) -> state`). Also implement exact expectation values ⟨ψ|O|ψ⟩ via `np.vdot(state, O @ state)` for the cases where sampling is wasteful. A simulator that only samples is half a simulator.

### 17.10 Circuit Parsing

Give your engine a front end so tests read like circuits. Define a tiny text format:

```text
H 0
CX 0 1
T 1
M 0 1
```

Parse lines → a list of (gate, operands) instructions; validate (qubit indices in range, no measurement mid-circuit unless you support it); then interpret. Round-trip test: convert a Qiskit circuit to this format (`qc.draw('text')` parsing is overkill — use `qiskit.qasm2` or export your own), run on both engines, assert equal distributions with the same seed. Now your simulator is a *dual* of Qiskit's, and every future chapter can check one against the other.

### 17.11 Performance Optimization

Ordered by payoff. One: tensordot over full-matrix apply (100–1000×). Two: `dtype=complex128` consistently — silent upcasting to complex256 or object arrays is a classic slowdown. Three: fuse single-qubit gate sequences per qubit before applying (matrix product of 2×2s, one tensordot). Four: batch shots by sampling once per distribution. Five: `np.einsum` with `optimize=True` for multi-axis contractions. Profile before optimizing (`cProfile`, `line_profiler`) — in simulation code the profile is almost never where intuition points. Realistic target: ~10⁶ gates/second at n=25 on a laptop M-series chip; Aer will still beat you 10×, and that's fine.

### 17.12 Memory Complexity

The state vector is 16·2ⁿ bytes; the wall arrives at n=30 (172 GB) on commodity hardware, n≈34 on a 512 GB machine. Be precise about what "simulating n qubits" costs: time O(gates·2ⁿ), memory O(2ⁿ) — and notice the asymmetry with hardware, which costs O(n) qubits to hold the same state. Extend Chapter 1's memory experiment: your own simulator, n = 24…30, plot time-per-gate (flat) and max memory (exponential). The exponential you measure on your laptop is the same constant that protects a 50-qubit state from simulation by the biggest supercomputer — the field's honest boundary, experienced firsthand.

### 17.13 Sparse Simulation

Many important states are sparse: computational basis states, and states reachable by circuits with few non-Clifford gates. Sparse simulators store (index, amplitude) pairs in a dict or hash map, and a gate on qubit k touches at most 2ⁿ⁻¹ *occupied* pairs. When does this win? Controlled additions (Shor-style arithmetic) create states with O(poly) occupied basis states per intermediate step — sparse simulation of Shor N=15 state-preparation runs in kilobytes. Implement `SparseSimulator` sharing your parser (17.10), and test it against the dense engine on small n. Qiskit's Aer doesn't ship one; research codes (and Google's 2019 Supremacy crossover claims) live in this regime.

### 17.14 Stabilizer Simulation

The Gottesman–Knill theorem: circuits made only of {H, S, CX, Paulis, measurement of Z} are classically simulable in O(n²) time and memory — no state vector at all. The state is represented by n stabilizer generators (Pauli strings with signs); each Clifford gate updates the tableau in polynomial time. This is why thousands of qubits of *error-correcting* circuitry (Part X: surface codes are Clifford circuits!) simulate fine while 50 algorithmic qubits don't. Implement a mini-tableau (Chase Gordon's `stim` is the reference — install it, read its paper) and verify: your stabilizer engine agrees with the dense engine on Clifford circuits of 10–30 qubits, in microseconds vs. seconds.

### 17.15 Tensor-Network Simulation

The frontier of classical simulation: represent the state as a network of small tensors (matrix product states, PEPS) whose size tracks *entanglement*, not qubit count. Low-entanglement circuits (1D dynamics, shallow depths) simulate to 100+ qubits; highly entangled circuits hit the bond-dimension wall — which is exactly how Google argued its 53-qubit 2019 result was hard to simulate classically (and how IBM's counter-analysis argued the crossover was reachable). You won't implement MPS here (Part XVIII offers it as a project), but know `quimb` and `ITensor`, and know the rule: tensor networks trade memory for entanglement assumption — the perfect counterpart to 17.12's hard exponential.

> [!research] The simulation arms race
> Every quantum-advantage claim is answered by a classical simulation advance. Random circuit sampling: Google 2019 claimed 10,000 years → optimized tensor-network methods brought it to minutes (with quality caveats) within two years. The current frontier is simulation of *noisy* circuits (Clifford + few T gates, Pauli perturbation methods), where 2024–25 results show near-term noisy circuits may be easier than clean ones. This matters to you as an engineer: the benchmark to beat is always a moving target, "beyond classical reach" claims decay fast, and the honest resource question is "how much *verified* classical work does the alternative cost?" — a question you are now equipped to ask.

## Project — Build a Small Quantum Simulator from Scratch

**Goal.** A pure-numpy state-vector simulator with a text circuit front end, faster than naive kron-multiplication by orders of magnitude, tested against both hand-computed answers and Qiskit.

**Deliverables.**
1. `qsim/` package: `dense.py` (state-vector engine, tensordot-based), `sparse.py` (dict-based), `parser.py`, `sampling.py`, `__init__.py`.
2. Gate set: H, X, Y, Z, S, T, RX/RY/RZ(θ), CX, CZ, SWAP, M (measurement), plus arbitrary 1q unitary.
3. CLI: `python -m qsim circuit.txt --shots 1024 --seed 7` → histogram; `--method dense|sparse`.
4. Test suite (`test_qsim.py`): differential tests vs. naive kron implementation (n≤8); vs. Qiskit Aer same-seed distributions (n≤10); property tests (unitarity, ancilla cleanliness); performance regression markers.
5. Benchmark report (`BENCHMARK.md`): time-per-gate and memory vs. n for your engine and Aer, one figure each.

**Milestones.**
- M1: single-qubit gates correct (17.3–17.4), tested against hand matrices.
- M2: CX/CZ/SWAP working (17.5), Bell state distribution 50/50 verified.
- M3: tensordot rewrite (17.7) passing all M1–M2 tests, ≥100× speedup at n=20.
- M4: parser + CLI + sampling (17.8–17.10).
- M5: sparse engine agreeing with dense on 5+ circuits (17.13).
- M6 (stretch): stabilizer engine via your own tableau or `stim` (17.14).

**Acceptance criteria.** All tests green; n=26 gate apply < 1 s; Bell, GHZ (n=8), QFT (n=4) distributions match Aer within 2σ at 4096 shots; every module has a docstring stating its complexity in n.
