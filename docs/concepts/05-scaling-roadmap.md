# Scaling roadmap

> **One-line take:** Today's quantum computers can do toy chemistry; the
> real fusion-wall problem needs hardware that doesn't exist yet but is on
> a credible roadmap. The same code in this repo bridges both eras.

## The visual

```
   algorithmically
   useful qubits
   (see note ↓)
     ↑
 200 │                                                            ●
     │                                              Full FT QPU  ╱
     │                                              W₈ vacancy  ╱
     │                                              cluster + H╱  ← 2029+
     │                                                        ╱     (logical)
 100 │                                                       ╱
     │                                          ●  multi-W  ╱
     │                                          ╱  cluster ╱ (logical)
  50 │                                         ╱
     │                                ●       ╱  ← 2027+
     │                       early FT╱           larger basis
     │              ●               ╱            CAS(10,10) (circuit)
  10 │              ╱  larger      ╱
     │      ●      ╱   active     ╱
   6 │ ─── ╱──────╱── space ─────╱  ← THIS POC (2026)
     │ WH⁻ ────────────────────             6 circuit qubits, NISQ noise
   2 │   H₂
     │ Bell  (circuit qubits)
     └──────────────────────────────────────────────────────→ year
       2025      2027         2029           2031        2033
       NISQ      early-FT     fault-tolerant  practical  quantum
       ~150q     thousands    millions of     advantage   simulation
       noisy    physical q    physical q      for chem    standard
```

<svg viewBox="0 0 480 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Quantum hardware scaling roadmap with chemistry milestones">
  <!-- axes -->
  <line x1="50" y1="240" x2="460" y2="240" stroke="#333" stroke-width="1.2"/>
  <line x1="50" y1="20" x2="50" y2="240" stroke="#333" stroke-width="1.2"/>
  <text x="20" y="130" font-family="sans-serif" font-size="11" fill="#333" transform="rotate(-90 20,130)">qubits — circuit (NISQ) / logical (FT)</text>
  <text x="255" y="265" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">year</text>

  <!-- year labels -->
  <text x="90" y="255" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">2026</text>
  <text x="175" y="255" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">2027</text>
  <text x="260" y="255" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">2029</text>
  <text x="345" y="255" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">2031</text>
  <text x="430" y="255" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">2033+</text>

  <!-- qubit milestone labels -->
  <text x="42" y="230" text-anchor="end" font-family="sans-serif" font-size="9" fill="#555">2</text>
  <text x="42" y="210" text-anchor="end" font-family="sans-serif" font-size="9" fill="#555">6</text>
  <text x="42" y="170" text-anchor="end" font-family="sans-serif" font-size="9" fill="#555">20</text>
  <text x="42" y="120" text-anchor="end" font-family="sans-serif" font-size="9" fill="#555">50</text>
  <text x="42" y="70" text-anchor="end" font-family="sans-serif" font-size="9" fill="#555">100</text>
  <text x="42" y="35" text-anchor="end" font-family="sans-serif" font-size="9" fill="#555">200</text>

  <!-- trajectory curve -->
  <path d="M 70 220 Q 130 200 175 170 Q 230 130 285 80 Q 350 45 440 30" fill="none" stroke="#2980b9" stroke-width="2.5" stroke-dasharray="5,3"/>

  <!-- milestones (each labeled with qubit type so they aren't conflated) -->
  <circle cx="80" cy="225" r="5" fill="#27ae60"/>
  <text x="80" y="218" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#27ae60">Bell + H₂ (circuit)</text>

  <circle cx="100" cy="210" r="5" fill="#c0392b"/>
  <text x="100" y="201" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#c0392b" font-weight="bold">THIS POC</text>
  <text x="100" y="190" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#c0392b">WH⁻ 6q (circuit)</text>

  <circle cx="175" cy="170" r="5" fill="#8e44ad"/>
  <text x="175" y="160" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#8e44ad">CAS(10,10) (circuit)</text>
  <text x="175" y="150" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#8e44ad">larger basis</text>

  <circle cx="240" cy="125" r="5" fill="#d35400"/>
  <text x="240" y="115" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#d35400">multi-W cluster (early-FT)</text>

  <circle cx="305" cy="75" r="6" fill="#c0392b" stroke="#333" stroke-width="1"/>
  <text x="305" y="65" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#c0392b">W₈ vacancy + H (logical)</text>
  <text x="305" y="55" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#c0392b" font-weight="bold">production target</text>

  <!-- shaded zones -->
  <rect x="50" y="20" width="120" height="220" fill="#e8f4f8" fill-opacity="0.4"/>
  <text x="110" y="30" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#2980b9">NISQ era</text>

  <rect x="170" y="20" width="100" height="220" fill="#fdf2e6" fill-opacity="0.5"/>
  <text x="220" y="30" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#d35400">early FT</text>

  <rect x="270" y="20" width="190" height="220" fill="#eafaf1" fill-opacity="0.5"/>
  <text x="365" y="30" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#27ae60">fault-tolerant era</text>
</svg>

**About the y-axis (read this before drawing comparisons).** The "qubits"
number means different things at different points on the chart. NISQ-era
markers (Bell, H₂, WH⁻ 6q, CAS(10,10) — labeled `(circuit)`) are **circuit
qubits** — raw qubits on the chip with no error correction. The FT-era
marker (W₈ vacancy + H — labeled `(logical)`) is **logical qubits** —
error-corrected abstractions, each backed by hundreds-to-thousands of
physical qubits. The "multi-W cluster" milestone sits in the transition
and is labeled `(early-FT)` to reflect that ambiguity. **These are not the
same unit of resource and the chart cannot be read as "200 logical = 33×
6 circuit"** — the physical-qubit footprints differ by orders of
magnitude. The chart's value is showing milestone *order* and timing, not
a literal resource scaling. See the [README's qubit-terminology
note](../../README.md#a-note-on-the-word-qubits) for the precise
definitions.

## What it actually means

In quantum computing there's a critical distinction between **physical**
qubits and **logical** qubits.

- A **physical qubit** is the actual transmon (or trapped ion, or
  whatever) sitting on the chip. They're noisy — every gate has ~0.1-1%
  error, errors compound, and a deep circuit becomes useless.
- A **logical qubit** is what you get when you combine *many* physical
  qubits with error-correcting codes. A logical qubit is essentially
  error-free for as long as the underlying physical qubits maintain coherence.

Today's biggest IBM Quantum machines (Heron r2 — `ibm_marrakesh`,
`ibm_kingston`, `ibm_fez`) have 156 physical qubits. **Zero logical qubits.**
Everything currently running is "NISQ" — Noisy Intermediate-Scale Quantum —
which is the polite term for "we're getting useful circuits to work despite
the noise, but only just."

The transition from NISQ to fault tolerance is the next decade's story.
Roughly:

| Era | Hardware | What chemistry can do |
|---|---|---|
| **NISQ** (now → ~2027) | ~150 noisy physical qubits | Toy molecules with active spaces ≤ ~10 circuit qubits. Single-point energies on QPU. Full VQE optimization on simulator. |
| **Early FT** (~2027–2029) | Thousands of physical qubits → tens of logical | Mid-sized molecules, ~20-qubit active spaces. Trotterized UCCSD becomes practical. |
| **Fault-tolerant** (2029+) | Millions of physical → hundreds of logical | The problems that motivate the field: transition metal catalysis, nitrogenase, fusion materials. Quantum Phase Estimation becomes the standard. |

Two things to internalize from this table:

1. **The interesting chemistry sits in the 2029+ row.** That's the row where
   quantum methods are expected to beat classical ones on problems of
   actual scientific value. The NISQ row is *necessary infrastructure
   development*, not production results.

2. **The order-of-magnitude jumps come from error correction, not from
   adding more physical qubits.** Going from 156 to 1560 physical qubits
   would still be NISQ. The fault-tolerant transition unlocks 100x more
   *usable* compute even if total qubit count grows modestly.

## Why it matters for our problem

This repo lives at the lowest milestone on the diagram. WH⁻ at 6 qubits.
That's deliberate.

Here's the part most readers miss: **the same code in `03_wh_binding.ipynb`
extends through every milestone on the chart.** What changes is parameters,
not architecture:

| What you change | NISQ-today | Early-FT (2027+) | FT-target (2029+) |
|---|---|---|---|
| Geometry | `W` + `H` (diatomic) | `W₂H₂`, small clusters | W₈ + vacancy + H |
| Basis | LANL2DZ / STO-3G | def2-SVPD | def2-TZVPD-J |
| Active space | CAS(4, 4) → 6q | CAS(10, 10) → ~16q | CAS(20, 20) → ~30+q |
| Ansatz | EfficientSU2(reps=4) | UCCSD-trotterized | QPE (Quantum Phase Estimation) |
| Backend | Aer sim + single-shot QPU | NISQ QPU + error mitigation | Fault-tolerant QPU |
| Result | Demonstration | Useful approximation | Chemical accuracy |

**This is what "scales when hardware catches up" actually means in
practice.** Not "rewrite everything" — just substitute different objects
into the same Qiskit pipeline.

The investment you make today in understanding this workflow pays off
across the entire roadmap. Whoever picks up your repo in 2029 with access
to fault-tolerant hardware can swap out the ansatz line and the backend
line, scale the active space, and be doing real fusion-wall chemistry.

## Next

→ [06 — Simulator vs QPU](06-sim-vs-qpu.md): the train-on-sim,
validate-on-QPU pattern that's standard for the entire NISQ era.

→ [04 — Active spaces](04-active-spaces.md) if you want to see why the
qubit numbers in that table are what they are.
