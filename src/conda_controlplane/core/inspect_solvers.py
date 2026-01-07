from __future__ import annotations

from typing import Callable, Dict, Optional

from .common import select_versions
from .conda_base import CondaContext

ExecutableResolver = Callable[[str], Optional[str]]


def _default_exec_resolver(ctx: CondaContext) -> ExecutableResolver:
    def _resolver(name: str) -> Optional[str]:
        path = f"{ctx.bin_dir}/{name}"
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
        exe = f"{path}.exe"
        if os.path.isfile(exe) and os.access(exe, os.X_OK):
            return exe
        return None

    import os

    return _resolver


def inspect_solvers(
    ctx: CondaContext,
    pkg_versions: Dict[str, str],
    exec_resolver: Optional[ExecutableResolver] = None,
) -> Dict[str, object]:
    resolver = exec_resolver or _default_exec_resolver(ctx)

    solver_pkgs = ["conda-libmamba-solver", "libmamba", "libmambapy", "mamba"]
    auth_pkgs = ["keyring", "certifi", "ca-certificates", "openssl", "requests", "urllib3", "cryptography"]
    platform_pkgs = ["archspec", "platformdirs", "distro"]

    wanted = solver_pkgs + auth_pkgs + platform_pkgs
    pkg_sel = select_versions(pkg_versions, wanted)

    execs = ["conda", "mamba", "python", "pip"]
    exec_sel = {e: resolver(e) for e in execs}

    return {
        "title": "Solvers, Auth & Platform Detection",
        "base_prefix": ctx.base_prefix,
        "bin_dir": ctx.bin_dir,
        "packages": pkg_sel,
        "executables": exec_sel,
        "notes": [
            "Focuses on solver selection, auth/TLS stack, and platform tagging.",
            "Package presence is taken from conda base via `conda list -p <base> --json`.",
        ],
    }
