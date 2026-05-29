"""Strip outputs and execution counts from every notebook in this repo.

Run from anywhere:
    python setup/clean_notebook_outputs.py

Use this before committing so diffs don't include kernel-run output noise.
"""
import nbformat
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    notebooks_dir = repo_root / "notebooks"

    for nb_path in sorted(notebooks_dir.glob("*.ipynb")):
        nb = nbformat.read(nb_path, as_version=4)
        cleared = 0
        for cell in nb.cells:
            if cell.cell_type != "code":
                continue
            if cell.get("outputs"):
                cleared += len(cell["outputs"])
                cell["outputs"] = []
            if cell.get("execution_count") is not None:
                cell["execution_count"] = None
        nbformat.write(nb, nb_path)
        print(f"{nb_path.name:40s}  ({cleared} output blocks cleared)")


if __name__ == "__main__":
    main()
