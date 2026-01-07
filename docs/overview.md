# Overview

`conda-controlplane` is a read-only inspector for tools that live in (or relate to) the conda **base** environment.

It focuses on control-plane categories:
- Solver selection and solver plugins
- Authentication/TLS + HTTP stack used by package management
- Platform detection / tagging utilities
- Compiler metapackages (mostly env-scoped)
- Packaging helpers (wheel building, repair, publishing)

Implementation notes:
- Base prefix is detected using `conda info --base`.
- Packages are queried with `conda list -p <base_prefix> --json`.

The tool does not:
- modify PATH
- export/alter environment variables
- install/uninstall packages
