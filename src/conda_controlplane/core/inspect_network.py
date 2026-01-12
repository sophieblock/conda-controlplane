from __future__ import annotations

from typing import Dict, Optional

from .common import select_versions
from .conda_base import CondaContext
from .inspect_solvers import _default_exec_resolver, ExecutableResolver


def inspect_network(
    ctx: CondaContext,
    pkg_versions: Dict[str, str],
    exec_resolver: Optional[ExecutableResolver] = None,
) -> Dict[str, object]:
    resolver = exec_resolver or _default_exec_resolver(ctx)

    tls_pkgs = ["openssl", "certifi", "ca-certificates", "cryptography"]
    http_clients = ["requests", "urllib3", "httpx"]
    downloader = ["libcurl", "curl"]

    pkg_sel = select_versions(pkg_versions, tls_pkgs + http_clients + downloader)
    execs = ["curl"]
    exec_sel = {e: resolver(e) for e in execs}

    return {
        "title": "Network Stack (TLS/HTTP)",
        "base_prefix": ctx.base_prefix,
        "bin_dir": ctx.bin_dir,
        "packages": pkg_sel,
        "executables": exec_sel,
        "notes": [
            "Covers TLS/HTTP dependencies commonly used by conda itself.",
            "Useful when debugging SSL errors or proxy/PKI issues.",
        ],
    }
