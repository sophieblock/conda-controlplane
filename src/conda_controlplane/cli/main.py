from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Optional

from conda_controlplane.core.common import package_map
from conda_controlplane.core.conda_base import CondaNotFoundError, load_packages, make_conda_context
from conda_controlplane.core.formatting import (
    format_json,
    format_report_summary,
    format_report_table,
)
from conda_controlplane.core.inspect_compilers import inspect_compilers
from conda_controlplane.core.inspect_controlplane import inspect_all
from conda_controlplane.core.inspect_network import inspect_network
from conda_controlplane.core.inspect_packaging import inspect_packaging
from conda_controlplane.core.inspect_solvers import inspect_solvers


def _build_parser(*, prog: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--base-prefix", help="Override base prefix (default: conda info --base)")
    parser.add_argument(
        "--format",
        choices=["json", "table", "summary"],
        default="summary",
        help="Output format",
    )
    parser.add_argument("--verbose", action="store_true", help="Include notes in textual output.")

    sub = parser.add_subparsers(dest="command", required=True)
    for cmd in ("solvers", "compilers", "packaging", "network", "all"):
        sub.add_parser(cmd, help=f"Inspect {cmd} control-plane category.")
    return parser


def _payload_for_category(name: str, category: Dict[str, object], ctx) -> Dict[str, object]:
    return {
        "base_prefix": ctx.base_prefix,
        "bin_dir": ctx.bin_dir,
        "categories": {name: category},
    }


def main(argv: Optional[List[str]] = None, *, prog: Optional[str] = None) -> int:
    prog = prog or "conda-controlplane"
    args = _build_parser(prog=prog).parse_args(argv)

    try:
        ctx = make_conda_context(base_prefix=args.base_prefix)
    except CondaNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.command == "all":
        payload = inspect_all(ctx)
    else:
        pkgs = package_map(load_packages(ctx))
        if args.command == "solvers":
            cat = inspect_solvers(ctx, pkgs)
        elif args.command == "compilers":
            cat = inspect_compilers(ctx, pkgs)
        elif args.command == "packaging":
            cat = inspect_packaging(ctx, pkgs)
        elif args.command == "network":
            cat = inspect_network(ctx, pkgs)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 2
        payload = _payload_for_category(args.command, cat, ctx)

    if args.format == "json":
        print(format_json(payload))
    elif args.format == "table":
        print(format_report_table(payload, verbose=args.verbose))
    else:
        print(format_report_summary(payload, verbose=args.verbose))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
