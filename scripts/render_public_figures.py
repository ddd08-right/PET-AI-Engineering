"""Render three provenance-bound public SVG figures and optional PNG previews.

Uses only the Python standard library for validation and SVG generation. PNG
previews are rendered by a caller-supplied local Chromium-based browser.
"""

from __future__ import annotations

import argparse
import ast
import html
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "docs" / "figures"
SUMMARY = ROOT / "docs" / "development_baseline_40e_summary.json"
METHOD = ROOT / "configs" / "development_baseline_40e" / "method.json"
TRAINER = ROOT / "src" / "pet_ai" / "nnunet_extensions" / "development_baseline_40e.py"
METHOD_README = ROOT / "configs" / "development_baseline_40e" / "README.md"

NAVY = "#23364d"
BLUE = "#527da5"
ORANGE = "#d18852"
TEAL = "#5b8e88"
SLATE = "#718096"
PALE_BLUE = "#edf3f8"
PALE_ORANGE = "#fbf1e9"
PALE_TEAL = "#edf5f3"
INK = "#263545"
MUTED = "#586879"
GRID = "#d9e0e7"
WHITE = "#ffffff"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_start(width: int, height: int, title: str, description: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{esc(title)}</title>',
        f'<desc id="desc">{esc(description)}</desc>',
        '<defs>',
        '<pattern id="control-hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">',
        '<rect width="9" height="9" fill="#f0f1f2"/>',
        '<line x1="0" y1="0" x2="0" y2="9" stroke="#929aa2" stroke-width="3"/>',
        '</pattern>',
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">',
        '<path d="M0,0 L10,5 L0,10 z" fill="#718096"/>',
        '</marker>',
        '</defs>',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{WHITE}"/>',
        '<style>text{font-family:sans-serif;fill:#263545} .title{font-size:34px;font-weight:700} .subtitle{font-size:18px;fill:#586879} .section{font-size:23px;font-weight:700} .body{font-size:18px} .small{font-size:15px;fill:#586879} .label{font-size:16px;font-weight:700} .metric{font-size:16px;font-variant-numeric:tabular-nums}</style>',
    ]


def text(x: float, y: float, content: str, cls: str = "body", anchor: str = "start", fill: str | None = None) -> str:
    fill_attr = f' fill="{fill}"' if fill else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{fill_attr}>{esc(content)}</text>'


def rect(x: float, y: float, width: float, height: float, fill: str, stroke: str = GRID, radius: int = 14, stroke_width: int = 2) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'


def line(x1: float, y1: float, x2: float, y2: float, stroke: str = SLATE, width: int = 2, arrow: bool = False, dash: str | None = None) -> str:
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"{marker}{dash_attr}/>'


def pill(x: float, y: float, label: str, fill: str, color: str = NAVY, width: float | None = None) -> str:
    width = width if width is not None else max(96, len(label) * 9 + 26)
    return "\n".join(
        [
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="34" rx="17" fill="{fill}"/>',
            f'<text x="{x + width / 2:.1f}" y="{y + 23:.1f}" class="label" text-anchor="middle" fill="{color}">{esc(label)}</text>',
        ]
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_and_validate_inputs() -> tuple[dict, dict, str]:
    try:
        data = json.loads(SUMMARY.read_text(encoding="utf-8"))
        method = json.loads(METHOD.read_text(encoding="utf-8"))
        source = TRAINER.read_text(encoding="utf-8")
        method_readme = METHOD_README.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"required public input is unreadable: {error}") from error

    require(data.get("evidence_status") == "DEVELOPMENT_EXPOSED", "unexpected case evidence status")
    scope = data.get("scope", {})
    require(scope.get("development_validation_cases") == 5, "expected five development cases")
    require(scope.get("independent_test") is False, "independent-test boundary is missing or changed")
    require(scope.get("seed") == 20260924 and scope.get("fold") == 0, "seed/fold scope mismatch")

    aggregates = data.get("aggregates", {})
    rows = [aggregates.get("final"), aggregates.get("ema_selected"), aggregates.get("ANALYTIC_EMPTY_PREDICTION_CONTROL")]
    require(all(isinstance(row, dict) for row in rows), "one or more aggregate rows are missing")
    for name, row in zip(("final", "EMA-selected", "analytic control"), rows, strict=True):
        for metric in ("strict_dice", "absolute_volume_error_mL"):
            record = row.get(metric)
            require(isinstance(record, dict), f"{name}: missing {metric}")
            mean = record.get("mean")
            applicable = record.get("applicable_cases")
            total = record.get("total_cases")
            require(isinstance(mean, (int, float)) and math.isfinite(mean), f"{name}: {metric} is non-finite or unknown")
            require(isinstance(applicable, int) and isinstance(total, int), f"{name}: {metric} case counts missing")
            require(total == 5, f"{name}: {metric} total case count mismatch")
        require(row["strict_dice"]["applicable_cases"] == 3, f"{name}: strict Dice denominator mismatch")
        require(row["absolute_volume_error_mL"]["applicable_cases"] == 5, f"{name}: volume-error case count mismatch")
        require(0.0 <= float(row["strict_dice"]["mean"]) <= 1.0, f"{name}: Dice outside [0, 1]")
        require(float(row["absolute_volume_error_mL"]["mean"]) >= 0.0, f"{name}: negative absolute volume error")

    require("not a model" in data["aggregates"]["ANALYTIC_EMPTY_PREDICTION_CONTROL"].get("description", ""), "analytic control not identified")
    require(method.get("evidence_status") == "PARTIAL_RECIPE", "method status mismatch")
    require(method.get("nnunet", {}).get("epochs") == 40, "method epoch value mismatch")
    sampling = method.get("sampling", {})
    slot0 = sampling.get("slot_0", "")
    slot1 = sampling.get("slot_1", "")
    require("no class-1 annotation coordinates" in slot0 and "force_fg=false" in slot0, "slot 0 description conflicts with source")
    probability_match = re.search(r"\b0\.\d+\b", slot1)
    require(probability_match is not None and "uniform positive case" in slot1, "slot 1 description conflicts with source")

    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise ValueError(f"public trainer source does not parse: {error}") from error
    source_checks = (
        'props["class_locations"].get(1, [])',
        "== 0",
        "> 0",
        "np.random.choice(self.negative_identifiers)",
        "np.random.choice(self.positive_identifiers)",
        "np.random.uniform() < self.positive_force_fg_probability",
        "if sample_idx == 0:",
        "if sample_idx == 1:",
        "DevelopmentMidpointDataLoader(",
    )
    normalized = ast.unparse(tree).replace("'", '"')
    for fragment in source_checks:
        require(fragment in normalized, f"public source lacks expected sampler branch: {fragment}")
    require(
        f"positive_force_fg_probability = {probability_match.group()}" in normalized,
        "method probability disagrees with the public source",
    )
    require(normalized.index("== 0") < normalized.index("> 0"), "case-pool definitions are not in expected order")
    require("ignore-label handling can change the" in method_readme, "method documentation omits ignore-label caveat")
    require("get_bbox" in method_readme, "method documentation omits upstream patch-selection dependency")
    require("clinical absence" in method_readme, "method documentation overstates annotation-negative stratum")
    return data, method, normalized


def overview_svg() -> str:
    width, height = 1600, 940
    parts = svg_start(
        width,
        height,
        "What this repository implements and evaluates",
        "Three parallel evidence tracks: a synthetic native PyTorch demo, a five-case single-seed fold-zero nnU-Net development case, and synthetic reliability validation. Independent testing, external validation, and a real reliability study remain incomplete.",
    )
    parts += [text(64, 72, "What this repository implements and evaluates", "title"), text(64, 106, "Three parallel evidence tracks; arrows show only the computation within each track.", "subtitle")]

    cards = [(64, PALE_BLUE, BLUE), (548, PALE_ORANGE, ORANGE), (1032, PALE_TEAL, TEAL)]
    for x, fill, accent in cards:
        parts.append(rect(x, 144, 440, 568, fill, stroke=accent, radius=18, stroke_width=2))
    # A — native PyTorch synthetic teaching path.
    x = 92
    parts += [text(x, 190, "A  Native PyTorch baseline", "section"), pill(x, 210, "SYNTHETIC DEMO", "#dce8f2", width=178)]
    parts += [rect(x, 292, 120, 90, WHITE, stroke="#b7c9d8"), text(x + 60, 332, "Synthetic", "label", "middle"), text(x + 60, 358, "PET/CT tensors", "small", "middle")]
    parts.append(line(x + 123, 337, x + 133, 337, BLUE, arrow=True))
    parts += [rect(x + 136, 292, 120, 90, WHITE, stroke="#b7c9d8"), text(x + 196, 332, "3D U-Net", "label", "middle"), text(x + 196, 358, "native PyTorch", "small", "middle")]
    parts.append(line(x + 259, 337, x + 269, 337, BLUE, arrow=True))
    parts += [rect(x + 272, 292, 124, 90, WHITE, stroke="#b7c9d8"), text(x + 334, 327, "Loss", "small", "middle"), text(x + 334, 350, "backward", "small", "middle"), text(x + 334, 373, "update", "small", "middle")]
    parts += [text(x, 445, "Demonstrates", "label"), text(x, 476, "forward pass → loss → gradient →", "body"), text(x, 504, "optimizer update on synthetic tensors.", "body"), text(x, 574, "No patient images or clinical", "small"), text(x, 598, "performance result in this track.", "small")]

    # B — real development case, separately evaluated.
    x = 576
    parts += [text(x, 190, "B  nnU-Net development case", "section"), pill(x, 210, "DEVELOPMENT_EXPOSED", "#f5e1d2", width=230)]
    parts += [pill(x, 266, "5 DEVELOPMENT CASES", WHITE, width=230), pill(x + 244, 266, "SINGLE SEED / FOLD 0", WHITE, width=194)]
    parts += [rect(x, 342, 126, 90, WHITE, stroke="#d8b89f"), text(x + 63, 378, "PET + CT", "label", "middle"), text(x + 63, 405, "inputs", "small", "middle")]
    parts.append(line(x + 131, 387, x + 159, 387, ORANGE, arrow=True))
    parts += [rect(x + 165, 342, 142, 90, WHITE, stroke="#d8b89f"), text(x + 236, 378, "Upstream", "label", "middle"), text(x + 236, 405, "nnU-Net + sampler", "small", "middle")]
    parts.append(line(x + 312, 387, x + 338, 387, ORANGE, arrow=True))
    parts += [rect(x + 344, 342, 92, 90, WHITE, stroke="#d8b89f"), text(x + 390, 378, "Mask", "label", "middle"), text(x + 390, 405, "metrics", "small", "middle")]
    parts += [pill(x, 466, "PARTIAL_RECIPE", "#f6e8dd", width=182), text(x, 554, "Final and EMA-selected predictions were", "body"), text(x, 582, "evaluated on five development cases.", "body"), text(x, 637, "Not an independent test or external", "small"), text(x, 661, "validation; public aggregates lack per-case", "small"), text(x, 685, "inputs for independent recomputation.", "small")]

    # C — mathematical reliability tools exercised synthetically.
    x = 1060
    parts += [text(x, 190, "C  Reliability toolkit", "section"), pill(x, 210, "SYNTHETIC VALIDATION", "#dcebe7", width=220)]
    parts += [rect(x, 318, 112, 90, WHITE, stroke="#b7cec9"), text(x + 56, 354, "Synthetic", "label", "middle"), text(x + 56, 381, "errors + scores", "small", "middle")]
    parts.append(line(x + 117, 363, x + 141, 363, TEAL, arrow=True))
    parts += [rect(x + 148, 318, 96, 90, WHITE, stroke="#b7cec9"), text(x + 196, 369, "Ranking", "label", "middle")]
    parts.append(line(x + 249, 363, x + 271, 363, TEAL, arrow=True))
    parts += [rect(x + 278, 318, 158, 90, WHITE, stroke="#b7cec9"), text(x + 357, 354, "Risk–coverage", "label", "middle"), text(x + 357, 381, "/ AURC", "small", "middle")]
    parts += [text(x, 475, "Exercises ranking and selective-review", "body"), text(x, 503, "calculations on synthetic arrays.", "body"), text(x, 574, "A real-patient reliability study and", "small"), text(x, 598, "clinical utility evaluation are not complete.", "small")]

    # Bottom-wide evidence limit and legend.
    parts.append(rect(64, 746, 1408, 146, "#f7f8fa", stroke=GRID, radius=16))
    parts += [text(92, 786, "Not completed", "label"), text(92, 816, "Independent test  •  External validation  •  Real-patient reliability study", "body"), text(92, 859, "Evidence labels describe engineering/run status; ENGINEERING_SMOKE or PASS does not establish clinical validity.", "small")]
    parts += [pill(1100, 770, "SYNTHETIC", "#e5edf4", width=128), pill(1244, 770, "DEVELOPMENT", "#f5e5d9", width=150), pill(1410, 770, "PLANNED", "#e8ebef", width=110)]
    parts.append('</svg>')
    return "\n".join(parts)


def metric_svg(data: dict) -> str:
    width, height = 1600, 980
    rows = [
        ("Final", data["aggregates"]["final"], BLUE, "solid"),
        ("EMA-selected", data["aggregates"]["ema_selected"], ORANGE, "solid"),
        ("Analytic empty control", data["aggregates"]["ANALYTIC_EMPTY_PREDICTION_CONTROL"], "url(#control-hatch)", "hatch"),
    ]
    max_error = max(float(row[1]["absolute_volume_error_mL"]["mean"]) for row in rows)
    volume_limit = math.ceil(max_error / 10.0) * 10.0
    parts = svg_start(width, height, "Checkpoint ranking depends on the evaluation endpoint", "Horizontal comparison of non-empty-reference Dice for three cases and mean absolute volume error in millilitres for five cases. The analytic empty-prediction control is not a model output.")
    parts += [text(64, 66, "Checkpoint ranking depends on the evaluation endpoint", "title"), text(64, 100, "Development-exposed case • single seed 20260924 • fold 0 • five development-validation cases", "subtitle")]
    panels = [(64, "Non-empty-reference Dice", "↑ higher", 0.0, 1.0), (824, "Mean absolute volume error (mL)", "↓ lower", 0.0, volume_limit)]
    for x, title, direction, lower, upper in panels:
        parts.append(rect(x, 142, 712, 600, WHITE, stroke=GRID, radius=16))
        parts += [text(x + 30, 188, title, "section"), pill(x + 520, 160, direction, "#f1f4f6", width=145)]
        plot_x, plot_y, plot_w = x + 244, 270, 392
        for tick_i in range(6):
            value = lower + (upper - lower) * tick_i / 5
            tick_x = plot_x + plot_w * tick_i / 5
            parts.append(line(tick_x, plot_y - 12, tick_x, plot_y + 340, GRID, width=1))
            tick_label = f"{value:.1f}" if upper <= 1 else f"{value:.0f}"
            parts.append(text(tick_x, plot_y + 367, tick_label, "small", "middle"))
        for index, (name, row, fill, kind) in enumerate(rows):
            y = plot_y + 30 + index * 112
            key = "strict_dice" if x < 800 else "absolute_volume_error_mL"
            record = row[key]
            value = float(record["mean"])
            n = int(record["applicable_cases"])
            total = int(record["total_cases"])
            normalized = value / upper if upper else 0
            bar_w = max(0.0, min(plot_w, plot_w * normalized))
            parts.append(text(x + 28, y + 9, name, "label"))
            parts.append(text(x + 28, y + 35, f"n={n} of {total}", "small"))
            if kind == "hatch":
                parts.append(f'<rect x="{plot_x:.1f}" y="{y - 2:.1f}" width="{bar_w:.1f}" height="42" rx="7" fill="url(#control-hatch)" stroke="#858e97" stroke-width="1.5"/>')
            else:
                parts.append(f'<rect x="{plot_x:.1f}" y="{y - 2:.1f}" width="{bar_w:.1f}" height="42" rx="7" fill="{fill}"/>')
            label_x = min(plot_x + plot_w - 4, plot_x + bar_w + 12)
            display = f"{value:.4f}" if key == "strict_dice" else f"{value:.2f} mL"
            parts.append(text(label_x, y + 26, display, "metric"))
        parts.append(line(plot_x, plot_y + 350, plot_x + plot_w, plot_y + 350, MUTED, width=1))

    # Consistent semantic legend.
    parts += [rect(64, 770, 1472, 162, "#f7f8fa", stroke=GRID, radius=14), text(92, 812, "Series", "label")]
    parts += [rect(186, 790, 22, 22, BLUE, radius=4), text(220, 807, "Final", "small"), rect(330, 790, 22, 22, ORANGE, radius=4), text(364, 807, "EMA-selected", "small"), rect(516, 790, 22, 22, "url(#control-hatch)", stroke="#858e97", radius=4), text(550, 807, "Analytic empty control (not model inference)", "small")]
    parts += [text(92, 852, "Strict Dice excludes empty-reference cases; volume-error values use all five cases.", "small"), text(92, 878, "The control has lower net-volume error while Dice is 0.0000 (n=3); lower net-volume error alone does not show usable foreground segmentation.", "small")]
    parts += [text(92, 914, "Source: docs/development_baseline_40e_summary.json. Aggregates cannot be independently recomputed without protected per-case values.", "small")]
    parts.append('</svg>')
    return "\n".join(parts)


def sampler_svg(method: dict) -> str:
    width, height = 1600, 1040
    slot0_force = "True" if "force_fg=true" in method["sampling"]["slot_0"].lower() else "False"
    probability = re.search(r"\b0\.\d+\b", method["sampling"]["slot_1"]).group()
    p = svg_start(width, height, "Development midpoint sampler", f"Case selection separates cases with and without class-1 annotation coordinates into fixed batch slots. Slot 1 uses a {probability} foreground-force probability. Patch position is delegated to upstream nnU-Net get_bbox.")
    p += [text(64, 68, "Development midpoint sampler", "title"), text(64, 102, "Case selection and patch selection are separate steps", "subtitle")]
    p.append(rect(64, 150, 1472, 554, WHITE, stroke=GRID, radius=18))
    p += [text(96, 198, "1  Case-level pools and slot assignment", "section"), text(96, 232, "Pool membership comes from preprocessed class_locations for label 1.", "small")]

    p.append(rect(100, 274, 370, 112, PALE_BLUE, stroke=BLUE, radius=14))
    p += [text(124, 314, "No class-1 annotation coordinates", "label"), text(124, 347, "annotation-defined stratum; not clinical absence", "small")]
    p.append(line(472, 330, 630, 330, BLUE, arrow=True))
    p.append(rect(650, 278, 290, 104, "#f4f7fa", stroke=BLUE, radius=14))
    p += [text(795, 319, "Uniform case selection", "label", "middle"), text(795, 349, "slot 0", "small", "middle")]
    p.append(line(944, 330, 1040, 330, BLUE, arrow=True))
    p.append(rect(1062, 278, 396, 104, WHITE, stroke=BLUE, radius=14))
    p += [text(1260, 319, f"force_fg = {slot0_force}", "label", "middle"), text(1260, 349, "always for slot 0", "small", "middle")]

    p.append(rect(100, 416, 370, 112, PALE_TEAL, stroke=TEAL, radius=14))
    p += [text(124, 456, "Has class-1 annotation coordinates", "label"), text(124, 489, "annotation-defined stratum", "small")]
    p.append(line(472, 472, 630, 472, TEAL, arrow=True))
    p.append(rect(650, 420, 290, 104, "#f1f7f5", stroke=TEAL, radius=14))
    p += [text(795, 461, "Uniform case selection", "label", "middle"), text(795, 491, "slot 1", "small", "middle")]
    p.append(line(944, 472, 1040, 472, TEAL, arrow=True))
    p.append(rect(1062, 420, 396, 104, WHITE, stroke=TEAL, radius=14))
    p += [text(1260, 461, "Draw uniform RNG value", "label", "middle"), text(1260, 491, f"compare with {probability} threshold", "small", "middle")]

    # Slot 1 random branch and patch-policy outcomes.
    p.append(line(1260, 526, 1260, 566, ORANGE, arrow=True))
    p.append(rect(1062, 568, 396, 74, PALE_ORANGE, stroke=ORANGE, radius=12))
    p += [text(1260, 599, f"RNG < {probability} → force_fg = True", "label", "middle"), text(1260, 625, "otherwise → force_fg = False", "small", "middle")]

    # Both case slots continue to the same upstream patch-selection routine.
    p.append(rect(64, 736, 1472, 238, "#f7f8fa", stroke=GRID, radius=16))
    p.append(rect(96, 758, 1408, 64, WHITE, stroke=SLATE, radius=12))
    p += [text(800, 785, "2  After case selection, both slots delegate patch location to upstream nnU-Net get_bbox", "label", "middle"), text(800, 810, "The case is already chosen; get_bbox selects a spatial patch within that case.", "small", "middle")]
    p.append('<path d="M1458 330 H1490 V726 H800 V752" fill="none" stroke="#718096" stroke-width="2" marker-end="url(#arrow)"/>')
    p.append('<path d="M1458 605 H1520 V732 H800 V752" fill="none" stroke="#718096" stroke-width="2" marker-end="url(#arrow)"/>')

    # Patch behavior details and evidence caveat.
    p += [text(96, 858, "Upstream patch behavior", "section"), pill(96, 874, "force_fg=True", "#f5e5d9", width=158), text(278, 898, "get_bbox centers a patch on a selected foreground coordinate when one is available.", "body")]
    p += [pill(96, 918, "force_fg=False", "#e8edf2", width=158), text(278, 942, "Without ignore-label mode, random-box branch; ignore-label handling can change it.", "small")]
    p += [text(96, 964, f"{probability} controls slot-1 foreground forcing, not positive-case selection or disease prevalence.", "small")]
    p.append('</svg>')
    return "\n".join(p)


def render_png(edge: Path, svg_path: Path, png_path: Path, width: int, height: int) -> None:
    uri = svg_path.resolve().as_uri()
    with tempfile.TemporaryDirectory(prefix="pet_ai_svg_preview_") as profile:
        command = [
            str(edge),
            "--headless=new",
            "--disable-gpu",
            "--disable-gpu-compositing",
            "--disable-features=VizDisplayCompositor",
            "--hide-scrollbars",
            "--no-first-run",
            "--disable-extensions",
            f"--user-data-dir={profile}",
            f"--window-size={width},{height}",
            f"--screenshot={png_path.resolve()}",
            uri,
        ]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                timeout=60,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise RuntimeError(
                f"SVG preview render failed for {svg_path.name}: {error}"
            ) from error
    if completed.returncode != 0 or not png_path.is_file():
        raise RuntimeError(
            f"SVG preview render failed for {svg_path.name}; exit={completed.returncode}; "
            f"stderr={completed.stderr.strip()}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edge", type=Path, help="Optional local Edge/Chromium executable for PNG previews")
    args = parser.parse_args()
    data, method, _ = load_and_validate_inputs()
    FIGURES.mkdir(parents=True, exist_ok=True)
    renders = [
        ("evidence_overview", overview_svg(), 1600, 940),
        ("development_metric_tradeoff", metric_svg(data), 1600, 980),
        ("midpoint_sampling", sampler_svg(method), 1600, 1040),
    ]
    for name, svg, width, height in renders:
        svg_path = FIGURES / f"{name}.svg"
        svg_path.write_text(svg + "\n", encoding="utf-8", newline="\n")
        print(f"WROTE {svg_path.relative_to(ROOT).as_posix()}")
        if args.edge:
            png_path = FIGURES / f"{name}.png"
            try:
                render_png(args.edge, svg_path, png_path, width, height)
            except RuntimeError as error:
                print(f"ERROR: {error}", file=sys.stderr)
                return 1
            print(f"WROTE {png_path.relative_to(ROOT).as_posix()}")
    print("INPUT_CHECK PASS: aggregate metrics and sampler contracts validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
