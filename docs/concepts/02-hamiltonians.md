# Hamiltonians and ground states

> **One-line take:** A Hamiltonian is the equation that tells you the energy
> of every possible state of a system; the *ground state* is whichever state
> has the lowest energy, and finding it is what chemistry is really about.

## The visual

```
   Energy
     ↑
     │      .─.                .─.
     │     ╱   ╲              ╱   ╲                 ← high-energy
     │    ╱     ╲            ╱     ╲                  excited states
     │   ╱       ╲          ╱       ╲
     │  ╱         ╲        ╱         ╲
     │ ╱           ╲      ╱           ╲
     │╱             ╲    ╱             ╲
     ●               ╲  ╱               ●
     │                ╲╱                 │
     │                ●  ← ground state  │
     │                                   │
     └───────────────────────────────────→  "configuration"
                  (parametrizes the wavefunction)

   The Hamiltonian defines this whole landscape.
   The ground state is the valley bottom.
   VQE's job is to slide down into it.
```

<svg viewBox="0 0 420 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Energy landscape with ground state at the minimum">
  <!-- axes -->
  <line x1="40" y1="180" x2="400" y2="180" stroke="#333" stroke-width="1.2"/>
  <line x1="40" y1="20" x2="40" y2="180" stroke="#333" stroke-width="1.2"/>
  <text x="20" y="100" font-family="sans-serif" font-size="12" fill="#333" transform="rotate(-90 20,100)">energy</text>
  <text x="220" y="205" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#333">configuration (wavefunction parameters)</text>
  <!-- landscape: smooth curve with hills around a valley -->
  <path d="M 50 80 Q 110 30 170 90 Q 220 160 270 90 Q 330 30 390 80"
        fill="none" stroke="#2c3e50" stroke-width="2.2"/>
  <!-- ground state marker -->
  <circle cx="220" cy="160" r="6" fill="#c0392b"/>
  <text x="220" y="178" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#c0392b">ground state (the answer)</text>
  <!-- excited markers (peaks) -->
  <circle cx="110" cy="30" r="4" fill="#7f8c8d"/>
  <circle cx="330" cy="30" r="4" fill="#7f8c8d"/>
  <text x="110" y="20" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7f8c8d">excited</text>
  <text x="330" y="20" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#7f8c8d">excited</text>
</svg>

## What it actually means

The **Hamiltonian** (written `Ĥ`) is the mathematical object that encodes
every interaction in a system. For a molecule, it sums up:

- The kinetic energy of each electron
- The attraction between each electron and each nucleus
- The repulsion between each pair of electrons
- The repulsion between each pair of nuclei

Once you know where the atoms are sitting, the Hamiltonian is fully
determined. It's not something you guess — it falls out of the geometry.

The Hamiltonian assigns an **energy** to every possible state of the system.
Some states have high energy (electrons piled on top of each other,
unfavourable arrangements), some have low energy (electrons settled into the
optimal pattern for that geometry).

The **ground state** is whichever state has the lowest possible energy. It's
the state the molecule actually occupies at zero temperature — and it's what
determines all the chemistry: bond strengths, geometries, reactivity.

In matrix language: the Hamiltonian is a (huge) matrix, and the ground state
is its **smallest eigenvalue's eigenvector**. For 50 electrons that matrix
has on the order of 10²⁰ rows. You cannot store it, let alone diagonalize
it. So we need a smarter approach than brute force — that's what VQE is.

## Why it matters for our problem

When we ask "how strongly does tungsten bind hydrogen?", what we're really
asking is:

> What's the lowest-energy state of (W + H together), and how does that
> compare to the lowest-energy states of (W alone) plus (H alone)?

The difference is the binding energy. So *everything* in this repo —
classical pyscf calculations, VQE on simulator, VQE on QPU — is ultimately a
ground-state-finding exercise on different Hamiltonians.

In `03_wh_binding.ipynb` we build the Hamiltonian for WH⁻ at one geometry,
then we scan through different W–H bond distances and rebuild it each time.
The curve we plot (`results/wh_minus_pec.png`) is just the ground-state
energy of each Hamiltonian as a function of distance — the **potential
energy curve**. Its minimum tells us the equilibrium bond length; its depth
tells us how much energy you'd need to pull the atoms apart.

## Next

→ [03 — The VQE loop](03-vqe-loop.md): how a quantum computer actually
finds the bottom of the valley.

→ [01 — Qubits and superposition](01-qubits-and-superposition.md) if you
haven't seen that one yet.
