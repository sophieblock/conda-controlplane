from __future__ import annotations

from typing import Callable, Dict, Optional

from .common import select_versions
from .conda_base import CondaContext
from .inspect_solvers import _default_exec_resolver, ExecutableResolver


def inspect_compilers(
    ctx: CondaContext,
    pkg_versions: Dict[str, str],
    exec_resolver: Optional[ExecutableResolver] = None,
) -> Dict[str, object]:
    resolver = exec_resolver or _default_exec_resolver(ctx)

    compiler_meta = ["compilers", "c-compiler", "cxx-compiler", "fortran-compiler"]
    build_orchestrators = ["conda-build", "boa", "rattler-build", "constructor", "conda-pack"]
    pkg_sel = select_versions(pkg_versions, compiler_meta + build_orchestrators)

    execs = ["conda-build", "conda-mambabuild", "cmake", "ninja", "meson"]
    exec_sel = {e: resolver(e) for e in execs}

    return {
        "title": "Compiler Metapackages & Build Orchestrators",
        "base_prefix": ctx.base_prefix,
        "bin_dir": ctx.bin_dir,
        "packages": pkg_sel,
        "executables": exec_sel,
        "notes": [
            "Compiler metapackages often live in target envs; seeing them in base is optional.",
            "Build orchestrators help construct artifacts (conda-build, boa/rattler-build, constructor).",
        ],
    }
