# Part XI — Quantum Hardware

*Author: GLM-5.3*

Above the hardware line — states, algorithms, codes — everything was abstraction. Here it stops: a quantum computer is a physical object built in a cleanroom or suspended in a vacuum, and every property you care about (fidelity, speed, scale) traces back to a physical mechanism and a physical limit. This part walks the real platforms: what the qubit physically is, what each design is good at, what it pays for it, and what you can actually reach from a laptop through cloud access today.

## 38. The Physical Quantum Computer

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** a qubit is not an abstraction; it is an engineered physical system — a circuit, an atom, a photon — from which two states have been carved and isolated.
> - **Mathematics —** any two-dimensional Hilbert space is a qubit; the DiVincenzo criteria formalize what a physical implementation must deliver.
> - **Implementation —** a driven two-level system is the common control physics of every platform and simulates in a few lines.
> - **Engineering —** platforms trade coherence, control speed, connectivity, and scalability against each other; the trade is the design.
> - **Research —** no platform satisfies all requirements at scale today; combining platforms' strengths is the open problem.

### 38.1 What a qubit physically is

Two states of some physical system: two energy levels of an atom, charge or flux states of a superconducting circuit, spin orientations of an electron, polarization of a photon. "Qubit" is the mathematics; the platform is the engineering that creates two levels, isolates them from everything else, drives transitions between them, and reads the result out. Real systems have more than two levels — a transmon is an oscillator with infinitely many — and the computational subspace is carved out of the ladder; falling out of it is leakage (29.6). Every platform in this part is a different answer to one question: which two levels of which system, at what cost in every other requirement?

### 38.2 Requirements for a physical qubit

DiVincenzo's checklist (1997) is still the standard scorecard: (1) a scalable system of well-characterized qubits; (2) initialization to a simple fiducial state; (3) coherence times much longer than gate times; (4) a universal set of quantum gates; (5) qubit-specific measurement. For networking, add interconversion between stationary and flying qubits. Apply it to every platform in this part and you will find each one fails some criterion gracefully and one painfully: superconductors are fast but forgetful, ions are stable but slow, photons fly but barely interact. The checklist also explains the field's structure — each hardware subfield exists because one criterion is hard for the others.

### 38.3 Coherence

Coherence times (29.2–29.3) set the clock. What matters is not raw T1 but the ratio to gate time: error per idle period ≈ duration / coherence time. Transmon: T1 ≈ 100 µs with gates ≈ 20 ns — a ratio near 5,000. Trapped ions: coherence in seconds to minutes with gates of 10–600 µs — a ratio near 10⁴–10⁵. Similar ratios from opposite extremes: fast-but-forgetful versus slow-but-stable. Note that coherence is engineered, not granted — transmon T1 rose from ~1 ns in 1999 to ~100 µs–1 ms today through materials, surface treatment, shielding, and filtering, and it is still improving. Demand this arithmetic from any platform claim: ratios, not adjectives.

### 38.4 Controllability

You must drive arbitrary single-qubit rotations and at least one entangling gate, faster than decoherence, with errors ≲ 10⁻³. Control is analog: shaped microwave pulses, laser pulses, flux pulses — the "program" of a quantum computer is ultimately a waveform library. Stronger, faster drives buy speed but spill into higher levels (leakage, 29.6) and bleed into neighbors (crosstalk, 29.7); that triangle — speed, leakage, crosstalk — is the daily trade of control engineering. The classical control stack (FPGAs, arbitrary waveform generators, GHz front ends) is a major cost center of every machine and, increasingly, the most software-intensive subsystem — a realistic entry point for engineers who cannot touch the physics.

### 38.5 Readout

Extract the state quickly, with high fidelity, without disturbing the neighbors: dispersive microwave readout for superconducting circuits (39.4), state-dependent fluorescence for ions and atoms (40.7), photon counting for photonics (42.6). Fidelities run 99–99.9%, durations from ~100 ns to milliseconds — and readout time counts twice: it bounds the machine's repetition rate and consumes coherence budget in error-correction cycles (Part X). Readout should be quantum non-demolition: measure without flipping. Errors here are the only noise you can patch purely in software (29.5). When benchmarking platforms, always ask for readout fidelity and readout time separately — they trade against each other.

### 38.6 Scalability

From a 50-qubit laboratory demonstration to 10⁶ qubits, wiring is the recurring villain. Each superconducting qubit wants 2–3 coaxial lines through a refrigerator with microwatt cooling power — hence cryo-CMOS multiplexing as the proposed escape. Ion traps need laser delivery to every qubit; neutral atoms need optical control over thousand-site arrays; photonics needs on-chip sources and detectors at scale. Platform roadmaps diverge here more than anywhere else, and small-scale laboratory results say almost nothing about the scaling limit. The engineering rule: ask for the per-qubit wiring, cooling, and optics budget at 10⁶ qubits, and ask what component technology has to change to get there.

### 38.7 Calibration

Every qubit needs its frequencies, pulse amplitudes, and readout discriminators calibrated — and recalibrated, because parameters drift (29.8). A large chip runs continuous automated calibration as a scheduling and optimization pipeline, consuming hours of machine time per day. This is also one of the most software-heavy parts of "hardware" companies: calibration is a classical control loop wrapped around an analog quantum system, and teams that build it look a lot like robotics teams. As a remote user you see the outputs — per-qubit, per-gate error rates published daily. Study those pages before running anything: they are the most honest performance data in the industry.

## 39. Superconducting Qubits

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** an LC circuit cooled until it behaves quantum-mechanically, with a nonlinear element that makes its two lowest levels individually addressable.
> - **Mathematics —** the Josephson junction is a nonlinear inductor; the transmon is a weakly anharmonic oscillator; dispersive coupling makes measurement possible.
> - **Implementation —** a transmon simulates as a 3-level oscillator under shaped pulses; Qiskit exposes pulse-level control.
> - **Engineering —** 10–20 mK cryogenics, per-qubit wiring, 20–300 ns gates, T1 ~ 100 µs; fabricated in cleanrooms like classical chips.
> - **Research —** coherence via materials science, wiring via cryo-CMOS, gates via tunable couplers — all active frontiers.

### 39.1 Josephson junctions

Two superconductors separated by a 1–2 nm insulator: Cooper pairs tunnel through, producing the current–phase relation I = Ic·sin(φ) — an inductor with a nonlinearity. The nonlinearity is the entire point: an ordinary LC oscillator has equally spaced energy levels, so a drive addressing |0⟩ → |1⟩ also drives |1⟩ → |2⟩, and no qubit can be isolated. The Josephson element makes the spacing unequal, so one transition can be addressed without the next. Junctions are patterned by electron-beam lithography with aluminum oxidation, and they are the most fabrication-sensitive part of the chip — the two-level defects of 29.10 live in their oxide layer.

### 39.2 Transmons

The dominant design: a Josephson junction shunted by a large capacitance. The large shunt makes the energy nearly insensitive to offset charge — killing the charge noise that limited earlier charge qubits — and carried coherence from nanoseconds (1999) to ~100 µs and beyond. The price is weak anharmonicity, only ~−200 to −300 MHz between adjacent transitions, so pulses must be carefully shaped or they leak (29.6). Variants: fixed-frequency transmons (better coherence, slower gates — IBM's choice) versus flux-tunable transmons (faster gates, more noise-sensitive — Google, Rigetti). When someone says "superconducting qubit" today, they almost always mean a transmon; IBM, Google, and Rigetti all build them.

### 39.3 Microwave control

Drive the |0⟩ ↔ |1⟩ transition with microwave pulses at 4–6 GHz, delivered down coaxial lines to a capacitive antenna on chip. Rabi oscillations calibrate pulse amplitude; pulse phase is controlled digitally, which makes rotations about the Z axis nearly free in software (virtual-Z gates). Shaping matters: Gaussian-derivative (DRAG) pulses suppress leakage into |2⟩ (29.6). Gate durations run 10–30 ns. Count the wiring: per qubit, 2–3 control lines plus a shared or dedicated readout line — multiply by a million qubits and the scaling wall of 38.6 becomes concrete. This per-qubit line count is why cryogenic control electronics is a research field.

### 39.4 Readout resonators

Dispersive readout: the qubit couples to a microwave resonator whose frequency shifts by ±χ depending on the qubit state; send a probe tone through and the outgoing phase or amplitude tells you the state. Signals are at the single-photon level, so quantum-limited amplifiers (Josephson parametric amplifiers, traveling-wave parametric amplifiers) are mandatory before conventional electronics can see anything. Readout takes ~100 ns to 1 µs at 99–99.9% fidelity — and during that window, T1 decay corrupts the answer (29.5). Resonators also couple qubits to each other unintentionally, making them a crosstalk channel as well as a measurement instrument (39.8).

### 39.5 Cryogenics

Why 10–20 mK: thermal excited-state population n = 1/(exp(hf/kT) − 1) must be far below 1, and at 5 GHz that demands temperatures well under 240 mK. A dilution refrigerator provides microwatts of cooling at the base stage; every coax line enters through attenuators (keeping blackbody radiation out) and exits through amplifiers. The refrigerator defines the machine's size, cost, and wiring budget, and its cooling power defines how much control electronics can live inside — which is why moving digital control to the 4 K or millikelvin stage (cryo-CMOS) is the central scaling battleground for this platform (38.6). You cannot shortcut this: warm transmons are simply not qubits.

### 39.6 Calibration

The daily pipeline (38.7, 29.8): spectroscopy to find each qubit's frequency, Rabi calibrations for pulse amplitudes, DRAG tuning, two-qubit gate calibration across every coupled pair, readout discriminator fitting. On a 100+ qubit device this is thousands of interacting parameters under frequency crowding — qubits sit only 100–500 MHz apart, so one qubit's calibration can invalidate a neighbor's. Deciding which calibrations to run, in what order, and when to re-run them is a genuine operations-research problem, made perpetual by drift. This is where superconducting-hardware companies employ their most software engineers — a classical control-and-optimization pipeline wrapped around physics.

### 39.7 Two-qubit gates

Three main mechanisms. **Cross-resonance** (IBM, fixed-frequency qubits): drive the control qubit at the target's frequency through their shared coupling; ~100–300 ns, errors 10⁻³–10⁻². **Tunable couplers** (Google): a dedicated coupler element is flux-pulsed to switch an effective interaction on and off, achieving faster gates (~30–60 ns) and the platform's best reported two-qubit errors. **Flux-tunable qubits** (Rigetti) gate by pulsing the qubits themselves. All are nearest-neighbor on a lattice — heavy-hexagonal for IBM — so every long-range interaction costs SWAP gates, and compiler overhead (Part XII) is part of the platform's true cost of ownership. Compare platforms at the compiled-circuit level, never the bare gate level.

### 39.8 Crosstalk

The platform's characteristic engineering disease. Qubits share control lines, readout chains, and couplers, so a pulse on qubit i drives qubit j at the 10⁻³ level; flux pulses leak through shared circuitry; and gates run simultaneously measurably degrade versus isolated calibration. The structural damage exceeds the per-gate number: crosstalk creates correlated errors between physical neighbors, straining the independence assumptions that error-correction thresholds are proven under (29.7, Part X). Countermeasures are classical engineering: careful frequency allocation, pulse shaping, dynamical decoupling on idle qubits, and simultaneous randomized benchmarking to quantify the damage. When comparing vendors, prefer the ones who publish crosstalk measurements — the ones who do not are not measuring it.

## 40. Trapped-Ion Quantum Computing

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** single atoms suspended in electromagnetic traps, qubits in internal atomic states, lasers doing everything: nature-made, defect-free qubits.
> - **Mathematics —** RF Paul traps confine ions; shared quantized motion (phonons) mediates Mølmer–Sørensen entangling gates.
> - **Implementation —** native gate sets (GPI/GPI2, ZZ) are exposed in cloud APIs; all-to-all connectivity changes compilation fundamentally.
> - **Engineering —** seconds-to-minutes coherence and ~99.9% two-qubit fidelity, but µs–ms gates and slow readout limit cycle speed.
> - **Research —** scaling past a single chain via shuttling and photonic links is the central open problem.

### 40.1 Trapped ions

The qubit is two internal states of a positively charged atom: hyperfine ground states (¹⁷¹Yb⁺, ⁴⁰Ca⁺) or optical excited states. Atoms are identical by construction — no fabrication variance, no dielectric defects — so every ion in every laboratory is the same qubit. State of the art: two-qubit gate fidelities at 99.9% and above (Quantinuum's H-series), the highest published two-qubit fidelities of any commercial platform, with coherence limited only by ambient field noise and reaching seconds to minutes. Chains of tens of ions sit in a linear trap; today's machines run tens of qubits with full connectivity inside the chain. The cost of all this quality is speed — everything is slower (40.6, 40.7).

### 40.2 Electromagnetic traps

Earnshaw's theorem forbids static fields from confining a charged particle, so the Paul trap uses an oscillating RF quadrupole field whose time-averaged potential is confining. Ions repel each other via Coulomb force and crystallize into a chain spaced ~5 µm apart. The chain's collective vibrations — quantized normal modes, or phonons — are shared by all ions; they are not noise to be eliminated but the data bus that entangling gates ride (40.6). Surface traps, with electrodes lithographed onto a chip, are the scaling path: they allow ions to be shuttled between storage, gate, and readout zones. Trap design is micromachining plus RF engineering, not cleanroom quantum fabrication.

### 40.3 Laser cooling

Gates need the shared motion nearly frozen. Doppler cooling: a red-detuned laser makes the ion absorb preferentially when moving toward the beam, dumping a momentum quantum each cycle — down to millikelvin. Sideband cooling then resolves individual motional modes and removes phonons one by one, reaching the motional ground state required for the highest-fidelity gates. Cooling runs between computations and refreshes the bus that gates heat up. The laser system is a serious engineering stack — phase-locked, sub-kHz-linewidth, frequency-stabilized lasers plus classical optics racks — and it is the platform's equivalent of control electronics: expensive, software-defined, and central to performance.

### 40.4 State preparation

Initialization by optical pumping: a polarized laser drives the ion until population funnels into one ground state and stays there — a dark state it cannot absorb from. Fidelity exceeds 99.9% in microseconds, and combined with sideband cooling (40.3) it prepares the register's all-zeros state. DiVincenzo criterion 2 is satisfied almost trivially — in contrast with superconducting chips, where initialization is either "wait for T1" or an actively engineered reset. The general pattern is worth naming: ion platforms spend *time* to obtain near-perfect primitives; superconducting platforms spend *hardware* to obtain speed. Neither is free, and the choice shapes everything downstream, including error correction.

### 40.5 Laser control

Single-qubit gates are Rabi rotations on the qubit transition, driven by a focused laser beam (optical qubits) or a microwave horn (hyperfine qubits); durations ~1–100 µs. Addressing individual ions in a 5 µm-spaced chain is an optics problem: tightly focused beams, acousto-optic deflectors for fast beam switching, and careful polarization control at every site. Gate phase is set by optical path length, so phase noise in the beam paths translates directly into dephasing errors — active path stabilization is a genuine engineering discipline here. Control complexity per qubit is higher than superconducting platforms', but it is optical and room-temperature rather than cryogenic microwave.

### 40.6 Entangling gates

Ions do not interact directly; entangling gates ride the shared phonons of 40.2. Cirac–Zoller (1995) mapped qubit state onto motion and back; Mølmer–Sørensen applies a bichromatic field that couples the whole chain to an effective XX-type interaction independent of the motion's exact state — this scheme and derivatives power modern machines. Durations ~10–600 µs; fidelities 99.9%+. The prize is connectivity: any pair of ions in the chain can gate directly — all-to-all — which eliminates most of the SWAP overhead that lattice platforms pay (44.4) and makes small circuits dramatically more efficient. The price: gates and heating disturb the bus, limiting practical chain length to tens of ions.

### 40.7 Measurement

State-dependent fluorescence: drive a cycling transition that only |1⟩ scatters, and the ion either glows (thousands of photons) or stays dark, collected by a photomultiplier or camera. Fidelity exceeds 99.9%, each ion in the chain is individually resolved, and crosstalk is negligible. This is the most ideal projective measurement of any platform — nearly quantum non-demolition. The cost is speed: detection takes ~100 µs to 1 ms, plus recooling afterward. For algorithms this is fine; for error correction (Part X) it is the bottleneck, because QEC demands fast repeated cycles of reset, gate, and measure — so the ion platform's fault-tolerance rate is limited by its best feature, its measurement.

### 40.8 Scaling

One chain shares one motional bus, and modes crowd together as ions are added — tens of ions is the practical chain limit. Three scaling paths exist. **Shuttling**: physically move ions between storage and gate zones through junction electrodes — Quantinuum's QCCD architecture works this way, and its shuttling-based machines with 50+ qubits are cloud-accessible today. **Photonic links**: entangle separate chains remotely via photons emitted and collected through cavities — demonstrated at small scale, currently slow, potentially unlimited. **Larger two-dimensional traps**: still exploratory. The open question is arithmetic: whether gate speed plus shuttling overhead can deliver the fast cycle times fault tolerance wants, or whether fidelity headroom must buy back the time.

## 41. Neutral Atoms

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** single neutral atoms held by focused laser light in reconfigurable 2D arrays; excite an atom to a huge Rydberg orbit and it blocks its neighbors — that is your gate.
> - **Mathematics —** Rydberg blockade: one excited atom shifts nearby atoms' levels out of resonance, giving a strong, long-range, controllable nonlinearity.
> - **Implementation —** simulate blockade-constrained scheduling and geometry; the array layout is software, reconfigurable per run.
> - **Engineering —** hundreds to thousands of atoms with fast gates, but two-qubit fidelity (~99.5%) trails ions, and atoms are lost during operation.
> - **Research —** mid-circuit loss recovery, gates on the move, and error correction on lossy, reconfigurable hardware are wide open.

### 41.1 Optical tweezers

A tightly focused laser beam, detuned from atomic resonance, polarizes a neutral atom and traps it at the focus. Paint an array of such foci with spatial light modulators or acousto-optic deflectors and you hold hundreds to thousands of single atoms (rubidium, cesium, strontium) in 2D patterns — arrays of 6,100 atoms were demonstrated in 2025. Loading is probabilistic per site (~50–60%), so rearrangement algorithms — grab atoms with movable tweezers and fill the holes — are a signature, software-solvable feature of the platform. The geometry of the array is literally programmable per experiment, which no fixed-lattice platform can offer.

### 41.2 Ultracold atoms

Atoms must be cold to stay trapped: laser cooling plus evaporative cooling brings them to microkelvin temperatures inside an ultra-high-vacuum cell. Being identical atoms, all sites are equivalent — no device-to-device fabrication variation, the same advantage ions have. Qubit states are hyperfine ground states or clock states, with coherence of seconds. Infrastructure is a real differentiator: apart from photonics hardware, the machine is room temperature and tabletop-scale — no dilution refrigerator in the physics. That changes who can build and host these machines, and it is one reason neutral-atom systems scaled in atom count faster than any other platform.

### 41.3 Rydberg excitation

Excite the valence electron to a state with principal quantum number n ≈ 70: a huge, diffuse electron orbit carrying an enormous electric dipole moment. Rydberg atoms interact strongly at micrometer distances — exactly the tweezer spacing — through dipole–dipole coupling, and the interaction strength grows steeply with n. Two-photon laser pulses drive |1⟩ → |r⟩ in tens of nanoseconds. The Rydberg state decays back in ~100 µs and is sensitive to stray electric fields, which sets the platform's noise floor and calibration burden. This single interaction is the transistor of neutral-atom quantum computing: everything else in 41.4–41.6 builds on it.

### 41.4 Rydberg blockade

If atom A is excited to |r⟩, its electric field shifts the neighboring atoms' Rydberg level by more than the excitation laser's linewidth: they can no longer be excited — one excitation per blockade radius of ~5–10 µm. This is a strong nonlinearity assembled from atoms, and it implements controlled-phase gates directly. It also powers the platform's **analog mode**: instead of digital gates, sweep the laser slowly and let the blockade geometry adiabatically prepare entangled many-body states — the mode in which QuEra's 2023–24 experiments with hundreds of atoms produced sampling results that challenged classical simulation. Digital and analog modes share hardware but demand different compilers.

### 41.5 Gate operations

Digital mode: Rydberg-mediated CZ between neighboring atoms in 100 ns–1 µs, with reported two-qubit fidelities around 99.5% (best ~99.8% in specialized geometries); single-qubit gates ~100 ns via microwave or Raman pulses. A unique option exists on no other platform: atoms can be moved during the computation, so "connectivity" includes transport — gate non-adjacent atoms by moving them together first. Mid-circuit measurement and single-atom reloading have been demonstrated, the primitives fault tolerance needs. The honest summary: speed is competitive with superconductors for some gates, and the gap to close versus ions is fidelity, not scale.

### 41.6 Arrays

Connectivity is defined in software, per run: triangular, square, Kagome, or multi-layer geometries, plus storage and entangling zones. This is architecturally unlike fixed-lattice superconductors — quantum error-correcting codes that need nonlocal connections (certain LDPC codes and surface-code variants) map naturally onto atom arrays, and the geometry can change between circuit executions. The compiler's job changes accordingly: scheduling atom moves becomes part of compilation (Part XII). QuEra and Pasqal expose such arrays through cloud access, and the 2023 Harvard/QuEra work ran error-corrected logical qubits on 200+ atom arrays — the first logical-qubit demonstrations on this platform, three years after Google's.

### 41.7 Scaling

The headline is atom count: thousands of physical qubits already exist, scaling by optically engineering larger arrays — there is no wiring wall like 39.5. The debts are equally concrete: two-qubit fidelity must roughly double its nines to reach ion class; atoms are lost during operation and must be detected and replaced mid-circuit, an unsolved systems problem at speed; laser, imaging, and vacuum systems grow complex with array size; and readout crosstalk across dense arrays needs management. Both landmark events of 2023–24 — analog advantage-class sampling (41.4) and logical-qubit demonstrations (41.6) — happened on this platform first. Its ceiling is genuinely unknown, which cuts both ways.

## 42. Photonic Quantum Computing

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** qubits made of light: photons rarely interact with anything, so they are perfect messengers and terrible collaborators — the platform's genius and its problem are the same fact.
> - **Mathematics —** qubits in polarization or path modes; linear optics plus measurement and ancilla photons give probabilistic gates (the KLM theorem).
> - **Implementation —** simulate interferometer unitaries and heralded-gate probabilities; the resource to track is photon loss.
> - **Engineering —** room temperature and network-native, but loss plus probabilistic gates force enormous multiplexed redundancy.
> - **Research —** deterministic sources, loss-tolerant GKP and fusion-based error correction, and massive on-chip integration.

### 42.1 Photons as qubits

Encode a qubit in a mode of light: polarization, path, or time-bin. The advantage list is real: photons do not decohere in flight (there is nothing in vacuum to interact with), they propagate through telecom fiber — the best quantum network channel available — generation and detection are mature technologies, and most of the machine runs at room temperature. The disadvantage is structural: photons barely interact with each other, so there is no natural two-qubit gate. The entire field is a set of increasingly clever answers to that one sentence. And the dominant error is not decoherence at all — it is loss, which behaves differently from every noise model in Part IX.

### 42.2 Polarization

Basis states |H⟩ and |V⟩, horizontal and vertical. Control uses waveplates — a half-wave plate is a rotation gate, a quarter-wave plate prepares circular states — and analysis uses polarizing beam splitters routing the two components to single-photon detectors. The best detectors are superconducting nanowire single-photon detectors (SNSPDs): 90–98% efficiency, picosecond timing, negligible dark counts — the platform's one cold component, needing a cryostat despite the room-temperature physics. Polarization is convenient in free space but drifts in fiber birefringence; deployed fiber systems usually prefer time-bin encoding, which moves the qubit to early-versus-late arrival slots that fiber leaves stable.

### 42.3 Path encoding

The qubit is which of two waveguides the photon occupies. On silicon photonic chips, beamsplitters are Mach–Zehnder interferometers and phase shifters are thermo-optic or electro-optic elements — the full single-qubit gate set in lithographed hardware. Integrated photonics solves the stability problem that kills tabletop free-space optics (centimeter paths drift; millimeter on-chip paths barely move) and inherits the semiconductor fabrication ecosystem — PsiQuantum's explicit strategy is to ride commercial fabs. Photonic integrated circuits with thousands of components are routine. After spin qubits (43.1), this is the most fabrication-native quantum platform, and the only one whose manufacturing story is literally classical semiconductor engineering.

### 42.4 Interferometry

Beam splitters and phase shifters implement arbitrary unitaries on modes: the Reck and Clements decompositions build any m×m mode unitary from O(m²) elements — a constructive theorem, and a pleasant numpy exercise. Interference of indistinguishable photons is the computational resource, which makes photon indistinguishability — spectral, temporal, and spatial purity — the hard systems requirement, and multi-photon interference fidelity the number to read first in any photonic paper. The same machinery is the entirety of boson sampling (42.7): the interferometer is the computer, and the output statistics across its ports are the result. Nothing else in the machine computes; the computation is the interference pattern.

### 42.5 Photonic gates

No photon–photon interaction means no deterministic gate from passive optics. Three answers exist. **KLM** (Knill–Laflamme–Milburn, 2001): measurement-induced gates — ancilla photons plus postselection make a two-qubit gate succeed with probability below 1 but announce its success, and gate teleportation chains these heralded gates into circuits. **Fusion gates**: probabilistic two-qubit measurements that stitch small entangled resource states into the large cluster states fault tolerance wants (PsiQuantum's architecture). **Matter-mediated gates**: atoms or quantum dots in cavities providing deterministic interaction — powerful but hardware-hard. Every route ends in multiplexing: massive redundancy in sources, paths, and timing so that probabilistic operations succeed almost always. The resource arithmetic follows from 31.3-style branch probabilities.

### 42.6 Measurement

Measurement is native and central: photonic computation is largely "prepare entangled states, measure, feed forward". Detectors are SNSPDs for photon counting (42.2) and homodyne or heterodyne detectors for continuous-variable encodings, which measure field quadratures — the route Xanadu takes with GKP qubits (42.8). Fast feed-forward electronics (microsecond scale) condition later operations on earlier outcomes, so the classical control plane is on the critical path of the quantum computation itself. Because every step is a measurement, classical post-processing throughput becomes a genuine architectural constraint, not an afterthought — the platform where the classical/quantum boundary is thinnest.

### 42.7 Boson sampling

The platform's native benchmark: send m indistinguishable photons through a large interferometer and sample the output distribution, which relates to matrix permanents — believed hard for classical computers (Aaronson–Arkhipov, 2011). USTC's Jiuzhang experiments (2020, 2021) claimed photonic quantum advantage with tens of photons; classical-algorithm groups then compressed the claim substantially — the same dynamic as 1.8, and a case study in honest benchmarking. Boson sampling is not universal quantum computing, but it validated the photonic stack end-to-end: sources, interferometers, detectors, and analysis at unprecedented scale. Xanadu's Borealis later made a programmable, cloud-accessible version — the photonic platform's public machine.

### 42.8 Photonic error correction

The error model is loss-dominated, so photonic QEC differs in kind from Part IX's models: use codes tolerant to erasure (you know *where* the photon was lost) and encode in states that fight loss directly. GKP qubits — grid states in an optical mode — were demonstrated with error correction on a photonic chip by Xanadu (2024), a below-threshold claim at small scale. Fusion-based fault tolerance (PsiQuantum) interconnects small resource states into a large code with loss tolerance built into the stitching. The resource arithmetic is unlike any other platform: millions of components, driven by the probability calculus of probabilistic gates (42.5). The bet is explicit — semiconductor fabs, not new physics, will close that gap.

## 43. Other Architectures

*Author: GLM-5.3*

> [!levels] Five levels of this chapter
> - **Intuition —** the big four do not exhaust the design space: spins in silicon, topological protection, and stabilized oscillator states attack the same problem from below, sideways, and above.
> - **Mathematics —** spin qubits are two-level Zeeman systems; cat qubits engineer noise bias, exponentially suppressing bit flips.
> - **Implementation —** simulate a biased-noise qubit: exponential bit-flip suppression with a linear phase-flip cost.
> - **Engineering —** silicon rides the semiconductor industry; topological remains unproven; cat qubits trade one error type for another, changing QEC arithmetic.
> - **Research —** each architecture bets the hardest problem can be solved in hardware rather than by error correction — someone will be right.

### 43.1 Spin qubits

The spin of a single electron (or hole) in a semiconductor as the qubit: |↓⟩ and |↑⟩ split by a magnetic field (the Zeeman effect), driven with microwave pulses. The attractions are stacked: nanometer scale (a million qubits fit a square centimeter on paper), coherence up to seconds in isotopically purified silicon, and — strategically the strongest — compatibility with existing CMOS fabrication. Two-qubit gates via exchange coupling of neighboring spins reach ~99–99.5% in small arrays (QuTech, Diraq, RIKEN). This is the platform with the best paper-scalability and the least cloud presence: devices today are single-digit to low-double-digit qubits, a decade behind superconductors in maturity but backed by fabs.

### 43.2 Quantum dots

The container for a spin qubit: an electrostatically defined island in Si/SiGe or GaAs where gate voltages confine exactly one electron. Neighboring dots couple spins through tunable exchange — the two-qubit gate; readout works by spin-to-charge conversion into a neighboring sensor dot. Crossbar architectures promise multiplexed wiring, addressing spin qubits' scaling on paper the way cryo-CMOS does for transmons (39.5). Progress is steady rather than spectacular: 6-qubit arrays with respectable fidelities by 2023–2025. Watch this space if your background is semiconductors — its problems (materials uniformity, yield, variability, cryogenic classical control) are classical engineering problems, which is precisely the platform's bet.

### 43.3 Silicon qubits

The materials story behind 43.1–43.2. Natural silicon carries nuclear spins that dephase electron spins; isotopically enriched ²⁸Si (99.99%+ zero nuclear spin) removes them, giving record coherence — T2 up to seconds. The remaining battle is at interfaces: Si/SiO₂ defects and valley physics, a surface-science problem attacked with fab-grade process control. Intel, imec, Diraq, and QuTech all bet that the semiconductor industry's decades of yield engineering transfer to qubits. For career planning this matters: the platform's openings look like materials science plus device engineering plus classical control software, and its fabrication base exists in far more countries than dilution-refrigerator supply chains do.

### 43.4 Topological approaches

Encode information in a global, topological property of a many-body state — concretely, Majorana zero modes in a superconductor–semiconductor hybrid wire — so that no local perturbation can read or corrupt it: error protection in hardware, potentially collapsing the overheads of Part X by orders of magnitude. The status must be stated honestly: the foundational experiments have a troubled history (a 2021 Nature paper retracted), and the 2025 "Majorana 1" topological-qubit chip claim drew scientific caution rather than acceptance. If real, the payoff is the largest in the field; the current evidence base is the thinnest of any architecture. Highest ceiling, lowest floor — treat claims with the 1.12 checklist.

### 43.5 Cat qubits

Encode a qubit in the two coherent states |−α⟩ and |+α⟩ of a superconducting oscillator, stabilized by engineered two-photon dissipation. The magic is noise **bias**: bit flips require tunneling between the two wells and are suppressed exponentially in the photon number |α|², while phase flips grow only linearly. Experiments (Alice & Bob, AWS) demonstrate exactly this trade. Why it matters: a hardware noise bias changes error-correction arithmetic — protecting against one error type needs only repetition-like codes rather than full surface codes, slashing the overhead estimates of Part X. The general lesson is bigger than this platform: engineer the error model, not just the error rate.

### 43.6 Hybrid architectures

Real machines will mix platforms by function: long-lived memories (cat qubits, ions), fast processors (transmons), and network links (photons), each doing what it does best. Early hybrids exist today: ions coupled to photons for networked modules (40.8), spin qubits read out through superconducting resonators, transmon memories with engineered dissipation. Modular architectures — many small, high-quality modules connected by teleported photonic entanglement — are the common answer to the wiring, size, and fabrication limits every platform hits when it scales alone (38.6). Expect the fault-tolerant era's machines to be federations rather than monoliths, and expect interconnect engineering — not qubit fabrication — to be the binding constraint.

### 43.7 Comparing physical tradeoffs

The honest summary, with numbers as of this writing — they move yearly, so verify against current calibration pages (38.7). Read the columns as a package: every platform buys its strength with a weakness, and no column is uniformly best.

| Platform | Coherence (T1/T2) | Two-qubit fidelity | Gate speed | Connectivity | Scalability outlook | Cloud access (2026) |
|----------|-------------------|--------------------|------------|--------------|---------------------|---------------------|
| Superconducting | ~100 µs / 50–200 µs | 99.0–99.9% | 20–300 ns | nearest-neighbor lattice | limited by wiring and cryogenics | IBM, Rigetti, IQM, OQC |
| Trapped ion | seconds to minutes | 99.9% and above | 10–600 µs | all-to-all within a chain | limited by chain size and shuttling | Quantinuum, IonQ |
| Neutral atom | seconds | 99.0–99.5% | 100 ns–1 µs | reconfigurable 2D geometry | arrays already reach thousands | QuEra, Pasqal |
| Photonic | unlimited in principle; loss dominates | gates are probabilistic | source and detector limited | built from resource states | needs extreme multiplexing | Xanadu; PsiQuantum limited |
| Spin qubits | seconds in ²⁸Si | around 99% | ~100 ns | nearest-neighbor dots | fab-compatible but early | research devices only |

For a remote user without institutional access — your situation — the cloud is the hardware. As of this writing: IBM Quantum offers free and paid superconducting access; AWS Braket fronts Rigetti, IonQ, OQC (superconducting), QuEra (neutral atoms), and more; Azure Quantum fronts Quantinuum and IonQ (ions) and Pasqal (atoms); Xanadu Cloud serves photonic machines. Everything in Parts III–X runs unchanged against any of them — only calibration numbers change.

> [!experiment] On your laptop — platform depth budget
> Coherence and fidelity both limit circuit depth. Compute both budgets for three platforms; the punchline is that at today's error rates, gate fidelity — not raw coherence — is what limits uncorrected circuits everywhere.
>
> ```python
> import numpy as np
>
> platforms = {
>     "superconducting": dict(t1=100e-6, tgate=30e-9,  err=1e-2),
>     "trapped-ion":     dict(t1=1e3,    tgate=300e-6, err=1e-3),
>     "neutral-atom":    dict(t1=1e3,    tgate=1e-6,   err=5e-3),
> }
>
> err_budget = 0.5   # cumulative error tolerated before results are garbage
>
> for name, q in platforms.items():
>     coherence_depth = int(q["t1"] / q["tgate"])
>     fidelity_depth = int(err_budget / q["err"])
>     print(f"{name:16s} coherence-limited depth ~{coherence_depth:>7d}"
>           f"   error-limited depth ~{fidelity_depth:>6d}")
> ```
>
> The superconducting row shows ~3,333 versus ~50: fidelity binds eight times earlier than decoherence. Rerun with err = 1e-3 to see what fault tolerance is buying.

> [!research] Research frontier
> Every platform's scaling story ends at the same wall: a single cryostat, trap, or array cannot host millions of high-quality qubits, so the field needs modular architectures — small, high-quality modules networked by teleported photonic entanglement (38.6, 40.8, 42.1). Inter-module entanglement rates today are orders of magnitude too slow for fault-tolerant throughput. Making module-to-module entanglement fast, heralded, and reliable is arguably the single most consequential open hardware problem — and parts of it (protocol design, rate modeling, classical control) are laptop-accessible, no cleanroom required.
