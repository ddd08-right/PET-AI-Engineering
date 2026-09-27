"""Render three provenance-bound public SVG figures and optional PNG previews.

SVG generation and input validation use only the Python standard library. PNG
previews require a caller-supplied local Chromium-based browser.
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

BLUE = "#3b6f9c"
ORANGE = "#c86f32"
TEAL = "#377f78"
SLATE = "#67717b"
INK = "#20252b"
MUTED = "#4f5963"
GRID = "#d6dbe0"
WHITE = "#ffffff"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_start(width: int, height: int, title: str, description: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{esc(title)}</title>',
        f'<desc id="desc">{esc(description)}</desc>',
        "<defs>",
        '<pattern id="control-hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">',
        '<rect width="8" height="8" fill="#f4f4f4"/>',
        '<line x1="0" y1="0" x2="0" y2="8" stroke="#69727a" stroke-width="2"/>',
        "</pattern>",
        '<marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">',
        f'<path d="M0,0 L8,4 L0,8 z" fill="{SLATE}"/>',
        "</marker>",
        "</defs>",
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{WHITE}"/>',
        f'<style>text{{font-family:Arial,Helvetica,sans-serif;fill:{INK}}} .title{{font-size:26px;font-weight:700}} .subtitle{{font-size:18px;fill:{MUTED}}} .section{{font-size:22px;font-weight:700}} .body{{font-size:19px}} .small{{font-size:17px;fill:{MUTED}}} .label{{font-size:18px;font-weight:700}} .metric{{font-size:18px;font-weight:700;font-variant-numeric:tabular-nums}}</style>',
    ]


def text(
    x: float,
    y: float,
    content: str,
    cls: str = "body",
    anchor: str = "start",
    fill: str | None = None,
) -> str:
    fill_attr = f' fill="{fill}"' if fill else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{fill_attr}>{esc(content)}</text>'


def rect(
    x: float,
    y: float,
    width: float,
    height: float,
    fill: str = WHITE,
    stroke: str = GRID,
    stroke_width: int = 1,
) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    stroke: str = SLATE,
    width: int = 2,
    arrow: bool = False,
) -> str:
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"{marker}/>'


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
    rows = [
        aggregates.get("final"),
        aggregates.get("ema_selected"),
        aggregates.get("ANALYTIC_EMPTY_PREDICTION_CONTROL"),
    ]
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

    control = aggregates["ANALYTIC_EMPTY_PREDICTION_CONTROL"]
    require("not a model" in control.get("description", ""), "analytic control not identified")
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
    normalized = ast.unparse(tree).replace("'", '"')
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
    width, height = 1400, 600
    parts = svg_start(
        width,
        height,
        "Three evidence tracks",
        "Separate PyTorch training demonstration, nnU-Net development analysis, and risk-coverage utility tracks; not a completed patient-level pipeline.",
    )
    parts += [
        text(50, 46, "Three evidence tracks", "title"),
        text(50, 76, "Inputs → computation → outputs; tracks are evaluated separately.", "subtitle"),
    ]
    panels = [
        (50, "A", "PyTorch training demonstration", BLUE),
        (485, "B", "nnU-Net development analysis", ORANGE),
        (920, "C", "Risk–coverage utilities", TEAL),
    ]
    for x, letter, title, accent in panels:
        parts += [
            rect(x, 110, 390, 400, stroke="#aeb7c0"),
            text(x + 22, 148, letter, "section", fill=accent),
            text(x + 58, 148, title, "label"),
        ]

    def track(x: float, labels: tuple[tuple[str, str], ...], color: str) -> None:
        box_y, box_w, box_h = 220, 104, 92
        positions = (x + 18, x + 143, x + 268)
        for index, ((top, bottom), box_x) in enumerate(zip(labels, positions, strict=True)):
            parts.extend(
                [
                    rect(box_x, box_y, box_w, box_h, stroke=color),
                    text(box_x + box_w / 2, box_y + 39, top, "label", "middle"),
                    text(box_x + box_w / 2, box_y + 65, bottom, "small", "middle"),
                ]
            )
            if index < 2:
                parts.append(line(box_x + box_w + 4, box_y + 46, positions[index + 1] - 6, box_y + 46, color, arrow=True))

    track(50, (("Synthetic", "PET/CT input"), ("Forward", "loss"), ("Backward", "update")), BLUE)
    parts += [text(70, 355, "Synthetic tests", "label"), text(70, 385, "Output: logits, loss, gradients, update", "small")]
    track(485, (("PET + CT", "5 cases"), ("Upstream", "nnU-Net"), ("Metrics", "Final / EMA")), ORANGE)
    parts += [
        text(505, 355, "Single seed / fold 0", "label"),
        text(505, 385, "Public sampler adaptation; PARTIAL_RECIPE", "small"),
        text(505, 414, "Development analysis; not an independent test", "small"),
    ]
    track(920, (("Synthetic", "errors, scores"), ("Risk rank", "expected ties"), ("Output", "risk–coverage")), TEAL)
    parts += [text(940, 355, "Synthetic tests", "label"), text(940, 385, "Real-patient reliability study incomplete", "small")]
    parts += [
        line(50, 550, 1350, 550, GRID, width=1),
        text(50, 580, "Shared QC and provenance do not make these tracks one end-to-end patient study.", "small"),
        "</svg>",
    ]
    return "\n".join(parts)


def metric_svg(data: dict) -> str:
    width, height = 1400, 620
    rows = [
        ("Final", data["aggregates"]["final"], BLUE, "solid"),
        ("EMA-selected checkpoint", data["aggregates"]["ema_selected"], ORANGE, "solid"),
        ("Empty-mask control (analytic)", data["aggregates"]["ANALYTIC_EMPTY_PREDICTION_CONTROL"], "url(#control-hatch)", "hatch"),
    ]
    parts = svg_start(
        width,
        height,
        "Development checkpoint comparison",
        "Mean Dice for three non-empty references and volume MAE in millilitres for all five cases. The empty-mask control is analytic, not model inference.",
    )
    parts += [
        text(50, 46, "Development checkpoint comparison", "title"),
        text(50, 76, "Five-case, single-seed/fold post-hoc development analysis", "subtitle"),
    ]
    panels = [
        (50, "A", "Mean Dice, non-empty references", "n=3", "strict_dice", 1.0, [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]),
        (720, "B", "Volume MAE (mL)", "all cases, n=5", "absolute_volume_error_mL", 80.0, [0, 20, 40, 60, 80]),
    ]
    for x, letter, title, denominator, key, upper, ticks in panels:
        accent = BLUE if letter == "A" else ORANGE
        parts += [
            rect(x, 105, 630, 430, stroke="#aeb7c0"),
            text(x + 22, 142, letter, "section", fill=accent),
            text(x + 58, 142, title, "label"),
            text(x + 58, 171, denominator, "small"),
        ]
        plot_x, plot_y, plot_w = x + 235, 218, 330
        for value in ticks:
            tick_x = plot_x + plot_w * float(value) / upper
            parts.append(line(tick_x, plot_y - 20, tick_x, plot_y + 240, GRID, width=1))
            tick_label = f"{value:.1f}" if upper == 1.0 else f"{value:.0f}"
            parts.append(text(tick_x, plot_y + 270, tick_label, "small", "middle"))
        for index, (name, row, fill, kind) in enumerate(rows):
            y = plot_y + index * 92
            value = float(row[key]["mean"])
            bar_w = 0.0 if value == 0.0 else min(plot_w, plot_w * value / upper)
            if name == "Empty-mask control (analytic)":
                parts.append(text(x + 22, y + 15, "Empty-mask control", "small"))
                parts.append(text(x + 22, y + 37, "(analytic)", "small"))
            else:
                parts.append(text(x + 22, y + 26, name, "small"))
            if kind == "hatch":
                parts.append(f'<rect x="{plot_x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="34" fill="url(#control-hatch)" stroke="#69727a" stroke-width="1.5"/>')
            else:
                parts.append(f'<rect x="{plot_x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="34" fill="{fill}"/>')
            label_x = min(plot_x + plot_w - 4, plot_x + bar_w + 12)
            display = f"{value:.4f}" if key == "strict_dice" else f"{value:.2f} mL"
            parts.append(text(label_x, y + 25, display, "metric"))
        parts.append(line(plot_x, plot_y + 240, plot_x + plot_w, plot_y + 240, SLATE, width=1))
    parts += [
        text(50, 580, "Values: frozen public aggregates; bars start at zero. No uncertainty intervals are available.", "small"),
        "</svg>",
    ]
    return "\n".join(parts)


def sampler_svg(method: dict) -> str:
    width, height = 1400, 620
    slot0_force = "True" if "force_fg=true" in method["sampling"]["slot_0"].lower() else "False"
    probability = re.search(r"\b0\.\d+\b", method["sampling"]["slot_1"]).group()
    parts = svg_start(
        width,
        height,
        "Development sampler",
        f"Cases are sampled uniformly within annotation-coordinate pools and assigned to fixed slots. Slot 1 uses u uniform on zero to one and force foreground when u is below {probability}. Both slots delegate patch selection to upstream nnU-Net get_bbox.",
    )
    parts += [
        text(50, 46, "Development sampler", "title"),
        text(50, 76, "Case selection is separate from upstream patch selection.", "subtitle"),
        text(60, 120, "A", "section", fill=BLUE),
        text(96, 120, "Case pool", "label"),
        text(440, 120, "B", "section", fill=ORANGE),
        text(476, 120, "Uniform draw + fixed slot", "label"),
        text(1110, 120, "C", "section", fill=TEAL),
        text(1146, 120, "Patch selection", "label"),
    ]
    rows = [
        (180, "No class-1 coordinates", "annotation-defined pool", "slot 0", f"force_fg = {slot0_force}", BLUE),
        (380, "Has class-1 coordinates", "annotation-defined pool", "slot 1", f"u ~ Uniform(0,1); force_fg = (u < {probability})", ORANGE),
    ]
    for y, pool, detail, slot, rule, color in rows:
        parts += [
            rect(60, y, 300, 100, stroke=color),
            text(210, y + 42, pool, "label", "middle"),
            text(210, y + 70, detail, "small", "middle"),
            line(370, y + 50, 430, y + 50, color, arrow=True),
            rect(440, y, 220, 100, stroke=color),
            text(550, y + 42, "Uniform case draw", "label", "middle"),
            text(550, y + 70, "within pool", "small", "middle"),
            line(670, y + 50, 730, y + 50, color, arrow=True),
            rect(740, y, 310, 100, stroke=color),
            text(895, y + 36, slot, "label", "middle"),
            text(895, y + 68, rule, "small", "middle"),
        ]
    parts += [
        rect(1120, 270, 230, 120, stroke=TEAL),
        text(1235, 317, "Upstream nnU-Net", "label", "middle"),
        text(1235, 349, "get_bbox", "section", "middle"),
        text(1235, 375, "patch selection", "small", "middle"),
        '<path d="M1050 230 H1085 V310 H1110" fill="none" stroke="#3b6f9c" stroke-width="2" marker-end="url(#arrow)"/>',
        '<path d="M1050 430 H1085 V350 H1110" fill="none" stroke="#c86f32" stroke-width="2" marker-end="url(#arrow)"/>',
        line(50, 530, 1350, 530, GRID, width=1),
        text(50, 565, "Pool membership uses class-1 annotation coordinates; no coordinates does not mean clinical absence.", "small"),
        text(50, 592, "Ignore-label settings can change upstream get_bbox behavior.", "small"),
        "</svg>",
    ]
    return "\n".join(parts)


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
            raise RuntimeError(f"SVG preview render failed for {svg_path.name}: {error}") from error
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
        ("evidence_overview", overview_svg(), 1400, 600),
        ("development_metric_tradeoff", metric_svg(data), 1400, 620),
        ("midpoint_sampling", sampler_svg(method), 1400, 620),
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
