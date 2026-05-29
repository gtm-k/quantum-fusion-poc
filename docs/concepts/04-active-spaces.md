# Active spaces

> **One-line take:** Molecules have thousands of orbitals; almost all of
> them are boring (full or empty all the time). The "active space" is the
> handful of orbitals where the interesting chemistry actually happens, and
> it's the only part we put on the quantum computer.

## The visual

```
   energy
     ↑                                            
     │                                            ← lots of empty orbitals
     │  ─────────                                    way up here, never
     │  ─────────                                    occupied in practice
     │  ─────────                                    → FROZEN (skip them)
     │  ─────────                                  
     │  ─────────                                  
     │ ╶─────────╴ ←─── LUMO                       
     │            ┓                                
     │  ─ ─ ─ ─ ─ ┃                                ← the action happens here
     │  ─ ─ ─ ─ ─ ┃ ACTIVE                          electrons get promoted
     │  ─ ─ ─ ─ ─ ┃ SPACE                           between these, that's
     │  ─ ─ ─ ─ ─ ┃ → put on the                    where correlation lives
     │            ┛   quantum computer            
     │ ╶─────────╴ ←─── HOMO                       
     │  ─────────                                  
     │  ─────────                                  ← always full,
     │  ─────────                                    electrons never leave
     │  ─────────                                    → FROZEN (skip them)
     │  ─────────                                  
     │
     └────────────────────────────────────────────→
                       orbital index

   HOMO = Highest Occupied Molecular Orbital
   LUMO = Lowest Unoccupied Molecular Orbital
```

<svg viewBox="0 0 380 320" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Active space diagram: frozen / active / virtual orbital bands">
  <!-- energy axis -->
  <line x1="40" y1="20" x2="40" y2="300" stroke="#333" stroke-width="1.2"/>
  <text x="20" y="160" font-family="sans-serif" font-size="12" fill="#333" transform="rotate(-90 20,160)">energy</text>

  <!-- virtual orbitals (top, frozen empty) -->
  <line x1="60" y1="30" x2="180" y2="30" stroke="#7f8c8d" stroke-width="2"/>
  <line x1="60" y1="45" x2="180" y2="45" stroke="#7f8c8d" stroke-width="2"/>
  <line x1="60" y1="60" x2="180" y2="60" stroke="#7f8c8d" stroke-width="2"/>
  <line x1="60" y1="75" x2="180" y2="75" stroke="#7f8c8d" stroke-width="2"/>
  <text x="290" y="55" font-family="sans-serif" font-size="11" fill="#7f8c8d" text-anchor="middle">virtual (frozen empty)</text>
  <text x="290" y="70" font-family="sans-serif" font-size="9" fill="#7f8c8d" text-anchor="middle">never occupied — skip</text>

  <!-- active space (middle, the interesting bit) -->
  <line x1="60" y1="120" x2="180" y2="120" stroke="#c0392b" stroke-width="2.5" stroke-dasharray="4,2"/>
  <line x1="60" y1="135" x2="180" y2="135" stroke="#c0392b" stroke-width="2.5" stroke-dasharray="4,2"/>
  <line x1="60" y1="150" x2="180" y2="150" stroke="#c0392b" stroke-width="2.5" stroke-dasharray="4,2"/>
  <line x1="60" y1="165" x2="180" y2="165" stroke="#c0392b" stroke-width="2.5" stroke-dasharray="4,2"/>
  <text x="290" y="135" font-family="sans-serif" font-size="11" fill="#c0392b" text-anchor="middle" font-weight="bold">ACTIVE SPACE</text>
  <text x="290" y="150" font-family="sans-serif" font-size="9" fill="#c0392b" text-anchor="middle">→ encoded into qubits</text>
  <text x="290" y="163" font-family="sans-serif" font-size="9" fill="#c0392b" text-anchor="middle">CAS(4 electrons, 4 orbitals)</text>

  <!-- HOMO marker -->
  <text x="190" y="124" font-family="sans-serif" font-size="9" fill="#27ae60">LUMO</text>
  <text x="190" y="168" font-family="sans-serif" font-size="9" fill="#27ae60">HOMO</text>

  <!-- core/inactive orbitals (bottom, frozen filled) -->
  <line x1="60" y1="220" x2="180" y2="220" stroke="#7f8c8d" stroke-width="2"/>
  <circle cx="100" cy="220" r="3" fill="#333"/>
  <circle cx="130" cy="220" r="3" fill="#333"/>
  <line x1="60" y1="235" x2="180" y2="235" stroke="#7f8c8d" stroke-width="2"/>
  <circle cx="100" cy="235" r="3" fill="#333"/>
  <circle cx="130" cy="235" r="3" fill="#333"/>
  <line x1="60" y1="250" x2="180" y2="250" stroke="#7f8c8d" stroke-width="2"/>
  <circle cx="100" cy="250" r="3" fill="#333"/>
  <circle cx="130" cy="250" r="3" fill="#333"/>
  <line x1="60" y1="265" x2="180" y2="265" stroke="#7f8c8d" stroke-width="2"/>
  <circle cx="100" cy="265" r="3" fill="#333"/>
  <circle cx="130" cy="265" r="3" fill="#333"/>
  <text x="290" y="245" font-family="sans-serif" font-size="11" fill="#7f8c8d" text-anchor="middle">core (frozen filled)</text>
  <text x="290" y="260" font-family="sans-serif" font-size="9" fill="#7f8c8d" text-anchor="middle">always occupied — skip</text>

  <!-- caption -->
  <text x="190" y="305" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">Tungsten ECP already replaces 60 core electrons; active space picks 4 more above that.</text>
</svg>

## What it actually means

A molecule's electrons sit in **molecular orbitals**, conceptually like
shells in a building. Real molecules have *thousands* of orbitals in any
realistic basis set. But for almost every chemistry question you might ask:

- The deep **core** orbitals are always fully occupied. The electrons there
  don't go anywhere. They affect the energy by a constant amount and you
  can subtract that off.
- The very high **virtual** orbitals are always empty. Electrons don't
  visit them at any reasonable temperature.

So you carve out a band in the middle — the **active space** — containing
the highest few occupied orbitals and the lowest few empty orbitals. Those
are where electrons can actually be promoted, where bond formation and
breaking happens, where electron correlation gets interesting. *Only the
active space goes onto the quantum computer.*

The notation `CAS(n, m)` means **C**omplete **A**ctive **S**pace with `n`
electrons distributed among `m` orbitals. Each spatial orbital is two qubits
(one for spin-up, one for spin-down), so `CAS(4, 4)` is 8 qubits before
optimization. Symmetry tricks (the **parity mapper** with Z₂ tapering)
shave that down to 6 qubits — which is what we use for WH⁻.

This isn't an approximation made up for quantum computers. Classical
chemistry has used active spaces for decades — they're how you make
high-accuracy methods like CASSCF and CASPT2 tractable. The quantum
adaptation is just: the same active space, encoded into qubits instead of
into a classical wavefunction expansion.

## Why it matters for our problem

The whole reason WH⁻ fits in 6 qubits is the active space.

- Tungsten has 74 electrons. Even with the LANL2DZ effective core potential
  (which freezes 60 inner-shell electrons as a fixed background), there are
  still 14 valence electrons plus hydrogen's 2 — that's 16 electrons across
  dozens of valence orbitals.
- We pick `CAS(4, 4)` — 4 electrons in 4 orbitals — centred on the W–H
  bonding region. Those are the orbitals where the W–H σ bond is forming
  and where electron correlation matters most.
- Everything else (the other 12 valence electrons, all the higher virtuals)
  is folded into the Hartree-Fock background and treated as a constant.

The honest caveat: **automatic active-space selection drifts at larger
bond distances.** Our notebook's PEC is capped at r = 3.0 Å because
qiskit-nature's `ActiveSpaceTransformer` starts picking different (non-bonding)
orbitals beyond that range. Production-grade work uses natural-orbital or
AO-character-based selection, which keeps a consistent active space across
geometries.

The fusion-wall problem at scale — tungsten vacancy + embedded hydrogens —
needs roughly `CAS(20, 20)` to capture the multi-centre correlation. In the
[canonical terminology from the README](../../README.md#a-note-on-the-word-qubits):
that's ~40 spin-orbital qubits before tapering, ~36 circuit qubits after a
Z₂ taper. Even bigger problems (W₈ vacancy cluster with multiple H sites,
the real production target) push into the ~150+ circuit-qubit regime —
which is where the error-correction story starts mattering, because at that
circuit depth noise compounds faster than NISQ chips can tolerate. The
"200+ logical qubits" figure you'll see quoted elsewhere is the
error-corrected count needed to *actually run* those circuits to chemical
accuracy.

## Next

→ [05 — Scaling roadmap](05-scaling-roadmap.md): how today's 6 qubits get
to tomorrow's 200.

→ [03 — The VQE loop](03-vqe-loop.md) for what we do with the active-space
Hamiltonian once it's on the chip.
