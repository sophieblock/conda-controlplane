from __future__ import annotations

import json
from typing import Dict, Iterable, List

Category = Dict[str, object]
Report = Dict[str, object]


def _fmt_packages(packages: Dict[str, str]) -> List[str]:
    if not packages:
        return ["  (none detected)"]
    width = max(len(n) for n in packages)
    return [f"  {name.ljust(width)}  {packages[name]}" for name in sorted(packages)]


def _fmt_execs(execs: Dict[str, str | None]) -> List[str]:
    if not execs:
        return ["  (none detected)"]
    width = max(len(n) for n in execs)
    lines: List[str] = []
    for name in sorted(execs):
        path = execs[name]
        if path:
            lines.append(f"  {name.ljust(width)}  {path}")
    if not lines:
        return ["  (none detected)"]
    return lines


def format_category_summary(cat: Category, *, verbose: bool = False) -> str:
    lines = [f"=== {cat['title']} ==="]
    lines.append(f"Base prefix: {cat.get('base_prefix')}")
    lines.append(f"Bin dir:     {cat.get('bin_dir')}")
    lines.append("Packages:")
    lines.extend(_fmt_packages(cat.get("packages", {})))
    lines.append("")
    lines.append("Executables:")
    lines.extend(_fmt_execs(cat.get("executables", {})))
    if verbose and cat.get("notes"):
        lines.append("")
        lines.append("Notes:")
        for note in cat["notes"]:
            lines.append(f"  - {note}")
    return "\n".join(lines)


def format_report_summary(report: Report, *, verbose: bool = False) -> str:
    cats = report.get("categories", {})
    parts = []
    for key in ("solvers", "compilers", "packaging", "network"):
        cat = cats.get(key)
        if cat:
            parts.append(format_category_summary(cat, verbose=verbose))
    return "\n\n".join(parts)


def format_category_table(cat: Category, *, verbose: bool = False) -> str:
    lines = [f"[{cat['title']}]"]
    lines.append(f"base: {cat.get('base_prefix')}  bin: {cat.get('bin_dir')}")
    if verbose and cat.get("notes"):
        for note in cat["notes"]:
            lines.append(f"- {note}")
    lines.append("packages")
    lines.extend(_fmt_packages(cat.get("packages", {})))
    lines.append("executables")
    lines.extend(_fmt_execs(cat.get("executables", {})))
    return "\n".join(lines)


def format_report_table(report: Report, *, verbose: bool = False) -> str:
    cats = report.get("categories", {})
    parts = []
    for key in ("solvers", "compilers", "packaging", "network"):
        cat = cats.get(key)
        if cat:
            parts.append(format_category_table(cat, verbose=verbose))
    return "\n\n".join(parts)


def format_json(payload: Dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)
