# firmware_runtime

## 职责

管理固件入口、任务启动链路和运行时驻留行为，确保基准程序从 RTOS 默认任务稳定进入 `app_main()`，并通过 USB CDC 输出结果。

## 接口定义（可选）

> 模块对外暴露的公共API和数据结构

### 公共API
| 函数/方法 | 参数 | 返回值 | 说明 |
|----------|------|--------|------|
| StartDefaultTask | `void* argument` | `void` | FreeRTOS 默认任务入口，负责触发 `app_main()` |
| app_main | `void` | `void` | 应用主入口，完成平台初始化、USB CDC 就绪等待与基准执行 |
| PlatformInit | `priority`, `stack_depth` | `void` | 初始化平台运行环境（LibXR） |
| Thread::Sleep | `duration_ms` | `void` | 当前线程休眠，维持系统驻留 |

### 数据结构
| 字段 | 类型 | 说明 |
|------|------|------|
| hpcd_USB_OTG_FS | `PCD_HandleTypeDef` | USB FS PCD 句柄，供 USB 设备栈与中断处理复用 |
| htim1 | `TIM_HandleTypeDef` | 作为时间基准的硬件定时器句柄 |
| timebase | `STM32TimerTimebase` | LibXR 时间基准对象 |
| power_manager | `STM32PowerManager` | 电源管理对象 |

## 行为规范

> 描述模块的核心行为和业务规则

### 系统初始化
**条件**: 固件启动，调度器创建并运行 `defaultTask`  
**行为**: `StartDefaultTask` 调用 `app_main()`，`app_main` 内构建时间基准对象、执行 `PlatformInit(2, 1024)`、初始化电源管理对象  
**结果**: 运行时基础设施可用

### USB 基准执行入口
**条件**: USB OTG FS 设备启动后，主机端 CDC 串口已拉起 DTR  
**行为**: `app_main` 等待 `IsDtrSet()` 为真后，执行 `BenchmarkRunner::RunAllBenchmarks(build_mode)`  
**结果**: 通过 USB CDC 连续输出 CSV 数据，结束后输出 `done`

### 驻留策略
**条件**: 基准流程执行结束  
**行为**: `app_main` 进入 `while(true)` + `Thread::Sleep(UINT32_MAX)`；`StartDefaultTask` 仅保底循环，不承担业务  
**结果**: 避免线程退出导致不可控调度行为

## 依赖关系

```yaml
依赖:
  - build_toolchain
  - third_party_stack
被依赖:
  - benchmark_experiment
```
