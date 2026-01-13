from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from conda_controlplane.core.common import package_map
from conda_controlplane.core.conda_base import CondaContext, load_packages, make_conda_context
from conda_controlplane.core.inspect_compilers import inspect_compilers
from conda_controlplane.core.inspect_controlplane import inspect_all
from conda_controlplane.core.inspect_network import inspect_network
from conda_controlplane.core.inspect_packaging import inspect_packaging
from conda_controlplane.core.inspect_solvers import inspect_solvers


@dataclass(frozen=True)
class Section:
    title: str
    base_prefix: str
    bin_dir: str
    packages: Dict[str, str]
    executables: Dict[str, Optional[str]]
    notes: List[str]


def _ctx(prefix_override: Optional[str] = None) -> CondaContext:
    return make_conda_context(base_prefix=prefix_override)


def _section(payload: Dict[str, object]) -> Section:
    title = payload.get("title")
    base_prefix = payload.get("base_prefix")
    bin_dir = payload.get("bin_dir")
    packages = payload.get("packages")
    executables = payload.get("executables")
    notes = payload.get("notes")

    return Section(
        title=str(title) if isinstance(title, str) else "",
        base_prefix=str(base_prefix) if isinstance(base_prefix, str) else "",
        bin_dir=str(bin_dir) if isinstance(bin_dir, str) else "",
        packages=dict(packages) if isinstance(packages, dict) else {},
        executables=dict(executables) if isinstance(executables, dict) else {},
        notes=list(notes) if isinstance(notes, list) else [],
    )


def get_solvers_section(prefix: Optional[str] = None) -> Section:
    """Return the Solvers/Auth/Platform section for the given base prefix."""

    ctx = _ctx(prefix)
    pkgs = package_map(load_packages(ctx))
    return _section(inspect_solvers(ctx, pkgs))


def get_compilers_section(prefix: Optional[str] = None) -> Section:
    """Return the Compiler Metapackages & Build Orchestrators section."""

    ctx = _ctx(prefix)
    pkgs = package_map(load_packages(ctx))
    return _section(inspect_compilers(ctx, pkgs))


def get_packaging_section(prefix: Optional[str] = None) -> Section:
    """Return the Packaging Helpers section."""

    ctx = _ctx(prefix)
    pkgs = package_map(load_packages(ctx))
    return _section(inspect_packaging(ctx, pkgs))


def get_network_section(prefix: Optional[str] = None) -> Section:
    """Return the Network/TLS section."""

    ctx = _ctx(prefix)
    pkgs = package_map(load_packages(ctx))
    return _section(inspect_network(ctx, pkgs))


def get_binaries(prefix: Optional[str] = None, sample_n: int = 20) -> Dict[str, Any]:
    """Return a summary of binaries in the base bin directory.

    The result contains ``{"count": int, "sample": List[str]}``.
    """

    ctx = _ctx(prefix)
    try:
        entries = sorted(os.listdir(ctx.bin_dir))
    except FileNotFoundError:
        entries = []
    return {"count": len(entries), "sample": entries[:sample_n]}


def get_full_report(prefix: Optional[str] = None, sample_n: int = 20) -> Dict[str, Any]:
    """Return a consolidated JSON-serialisable payload.

    This mirrors the CLI output of: `conda-controlplane all --format json`.
    """

    ctx = _ctx(prefix)
    payload = inspect_all(ctx)
    payload["binaries"] = get_binaries(prefix, sample_n=sample_n)
    return payload
