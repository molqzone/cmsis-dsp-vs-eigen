# benchmark_analysis

全量实验自动化工具，覆盖 `PLAN.md` 中 C1~C10 的全部实验项：

- 构建（cube-cmake + starm-clang）
- 烧录（JLink）
- 串口采样（CDC）
- 统计分析（均值/方差/95%CI）
- 报告生成（`report_full_matrix.md`，并同步输出 `report.md`）

## 1. 依赖安装

在 `benchmark_analysis/` 目录安装依赖：

```bash
uv sync
```

如果不使用 `uv`，可用：

```bash
python -m pip install -U matplotlib pandas pyserial
```

## 2. 一键全流程

在仓库根目录执行：

```bash
python -X utf8 "benchmark_analysis/run_full_matrix.py"
```

默认行为：

- profiles: `C1~C10`
- 每 profile 采样 `10` 轮
- 串口：`/dev/ttyACM0`
- 严格失败：任一 profile 失败立即中止，不生成最终报告
- 全部成功后自动调用 `generate_full_matrix_report.py`
- 全部成功后会把 `report_full_matrix.md` 同步复制为 `report.md`（兼容完成标志）

## 3. 常用参数

```bash
python -X utf8 "benchmark_analysis/run_full_matrix.py" \
  --profiles C1,C2,C3 \
  --runs 10 \
  --port /dev/ttyACM0 \
  --timeout-sec 420 \
  --resume
```

说明：

- `--resume`：跳过已完成的 profile（需存在完整 `run_*.csv` 与 `profile_meta.json`）
- `--dry-run`：仅验证流程配置，不执行构建/烧录/采样
- `--cube-cmake` / `--cube` / `--toolchain-bin` / `--jlink`：覆盖工具链路径
- 串口采样已内置“端口重连等待 + `/dev/ttyACM*` 自动探测”，用于处理烧录后 CDC 设备短暂重枚举
- `--timeout-sec` 为“串口空闲超时”（非整次采样总时长），仅在长时间无新串口数据时失败

## 4. 仅生成报告

若采样数据已存在，可单独生成报告：

```bash
python -X utf8 "benchmark_analysis/generate_full_matrix_report.py" \
  --input-root "build/bench_matrix" \
  --output-md "report_full_matrix.md" \
  --output-dir "benchmark_analysis/output/full_matrix" \
  --profiles C1,C2,C3,C4,C5,C6,C7,C8,C9,C10 \
  --strict
```

## 5. 生成更易读的合并报告（单图总览）

如果你希望报告更偏“读结论”，可生成可读版报告（包含每轮条件明细 + 现象分组 + 单张合成图）：

```bash
python -X utf8 "benchmark_analysis/generate_readable_report.py" \
  --input-root "build/bench_matrix" \
  --output-md "report_readable.md" \
  --output-dir "benchmark_analysis/output/readable" \
  --profiles C1,C2,C3,C4,C5,C6,C7,C8,C9,C10
```

产物：

- 报告：`report_readable.md`
- 单图总览：`benchmark_analysis/output/readable/overview_one_figure.png`
- 每轮明细：`benchmark_analysis/output/readable/run_details.csv`
- 现象分组：`benchmark_analysis/output/readable/phenomenon_groups.csv`

## 6. 目录约定

- 构建目录：`build/bench_matrix/<profile>/build/`
- 采样目录：`build/bench_matrix/<profile>/samples_release/`
- 日志目录：`build/bench_matrix/<profile>/logs/`
- profile 元数据：`build/bench_matrix/<profile>/profile_meta.json`
- 图表与统计：`benchmark_analysis/output/full_matrix/`
- 报告：`report_full_matrix.md` 与 `report.md`

## 7. 可视化口径说明

- 主口径：`speedup = Eigen / CMSIS`
- `speedup > 1`：CMSIS-DSP 更快；`speedup < 1`：Eigen 更快
- 图右侧副轴展示 `CMSIS/Eigen`（与板端原始字段 `cmsis_over_eigen` 对齐）
- 跨 profile 额外提供 speedup 分布图：
  - `mul_eigen_over_cmsis_box_by_profile.png`
  - `inv_eigen_over_cmsis_box_by_profile.png`
- 跨 profile 线图与箱线图按 profile 独立展示，不做曲线自动合并

## 8. 常见故障

### 7.1 configure/build 失败

- 检查 `build/bench_matrix/<profile>/logs/configure_build.log`
- 检查 `cube`、`cube-cmake`、`starm-clang` 是否可执行
- 若提示 `cube command is not available`，通常是 `cube` 路径未加入 PATH

### 7.2 JLink 烧录失败

- 检查 `build/bench_matrix/<profile>/logs/jlink_flash.log`
- 确认目标板上电、SWD 连接正常
- 确认 `--device` 与芯片型号匹配（默认 `STM32F407ZG`）

### 7.3 串口采样超时

- 检查 `build/bench_matrix/<profile>/logs/serial_capture.log`
- 确认设备节点（如 `/dev/ttyACM0`）正确且有权限
- 若端口变化，改用 `--port` 指定
- 修复后使用 `--resume` 继续
- 若日志长期停在 `mul,32` 或 `mul,64` 前后，这通常是大矩阵计算耗时，优先等待一段时间再判断超时
