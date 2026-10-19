from __future__ import annotations

import json
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from urllib.parse import unquote

import pytest

ROOT = Path(__file__).absolute().parents[1]
METHOD_LABELS = {
    "Entropy": "Entropy",
    "Fold variance": "Fold probability variance",
    "Predicted MTV (size baseline; not UQ)": "Predicted MTV",
    "Pairwise disagreement": "Pairwise disagreement",
}
STATUS_LABELS = {
    "FROZEN_ANALYSIS": "Frozen primary analysis",
    "POST_HOC": "Post-hoc",
}


def rounded(value: Decimal, places: int) -> str:
    return str(value.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP))


def public_payload() -> dict:
    return json.loads(
        (ROOT / "docs/fdg20_pilot_aggregate_summary.json").read_text(encoding="utf-8"),
        parse_float=Decimal,
    )


def table_by_score(markdown: str, header: str) -> dict[str, list[str]]:
    lines = markdown.splitlines()
    start = lines.index(header) + 2
    rows = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    assert rows, header
    assert len({row[0] for row in rows}) == len(rows), "duplicate score rows"
    return {row[0]: row[1:] for row in rows}


def validate_readme_metrics(readme: str, payload: dict) -> None:
    metrics = table_by_score(
        readme,
        "| Score | Analysis status | Discrete AURC (mL) | Mean retained risk at 80% coverage (mL) |",
    )
    shares = table_by_score(readme, "| Score | Referral-FNV share | Analysis status |")
    expected_names = {METHOD_LABELS[method["name"]] for method in payload["methods"]}
    assert set(metrics) == set(shares) == expected_names
    for method in payload["methods"]:
        name = METHOD_LABELS[method["name"]]
        status, aurc, retained = metrics[name]
        provenance = method["metric_analysis_status"]
        expected_status = STATUS_LABELS[provenance["discrete_AURC_mL"]]
        if name == "Predicted MTV":
            expected_status += " size baseline; not UQ"
        assert status == expected_status, f"{name}: AURC analysis status"
        retained_status = STATUS_LABELS[provenance["mean_retained_R_at_80pct_coverage_mL"]]
        assert status.startswith(retained_status), f"{name}: retained-risk analysis status"
        assert aurc == rounded(method["discrete_AURC_mL"], 2), f"{name}: AURC"
        assert retained == rounded(method["mean_retained_R_at_80pct_coverage_mL"], 2), name
        share, share_status = shares[name]
        expected_share = rounded(Decimal(method["cohort_FNV_share_in_4_referrals"]) * 100, 1)
        assert share == f"{expected_share}%", f"{name}: referral-FNV share"
        assert share_status == STATUS_LABELS[provenance["cohort_FNV_share_in_4_referrals"]], (
            f"{name}: referral-FNV analysis status"
        )
    for key in ("random_analytic_expected_AURC_mL", "oracle_AURC_mL"):
        assert f"{rounded(payload['references'][key], 2)} mL" in readme
    assert "All four shares are post-hoc" in readme
    assert "not independent validation" in readme


def test_readme_fdg20_table_and_referral_shares_match_public_json():
    validate_readme_metrics((ROOT / "README.md").read_text(encoding="utf-8"), public_payload())


def test_validator_rejects_swapped_referral_shares_in_memory():
    payload = public_payload()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    first, second = payload["methods"][:2]
    for method, other in ((first, second), (second, first)):
        name = METHOD_LABELS[method["name"]]
        share = rounded(Decimal(method["cohort_FNV_share_in_4_referrals"]) * 100, 1)
        wrong_share = rounded(Decimal(other["cohort_FNV_share_in_4_referrals"]) * 100, 1)
        original = f"| {name} | {share}% | Post-hoc |"
        assert original in readme
        readme = readme.replace(original, f"| {name} | {wrong_share}% | Post-hoc |")
    with pytest.raises(AssertionError, match="Entropy: referral-FNV share"):
        validate_readme_metrics(readme, payload)


def heading_anchors(markdown: str) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", markdown, re.MULTILINE):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        anchors.add(f"{slug}-{count}" if count else slug)
    return anchors


def test_pi_entry_point_local_links_and_anchors_resolve():
    pages = [ROOT / "README.md"] + [
        ROOT / "docs" / name
        for name in ("PI_EVIDENCE_MATRIX.md", "PI_RESEARCH_OVERVIEW.md", "RESEARCH_GATES.md")
    ]
    for page in pages:
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", page.read_text(encoding="utf-8")):
            if "://" in target:
                continue
            relative_path, _, fragment = unquote(target).partition("#")
            destination = page.parent / relative_path if relative_path else page
            assert destination.exists(), (page.name, target)
            if fragment:
                assert fragment in heading_anchors(destination.read_text(encoding="utf-8")), (
                    page.name, target
                )


def test_evidence_matrix_retains_all_claim_ids():
    matrix = (ROOT / "docs/PI_EVIDENCE_MATRIX.md").read_text(encoding="utf-8")
    actual = re.findall(r"^\| ([EDFPR]\d{2}) \|", matrix, re.MULTILINE)
    expected = [f"{prefix}{i:02}" for prefix, n in (("E", 5), ("D", 2), ("F", 7), ("P", 2), ("R", 3)) for i in range(1, n + 1)]
    assert actual == expected
