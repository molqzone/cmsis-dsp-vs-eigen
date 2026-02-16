# cmsis-dsp-vs-eigen 知识库

> 本文件是知识库的入口点

## 快速导航

| 需要了解 | 读取文件 |
|---------|---------|
| 项目概况、技术栈、开发约定 | [context.md](context.md) |
| 模块索引 | [modules/_index.md](modules/_index.md) |
| 基准实验设计模块 | [modules/benchmark_experiment.md](modules/benchmark_experiment.md) |
| 构建与工具链模块 | [modules/build_toolchain.md](modules/build_toolchain.md) |
| 固件运行时模块 | [modules/firmware_runtime.md](modules/firmware_runtime.md) |
| 第三方依赖栈模块 | [modules/third_party_stack.md](modules/third_party_stack.md) |
| 项目变更历史 | [CHANGELOG.md](CHANGELOG.md) |
| 历史方案索引 | [archive/_index.md](archive/_index.md) |
| 当前待执行的方案 | [plan/](plan/) |

## 知识库状态

```yaml
最后更新: 2026-02-15 21:15
模块数量: 4
待执行方案: 0
```

## 读取指引

```yaml
启动任务:
  1. 读取本文件获取导航
  2. 读取 context.md 获取项目上下文与实验目标
  3. 检查 plan/ 是否有进行中方案包

任务相关:
  - 调整实验方案: 读取 modules/benchmark_experiment.md
  - 调整编译选项: 读取 modules/build_toolchain.md
  - 调整固件入口与运行流程: 读取 modules/firmware_runtime.md
  - 调整第三方依赖接入: 读取 modules/third_party_stack.md
```
