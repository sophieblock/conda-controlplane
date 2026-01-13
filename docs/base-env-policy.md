# Base Environment Policy (Opinionated Best Practices)

## Philosophy

**Keep base as the "orchestrator" layer, not a runtime environment.**

The conda base environment should contain tools that *manage* environments, not tools that *run* in environments. This separation keeps base lean, stable, and easy to maintain.

## Recommended Base Contents

### Core (Essential)
- **conda** — The package manager itself
- **Solver plugin** — libmamba, conda-libmamba-solver (recommended for faster solving)
- **Auth/TLS chain** — openssl, certifi, ca-certificates
- **HTTP client** — requests, urllib3 (used by conda)

### Optional (If You Build/Publish Packages)
- **conda-build** — For building conda packages
- **conda-package-handling** — Package compression/decompression
- **Audit tools** — auditwheel (Linux), delocate (macOS) for wheel repair
- **Publishing tools** — anaconda-client, conda-verify

### Shell Integration (Minimal)
- **Completion scripts** — conda shell completions
- **Environment hooks** — conda activation scripts
- **Helper tools** — This plugin (`conda-controlplane`)!

## What to AVOID in Base

### ❌ Heavy Runtime Stacks
Don't install these in base unless you intentionally use base as your primary dev environment:
- **Scientific computing**: numpy, scipy, pandas, matplotlib
- **Machine learning**: torch, tensorflow, scikit-learn
- **Web frameworks**: django, flask, fastapi
- **Data processing**: dask, ray, spark

**Why?** These packages:
- Cause dependency conflicts with solver upgrades
- Bloat the base environment
- Make conda slower to start
- Complicate troubleshooting

### ❌ Project-Specific Dependencies
- Language runtimes for specific projects
- Project libraries and tools
- Development dependencies tied to one project

**Why?** Base should be project-agnostic. Each project gets its own environment.

### ❌ Multiple Python Versions
- Don't install python2, python3.8, python3.9, etc. all in base
- Base should have *one* Python version for conda itself

**Why?** Prevents confusion and conflicts. Use separate environments for different Python versions.

## Rationale for Separation

### 1. Fewer Conflicts
When base is minimal, conda upgrades rarely break due to dependency conflicts. Adding heavy packages increases the conflict surface area.

### 2. Easier Recovery
If base gets corrupted, recovery is simple when it only contains orchestration tools. A clean reinstall is fast and doesn't lose project work.

### 3. Faster Startup
Conda's startup time increases with the number of packages in base. Keep it lean for snappy performance.

### 4. Clear Mental Model
**Base = Control Plane**: Tools that manage environments
**Environments = Workloads**: Tools that do actual work

This separation makes it obvious where each tool belongs.

### 5. Upgrade Safety
When you upgrade conda or the solver, you want minimal risk. Fewer packages in base means fewer things that can break.

## Checking Your Base Environment

Use this plugin to audit what's in your base:

```bash
# See everything
conda controlplane all --format table

# Check if you have heavy packages that shouldn't be there
conda list -n base | grep -E "numpy|scipy|torch|tensorflow|pandas"
```

## Migration Strategy

If your base is already bloated, here's how to clean it up:

### Option 1: Selective Removal (Conservative)
```bash
# Remove obvious runtime packages
conda remove -n base numpy scipy pandas matplotlib

# Keep conda, solver, and build tools
```

### Option 2: Fresh Start (Recommended)
```bash
# Create a new environment with your old base's workflow
conda create -n my-work-env python=3.11 numpy scipy pandas

# Reinstall conda (fresh base)
# See: https://docs.conda.io/projects/conda/en/latest/user-guide/install/
```

### Option 3: Treat Base as Dev Environment (Acceptable)
If you actively use base for development work, that's okay! Just be aware of the trade-offs:
- Slower conda operations
- More potential for conflicts
- Harder to recover if something breaks

## Example: Clean Base

A minimal, healthy base environment might look like:

```
conda                    24.1.0
conda-libmamba-solver    24.1.0
libmamba                 1.5.6
requests                 2.31.0
urllib3                  2.0.7
openssl                  3.2.0
certifi                  2024.2.2
ca-certificates          2024.2.2
conda-build              24.1.0   # Optional, if you build packages
conda-controlplane       0.1.0    # This plugin!
```

Total: ~10-15 packages focused on orchestration.

## When to Break the Rules

**It's okay to have a heavier base if:**
1. You explicitly choose to use base as your primary dev environment
2. You understand the trade-offs
3. You have a backup/recovery plan
4. You're willing to deal with occasional conflicts

Just make it a *conscious choice*, not accidental accumulation.

## Further Reading

- [Conda environments best practices](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
- [Understanding conda base environment](https://conda.io/projects/conda/en/latest/user-guide/concepts/environments.html)

## Summary

**Keep base lean. Keep base clean. Keep base for orchestration.**

Use `conda controlplane all` regularly to ensure your base stays focused on its job: managing environments, not running them.
