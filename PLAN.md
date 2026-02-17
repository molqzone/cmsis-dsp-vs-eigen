# 实验设计报告：Eigen 与 CMSIS-DSP 在 Cortex-M4 平台下的矩阵运算性能基准测试

## 1. 实验目的

探究在资源受限的 Cortex-M4F 嵌入式平台上，现代 C++ 模板元编程库（Eigen）与 ARM 官方手写汇编优化库（CMSIS-DSP）在不同维度矩阵运算下的性能差异，找出两者的性能临界点（Crossover Point），为嵌入式算法选型提供数据支持。

## 2. 实验平台与环境 (Experimental Setup)

为了确保测试结果仅反映算法本身的效率，必须严格固定硬件和编译环境。

### 2.1 硬件环境

* **核心架构**：ARM Cortex-M4F (带单精度 FPU)
* **目标芯片**：STM32F407ZGT6
* **时钟配置**：
  * 系统时钟 (HCLK)：锁定最大频率 (如 168MHz/170MHz)，禁止动态调频。
  * Flash 等待周期 (Latency)：设置为该频率下的推荐值，开启预取指 (Prefetch) 和指令缓存 (I-Cache/D-Cache)。
* **运行介质**：核心测试代码放置于 `CCMRAM` (如有) 或 `SRAM` 中运行，以消除 Flash 取指不确定性的影响。

### 2.2 软件环境

* **编译器**：ST ARM Clang
* **编译条件矩阵**（新增，对每组条件分别编译并测试）：

| 条件编号 | 优化等级 | LTO | 浮点相关选项 | 其他选项 | 目的 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| C1（基线） | `-O3` | 开启 `-flto` | 默认 IEEE 行为 | `-DNDEBUG` | 对齐当前主流发布配置 |
| C2 | `-O2` | 开启 `-flto` | 默认 IEEE 行为 | `-DNDEBUG` | 评估较保守优化下的库差异 |
| C3 | `-O3` | 关闭 LTO | 默认 IEEE 行为 | `-DNDEBUG` | 评估跨编译单元优化对两库影响 |
| C4 | `-O3` | 开启 `-flto` | `-ffast-math` | `-DNDEBUG` | 评估激进浮点优化对性能/精度影响 |
| C5 | `-Ofast` | 开启 `-flto` | 隐含 fast-math 语义 | `-DNDEBUG` | 评估极限优化场景下的性能边界 |
| C6 | `-Os` | 开启 `-flto` | 默认 IEEE 行为 | `-DNDEBUG` | 评估代码尺寸优先策略对性能拐点影响 |
| C7 | `-O3` | 开启 `-flto` | 默认 IEEE 行为 | `-fno-unroll-loops -DNDEBUG` | 隔离循环展开对两库性能差异的贡献 |
| C8 | `-O3` | 开启 `-flto` | 默认 IEEE 行为 | `-fno-inline-functions-called-once -DNDEBUG` | 隔离函数内联策略对性能差异的贡献 |
| C9 | `-Og` | 开启 `-flto` | 默认 IEEE 行为 | `-g -DNDEBUG` | 观察调试友好优化等级对两库性能的影响 |
| C10 | `-Oz` | 开启 `-flto` | 默认 IEEE 行为 | `-DNDEBUG` | 观察极限尺寸优化策略对性能与拐点的影响 |

* *说明*：各条件下保持算法实现、输入数据、测试流程一致，仅改变编译参数。
* **FPU 设置**：`-mfloat-abi=hard -mfpu=fpv4-sp-d16` (强制生成 FPU 指令)
* **C++ 标准**：`-std=c++17`

### 2.3 本机工具链路径（2026-02-16 自动探测）

| 工具 | 命令可用性 | 路径（绝对路径） | 备注 |
| :--- | :--- | :--- | :--- |
| `cube-cmake` | 可用（未加入 PATH） | `/home/keruth/.vscode/extensions/stmicroelectronics.stm32cube-ide-build-cmake-1.43.0/resources/cube-cmake/linux/cube-cmake` | 由 STM32 VSCode 扩展提供 |
| `cube` | 可用（未加入 PATH） | `/home/keruth/.vscode/extensions/stmicroelectronics.stm32cube-ide-core-1.1.0/resources/binaries/linux/x86_64/cube` | 由 STM32 VSCode 扩展提供 |
| `starm-clang` | 可用（未加入 PATH） | `/home/keruth/.local/share/stm32cube/bundles/st-arm-clang/19.1.6+st.10/bin/starm-clang` | 检测到多个版本（含 `19.1.6+st.9`） |
| `jlink` | 小写命令未找到 | 未检出 | 本机以 SEGGER 大写命令提供 |
| SEGGER J-Link CLI | 可用 | `/usr/bin/JLinkExe` -> `/opt/SEGGER/JLink_V916a/JLinkExe` | `/usr/sbin/JLinkExe` 同样指向该目标 |
| SEGGER J-Link GDB Server | 可用 | `/usr/bin/JLinkGDBServerCLExe` -> `/opt/SEGGER/JLink_V916a/JLinkGDBServerCLExe` | `/usr/sbin/JLinkGDBServerCLExe` 同样指向该目标 |
| SEGGER J-Link RTT Client | 可用 | `/usr/bin/JLinkRTTClient` -> `/opt/SEGGER/JLink_V916a/JLinkRTTClientExe` | `/usr/sbin/JLinkRTTClient` 同样指向该目标 |

---

## 3. 实验变量设计 (Variables)

### 3.1 自变量 (Independent Variables)

1. **运算库 (Library)**：
    * **组 A (Eigen)**：使用 `Eigen::Matrix<float, N, N, RowMajor>` (定长、行优先)。
    * **组 B (CMSIS-DSP)**：使用 `arm_mat_mult_f32` 等标准 API。
2. **矩阵规模 (Matrix Size N)**：
    * **微型组**：3x3, 4x4 (典型姿态解算、机器人运动学场景)
    * **小型组**：6x6, 8x8, 10x10 (卡尔曼滤波、状态观测器场景)
    * **中型组**：16x16, 32x32 (部分信号处理、神经网络层)
    * **大型组**：64x64 (极限压力测试，考察缓存命中率)
3. **运算类型 (Operation)**：
    * 矩阵乘法 ($C = A \times B$)
    * 矩阵求逆 ($A^{-1}$，仅针对 $N \le 10$ 进行测试)
4. **编译条件 (Compile Profile C)**：
    * C1~C10（见 2.2 编译条件矩阵）
    * 对每个矩阵规模与运算类型，在全部编译条件下重复测试

### 3.2 因变量 (Dependent Variable)

* **执行耗时 (Execution Cycles)**：以 CPU 时钟周期数为单位。

---

## 4. 变量控制与干扰排除 (Control of Variables)

这是本实验最关键的部分，用于确保“公平竞争”。

| 控制项 | 控制策略 | 原因 |
| :--- | :--- | :--- |
| **内存分配** | **全静态分配 (Stack/BSS)** | 严禁在计时区间内使用 `malloc/new`。Eigen 必须使用 `Fixed Size` 模板参数，CMSIS-DSP 输入数组需预先定义。 |
| **数据布局** | **强制行优先 (Row-Major)** | CMSIS-DSP 默认为行优先。Eigen 默认为列优先，必须在定义类型时强制指定 `Eigen::RowMajor`，避免 Eigen 内部发生隐式转置带来的额外开销。 |
| **数据随机性** | **运行时伪随机填充** | 输入矩阵必须在运行时填充非零、非单位矩阵的伪随机浮点数。防止编译器进行“常量折叠”优化（直接算出结果），或算法库对特殊矩阵（如单位阵、零阵）走快速通道。 |
| **中断干扰** | **全局关中断 (`__disable_irq`)** | 在测试区间内彻底关闭中断，防止 SysTick 或其他外设中断打断流水线和测量计数。 |
| **缓存状态** | **热缓存 (Hot Cache)** | 每个测试运行 100 次，取平均值（或取中位数）。每次运算前先空跑一次（Warm-up），确保指令已加载至 I-Cache。 |
| **测量开销** | **扣除 DWT 读指令开销** | 测量单纯执行 `Start_Timer(); Stop_Timer();` 的耗时，并在最终结果中减去此 Base Overhead。 |
| **结果有效性** | **防优化桩 (Volatile Sink)** | 计算结果必须被“使用”（如打印校验和，或赋值给 volatile 变量），防止编译器判定为死代码（Dead Code）而将整个计算过程优化删除。 |

---

## 5. 实验流程 (Procedure)

### 阶段一：准备工作

1. 初始化 MCU 时钟、FPU、UART（用于输出结果）。
2. 开启 DWT (Data Watchpoint and Trace) 计数器。
3. 实现简易伪随机数生成器（LCG算法），避免使用标准库 `rand()` 的开销。

### 阶段二：基准测试循环 (针对每个 C、每个 N)

0. **构建与部署**：
    * 按条件 `C1~C10` 分别构建固件并烧录；
    * 记录编译产物大小（`.text/.rodata/.data/.bss`）用于后续关联分析；
    * 每次切换编译条件后执行一次系统重启与预热。

1. **数据准备**：
    * 生成两个 $N \times N$ 的源矩阵数据 $A_{data}, B_{data}$。
    * 将数据分别映射给 Eigen 对象和 CMSIS-DSP 结构体。
2. **CMSIS-DSP 测试**：
    * 关闭全局中断。
    * 重置并启动 DWT 计数器。
    * 执行 `arm_mat_mult_f32`。
    * 停止 DWT，读取计数值 $T_{cmsis}$。
    * 开启全局中断。
3. **Eigen 测试**：
    * 关闭全局中断。
    * 重置并启动 DWT 计数器。
    * 执行 `C.noalias() = A * B` (使用 `noalias()` 避免临时变量拷贝)。
    * 停止 DWT，读取计数值 $T_{eigen}$。
    * 开启全局中断。
4. **结果校验**：
    * 比较 Eigen 结果与 CMSIS-DSP 结果的欧几里得距离（误差范数）。
    * 若误差超过 `1e-4`，标记该次测试无效。
5. **循环**：
    * 在固定编译条件 C 下，上述步骤重复 100 次，记录所有数据；
    * 对全部 `C1~C10` 与全部 N 组合重复执行。

---

## 6. 数据记录与分析计划

### 6.1 数据表结构

| 编译条件 (C) | 矩阵大小 (N) | Eigen 平均周期 | CMSIS 平均周期 | 加速比 (CMSIS/Eigen) | 误差范数 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| C1 | 3x3 | ... | ... | > 1.0 表示 Eigen 快 | ... | |
| C1 | 4x4 | ... | ... | ... | ... | |
| C2 | 3x3 | ... | ... | ... | ... | |
| ... | ... | ... | ... | ... | ... | |

### 6.2 分析维度

1. **小矩阵优势区**：观察在 N=3, 4 时，Eigen 是否因为完全循环展开（Loop Unrolling）而显著快于 CMSIS-DSP。
2. **临界点识别**：寻找加速比曲线穿过 1.0 的 N 值。预测该点在 N=10~16 之间。
3. **大矩阵趋势**：观察 N > 30 时，CMSIS-DSP 的 SIMD 优化是否开始展现统治力。
4. **Flash 等待惩罚**：分析 Eigen 编译出的代码体积（Code Size）是否随 N 增大而剧烈膨胀，导致 Cache Miss 率上升从而拖累性能。
5. **编译条件敏感性**：比较 C1~C10 下的加速比曲线形态与临界点漂移，识别“对编译参数更敏感”的库。
6. **性能-精度权衡**：重点对比 C4/C5（fast-math 相关）与 C1 在性能提升和误差范数上的变化。
7. **展开策略影响**：对比 C7 与 C1，量化循环展开对小矩阵（N=3,4,6）与中矩阵（N=8,10,16）的影响。
8. **内联策略影响**：对比 C8 与 C1，量化函数内联变化对 Eigen 与 CMSIS-DSP 的相对收益差异。

## 7. 预期风险与对策

* **风险**：Eigen 模板展开导致编译出的二进制文件过大，Flash 放不下。
  * **对策**：仅测试关键尺寸，避免对大矩阵使用全展开模板，大矩阵可回退到 `Dynamic` 大小进行对比测试（注明变量变更）。
* **风险**：堆栈溢出 (Stack Overflow)。
  * **对策**：在链接脚本 (`.ld` 文件) 中增大 Stack Size，或者将大型测试矩阵定义为全局静态变量 (`static`)。
