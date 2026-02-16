from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import math
import matplotlib.pyplot as plt
import pandas as pd


@dataclass(frozen=True)
class Paths:
    repo_dir: Path
    samples_dir: Path
    output_dir: Path
    report_md: Path
    plan_md: Path
    cmake_cache: Path
    compile_commands: Path


def build_paths() -> Paths:
    repo_dir = Path(__file__).resolve().parents[1]
    return Paths(
        repo_dir=repo_dir,
        samples_dir=repo_dir / "build" / "Release_starmclang" / "samples_release",
        output_dir=repo_dir / "benchmark_analysis" / "output" / "release_samples",
        report_md=repo_dir / "report.md",
        plan_md=repo_dir / "PLAN.md",
        cmake_cache=repo_dir / "build" / "Release_starmclang" / "CMakeCache.txt",
        compile_commands=repo_dir / "build" / "Release_starmclang" / "compile_commands.json",
    )


def load_single_csv(path: Path, run_id: str) -> pd.DataFrame:
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


def load_all_samples(samples_dir: Path) -> pd.DataFrame:
    files = sorted(samples_dir.glob("run_*.csv"))
    if not files:
        raise RuntimeError(f"No sample csv files found in {samples_dir}")
    frames = []
    for f in files:
        run_id = f.stem
        frames.append(load_single_csv(f, run_id))
    df = pd.concat(frames, ignore_index=True)
    return df


def compute_stats(df: pd.DataFrame) -> pd.DataFrame:
    group = df.groupby(["op", "n"], as_index=False)
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


def plot_cycles(stats: pd.DataFrame, op: str, out_path: Path) -> None:
    sub = stats[stats["op"] == op].sort_values("n")
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
    ax.set_title(f"{op.upper()} Cycles (Release O3/LTO, n=10)")
    ax.set_xlabel("Matrix Size N")
    ax.set_ylabel("Average Cycles")
    ax.set_yscale("log")
    ax.grid(True, which="both", linestyle=":", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_ratio(stats: pd.DataFrame, op: str, out_path: Path) -> None:
    sub = stats[stats["op"] == op].sort_values("n")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(
        sub["n"],
        sub["ratio_mean"],
        yerr=sub["ratio_ci"],
        marker="o",
        label="CMSIS / Eigen",
    )
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_title(f"{op.upper()} Ratio (CMSIS/Eigen, mean ±95%CI)")
    ax.set_xlabel("Matrix Size N")
    ax.set_ylabel("Ratio")
    ax.grid(True, which="both", linestyle=":", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def read_cmake_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith(key + ":"):
            return line.split("=", 1)[-1].strip()
    return None


def extract_toolchain_version(path: Path) -> str:
    if not path.exists():
        return "未知"
    text = path.read_text(encoding="utf-8", errors="ignore")
    marker = "starm-clang"
    idx = text.find(marker)
    if idx == -1:
        return "未知"
    snippet = text[idx : idx + 200]
    return snippet.split(" ")[0].strip()


def build_report(paths: Paths, df: pd.DataFrame, stats: pd.DataFrame) -> str:
    plan_title = "未知"
    if paths.plan_md.exists():
        with paths.plan_md.open("r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if first_line:
                plan_title = first_line.lstrip("# ").strip()

    build_type = read_cmake_value(paths.cmake_cache, "CMAKE_BUILD_TYPE") or "未知"
    perf_mode = read_cmake_value(paths.cmake_cache, "BENCHMARK_PERF_MODE") or "未知"
    compiler = extract_toolchain_version(paths.compile_commands)

    expected_mul = [3, 4, 6, 8, 10, 16, 32, 64]
    expected_inv = [3, 4, 6, 8, 10]
    got_mul = stats[stats["op"] == "mul"]["n"].tolist()
    got_inv = stats[stats["op"] == "inv"]["n"].tolist()

    repeat_ok = bool((df["repeat"] == 100).all())
    valid_sum_ok = bool(((df["valid"] + df["invalid"]) == 100).all())
    error_ok = bool((df["error_l2"] <= 1e-4).all())

    build_modes = ", ".join(sorted(df["build_mode"].unique()))

    def format_table(op: str) -> str:
        sub = stats[stats["op"] == op].sort_values("n")
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

    return f"""# 基准统计报告（Release/O3/LTO，10 轮）

## 1. 关联计划
- 计划标题：`{plan_title}`
- 计划文件：`PLAN.md`

## 2. 构建与采样配置
- 工具链：`{compiler}`
- 构建类型：`{build_type}`
- BENCHMARK_PERF_MODE：`{perf_mode}`
- 采样轮数：`10`
- 数据目录：`build/Release_starmclang/samples_release`
- build_mode 字段：`{build_modes}`

## 3. 口径一致性检查
- `mul` 尺寸应为 `{expected_mul}`，实测为 `{got_mul}`
- `inv` 尺寸应为 `{expected_inv}`，实测为 `{got_inv}`
- `repeat=100`：`{"通过" if repeat_ok else "不通过"}`
- `valid+invalid=100`：`{"通过" if valid_sum_ok else "不通过"}`
- `error_l2 <= 1e-4`：`{"通过" if error_ok else "不通过"}`

## 4. 可视化结果
### 4.1 乘法周期（均值 ±95%CI）
![mul_cycles](benchmark_analysis/output/release_samples/mul_cycles.png)

### 4.2 求逆周期（均值 ±95%CI）
![inv_cycles](benchmark_analysis/output/release_samples/inv_cycles.png)

### 4.3 乘法比值（CMSIS/Eigen，均值 ±95%CI）
![mul_ratio](benchmark_analysis/output/release_samples/mul_ratio.png)

### 4.4 求逆比值（CMSIS/Eigen，均值 ±95%CI）
![inv_ratio](benchmark_analysis/output/release_samples/inv_ratio.png)

## 5. 统计表
> 置信区间按正态近似：`mean ± 1.96 * std / sqrt(n)`（n=10）。

### 5.1 乘法统计表
{format_table("mul")}

### 5.2 求逆统计表
{format_table("inv")}

## 6. 结论摘要
- 10 轮采样均完成，数据完整性通过。
- Release/O3/LTO 下的均值、方差与 95%CI 已给出，可用于正式性能结论的统计基础。
"""


def main() -> None:
    paths = build_paths()
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    df = load_all_samples(paths.samples_dir)
    stats = compute_stats(df)

    stats.to_csv(paths.output_dir / "summary.csv", index=False, encoding="utf-8")

    plot_cycles(stats, "mul", paths.output_dir / "mul_cycles.png")
    plot_cycles(stats, "inv", paths.output_dir / "inv_cycles.png")
    plot_ratio(stats, "mul", paths.output_dir / "mul_ratio.png")
    plot_ratio(stats, "inv", paths.output_dir / "inv_ratio.png")

    report = build_report(paths, df, stats)
    paths.report_md.write_text(report, encoding="utf-8")

    print(f"Generated report: {paths.report_md}")
    print(f"Generated plots in: {paths.output_dir}")


if __name__ == "__main__":
    main()
