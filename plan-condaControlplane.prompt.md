# conda-controlplane: plugin conversion + cleanup plan (working draft)

This document captures the current state of work and the remaining steps to finish converting this repo into a native conda plugin (`conda controlplane …`) while keeping the standalone console script (`conda-controlplane …`) as a compatibility path.

## What we already changed

### Plugin wiring

- Added a conda plugin module: `src/conda_controlplane/plugin.py`
  - Implements a `conda_subcommands()` hook that yields a `CondaSubcommand` named `controlplane`.
  - Delegates execution to the existing CLI entry point (`conda_controlplane.cli.main.main`).
  - Sets `prog="conda controlplane"` so help output matches the plugin invocation.
  - Uses an import-safe pattern so importing the module doesn’t hard-require `conda` at import time.

- Updated packaging config in `pyproject.toml`
  - Added `[project.entry-points."conda"]` so conda can discover the plugin.
  - Kept `[project.scripts]` for the console script `conda-controlplane`.
  - Added setuptools find/exclude rules to avoid packaging the legacy `control_controlplane*` package.

### CLI compatibility for plugin invocation

- Updated `src/conda_controlplane/cli/main.py` to accept an overridable `prog` so the exact command name displayed in `--help` output can differ between:
  - `conda-controlplane …` (console script)
  - `conda controlplane …` (conda plugin)

### Tooling + docs alignment

- Updated `ai-tools.manifest.yaml` to reference `conda_controlplane.tools` instead of legacy `control_controlplane.tools`.
- Updated documentation (`docs/tools.md`, `README.md`, and `tmp.prompt.md`) to:
  - Prefer `conda controlplane …` usage.
  - Reflect the current report structure (categories/binaries) rather than the legacy “sections list” shape.

### Tests

- Added a unit test ensuring the plugin module is import-safe (i.e., importing `conda_controlplane.plugin` should not crash in environments without `conda`).

## Known blockers / issues discovered

1. **Python is only available inside conda environments.**
   - Running tests from a bare shell fails (`python: command not found`).
   - Attempting `conda run -n dev python -m unittest -q` currently fails (exit code 5), suggesting the `dev` env may not have Python installed or command resolution is broken.

2. **Static analysis error in `src/conda_controlplane/shell/__init__.py`:**
   - `Pathish = Union[str, "os.PathLike[str]"]` but `os` is not imported.

3. **Repo cleanup still pending:**
   - The obsolete `src/control_controlplane/` directory still exists and should be deleted.
   - `src/conda_controlplane.egg-info/` appears present; if tracked, it should be removed (generated artifact).

## Remaining work (in order)

### 1) Fix `shell/__init__.py` typing import

- Add `import os` (or refactor typing to avoid referencing `os.PathLike` without importing `os`).
- Re-run static checks (or at least confirm the error disappears).

### 2) Remove the obsolete implementation

- Delete `src/control_controlplane/` from the repository.
- Ensure nothing in the supported code paths imports or references `control_controlplane`.
- Keep the setuptools exclusion in `pyproject.toml` as a belt-and-suspenders measure.

### 3) Remove build artifacts (egg-info) if tracked

- Determine whether `src/conda_controlplane.egg-info/` is committed.
- If committed, delete it and add appropriate ignore rules so it doesn’t come back.

### 4) Get a conda environment that actually has Python

- Use an env like `conda-controlplane-dev` (or fix `dev`) that includes Python.
- Confirm:
  - `python --version` works inside that env.
  - `python -m unittest -q` runs.

### 5) End-to-end verification

- Verify plugin path:
  - `conda controlplane --help`
  - `conda controlplane all --format json`

- Verify console script fallback:
  - `conda-controlplane --help`
  - `conda-controlplane all --format json`

## Acceptance criteria

The work is considered complete when:

- `conda controlplane --help` works and lists the expected subcommands (`solvers`, `compilers`, `packaging`, `network`, `all`) and formats (`summary`, `table`, `json`).
- The console script still works.
- `src/control_controlplane/` is deleted.
- `conda_controlplane.egg-info/` is not tracked (or is removed if it was).
- Unit tests pass inside a conda environment with Python.
- No obvious static analysis errors remain in the `src/conda_controlplane/` package.
