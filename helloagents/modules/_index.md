# 模块索引

> 通过此文件快速定位模块文档

## 模块清单

| 模块 | 职责 | 状态 | 文档 |
|------|------|------|------|
| benchmark_experiment | 定义并维护 Eigen vs CMSIS-DSP 基准实验方法与验收口径 | 📝 | [benchmark_experiment.md](./benchmark_experiment.md) |
| build_toolchain | 维护 CMake、工具链与编译参数约束 | ✅ | [build_toolchain.md](./build_toolchain.md) |
| firmware_runtime | 管理固件入口、平台初始化与运行时流程 | 🚧 | [firmware_runtime.md](./firmware_runtime.md) |
| third_party_stack | 维护第三方依赖接入边界与版本来源 | ✅ | [third_party_stack.md](./third_party_stack.md) |

## 模块依赖关系

```text
benchmark_experiment → firmware_runtime
benchmark_experiment → third_party_stack
firmware_runtime → build_toolchain
firmware_runtime → third_party_stack
build_toolchain → third_party_stack
```

## 状态说明
- ✅ 稳定
- 🚧 开发中
- 📝 规划中

