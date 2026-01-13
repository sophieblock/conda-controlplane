# conda-controlplane

A small CLI to inspect the **conda base** *control-plane* tooling — the solvers, compilers, packaging helpers, and network stack that orchestrate environments rather than shipping in your runtime `LD_LIBRARY_PATH`.

It reports four categories:

1. Solvers/auth/platform tagging
2. Compiler metapackages & build orchestrators
3. Packaging helpers (build/repair/publish)
4. Network/TLS stack used by conda

This tool finds base using `conda info --base` (when possible) and queries package presence using `conda list -p <base_prefix>`.  

## Repo Layout
```
conda-controlplane/
  pyproject.toml
  README.md
  src/conda_controlplane/
    core/          # OS-agnostic inspection helpers
    cli/           # argparse-based CLI
    shell/         # optional zsh shim
  tests/
  docs/
```

## Installation

```zsh
python -m pip install conda-controlplane
```

If installed into the same environment as `conda`, the plugin registers a native subcommand:

```zsh
conda controlplane --help
```

## CLI
Preferred (conda plugin):
```zsh
conda controlplane --help
conda controlplane solvers --format summary
conda controlplane all --format json --verbose
```

Compatibility console script (same behavior):

```zsh
conda-controlplane --help
```

Supported subcommands: `solvers`, `compilers`, `packaging`, `network`, `all`.

Formats: `summary` (default), `table`, `json`. Use `--verbose` to include notes.

## Zsh Wrappers

To source the bundled shim for helper functions:

```zsh
source "$(python - <<'PY'
import conda_controlplane.shell as sh
print(sh.zsh_shim_path())
PY
)"
```

Shim functions:

- `conda-show-solvers`
- `conda-show-compilers`
- `conda-show-packaging`
- `conda-show-network`
- `conda-show-controlplane`
