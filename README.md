# conda-controlplane

**A conda plugin for inspecting control-plane tooling in your conda base environment.**

This plugin helps you understand what orchestration tools live in your conda base — the solvers, compilers, packaging helpers, and network stack that manage environments rather than ship in your runtime workloads.

## What is Control-Plane Tooling?

Your conda **base environment** contains the tools that *orchestrate* package and environment management. These include:

1. **Solvers, Auth & Platform Detection** — libmamba, conda-libmamba-solver, platform tagging
2. **Compilers & Build Tools** — compiler metapackages, conda-build orchestrators
3. **Packaging Helpers** — conda-build, auditwheel, delocate, conda-package-handling
4. **Network & TLS Stack** — requests, urllib3, openssl, curl, certifi

These tools stay in base and don't ship in your environment's `LD_LIBRARY_PATH` or runtime.

## Installation

### From PyPI (coming soon)
```bash
pip install conda-controlplane
```

### From source (development)
```bash
git clone <repository-url>
cd conda-controlplane
pip install -e .
```

**Important:** Install this package in the same environment where conda is installed (typically your base environment) for the plugin to work.

## Usage

### Conda Plugin (Recommended)

Once installed, the plugin registers as a native conda subcommand:

```bash
# Show help
conda controlplane --help

# Inspect all categories with summary view
conda controlplane all

# Show solvers in table format
conda controlplane solvers --format table

# Export all data as JSON with verbose notes
conda controlplane all --format json --verbose
```

**Available subcommands:** `solvers`, `compilers`, `packaging`, `network`, `all`

**Output formats:** `summary` (default), `table`, `json`

**Flags:** `--verbose` (include detailed notes), `--base-prefix PATH` (override base detection)

### Console Script (Compatibility)

A standalone console script is also available:

```bash
conda-controlplane --help
conda-controlplane all --format summary
```

Both invocation methods provide identical functionality.

## How It Works

- Discovers base prefix using `conda info --base`
- Queries installed packages with `conda list -p <base_prefix> --json`
- Analyzes package presence and executable availability
- Reports findings in human-friendly or machine-readable formats

**This tool is read-only** — it never modifies packages, PATH, or environment variables.

## Examples

### Quick health check of your base environment
```bash
conda controlplane all
```

### See which solver you're using
```bash
conda controlplane solvers --format table
```

### Export control-plane inventory for debugging
```bash
conda controlplane all --format json > controlplane-inventory.json
```

### Check packaging tools before building conda packages
```bash
conda controlplane packaging --verbose
```

## Optional: Zsh Helper Functions

Source the bundled zsh shim for convenience wrappers:

```zsh
source "$(python - <<'PY'
import conda_controlplane.shell as sh
print(sh.zsh_shim_path())
PY
)"
```

This adds shell functions:
- `conda-show-solvers`
- `conda-show-compilers`
- `conda-show-packaging`
- `conda-show-network`
- `conda-show-controlplane`

## Development

### Setup
```bash
# Create development environment
conda create -n conda-controlplane-dev python=3.12 pytest
conda activate conda-controlplane-dev

# Install in editable mode
pip install -e .
```

### Run tests
```bash
python -m pytest tests/ -v
```

### Project structure
```
conda-controlplane/
├── src/conda_controlplane/
│   ├── plugin.py          # Conda plugin hook registration
│   ├── core/              # Inspection logic
│   ├── cli/               # Command-line interface
│   └── shell/             # Optional zsh helpers
├── tests/                 # Unit tests
├── docs/                  # Additional documentation
└── pyproject.toml         # Package configuration
```

## Documentation

- [.github/copilot-instructions.md](.github/copilot-instructions.md) — Plugin architecture and development guide
- [docs/overview.md](docs/overview.md) — Detailed overview of control-plane concepts
- [docs/base-env-policy.md](docs/base-env-policy.md) — Recommended base environment practices

## Why Use This?

Understanding your control-plane tooling helps with:
- **Debugging build issues** — Know which compiler/packaging tools are available
- **Solver troubleshooting** — Verify which solver and version you're using
- **Security audits** — Check TLS/network stack versions
- **Environment hygiene** — Keep base lean and focused on orchestration

## License

MIT
