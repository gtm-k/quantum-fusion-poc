# Frequently asked questions

Quick answers to the questions this POC tends to provoke. Skim it for the
parts that interest you; nothing builds on anything else.

If a question you have isn't covered, the [walkthrough](walkthrough.html)
or the [concept primers](concepts/) are likely the right next read.

---

## Scope and framing

### Q: "Did this beat classical methods?"

**A:** No, and it shouldn't be expected to. The active space we use —
CAS(4, 4) — is small enough that classical CASCI computes the *exact*
ground state in milliseconds. This POC isn't a quantum-advantage
demonstration; it's a workflow demonstration on the smallest meaningful
instance. **Quantum advantage for chemistry is a 2029+ fault-tolerant
story** — see [`docs/concepts/05-scaling-roadmap.md`](concepts/05-scaling-roadmap.md).

### Q: "What's the practical benefit today?"

**A:** Methodology readiness. The same code in `03_wh_binding.ipynb`
scales — by changing parameters, not architecture — to the active spaces
that fault-tolerant hardware will unlock. Whoever picks up this repo in
2029 with 200 logical qubits can swap the geometry, basis, active space,
and backend without rewriting the pipeline.

### Q: "Why these specific molecules?"

**A:** Three notebooks form a learning ladder.
- `01_hello_quantum.ipynb` — Bell state. Smallest non-trivial quantum
  circuit. Validates the toolchain.
- `02_h2_binding.ipynb` — H₂ at the STO-3G level. Smallest non-trivial
  quantum *chemistry* problem. Has a known exact answer (FCI) to compare against.
- `03_wh_binding.ipynb` — WH⁻ via pyscf. The smallest tungsten-hydrogen
  system that fits a 6-qubit budget while still containing real
  transition-metal correlation physics.

---

## Methodology

### Q: "How is this different from a regular pyscf calculation?"

**A:** pyscf does the *classical* part — Hartree-Fock reference, integral
generation, FCIDump export. VQE then finds the correlated ground state by
optimizing a quantum circuit. At this size pyscf could do the whole
calculation classically (it's CASCI at CAS(4,4)) — the point is that the
scaffold extends to active spaces pyscf can't handle on its own.

### Q: "Why WH⁻ instead of neutral WH?"

**A:** WH⁻ is a closed-shell singlet (16 valence electrons, all paired) —
qiskit-nature's `ActiveSpaceTransformer` handles it cleanly. Neutral WH is
a ⁶Σ⁺ sextet (5 unpaired electrons), which `ActiveSpaceTransformer` in
qiskit-nature 0.7 can't slice properly. WH⁻ keeps the W–H σ-bond physics
while fitting the qubit budget. **Important caveat:** the "well depth"
we compute is for WH⁻, not the experimental binding energy of WH — those
are different quantities. The 3.11 eV number landing close to literature
WH values is coincidental error cancellation, not validation. We document
this explicitly in the notebook.

### Q: "Why this ansatz (EfficientSU2) rather than UCCSD?"

**A:** UCCSD is chemistry-aware and would give higher accuracy. But at
6 qubits with our integrals it takes ~24 minutes per cost-function call
— that's days for a full VQE convergence. EfficientSU2 is
hardware-efficient: shallow, fast, robust. It gets us to ~11 mHa accuracy
in minutes. For a methodology demonstration that's the right tradeoff.
For production work, UCCSD or its successors.

### Q: "How accurate is the result?"

**A:** For H₂: ~2.45 nanohartree from the FCI reference — essentially
exact within the chosen basis. For WH⁻: 11.3 mHa from the CASCI reference,
which is roughly 300 meV or 7 kcal/mol. **That is well above chemical
accuracy (1 kcal/mol).** This is demonstration-grade, not
production-grade. The error budget would shrink with UCCSD or deeper
EfficientSU2 — and could be driven to whatever precision you like with QPE
on fault-tolerant hardware, *within the chosen basis and active space*
(the basis-set and active-space limitations remain).

---

## Hardware

### Q: "Did you actually run any of this on a real quantum computer?"

**A:** Yes — all three notebooks have been executed on real IBM Quantum
hardware end-to-end as of 2026-05-28.
- **Bell state** (`01_hello_quantum.ipynb`): submitted to `ibm_marrakesh`
  on 2026-05-27. Counts showed the expected entanglement signature
  (~50% `00`, ~50% `11`) plus a ~2.7% error from spurious `01`/`10`
  outcomes that violate perfect correlation. Job ID
  `d8bccr4e6kns73aasfi0`. Full record in
  [`results/qpu_runs/bell_marrakesh_2026-05-27.json`](../results/qpu_runs/bell_marrakesh_2026-05-27.json).
- **H₂ single-point** (at simulator-optimal θ\*): submitted to
  `ibm_marrakesh` on 2026-05-28. ΔE = E_qpu − E_sim ≈ +30.6 mHa = +834
  meV (no mitigation). Job ID `d8cd09j8amns73bjcan0`.
- **WH⁻ single-point** (at simulator-optimal θ\*): submitted to `ibm_fez`
  on 2026-05-28. ΔE ≈ +199.8 mHa = +5,438 meV (no mitigation).
  **Important read:** this ΔE *exceeds* the ~110 mHa well depth the
  simulator computed, which means the unmitigated QPU energy at θ\* sits
  above the dissociation asymptote and is physically uninformative as a
  binding-energy estimate. The value of this measurement is as a
  *noise-scaling data point*, not a chemistry result. Job ID
  `d8cd4hajki0s73ar3jj0`.

The two single-point ΔE values together quantify how noise scales with
circuit depth on this generation of hardware — see the README's
"H₂ and WH⁻ single-point QPU validation" section.

### Q: "Why don't you run full VQE on a real QPU?"

**A:** Math: a 6-qubit VQE with ~60 parameters takes ~2000 cost-function
evaluations to converge. At ~10 sec per QPU call, that's 5.5 hours of
hardware time. IBM Open plan gives 10 minutes per month. The pattern
that *does* fit — train on simulator, validate single-point on QPU — is
covered in [`docs/concepts/06-sim-vs-qpu.md`](concepts/06-sim-vs-qpu.md).

### Q: "Can you do error mitigation?"

**A:** Yes, via `qiskit-ibm-runtime`'s `EstimatorV2.options.resilience_level`.
Level 1 enables TREX (twirled readout error extinction). Level 2 adds ZNE
(zero-noise extrapolation). Each level costs more shots. We don't enable
mitigation in the current POC because the free-tier shot budget is
already tight; that's a stretch goal once we move to a paid plan or
larger time grants.

### Q: "Why is the WH⁻ noise worse than H₂?"

**A:** Circuit depth. EfficientSU2(reps=4, full entanglement) on 6 qubits
gives a circuit ~30 layers deep with on the order of 100 two-qubit gates
after transpilation. Every two-qubit gate has ~0.5% error and they
compound. H₂'s EfficientSU2(reps=2, linear) on 2 qubits is dramatically
shallower — only a handful of two-qubit gates — so the noise budget is
much smaller. The measured ΔE ratio (199.8 / 30.6 ≈ 6.5×) is the empirical
version of this scaling. Fault tolerance is what removes this entirely.

---

## Fusion context

### Q: "How does this connect to fusion reactors?"

**A:** Tritium retention in tungsten plasma-facing walls is a quantitative
problem: predicting binding energies of hydrogen isotopes in defective
tungsten lattices requires accurate electronic structure for transition
metal systems. Classical methods struggle (DFT functionals disagree with
experiment by 30+% on these systems; coupled cluster doesn't scale to
defect-cluster geometries). It's one of the canonical "useful chemistry
that quantum computers should eventually be able to do."

### Q: "So when will this matter for real fusion design?"

**A:** When fault-tolerant quantum hardware exists at the ~200 logical
qubit scale. That's plausibly 2029+ for first useful demonstrations,
mid-2030s for routine production use. The roadmap details are in
[`docs/concepts/05-scaling-roadmap.md`](concepts/05-scaling-roadmap.md).
This POC is the workflow scaffold for that future.

### Q: "Isn't ITER already operational with DFT-level binding predictions?"

**A:** Yes — and the disagreement between predicted and measured tritium
retention is a known source of operational uncertainty. Better
electronic-structure methods would reduce uncertainty in tritium inventory
projections, which matters for safety case modelling, fuel cycle design,
and regulatory approval. Improving the precision is the value proposition,
not enabling something that's currently impossible.

---

## Repo and methodology meta

### Q: "Why two requirements files?"

**A:** pyscf has no Windows wheels and its source build fails on Windows
out of the box. Notebook 03 needs pyscf; notebooks 01 and 02 don't. So
notebook 03 runs in a WSL2 Ubuntu venv while 01 and 02 run in a Windows
venv. The launcher (`setup/start-wh-jupyter.cmd`) bridges the two by
starting Jupyter inside WSL while pointing at the Windows-side notebook
folder.

### Q: "What's the next concrete improvement to this code?"

**A:** Three in order of cost/value (the original "single-point QPU
validation" item was completed on 2026-05-28 — see the result table in
the README):
1. **Error mitigation on the WH⁻ QPU run** — TREX + ZNE via
   `EstimatorV2.options.resilience_level=2`. Goal: bring the 199.8 mHa
   noise floor low enough to be smaller than the well depth. Costs more
   shots, fits a paid plan or a single deliberate Open-tier burn.
2. **Larger active space** — CAS(6,6) → ~10 circuit qubits, still
   NISQ-tractable, much better simulator accuracy (~paid tier).
3. **Larger basis** — def2-SVPD for the H side at least, to fix the
   well-depth basis-imbalance issue (~mostly classical cost, not QPU).

### Q: "Is this safe to share publicly?"

**A:** The repo is built private-first so we can audit it before flipping
to public. Specifically we've checked: no leaked API tokens (env-var
pattern, never in code); no proprietary data; no overclaiming in any
narrative; MIT licence; all numbers reproducible from the notebooks.

### Q: "What does this POC deliberately not address?"

**A:** Three substantive gaps a reader should know about:
- **The variational principle is taken as given.** We use ⟨ψ|Ĥ|ψ⟩ ≥ E_ground
  as the foundation of VQE without deriving it. Readers wanting the proof
  should consult a quantum-mechanics textbook (Sakurai, Griffiths) — it's
  one page of linear algebra.
- **Ansatz selection trade-offs are decided, not analysed.** We chose
  EfficientSU2 over UCCSD for cost reasons (see "Why this ansatz" above)
  but didn't sweep ansatz families systematically. A production version
  would benchmark adaptive ansätze (ADAPT-VQE), problem-aware variants
  (k-UpCCGSD), and chemically-motivated reductions before committing.
- **Error mitigation is mentioned, not deployed.** TREX/ZNE/PEC are
  described in [concept 6](concepts/06-sim-vs-qpu.md) but the current
  QPU validation runs are unmitigated. Enabling mitigation is the
  natural next step on a paid plan.
