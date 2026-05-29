# Concept primers

Six short reads, in order. Each one is ~300 words with one anchor diagram
and a "why this matters for our problem" tie-back. Read them straight
through — they're designed to build on each other.

| # | Topic | What you'll learn |
|---|---|---|
| [1](01-qubits-and-superposition.md) | **Qubits and superposition** | Why a qubit isn't just a probabilistic bit, and where the exponential power comes from |
| [2](02-hamiltonians.md) | **Hamiltonians and ground states** | What "find the ground state" actually means and why it's the chemistry question |
| [3](03-vqe-loop.md) | **The VQE loop** | The hybrid quantum–classical algorithm at the heart of this repo |
| [4](04-active-spaces.md) | **Active spaces** | Why 6 circuit qubits are enough for WH⁻ and isn't enough for the real fusion problem |
| [5](05-scaling-roadmap.md) | **Scaling roadmap** | NISQ today → fault-tolerant tomorrow, and what the same code lets you do at each stage |
| [6](06-sim-vs-qpu.md) | **Simulator vs QPU** | The train-on-sim, validate-on-QPU pattern that makes a real-hardware claim credible |

Already comfortable with most of this? Skip straight to the
[walkthrough](../walkthrough.html) for the end-to-end project narrative,
or open the notebooks at [`../../notebooks/`](../../notebooks/).

## A reading-order rationale

The order isn't arbitrary. Each doc unlocks the next:

```
   1. Qubits  ─────→  2. Hamiltonians  ─────→  3. VQE loop
   (the medium)        (what we're          (how we find it)
                       looking for)
                                              │
                                              ▼
   6. Sim vs QPU  ←─── 5. Scaling  ←─── 4. Active spaces
   (real-world          (where this        (how we make
   pattern)             scales to)         the problem fit)
```

If you only read one, read **[4 — Active spaces](04-active-spaces.md)** —
it's the single concept that makes the rest of this repo make sense, and
it's also the answer to "how can a 6-qubit chip say anything about a
74-electron tungsten atom?"
