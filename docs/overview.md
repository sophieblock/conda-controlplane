# Overview

## What is conda-controlplane?

`conda-controlplane` is a **conda plugin** that provides read-only inspection of control-plane tooling in your conda base environment. It helps you understand and debug the orchestration layer that manages your conda environments.

## What is the Control Plane?

In conda, the **control plane** refers to the tooling that *orchestrates* package and environment management but doesn't ship in your runtime workloads. These tools live in the conda **base environment** and include:

### 1. Solvers, Auth & Platform Detection
- **Solver engines**: libmamba, conda-libmamba-solver
- **Authentication**: conda-forge channel authentication
- **Platform detection**: Tools that determine your OS/architecture for package selection

### 2. Compilers & Build Tools
- **Compiler metapackages**: gcc/clang wrappers (mostly environment-scoped)
- **Build orchestrators**: conda-build and related tooling
- **Cross-compilation support**: Tools for building packages for different platforms

### 3. Packaging Helpers
- **Building**: conda-build, conda-package-handling
- **Repair/audit**: auditwheel (Linux), delocate (macOS)
- **Publishing**: conda-verify, package signing tools
- **Conversion**: Tools to convert between package formats

### 4. Network & TLS Stack
- **HTTP clients**: requests, urllib3, httpcore
- **TLS/SSL**: openssl, certifi
- **Network utilities**: curl, libcurl
- **Certificate management**: ca-certificates bundles

## Why Inspect Control Plane?

Understanding your control-plane tooling is valuable for:

1. **Troubleshooting solver issues** — Know which solver version you're using and whether it's configured correctly
2. **Debugging build failures** — Verify compiler metapackages and build tools are present
3. **Security audits** — Check TLS/SSL library versions and certificate bundles
4. **Environment hygiene** — Ensure base contains orchestration tools, not runtime dependencies
5. **Support requests** — Provide detailed environment information when reporting issues

## How It Works

### Detection Process

1. **Locate base prefix**
   - Uses `conda info --base` to find conda's base environment
   - Can be overridden with `--base-prefix` flag for testing

2. **Query packages**
   - Runs `conda list -p <base_prefix> --json` to get installed packages
   - Extracts package names and versions

3. **Check executables**
   - Looks for key executables in `<base_prefix>/bin` (or `Scripts` on Windows)
   - Verifies availability of critical tools like compilers, curl, etc.

4. **Categorize and report**
   - Groups packages by control-plane category
   - Formats output as summary, table, or JSON
   - Includes helpful notes when `--verbose` is used

### Safety Guarantees

This tool is **completely read-only** and never:
- Modifies `PATH` or environment variables
- Installs or uninstalls packages
- Changes conda configuration
- Writes to disk (except stdout)
- Executes package code

## Plugin Architecture

As a conda plugin, `conda-controlplane` integrates natively with conda:

- **Entry point**: Registered via `[project.entry-points."conda"]` in `pyproject.toml`
- **Hook system**: Uses conda's Pluggy-based plugin system
- **Subcommand registration**: Adds `conda controlplane` as a native command
- **Import safety**: Can be imported without conda installed (for testing)

See [../.github/copilot-instructions.md](../.github/copilot-instructions.md) for detailed plugin architecture information.

## Output Formats

### Summary Format (default)
Human-friendly report with sections for each category:
```
=== Solvers, Auth & Platform Detection ===
Packages:
  - conda-libmamba-solver: 24.1.0
  - libmamba: 1.5.6
...
```

### Table Format
Structured table showing packages and executables:
```
Category: Solvers
+-------------------------+----------+
| Package                 | Version  |
+-------------------------+----------+
| conda-libmamba-solver   | 24.1.0   |
...
```

### JSON Format
Machine-readable output for scripting/automation:
```json
{
  "base_prefix": "/path/to/base",
  "categories": {
    "solvers": {
      "packages": {...},
      "executables": {...}
    }
  }
}
```

## Related Documentation

- [base-env-policy.md](base-env-policy.md) — Best practices for base environment management
- [../.github/copilot-instructions.md](../.github/copilot-instructions.md) — Plugin implementation details
- [../README.md](../README.md) — Installation and usage guide
