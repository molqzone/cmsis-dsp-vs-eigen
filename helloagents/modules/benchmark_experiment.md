# benchmark_experiment

## 职责

维护本项目在 Cortex-M4F 平台上的矩阵基准执行口径与实现细节，确保 Eigen 与 CMSIS-DSP 对比具备可运行、可输出、可校验的 Debug 闭环。

## 接口定义（可选）

> 模块对外暴露的公共API和数据结构

### 公共API
| 函数/方法 | 参数 | 返回值 | 说明 |
|----------|------|--------|------|
| BenchmarkRunner::RunAllBenchmarks | `build_mode` | `void` | 固定顺序执行乘法全尺寸与求逆子集并输出 CSV |
| benchmark_analysis/run_full_matrix.py | `--profiles`,`--runs`,`--resume` 等 | `exit code` | 一键执行 C1~C10 构建/烧录/采样并触发报告生成 |
| benchmark_analysis/generate_full_matrix_report.py | `--input-root`,`--output-md`,`--strict` | `exit code` | 聚合 C1~C10 样本并生成 `report_full_matrix.md` |
| BenchmarkDwt::InitDwtCycleCounter | `void` | `void` | 初始化 DWT 周期计数器 |
| BenchmarkDwt::MeasureTimerOverhead | `void` | `uint32_t` | 采样计时本底开销 |
| BenchmarkDwt::MeasureCyclesCriticalSection | `lambda` | `uint32_t` | PRIMASK 保护下测量单次运算周期 |
| BenchmarkMath::ComputeFrobeniusError | `n`,`lhs`,`rhs` | `float` | 计算 `sqrt(sum((A-B)^2))` |

### 数据结构
| 字段 | 类型 | 说明 |
|------|------|------|
| kMulSizes | `std::array<size_t,8>` | 固定乘法维度：3/4/6/8/10/16/32/64 |
| kInvSizes | `std::array<size_t,5>` | 固定求逆维度：3/4/6/8/10 |
| BenchAggregate | 结构体 | 记录 cycles/error 累计、valid/invalid 计数 |
| LcgRng | 类 | 固定 LCG（`state = state * 1664525 + 1013904223`）输入生成器 |

## 行为规范

> 描述模块的核心行为和业务规则

### 矩阵乘法基准
**条件**: `n ∈ {3,4,6,8,10,16,32,64}`，`warmup=1`，`repeat=100`  
**行为**: 每轮填充随机矩阵后分别调用 CMSIS 与 Eigen；计时区间仅包裹被测函数；扣除计时开销；按 Frobenius 误差阈值 `1e-4` 判定有效性  
**结果**: 输出每个维度一行 CSV，且 `valid + invalid = 100`

### 矩阵求逆基准
**条件**: `n ∈ {3,4,6,8,10}`，输入矩阵采用“随机 + 对角增强（+N）”  
**行为**: CMSIS 返回 `ARM_MATH_SINGULAR` 计入 `invalid` 并继续后续轮次；其余状态与误差超阈值同样记为无效  
**结果**: 固定输出 5 行求逆 CSV，不因单次失败中断整轮

### 输出口径
**条件**: USB CDC 已连通且主机端 DTR 已置位  
**行为**: 先打印 Debug 警示，再打印 CSV 表头与数据行，最后打印 `done`  
**结果**: 形成可直接采集的统一文本结果流

### 全量矩阵自动化
**条件**: `build/bench_matrix/<C#>/` 尚未完整或用户指定 `--resume`  
**行为**: 对 C1~C10 执行构建→JLink 烧录→串口采样，单 profile 失败即中止并保留日志；全部成功后生成 `report_full_matrix.md` 并同步 `report.md`  
**结果**: 每个 profile 产出 `run_*.csv`、`profile_meta.json`、日志与图表，支持断点续跑

### 串口重连与握手稳定性
**条件**: 烧录后 CDC 设备节点短暂消失或重枚举  
**行为**: 采样脚本对 `/dev/ttyACM*` 做重试探测，打开端口后设置 DTR/RTS；板端 force 模式启动前等待短暂 DTR 窗口  
**结果**: 降低首段样本丢失和“端口不存在”导致的失败率

输出表头固定为：
`op,n,repeat,warmup,eigen_avg_cycles,cmsis_avg_cycles,cmsis_over_eigen,error_l2,valid,invalid,build_mode`

Debug 模式固定警示：
`WARNING: debug build, no formal performance conclusion`

## 依赖关系

```yaml
依赖:
  - firmware_runtime
  - third_party_stack
被依赖:
  - 无（当前作为业务核心模块）
```
