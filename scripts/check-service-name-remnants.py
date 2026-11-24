#!/usr/bin/env python3
"""Find legacy PF service-name aliases in paths and file contents.

The check is intentionally strict: any matching path or content is reported and
causes a non-zero exit status. Historical records can be reviewed separately or
excluded by selecting a narrower root; this tool does not silently bless them.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


def legacy_aliases() -> tuple[str, ...]:
    """Build aliases without placing a complete alias in this source file."""

    return (
        "pf" + "-payroll",
        "pf" + "_payroll",
        "pf" + "payroll",
        "pf" + "-rates",
        "pf" + "_rates",
        "pf" + "rates",
    )


@dataclass(frozen=True)
class Finding:
    kind: str
    path: Path
    line: int | None = None
    text: str | None = None


def iter_files(root: Path, excluded: set[Path]) -> list[Path]:
    ignored = {".git", "__pycache__"}
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not ignored.intersection(path.relative_to(root).parts)
        and not any(
            path == excluded_path or excluded_path in path.parents
            for excluded_path in excluded
        )
    )


def compile_alias_pattern() -> re.Pattern[str]:
    aliases = "|".join(re.escape(alias) for alias in legacy_aliases())
    return re.compile(aliases, re.IGNORECASE)


def scan_paths(
    root: Path, pattern: re.Pattern[str], excluded: set[Path]
) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files(root, excluded):
        relative = path.relative_to(root)
        for component in relative.parts:
            if pattern.search(component):
                findings.append(Finding("path", relative, text=component))
                break
    return findings


def scan_contents(
    root: Path, pattern: re.Pattern[str], excluded: set[Path]
) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files(root, excluded):
        relative = path.relative_to(root)
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                findings.append(Finding("content", relative, line_number, line))
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find legacy PF service-name aliases in paths and file contents."
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Directory to scan (default: the improvements repository)",
    )
    parser.add_argument(
        "--exclude-path",
        action="append",
        default=[],
        type=Path,
        help="Path relative to root to exclude; may be repeated",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"error: scan root is not a directory: {root}", file=sys.stderr)
        return 2

    excluded: set[Path] = set()
    for excluded_path in args.exclude_path:
        candidate = (root / excluded_path).resolve()
        if candidate != root and root not in candidate.parents:
            print(
                f"error: excluded path is outside scan root: {excluded_path}",
                file=sys.stderr,
            )
            return 2
        excluded.add(candidate)

    pattern = compile_alias_pattern()
    findings = scan_paths(root, pattern, excluded) + scan_contents(root, pattern, excluded)
    if not findings:
        print(f"No legacy service-name remnants found under {root}")
        return 0

    for finding in findings:
        location = str(finding.path)
        if finding.line is not None:
            location += f":{finding.line}"
        print(f"{finding.kind}: {location}: {finding.text or ''}")
    print(f"Found {len(findings)} legacy service-name remnant(s)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
