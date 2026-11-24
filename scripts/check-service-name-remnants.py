#!/usr/bin/env python3
"""Find legacy PF service aliases in file paths and UTF-8 text."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EVIDENCE_DIR = Path("records/IMP-018-active-service-name-normalization/evidence")
IGNORED_DIRECTORIES = {
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
    ".venv",
    "venv",
}
IGNORED_FILES = {".DS_Store", ".coverage"}


@dataclass(frozen=True)
class Finding:
    kind: str
    path: Path
    line: int | None = None
    detail: str = ""


def legacy_aliases() -> tuple[str, ...]:
    """Build aliases in fragments so this script does not report itself."""

    return (
        "pf" + "_income",
        "pf" + "-income",
        "pf" + "_payrolls",
        "pf" + "-payrolls",
        "pf" + "_payroll",
        "pf" + "-payroll",
        "pf" + "payrolls",
        "pf" + "payroll",
        "pf" + "_reference",
        "pf" + "-reference",
        "pf" + "_rates",
        "pf" + "-rates",
        "pf" + "_rate",
        "pf" + "-rate",
        "pf" + "rates",
        "pf" + "rate",
    )


def alias_pattern() -> re.Pattern[str]:
    aliases = sorted(legacy_aliases(), key=len, reverse=True)
    return re.compile("|".join(re.escape(alias) for alias in aliases), re.IGNORECASE)


def is_inventory_output(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    evidence_parts = EVIDENCE_DIR.parts
    return (
        tuple(relative.parent.parts[-len(evidence_parts) :]) == evidence_parts
        and relative.name.startswith("remnants-")
        and relative.suffix == ".txt"
    )


def iter_files(root: Path, excluded: set[Path]) -> list[Path]:
    files: list[Path] = []
    for directory, directories, filenames in __import__("os").walk(root):
        directory_path = Path(directory).resolve()
        if any(directory_path == path or path in directory_path.parents for path in excluded):
            directories[:] = []
            continue
        directories[:] = [
            name
            for name in directories
            if name not in IGNORED_DIRECTORIES
            and (directory_path / name).resolve() not in excluded
        ]
        for filename in filenames:
            path = directory_path / filename
            if filename in IGNORED_FILES or is_inventory_output(path, root):
                continue
            if any(path == excluded_path or excluded_path in path.parents for excluded_path in excluded):
                continue
            files.append(path)
    return sorted(files)


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
                    Finding("path", relative, detail=f"aliases={','.join(matches)}")
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
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            findings.append(
                Finding(
                    "skipped",
                    relative,
                    detail=f"{exc.__class__.__name__}; inventory incomplete",
                )
            )
            continue
        for line_number, line in enumerate(lines, start=1):
            matches = pattern.findall(line)
            if matches:
                findings.append(
                    Finding(
                        "content",
                        relative,
                        line_number,
                        f"aliases={','.join(matches)}",
                    )
                )
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find legacy PF aliases in paths and UTF-8 file content."
    )
    parser.add_argument(
        "roots",
        nargs="*",
        type=Path,
        help="Directories to scan; defaults to the improvements repository",
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
        help="Path relative to every root to exclude; may be repeated",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    roots = [*args.roots, *args.option_roots]
    if not roots:
        roots = [Path(__file__).resolve().parents[1]]

    pattern = alias_pattern()
    all_findings: list[Finding] = []
    multiple_roots = len(roots) > 1
    resolved_roots: list[Path] = []

    for root_argument in roots:
        root = root_argument.resolve()
        if not root.is_dir():
            print(f"error: scan root is not a directory: {root}", file=sys.stderr)
            return 2
        resolved_roots.append(root)
        excluded = set()
        for excluded_argument in args.exclude_path:
            excluded_path = (root / excluded_argument).resolve()
            if excluded_path != root and root not in excluded_path.parents:
                print(
                    f"error: excluded path is outside scan root: {excluded_argument}",
                    file=sys.stderr,
                )
                return 2
            excluded.add(excluded_path)

        findings = scan_paths(root, pattern, excluded) + scan_contents(
            root, pattern, excluded
        )
        if multiple_roots:
            findings = [
                Finding(
                    finding.kind,
                    Path(root.name) / finding.path,
                    finding.line,
                    finding.detail,
                )
                for finding in findings
            ]
        all_findings.extend(findings)

    skipped = [finding for finding in all_findings if finding.kind == "skipped"]
    if skipped:
        for finding in skipped:
            print(f"{finding.kind}: {finding.path}: {finding.detail}", file=sys.stderr)
        print(f"Skipped {len(skipped)} file(s); inventory is incomplete", file=sys.stderr)
        return 2

    if not all_findings:
        scanned = ", ".join(str(root) for root in resolved_roots)
        print(f"No legacy service-name remnants found under {scanned}")
        return 0

    for finding in all_findings:
        location = str(finding.path)
        if finding.line is not None:
            location += f":{finding.line}"
        print(f"{finding.kind}: {location}: {finding.detail}")
    print(f"Found {len(all_findings)} legacy service-name remnant(s)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        import traceback

        traceback.print_exc()
        raise SystemExit(2)
