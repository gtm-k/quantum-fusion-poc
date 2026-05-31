# Contributing

Thanks for your interest! This is a small, single-author **research prototype**,
so the scope is intentionally narrow — but issues and pull requests are welcome.

## Read this first

The repo demonstrates a **workflow** (VQE on a tungsten–hydrogen proxy molecule),
not a production chemistry tool. Before opening result-related issues, please
read the honesty caveats in the [README](README.md) and
[`docs/concepts/`](docs/concepts/) — the value of this project is its rigor about
what the numbers do and do **not** mean (e.g. WH⁻ well depth ≠ experimental
binding energy; unmitigated/ZNE results are methodology data points, not
chemistry; this is not a quantum-advantage claim).

## Setup

| Notebooks | Environment | Install |
|---|---|---|
| `01`, `02` | Windows or Linux | `pip install -r requirements-windows.txt` |
| `03` (needs pyscf) | WSL / Linux | `pip install -r requirements-wsl.txt` |

**Never hardcode your IBM Quantum token.** Set the `IBM_QUANTUM_TOKEN`
environment variable, or use a saved account at `~/.qiskit/qiskit-ibm.json`
(git-ignored). Tokens must never appear in code, notebooks, or commits.

## Before opening a PR

- **Clear notebook outputs:** `python setup/clean_notebook_outputs.py`
- **Don't submit QPU jobs in CI or PRs** — real hardware runs cost limited
  QPU minutes (IBM Open plan is 10 min/month).
- **Validate on the simulator first.** Any circuit change should be re-checked
  on the noiseless Aer simulator before spending QPU time.
- **Keep claims honest and caveated.** New results need their limitations stated
  alongside the numbers, matching the existing tone.

## Reporting a security/credential concern

If you find a leaked credential or a security issue, please open an issue
without posting the secret itself, or contact the maintainer privately.
