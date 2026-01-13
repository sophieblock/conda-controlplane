## Current shape of `conda-controlplane` (aligned to repo)

A small, read-only inspector for the conda **base** control plane (solvers/auth/platform, compiler metapackages, packaging helpers). Core is Python-only and OS-agnostic; output can be text or JSON.

### Repo layout (today)
- `pyproject.toml`: `conda-controlplane` 0.1.0, Python >=3.11, zero runtime deps, console script `conda-controlplane = conda_controlplane.cli.main:main`.
- `src/conda_controlplane/`: plugin + CLI + core inspection modules.
- `docs/`: `overview.md`, `base-env-policy.md`, `tools.md`.
- Zsh shim and unit tests are present.

### CLI surface (`conda_controlplane/cli/main.py`)
- Parser: `argparse` with flags `--base-prefix` (override base prefix; default auto-detect via `conda info --base`) and `--format` (`summary|table|json`).
- Subcommands: `solvers`, `compilers`, `packaging`, `network`, `all`.
- JSON mode: emits a payload containing base prefix, bin dir, and per-category data.

### Core logic
- `core/conda_base.py`: picks `CONDA_EXE` or `conda` on PATH; finds base via `conda info --base`; lists packages via `conda list -p <prefix> --json`; derives bin dir (`<prefix>/bin` or `Scripts`).
- `core/inspect_*.py`: builds category payloads (solvers/compilers/packaging/network).
- `tools.py`: agent-friendly helpers with optional prefix override and bin inventory sampling.

### JSON shape (CLI `all --format json` or `tools.get_full_report`)
```jsonc
{
	"base_prefix": "<path>",
	"bin_dir": "<path>",
	"categories": {
		"solvers": { "title": "...", "packages": {"name": "version"}, "executables": {"exe": null}, "notes": ["..."] },
		"compilers": { "title": "...", "packages": {"name": "version"}, "executables": {"exe": null}, "notes": ["..."] },
		"packaging": { "title": "...", "packages": {"name": "version"}, "executables": {"exe": null}, "notes": ["..."] },
		"network": { "title": "...", "packages": {"name": "version"}, "executables": {"exe": null}, "notes": ["..."] }
	},
	"binaries": { "count": 123, "sample": ["conda", "python", ...] }
}
```

### Known gaps / next steps
- Consider wiring as a conda plugin (`conda controlplane`) via entry points.