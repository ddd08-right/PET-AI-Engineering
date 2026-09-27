from __future__ import annotations

import binascii
import importlib.util
import struct
import subprocess
import zlib
from pathlib import Path


def _scanner_module():
    script = Path(__file__).parents[1] / "scripts" / "verify_public_repo.py"
    spec = importlib.util.spec_from_file_location("verify_public_repo", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def _png(*extra_chunks: bytes) -> bytes:
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    idat = _chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00"))
    return signature + ihdr + b"".join(extra_chunks) + idat + _chunk(b"IEND", b"")


def test_untracked_blocked_artifact_is_a_scan_candidate(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    safe_file = tmp_path / "README.md"
    safe_file.write_text("synthetic fixture\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    blocked = tmp_path / "SYNTHETIC_FORBIDDEN.nii.gz"
    blocked.write_bytes(b"synthetic test bytes")

    scanner = _scanner_module()
    candidates = scanner.candidate_files(tmp_path)

    assert blocked in candidates
    assert scanner.is_blocked_artifact(blocked)


def test_explicit_ignored_delivery_file_is_scanned(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    (tmp_path / ".gitignore").write_text("*.ckpt\n", encoding="utf-8")
    ignored = tmp_path / "SYNTHETIC_FORBIDDEN.ckpt"
    ignored.write_bytes(b"synthetic test bytes")

    scanner = _scanner_module()
    candidates = scanner.candidate_files(tmp_path, [Path(ignored.name)])

    assert ignored in candidates
    assert scanner.is_blocked_artifact(ignored)


def test_valid_synthetic_png_passes_structural_scan(tmp_path: Path) -> None:
    image = tmp_path / "synthetic.png"
    image.write_bytes(_png())

    assert _scanner_module().scan_png(image) == []


def test_text_disguised_as_png_is_not_skipped(tmp_path: Path) -> None:
    image = tmp_path / "disguised.png"
    image.write_text("synthetic placeholder, not an image", encoding="utf-8")

    assert "invalid PNG signature" in _scanner_module().scan_png(image)


def test_png_text_metadata_is_rejected_without_decompression(tmp_path: Path) -> None:
    image = tmp_path / "metadata.png"
    marker = "API" + "_KEY=synthetic-placeholder"
    image.write_bytes(_png(_chunk(b"zTXt", b"Comment\x00\x00" + zlib.compress(marker.encode()))))

    findings = _scanner_module().scan_png(image)
    assert "PNG text metadata chunk zTXt is not allowed" in findings


def test_markdown_and_svg_still_detect_sensitive_or_active_content(tmp_path: Path) -> None:
    scanner = _scanner_module()
    markdown = tmp_path / "note.md"
    markdown.write_text("TO" + "KEN=synthetic-placeholder", encoding="utf-8")
    svg = tmp_path / "active.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script>'
        '<image href="https://example.invalid/placeholder.png"/></svg>',
        encoding="utf-8",
    )

    assert any("probable secret pattern" in item for item in scanner.scan_text(markdown, tmp_path))
    svg_findings = scanner.scan_svg(svg, tmp_path)
    assert "SVG script element is not allowed" in svg_findings
    assert "SVG external resource reference is not allowed" in svg_findings
