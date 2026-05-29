# Quantum Fusion POC — tungsten–hydrogen binding via VQE

A small, honest prototype: compute the binding behaviour of a tungsten–hydrogen
system on a quantum computer using the Variational Quantum Eigensolver (VQE).
The fusion-reactor motivation is real; the current quantum hardware can only
handle a tiny version of the problem. This repo demonstrates the **workflow**
on the smallest meaningful instance, with a code skeleton that scales to the
real problem when fault-tolerant hardware arrives (~2029+).

> [!IMPORTANT]
> **What this is.** A methodology proof. Three Jupyter notebooks that
> walk you from "Hello, Bell state" up to a 6-circuit-qubit VQE on
> tungsten hydride anion (WH⁻).
>
> **Hardware status (2026-05-28).** All three notebooks have been
> executed end-to-end on real IBM Quantum hardware — Bell state on
> `ibm_marrakesh`, H₂ single-point validation on `ibm_marrakesh`, WH⁻
> single-point validation on `ibm_fez`. Each result is captured in
> [`results/qpu_runs/`](results/qpu_runs/) with the raw counts /
> energies, backend, job ID, and shot count. No error mitigation was
> applied — the noise figures you'll see in the result table are the
> *unmitigated* hardware cost.
>
> **What this is not.** A production tungsten-binding calculator. The
> physical system that matters for fusion reactor walls (a W₈ vacancy
> cluster + embedded hydrogens) needs ~200 error-corrected *logical*
> qubits and fault-tolerant hardware. We're not there yet — globally —
> in 2026.
>
> The numbers in this repo are deliberately scoped to be reproducible
> on the IBM Open plan (free tier).

---

## The fusion problem in one paragraph

ITER, DEMO, and every other deuterium–tritium fusion reactor design uses
tungsten as a plasma-facing wall material. Tungsten traps tritium atoms in
its lattice — that's a radioactive-inventory problem (tritium is expensive,
hard to recover, and regulated). Predicting *how strongly* tungsten holds
onto hydrogen at the electronic-structure level is one of the workloads
quantum chemistry is expected to do well at, eventually. The transition
metals in tungsten have strongly correlated d-electrons that classical
methods (DFT, even high-level coupled cluster) struggle with.

## The today ↔ future story

```
   Today (this repo)              Future (2029+, FT hardware)
   ┌─────────────────────┐        ┌──────────────────────────────┐
   │ WH⁻ molecule        │        │ W₈ vacancy cluster + H atoms │
   │ 4 active electrons  │ ───→   │ 20+ active electrons         │
   │ 4 active orbitals   │ same   │ 20+ active orbitals          │
   │ 6 circuit qubits    │ code   │ 200+ logical qubits          │
   │ (post Z₂-tapering)  │ skel-  │ (error-corrected)            │
   │ EfficientSU2 ansatz │ eton   │ UCCSD-trotterized or QPE     │
   │ Aer simulator       │        │ fault-tolerant QPU           │
   │ Bell verified on    │        │ Full optimization on QPU     │
   │  ibm_marrakesh      │        │ → chemical accuracy          │
   │ → 3.11 eV (caveat!) │        │                              │
   └─────────────────────┘        └──────────────────────────────┘
        Bell verified on ibm_marrakesh (2026-05-27).
        H₂ single-point QPU validation on ibm_marrakesh (2026-05-28).
        WH⁻ single-point QPU validation on ibm_fez (2026-05-28).
```

### A note on the word "qubits"

You'll see "qubits" used in this repo to mean three different things.
This is the convention used in the field, but it's easy to confuse:

| Term | Meaning | Example in this repo |
|---|---|---|
| **Spin-orbital qubits** | Raw count from the fermion-to-qubit mapping (1 spin-orbital → 1 qubit) | CAS(4, 4) → 8 spin-orbital qubits |
| **Circuit qubits** | After Z₂ symmetry tapering — what actually runs on the chip | WH⁻ ParityMapper(2-tapered) → **6 circuit qubits** |
| **Logical qubits** | Error-corrected qubits in a fault-tolerant system. Each backed by hundreds or thousands of physical qubits. | Future fusion-wall problem → **200+ logical qubits** |
| **Physical qubits** | Raw qubits on today's NISQ chips, no error correction | `ibm_marrakesh` has **156 physical qubits** |

When this README says "6 qubits" it means circuit qubits. When it says "200
qubits" it means logical qubits. The order-of-magnitude jump between them
is what fault tolerance unlocks.

## The three notebooks

| Notebook | Circuit qubits | What it teaches | Hardware status |
|---|---|---|---|
| **`01_hello_quantum.ipynb`** | 2 | Save credentials, build a Bell state, run on Aer, then on a real IBM QPU. Counts-based view of entanglement and noise. | Bell run completed on `ibm_marrakesh` (2026-05-27) |
| **`02_h2_binding.ipynb`** | 2 | Full VQE on H₂ with a hardcoded STO-3G parity-mapped Hamiltonian. Recovers the FCI ground state to ~2.45 nHa on the simulator. | Aer-trained + QPU single-point validated on `ibm_marrakesh` (ΔE ≈ 30.6 mHa, no mitigation) |
| **`03_wh_binding.ipynb`** | 6 | The main event. Tungsten hydride anion via pyscf + qiskit-nature. CAS(4,4) active space → ParityMapper → EfficientSU2(reps=4). Computes a potential-energy curve. | Aer-trained + QPU single-point validated on `ibm_fez` (ΔE ≈ 199.8 mHa, no mitigation) |

## Quickstart (Windows)

```cmd
git clone https://github.com/<your-user>/quantum-fusion-poc.git
cd quantum-fusion-poc

python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements-windows.txt

REM Set your IBM Quantum token — get one at https://quantum.cloud.ibm.com
set IBM_QUANTUM_TOKEN=your_token_here

jupyter notebook
```

Open `notebooks/01_hello_quantum.ipynb` and run all cells. Skip the last cell
(real QPU submission) if you'd rather not spend QPU minutes.

For `03_wh_binding.ipynb` you need WSL2 + a Linux venv because pyscf has no
Windows wheels. See [`setup/`](setup/) for the launcher and instructions.

## Verified on real IBM Quantum hardware

The Bell state in `01_hello_quantum.ipynb` was run on **`ibm_marrakesh`**
(156-qubit Heron r2 processor). Raw counts from 1024 shots:

| Outcome | Counts | Expected (noiseless) |
|---|---|---|
| `00` | 493 | ~512 |
| `11` | 503 | ~512 |
| `01` | 9   | 0 |
| `10` | 19  | 0 |

The 28 spurious `01`/`10` counts are the noise signature — about 2.7% of
shots violated the perfect *correlation* of the Bell |Φ+⟩ state (both
qubits should always agree: `00` or `11`, never one of each). **That
number is the whole reason we use error mitigation, and ultimately
fault tolerance, for serious chemistry.** Full record at
[`results/qpu_runs/bell_marrakesh_2026-05-27.json`](results/qpu_runs/bell_marrakesh_2026-05-27.json);
original job ID `d8bccr4e6kns73aasfi0` (retrievable from the IBM job archive
within IBM's retention window).

## H₂ and WH⁻ single-point QPU validation

Both VQE notebooks have been validated on real IBM Quantum hardware
using the train-on-simulator, validate-single-point-on-QPU pattern
(see [`docs/concepts/06-sim-vs-qpu.md`](docs/concepts/06-sim-vs-qpu.md)).
The simulator-optimal parameters θ\* were locked into JSON files, then
the same circuits were submitted to the least-busy operational backend
at exactly those parameters. No error mitigation.

> [!WARNING]
> **The WH⁻ unmitigated QPU energy is physically uninformative as a
> binding-energy estimate.** Read the table as a *noise-scaling
> measurement*, not a chemistry result. The 199.8 mHa hardware cost
> at WH⁻'s circuit depth **exceeds** the ~110 mHa well depth the
> simulator computed — meaning the bare hardware energy at θ\* sits
> well above the dissociation asymptote. The H₂ row is a useful
> noise figure; the WH⁻ row says "circuits this deep are not yet
> usable for serious chemistry without mitigation."

| Run | Backend | E_sim | E_qpu | ΔE (lumped hardware cost) | Artifact |
|---|---|---|---|---|---|
| H₂ (2 circuit qubits, EfficientSU2 reps=2) | `ibm_marrakesh` | -1.857275 Ha | -1.826635 Ha | **+30.6 mHa = +834 meV** | [`h2_qpu_validation_2026-05-28.json`](results/qpu_runs/h2_qpu_validation_2026-05-28.json) |
| WH⁻ (6 circuit qubits, EfficientSU2 reps=4 full) | `ibm_fez` | -67.443 Ha | -67.243 Ha | **+199.8 mHa = +5,438 meV** *(see warning above — exceeds well depth)* | [`wh_qpu_validation_2026-05-28.json`](results/qpu_runs/wh_qpu_validation_2026-05-28.json) |

The two backends are different physical machines but the same Heron r2
generation (156 qubits each, same gate set), so the ΔE comparison
reflects circuit-depth scaling, not a same-chip apples-to-apples noise
measurement.

The two ΔE values tell the same story: **noise scales steeply with
circuit depth**. WH⁻'s circuit is ~10× deeper than H₂'s (60 parameters
vs 12, full vs linear entanglement), and its noise floor is ~6.5× worse
(199.8 / 30.6 ≈ 6.53). For H₂ the QPU result is ~10× worse than chemical
accuracy. For WH⁻ — as the warning above states — the noise *exceeds*
the well depth, so the unmitigated QPU energy at θ\* is physically
uninformative. That's the expected NISQ-era lesson — this is why
error mitigation (ZNE, PEC) and ultimately fault tolerance matter for
serious chemistry.

ΔE here is a **lumped cost**: shot noise + readout error + compounding
gate errors + transpilation effects + backend drift, all conflated into
one number. Disentangling them needs additional calibration circuits,
which a follow-on phase could add.

## Result snapshot

| Quantity | Value | Reference / caveat |
|---|---|---|
| H₂ ground-state energy (sim, VQE) | −1.857275 Ha | Matches FCI to 2.45 nHa |
| H₂ ground-state energy (QPU, unmitigated) | −1.826635 Ha | `ibm_marrakesh`, 4096 shots |
| H₂ binding energy (sim) | 5.55 eV | Literature D_e ≈ 4.52 eV — STO-3G overbinds; explained in notebook |
| WH⁻ ground-state energy (sim, VQE) | −67.443 Ha | CASCI reference: −67.4545 Ha. Sim error 11.3 mHa. |
| WH⁻ ground-state energy (QPU, unmitigated) | −67.243 Ha | `ibm_fez`, 4096 shots. ΔE vs sim ≈ 200 mHa — **exceeds the sim well depth, see warning above the QPU table**. |
| WH⁻ well depth (Approach B, basis-consistent, sim) | 3.11 eV | **Not** the experimental binding energy of neutral WH (see Caveats). The QPU energy row above does NOT support a "QPU recovered the binding energy" reading. |

### Caveats (read before quoting numbers)

- **The "WH⁻ well depth" is not the experimental binding energy of WH.**
  WH⁻ closed-shell singlet was chosen as a tractable proxy that fits the
  qubit budget. Neutral WH is a ⁶Σ⁺ sextet (5 unpaired electrons), open-shell,
  intractable in a 4–6 qubit active space. The 3.11 eV landing near
  literature values for neutral WH is coincidental error cancellation, not
  physics. The notebook documents this explicitly.
- **VQE at 6 circuit qubits, EfficientSU2(reps=4) is demonstration-grade,
  not production-grade.** 11.3 mHa error is ~7 kcal/mol, well above
  chemical accuracy (1 kcal/mol). UCCSD or a deeper hardware-efficient
  ansatz would do better but is computationally prohibitive at this scale.
- **STO-3G + LANL2DZ is a tiny basis.** Production chemistry uses
  def2-TZVPD-J or larger; that's a 10–100x cost multiplier and is why the
  larger active spaces below need fault-tolerant hardware.

## Repo layout

```
quantum-fusion-poc/
├── README.md                    ← you are here
├── LICENSE                      ← MIT
├── requirements-windows.txt     ← for notebooks 01, 02
├── requirements-wsl.txt         ← for notebook 03 (pyscf)
├── notebooks/                   ← the three notebooks, in learning order
│   ├── 01_hello_quantum.ipynb
│   ├── 02_h2_binding.ipynb
│   └── 03_wh_binding.ipynb
├── docs/
│   ├── walkthrough.html         ← visual narrative, open in any browser
│   └── concepts/                ← short visual primers (qubits, VQE, ...)
├── results/
│   └── wh_minus_pec.png         ← potential-energy curve chart
└── setup/
    ├── start-wh-jupyter.cmd     ← launches Jupyter inside WSL
    └── clean_notebook_outputs.py ← strips outputs before committing
```

## Concepts (for newcomers)

If "qubit", "Hamiltonian", or "active space" are unfamiliar, start with the
[walkthrough](docs/walkthrough.html) — a single self-contained HTML page that
explains the whole project in plain language with diagrams. Then dip into
[`docs/concepts/`](docs/concepts/) for short visual primers on individual
topics. Common questions are collected in [`docs/FAQ.md`](docs/FAQ.md).

## Scaling roadmap

| Stage | Qubit count | Qubit type | Hardware | Timeline |
|---|---|---|---|---|
| This POC | 6 | circuit (post-tapering) | NISQ simulator + completed unmitigated single-point QPU validation (2026-05-28) | Today |
| Larger WH⁻ basis (def2-SVPD, CAS(6,6)) | ~10 | circuit (post-tapering) | Same NISQ pattern, more QPU minutes | Today, paid plan |
| Multi-atom W cluster (W₂, W₃ + H) | 20–40 | circuit (post-tapering) | Late-NISQ + error mitigation | ~2027 |
| Tungsten vacancy + H trapping (W₈ + vacancy) | 200+ | logical (error-corrected) | Fault-tolerant QPU | 2029+ |

The same code skeleton in `03_wh_binding.ipynb` extends through all four
stages. What changes is the geometry, basis, active space, ansatz, and
backend.

## License

MIT. See [`LICENSE`](LICENSE).

## Acknowledgements

Built on Qiskit, qiskit-nature, qiskit-ibm-runtime, and pyscf. Tungsten ECP
data from the LANL2DZ basis set. Honest framing influenced by ongoing
community discussion of NISQ-era quantum-chemistry claims — the goal here is
to demonstrate methodology, not to overclaim results.
