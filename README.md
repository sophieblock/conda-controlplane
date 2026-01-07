# conda-controlplane

A small CLI to inspect **conda base** *control-plane* tooling — the stuff that orchestrates environments, builds, and packaging, rather than ending up on your runtime `LD_LIBRARY_PATH`.

It reports three categories:

1. Solver plugins, auth helpers, platform detection
2. Compiler metapackages (control-plane; usually env-scoped)
3. Packaging helpers (wheel build/repair/publish tooling)

This tool finds base using `conda info --base` (when possible) and queries package presence using `conda list -p <base_prefix>`.  

## Repo Layout
```csharp
conda-controlplane/
  pyproject.toml
  README.md
  .gitignore
  src/
    conda_controlplane/
      __init__.py
      cli.py
      conda.py
      report.py
  zsh/
    conda-controlplane.zsh
  docs/
    overview.md
    base-env-policy.md
  scripts/
    dev_install.sh
  tests/
    test_report.py
  .github/
    prompts/
      conda-control-plane-inspector.prompt.md
```