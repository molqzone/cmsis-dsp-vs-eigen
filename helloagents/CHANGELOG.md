# 变更日志

## [Unreleased]

### 新增
- **[benchmark_experiment]**: 新增 Debug 闭环基准框架实现
  - 新增 `User/benchmark_config.hpp` 常量配置：`kMulSizes={3,4,6,8,10,16,32,64}`、`kInvSizes={3,4,6,8,10}`、`kWarmup=1`、`kRepeat=100`、`kErrThreshold=1e-4`
  - 新增 DWT 计时模块、LCG 随机输入模块、CMSIS/Eigen 计算封装模块、结果汇总与 CSV 输出模块
  - 输出口径固定为 `op,n,repeat,warmup,eigen_avg_cycles,cmsis_avg_cycles,cmsis_over_eigen,error_l2,valid,invalid,build_mode`
- **[benchmark_experiment]**: 新增全量矩阵自动化与报告生成能力（C1~C11）
  - 新增 `benchmark_analysis/run_full_matrix.py`：一键执行构建、JLink 烧录、串口采样、严格失败中止与 `--resume` 续跑
  - 新增 `benchmark_analysis/generate_full_matrix_report.py`：聚合 `build/bench_matrix/*/samples_release/run_*.csv` 并生成 `report_full_matrix.md`
  - 新增 `benchmark_analysis/full_matrix_common.py`：统一 profile 矩阵、CSV 解析、run 校验、临界点检测
  - 新增单元测试 `tests/benchmark_analysis/test_full_matrix_common.py`
  - 更新 `benchmark_analysis/README.md` 与 `benchmark_analysis/pyproject.toml`（新增 `pyserial>=3.5`）
  - 扩展 profile 到 C1~C11，新增 C9(`-Og`)、C10(`-Oz`) 与 C11(`-O3 -flto` 纯优化参数) 编译条件
- **[benchmark_experiment]**: 新增可读版聚合报告（按现象分组 + 单图总览）
  - 新增 `benchmark_analysis/generate_readable_report.py`：输出 `report_readable.md`，包含每轮条件明细与现象分组合并
  - 输出 `benchmark_analysis/output/readable/overview_one_figure.png`（热力图 + 综合几何均值条形图）
  - 输出机器可读明细 `run_details.csv` 与 `phenomenon_groups.csv`
  - 在 `benchmark_analysis/full_matrix_common.py` 增加现象签名/分组函数并补充对应单元测试

### 变更
- **[benchmark_experiment]**: 默认实验矩阵移除 C11，统一为 C1~C10
  - `benchmark_analysis/full_matrix_common.py` 删除 `C11` profile 定义，默认矩阵更新为 `C1~C10`
  - `benchmark_analysis/run_full_matrix.py`、`benchmark_analysis/generate_full_matrix_report.py`、`benchmark_analysis/generate_readable_report.py` 默认 `--profiles` 同步改为 `C1~C10`
  - `tests/benchmark_analysis/test_full_matrix_common.py` 调整断言，验证默认矩阵不再包含 `C11`
  - `benchmark_analysis/README.md` 与 `PLAN.md` 的条件范围描述同步为 `C1~C10`
- **[benchmark_experiment]**: 报告生成支持“部分 profile 缺样本”容错
  - `benchmark_analysis/generate_full_matrix_report.py` 在非 strict 模式下自动跳过缺样本 profile 的跨条件分析与绘图
  - 报告正文新增“缺失样本（已跳过跨条件分析）”标注，避免因 `C1/C7` 等缺样本中断报告重生
- **[firmware_runtime]**: 调整运行入口到 `defaultTask -> app_main`
  - `Core/Src/main.c` 中 `StartDefaultTask` 由空转改为调用 `app_main()`
  - `Core/Src/main.c` 增加 `#include "app_main.h"`
- **[benchmark_experiment]**: 提升烧录后串口采样稳定性
  - `benchmark_analysis/run_full_matrix.py` 新增串口端口重连等待与 `/dev/ttyACM*` 自动探测
  - 打开串口后显式设置 `DTR/RTS` 并改进日志落盘，降低烧录后端口重枚举导致的采样失败
  - 串口超时语义调整为空闲超时（有持续数据则不会因总时长过长误判失败）
  - 流程完成后自动将 `report_full_matrix.md` 复制为 `report.md` 作为兼容完成标志
- **[benchmark_experiment]**: 优化全量报告可视化语义，避免 ratio 方向误读
  - 报告主口径统一为 `eigen/cmsis`，并以此生成统计字段与结论文本
  - speedup 图增加领先区域着色、对数轴与右侧 `cmsis/eigen` 副坐标
  - 新增跨 profile speedup 分布图：`mul_eigen_over_cmsis_box_by_profile.png`、`inv_eigen_over_cmsis_box_by_profile.png`
  - 修正分析文本中的小矩阵胜负判定逻辑，统一以 `eigen/cmsis>1 => CMSIS更快` 解释
  - `benchmark_analysis/README.md` 增补“可视化口径说明”
- **[benchmark_experiment]**: 合并同曲线 profile 的可视化展示
  - `benchmark_analysis/generate_full_matrix_report.py` 新增曲线签名分组，跨 profile 线图与箱线图自动合并同结果 profile
  - `report_full_matrix.md` 的“各编译条件结果”与“附录统计表”改为按合并组展示，减少重复图线与重复表格
  - 分组口径调整为 `eigen/cmsis` 曲线（含容差舍入），避免因 cycle 均值微小抖动导致“看起来相同却被拆组”
  - 图例采用 `C1/C2/...` 合并标签，减少重叠曲线并提升可读性
  - 为分组逻辑补充单元测试 `test_plot_grouping_merges_identical_curves`
- **[benchmark_experiment]**: 取消合并组展示，恢复按 profile 独立展示
  - `benchmark_analysis/generate_full_matrix_report.py` 的跨 profile 线图与箱线图改为每个 profile 单独一条，不再按同曲线自动合并
  - `report_full_matrix.md` 的第 4 章与第 8 章改为 `C1~C10` 逐 profile 展示，不再输出“合并组 Gx”
  - 同步更新 `report.md` 与 `benchmark_analysis/README.md` 的相关说明文字
- **[benchmark_experiment]**: full matrix 报告补充编译参数明细
  - `benchmark_analysis/generate_full_matrix_report.py` 在“工具链与环境信息”后新增“编译参数矩阵（实际执行口径）”
  - `report_full_matrix.md` / `report.md` 新增 C1~C10 的 `CFLAGS/CXXFLAGS/LDFLAGS/uses_lto` 对照表
- **[benchmark_experiment]**: 在 full matrix 结论新增“实验轮次优先级”建议
  - `benchmark_analysis/generate_full_matrix_report.py` 新增基于 `eigen/cmsis` 曲线差异的优先级计算（相对 C1 的 L1 差异 + 最近邻差异）
  - `report_full_matrix.md` / `report.md` 第 7 章新增“高信息量建议保留”与“可降权复测”清单及依据表
- **[firmware_runtime]**: 调整 `BENCHMARK_AUTORUN_FORCE` 启动窗口
  - `User/app_main.cpp` 在 force 模式下增加短暂 DTR 等待窗口，降低主机采样器错过首段输出的概率
- **[firmware_runtime]**: 打通 USB PCD 中断链路
  - `Core/Inc/stm32f4xx_it.h` 新增 `OTG_FS_IRQHandler(void)` 声明
  - `Core/Src/stm32f4xx_it.c` 新增 `OTG_FS_IRQHandler`，转发 `HAL_PCD_IRQHandler(&hpcd_USB_OTG_FS)`
  - `Core/Src/stm32f4xx_hal_msp.c` 在 `HAL_PCD_MspInit` 中开启 `OTG_FS_IRQn`
- **[third_party_stack]**: 接入 CMSIS-DSP 矩阵 F32 必要子集
  - `CMakeLists.txt` 增加 `Drivers/CMSIS/DSP/Include` 与 `arm_mat_init_f32.c / arm_mat_mult_f32.c / arm_mat_inverse_f32.c`
  - 增加宏定义 `ARM_MATH_LOOPUNROLL`
- **[build_toolchain]**: 新增二阶段性能构建开关
  - `CMakeLists.txt` 增加 `BENCHMARK_PERF_MODE`（默认 `OFF`）
  - 开关开启时为主目标及相关依赖追加 `-O3 -flto`
- **[third_party_stack]**: 固定 USB CDC 输出路径
  - `User/app_main.cpp` 固定 `USB_OTG_FS` + `STM32USBDeviceOtgFS` + `USB::CDCUart`
  - 描述符固定 `VID=0xCAFE`、`PID=0x4010`、产品名 `CMSIS-Eigen-Bench`
  - `User/libxr_config.yaml` 启用 `usb_otg_fs`

### 微调
- **[benchmark_experiment]**: 扩展实验设计到多编译条件性能对比
  - 类型: 微调（无方案包）
  - 文件: `PLAN.md:23`, `PLAN.md:54`, `PLAN.md:88`, `PLAN.md:136`
- **[benchmark_experiment]**: 增补编译条件 C6~C8（尺寸优先、禁循环展开、限制内联）
  - 类型: 微调（无方案包）
  - 文件: `PLAN.md:31`, `PLAN.md:58`, `PLAN.md:94`, `PLAN.md:143`
- **[build_toolchain]**: 补充本机工具链路径探测结果（cube-cmake/starm-clang/jlink）
  - 类型: 微调（无方案包）
  - 文件: `PLAN.md:40`
- **[build_toolchain]**: 修正工具链路径表（确认 cube-cmake/cube/starm-clang 实际安装路径）
  - 类型: 微调（无方案包）
  - 文件: `PLAN.md:44`

### 验收
- **[debug_closure]**: 已完成代码级闭环
  - 已完成：入口链路、USB CDC 通路、CMSIS/Eigen 双实现、DWT 测时、CSV 输出、误差/无效样本处理
  - 未完成：本环境缺少 `starm-clang`，尚未执行真实 Debug 构建与板级枚举/串口验收

## [0.1.0] - 2026-02-15

### 新增
- **[知识库]**: 初始化 HelloAGENTS 知识库，建立项目上下文、模块索引与归档索引
  - 类型: ~init 初始化（无方案包）
  - 文件: helloagents/INDEX.md, helloagents/context.md, helloagents/modules/_index.md, helloagents/archive/_index.md
