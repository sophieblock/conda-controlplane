from __future__ import annotations

from importlib.resources import files
from typing import Union

Pathish = Union[str, "os.PathLike[str]"]  # pragma: no cover


def zsh_shim_path() -> str:
    """Return absolute path to the zsh shim shipped with the package."""
    return str(files(__package__).joinpath("zsh_shim.zsh"))


__all__ = ["zsh_shim_path"]
