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