# Refactor & Cleanup Tasks

> **Context**: This project is a custom conda plugin. See [../.github/copilot-instructions.md](../.github/copilot-instructions.md) for full architectural details, plugin system explanation, and development environment constraints.

## Summary

The plugin conversion is **mostly complete**. This document tracks the remaining tactical cleanup tasks to finalize the implementation.

## Completed Work ✅

The major plugin implementation is done:
- ✅ Plugin hook in [plugin.py](../../src/conda_controlplane/plugin.py) with `@conda.plugins.hookimpl`
- ✅ Entry point registration in [pyproject.toml](../../pyproject.toml) under `[project.entry-points."conda"]`
- ✅ Dual-mode support: `conda controlplane` (plugin) + `conda-controlplane` (console script)
- ✅ Import-safety test in [test_core.py](../../tests/test_core.py)
- ✅ CLI accepts overridable `prog` parameter for correct help output
- ✅ Documentation updated to prefer plugin usage

## Remaining Tasks 🚧

### 1. Fix typing error in `shell/__init__.py`

**Issue**: Line 6 references `os.PathLike[str]` without importing `os`

**Fix**:
```python
# Add import at top of file
import os
```

**Files**: [src/conda_controlplane/shell/__init__.py:6](../../src/conda_controlplane/shell/__init__.py#L6)

---

### 2. Delete obsolete `control_controlplane` directory

**Issue**: Legacy flat implementation still exists at `src/control_controlplane/`

**Action**:
- Delete entire `src/control_controlplane/` directory
- Verify no imports reference it (already excluded from packaging in `pyproject.toml`)

**Rationale**: This is the old implementation before modular refactoring to `conda_controlplane`

---

### 3. Clean up build artifacts

**Issue**: `src/conda_controlplane.egg-info/` present (generated build artifact)

**Action**:
- Check if tracked in git: `git ls-files src/conda_controlplane.egg-info/`
- If tracked, delete it: `rm -rf src/conda_controlplane.egg-info/`
- Ensure `.gitignore` includes `*.egg-info/`

---

### 4. Verify development environment

**Issue**: Tests need to run in a conda environment with Python installed

**Action**:
```bash
# Verify environment exists and has Python
conda activate conda-controlplane-dev
python --version
python -m pytest
```

**Note**: See [Development Environment Constraints](../.github/copilot-instructions.md#development-environment-constraints) for critical info about Python only being available in conda environments.

---

### 5. End-to-end verification

**Verify plugin mode**:
```bash
conda controlplane --help
conda controlplane all --format json
```

**Verify console script fallback**:
```bash
conda-controlplane --help
conda-controlplane all --format json
```

## Acceptance Criteria

The refactor is complete when:

- ✅ No static analysis errors (typing error in `shell/__init__.py` fixed)
- ✅ `src/control_controlplane/` deleted
- ✅ Build artifacts not tracked in git
- ✅ Tests pass: `python -m pytest` (in conda environment)
- ✅ Plugin works: `conda controlplane --help` shows subcommands
- ✅ Console script works: `conda-controlplane --help` shows subcommands
- ✅ Both modes support all subcommands: `solvers`, `compilers`, `packaging`, `network`, `all`
- ✅ All output formats work: `summary`, `table`, `json`

## Additional Notes

### Environment Setup Reminder

**CRITICAL**: Python commands only work inside conda environments. Always activate first:

```bash
conda activate conda-controlplane-dev
```

See [copilot-instructions.md](../.github/copilot-instructions.md#development-environment-constraints) for full details.

### Plugin vs Console Script

Both invocation methods are supported:
- **Plugin** (`conda controlplane`): Native conda integration, discovered via entry points
- **Console script** (`conda-controlplane`): Backward compatibility, direct executable

Both use the same underlying implementation in `conda_controlplane.cli.main:main()`.
