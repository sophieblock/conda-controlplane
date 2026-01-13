# Copilot Instructions: conda-controlplane

## Project Overview

**conda-controlplane is a custom conda plugin** that extends conda's functionality to inspect and report on the control-plane tooling in conda's base environment.

## What is a Conda Plugin?

This project aims to be a **conda plugin** that can be invoked as:
```bash
conda controlplane [subcommand]
```

It integrates with conda's plugin system to provide control-plane inspection capabilities as a native conda command.

## What are Control-Plane Tools?

Control-plane tools are packages that live in conda's **base environment** and orchestrate environment management, but don't ship in your runtime environments:

1. **Solvers/Auth/Platform**: libmamba, conda-libmamba-solver, conda-forge channel tools
2. **Compilers**: gcc/clang metapackages, conda-build, build orchestrators
3. **Packaging helpers**: conda-build, conda-package-handling, auditwheel, delocate, conda-verify
4. **Network/TLS stack**: requests, urllib3, openssl, curl, certifi

These tools manage and build environments but are separate from the environments themselves.

## Conda Plugin System Architecture

### How Conda Plugins Work

Conda uses the **Pluggy framework** (same as pytest, tox, devpi) to implement its plugin system. This provides:

1. **Hook-based extension**: Plugins extend conda by implementing specific hook functions
2. **Entry point discovery**: Conda auto-discovers plugins via Python package entry points
3. **Runtime integration**: Plugins are loaded and executed as part of conda's normal operation

### Key Integration Points

To create a conda plugin, you need:

1. **Plugin Hook Implementation** - Create functions decorated with `@conda.plugins.hookimpl`
2. **Entry Point Registration** - Register your plugin in `pyproject.toml` or `setup.py`
3. **Plugin Type Objects** - Return appropriate conda plugin types (e.g., `CondaSubcommand`)

### Example: Subcommand Plugin

```python
import conda.plugins
import conda.plugins.types

def controlplane_action(arguments: list[str]):
    """Main entry point when `conda controlplane` is invoked."""
    # Your CLI logic here
    pass

@conda.plugins.hookimpl
def conda_subcommands():
    """Hook that registers subcommands with conda."""
    yield conda.plugins.types.CondaSubcommand(
        name="controlplane",
        action=controlplane_action,
        summary="Inspect conda base control-plane tooling",
    )
```

### Entry Point Configuration

In `pyproject.toml`:
```toml
[project.entry-points."conda"]
conda-controlplane = "conda_controlplane.plugin"
```

This tells conda to load `conda_controlplane.plugin` module and discover hooks.

### Architecture Differences: Standalone CLI vs Plugin

**Current (Standalone CLI)**:
```
User runs: conda-controlplane solvers
         ↓
Entry point: [project.scripts] conda-controlplane
         ↓
Calls: conda_controlplane.cli.main:main()
         ↓
Uses subprocess to call: conda info --base, conda list
```

**Target (Conda Plugin)**:
```
User runs: conda controlplane solvers
         ↓
Conda discovers: [project.entry-points."conda"]
         ↓
Loads: conda_controlplane.plugin module
         ↓
Calls: @hookimpl decorated function
         ↓
Executes: your action function
         ↓
Can use conda's internal APIs directly (no subprocess needed!)
```

### Benefits of Plugin Architecture

1. **Native integration**: `conda controlplane` feels like a built-in command
2. **Internal API access**: Can use `conda.base.context`, `conda.core.*` directly
3. **Auto-discovery**: Users don't need to know it's a plugin
4. **Consistent UX**: Follows conda's conventions for help, arguments, etc.

## Package Structure

The correct package name is **`conda_controlplane`** (with underscore):
- Python module: `conda_controlplane`
- PyPI package: `conda-controlplane` (with hyphen)
- Conda plugin command: `conda controlplane` (space-separated)

### Directory Structure
```
src/conda_controlplane/
  __init__.py
  plugin.py          # NEW: Plugin hook registration
  core/              # Core inspection logic
    conda_base.py    # Context and conda interactions
    inspect_*.py     # Category-specific inspectors
    formatting.py    # Output formatting
    common.py        # Shared utilities
  cli/               # CLI interface (plugin entry point)
    main.py          # Argument parsing and command dispatch
  shell/             # Optional zsh shim helpers
    __init__.py
    zsh_shim.zsh
```

## DO NOT Use `control_controlplane`

The directory `src/control_controlplane/` is **obsolete** and should be deleted. It contains an older, flat implementation that was refactored into the current modular structure.

- ❌ WRONG: `control_controlplane`
- ✅ CORRECT: `conda_controlplane`

## Plugin Integration Goals

As a conda plugin, this tool should:
1. Register as a conda subcommand via conda's plugin system
2. Be invokable as `conda controlplane` (not `conda-controlplane`)
3. Provide subcommands: `solvers`, `compilers`, `packaging`, `network`, `all`
4. Support multiple output formats: `summary`, `table`, `json`
5. Allow base prefix override for testing/debugging

## Implementation Notes

- The plugin inspects conda's base environment from the outside
- Uses `conda info --base` to locate the base prefix
- Uses `conda list -p <prefix> --json` to query installed packages
- Analyzes package presence and executable availability
- Reports findings in user-friendly or machine-readable formats

## Development Environment Constraints

### Python/Conda Environment Setup

**CRITICAL**: Python is ONLY available inside conda environments. The default terminal shell does not auto-activate any conda environment, so `python` and `pip` commands are NOT available in a bare shell.

- **Always activate an environment first**: Before running any Python commands, tests, or builds, you must activate a conda environment
- **Testing requires conda base**: This plugin inspects conda's base environment, so tests should run in an environment where conda itself is available
- **No system Python**: Do not assume `/usr/bin/python` or similar system Python installations exist or should be used
- **All Python tooling requires conda**: Commands like `pytest`, `pip`, `python`, etc. will fail with "command not found" unless a conda environment is active

### Running Commands

```bash
# ❌ WRONG - will fail with "command not found: python"
python -m pytest
pip install -e .

# ✅ CORRECT - activate environment first
conda activate conda-controlplane-dev
python -m pytest
pip install -e .
```

### Setting Up Development Environment

```bash
# Create development environment
conda create -n conda-controlplane-dev python=3.11
conda activate conda-controlplane-dev

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Customization Philosophy

This is **your custom plugin**, designed to be:
- Extensible: Easy to add new control-plane categories
- Modular: Clear separation between inspection, formatting, and CLI
- Testable: Dependency injection for external commands
- Flexible: Multiple output formats for different use cases

## Current Implementation Status

### ✅ Completed
- Plugin hook implementation in [plugin.py](../src/conda_controlplane/plugin.py)
- Entry point registration in [pyproject.toml](../pyproject.toml)
- Dual-mode support: both `conda controlplane` (plugin) and `conda-controlplane` (console script)
- Import-safety test for plugin module
- Core inspection logic for all categories (solvers, compilers, packaging, network)

### 🚧 Remaining Tasks
See [refactor-prompt.md](.github/prompts/refactor-prompt.md) for tactical cleanup tasks.

## References

- [Conda Plugin Documentation](https://docs.conda.io/projects/conda/en/latest/dev-guide/plugins/index.html)
- [Introducing Conda Plugin Mechanism](https://www.anaconda.com/blog/introducing-a-new-plugin-mechanism-for-conda)
- [Conda Plugin API](https://docs.conda.io/projects/conda/en/latest/dev-guide/api/conda/plugins/index.html)
