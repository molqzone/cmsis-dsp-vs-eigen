# build_toolchain

## 职责

维护工程构建系统、交叉编译工具链和关键编译参数，保证实验固件可在 STM32F407 平台稳定构建，并满足基准实验可比性要求。

## 接口定义（可选）

> 模块对外暴露的公共API和数据结构

### 公共API
| 函数/方法 | 参数 | 返回值 | 说明 |
|----------|------|--------|------|
| CMakePreset: Debug | 无 | 构建配置 | 使用 `starm-clang` 生成调试构建 |
| CMakePreset: Release | 无 | 构建配置 | 使用 `starm-clang` 生成发布构建 |
| starm-clang toolchain | 无 | 工具链配置 | 定义 `cortex-m4`、FPU、链接脚本等参数 |
| run_full_matrix.py tool options | `--cube-cmake`,`--cube`,`--toolchain-bin`,`--jlink` | 运行时路径绑定 | 绑定 VSCode Cube 工具链与 JLink 命令路径 |

### 数据结构
| 字段 | 类型 | 说明 |
|------|------|------|
| TARGET_FLAGS | `string` | 目标平台编译参数（CPU/FPU/ABI） |
| CMAKE_BUILD_TYPE | `string` | 当前构建类型（Debug/Release） |
| TOOLCHAIN_FILE | `path` | `cmake/starm-clang.cmake` |

## 行为规范

> 描述模块的核心行为和业务规则

### 构建配置选择
**条件**: 用户选择 Debug 或 Release 预设  
**行为**: 通过 `CMakePresets.json` 生成对应构建目录和缓存  
**结果**: 输出可编译的目标工程与 map 文件

### 平台编译约束
**条件**: 构建目标为 STM32F407 Cortex-M4F  
**行为**: 应用 `-mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=hard` 等工具链参数  
**结果**: 生成可在目标芯片运行的 ELF 映像

### 编译条件矩阵执行
**条件**: 触发全量实验流水线（C1~C10）  
**行为**: 每个 profile 使用独立构建目录 `build/bench_matrix/<C#>/build` 与 profile 专属 `CMAKE_*_FLAGS_RELEASE`  
**结果**: 保证不同编译条件相互隔离且可追溯，产物与日志按 profile 划分

## 依赖关系

```yaml
依赖:
  - third_party_stack
被依赖:
  - firmware_runtime
  - benchmark_experiment
```
