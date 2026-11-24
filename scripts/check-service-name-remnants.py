#!/usr/bin/env python3
"""Find legacy PF service-name aliases in paths and file contents.

The check supports one or more roots. Any matching path or content causes a non-zero
exit status. Historical records can be reviewed separately or excluded by selecting a
narrower root; this tool does not silently bless them.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


INVENTORY_EVIDENCE_DIR = Path(
    "records/IMP-018-active-service-name-normalization/evidence"
)


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


def is_inventory_output(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    evidence_parts = tuple(INVENTORY_EVIDENCE_DIR.parts)
    return (
        tuple(relative.parent.parts[-len(evidence_parts) :]) == evidence_parts
        and relative.name.startswith("remnants-")
        and relative.suffix == ".txt"
    )


def iter_files(root: Path, excluded: set[Path]) -> list[Path]:
    ignored_directories = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        "__pycache__",
        "build",
        "coverage",
        "dist",
        "htmlcov",
        "node_modules",
        "venv",
        ".venv",
    }
    ignored_files = {".DS_Store"}
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.name not in ignored_files
        and not is_inventory_output(path, root)
        and not ignored_directories.intersection(path.relative_to(root).parts)
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
            matches = pattern.findall(component)
            if matches:
                findings.append(
                    Finding("path", relative, text=f"aliases={','.join(matches)}")
                )
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
        except (UnicodeDecodeError, OSError) as exc:
            findings.append(
                Finding(
                    "skipped",
                    relative,
                    text=f"{exc.__class__.__name__}; inventory incomplete for this file",
                )
            )
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            matches = pattern.findall(line)
            if matches:
                findings.append(
                    Finding(
                        "content",
                        relative,
                        line_number,
                        text=f"aliases={','.join(matches)}",
                    )
                )
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find legacy PF service-name aliases in paths and file contents."
    )
    parser.add_argument(
        "roots",
        nargs="*",
        type=Path,
        help="Directories to scan (default: the improvements repository)",
    )
    parser.add_argument(
        "--root",
        dest="option_roots",
        action="append",
        default=[],
        type=Path,
        help="Additional directory to scan; may be repeated",
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
    roots = [*args.roots, *args.option_roots]
    if not roots:
        roots = [Path(__file__).resolve().parents[1]]

    pattern = compile_alias_pattern()
    all_findings: list[Finding] = []
    resolved_roots: list[Path] = []
    multiple_roots = len(roots) > 1
    for root_argument in roots:
        root = root_argument.resolve()
        if not root.is_dir():
            print(f"error: scan root is not a directory: {root}", file=sys.stderr)
            return 2
        resolved_roots.append(root)

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
        root_findings = scan_paths(root, pattern, excluded)
        root_findings.extend(scan_contents(root, pattern, excluded))
        if multiple_roots:
            root_findings = [
                Finding(
                    finding.kind,
                    Path(root.name) / finding.path,
                    finding.line,
                    finding.text,
                )
                for finding in root_findings
            ]
        all_findings.extend(root_findings)

    skipped = [finding for finding in all_findings if finding.kind == "skipped"]
    if skipped:
        for finding in skipped:
            print(f"{finding.kind}: {finding.path}: {finding.text}", file=sys.stderr)
        print(
            f"Skipped {len(skipped)} file(s); inventory is incomplete",
            file=sys.stderr,
        )
        return 2
    if not all_findings:
        scanned = ", ".join(str(root) for root in resolved_roots)
        print(f"No legacy service-name remnants found under {scanned}")
        return 0

    for finding in all_findings:
        location = str(finding.path)
        if finding.line is not None:
            location += f":{finding.line}"
        print(f"{finding.kind}: {location}: {finding.text or ''}")
    print(
        f"Found {len(all_findings)} legacy service-name remnant(s)",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        import traceback

        traceback.print_exc()
        raise SystemExit(2)
