from __future__ import annotations

import platform
from typing import Dict, Optional

from .common import select_versions
from .conda_base import CondaContext
from .inspect_solvers import _default_exec_resolver, ExecutableResolver


def inspect_packaging(
    ctx: CondaContext,
    pkg_versions: Dict[str, str],
    exec_resolver: Optional[ExecutableResolver] = None,
) -> Dict[str, object]:
    resolver = exec_resolver or _default_exec_resolver(ctx)

    core = ["pip", "setuptools", "wheel", "build", "twine"]
    modern_pm = ["pipx", "uv", "pdm", "poetry", "hatch"]
    sysname = platform.system()
    wheel_repair = ["delocate"] if sysname == "Darwin" else ["auditwheel", "patchelf"] if sysname == "Linux" else []

    pkg_sel = select_versions(pkg_versions, core + modern_pm + wheel_repair)

    execs = ["pip", "python", "twine", "delocate-wheel", "auditwheel", "patchelf"]
    exec_sel = {e: resolver(e) for e in execs}

    return {
        "title": "Packaging Helpers (Build/Repair/Publish)",
        "base_prefix": ctx.base_prefix,
        "bin_dir": ctx.bin_dir,
        "packages": pkg_sel,
        "executables": exec_sel,
        "notes": [
            "Wheel repair is platform-specific: delocate on macOS, auditwheel/patchelf on Linux.",
            "Covers build/publish helpers in the base control plane.",
        ],
    }
