# 变更日志

## [Unreleased]

### 新增
- **[benchmark_experiment]**: 新增 Debug 闭环基准框架实现
  - 新增 `User/benchmark_config.hpp` 常量配置：`kMulSizes={3,4,6,8,10,16,32,64}`、`kInvSizes={3,4,6,8,10}`、`kWarmup=1`、`kRepeat=100`、`kErrThreshold=1e-4`
  - 新增 DWT 计时模块、LCG 随机输入模块、CMSIS/Eigen 计算封装模块、结果汇总与 CSV 输出模块
  - 输出口径固定为 `op,n,repeat,warmup,eigen_avg_cycles,cmsis_avg_cycles,cmsis_over_eigen,error_l2,valid,invalid,build_mode`

### 变更
- **[firmware_runtime]**: 调整运行入口到 `defaultTask -> app_main`
  - `Core/Src/main.c` 中 `StartDefaultTask` 由空转改为调用 `app_main()`
  - `Core/Src/main.c` 增加 `#include "app_main.h"`
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

### 验收
- **[debug_closure]**: 已完成代码级闭环
  - 已完成：入口链路、USB CDC 通路、CMSIS/Eigen 双实现、DWT 测时、CSV 输出、误差/无效样本处理
  - 未完成：本环境缺少 `starm-clang`，尚未执行真实 Debug 构建与板级枚举/串口验收

## [0.1.0] - 2026-02-15

### 新增
- **[知识库]**: 初始化 HelloAGENTS 知识库，建立项目上下文、模块索引与归档索引
  - 类型: ~init 初始化（无方案包）
  - 文件: helloagents/INDEX.md, helloagents/context.md, helloagents/modules/_index.md, helloagents/archive/_index.md
