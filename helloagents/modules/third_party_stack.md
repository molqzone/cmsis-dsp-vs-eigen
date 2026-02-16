# third_party_stack

## 职责

维护第三方依赖栈的来源、接入方式和边界，重点覆盖 CMSIS-DSP 矩阵 F32 子集、Eigen 定长矩阵计算、LibXR USB CDC 通道与 STM32 HAL/FreeRTOS 底座。

## 接口定义（可选）

> 模块对外暴露的公共API和数据结构

### 公共API
| 函数/方法 | 参数 | 返回值 | 说明 |
|----------|------|--------|------|
| arm_mat_init_f32 | `arm_matrix_instance_f32*`,`rows`,`cols`,`pData` | `void` | 初始化 CMSIS-DSP 矩阵对象 |
| arm_mat_mult_f32 | `arm_matrix_instance_f32*` | `arm_status` | CMSIS-DSP F32 矩阵乘法接口 |
| arm_mat_inverse_f32 | `arm_matrix_instance_f32*` | `arm_status` | CMSIS-DSP F32 矩阵求逆接口 |
| Eigen::Matrix | 模板参数 | 矩阵对象 | Eigen 定长/动态矩阵容器 |
| STM32USBDeviceOtgFS | USB 配置参数 | USB 设备对象 | LibXR 的 STM32 FS 设备封装 |
| USB::CDCUart | 缓冲区参数 | CDC 串口对象 | USB CDC 文本输出通道 |

### 数据结构
| 字段 | 类型 | 说明 |
|------|------|------|
| arm_matrix_instance_f32 | 结构体 | CMSIS-DSP 矩阵描述结构 |
| Eigen::Matrix<float, N, N, RowMajor> | 模板类型 | Eigen 行优先矩阵类型 |
| PCD_HandleTypeDef | HAL 结构体 | USB OTG FS 外设句柄 |
| FreeRTOS task control block | 内核结构 | 运行时任务调度结构 |

## 行为规范

> 描述模块的核心行为和业务规则

### 第三方源码集成
**条件**: 工程配置完成并执行 CMake 生成  
**行为**: `CMakeLists.txt` 将 CMSIS-DSP include 与 `arm_mat_init_f32.c / arm_mat_mult_f32.c / arm_mat_inverse_f32.c` 加入主目标；LibXR/Eigen 由既有工程配置接入  
**结果**: 依赖组件与应用代码共同链接为固件映像

### USB CDC 通道依赖
**条件**: 固件运行并初始化 USB 设备  
**行为**: HAL PCD + LibXR USB Device + CDCUart 共同建立 `USB_OTG_FS` 文本通路，`STDIO::write_` 绑定到 CDC 写端口  
**结果**: 基准结果通过 USB CDC 统一输出，不依赖 UART

### 性能构建开关
**条件**: `BENCHMARK_PERF_MODE=ON`  
**行为**: 对主目标及相关依赖追加 `-O3 -flto`  
**结果**: 为后续正式性能采样准备统一编译优化口径（当前 Debug 闭环默认关闭）

## 依赖关系

```yaml
依赖: []
被依赖:
  - build_toolchain
  - firmware_runtime
  - benchmark_experiment
```
