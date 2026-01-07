# condacontrolplane Tools

This project exposes a small, read-only "control plane" API for inspecting a conda base environment.
These helpers live in `control_controlplane.tools` and are safe to call from other Python code or
from AI agents/tooling.

All functions auto-detect the conda base environment by default using `conda info --base`. You can
override the base prefix with a `prefix` argument.

## Python module: `control_controlplane.tools`

### `get_solvers_section(prefix: str | None = None) -> Section`

Return the **Solvers, Auth & Platform Detection** section.

- **prefix**: optional conda base prefix. If omitted, uses `conda info --base`.
- **returns**: a `Section` dataclass with:
  - `title: str`
  - `base_prefix: str`
  - `bin_dir: str`
  - `packages: dict[str, str]` – key packages (solvers, TLS/auth, platform helpers) and versions
  - `executables: dict[str, str | None]` – key executables and their resolved paths (or `None`)
  - `notes: list[str]` – human-readable notes about the section

Typical uses:
- Check whether `conda-libmamba-solver`, `mamba`, TLS packages, etc. are present in base.
- Inspect which `conda`/`mamba` binary is actually being used from the base bin directory.

---

### `get_compilers_section(prefix: str | None = None) -> Section`

Return the **Compiler Metapackages & Build Orchestrators** section.

Focuses on packages like:
- Compiler meta-packages: `compilers`, `c-compiler`, `cxx-compiler`, `fortran-compiler`
- Build tools: `conda-build`, `boa`, `rattler-build`, `constructor`, `conda-pack`

Also inspects common build executables in the base bin (e.g. `conda-build`, `conda-mambabuild`, `cmake`, `ninja`, `meson`).

---

### `get_packaging_section(prefix: str | None = None) -> Section`

Return the **Packaging Helpers (Build/Repair/Publish)** section.

Covers packaging-related tools, including:
- Core Python packaging: `pip`, `setuptools`, `wheel`, `build`, `twine`
- Modern Python package managers: `pipx`, `uv`, `pdm`, `poetry`, `hatch`
- Wheel-repair utilities (platform-specific):
  - macOS: `delocate`
  - Linux: `auditwheel`, `patchelf`

Executable inventory includes `pip`, `python`, `twine`, and platform-specific repair tools in base bin.

---

### `get_binaries(prefix: str | None = None, sample_n: int = 20) -> dict`

Return a summary of the base environment's bin directory contents.

- **prefix**: optional base prefix override.
- **sample_n**: number of entries from the bin directory to include in the sample (default: 20).
- **returns**: a dict
  - `{"count": int, "sample": list[str]}` where `count` is the total number of entries
    in the bin dir and `sample` contains the first `sample_n` names (sorted).

This is useful for quick, low-cost visibility into how "busy" the base bin is.

---

### `get_full_report(prefix: str | None = None, sample_n: int = 20) -> dict`

Return a JSON-serialisable payload equivalent to the CLI command:

- `conda-controlplane report --json`

The result has the shape:

```jsonc
{
  "base_prefix": "<path>",
  "bin_dir": "<path>",
  "sections": [
    {
      "title": "...",
      "base_prefix": "...",
      "bin_dir": "...",
      "packages": { "name": "version", ... },
      "executables": { "exe": "path-or-null", ... },
      "notes": ["..."]
    },
    // solvers, compilers, packaging sections in order
  ],
  "binaries": {
    "count": 123,
    "sample": ["conda", "python", ...]
  }
}
```

Ideal for:
- Feeding a single, structured snapshot into an AI agent.
- Logging or diagnostics about a given conda installation.

## Agent / tool integration notes

- These functions are read-only and do **not** mutate environments, install packages,
  or modify `PATH`.
- They assume `conda` is installed and either on `PATH` or pointed to by `CONDA_EXE`.
- When integrating into an AI agent, surface `prefix` (and optionally `sample_n`) as
  parameters so agents can target specific installations.
