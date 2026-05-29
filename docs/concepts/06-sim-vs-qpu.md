# Simulator vs QPU: the train-then-validate pattern

> **One-line take:** Nobody runs full VQE on a real QPU today. The pattern
> is *train on simulator, validate on QPU* — find the optimal parameters
> classically, then evaluate the final energy once on real hardware to see
> how much noise costs you.

## The visual

```
   ┌─────────────────────────────────────────────────────────────┐
   │                                                             │
   │   PHASE 1: TRAIN (simulator)                                │
   │   ┌──────────────────────────────────────┐                  │
   │   │  Aer simulator (your laptop)         │                  │
   │   │                                      │                  │
   │   │  Full VQE loop:                      │                  │
   │   │    hundreds–thousands of             │                  │
   │   │    cost evaluations                  │                  │
   │   │    (H₂: ~500, WH⁻: ~2000)            │                  │
   │   │    optimizer iterates                │                  │
   │   │    converges to θ*                   │                  │
   │   │                                      │                  │
   │   │  Output: θ* (optimal parameters)     │                  │
   │   │          E_sim(θ*) (sim energy)      │                  │
   │   └──────────────┬───────────────────────┘                  │
   │                  │                                          │
   │                  │  hand off θ*                             │
   │                  ▼                                          │
   │   ┌──────────────────────────────────────┐                  │
   │   │  PHASE 2: VALIDATE (real QPU)        │                  │
   │   │                                      │                  │
   │   │  ibm_marrakesh (cloud)               │                  │
   │   │                                      │                  │
   │   │  ONE parameter point θ*:             │                  │
   │   │    prepare |ψ(θ*)⟩ on the chip       │                  │
   │   │    many shots, batched Paulis        │                  │
   │   │    → E_qpu(θ*)                       │                  │
   │   │                                      │                  │
   │   │  Compare: ΔE = E_qpu − E_sim         │                  │
   │   │  ΔE = lumped hardware cost           │                  │
   │   │  (shot noise + readout + gate err    │                  │
   │   │   + transpilation + drift)           │                  │
   │   └──────────────────────────────────────┘                  │
   │                                                             │
   └─────────────────────────────────────────────────────────────┘
```

<svg viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Sim-then-QPU validation pattern">
  <!-- phase 1 box -->
  <rect x="20" y="20" width="220" height="240" rx="8" fill="#e8f4f8" stroke="#2980b9" stroke-width="1.5"/>
  <text x="130" y="42" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#2980b9">Phase 1: TRAIN on simulator</text>
  <text x="130" y="60" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">Aer simulator (your laptop)</text>

  <rect x="50" y="80" width="160" height="100" rx="4" fill="#fff" stroke="#2980b9" stroke-width="1"/>
  <text x="130" y="100" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">Full VQE loop:</text>
  <text x="130" y="118" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">~500–2000 cost evals</text>
  <text x="130" y="132" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">classical optimizer</text>
  <text x="130" y="146" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">converges to θ*</text>
  <text x="130" y="165" text-anchor="middle" font-family="sans-serif" font-size="10" font-style="italic" fill="#2980b9">duration: minutes</text>

  <text x="130" y="200" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">Outputs:</text>
  <text x="130" y="216" text-anchor="middle" font-family="sans-serif" font-size="10" font-style="italic" fill="#333">θ* (optimal params)</text>
  <text x="130" y="232" text-anchor="middle" font-family="sans-serif" font-size="10" font-style="italic" fill="#333">E_sim(θ*) (sim energy)</text>

  <!-- arrow -->
  <line x1="240" y1="140" x2="280" y2="140" stroke="#333" stroke-width="2" marker-end="url(#arrow3)"/>
  <text x="260" y="130" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">θ*</text>

  <!-- phase 2 box -->
  <rect x="280" y="20" width="200" height="240" rx="8" fill="#fdf2e6" stroke="#d35400" stroke-width="1.5"/>
  <text x="380" y="42" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="bold" fill="#d35400">Phase 2: VALIDATE on QPU</text>
  <text x="380" y="60" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">ibm_marrakesh (cloud)</text>

  <rect x="300" y="80" width="160" height="100" rx="4" fill="#fff" stroke="#d35400" stroke-width="1"/>
  <text x="380" y="100" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">ONE parameter point:</text>
  <text x="380" y="118" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">prepare |ψ(θ*)⟩</text>
  <text x="380" y="132" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">many shots, batch Paulis</text>
  <text x="380" y="146" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">→ E_qpu(θ*)</text>
  <text x="380" y="165" text-anchor="middle" font-family="sans-serif" font-size="10" font-style="italic" fill="#d35400">duration: seconds–minutes</text>

  <text x="380" y="200" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">Result:</text>
  <text x="380" y="218" text-anchor="middle" font-family="sans-serif" font-size="10" font-style="italic" fill="#333">ΔE = E_qpu − E_sim</text>
  <text x="380" y="232" text-anchor="middle" font-family="sans-serif" font-size="10" font-style="italic" fill="#d35400">= lumped hardware-cost</text>

  <defs>
    <marker id="arrow3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#333"/>
    </marker>
  </defs>
</svg>

## What it actually means

Running a full VQE on a real QPU today is almost always a bad idea. Here's
the math:

- A 6-qubit VQE with 60 parameters and a reasonable optimizer needs ~2000
  cost-function evaluations to converge.
- Each evaluation on a real QPU is ~10 seconds (queue + transpile + run +
  measurement).
- Total: ~5.5 hours of QPU time per VQE run.
- IBM Open plan free tier: 10 minutes per month.

You can do the arithmetic. Even with paid access this is a poor use of
expensive hardware. And worse, the optimizer can be confused by shot noise —
making it slow to converge or settle at a wrong answer.

The pragmatic pattern that the field has converged on:

1. **Train on the simulator.** Aer gives noiseless, fast cost evaluations.
   Run the full VQE loop, get the optimal parameters `θ*`.
2. **Submit a single QPU job at `θ = θ*`.** "Single" here means *one
   parameter configuration*, not one measurement shot — the energy
   estimate at θ* is built from many shots (typically thousands per Pauli
   term, batched). You get back `E_qpu(θ*)`.
3. **Compare to `E_sim(θ*)`.** The gap `ΔE = E_qpu(θ*) − E_sim(θ*)` is the
   *total* impact of running on noisy hardware at that parameter setting.
   That ΔE is itself a composite — it includes shot noise (statistical),
   readout error (qubit-flip on measurement), gate errors (compounded
   across the circuit depth), transpilation effects (gate mapping
   changes the noise profile), and any backend drift between calibration
   and execution. Pulling those apart requires extra runs (calibration
   circuits, repeated submissions); the headline ΔE is just the lumped
   sum.

This gives you a credible "ran on real hardware" claim *and* a meaningful
result, without burning QPU minutes on optimizer iterations that the
classical simulator can do for free.

### What about error mitigation?

Even a single-shot measurement on a noisy chip gives a biased energy.
**Error mitigation** is a family of techniques to reduce that bias without
needing full error correction. The main ones:

- **TREX (Twirled Readout Error eXtinction)** — corrects measurement
  errors by deliberately scrambling and unscrambling readouts.
- **ZNE (Zero-Noise Extrapolation)** — runs the circuit at deliberately
  *increased* noise levels, then extrapolates back to zero noise.
- **M3 (Matrix-free Measurement Mitigation)** — fixes readout errors using
  a calibration matrix.
- **PEC (Probabilistic Error Cancellation)** — most powerful, also most
  expensive: samples from a quasi-probability distribution that exactly
  cancels noise on average.

Each technique trades extra QPU shots for less biased energies. For
demonstrations a 2-5x overhead from ZNE is reasonable. The Open plan free
tier doesn't really give you room for this; a paid plan does.

`qiskit-ibm-runtime`'s `EstimatorV2` exposes mitigation via `options`:

```python
from qiskit_ibm_runtime import EstimatorV2

estimator = EstimatorV2(mode=backend)
estimator.options.resilience_level = 2   # adds TREX + ZNE
estimator.options.default_shots = 4096
```

That's it. Toggling a number turns mitigation on. The added cost is
shots, not code complexity.

## Why it matters for our problem

In `01_hello_quantum.ipynb` we already ran a Bell state on `ibm_marrakesh`
and saw the noise signature (2.7% of shots came out wrong). That's
*measurement* noise on a 1-layer circuit.

`02_h2_binding.ipynb` and `03_wh_binding.ipynb` both follow the
train-then-validate pattern, and both validations were run on real IBM
Quantum hardware on 2026-05-28 (`ibm_marrakesh` for H₂, `ibm_fez` for
WH⁻; details in the README).

**Read the WH⁻ result with this caveat up front:** the unmitigated WH⁻
hardware noise *exceeded* the well depth the simulator computed. The
bare QPU energy at θ\* sits well above the dissociation asymptote, which
means it is physically uninformative as a binding-energy estimate. The
WH⁻ run's *value* is as a noise-scaling data point on a real chemistry
circuit, not as a chemistry result.

With that frame: the two ΔE values quantified the lesson this primer
predicted — noise at the WH⁻ circuit depth (EfficientSU2 reps=4 with
full entanglement, ≈ 30-layer circuit, ~100 two-qubit gates after
transpilation) is **~6.5× larger** than at H₂'s shallower depth on the
same generation of hardware. That is the expected NISQ-era lesson, and
it's why mitigation (and ultimately fault tolerance) matter at this
scale.

When fault-tolerant hardware arrives, this two-phase pattern collapses
into a single phase: full VQE (or its FT-era successor QPE) runs on the
QPU end-to-end, classical simulators become development tools, not runtime
participants.

## Next

→ [05 — Scaling roadmap](05-scaling-roadmap.md): the larger picture of how
hardware capability evolves.

→ Or open `01_hello_quantum.ipynb` (the most QPU-ready of the three) and
re-run the final cell against today's least-busy backend.
