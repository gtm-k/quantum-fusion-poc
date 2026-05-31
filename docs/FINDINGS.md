# Findings & lessons learned

A plain-English synthesis of what this proof-of-concept actually demonstrated.
For the raw per-run numbers see the [README result table](../README.md#result-snapshot)
and [`results/qpu_runs/`](../results/qpu_runs/); for the concepts behind them see
[`docs/concepts/`](concepts/).

> **Headline.** We proved the entire quantum-chemistry pipeline runs end-to-end
> on real tungsten chemistry on real IBM Quantum hardware — and we measured,
> transparently, exactly how far today's machines are from trustworthy chemistry.

---

## 1. The workflow works — and it scales by parameters, not architecture

Three experiments of rising difficulty were validated on real IBM Quantum
hardware, each with a saved artifact (job ID, backend, shot count):
**Bell → H₂ → WH⁻**. The full chain runs end-to-end:

```
pyscf Hamiltonian → active space → qubit mapping → ansatz → VQE → QPU validation
```

The same code skeleton extends to the real fusion-relevant problem (a W₈ vacancy
cluster with hydrogen, ~200 logical qubits, ~2029+). What changes between "today"
and "future" is geometry, active space, ansatz, and backend — **not the
architecture**. The validated scaffold *is* the deliverable.

## 2. Noise scales steeply with circuit depth — and we quantified it

| Experiment | Circuit | Hardware error |
|---|---|---|
| Bell state | 1 layer | **2.7%** spurious counts (28 / 1024) |
| H₂ | 2 qubits, shallow | ΔE = **+30.6 mHa** |
| WH⁻ | 6 qubits, ~100 two-qubit gates | ΔE = **+199.8 mHa** |

**The key observation:** H₂ and WH⁻ used the *same* 4096 shots, yet WH⁻'s error
was **~6.5× larger** — and that ratio tracks **circuit depth**, not shot count.
That is the empirical fingerprint that the dominant error is systematic
**gate-error bias**, not random shot noise. It is a clean, real-hardware
demonstration of the single most important NISQ-era lesson.

## 3. On a hard problem today, the noise can exceed the signal

WH⁻'s unmitigated hardware noise (~200 mHa) **exceeded the well depth it was
trying to measure** (~110 mHa). When the error bar is larger than the quantity
itself, the result is physically uninformative *as chemistry*. This is the
crispest possible marker of where current hardware sits relative to a real
chemistry target — and it is reported honestly rather than hidden.

## 4. Error mitigation helps in magnitude — but isn't reliable yet, and can overshoot

A Zero-Noise Extrapolation run (`ibm_marrakesh`, 2026-05-31, job
`d8e6ucjo3njc73eub3v0`) cut the error magnitude **~2×** — from +199.8 mHa to
**−97.9 mHa**, dipping under the ~110 mHa well depth. **But it overshot:** the
mitigated energy (−67.5411 Ha) landed ~87 mHa *below* the exact CASCI ground
state (−67.4545 Ha), which is physically impossible for a true expectation
value. ZNE over-extrapolated at this circuit depth — trading a *too-high* bias
for a *too-low* overshoot.

The lesson is not "mitigation failed." It is that at ~100 two-qubit gates, ZNE
buys a **magnitude** improvement, not a **reliability** one. Two corollaries:

- **The variational floor is a free correctness check.** A real energy can never
  fall below the ground state, so the negative result instantly self-flagged as
  untrustworthy. See [`docs/concepts/07-error-mitigation.md`](concepts/07-error-mitigation.md).
- **More shots would not have helped** — shots fight *variance*; this is *bias*.

## 5. The real unlock is error correction, not cleverness

Error mitigation buys roughly **2–10×**; reaching chemical accuracy (~1.6 mHa)
on this problem needs about **100×**. No amount of mitigation tuning closes that
gap on today's chips — it is a **fault-tolerance (2029+) story**. The value of
this prototype is that it *quantifies the gap precisely* instead of hand-waving.

## 6. Honest scoping is the product — what this is **not**

- The WH⁻ "well depth" is **not** the experimental binding energy of neutral WH.
  It is a tractable closed-shell anion proxy; its proximity to literature values
  is **coincidental error cancellation, not physics**.
- This is **not** a quantum-advantage demonstration — CAS(4,4) is small enough
  that classical CASCI solves it exactly in milliseconds.
- The result is a **validated workflow + an honest noise benchmark**, not a
  trustworthy tungsten chemistry answer.

---

## "So… did it work?"

> **Yes — as a workflow proof and an honest hardware benchmark.** It ran the
> complete quantum-chemistry pipeline on real tungsten chemistry on real quantum
> hardware, and it transparently measured how far today's machines are from
> trustworthy chemistry: the noise exceeds the signal, mitigation helps but
> overshoots, and chemical accuracy needs error correction (~2029+). It did
> **not**, and was never meant to, produce a trustworthy tungsten binding energy.

## Summary in five bullets

1. The full VQE-on-real-chemistry pipeline runs end-to-end on real IBM hardware,
   and scales to the production problem by parameters, not architecture.
2. Noise scales with circuit depth (2.7% → 30.6 → 199.8 mHa); the 6.5× gap at
   equal shots is the signature of **bias**, not shot noise.
3. On WH⁻, **noise (~200) exceeded the signal (~110)** — today's hardware cannot
   yet see this chemistry.
4. ZNE halved the error magnitude but **overshot the physical floor** —
   mitigation buys magnitude, not reliability, at this depth.
5. Chemical accuracy needs **fault tolerance (~2029+)**; this POC quantifies the
   gap honestly rather than overclaiming.
