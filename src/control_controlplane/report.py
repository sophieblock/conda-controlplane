from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from .conda import CondaContext, conda_list_json


@dataclass(frozen=True)
class Section:
    title: str
    base_prefix: str
    bin_dir: str
    packages: Dict[str, str]  # name -> version
    executables: Dict[str, Optional[str]]  # exe -> path or None
    notes: List[str]


def _pkg_map(pkgs_json: List[dict]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for p in pkgs_json:
        name = p.get("name")
        ver = p.get("version")
        if isinstance(name, str) and isinstance(ver, str):
            out[name] = ver
    return out


def _which_in_bindir(bin_dir: str, exe: str) -> Optional[str]:
    """Prefer <bin_dir>/<exe> to avoid PATH ambiguity. If not present, return None."""
    candidate = os.path.join(bin_dir, exe)
    if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
        return candidate
    # Windows .exe fallback
    if platform.system() == "Windows":
        candidate_exe = candidate + ".exe"
        if os.path.isfile(candidate_exe) and os.access(candidate_exe, os.X_OK):
            return candidate_exe
    return None


def _select_versions(pkg_versions: Dict[str, str], names: Iterable[str]) -> Dict[str, str]:
    return {n: pkg_versions[n] for n in names if n in pkg_versions}


def build_section_solvers(ctx: CondaContext) -> Section:
    pkgs = _pkg_map(conda_list_json(ctx.base_prefix, ctx.conda_exe))

    solver_pkgs = [
        "conda-libmamba-solver",
        "libmamba",
        "libmambapy",
        "mamba",
    ]
    auth_pkgs = [
        "keyring",
        "certifi",
        "ca-certificates",
        "openssl",
        "requests",
        "urllib3",
        "cryptography",
    ]
    platform_pkgs = [
        "archspec",
        "platformdirs",
        "distro",
    ]

    wanted = solver_pkgs + auth_pkgs + platform_pkgs
    pkg_sel = _select_versions(pkgs, wanted)

    execs = ["conda", "mamba", "python", "pip"]
    exec_sel = {e: _which_in_bindir(ctx.bin_dir, e) for e in execs}

    notes = [
        "This section is about 'control-plane' plumbing: solver selection, auth/TLS stack, and platform tagging.",
        "Package presence is taken from conda base via `conda list -p <base> --json`.",
    ]
    return Section(
        title="Solvers, Auth & Platform Detection",
        base_prefix=ctx.base_prefix,
        bin_dir=ctx.bin_dir,
        packages=pkg_sel,
        executables=exec_sel,
        notes=notes,
    )


def build_section_compilers(ctx: CondaContext) -> Section:
    pkgs = _pkg_map(conda_list_json(ctx.base_prefix, ctx.conda_exe))

    compiler_meta = ["compilers", "c-compiler", "cxx-compiler", "fortran-compiler"]
    build_orchestrators = ["conda-build", "boa", "rattler-build", "constructor", "conda-pack"]

    wanted = compiler_meta + build_orchestrators
    pkg_sel = _select_versions(pkgs, wanted)

    execs = ["conda-build", "conda-mambabuild", "cmake", "ninja", "meson"]
    exec_sel = {e: _which_in_bindir(ctx.bin_dir, e) for e in execs}

    notes = [
        "Compiler *metapackages* generally matter for activated target envs (they wire toolchains/activation scripts).",
        "Seeing them in base is optional; many setups keep base minimal.",
    ]
    return Section(
        title="Compiler Metapackages & Build Orchestrators",
        base_prefix=ctx.base_prefix,
        bin_dir=ctx.bin_dir,
        packages=pkg_sel,
        executables=exec_sel,
        notes=notes,
    )


def build_section_packaging(ctx: CondaContext) -> Section:
    pkgs = _pkg_map(conda_list_json(ctx.base_prefix, ctx.conda_exe))

    core = ["pip", "setuptools", "wheel", "build", "twine"]
    modern_pm = ["pipx", "uv", "pdm", "poetry", "hatch"]
    wheel_repair: List[str] = []
    sysname = platform.system()
    if sysname == "Darwin":
        wheel_repair = ["delocate"]
    elif sysname == "Linux":
        wheel_repair = ["auditwheel", "patchelf"]

    wanted = core + modern_pm + wheel_repair
    pkg_sel = _select_versions(pkgs, wanted)

    execs = ["pip", "python", "twine", "delocate-wheel", "auditwheel", "patchelf"]
    exec_sel = {e: _which_in_bindir(ctx.bin_dir, e) for e in execs}

    notes = [
        "Wheel repair is platform-specific: delocate on macOS, auditwheel/patchelf on Linux.",
        "This report is read-only and does not alter PATH or environment variables.",
    ]
    return Section(
        title="Packaging Helpers (Build/Repair/Publish)",
        base_prefix=ctx.base_prefix,
        bin_dir=ctx.bin_dir,
        packages=pkg_sel,
        executables=exec_sel,
        notes=notes,
    )


def build_section_binaries(ctx: CondaContext, *, sample_n: int = 20) -> Tuple[int, List[str]]:
    try:
        entries = sorted(os.listdir(ctx.bin_dir))
    except FileNotFoundError:
        return 0, []
    return len(entries), entries[:sample_n]
