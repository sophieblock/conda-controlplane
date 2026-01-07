## Plan: Design `conda-controlplane` CLI and zsh shim

Design a Python-based CLI that inspects the Conda base “control plane” (solvers, compilers, packaging, network stack) and layer a thin, optional zsh shim on top. Keep the core OS-agnostic and testable, with the shim providing user-friendly functions like your current `conda-show-*` helpers.

### Steps

1. Define repo layout in `sophieblock/conda-controlplane` with `src/conda_controlplane/{core,cli,shell}` plus `tests`, `README`, and `pyproject.toml`.
2. Implement `core` modules (`conda_base`, `inspect_solvers`, `inspect_compilers`, `inspect_packaging`, `inspect_network`, `inspect_controlplane`, `formatting`) using `conda info --base` and `conda list -p <prefix>`.
3. Build a CLI layer (`cli/main.py`) with subcommands like `solvers`, `compilers`, `packaging`, `network`, `all` and options `--base-prefix`, `--format {json,table,summary}`, `--verbose`.
4. Create a zsh shim file (`shell/zsh_shim.zsh`) that defines functions (`conda-show-solvers`, `conda-show-compilers`, `conda-show-packaging`, `conda-show-controlplane`) calling the CLI with appropriate `--format` flags.
5. Wire up packaging: console-script entry point `conda-controlplane`, document installation via `pip` (and future `conda`) and a single `.zshrc` line to source the shim.
6. Add basic tests for Conda base discovery and classification logic, plus example outputs to keep the JSON schema and human-facing sections stable.

### Further Considerations

1. CLI framework: prefer `argparse` (zero deps) or `typer`/`click` (nicer UX) for subcommands and options?
2. Output stability: lock in a simple JSON schema early (per-category keys) to avoid breaking future tooling that may consume it.
3. Shim sourcing: keep it simple (direct path under site-packages) or add a tiny `conda-controlplane shell zsh` helper that prints the path for `.zshrc` to source?