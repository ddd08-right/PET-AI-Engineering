"""Render an SVG summary from the public FDG20 aggregate JSON only."""

from __future__ import annotations

import argparse
import json
import math
from html import escape
from pathlib import Path
from typing import Any


METHODS = (
    "Entropy",
    "Fold variance",
    "Predicted MTV (size baseline; not UQ)",
    "Pairwise disagreement",
)
EXPECTED_STATUS = {
    "Entropy": "FROZEN_ANALYSIS",
    "Fold variance": "FROZEN_ANALYSIS",
    "Predicted MTV (size baseline; not UQ)": "POST_HOC",
    "Pairwise disagreement": "POST_HOC",
}
COLORS = {
    "FROZEN_ANALYSIS": "#315f86",
    "POST_HOC": "#bf6b32",
    "RANDOM": "#69727a",
    "ORACLE": "#202a33",
}


def validate_payload(payload: dict[str, Any]) -> None:
    """Reject incomplete, incompatible, or non-aggregate input."""
    if payload.get("schema") != "fdg20-pilot-aggregate-summary-v2":
        raise ValueError("unsupported aggregate schema")
    cohort = payload.get("cohort", {})
    if (
        cohort.get("n") != 20
        or cohort.get("reference_foreground_annotations") != 10
        or cohort.get("empty_reference_annotations") != 10
        or cohort.get("training_exposure_excluded") is not False
        or cohort.get("independent_validation") is not False
    ):
        raise ValueError("cohort scope does not match the public FDG20 pilot")
    risk = payload.get("risk", {})
    if (
        risk.get("definition") != "R = FPV + FNV"
        or risk.get("unit") != "mL"
        or risk.get("coverage_80") != "16 retained / 4 referred"
        or risk.get("lower_AURC_is_better") is not True
    ):
        raise ValueError("risk definition or coverage contract is incompatible")

    records = payload.get("methods")
    if not isinstance(records, list) or len(records) != len(METHODS):
        raise ValueError("expected exactly four method aggregate records")
    by_name = {record.get("name"): record for record in records}
    if set(by_name) != set(METHODS):
        raise ValueError("method names do not match the public schema")
    for name, status in EXPECTED_STATUS.items():
        record = by_name[name]
        if record.get("analysis_status") != status:
            raise ValueError(f"unexpected analysis status for {name}")
        for key in (
            "discrete_AURC_mL",
            "mean_retained_R_at_80pct_coverage_mL",
            "cohort_FNV_share_in_4_referrals",
        ):
            value = record.get(key)
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"missing or non-finite {key} for {name}")
        if record["discrete_AURC_mL"] < 0:
            raise ValueError(f"negative AURC for {name}")
        share = record["cohort_FNV_share_in_4_referrals"]
        if not 0 <= share <= 1:
            raise ValueError(f"FNV share outside [0, 1] for {name}")

    references = payload.get("references", {})
    for key in ("random_analytic_expected_AURC_mL", "oracle_AURC_mL"):
        value = references.get(key)
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"missing or invalid reference {key}")
    if "case_id" in payload or "patient_id" in payload or "patients" in payload:
        raise ValueError("case-level fields are not permitted in public aggregate input")


def render_svg(payload: dict[str, Any]) -> str:
    """Create a two-panel aggregate SVG; no patient rows are used."""
    validate_payload(payload)
    by_name = {record["name"]: record for record in payload["methods"]}
    width, height = 1440, 960
    left, plot_x, plot_width = 70, 440, 820
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#202a33}'
        '.title{font-size:30px;font-weight:bold}.sub{font-size:18px}'
        '.label{font-size:19px}.small{font-size:15px}.value{font-size:17px;'
        'font-weight:bold;font-family:monospace}</style>',
        '<text x="70" y="52" class="title">FDG20 aggregate development results</text>',
        '<text x="70" y="84" class="sub">n=20 availability-sampled; '
        '10 reference-foreground / 10 empty-reference; training exposure not excluded</text>',
    ]

    def bar_panel(
        *,
        y0: int,
        title: str,
        names: tuple[str, ...],
        values: dict[str, float],
        upper: float,
        ticks: tuple[float, ...],
        unit: str,
        labels: dict[str, str],
    ) -> None:
        panel_height = 350
        parts.append(
            f'<rect x="55" y="{y0}" width="1330" height="{panel_height}" '
            'fill="#ffffff" stroke="#aeb7c0"/>'
        )
        parts.append(f'<text x="{left}" y="{y0 + 38}" class="title">{escape(title)}</text>')
        axis_y = y0 + 74
        for tick in ticks:
            x = plot_x + plot_width * tick / upper
            tick_label = f"{tick * 100:.0f}%" if not unit else f"{tick:g}"
            parts.extend(
                [
                    f'<line x1="{x:.1f}" y1="{axis_y}" x2="{x:.1f}" '
                    f'y2="{y0 + 300}" stroke="#d9dee3"/>',
                    f'<text x="{x:.1f}" y="{y0 + 324}" class="small" '
                    f'text-anchor="middle">{escape(tick_label)}</text>',
                ]
            )
        row_h = 40
        for index, name in enumerate(names):
            y = axis_y + 15 + index * row_h
            value = values[name]
            # Panel B is a post-hoc derived quantity even for frozen scores.
            color_key = (
                "POST_HOC"
                if title.startswith("B.") and name not in ("Random", "Oracle")
                else EXPECTED_STATUS.get(name, name.upper())
            )
            color = COLORS[color_key]
            if name in ("Random", "Oracle"):
                marker_x = plot_x + plot_width * value / upper
                parts.append(
                    f'<line x1="{marker_x:.1f}" y1="{y - 3}" '
                    f'x2="{marker_x:.1f}" y2="{y + 27}" '
                    f'stroke="{color}" stroke-width="3" stroke-dasharray="6 4"/>'
                )
                parts.append(
                    f'<circle cx="{marker_x:.1f}" cy="{y + 10}" r="5" '
                    f'fill="{color}"/>'
                )
            else:
                bar_width = plot_width * value / upper
                parts.append(
                    f'<rect x="{plot_x}" y="{y}" width="{bar_width:.2f}" '
                    f'height="24" fill="{color}"/>'
                )
            parts.append(
                f'<text x="{left}" y="{y + 19}" class="label">{escape(labels[name])}</text>'
            )
            display = f"{value:.3f} {unit}" if unit else f"{value * 100:.1f}%"
            value_x = min(plot_x + plot_width + 10, plot_x + plot_width * value / upper + 12)
            parts.append(
                f'<text x="{value_x:.1f}" y="{y + 19}" class="value">'
                f'{escape(display)}</text>'
            )
        parts.append(
            f'<text x="{plot_x}" y="{y0 + 344}" class="small">{escape(unit)}</text>'
        )

    aurc_names = (*METHODS, "Random", "Oracle")
    aurc_values = {
        **{name: float(by_name[name]["discrete_AURC_mL"]) for name in METHODS},
        "Random": float(payload["references"]["random_analytic_expected_AURC_mL"]),
        "Oracle": float(payload["references"]["oracle_AURC_mL"]),
    }
    aurc_labels = {
        "Entropy": "Frozen — Entropy",
        "Fold variance": "Frozen — Fold variance",
        "Predicted MTV (size baseline; not UQ)": "Post-hoc — Predicted MTV (size baseline)",
        "Pairwise disagreement": "Post-hoc — Pairwise disagreement",
        "Random": "Random analytic expectation",
        "Oracle": "Reference-informed oracle (not deployable)",
    }
    bar_panel(
        y0=112,
        title="A. Discrete AURC (lower is better)",
        names=aurc_names,
        values=aurc_values,
        upper=70,
        ticks=(0, 20, 40, 60),
        unit="mL",
        labels=aurc_labels,
    )
    fnv_names = METHODS
    fnv_values = {
        name: float(by_name[name]["cohort_FNV_share_in_4_referrals"])
        for name in METHODS
    }
    fnv_labels = {
        "Entropy": "Post-hoc referral share — Entropy",
        "Fold variance": "Post-hoc referral share — Fold variance",
        "Predicted MTV (size baseline; not UQ)": "Post-hoc — Predicted MTV",
        "Pairwise disagreement": "Post-hoc — Pairwise disagreement",
    }
    bar_panel(
        y0=490,
        title="B. Cohort FNV assigned to 4/20 referrals",
        names=fnv_names,
        values=fnv_values,
        upper=1,
        ticks=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
        unit="",
        labels=fnv_labels,
    )
    parts.extend(
        [
            '<text x="70" y="865" class="small">80% coverage = 16 retained / 4 referred. '
            'Referral FNV share is not observed clinical correction or reader time.</text>',
            '<text x="70" y="890" class="small">Fixed predictions; no independent validation or '
            'demonstrated clinical benefit. Entropy/variance are frozen; MTV/Pairwise '
            'comparisons and Panel B are post-hoc.</text>',
            "</svg>",
        ]
    )
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="public aggregate JSON")
    parser.add_argument("--output", type=Path, required=True, help="destination SVG file")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
    svg = render_svg(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Use open(..., newline=...) for Python 3.9-compatible local tooling too.
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(svg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
