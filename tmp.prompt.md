## Current shape of `conda-controlplane` (aligned to repo)

A small, read-only inspector for the conda **base** control plane (solvers/auth/platform, compiler metapackages, packaging helpers). Core is Python-only and OS-agnostic; output can be text or JSON.

### Repo layout (today)
- `pyproject.toml`: `conda-controlplane` 0.1.0, Python >=3.11, zero runtime deps, console script `conda-controlplane = control_controlplane.cli:main`.
- `src/control_controlplane/`: `cli.py`, `conda.py`, `report.py`, `tools.py`.
- `docs/`: `overview.md`, `base-env-policy.md`, `tools.md`.
- No zsh shim or tests are present yet.

### CLI surface (`control_controlplane/cli.py`)
- Parser: `argparse` with flags `--json` (machine-readable) and `--prefix` (override base prefix; default auto-detect via `conda info --base`).
- Subcommands: `report`, `solvers`, `compilers`, `packaging`, `binaries`.
- Text mode: prints sections with packages/executables/notes; binaries show count + first 20 entries.
- JSON mode: emits a payload containing base prefix, bin dir, per-section data, and optional binaries block.

### Core logic
- `conda.py`: picks `CONDA_EXE` or `conda` on PATH; finds base via `conda info --base`; lists packages via `conda list -p <prefix> --json`; derives bin dir (`<prefix>/bin` or `Scripts`).
- `report.py`: builds three sections (Solvers/Auth/Platform, Compiler Metapackages & Build Orchestrators, Packaging Helpers). Each section includes versions from `conda list` and key executables found in base bin.
- `tools.py`: agent-friendly helpers (`get_solvers_section`, `get_compilers_section`, `get_packaging_section`, `get_binaries`, `get_full_report`) with optional prefix override and sample size for binaries.

### JSON shape (CLI `--json` or `tools.get_full_report`)
```jsonc
{
	"base_prefix": "<path>",
	"bin_dir": "<path>",
	"sections": [
		{
			"title": "...",
			"base_prefix": "...",
			"bin_dir": "...",
			"packages": { "name": "version", ... },
			"executables": { "exe": "path-or-null", ... },
			"notes": ["..."]
		}
		// solvers, compilers, packaging in that order
	],
	"binaries": { "count": 123, "sample": ["conda", "python", ...] }
}
```

### Known gaps / next steps
- Add tests around base discovery, package selection, executables resolution, and JSON schema stability.
- Optional: add a zsh shim (none exists yet) that wraps the CLI, or expose a helper to print the shim path for sourcing.
- Consider richer formats (table/summary) only if adding dependencies is acceptable; currently output is text or JSON only.