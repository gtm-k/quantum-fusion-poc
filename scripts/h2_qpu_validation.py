"""H2 VQE QPU validation — train on Aer simulator, validate single-point on real IBM QPU.

The Hamiltonian and ansatz are defined once here, so the simulator-optimal
parameters that get saved to JSON are guaranteed to match what the QPU
job submits.

Usage:
    python scripts/h2_qpu_validation.py sim
        Train on Aer simulator, write
        results/qpu_runs/h2_optimal_params.json with the optimal theta*
        plus the full ansatz/optimizer/Hamiltonian configuration.

    python scripts/h2_qpu_validation.py qpu
        Load theta* from the JSON, submit a single-point energy
        evaluation to the least-busy IBM Quantum backend, write
        results/qpu_runs/h2_qpu_validation_<DATE>.json with the
        measured energy and the simulator-vs-QPU delta.

Environment:
    IBM_QUANTUM_TOKEN must be set, OR a saved account must exist at
    ~/.qiskit/qiskit-ibm.json (the script tries the env var first, then
    falls back to the saved account).
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import efficient_su2
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

HARTREE_TO_EV = 27.211386245988

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "results" / "qpu_runs"
PARAMS_PATH = RESULTS_DIR / "h2_optimal_params.json"


def build_problem():
    """Build the H2 Hamiltonian (parity-tapered, 2 circuit qubits) and the ansatz.

    Hamiltonian coefficients from O'Malley et al., Phys. Rev. X 6, 031007
    (2016), Appendix B. STO-3G basis at r = 0.735 Angstrom.
    """
    H2 = SparsePauliOp.from_list([
        ("II", -1.052373245772859),
        ("IZ",  0.39793742484318045),
        ("ZI", -0.39793742484318045),
        ("ZZ", -0.01128010425623538),
        ("XX",  0.18093119978423156),
    ])
    ansatz = efficient_su2(num_qubits=2, reps=2, entanglement="linear")
    return H2, ansatz


def run_sim() -> None:
    H2, ansatz = build_problem()
    estimator = StatevectorEstimator()
    history: list[float] = []

    def cost(params):
        job = estimator.run([(ansatz, H2, params)])
        e = float(job.result()[0].data.evs)
        history.append(e)
        return e

    rng = np.random.default_rng(seed=7)
    x0 = rng.uniform(0, 2 * np.pi, ansatz.num_parameters)
    result = minimize(
        cost, x0=x0, method="COBYLA",
        options={"maxiter": 300, "rhobeg": 0.5},
    )
    E_exact = float(np.linalg.eigvalsh(H2.to_matrix())[0])
    err = abs(result.fun - E_exact)

    payload = {
        "experiment": "H2 ground-state VQE — simulator-optimal parameters",
        "molecule": "H2",
        "bond_length_angstrom": 0.735,
        "basis": "STO-3G",
        "hamiltonian_source": "O'Malley et al., Phys. Rev. X 6, 031007 (2016), Appendix B",
        "ansatz": {
            "kind": "efficient_su2",
            "num_qubits": 2,
            "reps": 2,
            "entanglement": "linear",
            "num_parameters": int(ansatz.num_parameters),
        },
        "optimizer": {
            "method": "COBYLA",
            "maxiter": 300,
            "rhobeg": 0.5,
            "rng_seed": 7,
        },
        "simulator": "qiskit StatevectorEstimator (noiseless)",
        "final_parameters": [float(x) for x in result.x],
        "final_energy_ha": float(result.fun),
        "exact_eigenvalue_ha": E_exact,
        "vqe_error_ha": err,
        "vqe_error_nha": err * 1e9,
        "cost_evaluations": len(history),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PARAMS_PATH.write_text(json.dumps(payload, indent=2))

    print(f"wrote {PARAMS_PATH}")
    print(f"  VQE energy : {result.fun:+.10f} Ha")
    print(f"  Exact      : {E_exact:+.10f} Ha")
    print(f"  Error      : {err * 1e9:.3f} nHa")
    print(f"  Cost calls : {len(history)}")


def run_qpu() -> None:
    if not PARAMS_PATH.exists():
        print(f"ERROR: {PARAMS_PATH} not found. Run 'sim' mode first.")
        sys.exit(1)

    try:
        from qiskit_ibm_runtime import EstimatorV2, QiskitRuntimeService
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    except ImportError as exc:
        print(f"ERROR: qiskit_ibm_runtime missing — {exc}")
        sys.exit(1)

    payload = json.loads(PARAMS_PATH.read_text())
    theta_star = np.array(payload["final_parameters"])

    H2, ansatz = build_problem()
    bound = ansatz.assign_parameters(theta_star)

    # Authentication: prefer the env var (in-memory, ephemeral). Fall back
    # to a previously saved account at ~/.qiskit/qiskit-ibm.json if the env
    # var isn't set in this shell (notebook 01's optional save_account
    # cell puts it there).
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
                "  Either set the env var first, or run "
                "notebook 01's optional save_account cell to persist credentials.\n"
                f"  underlying error: {exc}"
            )
            sys.exit(1)

    backend = service.least_busy(simulator=False, operational=True)
    print(f"submitting to: {backend.name}  (queued: {backend.status().pending_jobs})")

    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    isa_ansatz = pm.run(bound)
    isa_H = H2.apply_layout(isa_ansatz.layout)

    estimator = EstimatorV2(mode=backend)
    estimator.options.default_shots = 4096

    job = estimator.run([(isa_ansatz, isa_H)])
    print(f"job id: {job.job_id()}")
    result = job.result()
    E_qpu = float(result[0].data.evs)
    E_sim = float(payload["final_energy_ha"])

    out = {
        "experiment": "H2 VQE — QPU single-point validation at simulator-optimal theta*",
        "loaded_from": PARAMS_PATH.name,
        "backend": backend.name,
        "backend_qubits": backend.num_qubits,
        "job_id": job.job_id(),
        "shots": 4096,
        "transpiler_optimization_level": 1,
        "mitigation": "none",
        "E_sim_ha": E_sim,
        "E_qpu_ha": E_qpu,
        "delta_E_ha": E_qpu - E_sim,
        "delta_E_mHa": (E_qpu - E_sim) * 1000,
        "delta_E_meV": (E_qpu - E_sim) * HARTREE_TO_EV * 1000,
        "interpretation": (
            "delta_E is the lumped hardware-cost: shot noise + readout error + "
            "gate errors + transpilation effects + backend drift. No mitigation."
        ),
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "retention_note": "IBM Open plan typically retains job records for ~30 days.",
    }
    out_path = RESULTS_DIR / f"h2_qpu_validation_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"
    if out_path.exists():
        # Don't clobber an existing same-date artifact; disambiguate by job id.
        out_path = out_path.with_name(f"{out_path.stem}_{out.get('job_id', 'rerun')}.json")
    out_path.write_text(json.dumps(out, indent=2))

    print(f"wrote {out_path}")
    print(f"  E_sim : {E_sim:+.6f} Ha")
    print(f"  E_qpu : {E_qpu:+.6f} Ha")
    print(f"  Delta : {(E_qpu - E_sim) * 1000:+.3f} mHa "
          f"= {(E_qpu - E_sim) * HARTREE_TO_EV * 1000:+.0f} meV")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("mode", choices=["sim", "qpu"])
    args = parser.parse_args()
    if args.mode == "sim":
        run_sim()
    else:
        run_qpu()


if __name__ == "__main__":
    main()
