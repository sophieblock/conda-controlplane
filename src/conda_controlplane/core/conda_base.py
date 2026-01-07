from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


class CondaNotFoundError(RuntimeError):
    """Raised when a conda executable cannot be located."""


@dataclass(frozen=True)
class CondaContext:
    conda_exe: str
    base_prefix: str
    bin_dir: str


Runner = Callable[[List[str], int], subprocess.CompletedProcess]


def _run(cmd: List[str], timeout_s: int = 20) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout_s,
    )


def pick_conda_exe(env: Optional[Dict[str, str]] = None, which: Callable[[str], Optional[str]] = shutil.which) -> str:
    """Pick a conda executable, preferring CONDA_EXE and falling back to PATH."""
    env = env or os.environ
    conda_exe = env.get("CONDA_EXE")
    if conda_exe and os.path.isfile(conda_exe) and os.access(conda_exe, os.X_OK):
        return conda_exe

    conda_on_path = which("conda")
    if conda_on_path:
        return conda_on_path

    raise CondaNotFoundError("conda executable not found (neither CONDA_EXE nor PATH)")


def guess_bindir(prefix: str) -> str:
    """Return the most likely bin directory for a prefix."""
    bin_dir = os.path.join(prefix, "bin")
    if os.path.isdir(bin_dir):
        return bin_dir
    scripts = os.path.join(prefix, "Scripts")
    if os.path.isdir(scripts):
        return scripts
    return bin_dir


def find_base_prefix(conda_exe: Optional[str] = None, runner: Runner = _run) -> str:
    """Find the conda base prefix using `conda info --base`."""
    conda_exe = conda_exe or pick_conda_exe()
    proc = runner([conda_exe, "info", "--base"], 20)
    base = proc.stdout.strip()
    if proc.returncode == 0 and base and os.path.isdir(base):
        return base
    raise RuntimeError(
        f"Failed to determine base prefix via `{conda_exe} info --base`.\n"
        f"stdout: {proc.stdout}\n"
        f"stderr: {proc.stderr}"
    )


def conda_list_json(prefix: str, conda_exe: Optional[str] = None, runner: Runner = _run) -> List[Dict[str, Any]]:
    """Return package list for prefix as JSON via `conda list -p <prefix> --json`."""
    conda_exe = conda_exe or pick_conda_exe()
    proc = runner([conda_exe, "list", "-p", prefix, "--json"], 40)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Failed `conda list -p {prefix} --json`.\nstdout: {proc.stdout}\nstderr: {proc.stderr}"
        )
    return json.loads(proc.stdout or "[]")


def load_packages(ctx: CondaContext, runner: Runner = _run) -> List[Dict[str, Any]]:
    """Load package metadata for the base environment."""
    return conda_list_json(ctx.base_prefix, ctx.conda_exe, runner)


def make_conda_context(
    base_prefix: Optional[str] = None,
    conda_exe: Optional[str] = None,
    runner: Runner = _run,
) -> CondaContext:
    """Build a CondaContext, discovering base prefix when not provided."""
    conda_exe = conda_exe or pick_conda_exe()
    base_prefix = base_prefix or find_base_prefix(conda_exe, runner)
    bin_dir = guess_bindir(base_prefix)
    return CondaContext(conda_exe=conda_exe, base_prefix=base_prefix, bin_dir=bin_dir)
