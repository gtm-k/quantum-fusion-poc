# Error mitigation: why more shots can't save you, but ZNE might

> **One-line take:** More shots only shrink *random* scatter; they do nothing
> to the *systematic bias* that dominates a deep-circuit QPU result. Zero-Noise
> Extrapolation (ZNE) is the one bias-fighter you can run on today's hardware —
> and it is now wired into `wh_qpu_validation.py` behind `--mitigation zne`.

## Two completely different kinds of error

Every QPU energy carries two errors that behave nothing alike:

| | **Shot noise** (statistical / variance) | **Systematic bias** |
|---|---|---|
| Source | Measurement is a coin flip; you average finite samples | Imperfect gates, decoherence, readout bias, crosstalk |
| Direction | Random — scatters both ways | Consistent — pushes the answer the *same* way every shot |
| Shrinks with more shots? | **Yes**, as 1/√N (4× shots → ½ the scatter) | **No** — averaging just converges onto the biased value |
| Analogy | A fuzzy bathroom scale | A scale miscalibrated +10 lb |

This is the whole answer to *"why not just take more shots?"* — **more shots make
a wrong answer more precise, not more correct.** You converge, beautifully, onto
the biased number.

### The evidence is already in our own data

The H₂ and WH⁻ validations both used **4096 shots**. If shot noise were the
bottleneck, their errors would be similar. Instead WH⁻ was **~6.5× worse**
(199.8 vs 30.6 mHa) — and that ratio tracks **circuit depth**, not shot count.
Shot noise is blind to depth; gate-error bias grows with it. That 6.5× is the
fingerprint of bias, which is exactly what more shots cannot touch.

## How ZNE fights the bias

You can't measure the zero-noise answer directly — but you *can* measure how the
answer drifts as you deliberately make the chip noisier, then extrapolate back to
the noise-free limit you can't reach.

```
  energy
    ^
    |                                   x  (noise factor 5)
    |                         x            (noise factor 3)
    |               x                      (noise factor 1 = raw run)
    |          ?  <-- extrapolate to noise = 0
    |        (the ZNE estimate)
    +-------------------------------------------> noise factor
            0     1         3         5
```

In practice (qiskit-ibm-runtime `EstimatorV2`):

- **Gate folding** amplifies noise by replacing each gate `G` with `G·G†·G`
  (same logical operation, more physical noise) at factors `[1, 3, 5]`.
- The energy is measured at each factor, and an **exponential extrapolator**
  (falling back to **linear** if the fit fails on the degraded high-noise
  points) fits the trend back to factor 0.
- We also enable **twirled readout mitigation** (measurement-error correction)
  in the same pass.

ZNE only suppresses *real* hardware noise, so it is a **no-op on the noiseless
simulator** and roughly **multiplies QPU cost by the number of noise factors**
(~3× here, more with readout learning).

## How to run it in this repo

The baseline (unmitigated) path remains the default — its only schema change
is an added `mitigation_detail` field recording that no mitigation was applied:

```bash
# baseline — raw hardware (now records mitigation_detail = {"method": "none"})
python scripts/wh_qpu_validation.py qpu

# mitigated — ZNE + readout mitigation
python scripts/wh_qpu_validation.py qpu --mitigation zne
```

The mitigated run writes a **separate** artifact so the baseline proof stays
intact:

```
results/qpu_runs/wh_qpu_validation_zne_<DATE>.json
```

That JSON records the full mitigation configuration, so the run is reproducible
and self-describing:

```jsonc
{
  "mitigation": "zne",
  "mitigation_detail": {
    "method": "zne",
    "measure_mitigation": true,
    "zne_noise_factors": [1, 3, 5],
    "zne_extrapolator": ["exponential", "linear"],
    "note": "..."
  },
  "E_qpu_total_ha": "...",        // mitigated energy
  "delta_E_mHa": "...",           // residual vs the simulator
  "interpretation": "...compare against the unmitigated baseline..."
}
```

## What to honestly expect

ZNE will **help**, but it will not make WH⁻ "right":

- Typical gain is **~2–10×**. On our ~200 mHa that could plausibly drop ΔE
  **below the ~110 mHa well depth** — which would flip the WH⁻ result from
  *"physically uninformative"* to *"the valley is visible."* That is a genuine,
  reportable **methodology** win.
- It will **not** reach chemical accuracy (~1.6 mHa) — not close.
- At this depth (~30 layers, ~100 two-qubit gates), the noise-amplified runs are
  so degraded that the **extrapolation itself can wobble or mislead**. ZNE is
  near the edge of its reliable regime here, so the mitigated value is a
  **methodology data point, not a chemistry result.**

The ladder, for orientation: **shots fight variance · ZNE fights bias · error
correction fights both** (the last only arrives with fault-tolerant hardware —
see [05 — Scaling roadmap](05-scaling-roadmap.md)).

## Result (2026-05-31): a textbook "edge of reliability" outcome

Ran on `ibm_marrakesh` (job `d8e6ucjo3njc73eub3v0`, 4096 shots, noise factors
`[1, 3, 5]`). What ZNE did to the WH⁻ error:

| | Unmitigated baseline | **ZNE** |
|---|---|---|
| ΔE vs simulator | +199.8 mHa | **−97.9 mHa** |
| \|error\| magnitude | 199.8 mHa | **97.9 mHa (≈2× smaller)** |
| vs exact CASCI ground state (−67.4545 Ha) | above it | **~87 mHa _below_ it** |

So ZNE **roughly halved the error magnitude** — and `97.9 < 110`, so it dipped
under the well depth. But the sign flipped: the mitigated energy
(−67.5411 Ha) landed **below the exact ground state**, which is physically
impossible for a true expectation value. ZNE **over-extrapolated**, trading a
+200 mHa bias for an ~−87 mHa overshoot.

This is exactly the failure mode this primer predicted: at ~30 layers /
~100 two-qubit gates, the 3× and 5× points are so degraded that the
extrapolation overshoots. **Verdict: a genuine magnitude improvement, but a
methodology data point — not a trustworthy chemistry result.** A single ZNE
point also carries its own variance, so the overshoot is indicative, not a
precise bias measurement.

Full record: [`wh_qpu_validation_zne_2026-05-31.json`](../../results/qpu_runs/wh_qpu_validation_zne_2026-05-31.json).
The unmitigated baseline remains the reference result.

## Next

→ Back to [06 — Simulator vs QPU](06-sim-vs-qpu.md) for the train-then-validate
pattern this builds on, or run the command above once your IBM token is set.
