from __future__ import annotations

import importlib
from typing import Any, List, Optional

# NOTE: This module is intentionally import-safe when `conda` is not installed.
# Conda will import it when discovering plugins via entry points.
try:
    _conda_plugins: Any = importlib.import_module("conda.plugins")
    _conda_types: Any = importlib.import_module("conda.plugins.types")
    _hookimpl = _conda_plugins.hookimpl
except ModuleNotFoundError:  # pragma: no cover
    _conda_plugins = None
    _conda_types = None

    def _hookimpl(func):  # type: ignore[no-redef]
        return func


def controlplane_action(argv: Optional[List[str]] = None) -> int:
    """Entry point for `conda controlplane`.

    Conda passes a list of argv-style arguments for the subcommand.
    """

    from conda_controlplane.cli.main import main

    return main(argv, prog="conda controlplane")


@_hookimpl
def conda_subcommands():
    """Register the `conda controlplane` subcommand."""

    if _conda_types is None:  # pragma: no cover
        return

    yield _conda_types.CondaSubcommand(
        name="controlplane",
        action=controlplane_action,
        summary="Inspect conda base control-plane tooling",
    )
