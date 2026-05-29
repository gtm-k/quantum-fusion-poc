# The VQE loop

> **One-line take:** VQE is a thermostat for energy — a quantum circuit
> prepares a guess at the ground state, a classical optimizer measures how
> good the guess is and adjusts the dials, and the loop keeps going until
> the energy stops dropping.

## The visual

```
                    ┌─────────────────────────────────────────┐
                    │   QUANTUM (the chip)                    │
                    │                                         │
                    │   Build circuit with parameters θ       │
                    │   ┌──────────────────────────────┐      │
                    │   │  |0⟩─[Ry(θ₁)]─●─[Ry(θ₅)]─    │      │
                    │   │  |0⟩─[Ry(θ₂)]─X─[Ry(θ₆)]─    │      │
                    │   │  |0⟩─[Ry(θ₃)]─●─[Ry(θ₇)]─    │      │
                    │   │  |0⟩─[Ry(θ₄)]─X─[Ry(θ₈)]─    │      │
                    │   └──────────────────────────────┘      │
                    │              │                          │
                    │              ▼                          │
                    │   Measure ⟨Ĥ⟩ on this state             │
                    └──────────────┬──────────────────────────┘
                                   │  E(θ)
                                   ▼
                    ┌─────────────────────────────────────────┐
                    │   CLASSICAL (your laptop / cloud)       │
                    │                                         │
                    │   Optimizer (e.g. COBYLA, SPSA):        │
                    │   "energy dropped — try θ + Δ"          │
                    │   "energy rose — go the other way"      │
                    │                                         │
                    │   New parameters θ' ───────────┐        │
                    └─────────────────────────────────┼───────┘
                                                     │
                              loops until ───────────┘
                              E(θ) stops dropping
```

<svg viewBox="0 0 460 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="VQE hybrid loop">
  <!-- quantum side -->
  <rect x="20" y="20" width="200" height="100" rx="8" fill="#e8f4f8" stroke="#2980b9" stroke-width="1.5"/>
  <text x="120" y="40" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#2980b9">QUANTUM (the chip)</text>
  <text x="120" y="60" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">prepare ansatz |ψ(θ)⟩</text>
  <text x="120" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">measure expectation</text>
  <text x="120" y="93" text-anchor="middle" font-family="sans-serif" font-size="11" font-style="italic" fill="#333">E(θ) = ⟨ψ(θ)|Ĥ|ψ(θ)⟩</text>

  <!-- classical side -->
  <rect x="240" y="20" width="200" height="100" rx="8" fill="#fdf2e6" stroke="#d35400" stroke-width="1.5"/>
  <text x="340" y="40" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold" fill="#d35400">CLASSICAL (your laptop)</text>
  <text x="340" y="60" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">optimizer (COBYLA / SPSA)</text>
  <text x="340" y="78" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">"E dropped — go this way"</text>
  <text x="340" y="93" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#333">propose new θ</text>

  <!-- arrows between -->
  <path d="M 220 70 L 240 70" stroke="#333" stroke-width="1.5" marker-end="url(#arrow2)"/>
  <text x="230" y="62" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">E(θ)</text>

  <path d="M 340 120 L 340 160 L 120 160 L 120 120" fill="none" stroke="#333" stroke-width="1.5" marker-end="url(#arrow2)"/>
  <text x="230" y="155" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">new θ</text>

  <!-- loop termination -->
  <text x="230" y="200" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#27ae60" font-weight="bold">stop when E(θ) plateaus → ground state ≈ E(θ*)</text>

  <!-- caption -->
  <text x="230" y="240" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">VQE = hybrid loop. Quantum does what it's good at (state prep + measurement),</text>
  <text x="230" y="255" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#555">classical does what it's good at (numerical optimization).</text>

  <defs>
    <marker id="arrow2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#333"/>
    </marker>
  </defs>
</svg>

## What it actually means

VQE — **Variational Quantum Eigensolver** — is a hybrid algorithm. Quantum
computers and classical computers each do part of the work.

The quantum part is a **parametrized circuit** called the *ansatz*. It has a
fixed structure but adjustable knobs — typically tens to hundreds of
rotation angles. For any setting of the knobs `θ`, the circuit produces a
specific quantum state `|ψ(θ)⟩`. By choosing the structure carefully, you
make sure that **somewhere** in the space of possible θ values, there's a
state close to the molecule's true ground state.

The quantum chip's job is to:
1. Run the circuit with the current θ.
2. Measure the expectation value of the Hamiltonian on the resulting state.
3. Report back a number: `E(θ)`.

That number is the energy of the current guess. The lower it is, the closer
the guess is to the ground state. (This is guaranteed by the *variational
principle* — the energy of any state is always ≥ the true ground state
energy.)

The classical part is a **numerical optimizer** — the kind that's been
solving "minimize f(x)" problems for decades. It takes the current `E(θ)`,
proposes a new θ that should give lower energy, and asks the quantum chip
to evaluate it. After many iterations the energy stops dropping, and the θ
at that point is your VQE-approximation to the ground state.

**Why hybrid?** Because today's quantum computers are too noisy to run very
deep circuits. VQE keeps the circuit shallow (good for noise tolerance) and
puts all the iterative work on the classical side. It's pragmatic. The more
elegant alternative — Quantum Phase Estimation — gives ground-state
energies to arbitrarily high precision (within the chosen basis and active
space) but needs fault-tolerant hardware to sustain the deep, repeated
controlled-evolution circuits it requires. That hardware doesn't exist
yet.

## Why it matters for our problem

Every notebook in this repo, except the Bell state demo, is a VQE.

- `02_h2_binding.ipynb`: 2 circuit qubits, a small EfficientSU2 ansatz,
  finds the H₂ ground state to nanohartree precision in seconds.
- `03_wh_binding.ipynb`: 6 circuit qubits, EfficientSU2(reps=4)
  (~60 parameters), finds WH⁻ ground state to ~11 mHa accuracy — that's
  roughly 300 meV off, workable for a demonstration but a long way from
  chemical accuracy.

The ansatz choice is the most consequential decision in VQE. We use
**EfficientSU2** — a hardware-efficient ansatz that maps cleanly onto real
QPU gate sets — because it's robust and runs fast. The chemistry-aware
alternative, **UCCSD**, would give better accuracy but takes ~24 minutes
per cost evaluation at our problem size, which is impractical for a
demonstration.

This trade-off (accuracy vs. tractability) is exactly the kind of choice
that gets cheaper when fault-tolerant hardware arrives: QPE or
trotterized UCCSD become practical, and within the chosen basis and
active space (and with a suitable initial state preparation) you can drive
the algorithmic error arbitrarily low. The basis-set and active-space
errors don't go away — those are physics choices, not algorithm choices.

## Next

→ [04 — Active spaces](04-active-spaces.md): why 6 qubits is enough for WH⁻
(and why it isn't enough for the real fusion problem).

→ [02 — Hamiltonians and ground states](02-hamiltonians.md) for what we're
actually minimizing.
