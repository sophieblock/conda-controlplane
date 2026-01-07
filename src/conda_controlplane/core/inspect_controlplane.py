from __future__ import annotations

from typing import Callable, Dict, List, Optional

from .common import package_map
from .conda_base import CondaContext, load_packages
from .inspect_compilers import inspect_compilers
from .inspect_network import inspect_network
from .inspect_packaging import inspect_packaging
from .inspect_solvers import inspect_solvers

PackageJson = List[Dict[str, object]]


def inspect_all(
    ctx: CondaContext,
    *,
    packages: Optional[PackageJson] = None,
    exec_resolver: Optional[Callable[[str], Optional[str]]] = None,
) -> Dict[str, object]:
    """Inspect all categories with a shared package snapshot."""
    pkgs = packages or load_packages(ctx)
    pkg_map = package_map(pkgs)

    return {
        "base_prefix": ctx.base_prefix,
        "bin_dir": ctx.bin_dir,
        "categories": {
            "solvers": inspect_solvers(ctx, pkg_map, exec_resolver),
            "compilers": inspect_compilers(ctx, pkg_map, exec_resolver),
            "packaging": inspect_packaging(ctx, pkg_map, exec_resolver),
            "network": inspect_network(ctx, pkg_map, exec_resolver),
        },
    }
