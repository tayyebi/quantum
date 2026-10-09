# Part IX — Noise: The Real Computer

*Author: GLM-5.3*

Everything so far assumed unitary evolution of a perfectly isolated state vector. Real devices are open systems in constant contact with an environment they cannot control. This part builds the working language of noise: the failure mechanisms themselves (29), the state object that can actually represent them (30), and the operators that propagate them step by step (31). Density matrices and quantum channels are the objects you will simulate when you want to be honest about a real machine.

## 29. Why Quantum Computers Fail

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** a qubit is an open system in constant, unwanted conversation with its environment; the conversation is what destroys quantum information.
> - **Mathematics —** error processes decompose into relaxation (T1), dephasing (T2), and discrete faults: gate errors, measurement errors, leakage, and correlated noise.
> - **Implementation —** simulate readout error and correct it with a confusion matrix, entirely on a laptop.
> - **Engineering —** a transmon has T1 ≈ 100 µs and gates ≈ 20 ns; every design decision in this book is arithmetic on numbers like these.
> - **Research —** real noise is non-Markovian, correlated, and drifting; making error models honest is an open and active field.

### 29.1 Decoherence

Decoherence is the loss of definite phase relations between probability amplitudes, caused by the system becoming entangled with environmental degrees of freedom nobody observes. There is nothing mystical about it: the joint system-plus-environment evolves unitarily, and if you ignore the environment, your system's description degrades from a pure state into a mixture — Chapter 30 gives exactly the machinery for this. What is lost is interference, the computational resource of 1.2. The clock it sets is brutal: in a transmon, phase relations survive for tens of microseconds; in trapped ions, for seconds. Every quantum computation races this clock, and loses unless it finishes first.

### 29.2 Relaxation

Energy relaxation is the decay of the excited state |1⟩ down to |0⟩, characterized by the time T1. It is irreversible dissipation — no unitary can restore what leaked away — and the channel that describes it is amplitude damping (31.7). In superconducting qubits the mechanisms are dielectric loss in amorphous oxides, Purcell decay through the readout resonator, and quasiparticle tunneling. The arithmetic to internalize: a qubit excited at t = 0 survives with probability exp(−t/T1). With T1 ≈ 100 µs and gates ≈ 20 ns, one gate loses about 2×10⁻⁴ to relaxation — negligible alone, meaningful multiplied over a thousand-gate circuit, fatal in a fault-tolerance cycle.

### 29.3 Dephasing

Dephasing destroys relative phase without exchanging energy: populations stay fixed while the off-diagonal entries of the density matrix decay with the transverse time T2. The exact relation is 1/T2 = 1/(2·T1) + 1/Tφ, where Tφ is the pure dephasing time — hence T2 ≤ 2·T1 always. Dephasing is easy to underestimate because energy measurements see nothing: a superposition degrades into a classical mixture (30.2) while its energy statistics look perfectly healthy. Part of the noise is slow frequency wandering, which echo techniques (a mid-sequence π pulse, Hahn echo) can refocus — one of the few places noise is partially reversible.

### 29.4 Gate errors

Every gate is a physical analog operation, and its error has two families. **Coherent** errors are systematic miscalibrations — over-rotation by a fixed angle, a wrong phase — which do not randomize the state but rotate it to the wrong state; their amplitudes add coherently over n gates, which can grow worse than the naive expectation. **Stochastic** errors are relaxation and dephasing during the gate plus control noise; their probabilities add. The standard metric is average gate fidelity from randomized benchmarking, which cleanly separates gate error from state-preparation and measurement error. Typical numbers: single-qubit gates 10⁻⁴–10⁻³, two-qubit gates 10⁻³–10⁻², against a surface-code threshold near 10⁻² (Part X).

### 29.5 Measurement errors

Readout assigns the wrong bit: it reports 1 when the qubit was 0, or 0 when it was 1. The model is an asymmetric confusion matrix — the two error rates are generally different — and modern machines run 99–99.9% fidelity. Causes: a weak measurement signal before amplification, T1 decay during the 100 ns–1 µs readout itself, and discriminator drift (29.8). Readout error has a property no other error has: it acts after all quantum operations are done, so it can be corrected statistically in classical post-processing by inverting the confusion matrix — at the price of amplifying shot noise. This is the one error a software engineer can fully own, and the experiment below does exactly that.

### 29.6 Leakage

Leakage is population escaping the computational subspace {|0⟩, |1⟩} into higher levels. Real qubits are not two-level systems: a transmon is a weakly anharmonic oscillator with |2⟩, |3⟩, ... sitting only ~200–300 MHz above |1⟩, and strong or misshapen pulses populate them. Leakage breaks the two-level channel models of Chapter 31 and is poison for error correction: a leaked qubit produces faulty syndromes and keeps doing so, since leakage does not randomize away. Mitigations: DRAG pulse shaping, leakage-reduction units between cycles, and leakage-aware compilation. Typical per-gate leakage is 10⁻⁴–10⁻³ — small, but it accumulates in long fault-tolerance computations.

### 29.7 Crosstalk

Crosstalk is unintended drive of qubit j while you are addressing qubit i: shared microwave lines, a common resonator bus, and flux pulses bleeding through shared circuitry all do it. The measurable symptom: gates run simultaneously degrade in fidelity compared with isolated calibration, sometimes by several times. The structural damage is worse than the per-gate number suggests — crosstalk creates **correlated** errors between physical neighbors, and correlated errors violate the independence assumptions that error-correction thresholds are proven under (Part X). Countermeasures are classical engineering: frequency allocation, pulse shaping, dynamical decoupling on idle qubits, and simultaneous randomized benchmarking to quantify the damage. Nothing fundamental prevents engineering it down.

### 29.8 Calibration drift

Device parameters move on hours-to-days timescales: qubit frequencies shift with flux noise and temperature, pulse amplitudes drift as electronics age, readout discriminators wander. A large machine is therefore never fully calibrated; it runs continuous automated recalibration, and vendors publish per-qubit, per-day error rates. Two consequences for working practice. First, fidelity is a time series, not a constant: a benchmark at 09:00 does not describe the machine at 21:00, and honest experiments sample over time. Second, calibration automation — scheduling what to recalibrate and when on a device with thousands of interacting parameters — is one of the most software-heavy jobs inside hardware companies.

### 29.9 Thermal effects

A qubit arrives thermally excited unless the machine is colder than its own frequency: excited-state population is n = 1/(exp(hf/kT) − 1). A 5 GHz transmon needs T ≪ 240 mK, which is why dilution refrigerators run at 10–20 mK, giving n ~ 10⁻⁵. Warm wiring radiates blackbody photons into the chip, so attenuation and filtering are load-bearing components. Thermal effects differ per platform rather than disappearing: ions and neutral atoms escape cryogenics but pay in laser cooling and ultra-high vacuum; photonic detectors (SNSPDs) still need a cryostat. Every platform pays a thermal bill — the engineering question is where, and in what currency.

### 29.10 Environmental noise

The environment is not an abstract bath; it has a spectrum you can measure and structures you can name. In superconducting chips: two-level-system defects in amorphous dielectrics, 1/f flux noise, charge noise, quasiparticles — and ionizing radiation, where cosmic rays or radioactive decay deposit energy bursts that flip or dephase *hundreds* of qubits at once, a documented correlated-error problem that directly threatens error correction (Part X). Mitigation is materials science, shielding, filtering, and layout discipline. The mindset is the one classical electronics engineers already have — grounding, EMI, noise budgets — raised to a much higher standard, because here the signal is a single quantum of energy.

> [!experiment] On your laptop — readout error and the confusion matrix
> Simulate a qubit with asymmetric readout error, then correct the observed statistics by inverting the confusion matrix. This is exactly what real readout-error mitigation does.
>
> ```python
> import numpy as np
>
> rng = np.random.default_rng(0)
> e01, e10 = 0.02, 0.06        # P(1|0) and P(0|1): readout is asymmetric
>
> # confusion matrix A[measured, true] = P(measured | true)
> A = np.array([[1 - e01, e10],
>               [e01, 1 - e10]])
>
> true_s = rng.choice([0, 1], size=200_000)
> flip = rng.random(200_000) < np.where(true_s == 0, e01, e10)
> measured = true_s ^ flip.astype(int)   # flip the bit where readout failed
>
> obs = np.bincount(measured, minlength=2) / len(measured)
> corrected = np.linalg.inv(A) @ obs     # undo the confusion in post-processing
> print("true:      ", np.bincount(true_s, minlength=2) / len(true_s))
> print("observed:  ", obs)
> print("corrected: ", corrected)
> ```
>
> The corrected frequencies land back on 50/50. Note the trade: correction is exact in expectation but amplifies statistical noise — the reason mitigation is not a substitute for better hardware.

## 30. Density Matrices

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** a density matrix is a probability distribution over quantum states: the honest description of anything real, and the smallest object that can hold noise.
> - **Mathematics —** ρ is Hermitian, positive semidefinite, trace 1; every prediction is a trace: ⟨M⟩ = Tr(Mρ).
> - **Implementation —** represent ρ as a 2ⁿ×2ⁿ numpy array; simulate noise by mixing, damping, and partial trace.
> - **Engineering —** every fidelity number in vendor datasheets is a statement about density matrices; simulation memory grows as 4ⁿ.
> - **Research —** entropy and purity of ρ connect decoherence to thermalization and bound classical simulation of many-body dynamics.

### 30.1 Pure states revisited

The state vector |ψ⟩ of Part III encodes maximal knowledge of an isolated system. To let it degrade, rewrite it as an object: ρ = |ψ⟩⟨ψ|, the outer product of the state with itself. Check its properties: Hermitian, positive semidefinite, trace 1, and idempotent — ρ² = ρ, rank one. Every prediction you already know transfers unchanged: the probability of measurement outcome m is Tr(|m⟩⟨m|ρ) = |⟨m|ψ⟩|², and evolution is ρ → UρU†. Nothing changes for pure states. The point is that ρ is a *larger* language: it describes situations the state vector cannot — and noise is precisely those situations.

### 30.2 Mixed states

A mixed state is classical uncertainty: with probabilities pₖ the system is in state |ψₖ⟩, and ρ = Σₖ pₖ|ψₖ⟩⟨ψₖ|. Keep the distinction sharp: α|0⟩ + β|1⟩ is one pure state whose amplitudes can interfere; a 50/50 mixture of |0⟩ and |1⟩ is ρ = ½(|0⟩⟨0| + |1⟩⟨1|) = I/2 — maximum ignorance, no phase, no interference, nothing recoverable. The test is purity Tr(ρ²): it equals 1 if and only if the state is pure, and I/2 scores ½. Decoherence (29.1) is exactly the conversion of pure states into mixed ones — this chapter is where that sentence becomes computable.

### 30.3 Density operators

The three axioms: ρ is Hermitian (ρ† = ρ), positive semidefinite (⟨φ|ρ|φ⟩ ≥ 0 for all |φ⟩), and has unit trace. Closed-system evolution is ρ → UρU†; the expectation of any observable is ⟨M⟩ = Tr(Mρ). Why this is *the* state object you can actually simulate noise with: a noisy process maps valid density matrices to valid density matrices, and a state vector simply cannot express "half the coherence is left" — the concept does not exist for it. The price is memory: an n-qubit ρ is a 2ⁿ×2ⁿ matrix, so cost grows as 4ⁿ. One and two qubits simulate instantly; about 12–14 qubits strain a laptop; beyond that you need tensor networks (Part V).

### 30.4 Bloch representation

For a single qubit, ρ = ½(I + x·X + y·Y + z·Z), with a real Bloch vector r = (x, y, z). Pure states are the sphere's surface (|r| = 1), mixed states the interior, I/2 the exact center. Noise becomes geometry: amplitude damping drags z toward −1 (29.2), dephasing shrinks x and y toward 0 (29.3), depolarizing shrinks the whole vector toward the center (31.4). The vector's length is a purity measure, Tr(ρ²) = ½(1 + |r|²), so "how mixed is this state" becomes "how long is this vector" — and the experiment at the end of this chapter implements that decay directly.

### 30.5 Reduced density matrices

For a composite system, the reduced density matrix ρ_A is "everything observable about subsystem A alone". Take the Bell state (|00⟩ + |11⟩)/√2: the joint state is pure and completely known, yet each qubit individually has ρ = I/2 — maximally mixed. That gap between joint purity and subsystem purity is entanglement, made quantitative. It is also the precise formal statement of decoherence: the system entangles with the environment, the environment is unobserved, so the system's reduced state is mixed. Nothing collapsed; you simply stopped tracking correlations — and correlations are exactly what a reduced state discards.

### 30.6 Partial trace

The mechanics: ρ_A = Tr_B(ρ), computed by summing over the basis of B — element (i, j) is Σₖ ⟨i,k|ρ|j,k⟩. In numpy the idiom is to reshape the state vector into a tensor with one dimension of size 2 per qubit, then contract (trace) over the indices belonging to B. Do the Bell state by hand once: partial trace over either qubit returns I/2, confirming 30.5. Get this operation fluent — every noise simulation, every entropy calculation, and every "what does this qubit actually know" question runs through it, and implementing it correctly on a reshaped tensor is a rite of passage worth one focused hour.

### 30.7 Entropy

The von Neumann entropy of ρ is S(ρ) = −Tr(ρ log₂ ρ) = −Σₖ λₖ log₂ λₖ, over the eigenvalues λₖ. A pure state has S = 0 — one eigenvalue 1, the rest 0 — regardless of how complicated the state vector looks. The maximally mixed n-qubit state has S = n bits, the maximum. With log₂ the unit is bits and the quantum generalization is exact: for a diagonal ρ, this is the Shannon entropy of the diagonal entries. Entropy answers "how much information is missing about the actual state" — zero for pure states, however elaborate; n for total ignorance.

### 30.8 Von Neumann entropy

What the entropy buys you. **Entanglement measure**: for a pure joint state, S(ρ_A) quantifies how entangled A is with the rest, and it is basis-independent — a property of the state, not of its description. **Thermodynamics**: thermal (Gibbs) states are exactly the states minimizing S at fixed energy, and noise increases S — the second law reappears as a statement about channels (31.9). **Practice**: computing S requires eigenvalues, an O(d³) operation, so simulators often track the cheap alternative purity Tr(ρ²) instead. Research hook: the rapid growth of entanglement entropy under generic dynamics is precisely what makes large quantum systems classically intractable — entropy is the boundary of simulability.

> [!experiment] On your laptop — watch the Bloch vector decay
> Integrate the Bloch equations for a transmon-like qubit (T1 = 100 µs, T2 = 80 µs) starting at |+⟩, and watch relaxation pull z toward −1 while dephasing shrinks x and y. This is 30.4 and 31.7 in one loop.
>
> ```python
> import numpy as np
>
> T1, T2 = 100e-6, 80e-6          # transmon-like: 100 µs, 80 µs
> dt, n_steps = 1e-6, 100
> r = np.array([1.0, 0.0, 0.0])   # Bloch vector of |+>
>
> for step in range(1, n_steps + 1):
>     r[0] *= np.exp(-dt / T2)                          # dephasing shrinks x
>     r[1] *= np.exp(-dt / T2)                          # dephasing shrinks y
>     r[2] += (-(r[2] + 1.0)) * (1 - np.exp(-dt / T1))  # relaxation pulls z to -1
>     if step in (1, 10, 25, 50, 100):
>         print(f"t = {step*dt*1e6:5.0f} µs   r = [{r[0]:+.3f} {r[1]:+.3f} {r[2]:+.3f}]"
>               f"   |r| = {np.linalg.norm(r):.3f}")
> ```
>
> After 100 µs the vector has shrunk from length 1 to about 0.69: the state is now a mixture. Extend it — start at |0⟩ and confirm z decays toward −1 with the same T1.

## 31. Quantum Channels

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** a channel is the most general physically legal noise step: a machine that eats one density matrix and outputs another, applied at every time step of every real device.
> - **Mathematics —** completely positive trace-preserving maps; Kraus form Σₖ KₖρKₖ† with the constraint Σₖ Kₖ†Kₖ = I.
> - **Implementation —** implement depolarizing, bit-flip, phase-flip, and amplitude-damping channels directly in numpy.
> - **Engineering —** vendor noise models are libraries of channels; composing them per gate builds a full-circuit noise model.
> - **Research —** Markovian channels assume memoryless, uncorrelated noise; real devices remember and correlate — modeling that honestly is open.

### 31.1 Completely positive maps

Which transformations of density matrices are physically possible? The output must be a valid density matrix for every valid input — but positivity alone is not enough. There exist maps that map every density matrix to something valid, yet when applied to *half of an entangled pair* produce an impossible, negative state. Complete positivity closes the hole: the map must stay positive even after you tensor it with the identity on any ancillary system. The classic unphysical example is the transpose map — positive, but not completely positive, and equivalent to signaling through entanglement if it were allowed. Complete positivity is the mathematics of "implementable noise", and every hardware noise model must pass this test.

### 31.2 Trace preservation

A channel must conserve probability: Tr(E(ρ)) = Tr(ρ) for every ρ — nothing silently discarded, no unmonitored postselection. In Kraus form this becomes one algebraic constraint, Σₖ Kₖ†Kₖ = I, which you should verify on each channel below. Relax it to Tr(E(ρ)) ≤ 1 and you get the broader class of operations with postselection — the mathematical form of "measure and keep only the good runs", which heralded schemes exploit (42.5). The organizational picture: every gate is the special case of a unitary channel ρ → UρU†, trivially completely positive and trace-preserving; noise is any other map in the same class.

### 31.3 Kraus operators

The central formula of this chapter: E(ρ) = Σₖ Kₖ ρ Kₖ†, with Σₖ Kₖ†Kₖ = I. Read it as an error bank: branch k occurs with probability pₖ = Tr(KₖρKₖ†), leaving the conditional state KₖρKₖ†/pₖ. On d dimensions, d² operators always suffice — every completely positive trace-preserving map fits this form. The representation is not unique: different operator sets can define the identical channel, so the channel, not the operators, is the physical object; the operators are coordinates. Simulation is three lines: loop over the Kraus operators, conjugate, sum. The experiments in this chapter are exactly that loop, instantiated for each standard noise process.

### 31.4 Depolarizing channels

With probability p, replace the state by the maximally mixed state I/2; with probability 1 − p, leave it untouched. Kraus operators: K₀ = √(1 − 3p/4)·I and K₁, K₂, K₃ = √(p/4)·X, √(p/4)·Y, √(p/4)·Z. On the Bloch picture the effect is r → (1 − p)·r: uniform shrink toward the center, all directions equally. This is the "generic noise" default of every simulator — one parameter, symmetric, information-destroying in every basis — and the honest caveat is that real devices are *not* symmetric. The experiment below builds the channel two ways, by mixing density matrices and by Kraus operators, and confirms they agree exactly.

> [!experiment] On your laptop — depolarizing channel, two ways
> Build the depolarizing channel by mixing density matrices and by applying Kraus operators; the results must match. Mixing is the definition, Kraus is the simulation workhorse.
>
> ```python
> import numpy as np
>
> I = np.eye(2, dtype=complex)
> X = np.array([[0, 1], [1, 0]], dtype=complex)
> Y = np.array([[0, -1j], [1j, 0]])
> Z = np.array([[1, 0], [0, -1]], dtype=complex)
>
> rho = np.array([[0.5, 0.5], [0.5, 0.5]])   # |+><+|
> p = 0.3
>
> # way 1: with probability p, replace rho by the maximally mixed state
> rho_mix = (1 - p) * rho + p * I / 2
>
> # way 2: Kraus operators K0 = sqrt(1-3p/4) I, K1..3 = sqrt(p/4) X, Y, Z
> K = [np.sqrt(1 - 3*p/4) * I,
>      np.sqrt(p/4) * X, np.sqrt(p/4) * Y, np.sqrt(p/4) * Z]
> rho_kraus = sum(Ki @ rho @ Ki.conj().T for Ki in K)
>
> print("mixing:", np.round(rho_mix.ravel().real, 10))
> print("kraus: ", np.round(rho_kraus.ravel().real, 10))
> print("match:", np.allclose(rho_mix, rho_kraus))
> ```
>
> Then verify the Bloch claim of 31.4: apply both to |0⟩ and check the vector shrinks by the factor 1 − p.

### 31.5 Bit-flip channels

With probability p apply X; otherwise identity. Kraus operators: K₀ = √(1 − p)·I and K₁ = √p·X; the channel is ρ → (1 − p)ρ + p·XρX. On the Bloch sphere: the x component is untouched, while y and z are scaled by (1 − 2p) — the sphere pinches toward the x-axis. This is the closest quantum analogue of classical bit corruption, and it is the channel the three-qubit bit-flip code of Part X was designed to correct. Reality check: hardware does not produce pure bit flips — real noise is closer to depolarizing plus amplitude damping — which is exactly why the clean code analyses of Part X need the general channel theory you are building here.

### 31.6 Phase-flip channels

With probability p apply Z: ρ → (1 − p)ρ + p·ZρZ, with Kraus operators K₀ = √(1 − p)·I and K₁ = √p·Z. Bloch picture: z untouched, x and y scaled by (1 − 2p). Two identities make this channel important. First, it *is* the bit-flip channel in a rotated basis: since H·X·H = Z, conjugating the states and operators by Hadamards converts one into the other — which is why the three-qubit phase-flip code in Part X is just the bit-flip code wearing H gates. Second, its continuous-time limit is pure dephasing (29.3): many small random phase kicks rather than rare discrete flips, governed by Tφ.

### 31.7 Amplitude damping

The channel of T1 (29.2), written in the {|0⟩, |1⟩} basis as K₀ with diagonal (1, √(1 − γ)) and K₁ = γ-excitation-lowering: K₁ takes the amplitude of |1⟩ and moves it to |0⟩, with γ = 1 − exp(−t/T1) the decay probability over time t. It maps |1⟩ → |0⟩ with probability γ — irreversible, and therefore **non-unital**: E(I) ≠ I, the identity is not a fixed point because the channel cools the qubit toward |0⟩. Bloch arithmetic: z → (1 − γ)z − γ and x, y → √(1 − γ)·(x, y). On superconducting hardware this is the dominant irreducible channel; the experiment applies it and recovers the exponential T1 curve.

> [!experiment] On your laptop — T1 decay with amplitude damping
> Start a qubit in |1⟩ and apply the amplitude-damping channel for growing times with T1 = 100 µs. The excited population should follow the exponential 1 − exp(−t/T1).
>
> ```python
> import numpy as np
>
> def amplitude_damping(rho, gamma):
>     K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
>     K1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)
>     return K0 @ rho @ K0.conj().T + K1 @ rho @ K1.conj().T
>
> ket1 = np.array([0, 1], dtype=complex)
> rho = np.outer(ket1, ket1.conj())          # start in |1>
>
> for t_us in (0, 50, 100, 200, 400):
>     gamma = 1 - np.exp(-t_us / 100)        # T1 = 100 µs
>     d = amplitude_damping(rho, gamma)
>     print(f"t = {t_us:3d} µs   P(|0>) = {d[0,0].real:.3f}   P(|1>) = {d[1,1].real:.3f}")
> ```
>
> At t = T1 = 100 µs you should see P(|0>) ≈ 0.632. Then feed it |+⟩ and confirm that both populations move while coherence shrinks by √(1 − γ).

### 31.8 Phase damping

Energy-preserving loss of coherence: populations untouched, off-diagonal entries multiplied by a decay factor. A Kraus pair: K₀ = diag(1, √(1 − λ)) and K₁ = diag(0, √λ); over time t the off-diagonals carry the factor exp(−t/T2). Distinguish it carefully from the phase-flip channel (31.6): phase flips are rare discrete events; phase damping is a continuous random walk of the qubit's phase — the physical picture of a transition frequency wobbling under low-frequency noise. Compose amplitude damping (31.7) with phase damping and you have both independent decay clocks of hardware, T1 and T2: the complete minimal one-qubit noise model that Chapter 29's numbers describe.

### 31.9 Channel composition

Build large noise models from small pieces. **Sequential** composition E₂∘E₁ (apply E₁, then E₂) has as its Kraus set all products of a second-channel operator applied after a first-channel operator. **Parallel** composition on disjoint qubits tensor-products the operator sets. A full circuit's noise model is exactly this: after every gate, insert that gate's channel, all composed in circuit order. In continuous time the family of channels forms a semigroup E(t) = exp(tL), whose generator L is the Lindbladian — the equation behind physical-device simulators. And note what composition preserves: the state stays a density matrix, so noise remains representable at every step — something state-vector simulation structurally cannot deliver.

> [!research] Research frontier
> The channels of this chapter are Markovian: memoryless, instantaneous, and independent across qubits. Real devices violate all three — 1/f noise carries long memory, cosmic-ray bursts corrupt whole regions coherently (29.10), and crosstalk correlates qubits continuously. Building honest non-Markovian and correlated noise models is an active research field because error-correction thresholds and decoder design depend sensitively on the assumed error structure (Part X). A laptop-accessible entry point: vendor calibration pages publish per-qubit, per-day error rates — test how far a memoryless model diverges from that data, and what a simple drift model recovers.
