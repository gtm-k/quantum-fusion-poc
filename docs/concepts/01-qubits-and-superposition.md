# Qubits and superposition

> **One-line take:** A classical bit is a switch (on/off); a qubit is an
> *arrow* in 3D space that points anywhere on a sphere — but when you measure
> it, you only ever get a single 0 or 1.

## The visual

```
                    The Bloch sphere
                    (one qubit's state space)

                          z = |0⟩
                            │
                            │   ↗ state vector |ψ⟩
                            │  ╱   (points anywhere on the sphere)
                            │ ╱
                            │╱
              ──────────────●──────────────  y
                           ╱│
                          ╱ │
                         ╱  │
                        ↙   │
                            │
                          z = |1⟩

   |0⟩  = north pole       |1⟩  = south pole
   Anywhere else on the sphere = a SUPERPOSITION of |0⟩ and |1⟩.

   Measure the qubit → it "collapses" to either |0⟩ or |1⟩.
   The probability of each is determined by where on the sphere
   the state vector was pointing.
```

<svg viewBox="0 0 360 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Bloch sphere diagram">
  <!-- sphere outline -->
  <ellipse cx="180" cy="140" rx="100" ry="100" fill="none" stroke="#666" stroke-width="1.2"/>
  <!-- equator -->
  <ellipse cx="180" cy="140" rx="100" ry="28" fill="none" stroke="#999" stroke-width="0.8" stroke-dasharray="3,3"/>
  <!-- meridian -->
  <ellipse cx="180" cy="140" rx="28" ry="100" fill="none" stroke="#999" stroke-width="0.8" stroke-dasharray="3,3"/>
  <!-- axes -->
  <line x1="180" y1="40" x2="180" y2="240" stroke="#333" stroke-width="1"/>
  <line x1="80" y1="140" x2="280" y2="140" stroke="#333" stroke-width="1"/>
  <!-- state vector |psi> -->
  <line x1="180" y1="140" x2="240" y2="80" stroke="#c0392b" stroke-width="2.2" marker-end="url(#arrow)"/>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#c0392b"/>
    </marker>
  </defs>
  <!-- labels -->
  <text x="180" y="32" text-anchor="middle" font-family="serif" font-size="14" font-style="italic">|0⟩</text>
  <text x="180" y="258" text-anchor="middle" font-family="serif" font-size="14" font-style="italic">|1⟩</text>
  <text x="246" y="74" font-family="serif" font-size="13" font-style="italic" fill="#c0392b">|ψ⟩</text>
  <text x="290" y="144" font-family="sans-serif" font-size="12" fill="#555">y</text>
  <text x="60" y="144" font-family="sans-serif" font-size="12" fill="#555">x</text>
  <text x="180" y="270" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">Bloch sphere — every point on the surface is a valid qubit state</text>
</svg>

## What it actually means

A **classical bit** has exactly two values: 0 or 1. Like a light switch.

A **qubit** is described by a vector pointing from the centre of a sphere to
some point on its surface. The north pole is the state we call `|0⟩`, the
south pole is `|1⟩`. Every other point on the sphere is a **superposition**
of `|0⟩` and `|1⟩` — a specific *combination* of the two, weighted by amounts
called *amplitudes*.

The catch: when you **measure** a qubit, you don't see the arrow. You see
either 0 or 1. The probability of seeing each is determined by how the arrow
was oriented before measurement. After measurement, the arrow snaps to the
pole you observed — the superposition is gone.

So why bother? Because **before** you measure, the qubit can participate in
operations that depend on it being in both states at once. With *N* qubits
you have a joint state living in a space of `2^N` amplitudes — and you can
manipulate all of them at once with a single quantum gate. That's where the
power comes from. Not from "trying many things in parallel" (a common
oversimplification), but from being able to set up patterns of *interference*
between amplitudes so that the right answer gets reinforced and wrong
answers cancel out.

## Why it matters for our problem

The wavefunction of a molecule lives in an exponentially large space — for
*N* electrons distributed over *M* orbitals, there are `C(M, N)` ways to
arrange them, and a real molecule's ground state is a *superposition* of all
those arrangements with specific amplitudes. Classical computers have to
track every amplitude separately; for ~50 electrons that's astronomical.

A quantum computer can store the same superposition naturally — one
amplitude per basis state, encoded across qubits — and manipulate it with
gates. **That's the fundamental reason quantum computers should eventually
be good at chemistry.**

In our `03_wh_binding.ipynb`, the WH⁻ wavefunction is encoded in 6 qubits =
2⁶ = 64 amplitudes. The full fusion problem (a tungsten vacancy with
embedded hydrogens) would need on the order of 200+ qubits = 2²⁰⁰ ≈ 10⁶⁰
amplitudes — comparable to the number of grains of sand on Earth (~10²⁰)
*cubed*. No classical computer will ever store that vector. A 200-qubit
chip, in principle, encodes the full superposition natively in its
hardware state.

(One nuance worth flagging early: you can't *read out* those 10⁶⁰
amplitudes — measurement collapses the state to a single classical outcome.
The magic isn't random-access storage, it's that quantum gates can shape
the amplitudes in ways that make the right answer pop out at measurement
time. We'll come back to that in the VQE primer.)

## Next

→ [02 — Hamiltonians and ground states](02-hamiltonians.md): what we're
trying to find with all those amplitudes.

→ Or jump back to the [project walkthrough](../walkthrough.html) if you want
the visual narrative end-to-end.
