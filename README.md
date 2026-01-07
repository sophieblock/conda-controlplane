# conda-controlplane

A small CLI to inspect **conda base** *control-plane* tooling — the stuff that orchestrates environments, builds, and packaging, rather than ending up on your runtime `LD_LIBRARY_PATH`.

It reports three categories:

1. Solver plugins, auth helpers, platform detection
2. Compiler metapackages (control-plane; usually env-scoped)
3. Packaging helpers (wheel build/repair/publish tooling)

This tool finds base using `conda info --base` (when possible) and queries package presence using `conda list -p <base_prefix>`.  

## Install (developer mode)

From the repo root:

```zsh
python -m pip install -e .
```

After install, the command is:
```zsh
conda-controlplane --help
```

## Install via pipx (recommended for “control-plane” CLIs)
pipx installs Python apps in an isolated environment and exposes their entry-point commands.

Example patterns:
- pipx install . (local folder)
- pipx install git+<repo-url> (from source control)

## Usage 
Show everything:
```zsh
conda-controlplane report
```

Only one section:
```zsh
conda-controlplane solvers
conda-controlplane compilers
conda-controlplane packaging
conda-controlplane binaries
```
JSON output:

```zsh
conda-controlplane report --json
```

Override base prefix (rarely needed):
```zsh
conda-controlplane report --prefix /path/to/your/base
```
## Zsh wrappers 

If you prefer your original `conda-show-*` commands, source:
`zsh/conda-controlplane.zsh` from your `.zshrc`.

## Notes
- Read-only inspection: no PATH edits, no env-var exports.

- Cross-platform: macOS/Linux detection for delocate/auditwheel/patchelf.
