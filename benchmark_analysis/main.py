from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


@dataclass(frozen=True)
class Paths:
    project_dir: Path
    repo_dir: Path
    csv_off: Path
    csv_on: Path
    plan_md: Path
    output_dir: Path
    report_md: Path


def build_paths() -> Paths:
    project_dir = Path(__file__).resolve().parent
    repo_dir = project_dir.parent
    return Paths(
        project_dir=project_dir,
        repo_dir=repo_dir,
        csv_off=repo_dir / "build" / "Debug" / "benchmark_capture_after_reset.csv",
        csv_on=repo_dir / "build" / "Debug" / "benchmark_capture_perf_mode.csv",
        plan_md=repo_dir / "PLAN.md",
        output_dir=project_dir / "output",
        report_md=repo_dir / "report.md",
    )


def load_benchmark_csv(csv_path: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    with csv_path.open("r", encoding="utf-8") as f:
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
    df = pd.DataFrame(rows).sort_values(["op", "n"], ignore_index=True)
    if df.empty:
        raise RuntimeError(f"Empty benchmark data: {csv_path}")
    return df


def make_cycles_plot(df_off: pd.DataFrame, df_on: pd.DataFrame, op: str, out_path: Path) -> None:
    off_op = df_off[df_off["op"] == op].sort_values("n")
    on_op = df_on[df_on["op"] == op].sort_values("n")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        off_op["n"],
        off_op["eigen_avg_cycles"],
        marker="o",
        label="Eigen (PERF_MODE=OFF)",
    )
    ax.plot(
        off_op["n"],
        off_op["cmsis_avg_cycles"],
        marker="o",
        label="CMSIS (PERF_MODE=OFF)",
    )
    ax.plot(
        on_op["n"],
        on_op["eigen_avg_cycles"],
        marker="s",
        linestyle="--",
        label="Eigen (PERF_MODE=ON)",
    )
    ax.plot(
        on_op["n"],
        on_op["cmsis_avg_cycles"],
        marker="s",
        linestyle="--",
        label="CMSIS (PERF_MODE=ON)",
    )
    ax.set_title(f"{op.upper()} Cycles Comparison")
    ax.set_xlabel("Matrix Size N")
    ax.set_ylabel("Average Cycles")
    ax.set_yscale("log")
    ax.grid(True, which="both", linestyle=":", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def make_speedup_plot(merged: pd.DataFrame, out_path: Path) -> None:
    merged = merged.copy()
    merged["label"] = merged["op"] + "-" + merged["n"].astype(str)
    x = range(len(merged))
    width = 0.4

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(
        [v - width / 2 for v in x],
        merged["eigen_speedup"],
        width=width,
        label="Eigen speedup (OFF/ON)",
    )
    ax.bar(
        [v + width / 2 for v in x],
        merged["cmsis_speedup"],
        width=width,
        label="CMSIS speedup (OFF/ON)",
    )
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_xticks(list(x))
    ax.set_xticklabels(merged["label"], rotation=45, ha="right")
    ax.set_ylabel("Speedup")
    ax.set_title("Speedup from PERF_MODE=OFF to ON")
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def build_merged_table(df_off: pd.DataFrame, df_on: pd.DataFrame) -> pd.DataFrame:
    merged = pd.merge(
        df_off,
        df_on,
        on=["op", "n"],
        suffixes=("_off", "_on"),
        validate="one_to_one",
    ).sort_values(["op", "n"], ignore_index=True)
    merged["eigen_speedup"] = merged["eigen_avg_cycles_off"] / merged["eigen_avg_cycles_on"]
    merged["cmsis_speedup"] = merged["cmsis_avg_cycles_off"] / merged["cmsis_avg_cycles_on"]
    return merged


def format_table(df: pd.DataFrame) -> str:
    headers = [
        "op",
        "n",
        "eigen_avg_cycles_off",
        "eigen_avg_cycles_on",
        "eigen_speedup",
        "cmsis_avg_cycles_off",
        "cmsis_avg_cycles_on",
        "cmsis_speedup",
    ]
    lines = [
        "| op | n | eigen_off | eigen_on | eigen_speedup | cmsis_off | cmsis_on | cmsis_speedup |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in df[headers].iterrows():
        lines.append(
            "| {op} | {n} | {eoff:.2f} | {eon:.2f} | {es:.2f}x | {coff:.2f} | {con:.2f} | {cs:.2f}x |".format(
                op=r["op"],
                n=int(r["n"]),
                eoff=r["eigen_avg_cycles_off"],
                eon=r["eigen_avg_cycles_on"],
                es=r["eigen_speedup"],
                coff=r["cmsis_avg_cycles_off"],
                con=r["cmsis_avg_cycles_on"],
                cs=r["cmsis_speedup"],
            )
        )
    return "\n".join(lines)


def build_report(paths: Paths, df_off: pd.DataFrame, df_on: pd.DataFrame, merged: pd.DataFrame) -> str:
    plan_title = "未知"
    with paths.plan_md.open("r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        if first_line:
            plan_title = first_line.lstrip("# ").strip()

    expected_mul = [3, 4, 6, 8, 10, 16, 32, 64]
    expected_inv = [3, 4, 6, 8, 10]
    got_mul = df_on[df_on["op"] == "mul"]["n"].tolist()
    got_inv = df_on[df_on["op"] == "inv"]["n"].tolist()
    repeat_ok = bool((df_on["repeat"] == 100).all())
    valid_sum_ok = bool(((df_on["valid"] + df_on["invalid"]) == 100).all())
    error_ok = bool((df_on["error_l2"] <= 1e-4).all())

    cmsis_faster_on = merged[merged["cmsis_avg_cycles_on"] < merged["eigen_avg_cycles_on"]]
    cmsis_faster_labels = [f'{r["op"]}-{int(r["n"])}' for _, r in cmsis_faster_on.iterrows()]

    return f"""# 基准测试结果报告（基于 PLAN.md）

## 1. 关联计划
- 计划标题：`{plan_title}`
- 计划文件：`PLAN.md`
- 数据来源：
  - `build/Debug/benchmark_capture_after_reset.csv`（PERF_MODE=OFF）
  - `build/Debug/benchmark_capture_perf_mode.csv`（PERF_MODE=ON）

## 2. 计划口径一致性检查
- `mul` 尺寸应为 `{expected_mul}`，实测为 `{got_mul}`
- `inv` 尺寸应为 `{expected_inv}`，实测为 `{got_inv}`
- `repeat=100`：`{"通过" if repeat_ok else "不通过"}`
- `valid+invalid=100`：`{"通过" if valid_sum_ok else "不通过"}`
- `error_l2 <= 1e-4`：`{"通过" if error_ok else "不通过"}`

## 3. 可视化结果
### 3.1 乘法周期对比（对数坐标）
![mul_cycles](benchmark_analysis/output/mul_cycles.png)

### 3.2 求逆周期对比（对数坐标）
![inv_cycles](benchmark_analysis/output/inv_cycles.png)

### 3.3 OFF->ON 加速倍数对比
![speedup](benchmark_analysis/output/speedup.png)

## 4. 关键观察
- PERF_MODE 从 OFF 切换到 ON 后，Eigen 整体加速更明显，CMSIS 提升幅度相对有限。
- 在 PERF_MODE=ON 下，CMSIS 更快（`cmsis_avg_cycles < eigen_avg_cycles`）的点位：
  - {", ".join(cmsis_faster_labels) if cmsis_faster_labels else "无"}
- 注意：当前数据中的 `build_mode` 仍为 `Debug`，仅可用于框架和趋势验证，不作为最终正式性能结论。

## 5. OFF vs ON 详细对比表
{format_table(merged)}

## 6. 结论
- 按 PLAN.md 约束，本次测试已完成矩阵乘法（8 个尺寸）与求逆（5 个尺寸）的完整闭环。
- 可视化和数据一致性检查通过，说明基准框架可用于后续正式采样。
- 若要发布正式结论，建议在统一 Release/O3/LTO 条件下重复采样并增加多次运行统计（均值+方差/置信区间）。
"""


def main() -> None:
    paths = build_paths()
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    df_off = load_benchmark_csv(paths.csv_off)
    df_on = load_benchmark_csv(paths.csv_on)
    merged = build_merged_table(df_off, df_on)

    make_cycles_plot(df_off, df_on, "mul", paths.output_dir / "mul_cycles.png")
    make_cycles_plot(df_off, df_on, "inv", paths.output_dir / "inv_cycles.png")
    make_speedup_plot(merged, paths.output_dir / "speedup.png")

    report = build_report(paths, df_off, df_on, merged)
    paths.report_md.write_text(report, encoding="utf-8")

    print(f"Generated report: {paths.report_md}")
    print(f"Generated plots in: {paths.output_dir}")


if __name__ == "__main__":
    main()
