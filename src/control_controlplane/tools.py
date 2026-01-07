from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .conda import CondaContext, conda_context
from .report import (
    Section,
    build_section_binaries,
    build_section_compilers,
    build_section_packaging,
    build_section_solvers,
)


def _ctx_with_override(prefix_override: Optional[str] = None) -> CondaContext:
    ctx = conda_context()
    if prefix_override:
        from .conda import CondaContext as CC, guess_bindir

        return CC(
            conda_exe=ctx.conda_exe,
            base_prefix=prefix_override,
            bin_dir=guess_bindir(prefix_override),
        )
    return ctx


def get_solvers_section(prefix: Optional[str] = None) -> Section:
    """Return the Solvers/Auth/Platform section for the given base prefix.

    If *prefix* is None, the conda base prefix is auto-detected.
    """

    ctx = _ctx_with_override(prefix)
    return build_section_solvers(ctx)


def get_compilers_section(prefix: Optional[str] = None) -> Section:
    """Return the Compiler Metapackages & Build Orchestrators section."""

    ctx = _ctx_with_override(prefix)
    return build_section_compilers(ctx)


def get_packaging_section(prefix: Optional[str] = None) -> Section:
    """Return the Packaging Helpers section."""

    ctx = _ctx_with_override(prefix)
    return build_section_packaging(ctx)


def get_binaries(prefix: Optional[str] = None, sample_n: int = 20) -> Dict[str, Any]:
    """Return a summary of binaries in the base bin directory.

    The result contains ``{"count": int, "sample": List[str]}``.
    """

    ctx = _ctx_with_override(prefix)
    count, sample = build_section_binaries(ctx, sample_n=sample_n)
    return {"count": count, "sample": sample}


def get_full_report(prefix: Optional[str] = None, sample_n: int = 20) -> Dict[str, Any]:
    """Return a JSON-serialisable payload matching the CLI's ``--json report`` output."""

    ctx = _ctx_with_override(prefix)

    payload: Dict[str, Any] = {
        "base_prefix": ctx.base_prefix,
        "bin_dir": ctx.bin_dir,
        "sections": [],
    }

    for builder in (build_section_solvers, build_section_compilers, build_section_packaging):
        sec = builder(ctx)
        payload["sections"].append(
            {
                "title": sec.title,
                "base_prefix": sec.base_prefix,
                "bin_dir": sec.bin_dir,
                "packages": sec.packages,
                "executables": sec.executables,
                "notes": sec.notes,
            }
        )

    count, sample = build_section_binaries(ctx, sample_n=sample_n)
    payload["binaries"] = {"count": count, "sample": sample}

    return payload
