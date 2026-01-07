from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List

from .conda import CondaNotFoundError, CondaContext, conda_context
from .report import (
    build_section_binaries,
    build_section_compilers,
    build_section_packaging,
    build_section_solvers,
    Section,
)


def _section_to_dict(s: Section) -> Dict[str, Any]:
    return {
        "title": s.title,
        "base_prefix": s.base_prefix,
        "bin_dir": s.bin_dir,
        "packages": s.packages,
        "executables": s.executables,
        "notes": s.notes,
    }


def _print_section_text(s: Section) -> None:
    print(f"=== {s.title} ===")
    print(f"Base prefix: {s.base_prefix}")
    print(f"Base bin:    {s.bin_dir}")
    print()

    if s.packages:
        print("Packages:")
        for name in sorted(s.packages):
            print(f"  ✓ {name}: {s.packages[name]}")
    else:
        print("Packages: (none detected)")
    print()

    if s.executables:
        print("Executables (in base bin):")
        any_found = False
        for exe in sorted(s.executables):
            path = s.executables[exe]
            if path:
                any_found = True
                print(f"  ✓ {exe}: {path}")
        if not any_found:
            print("  (none detected)")
    print()

    if s.notes:
        print("Notes:")
        for n in s.notes:
            print(f"  - {n}")
    print()


def _make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="conda-controlplane")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    p.add_argument(
        "--prefix",
        default=None,
        help="Override base prefix (default: detect via conda info --base).",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("report", help="Show all sections.")
    sub.add_parser("solvers", help="Show solver/auth/platform section.")
    sub.add_parser("compilers", help="Show compiler metapackages/build orchestrators section.")
    sub.add_parser("packaging", help="Show packaging helpers section.")
    sub.add_parser("binaries", help="Show base bin inventory (count + sample).")

    return p


def _ctx_with_override(prefix_override: str | None) -> CondaContext:
    ctx = conda_context()
    if prefix_override:
        # keep conda_exe from detected ctx but override prefix/bin
        from .conda import guess_bindir, CondaContext as CC
        return CC(conda_exe=ctx.conda_exe, base_prefix=prefix_override, bin_dir=guess_bindir(prefix_override))
    return ctx


def main(argv: List[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    args = _make_parser().parse_args(argv)

    try:
        ctx = _ctx_with_override(args.prefix)
    except CondaNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    payload: Dict[str, Any] = {"base_prefix": ctx.base_prefix, "bin_dir": ctx.bin_dir, "sections": []}

    if args.cmd in ("report", "solvers"):
        sec = build_section_solvers(ctx)
        payload["sections"].append(_section_to_dict(sec))
        if not args.json:
            _print_section_text(sec)

    if args.cmd in ("report", "compilers"):
        sec = build_section_compilers(ctx)
        payload["sections"].append(_section_to_dict(sec))
        if not args.json:
            _print_section_text(sec)

    if args.cmd in ("report", "packaging"):
        sec = build_section_packaging(ctx)
        payload["sections"].append(_section_to_dict(sec))
        if not args.json:
            _print_section_text(sec)

    if args.cmd in ("report", "binaries"):
        count, sample = build_section_binaries(ctx)
        payload["binaries"] = {"count": count, "sample": sample}
        if not args.json:
            print("=== Binary Inventory ===")
            print(f"Base prefix: {ctx.base_prefix}")
            print(f"Base bin:    {ctx.bin_dir}")
            print(f"Binary count: {count}")
            print()
            print("Sample binaries (first 20):")
            for e in sample:
                print(f"  {e}")
            print()

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
