"""WH- VQE QPU validation — train on Aer simulator, validate single-point on real IBM QPU.

The Hamiltonian is built fresh each run via pyscf (LANL2DZ ECP for W,
STO-3G for H) and the qiskit-nature CAS(4,4) → ParityMapper pipeline.
The same code builds the operator in both 'sim' and 'qpu' modes, so the
QPU job submits the same circuit the simulator trained on.

This script MUST run inside WSL — pyscf has no Windows wheels.

Usage (from inside WSL Ubuntu):
    python scripts/wh_qpu_validation.py sim
        Build WH- at r=1.73 A, run VQE on Aer to convergence, write
        results/qpu_runs/wh_optimal_params.json with theta*, Hamiltonian
        Pauli coefficients, and the ansatz/optimizer configuration.

    python scripts/wh_qpu_validation.py qpu [--mitigation {none,zne}]
        Load theta* and the Hamiltonian from JSON (saves us re-running
        pyscf), reconstruct the ansatz, transpile to the least-busy
        IBM backend, submit a single-point energy evaluation, write
        results/qpu_runs/wh_qpu_validation[_<mit>]_<DATE>.json.
        --mitigation zne enables Zero-Noise Extrapolation + readout
        mitigation (real-hardware only; ~3-5x QPU cost). Default: none,
        which reproduces the unmitigated baseline result (now also recording
        a mitigation_detail field noting that no mitigation was applied).

Environment:
    IBM_QUANTUM_TOKEN must be set, OR a saved account must exist at
    ~/.qiskit/qiskit-ibm.json (the script tries env var first, then
    falls back to the saved account).

Expected wall clock:
    sim mode: 3-5 minutes (pyscf RHF + VQE convergence with ~2000 evals)
    qpu mode: queue + ~3-5 minutes QPU time (95 Pauli terms, batched)
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HARTREE_TO_EV = 27.211386245988

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "results" / "qpu_runs"
PARAMS_PATH = RESULTS_DIR / "wh_optimal_params.json"

R_EQ_ANGSTROM = 1.73  # see notebook 03 Step 1 — grid anchor, not a prediction
ANSATZ_REPS = 4
ANSATZ_ENTANGLEMENT = "full"
OPTIMIZER_SEED = 7
OPTIMIZER_MAXITER = 2000
OPTIMIZER_RHOBEG = 0.3

QPU_SHOTS = 4096
# ZNE (Zero-Noise Extrapolation) — applied only when --mitigation zne (qpu mode).
# noise_factors are the gate-folding amplification levels; the energy is measured
# at each and extrapolated back to the (unreachable) zero-noise limit.
ZNE_NOISE_FACTORS = [1, 3, 5]
# Extrapolators are tried in order: if the exponential fit fails on the
# heavily-degraded high-noise points (likely at this circuit depth), it falls
# back to linear rather than erroring out a job whose shots are already spent.
ZNE_EXTRAPOLATOR = ["exponential", "linear"]


def build_hamiltonian():
    """pyscf RHF + qiskit-nature CAS(4,4) → ParityMapper → 6-qubit operator.

    Returns (qubit_op, energy_offset). The qubit_op is a SparsePauliOp.
    energy_offset is the additive constant (nuclear repulsion + frozen-core)
    that must be added to electronic eigenvalues to get total energy.
    """
    from pyscf import gto, scf, tools
    from qiskit_nature.second_q.formats.fcidump import FCIDump
    from qiskit_nature.second_q.formats.fcidump_translator import fcidump_to_problem
    from qiskit_nature.second_q.mappers import ParityMapper
    from qiskit_nature.second_q.transformers import ActiveSpaceTransformer

    mol = gto.M(
        atom=f"W 0 0 0; H 0 0 {R_EQ_ANGSTROM}",
        basis={"W": "lanl2dz", "H": "sto-3g"},
        ecp={"W": "lanl2dz"},
        charge=-1, spin=0, verbose=0,
    )
    mf = scf.RHF(mol).run(max_cycle=200, conv_tol=1e-9, verbose=0)
    if not mf.converged:
        raise RuntimeError(f"RHF did not converge at r={R_EQ_ANGSTROM}")

    fcidump_path = "/tmp/wh_minus_qpu_validation.fcidump"
    tools.fcidump.from_scf(mf, fcidump_path)
    problem = fcidump_to_problem(FCIDump.from_file(fcidump_path))

    reduced = ActiveSpaceTransformer(num_electrons=4, num_spatial_orbitals=4).transform(problem)
    mapper = ParityMapper(num_particles=reduced.num_particles)
    qubit_op = mapper.map(reduced.hamiltonian.second_q_op())
    energy_offset = float(sum(reduced.hamiltonian.constants.values()))
    return qubit_op, energy_offset


def build_ansatz(num_qubits: int):
    from qiskit.circuit.library import efficient_su2
    return efficient_su2(
        num_qubits=num_qubits,
        reps=ANSATZ_REPS,
        entanglement=ANSATZ_ENTANGLEMENT,
    )


def serialize_pauli_op(qubit_op):
    """Convert SparsePauliOp to a JSON-friendly representation."""
    return [
        {"pauli": str(label), "coeff_real": float(coeff.real), "coeff_imag": float(coeff.imag)}
        for label, coeff in zip(qubit_op.paulis.to_labels(), qubit_op.coeffs)
    ]


def deserialize_pauli_op(serialized):
    """Rebuild SparsePauliOp from the JSON representation."""
    from qiskit.quantum_info import SparsePauliOp
    paulis = [item["pauli"] for item in serialized]
    coeffs = np.array(
        [item["coeff_real"] + 1j * item["coeff_imag"] for item in serialized],
        dtype=complex,
    )
    return SparsePauliOp(paulis, coeffs)


def run_sim() -> None:
    from qiskit.primitives import StatevectorEstimator

    print("building WH- Hamiltonian via pyscf...")
    qubit_op, energy_offset = build_hamiltonian()
    num_qubits = qubit_op.num_qubits
    num_terms = len(qubit_op)
    print(f"  qubits: {num_qubits}  Pauli terms: {num_terms}")
    print(f"  frozen + V_NN offset: {energy_offset:+.6f} Ha")

    print("computing CASCI reference...")
    E_electronic_exact = float(np.linalg.eigvalsh(qubit_op.to_matrix())[0])
    E_total_exact = E_electronic_exact + energy_offset
    print(f"  CASCI total energy: {E_total_exact:+.6f} Ha")

    print("running VQE on Aer (no noise)...")
    ansatz = build_ansatz(num_qubits)
    estimator = StatevectorEstimator()
    history: list[float] = []

    def cost(params):
        job = estimator.run([(ansatz, qubit_op, params)])
        e = float(job.result()[0].data.evs)
        history.append(e)
        return e

    rng = np.random.default_rng(seed=OPTIMIZER_SEED)
    x0 = rng.uniform(-np.pi, np.pi, ansatz.num_parameters)

    result = minimize(
        cost, x0=x0, method="COBYLA",
        options={"maxiter": OPTIMIZER_MAXITER, "rhobeg": OPTIMIZER_RHOBEG, "tol": 1e-8},
    )
    E_electronic_vqe = float(result.fun)
    E_total_vqe = E_electronic_vqe + energy_offset
    err_ha = E_electronic_vqe - E_electronic_exact

    payload = {
        "experiment": "WH- ground-state VQE — simulator-optimal parameters",
        "molecule": "WH-",
        "bond_length_angstrom": R_EQ_ANGSTROM,
        "bond_length_anchor_note": (
            "1.73 A is the literature equilibrium for *neutral* WH used here "
            "as a grid anchor. See notebook 03 Step 1 — this is not a "
            "prediction of the WH- equilibrium bond length."
        ),
        "basis": {"W": "lanl2dz (ECP-replaced)", "H": "STO-3G"},
        "active_space": "CAS(4 electrons, 4 spatial orbitals)",
        "mapper": "ParityMapper with Z2 tapering",
        "circuit_qubits": int(qubit_op.num_qubits),
        "pauli_terms": int(num_terms),
        "energy_offset_ha": energy_offset,
        "hamiltonian_pauli_op": serialize_pauli_op(qubit_op),
        "ansatz": {
            "kind": "efficient_su2",
            "num_qubits": int(qubit_op.num_qubits),
            "reps": ANSATZ_REPS,
            "entanglement": ANSATZ_ENTANGLEMENT,
            "num_parameters": int(ansatz.num_parameters),
        },
        "optimizer": {
            "method": "COBYLA",
            "maxiter": OPTIMIZER_MAXITER,
            "rhobeg": OPTIMIZER_RHOBEG,
            "rng_seed": OPTIMIZER_SEED,
        },
        "simulator": "qiskit StatevectorEstimator (noiseless)",
        "final_parameters": [float(x) for x in result.x],
        "final_electronic_energy_ha": E_electronic_vqe,
        "final_total_energy_ha": E_total_vqe,
        "exact_casci_electronic_ha": E_electronic_exact,
        "exact_casci_total_ha": E_total_exact,
        "vqe_error_ha": err_ha,
        "vqe_error_mha": err_ha * 1000,
        "vqe_error_mev": err_ha * HARTREE_TO_EV * 1000,
        "cost_evaluations": len(history),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PARAMS_PATH.write_text(json.dumps(payload, indent=2))

    print(f"\nwrote {PARAMS_PATH}")
    print(f"  VQE total energy : {E_total_vqe:+.6f} Ha")
    print(f"  CASCI total      : {E_total_exact:+.6f} Ha")
    print(f"  VQE error        : {err_ha * 1000:+.3f} mHa "
          f"({err_ha * HARTREE_TO_EV * 1000:+.0f} meV)")
    print(f"  Cost calls       : {len(history)}")


def _configure_mitigation(estimator, mitigation: str) -> dict:
    """Apply the requested error mitigation to an EstimatorV2 and return a
    JSON-serializable record of what was applied (for the run artifact).

    'none' leaves the estimator raw. 'zne' enables Zero-Noise Extrapolation
    (gate folding: re-run the circuit at each noise factor and extrapolate to
    the zero-noise limit) plus twirled readout mitigation. ZNE only suppresses
    *real* hardware noise, so it is a no-op on a noiseless simulator and
    multiplies QPU cost by roughly the number of noise factors.
    """
    if mitigation == "none":
        return {"method": "none"}
    if mitigation == "zne":
        estimator.options.resilience.measure_mitigation = True
        estimator.options.resilience.zne_mitigation = True
        estimator.options.resilience.zne.noise_factors = ZNE_NOISE_FACTORS
        estimator.options.resilience.zne.extrapolator = ZNE_EXTRAPOLATOR
        return {
            "method": "zne",
            "measure_mitigation": True,
            "zne_noise_factors": list(ZNE_NOISE_FACTORS),
            "zne_extrapolator": ZNE_EXTRAPOLATOR,
            "note": (
                "Zero-Noise Extrapolation via gate folding plus twirled readout "
                "mitigation. Suppresses systematic hardware bias by extrapolating "
                f"from amplified-noise runs; ~{len(ZNE_NOISE_FACTORS)}x the QPU "
                "executions of an unmitigated run. Does not remove bias entirely."
            ),
        }
    raise ValueError(f"unknown mitigation: {mitigation!r}")


INTERP_NONE = (
    "delta_E is the lumped hardware-cost on a 6-qubit, ~30-layer-deep "
    "EfficientSU2(reps=4, full) circuit: shot noise + readout error + "
    "compounding gate errors + transpilation effects + backend drift. "
    "Expected to be substantially larger than the H2 (2-qubit, shallow) "
    "delta_E. The H2 and WH- jobs landed on different physical backends "
    "(H2 on ibm_marrakesh, WH- on ibm_fez) but the same Heron r2 "
    "generation, so the comparison reflects circuit-depth scaling and "
    "not a same-chip apples-to-apples noise measurement. No mitigation."
)

INTERP_ZNE = (
    "delta_E AFTER Zero-Noise Extrapolation (+ twirled readout mitigation) "
    "on the same 6-qubit, ~30-layer EfficientSU2(reps=4, full) circuit. ZNE "
    "estimates and subtracts systematic hardware bias by extrapolating from "
    "deliberately noise-amplified runs; the residual delta_E reflects "
    "extrapolation error plus un-mitigated shot noise. Compare against the "
    "unmitigated baseline (wh_qpu_validation_<date>.json, delta_E ~ +199.8 "
    "mHa) to quantify how much mitigation recovers. At this circuit depth ZNE "
    "is near the edge of reliability, so treat the mitigated value as a "
    "methodology data point, not a chemistry result."
)


def _build_qpu_payload(
    *,
    params: dict,
    backend_name: str,
    backend_qubits: int,
    job_id: str,
    mitigation: str,
    mitigation_detail: dict,
    e_qpu_electronic: float,
    e_qpu_total: float,
    e_sim_total: float,
    executed_at_iso: str,
) -> dict:
    """Assemble the QPU-run result artifact. Pure: no I/O, no network.

    Kept separate from run_qpu so the output schema can be unit-tested
    offline — a logic bug here would otherwise only surface (expensively)
    during a live, paid QPU submission.
    """
    delta_ha = e_qpu_total - e_sim_total
    return {
        "experiment": "WH- VQE — QPU single-point validation at simulator-optimal theta*",
        "loaded_from": PARAMS_PATH.name,
        "backend": backend_name,
        "backend_qubits": backend_qubits,
        "job_id": job_id,
        "shots": QPU_SHOTS,
        "transpiler_optimization_level": 1,
        "mitigation": mitigation,
        "mitigation_detail": mitigation_detail,
        "E_sim_electronic_ha": float(params["final_electronic_energy_ha"]),
        "E_sim_total_ha": e_sim_total,
        "E_qpu_electronic_ha": e_qpu_electronic,
        "E_qpu_total_ha": e_qpu_total,
        "delta_E_ha": delta_ha,
        "delta_E_mHa": delta_ha * 1000,
        "delta_E_meV": delta_ha * HARTREE_TO_EV * 1000,
        "interpretation": INTERP_NONE if mitigation == "none" else INTERP_ZNE,
        "executed_at_utc": executed_at_iso,
        "retention_note": "IBM Open plan typically retains job records for ~30 days.",
    }


def run_qpu(mitigation: str = "none") -> None:
    if not PARAMS_PATH.exists():
        print(f"ERROR: {PARAMS_PATH} not found. Run 'sim' mode first.")
        sys.exit(1)

    try:
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from qiskit_ibm_runtime import EstimatorV2, QiskitRuntimeService
    except ImportError as exc:
        print(f"ERROR: qiskit_ibm_runtime missing — {exc}")
        sys.exit(1)

    payload = json.loads(PARAMS_PATH.read_text())
    theta_star = np.array(payload["final_parameters"])

    qubit_op = deserialize_pauli_op(payload["hamiltonian_pauli_op"])
    ansatz = build_ansatz(qubit_op.num_qubits)
    bound = ansatz.assign_parameters(theta_star)

    token = os.environ.get("IBM_QUANTUM_TOKEN")
    if token:
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
        del token
        print("authenticated via IBM_QUANTUM_TOKEN env var (in-memory)")
    else:
        try:
            service = QiskitRuntimeService()
            print("authenticated via saved account at ~/.qiskit/qiskit-ibm.json")
        except Exception as exc:
            print(
                "ERROR: no IBM_QUANTUM_TOKEN env var and no saved account found.\n"
                f"  underlying error: {exc}"
            )
            sys.exit(1)

    backend = service.least_busy(simulator=False, operational=True)
    print(f"submitting to: {backend.name}  (queued: {backend.status().pending_jobs})")

    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_ansatz = pm.run(bound)
    isa_H = qubit_op.apply_layout(isa_ansatz.layout)

    estimator = EstimatorV2(mode=backend)
    estimator.options.default_shots = QPU_SHOTS
    mitigation_detail = _configure_mitigation(estimator, mitigation)
    if mitigation == "zne":
        print(f"mitigation: zne  (noise factors {ZNE_NOISE_FACTORS}, "
              f"extrapolator {ZNE_EXTRAPOLATOR}, ~{len(ZNE_NOISE_FACTORS)}x QPU cost)")
    else:
        print("mitigation: none (raw hardware)")

    job = estimator.run([(isa_ansatz, isa_H)])
    print(f"job id: {job.job_id()}")
    print("waiting for result (95 Pauli terms, batched)...")
    result = job.result()
    E_electronic_qpu = float(result[0].data.evs)
    E_total_qpu = E_electronic_qpu + float(payload["energy_offset_ha"])

    E_total_sim = float(payload["final_total_energy_ha"])

    out = _build_qpu_payload(
        params=payload,
        backend_name=backend.name,
        backend_qubits=backend.num_qubits,
        job_id=job.job_id(),
        mitigation=mitigation,
        mitigation_detail=mitigation_detail,
        e_qpu_electronic=E_electronic_qpu,
        e_qpu_total=E_total_qpu,
        e_sim_total=E_total_sim,
        executed_at_iso=datetime.now(timezone.utc).isoformat(),
    )
    delta_ha = out["delta_E_ha"]

    suffix = "" if mitigation == "none" else f"_{mitigation}"
    out_path = RESULTS_DIR / (
        f"wh_qpu_validation{suffix}_"
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"
    )
    if out_path.exists():
        # Don't clobber an existing same-date artifact; disambiguate by job id.
        out_path = out_path.with_name(f"{out_path.stem}_{out.get('job_id', 'rerun')}.json")
    out_path.write_text(json.dumps(out, indent=2))

    print(f"\nwrote {out_path}")
    print(f"  E_sim (total)  : {E_total_sim:+.6f} Ha")
    print(f"  E_qpu (total)  : {E_total_qpu:+.6f} Ha")
    print(f"  Delta          : {delta_ha * 1000:+.3f} mHa "
          f"= {delta_ha * HARTREE_TO_EV * 1000:+.0f} meV")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("mode", choices=["sim", "qpu"])
    parser.add_argument(
        "--mitigation",
        choices=["none", "zne"],
        default="none",
        help=(
            "QPU error mitigation (qpu mode only). 'none' = raw hardware "
            "(default; preserves the baseline artifact). 'zne' = Zero-Noise "
            "Extrapolation + readout mitigation; real-hardware only, ~3-5x QPU cost."
        ),
    )
    args = parser.parse_args()
    if args.mode == "sim":
        if args.mitigation != "none":
            print("note: --mitigation applies to qpu mode only; ignored for sim.")
        run_sim()
    else:
        run_qpu(mitigation=args.mitigation)


if __name__ == "__main__":
    main()
