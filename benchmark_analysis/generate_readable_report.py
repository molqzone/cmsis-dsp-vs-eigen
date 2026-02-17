from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Iterable
from typing import Sequence

try:
    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    import numpy as np
    import pandas as pd
    _IMPORT_ERROR: Exception | None = None
except ImportError as exc:  # pragma: no cover - runtime dependency
    mcolors = None  # type: ignore[assignment]
    plt = None  # type: ignore[assignment]
    Patch = object  # type: ignore[assignment]
    np = None  # type: ignore[assignment]
    pd = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc

from full_matrix_common import BuildProfile
from full_matrix_common import EXPECTED_INV_SIZES
from full_matrix_common import EXPECTED_MUL_SIZES
from full_matrix_common import SampleRecord
from full_matrix_common import default_profiles
from full_matrix_common import detect_crossover
from full_matrix_common import group_profiles_by_phenomenon
from full_matrix_common import parse_profile_names
from full_matrix_common import parse_run_lines
from full_matrix_common import validate_records


@dataclass(frozen=True)
class ReportPaths:
    """Groups report generation paths.

    Args:
        repo_dir: Repository root directory.
        input_root: Matrix input root.
        output_md: Markdown output path.
        output_dir: Plot/CSV output directory.
    """

    repo_dir: Path
    input_root: Path
    output_md: Path
    output_dir: Path


def parse_args() -> argparse.Namespace:
    """Parses CLI args for readable report generation."""

    parser = argparse.ArgumentParser(
        description="Generate a readable full-matrix benchmark report."
    )
    parser.add_argument("--input-root", default="build/bench_matrix")
    parser.add_argument("--output-md", default="report_readable.md")
    parser.add_argument("--output-dir", default="benchmark_analysis/output/readable")
    parser.add_argument("--profiles", default="C1,C2,C3,C4,C5,C6,C7,C8,C9,C10")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--group-tolerance", type=float, default=0.02)
    return parser.parse_args()


def build_paths(args: argparse.Namespace) -> ReportPaths:
    """Builds absolute report paths from args."""

    repo_dir = Path(__file__).resolve().parents[1]
    input_root = Path(args.input_root)
    if not input_root.is_absolute():
        input_root = repo_dir / input_root
    output_md = Path(args.output_md)
    if not output_md.is_absolute():
        output_md = repo_dir / output_md
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = repo_dir / output_dir
    return ReportPaths(
        repo_dir=repo_dir,
        input_root=input_root,
        output_md=output_md,
        output_dir=output_dir,
    )


def load_profile_meta(profile_dir: Path) -> dict[str, object]:
    """Loads one profile metadata JSON if present."""

    meta_file = profile_dir / "profile_meta.json"
    if not meta_file.is_file():
        return {}
    return json.loads(meta_file.read_text(encoding="utf-8"))


def records_to_dicts(
    profile: str,
    run_id: str,
    records: Iterable[SampleRecord],
) -> list[dict[str, object]]:
    """Converts SampleRecord sequence into DataFrame rows."""

    rows: list[dict[str, object]] = []
    for rec in records:
        rows.append(
            {
                "profile": profile,
                "run_id": run_id,
                "op": rec.op,
                "n": rec.n,
                "repeat": rec.repeat,
                "warmup": rec.warmup,
                "eigen_avg_cycles": rec.eigen_avg_cycles,
                "cmsis_avg_cycles": rec.cmsis_avg_cycles,
                "cmsis_over_eigen": rec.cmsis_over_eigen,
                "eigen_over_cmsis": (
                    (1.0 / rec.cmsis_over_eigen)
                    if rec.cmsis_over_eigen > 0
                    else float("inf")
                ),
                "error_l2": rec.error_l2,
                "valid": rec.valid,
                "invalid": rec.invalid,
                "build_mode": rec.build_mode,
            }
        )
    return rows


def load_profile_runs(profile: str, profile_dir: Path, strict: bool) -> pd.DataFrame:
    """Loads all run CSV files for one profile.

    Args:
        profile: Profile name (for example `C1`).
        profile_dir: Directory containing `samples_release/`.
        strict: Whether missing/incomplete data should fail fast.

    Returns:
        DataFrame with parsed benchmark rows.
    """

    samples_dir = profile_dir / "samples_release"
    if not samples_dir.is_dir():
        if strict:
            raise FileNotFoundError(f"samples_release missing for {profile}: {samples_dir}")
        return pd.DataFrame()

    rows: list[dict[str, object]] = []
    run_files = sorted(samples_dir.glob("run_*.csv"))
    if not run_files and strict:
        raise RuntimeError(f"No run_*.csv found for {profile} in {samples_dir}")

    for run_file in run_files:
        lines = run_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        records = parse_run_lines(lines)
        validate_records(records, expected_repeat=records[0].repeat)
        rows.extend(records_to_dicts(profile, run_file.stem, records))

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def safe_geometric_mean(values: Sequence[float]) -> float:
    """Computes geometric mean while ignoring non-positive values."""

    positive = [float(v) for v in values if v > 0]
    if not positive:
        return float("nan")
    return math.exp(sum(math.log(v) for v in positive) / len(positive))


def compute_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Computes profile/op/n summary stats."""

    grouped = df.groupby(["profile", "op", "n"], as_index=False)
    stats = grouped.agg(
        runs=("run_id", "nunique"),
        eigen_mean=("eigen_avg_cycles", "mean"),
        cmsis_mean=("cmsis_avg_cycles", "mean"),
        eigen_over_cmsis_mean=("eigen_over_cmsis", "mean"),
        eigen_over_cmsis_std=("eigen_over_cmsis", "std"),
        error_mean=("error_l2", "mean"),
        error_max=("error_l2", "max"),
    )
    stats["ci_mult"] = stats["runs"].apply(lambda n: 1.96 / math.sqrt(n) if n > 0 else float("nan"))
    stats["eigen_over_cmsis_ci95"] = stats["eigen_over_cmsis_std"].fillna(0.0) * stats["ci_mult"]
    return stats


def compute_run_level_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Builds per-run readable summary rows."""

    rows: list[dict[str, object]] = []
    grouped = df.groupby(["profile", "run_id"], as_index=False)
    for _, run in grouped:
        profile = str(run.iloc[0]["profile"])
        run_id = str(run.iloc[0]["run_id"])
        mul = run[run["op"] == "mul"]
        inv = run[run["op"] == "inv"]
        rows.append(
            {
                "profile": profile,
                "run_id": run_id,
                "repeat": int(run["repeat"].iloc[0]),
                "warmup": int(run["warmup"].iloc[0]),
                "build_mode": str(run["build_mode"].iloc[0]),
                "records": int(len(run)),
                "mul_points": int(len(mul)),
                "inv_points": int(len(inv)),
                "mul_eigen_over_cmsis_mean": float(mul["eigen_over_cmsis"].mean()),
                "inv_eigen_over_cmsis_mean": float(inv["eigen_over_cmsis"].mean()),
                "overall_eigen_over_cmsis_gmean": safe_geometric_mean(
                    run["eigen_over_cmsis"].tolist()
                ),
                "error_mean": float(run["error_l2"].mean()),
                "error_max": float(run["error_l2"].max()),
            }
        )
    return (
        pd.DataFrame(rows)
        .sort_values(["profile", "run_id"])
        .reset_index(drop=True)
    )


def build_profile_points(stats: pd.DataFrame, profiles: Sequence[str]) -> dict[str, list[tuple[str, int, float]]]:
    """Builds profile->(op,n,speedup) mapping for phenomenon grouping."""

    mapping: dict[str, list[tuple[str, int, float]]] = {}
    for profile in profiles:
        sub = stats[stats["profile"] == profile]
        points: list[tuple[str, int, float]] = []
        for _, row in sub.iterrows():
            points.append((str(row["op"]), int(row["n"]), float(row["eigen_over_cmsis_mean"])))
        mapping[profile] = points
    return mapping


def parse_signature(signature: str) -> tuple[str, str, str, str]:
    """Parses phenomenon signature text into structured fields."""

    # Example: mul:CCCCCCCC:cross=none|inv:CCCCC:cross=none
    sections = signature.split("|")
    mul_pattern = ""
    mul_cross = "none"
    inv_pattern = ""
    inv_cross = "none"
    for section in sections:
        fields = section.split(":")
        if len(fields) != 3:
            continue
        op = fields[0]
        pattern = fields[1]
        cross = fields[2].replace("cross=", "")
        if op == "mul":
            mul_pattern = pattern
            mul_cross = cross
        elif op == "inv":
            inv_pattern = pattern
            inv_cross = cross
    return mul_pattern, mul_cross, inv_pattern, inv_cross


def build_group_summary(
    grouped: Sequence[tuple[str, list[str]]],
    stats: pd.DataFrame,
) -> list[dict[str, object]]:
    """Builds readable phenomenon group summaries."""

    summaries: list[dict[str, object]] = []
    for idx, (signature, members) in enumerate(grouped, start=1):
        subset = stats[stats["profile"].isin(members)]
        profile_gmeans = (
            subset.groupby("profile")["eigen_over_cmsis_mean"]
            .apply(lambda s: safe_geometric_mean(list(s)))
            .to_dict()
        )
        gmean_values = [float(v) for v in profile_gmeans.values() if v > 0]
        gmean_min = min(gmean_values) if gmean_values else float("nan")
        gmean_max = max(gmean_values) if gmean_values else float("nan")
        mul_pattern, mul_cross, inv_pattern, inv_cross = parse_signature(signature)
        summaries.append(
            {
                "group_id": f"G{idx}",
                "signature": signature,
                "profiles": members,
                "mul_pattern": mul_pattern,
                "mul_cross": mul_cross,
                "inv_pattern": inv_pattern,
                "inv_cross": inv_cross,
                "gmean_min": gmean_min,
                "gmean_max": gmean_max,
                "size": len(members),
            }
        )
    return summaries


def plot_overview_one_figure(
    stats: pd.DataFrame,
    profiles: Sequence[str],
    group_summary: Sequence[dict[str, object]],
    out_file: Path,
) -> None:
    """Generates one combined figure for fast reading.

    Top subplot: heatmap of Eigen/CMSIS per profile and point.
    Bottom subplot: geometric-mean bar chart per profile.
    """

    point_order: list[tuple[str, int]] = []
    point_order.extend(("mul", n) for n in EXPECTED_MUL_SIZES)
    point_order.extend(("inv", n) for n in EXPECTED_INV_SIZES)

    matrix_rows: list[list[float]] = []
    for profile in profiles:
        row: list[float] = []
        sub = stats[stats["profile"] == profile]
        for op, n in point_order:
            val = sub[(sub["op"] == op) & (sub["n"] == n)]["eigen_over_cmsis_mean"]
            row.append(float(val.iloc[0]) if not val.empty else float("nan"))
        matrix_rows.append(row)

    matrix = np.array(matrix_rows, dtype=float)
    finite_mask = np.isfinite(matrix) & (matrix > 0)
    if not finite_mask.any():
        raise RuntimeError("No valid speedup points to plot in overview figure.")

    log_matrix = np.full_like(matrix, np.nan)
    log_matrix[finite_mask] = np.log2(matrix[finite_mask])
    finite_logs = log_matrix[np.isfinite(log_matrix)]
    max_abs = max(abs(float(np.min(finite_logs))), abs(float(np.max(finite_logs))))
    if max_abs <= 0:
        max_abs = 0.5

    group_color_map: dict[str, str] = {}
    palette = plt.get_cmap("tab20")
    for index, group in enumerate(group_summary):
        color = palette(index % 20)
        for profile in group["profiles"]:
            group_color_map[str(profile)] = color

    fig = plt.figure(figsize=(18, 11), constrained_layout=True)
    grid = fig.add_gridspec(2, 1, height_ratios=[3.0, 1.8], hspace=0.35)

    ax_heat = fig.add_subplot(grid[0, 0])
    norm = mcolors.TwoSlopeNorm(vmin=-max_abs, vcenter=0.0, vmax=max_abs)
    image = ax_heat.imshow(log_matrix, cmap="RdYlGn", norm=norm, aspect="auto")
    ax_heat.set_title("Combined heatmap (log2(Eigen/CMSIS), >0 means CMSIS faster)")
    ax_heat.set_xticks(np.arange(len(point_order)))
    ax_heat.set_yticks(np.arange(len(profiles)))
    ax_heat.set_yticklabels(profiles)
    ax_heat.set_xticklabels([f"{op}-{n}" for op, n in point_order], rotation=45, ha="right")

    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            value = matrix[y, x]
            if math.isfinite(value) and value > 0:
                color = "black" if abs(log_matrix[y, x]) < (max_abs * 0.55) else "white"
                ax_heat.text(x, y, f"{value:.2f}", ha="center", va="center", fontsize=8, color=color)

    cbar = fig.colorbar(image, ax=ax_heat, fraction=0.035, pad=0.02)
    cbar.set_label("log2(Eigen/CMSIS)")

    ax_bar = fig.add_subplot(grid[1, 0])
    profile_gmeans: list[float] = []
    for profile in profiles:
        sub = stats[stats["profile"] == profile]
        profile_gmeans.append(safe_geometric_mean(sub["eigen_over_cmsis_mean"].tolist()))

    bar_colors = [group_color_map.get(profile, "#4c78a8") for profile in profiles]
    bars = ax_bar.bar(profiles, profile_gmeans, color=bar_colors)
    ax_bar.axhline(1.0, linestyle="--", linewidth=1.2, color="black")
    ax_bar.set_ylabel("Geometric mean Eigen/CMSIS")
    ax_bar.set_title("Overall speedup by profile (geometric mean)")
    ax_bar.grid(axis="y", linestyle=":", alpha=0.4)

    for rect, value in zip(bars, profile_gmeans):
        ax_bar.text(
            rect.get_x() + rect.get_width() / 2.0,
            rect.get_height(),
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    legend_handles: list[Patch] = []
    for group in group_summary:
        first_profile = str(group["profiles"][0])
        legend_handles.append(
            Patch(
                facecolor=group_color_map.get(first_profile, "#4c78a8"),
                label=f"{group['group_id']}: {', '.join(group['profiles'])}",
            )
        )
    if legend_handles:
        ax_bar.legend(handles=legend_handles, loc="upper right", fontsize=8, framealpha=0.9)

    fig.savefig(out_file, dpi=180)
    plt.close(fig)


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """Builds a markdown table string from headers and rows."""

    header_line = "| " + " | ".join(headers) + " |"
    separator = "|" + "|".join("---" for _ in headers) + "|"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, separator, *body])


def build_report_markdown(
    paths: ReportPaths,
    profiles: Sequence[BuildProfile],
    profile_meta: dict[str, dict[str, object]],
    run_summary: pd.DataFrame,
    stats: pd.DataFrame,
    group_summary: Sequence[dict[str, object]],
    figure_rel_path: str,
    run_details_rel_path: str,
    groups_rel_path: str,
) -> str:
    """Builds readable markdown report text."""

    profile_names = [profile.name for profile in profiles]
    lines: list[str] = []
    lines.append("# 可读版全量实验报告（合并同类现象）")
    lines.append("")

    lines.append("## 1. 实验概览")
    lines.append(f"- 计划来源：`{paths.repo_dir / 'PLAN.md'}`")
    lines.append(f"- 覆盖 profile：`{', '.join(profile_names)}`")
    run_counts = run_summary.groupby("profile")["run_id"].nunique().to_dict()
    lines.append(f"- 采样轮次（按 profile）：`{sorted(run_counts.items())}`")
    lines.append(f"- 统计口径：`Eigen/CMSIS`（>1 表示 CMSIS 更快）")
    lines.append(f"- 生成时间：`{datetime.now(timezone.utc).isoformat()}`")
    lines.append("")

    lines.append("## 2. 编译与工具链条件")
    condition_headers = [
        "profile",
        "cflags",
        "cxxflags",
        "ldflags",
        "uses_lto",
        "text",
        "rodata",
        "data",
        "bss",
    ]
    condition_rows: list[list[str]] = []
    for profile in profiles:
        meta = profile_meta.get(profile.name, {})
        memory = meta.get("memory", {}) if isinstance(meta.get("memory"), dict) else {}
        condition_rows.append(
            [
                profile.name,
                profile.cflags,
                profile.cxxflags,
                profile.ldflags,
                str(profile.uses_lto),
                str(int(memory.get("text", 0))),
                str(int(memory.get("rodata", 0))),
                str(int(memory.get("data", 0))),
                str(int(memory.get("bss", 0))),
            ]
        )
    lines.append(markdown_table(condition_headers, condition_rows))
    lines.append("")

    tools = {}
    for profile in profile_names:
        meta_tools = profile_meta.get(profile, {}).get("tools", {})
        if isinstance(meta_tools, dict) and meta_tools:
            tools = meta_tools
            break
    if tools:
        lines.append("工具链路径：")
        for key in ("cube_cmake", "cube", "starm_clang", "jlink"):
            if key in tools:
                lines.append(f"- `{key}`: `{tools[key]}`")
        lines.append("")

    lines.append("## 3. 每轮测试条件与结果明细")
    lines.append(f"- 机器可读明细：`{run_details_rel_path}`")
    detail_headers = [
        "profile",
        "run_id",
        "repeat",
        "warmup",
        "build_mode",
        "records",
        "mul_mean(E/C)",
        "inv_mean(E/C)",
        "overall_gmean(E/C)",
        "error_max",
    ]
    detail_rows: list[list[str]] = []
    for _, row in run_summary.iterrows():
        detail_rows.append(
            [
                str(row["profile"]),
                str(row["run_id"]),
                str(int(row["repeat"])),
                str(int(row["warmup"])),
                str(row["build_mode"]),
                str(int(row["records"])),
                f"{float(row['mul_eigen_over_cmsis_mean']):.3f}",
                f"{float(row['inv_eigen_over_cmsis_mean']):.3f}",
                f"{float(row['overall_eigen_over_cmsis_gmean']):.3f}",
                f"{float(row['error_max']):.8f}",
            ]
        )
    lines.append(markdown_table(detail_headers, detail_rows))
    lines.append("")

    lines.append("## 4. 合并后的现象分组")
    lines.append(f"- 分组明细：`{groups_rel_path}`")
    for group in group_summary:
        profiles_text = ", ".join(group["profiles"])
        lines.append(f"### {group['group_id']}（{group['size']} 个 profile）")
        lines.append(f"- 成员：`{profiles_text}`")
        lines.append(f"- mul 模式：`{group['mul_pattern']}`，临界点：`{group['mul_cross']}`")
        lines.append(f"- inv 模式：`{group['inv_pattern']}`，临界点：`{group['inv_cross']}`")
        lines.append(
            f"- 综合速度比几何均值范围：`{float(group['gmean_min']):.3f} ~ {float(group['gmean_max']):.3f}`"
        )
        lines.append("")

    lines.append("## 5. 单图总览")
    lines.append(f"![overview_one_figure]({figure_rel_path})")
    lines.append("")

    lines.append("## 6. 关键结论")
    for profile in profile_names:
        sub = stats[(stats["profile"] == profile) & (stats["op"] == "mul")]
        pairs = list(sub[["n", "eigen_over_cmsis_mean"]].itertuples(index=False, name=None))
        cross = detect_crossover([(int(n), float(speedup)) for n, speedup in pairs])
        gmean = safe_geometric_mean(stats[stats["profile"] == profile]["eigen_over_cmsis_mean"].tolist())
        lines.append(
            f"- `{profile}`: 综合几何均值 `Eigen/CMSIS={gmean:.3f}`，mul 临界点 `{cross if cross is not None else 'none'}`"
        )
    lines.append("- 建议优先关注与目标业务矩阵规模一致的现象组，而不是只看单点峰值。")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    """Entry point for readable report generation."""

    args = parse_args()
    if pd is None or plt is None or np is None or mcolors is None:
        raise RuntimeError(
            "matplotlib/pandas/numpy are required. Install benchmark_analysis dependencies first."
        ) from _IMPORT_ERROR

    paths = build_paths(args)
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    all_profiles = default_profiles()
    selected_names = parse_profile_names(args.profiles)
    selected_profiles: list[BuildProfile] = []
    for name in selected_names:
        if name not in all_profiles:
            raise ValueError(f"Unknown profile: {name}")
        selected_profiles.append(all_profiles[name])

    frames: list[pd.DataFrame] = []
    profile_meta: dict[str, dict[str, object]] = {}
    for profile in selected_profiles:
        profile_dir = paths.input_root / profile.name
        profile_meta[profile.name] = load_profile_meta(profile_dir)
        frame = load_profile_runs(profile.name, profile_dir, strict=args.strict)
        if not frame.empty:
            frames.append(frame)
        elif args.strict:
            raise RuntimeError(f"No data for profile {profile.name}")

    if not frames:
        raise RuntimeError("No benchmark data found.")

    df = pd.concat(frames, ignore_index=True)
    stats = compute_stats(df)
    run_summary = compute_run_level_summary(df)

    selected_profile_names = [profile.name for profile in selected_profiles]
    profile_points = build_profile_points(stats, selected_profile_names)
    grouped = group_profiles_by_phenomenon(
        profile_points=profile_points,
        tolerance=float(args.group_tolerance),
    )
    group_summary = build_group_summary(grouped, stats)

    figure_file = paths.output_dir / "overview_one_figure.png"
    plot_overview_one_figure(
        stats=stats,
        profiles=selected_profile_names,
        group_summary=group_summary,
        out_file=figure_file,
    )

    run_details_csv = paths.output_dir / "run_details.csv"
    run_summary.to_csv(run_details_csv, index=False, encoding="utf-8")

    group_rows: list[dict[str, object]] = []
    for group in group_summary:
        group_rows.append(
            {
                "group_id": group["group_id"],
                "profiles": ",".join(group["profiles"]),
                "mul_pattern": group["mul_pattern"],
                "mul_cross": group["mul_cross"],
                "inv_pattern": group["inv_pattern"],
                "inv_cross": group["inv_cross"],
                "gmean_min": group["gmean_min"],
                "gmean_max": group["gmean_max"],
                "signature": group["signature"],
            }
        )
    groups_csv = paths.output_dir / "phenomenon_groups.csv"
    pd.DataFrame(group_rows).to_csv(groups_csv, index=False, encoding="utf-8")

    report_text = build_report_markdown(
        paths=paths,
        profiles=selected_profiles,
        profile_meta=profile_meta,
        run_summary=run_summary,
        stats=stats,
        group_summary=group_summary,
        figure_rel_path=str(figure_file.relative_to(paths.repo_dir)),
        run_details_rel_path=str(run_details_csv.relative_to(paths.repo_dir)),
        groups_rel_path=str(groups_csv.relative_to(paths.repo_dir)),
    )
    paths.output_md.write_text(report_text, encoding="utf-8")

    print(f"Generated report: {paths.output_md}")
    print(f"Generated one-figure summary: {figure_file}")
    print(f"Generated run details: {run_details_csv}")
    print(f"Generated phenomenon groups: {groups_csv}")


if __name__ == "__main__":
    main()
