from __future__ import annotations

import json
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).absolute().parents[1]


def rounded(value: Decimal, places: int) -> str:
    return str(value.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP))


def test_readme_fdg20_table_and_referral_shares_match_public_json():
    payload = json.loads(
        (ROOT / "docs/fdg20_pilot_aggregate_summary.json").read_text(encoding="utf-8"),
        parse_float=Decimal,
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    rows = [line.split("|") for line in readme.splitlines() if line.startswith("| ")]
    metric_rows = [row for row in rows if len(row) == 6]
    metric_rows = [row for row in metric_rows if row[1].strip() != "Score"]
    assert len(metric_rows) == len(payload["methods"])
    for row, method in zip(metric_rows, payload["methods"], strict=True):
        assert row[3].strip() == rounded(method["discrete_AURC_mL"], 2)
        assert row[4].strip() == rounded(method["mean_retained_R_at_80pct_coverage_mL"], 2)
        expected_status = method["metric_analysis_status"]["discrete_AURC_mL"]
        assert ("Frozen" in row[2]) == (expected_status == "FROZEN_ANALYSIS")
        share = Decimal(method["cohort_FNV_share_in_4_referrals"]) * 100
        assert f"{rounded(share, 1)}%" in readme
    for key in ("random_analytic_expected_AURC_mL", "oracle_AURC_mL"):
        assert f"{rounded(payload['references'][key], 2)} mL" in readme
    assert "All four shares are post-hoc" in readme
    assert "not independent validation" in readme


def test_pi_entry_point_local_links_resolve():
    pages = [ROOT / "README.md"] + [
        ROOT / "docs" / name
        for name in ("PI_EVIDENCE_MATRIX.md", "PI_RESEARCH_OVERVIEW.md", "RESEARCH_GATES.md")
    ]
    for page in pages:
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", page.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            relative_path = target.split("#", 1)[0]
            assert (page.parent / relative_path).exists(), (page.name, target)
