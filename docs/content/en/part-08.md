# Part VIII — Quantum Complexity

*Author: GLM-5.3*

You have now seen the algorithms — Deutsch, Grover, Shor, QFT, phase estimation. Before we turn to why hardware is hard, we owe the theoretical foundations an honest chapter: what complexity theory actually claims about quantum computers, what it does not, and where speedups genuinely come from. This is the part that protects you from the two symmetrical diseases of the field: hype ("quantum computers solve everything exponentially faster") and dismissiveness ("just parallel universes guessing"). Both die on contact with the material below.

## 27. Computational Complexity

*Author: GLM-5.3*

> [!levels] In this chapter
> **Lv1** you learn P, NP, EXP, and why "polynomial" is the dividing line. **Lv2** you learn reductions and complexity classes as a map of the computational world. **Lv3** you place BQP on that map — inside PSPACE, containing factoring, with P's relationship genuinely open. **Lv4** you can read oracle separations and know exactly what they do and don't prove. **Lv5** you can articulate the open problems (BQP vs NP, the power of QMA, the status of factoring in P) the way a researcher would.

### 27.1 P

P is the class of decision problems solvable in polynomial time — where the exponent is a fixed constant and the input size n is the variable. Sorting, shortest paths, primality (AKS, 2002), linear programming: all in P. "Polynomial" is the field's formalization of "scalable": O(n²) may be painful, but O(2ⁿ) is hopeless, and there is no natural class in between. The pragmatist's caveat, which you should never forget: a "polynomial" O(n¹⁰⁰) algorithm is worthless, and hardware constants matter — P is a statement about *asymptotic existence*, and engineering (Part XII) is about the constants P ignores. Quantum complexity inherits every one of these caveats.

### 27.2 NP

NP: problems whose *yes* answers have short certificates you can verify quickly — finding the certificate may be hard, checking it is easy. SAT, factoring-as-decision, Hamiltonian cycles, all of optimization's hardest darlings. NP-complete problems (Cook–Levin: SAT is universal) are the hardest in NP; solving one in polynomial time solves all of them. Two clarifications the popular press gets wrong constantly: NP does not mean "non-polynomial," and P vs NP is open — decades of effort, proof barriers (relativization, natural proofs, algebrization) catalogued, no resolution. Whether quantum computers touch NP is a precise, answerable question — see 27.10 — and the answer is the most-quoted negative result in the field.

### 27.3 Polynomial Time

Why worship polynomials? Three reasons. Closure: polynomials compose — a poly-time subroutine called poly-times stays poly, which is what lets complexity classes be closed under reduction. Robustness: the class is invariant under every reasonable machine model (RAM, Turing, λ-calculus — the Church–Turing thesis' quantitative cousin, the "extended Church–Turing thesis," is exactly the claim that *quantum* machines also don't change it — and Shor is the counterexample-in-waiting). Honesty: asymptotics encode the only insight that survives hardware churn. The engineer's translation: complexity classes tell you which battles are worth fighting; the exponent and constants tell you whether you'll win this year.

### 27.4 Exponential Time

EXP and friends: solvable with 2^poly(n) resources. Every problem is decidable in EXP, most interesting problems have exponential brute-force fallbacks, and the whole drama of algorithms is the gap between EXP and P. Quantum computing enters as a *partial* shrinker of that gap: Grover gives a generic √ speedup on any search-shaped problem (2ⁿ → 2^(n/2)), which is real and universal and — this is the letdown — nowhere near collapsing EXP to P. The structural lesson: quantum speedups are not one phenomenon; generic search speedup (quadratic), structural speedup (exponential, but only for problems with the right hidden algebra), and sampling speedups are three different animals. Part 28 taxonomizes them.

### 27.5 Reductions

A reduction is a translation: problem A reduces to B if a B-solver gives you an A-solver with polynomial overhead. It is complexity theory's only microscope — direct proofs of hardness are beyond current techniques, but reductions propagate difficulty across the map. For you: when someone claims quantum speedup for problem X, your first question is "reduced from what, or to what?" Reduction *from* a known-hard problem suggests depth; reduction *to* a known-easy structure is where quantum speedup claims usually die (the structured instance may be classically easy for reasons the reducer never checked). Reduction literacy is the difference between reading a quantum-advantage paper and being read by it.

### 27.6 Complexity Classes

The map, honestly drawn: P ⊆ BQP ⊆ PSPACE (proven); NP ⊆ PSPACE; whether BQP intersects NP-hard territory: unknown and believed mostly no (for decision problems); P vs BQP: open — Shor is evidence of separation, not proof. Add the quantum-flavored siblings: QMA (quantum certificates — the class of ground-state-energy problems, 28.6), QIP, BQC (verified delegated computation). The picture to keep: quantum computing carves *sideways* through the map — taking problems believed classical-hard (factoring, which sits in NP∩co-NP, outside believed-P but not NP-complete) into BQP, while leaving NP-complete problems standing.

### 27.7 BQP

BQP: problems solvable on a quantum computer in polynomial time, with error probability ≤ 1/3, uniformly. The definition's moving parts deserve attention: bounded error (amplifiable by repetition to 1/3ᵏ — the machinery of Part VII's repetition arguments), uniformity (one algorithm family, not per-input advice), polynomial in *n qubits and time*. Everything on IBM's and Google's roadmaps is an attempt to build a physical BQP machine at scale; everything in Part VII is BQP's greatest hits. The class is robust to the gate set (any reasonable universal set gives the same BQP) and to modest noise assumptions — which is what makes it an engineering target at all.

### 27.8 Quantum Speedups

Taxonomy before enthusiasm. *Exponential, structural*: factoring, discrete log, phase-estimation-flavored problems — require hidden algebraic structure; the speedup comes from the QFT revealing periodicity (Ch. 23). *Quadratic, generic*: Grover/amplitude amplification — works on any search, guaranteed, and quadratic is provably optimal for black-box search (BBBV bound). *Sampling*: random circuit sampling, boson sampling — provable separations under complexity assumptions, but verification is itself hard. *Simulation*: quantum chemistry, materials — Feynman's original proposal; the speedup claim rests on representing a quantum system with a quantum system. Four different beasts; four different evidence standards; all four get marketed identically, which is exactly why you need the taxonomy.

### 27.9 Oracle Separations

The field's main proof technology, and its most misused. An oracle O is a black-box function; a separation relative to O shows that with O given for free, quantum machines solve some task in fewer queries than classical ones. Simon's oracle separation (1994) directly inspired Shor. But separations *relative to an oracle* do not separate the classes themselves — the oracle may bake the structure in. TheBBBV theorem shows oracles where Grover's quadratic is optimal; recursive oracles (Aaronson–Kuperberg) separate QMA from QCMA both ways. Rule: oracle results are evidence about *technique*, not about *the world*. When a paper headlines an oracle separation, appreciate it, then ask what happens with the oracle instantiated.

### 27.10 What Quantum Computing Does Not Prove

The negative results are as load-bearing as the positive ones. One: BQP ⊆ PSPACE — quantum computers do not beat *all* classical computation, only efficient classical computation. Two: no known speedup for NP-complete problems; Grover's quadratic is the ceiling for unstructured search, and BBBV says no quantum trick beats it. Three: no-cloning forbids "try all answers in parallel and read them out" — the misunderstanding underlying half of all overclaims. Four: P vs NP and P vs BQP remain open; Shor's algorithm is a pointer, not a proof. Five: sampling speedups rest on unproven complexity assumptions. Fluency in these five is your defense against both hype and its overcorrection.

## 28. Where Quantum Speedups Actually Come From

*Author: GLM-5.3*

> [!levels] In this chapter
> **Lv1** you can name the sources: interference, amplitude amplification, hidden structure, sampling, simulation. **Lv2** you can trace each source in the algorithms of Part VII. **Lv3** you can predict, for a new problem, whether a quantum speedup is plausible — and justify the prediction. **Lv4** you can separate asymptotic from practical advantage, including the role of error-correction overhead. **Lv5** you can engage with the research frontier: dequantization (classical algorithms eating quantum claims), the search for new algorithmic primitives, and the open question of what BQP is really good for.

### 28.1 Brute-Force Misconceptions

The most damaging sentence in quantum computing: "it tries all 2ⁿ answers in parallel." If that were the mechanism, we'd collapse NP overnight — measure the satisfying assignment out of the superposition. We can't, because measurement samples the distribution we built, and building the right distribution *is* the problem. Parallelism in superposition is free; *reading anything useful out* costs. Every real speedup works not by trying more, but by arranging interference so that the answer's amplitude is large at measurement time — a constraint-driven optimization, not a brute-force windfall. Kill this misconception now; it will otherwise resurface in every meeting you ever sit in.

### 28.2 Interference

The universal mechanism. A quantum computation is a choreography of amplitudes: paths from input to wrong answers acquire phases that cancel; paths to right answers reinforce. Deutsch's algorithm is the minimal demonstration — one query, two paths, one destructive interference. Grover is the industrial version: reflect about the mean, reflect about the marked state, rotate amplitude where you want it, 2ⁿ/² times. QFT is interference as readout: phases accumulated along a register recombine into a period estimate. The design question is never "how do I try everything?" but "which phases do I kick where so the histogram ends up peaked?" — and that question has only a handful of known answering techniques.

### 28.3 Amplitude Amplification

The one *generic* primitive: given a checking procedure (oracle) and any preparation of a search space, amplify the good amplitude quadratically faster than random sampling — O(√(N/M)) queries for M marked items, provably optimal. Its generalizations cover most "quantum speedup" proposals in the wild: quantum counting (estimating M), fixed-point search, amplitude estimation (Monte Carlo with √ advantage — finance's favorite claim, Ch. 50), and boosting. Its limits are equally generic: quadratic only, oracle cost counts, and the input must be preparable. When evaluating any proposed quantum algorithm, locate it relative to amplitude amplification first; most are it, wearing a costume.

### 28.4 Hidden Structure

Exponential speedups live here, and the gate is narrow: the problem must contain algebraic structure that the QFT can expose — periodicity (Shor: f(x+r) = f(x)), hidden subgroup (the generalization; efficient for abelian groups, open for non-abelian — which is why graph isomorphism and lattice problems remain classical-side), hidden shift, phase estimation of accessible unitaries. Note what's absent: no NP-complete problem is known to reduce to a hidden-subgroup problem over an abelian group. The engineering moral: exponential quantum advantage is *rare and structural*, not a general-purpose accelerant. Roadmap claims of "exponential speedup for your industry" should be audited against this gate.

### 28.5 Sampling Problems

Provable separations without structure: sample from distributions that are easy to prepare quantumly and believed hard classically. Random circuit sampling (Google 2019), boson sampling (photonic), IQP circuits. The evidence standard: separation holds *under complexity assumptions* (polynomial hierarchy doesn't collapse) and the verification story is statistical (XEB), not absolute — critics like Kalai have pushed hard on exactly this. Practical payoff is currently nil: the distributions sampled have no known use. The scientific payoff is enormous: these are the only controlled experiments testing whether BQP machines outperform classical ones at all. Read supremacy-era papers as physics experiments with complexity-theory error bars.

### 28.6 Simulation Problems

Feynman 1982: nature isn't classical, so simulate physics with quantum machinery. This is the most defensible speedup class because it requires no hidden algebra — representing an n-body quantum system's state classically costs exponential space *by construction* (Part V!), while 2n qubits do it natively. Quantum chemistry (ground-state energies for catalysis, Ch. 48), materials (high-Tc superconductors), nuclear and condensed-matter dynamics, and — increasingly — quantum-enhanced verification of quantum hardware itself. The catch is precision: chemical accuracy needs error correction at scale, which is why simulation is the *roadmap* application, not the NISQ one. Ch. 48 gives the honest state of play.

### 28.7 Algebraic Structure

Zoom out and the pattern sharpens: every exponential speedup runs through algebra — Fourier transforms over groups, periodicity, eigenvalue access. This is both a map (where to hunt for new algorithms: quantum walk on structures, linear-systems problems with structured oracles — HHL's caveats being the cautionary tale, Ch. 49) and a wall (structureless problems are quantumly boring: BBBV). The dequantization saga is the wall in motion: Tang's 2019 classical algorithm ate the claimed speedups for recommendation-systems-flavored linear algebra by exploiting the same structure classically *plus* sample access. Current best practice: assume every structure-based quantum claim has a classical competitor until you've checked the last five years of literature.

### 28.8 Quantum Complexity Theory

The living theory beyond BQP: QMA (quantum NP — local Hamiltonians are QMA-complete; the quantum chemistry "hard even for quantum computers in the worst case" caveat), QQC and adiabatic classes, query-complexity lower bounds (polynomial method, adversary method — the tools that *prove* Grover optimal), and the interplay with cryptography (lattices resist known quantum attacks — post-quantum crypto's foundation, Ch. 46). If research calls to you (Part XIV), this is the subfield where a software engineer's skill at *implementation and empiricism* meets open theory: lower-bound techniques in particular are under-explored computationally, and machine-assisted proof is young.

### 28.9 Practical vs Asymptotic Speedup

The final filter. Asymptotic: for large enough n, quantum wins. Practical: at the sizes anyone cares about, on real hardware, with error-correction overhead included. The gap between them is where careers and companies have been lost. Concretely: Shor's asymptotic advantage is exponential, but factoring RSA-2048 needs ~4,000 logical qubits and ~10⁹ logical gates — a machine that doesn't exist yet (Starling-class, ~2029+, and Starling targets 100 logical qubits, not 4,000). Grover vs AES-128 needs ~3,000 logical qubits running 2⁶⁴ iterations for days. The honest analysis every engineer owes their stakeholders: *pipeline the whole stack* — algorithm → logical qubits → physical qubits → hours → dollars — before quoting any speedup. Part XIX builds that spreadsheet.

> [!research] The hunt for new primitives
> Between 1994 (Shor) and today, the list of genuinely new quantum algorithmic primitives is short: amplitude amplification, QFT/phase estimation, quantum walks, HHL-style linear algebra, variational methods, and quantum signal processing/qubitization (2010s — the cleanest unification of "structured" speedups, and the engine behind the best known bounds for quantum chemistry). Each new primitive historically unlocked a decade of applications. The open hunt — for primitives beyond these, for non-abelian hidden subgroup techniques, for speedups in sampling that are *verifiable*, for dequantization-resistant linear algebra — is one of the healthiest research fronts for a newcomer: the field's central question ("what is BQP actually good for?") is wide open, and progress is measured in ideas, not cryostats.
