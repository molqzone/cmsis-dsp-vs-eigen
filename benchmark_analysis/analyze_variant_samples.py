from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import math
import matplotlib.pyplot as plt
import pandas as pd


@dataclass(frozen=True)
class Variant:
    name: str
    cflags: str
    cxxflags: str
    ldflags: str


@dataclass(frozen=True)
class Paths:
    repo_dir: Path
    output_dir: Path
    report_md: Path


def build_paths() -> Paths:
    repo_dir = Path(__file__).resolve().parents[1]
    return Paths(
        repo_dir=repo_dir,
        output_dir=repo_dir / "benchmark_analysis" / "output" / "variant_samples",
        report_md=repo_dir / "report.md",
    )


def load_single_csv(path: Path, run_id: str, variant: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line == "done":
                continue
            cols = line.split(",")
            first = cols[0].lstrip("\ufeff")
            if first == "op":
                continue
            if len(cols) != 11:
                continue
            rows.append(
                {
                    "variant": variant,
                    "run_id": run_id,
                    "op": first,
                    "n": int(cols[1]),
                    "repeat": int(cols[2]),
                    "warmup": int(cols[3]),
                    "eigen_avg_cycles": float(cols[4]),
                    "cmsis_avg_cycles": float(cols[5]),
                    "cmsis_over_eigen": float(cols[6]),
                    "error_l2": float(cols[7]),
                    "valid": int(cols[8]),
                    "invalid": int(cols[9]),
                    "build_mode": cols[10],
                }
            )
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError(f"Empty benchmark data: {path}")
    return df


def load_all_samples(samples_dir: Path, variant: str) -> pd.DataFrame:
    files = sorted(samples_dir.glob("run_*.csv"))
    if not files:
        raise RuntimeError(f"No sample csv files found in {samples_dir}")
    frames = []
    for f in files:
        run_id = f.stem
        frames.append(load_single_csv(f, run_id, variant))
    df = pd.concat(frames, ignore_index=True)
    return df


def compute_stats(df: pd.DataFrame) -> pd.DataFrame:
    group = df.groupby(["variant", "op", "n"], as_index=False)
    stats = group.agg(
        runs=("run_id", "nunique"),
        eigen_mean=("eigen_avg_cycles", "mean"),
        eigen_var=("eigen_avg_cycles", "var"),
        eigen_std=("eigen_avg_cycles", "std"),
        cmsis_mean=("cmsis_avg_cycles", "mean"),
        cmsis_var=("cmsis_avg_cycles", "var"),
        cmsis_std=("cmsis_avg_cycles", "std"),
        ratio_mean=("cmsis_over_eigen", "mean"),
        ratio_var=("cmsis_over_eigen", "var"),
        ratio_std=("cmsis_over_eigen", "std"),
        error_mean=("error_l2", "mean"),
        error_var=("error_l2", "var"),
        error_std=("error_l2", "std"),
    )
    stats["ci_mult"] = stats["runs"].apply(lambda n: 1.96 / math.sqrt(n))
    stats["eigen_ci"] = stats["eigen_std"] * stats["ci_mult"]
    stats["cmsis_ci"] = stats["cmsis_std"] * stats["ci_mult"]
    stats["ratio_ci"] = stats["ratio_std"] * stats["ci_mult"]
    stats["error_ci"] = stats["error_std"] * stats["ci_mult"]
    return stats


def plot_cycles(stats: pd.DataFrame, variant: str, op: str, out_path: Path) -> None:
    sub = stats[(stats["variant"] == variant) & (stats["op"] == op)].sort_values("n")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(
        sub["n"],
        sub["eigen_mean"],
        yerr=sub["eigen_ci"],
        marker="o",
        label="Eigen mean ±95%CI",
    )
    ax.errorbar(
        sub["n"],
        sub["cmsis_mean"],
        yerr=sub["cmsis_ci"],
        marker="s",
        label="CMSIS mean ±95%CI",
    )
    ax.set_title(f"{variant.upper()} {op.upper()} Cycles (n=10)")
    ax.set_xlabel("Matrix Size N")
    ax.set_ylabel("Average Cycles")
    ax.set_yscale("log")
    ax.grid(True, which="both", linestyle=":", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_ratio(stats: pd.DataFrame, variant: str, op: str, out_path: Path) -> None:
    sub = stats[(stats["variant"] == variant) & (stats["op"] == op)].sort_values("n")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(
        sub["n"],
        sub["ratio_mean"],
        yerr=sub["ratio_ci"],
        marker="o",
        label="CMSIS / Eigen",
    )
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_title(f"{variant.upper()} {op.upper()} Ratio (mean ±95%CI)")
    ax.set_xlabel("Matrix Size N")
    ax.set_ylabel("Ratio")
    ax.grid(True, which="both", linestyle=":", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def format_table(stats: pd.DataFrame, variant: str, op: str) -> str:
    sub = stats[(stats["variant"] == variant) & (stats["op"] == op)].sort_values("n")
    lines = [
        "| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | ratio_mean | ratio_var | ratio_95%CI |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in sub.iterrows():
        lines.append(
            "| {n} | {em:.2f} | {ev:.2f} | ±{eci:.2f} | {cm:.2f} | {cv:.2f} | ±{cci:.2f} | {rm:.3f} | {rv:.5f} | ±{rci:.3f} |".format(
                n=int(r["n"]),
                em=r["eigen_mean"],
                ev=r["eigen_var"],
                eci=r["eigen_ci"],
                cm=r["cmsis_mean"],
                cv=r["cmsis_var"],
                cci=r["cmsis_ci"],
                rm=r["ratio_mean"],
                rv=r["ratio_var"],
                rci=r["ratio_ci"],
            )
        )
    return "\n".join(lines)


def replace_section(text: str, heading: str, new_section: str) -> str:
    if heading not in text:
        return text.rstrip() + "\n\n" + new_section.strip() + "\n"
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start = i
            break
    if start is None:
        return text.rstrip() + "\n\n" + new_section.strip() + "\n"
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    updated = lines[:start] + new_section.strip().splitlines() + lines[end:]
    return "\n".join(updated).rstrip() + "\n"


def build_report_section(
    variants: list[Variant],
    stats: pd.DataFrame,
    missing: list[str],
    output_dir: Path,
) -> str:
    lines = []
    lines.append("## 7. 编译器参数变体对比")
    lines.append("")
    lines.append("### 7.1 变体配置")
    lines.append("| variant | C_FLAGS_RELEASE | CXX_FLAGS_RELEASE | LD_FLAGS_RELEASE | 数据状态 |")
    lines.append("|---|---|---|---|---|")
    for v in variants:
        status = "有数据"
        if v.name in missing:
            status = "缺失"
        lines.append(
            f"| {v.name} | `{v.cflags}` | `{v.cxxflags}` | `{v.ldflags}` | {status} |"
        )
    if missing:
        lines.append("")
        lines.append("### 7.2 异常/跳过说明")
        lines.append("以下变体未获得完整采样数据，请检查构建或 CDC 采样日志后重试：")
        for name in missing:
            lines.append(f"- `{name}`")

    idx = 3
    for v in variants:
        if v.name in missing:
            continue
        lines.append("")
        lines.append(f"### 7.{idx} {v.name} 结果")
        lines.append("")
        lines.append(
            f"![{v.name}_mul_cycles](benchmark_analysis/output/variant_samples/{v.name}_mul_cycles.png)"
        )
        lines.append(
            f"![{v.name}_inv_cycles](benchmark_analysis/output/variant_samples/{v.name}_inv_cycles.png)"
        )
        lines.append(
            f"![{v.name}_mul_ratio](benchmark_analysis/output/variant_samples/{v.name}_mul_ratio.png)"
        )
        lines.append(
            f"![{v.name}_inv_ratio](benchmark_analysis/output/variant_samples/{v.name}_inv_ratio.png)"
        )
        lines.append("")
        lines.append(f"#### 7.{idx}.1 乘法统计表")
        lines.append(format_table(stats, v.name, "mul"))
        lines.append("")
        lines.append(f"#### 7.{idx}.2 求逆统计表")
        lines.append(format_table(stats, v.name, "inv"))
        idx += 1

    return "\n".join(lines)


def main() -> None:
    variants = [
        Variant("o2", "-g0 -O2", "-g0 -O2", ""),
        Variant("o3", "-g0 -O3", "-g0 -O3", ""),
        Variant("ofast", "-g0 -Ofast", "-g0 -Ofast", ""),
        Variant("o3_lto", "-g0 -O3 -flto", "-g0 -O3 -flto", "-flto"),
    ]

    paths = build_paths()
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    missing = []
    for v in variants:
        samples_dir = paths.repo_dir / "build" / "bench_flags" / v.name / "samples_release"
        try:
            df = load_all_samples(samples_dir, v.name)
            frames.append(df)
        except Exception:
            missing.append(v.name)

    if not frames:
        raise RuntimeError("No variant samples available to analyze.")

    df_all = pd.concat(frames, ignore_index=True)
    stats = compute_stats(df_all)
    stats.to_csv(paths.output_dir / "summary_variants.csv", index=False, encoding="utf-8")

    for v in variants:
        if v.name in missing:
            continue
        plot_cycles(stats, v.name, "mul", paths.output_dir / f"{v.name}_mul_cycles.png")
        plot_cycles(stats, v.name, "inv", paths.output_dir / f"{v.name}_inv_cycles.png")
        plot_ratio(stats, v.name, "mul", paths.output_dir / f"{v.name}_mul_ratio.png")
        plot_ratio(stats, v.name, "inv", paths.output_dir / f"{v.name}_inv_ratio.png")

    section = build_report_section(variants, stats, missing, paths.output_dir)
    report_text = paths.report_md.read_text(encoding="utf-8")
    updated = replace_section(report_text, "## 7. 编译器参数变体对比", section)
    paths.report_md.write_text(updated, encoding="utf-8")

    print(f"Generated variant summary: {paths.output_dir / 'summary_variants.csv'}")
    print(f"Updated report: {paths.report_md}")


if __name__ == "__main__":
    main()
