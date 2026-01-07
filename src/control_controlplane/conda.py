from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class CondaNotFoundError(RuntimeError):
    pass


@dataclass(frozen=True)
class CondaContext:
    conda_exe: str
    base_prefix: str
    bin_dir: str


def _pick_conda_exe() -> str:
    """
    Prefer CONDA_EXE when present (set by conda), else fall back to `conda` on PATH.
    """
    conda_exe = os.environ.get("CONDA_EXE")
    if conda_exe and os.path.isfile(conda_exe) and os.access(conda_exe, os.X_OK):
        return conda_exe

    conda_on_path = shutil.which("conda")
    if conda_on_path:
        return conda_on_path

    raise CondaNotFoundError("conda executable not found (neither CONDA_EXE nor PATH)")


def _run(cmd: List[str], *, timeout_s: int = 20) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout_s,
    )


def find_base_prefix(conda_exe: Optional[str] = None) -> str:
    """
    Find conda base prefix using `conda info --base`.
    """
    conda_exe = conda_exe or _pick_conda_exe()
    proc = _run([conda_exe, "info", "--base"])
    base = proc.stdout.strip()
    if proc.returncode == 0 and base and os.path.isdir(base):
        return base
    raise RuntimeError(
        f"Failed to determine base prefix via `{conda_exe} info --base`.\n"
        f"stdout: {proc.stdout}\n"
        f"stderr: {proc.stderr}"
    )


def guess_bindir(prefix: str) -> str:
    """
    Base bin dir: POSIX uses <prefix>/bin; Windows often uses <prefix>/Scripts.
    """
    bin_dir = os.path.join(prefix, "bin")
    if os.path.isdir(bin_dir):
        return bin_dir
    scripts = os.path.join(prefix, "Scripts")
    if os.path.isdir(scripts):
        return scripts
    return bin_dir


def conda_list_json(prefix: str, conda_exe: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get package list as JSON using `conda list -p <prefix> --json`.
    """
    conda_exe = conda_exe or _pick_conda_exe()
    proc = _run([conda_exe, "list", "-p", prefix, "--json"], timeout_s=40)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Failed `conda list -p {prefix} --json`.\nstdout: {proc.stdout}\nstderr: {proc.stderr}"
        )
    return json.loads(proc.stdout)


def conda_context() -> CondaContext:
    conda_exe = _pick_conda_exe()
    base_prefix = find_base_prefix(conda_exe)
    bin_dir = guess_bindir(base_prefix)
    return CondaContext(conda_exe=conda_exe, base_prefix=base_prefix, bin_dir=bin_dir)
(conda info --base: 
Conda Documentation
; conda list [-n | -p PATH]: 
Conda Documentation
)

src/conda_controlplane/report.py
python
Copy code
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
    packages: Dict[str, str]          # name -> version
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
    """
    Prefer <bin_dir>/<exe> to avoid PATH ambiguity. If not present, return None.
    """
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
    wheel_repair = []
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
