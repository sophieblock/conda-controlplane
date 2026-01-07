from __future__ import annotations

from typing import Dict, Iterable, List

PackageJson = List[Dict[str, object]]


def package_map(pkgs_json: PackageJson) -> Dict[str, str]:
    """Convert ``conda list`` JSON entries to ``name -> version`` map."""
    out: Dict[str, str] = {}
    for p in pkgs_json:
        name = p.get("name")
        ver = p.get("version")
        if isinstance(name, str) and isinstance(ver, str):
            out[name] = ver
    return out


def select_versions(pkg_versions: Dict[str, str], names: Iterable[str]) -> Dict[str, str]:
    return {n: pkg_versions[n] for n in names if n in pkg_versions}
