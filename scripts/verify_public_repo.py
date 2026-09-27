
from __future__ import annotations

import argparse
import binascii
import re
import struct
import subprocess
import sys
from pathlib import Path

BLOCKED_SUFFIXES = (
    ".dcm",
    ".nii",
    ".nii.gz",
    ".mha",
    ".mhd",
    ".nrrd",
    ".raw",
    ".pt",
    ".pth",
    ".ckpt",
)
SENSITIVE_STRINGS = (
    "Patient" + "Name",
    "Patient" + "Birth" + "Date",
    "Accession" + "Number",
    "Medical" + "Record" + "Number",
)
SECRET_PATTERNS = (
    re.compile(r"(?i)\bTOKEN\s*="),
    re.compile(r"(?i)\bAPI_KEY\s*="),
    re.compile(r"(?i)\bPASSWORD\s*="),
)
MACHINE_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"\b" + "Users" + r"\\"),
    re.compile(r"\b" + "D" + "YL" + r"\b"),
    re.compile("Codex" + "Sandbox" + "Offline"),
)
EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "data",
    "datasets",
    "raw",
    "images",
    "predictions",
    "checkpoints",
    "weights",
    "logs",
}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_TEXT_CHUNKS = {b"tEXt", b"zTXt", b"iTXt"}
MAX_PNG_BYTES = 100 * 1024 * 1024
MAX_PNG_CHUNK_BYTES = 64 * 1024 * 1024


def git_tracked_files(repo_root: Path) -> list[Path] | None:
    try:
        completed = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    files = [repo_root / line.strip() for line in completed.stdout.splitlines() if line.strip()]
    return files or None


def git_untracked_files(repo_root: Path) -> list[Path] | None:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return [repo_root / line for line in completed.stdout.splitlines() if line]


def filesystem_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*"):
        rel_parts = path.relative_to(repo_root).parts
        if any(part in EXCLUDED_DIRS for part in rel_parts):
            continue
        if path.is_file():
            files.append(path)
    return files


def candidate_files(repo_root: Path, explicit_paths: list[Path] | None = None) -> list[Path]:
    tracked = git_tracked_files(repo_root)
    if tracked is None:
        candidates = filesystem_files(repo_root)
    else:
        untracked = git_untracked_files(repo_root)
        candidates = tracked if untracked is None else tracked + untracked
    for path in explicit_paths or []:
        resolved = path if path.is_absolute() else repo_root / path
        try:
            resolved.resolve().relative_to(repo_root)
        except ValueError as error:
            raise ValueError(f"explicit scan path is outside repository: {path}") from error
        candidates.append(resolved)
    return sorted(set(candidates))


def is_blocked_artifact(path: Path) -> bool:
    lowered = path.name.lower()
    return any(lowered.endswith(suffix) for suffix in BLOCKED_SUFFIXES)


def scan_text(path: Path, repo_root: Path) -> list[str]:
    findings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return [f"could not read text: {exc}"]
    rel = path.relative_to(repo_root).as_posix()
    scanner_file = rel == "scripts/verify_public_repo.py"
    if not scanner_file:
        for marker in SENSITIVE_STRINGS:
            if marker in text:
                findings.append(f"sensitive metadata marker found: {marker}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"probable secret pattern found: {pattern.pattern}")
        for pattern in MACHINE_PATH_PATTERNS:
            if pattern.search(text):
                findings.append(f"machine-specific path marker found: {pattern.pattern}")
    return findings


def scan_png(path: Path) -> list[str]:
    """Validate basic PNG structure without decoding image or compressed data."""
    try:
        size = path.stat().st_size
        if size > MAX_PNG_BYTES:
            return [f"PNG exceeds {MAX_PNG_BYTES} byte scan limit"]
        data = path.read_bytes()
    except OSError as exc:
        return [f"could not read PNG: {exc}"]
    if not data.startswith(PNG_SIGNATURE):
        return ["invalid PNG signature"]

    findings: list[str] = []
    offset = len(PNG_SIGNATURE)
    chunk_index = 0
    saw_idat = False
    saw_iend = False
    while offset < len(data):
        if len(data) - offset < 12:
            findings.append("truncated PNG chunk")
            break
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        if length > MAX_PNG_CHUNK_BYTES:
            findings.append(f"PNG chunk exceeds {MAX_PNG_CHUNK_BYTES} byte scan limit")
            break
        end = offset + 12 + length
        if end > len(data):
            findings.append("PNG chunk length exceeds file bounds")
            break
        payload = data[offset + 8 : offset + 8 + length]
        expected_crc = struct.unpack(">I", data[offset + 8 + length : end])[0]
        actual_crc = binascii.crc32(chunk_type + payload) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            findings.append(f"PNG chunk {chunk_type!r} has invalid CRC")
        if chunk_index == 0 and (chunk_type != b"IHDR" or length != 13):
            findings.append("PNG first chunk is not a 13-byte IHDR")
        if chunk_type == b"IHDR" and length == 13:
            width, height = struct.unpack(">II", payload[:8])
            if width == 0 or height == 0:
                findings.append("PNG has zero width or height")
        if chunk_type in PNG_TEXT_CHUNKS:
            findings.append(f"PNG text metadata chunk {chunk_type.decode('ascii')} is not allowed")
        if chunk_type == b"IDAT":
            saw_idat = True
        if chunk_type == b"IEND":
            if length != 0:
                findings.append("PNG IEND chunk is not empty")
            saw_iend = True
            offset = end
            if offset != len(data):
                findings.append("PNG has trailing data after IEND")
            break
        offset = end
        chunk_index += 1
    if not saw_idat:
        findings.append("PNG has no IDAT chunk")
    if not saw_iend:
        findings.append("PNG has no IEND chunk")
    return findings


def scan_svg(path: Path, repo_root: Path) -> list[str]:
    findings = scan_text(path, repo_root)
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError) as exc:
        return findings + [f"could not read SVG as UTF-8 text: {exc}"]
    checks = (
        (re.compile(r"(?is)<\s*script\b"), "SVG script element is not allowed"),
        (re.compile(r"(?is)\bon\w+\s*="), "SVG event-handler attribute is not allowed"),
        (re.compile(r"(?is)\b(?:href|src)\s*=\s*['\"]\s*(?!#)(?:https?:|file:|//)"), "SVG external resource reference is not allowed"),
        (re.compile(r"(?is)\b(?:href|src)\s*=\s*['\"]\s*data:"), "SVG embedded data payload is not allowed"),
        (re.compile(r"(?is)<!DOCTYPE|<!ENTITY"), "SVG DTD/entity declaration is not allowed"),
    )
    for pattern, message in checks:
        if pattern.search(text):
            findings.append(message)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guardrail scan for public repository content. This is not a formal PHI detector."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        type=Path,
        help="Also scan an explicit delivery file, including a normally ignored file.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    errors: list[str] = []
    try:
        candidates = candidate_files(repo_root, args.include)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    for path in candidates:
        if not path.exists():
            continue
        rel = path.relative_to(repo_root)
        if is_blocked_artifact(path):
            errors.append(f"{rel}: blocked medical/model artifact extension")
            continue
        if path.is_file():
            if path.suffix.lower() == ".png":
                findings = scan_png(path)
            elif path.suffix.lower() == ".svg":
                findings = scan_svg(path, repo_root)
            else:
                findings = scan_text(path, repo_root)
            for finding in findings:
                errors.append(f"{rel}: {finding}")

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print("FAIL: public repository guardrail found blocked content", file=sys.stderr)
        return 1
    print("PASS: public repository guardrail found no blocked content")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
