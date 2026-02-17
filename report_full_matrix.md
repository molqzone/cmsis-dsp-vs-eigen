# 全量基准实验报告（C1~C10）

## 1. 关联计划与实验矩阵
- 计划文件：`/home/keruth/Projects/cmsis-dsp-vs-eigen/PLAN.md`
- 覆盖 profile：`C1, C2, C3, C4, C5, C6, C7, C8, C9, C10`
- 采样 run 数（按 profile）：`[('C1', 3), ('C10', 3), ('C2', 3), ('C3', 3), ('C4', 3), ('C5', 3), ('C6', 3), ('C7', 3), ('C8', 3), ('C9', 3)]`
- build_mode：`Release`
- repeat 范围：`100 ~ 100`

## 2. 工具链与环境信息
- 生成时间：`2026-02-17T16:54:57.891711+00:00`
- cube_cmake: `/home/keruth/.vscode/extensions/stmicroelectronics.stm32cube-ide-build-cmake-1.43.0/resources/cube-cmake/linux/cube-cmake`
- cube: `/home/keruth/.vscode/extensions/stmicroelectronics.stm32cube-ide-core-1.1.0/resources/binaries/linux/x86_64/cube`
- starm_clang: `/home/keruth/.local/share/stm32cube/bundles/st-arm-clang/19.1.6+st.10/bin/starm-clang`
- jlink: `/opt/SEGGER/JLink_V916a/JLinkExe`

## 2.1 编译参数矩阵（实际执行口径）
| profile | CFLAGS | CXXFLAGS | LDFLAGS | uses_lto |
|---|---|---|---|---|
| C1 | `-g0 -O3 -flto -DNDEBUG` | `-g0 -O3 -flto -DNDEBUG` | `-flto -Wl,--undefined=vTaskSwitchContext` | `True` |
| C2 | `-g0 -O2 -flto -DNDEBUG` | `-g0 -O2 -flto -DNDEBUG` | `-flto -Wl,--undefined=vTaskSwitchContext` | `True` |
| C3 | `-g0 -O3 -DNDEBUG` | `-g0 -O3 -DNDEBUG` | `-Wl,--undefined=vTaskSwitchContext` | `False` |
| C4 | `-g0 -O3 -flto -ffast-math -DNDEBUG` | `-g0 -O3 -flto -ffast-math -DNDEBUG` | `-flto -Wl,--undefined=vTaskSwitchContext` | `True` |
| C5 | `-g0 -Ofast -flto -DNDEBUG` | `-g0 -Ofast -flto -DNDEBUG` | `-flto -Wl,--undefined=vTaskSwitchContext` | `True` |
| C6 | `-g0 -Os -flto -DNDEBUG` | `-g0 -Os -flto -DNDEBUG` | `-flto -Wl,--undefined=vTaskSwitchContext` | `True` |
| C7 | `-g0 -O3 -flto -fno-unroll-loops -DNDEBUG` | `-g0 -O3 -flto -fno-unroll-loops -DNDEBUG` | `-flto -Wl,--undefined=vTaskSwitchContext` | `True` |
| C8 | `-g0 -O3 -flto -fno-inline-functions-called-once -DNDEBUG` | `-g0 -O3 -flto -fno-inline-functions-called-once -DNDEBUG` | `-flto -Wl,--undefined=vTaskSwitchContext` | `True` |
| C9 | `-g -Og -flto -DNDEBUG` | `-g -Og -flto -DNDEBUG` | `-flto -Wl,--undefined=vTaskSwitchContext` | `True` |
| C10 | `-g0 -Oz -flto -DNDEBUG` | `-g0 -Oz -flto -DNDEBUG` | `-flto -Wl,--undefined=vTaskSwitchContext` | `True` |

## 3. 数据完整性与口径校验
- `C1`: mul=[3, 4, 6, 8, 10, 16, 32, 64], inv=[3, 4, 6, 8, 10], expected_mul=[3, 4, 6, 8, 10, 16, 32, 64], expected_inv=[3, 4, 6, 8, 10]
- `C2`: mul=[3, 4, 6, 8, 10, 16, 32, 64], inv=[3, 4, 6, 8, 10], expected_mul=[3, 4, 6, 8, 10, 16, 32, 64], expected_inv=[3, 4, 6, 8, 10]
- `C3`: mul=[3, 4, 6, 8, 10, 16, 32, 64], inv=[3, 4, 6, 8, 10], expected_mul=[3, 4, 6, 8, 10, 16, 32, 64], expected_inv=[3, 4, 6, 8, 10]
- `C4`: mul=[3, 4, 6, 8, 10, 16, 32, 64], inv=[3, 4, 6, 8, 10], expected_mul=[3, 4, 6, 8, 10, 16, 32, 64], expected_inv=[3, 4, 6, 8, 10]
- `C5`: mul=[3, 4, 6, 8, 10, 16, 32, 64], inv=[3, 4, 6, 8, 10], expected_mul=[3, 4, 6, 8, 10, 16, 32, 64], expected_inv=[3, 4, 6, 8, 10]
- `C6`: mul=[3, 4, 6, 8, 10, 16, 32, 64], inv=[3, 4, 6, 8, 10], expected_mul=[3, 4, 6, 8, 10, 16, 32, 64], expected_inv=[3, 4, 6, 8, 10]
- `C7`: mul=[3, 4, 6, 8, 10, 16, 32, 64], inv=[3, 4, 6, 8, 10], expected_mul=[3, 4, 6, 8, 10, 16, 32, 64], expected_inv=[3, 4, 6, 8, 10]
- `C8`: mul=[3, 4, 6, 8, 10, 16, 32, 64], inv=[3, 4, 6, 8, 10], expected_mul=[3, 4, 6, 8, 10, 16, 32, 64], expected_inv=[3, 4, 6, 8, 10]
- `C9`: mul=[3, 4, 6, 8, 10, 16, 32, 64], inv=[3, 4, 6, 8, 10], expected_mul=[3, 4, 6, 8, 10, 16, 32, 64], expected_inv=[3, 4, 6, 8, 10]
- `C10`: mul=[3, 4, 6, 8, 10, 16, 32, 64], inv=[3, 4, 6, 8, 10], expected_mul=[3, 4, 6, 8, 10, 16, 32, 64], expected_inv=[3, 4, 6, 8, 10]

## 4. 各编译条件结果（图表）

- 图表口径：`speedup = Eigen / CMSIS`，`speedup > 1` 表示 CMSIS 更快，`speedup < 1` 表示 Eigen 更快。
- 右侧副轴展示 `CMSIS/Eigen`，与板端原始字段 `cmsis_over_eigen` 对齐。
- 各 profile 独立展示，不做曲线合并。

### 4.1 C1
![C1_mul_cycles](benchmark_analysis/output/full_matrix/C1_mul_cycles.png)
![C1_inv_cycles](benchmark_analysis/output/full_matrix/C1_inv_cycles.png)
![C1_mul_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C1_mul_eigen_over_cmsis.png)
![C1_inv_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C1_inv_eigen_over_cmsis.png)

### 4.2 C2
![C2_mul_cycles](benchmark_analysis/output/full_matrix/C2_mul_cycles.png)
![C2_inv_cycles](benchmark_analysis/output/full_matrix/C2_inv_cycles.png)
![C2_mul_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C2_mul_eigen_over_cmsis.png)
![C2_inv_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C2_inv_eigen_over_cmsis.png)

### 4.3 C3
![C3_mul_cycles](benchmark_analysis/output/full_matrix/C3_mul_cycles.png)
![C3_inv_cycles](benchmark_analysis/output/full_matrix/C3_inv_cycles.png)
![C3_mul_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C3_mul_eigen_over_cmsis.png)
![C3_inv_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C3_inv_eigen_over_cmsis.png)

### 4.4 C4
![C4_mul_cycles](benchmark_analysis/output/full_matrix/C4_mul_cycles.png)
![C4_inv_cycles](benchmark_analysis/output/full_matrix/C4_inv_cycles.png)
![C4_mul_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C4_mul_eigen_over_cmsis.png)
![C4_inv_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C4_inv_eigen_over_cmsis.png)

### 4.5 C5
![C5_mul_cycles](benchmark_analysis/output/full_matrix/C5_mul_cycles.png)
![C5_inv_cycles](benchmark_analysis/output/full_matrix/C5_inv_cycles.png)
![C5_mul_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C5_mul_eigen_over_cmsis.png)
![C5_inv_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C5_inv_eigen_over_cmsis.png)

### 4.6 C6
![C6_mul_cycles](benchmark_analysis/output/full_matrix/C6_mul_cycles.png)
![C6_inv_cycles](benchmark_analysis/output/full_matrix/C6_inv_cycles.png)
![C6_mul_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C6_mul_eigen_over_cmsis.png)
![C6_inv_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C6_inv_eigen_over_cmsis.png)

### 4.7 C7
![C7_mul_cycles](benchmark_analysis/output/full_matrix/C7_mul_cycles.png)
![C7_inv_cycles](benchmark_analysis/output/full_matrix/C7_inv_cycles.png)
![C7_mul_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C7_mul_eigen_over_cmsis.png)
![C7_inv_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C7_inv_eigen_over_cmsis.png)

### 4.8 C8
![C8_mul_cycles](benchmark_analysis/output/full_matrix/C8_mul_cycles.png)
![C8_inv_cycles](benchmark_analysis/output/full_matrix/C8_inv_cycles.png)
![C8_mul_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C8_mul_eigen_over_cmsis.png)
![C8_inv_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C8_inv_eigen_over_cmsis.png)

### 4.9 C9
![C9_mul_cycles](benchmark_analysis/output/full_matrix/C9_mul_cycles.png)
![C9_inv_cycles](benchmark_analysis/output/full_matrix/C9_inv_cycles.png)
![C9_mul_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C9_mul_eigen_over_cmsis.png)
![C9_inv_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C9_inv_eigen_over_cmsis.png)

### 4.10 C10
![C10_mul_cycles](benchmark_analysis/output/full_matrix/C10_mul_cycles.png)
![C10_inv_cycles](benchmark_analysis/output/full_matrix/C10_inv_cycles.png)
![C10_mul_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C10_mul_eigen_over_cmsis.png)
![C10_inv_eigen_over_cmsis](benchmark_analysis/output/full_matrix/C10_inv_eigen_over_cmsis.png)

### 4.x 跨条件 speedup 曲线（Eigen/CMSIS）
- 图中每条线对应一个 profile，不做自动合并。
![mul_eigen_over_cmsis_by_profile](benchmark_analysis/output/full_matrix/mul_eigen_over_cmsis_by_profile.png)
![inv_eigen_over_cmsis_by_profile](benchmark_analysis/output/full_matrix/inv_eigen_over_cmsis_by_profile.png)
![mul_eigen_over_cmsis_box_by_profile](benchmark_analysis/output/full_matrix/mul_eigen_over_cmsis_box_by_profile.png)
![inv_eigen_over_cmsis_box_by_profile](benchmark_analysis/output/full_matrix/inv_eigen_over_cmsis_box_by_profile.png)

## 5. 跨条件分析（对齐 PLAN.md）

### 5.1 小矩阵优势区（N=3,4）
- `C1`: mul@3=0.526, mul@4=0.336 -> Eigen 更快
- `C2`: mul@3=0.351, mul@4=0.321 -> Eigen 更快
- `C3`: mul@3=0.484, mul@4=0.443 -> Eigen 更快
- `C4`: mul@3=0.564, mul@4=0.344 -> Eigen 更快
- `C5`: mul@3=0.564, mul@4=0.344 -> Eigen 更快
- `C6`: mul@3=0.363, mul@4=0.354 -> Eigen 更快
- `C7`: mul@3=0.417, mul@4=0.354 -> Eigen 更快
- `C8`: mul@3=0.526, mul@4=0.336 -> Eigen 更快
- `C9`: mul@3=0.416, mul@4=0.540 -> Eigen 更快
- `C10`: mul@3=1.005, mul@4=0.996 -> 各有胜负

### 5.2 临界点识别（eigen/cmsis 穿越 1.0）
- `C1`: mul 临界点=3, inv 临界点=3
- `C2`: mul 临界点=3, inv 临界点=3
- `C3`: mul 临界点=3, inv 临界点=3
- `C4`: mul 临界点=3, inv 临界点=3
- `C5`: mul 临界点=3, inv 临界点=3
- `C6`: mul 临界点=3, inv 临界点=3
- `C7`: mul 临界点=3, inv 临界点=3
- `C8`: mul 临界点=3, inv 临界点=3
- `C9`: mul 临界点=3, inv 临界点=3
- `C10`: mul 临界点=4, inv 临界点=3

### 5.3 大矩阵趋势（mul, N>=32）
- `C1`: 平均 eigen/cmsis=1.012，对应 cmsis/eigen=0.989
- `C2`: 平均 eigen/cmsis=1.037，对应 cmsis/eigen=0.965
- `C3`: 平均 eigen/cmsis=1.005，对应 cmsis/eigen=0.997
- `C4`: 平均 eigen/cmsis=0.876，对应 cmsis/eigen=1.144
- `C5`: 平均 eigen/cmsis=0.876，对应 cmsis/eigen=1.144
- `C6`: 平均 eigen/cmsis=1.162，对应 cmsis/eigen=0.930
- `C7`: 平均 eigen/cmsis=1.075，对应 cmsis/eigen=0.972
- `C8`: 平均 eigen/cmsis=1.012，对应 cmsis/eigen=0.989
- `C9`: 平均 eigen/cmsis=1.288，对应 cmsis/eigen=0.835
- `C10`: 平均 eigen/cmsis=1.274，对应 cmsis/eigen=0.819

### 5.4 编译条件敏感性（C1~C10）
- 全点位 eigen/cmsis 标准差均值：`0.1096`（值越大表示对编译条件越敏感）

### 5.5 性能-精度权衡（C4/C5 vs C1）
- `C4` 相比 `C1`: eigen/cmsis 变化 `-2.73%`，error 变化 `-21.15%`
- `C5` 相比 `C1`: eigen/cmsis 变化 `-2.73%`，error 变化 `-21.15%`

### 5.6 展开策略影响（C7 vs C1）
- mul@3: C1=0.526, C7=0.417, 差值=-0.108
- mul@4: C1=0.336, C7=0.354, 差值=+0.018
- mul@6: C1=0.345, C7=0.452, 差值=+0.107
- mul@8: C1=1.618, C7=1.472, 差值=-0.146
- mul@10: C1=1.497, C7=1.336, 差值=-0.160
- mul@16: C1=1.147, C7=1.055, 差值=-0.092

### 5.7 内联策略影响（C8 vs C1）
- mul@3: C1=0.526, C8=0.526, 差值=+0.000
- mul@4: C1=0.336, C8=0.336, 差值=-0.000
- mul@6: C1=0.345, C8=0.345, 差值=-0.000
- mul@8: C1=1.618, C8=1.618, 差值=+0.000
- mul@10: C1=1.497, C8=1.497, 差值=+0.000
- mul@16: C1=1.147, C8=1.147, 差值=+0.000

## 6. 代码体积/Flash 惩罚（.text/.rodata/.data/.bss）
| profile | .text | .rodata | .data | .bss |
|---|---:|---:|---:|---:|
| C1 | 110720 | 864 | 8 | 112920 |
| C2 | 98244 | 864 | 8 | 112940 |
| C3 | 93956 | 1968 | 36 | 112944 |
| C4 | 108692 | 864 | 8 | 112920 |
| C5 | 108692 | 864 | 8 | 112920 |
| C6 | 55080 | 872 | 8 | 112940 |
| C7 | 64720 | 872 | 8 | 112920 |
| C8 | 110720 | 864 | 8 | 112920 |
| C9 | 65448 | 1132 | 40 | 112948 |
| C10 | 46012 | 880 | 8 | 112920 |

## 7. 结论与建议配置
- 基线 C1 的 mul 临界点：`3`。
- 建议优先使用 C1 作为默认发布配置，再按目标矩阵规模选择 C4/C5/C7/C8 做定向优化。

### 7.1 实验轮次优先级（C1~C10）
- 高信息量（建议默认保留）：`C1, C3, C4, C7, C9, C10`
- 可降权/按需复测：`C2, C5, C6, C8`
- 依据口径：`eigen/cmsis` 全点位曲线相对 C1 的平均绝对差（L1），并结合编译策略覆盖面。

| profile | mean_abs_curve_diff_vs_C1 | nearest_profile | nearest_diff |
|---|---:|---|---:|
| C1 | 0.000000 | C1 | 0.000000 |
| C2 | 0.043712 | C8 | 0.043709 |
| C3 | 0.054754 | C1 | 0.054754 |
| C4 | 0.065370 | C5 | 0.000006 |
| C5 | 0.065369 | C4 | 0.000006 |
| C6 | 0.152913 | C7 | 0.029486 |
| C7 | 0.134398 | C6 | 0.029486 |
| C8 | 0.000003 | C1 | 0.000003 |
| C9 | 0.143528 | C6 | 0.095036 |
| C10 | 0.206822 | C9 | 0.148043 |

## 8. 附录：全量统计表（按 profile）
### 8.1 C1 mul
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 185.94 | 0.00 | ±0.02 | 353.83 | 0.00 | ±0.00 | 0.526 | 0.00000 | ±0.000 | Eigen | 0.00000007 |
| 4 | 356.90 | 0.00 | ±0.04 | 1062.80 | 0.00 | ±0.00 | 0.336 | 0.00000 | ±0.000 | Eigen | 0.00000011 |
| 6 | 1013.89 | 0.00 | ±0.06 | 2935.92 | 0.02 | ±0.16 | 0.345 | 0.00000 | ±0.000 | Eigen | 0.00000030 |
| 8 | 9362.87 | 0.00 | ±0.00 | 5787.98 | 0.00 | ±0.00 | 1.618 | 0.00000 | ±0.000 | CMSIS | 0.00000054 |
| 10 | 16369.93 | 0.00 | ±0.00 | 10936.98 | 0.00 | ±0.00 | 1.497 | 0.00000 | ±0.000 | CMSIS | 0.00000064 |
| 16 | 44312.93 | 0.00 | ±0.00 | 38635.98 | 0.00 | ±0.00 | 1.147 | 0.00000 | ±0.000 | CMSIS | 0.00000203 |
| 32 | 266131.93 | 0.00 | ±0.00 | 254848.98 | 0.00 | ±0.00 | 1.044 | 0.00000 | ±0.000 | CMSIS | 0.00000767 |
| 64 | 1864669.96 | 0.00 | ±0.02 | 1902238.00 | 0.00 | ±0.00 | 0.980 | 0.00000 | ±0.000 | Eigen | 0.00000000 |

### 8.1 C1 inv
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 193.76 | 0.00 | ±0.00 | 1584.83 | 0.00 | ±0.00 | 0.122 | 0.00000 | ±0.000 | Eigen | 0.00000004 |
| 4 | 763.00 | 0.00 | ±0.00 | 2913.96 | 0.01 | ±0.08 | 0.262 | 0.00000 | ±0.000 | Eigen | 0.00000005 |
| 6 | 13634.95 | 0.00 | ±0.00 | 7622.00 | 0.00 | ±0.00 | 1.789 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 8 | 23776.95 | 0.00 | ±0.00 | 14469.00 | 0.00 | ±0.00 | 1.643 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 10 | 40707.53 | 0.00 | ±0.00 | 26211.00 | 0.00 | ±0.00 | 1.553 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |

### 8.2 C2 mul
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 214.83 | 0.00 | ±0.00 | 611.68 | 0.00 | ±0.00 | 0.351 | 0.00000 | ±0.000 | Eigen | 0.00000007 |
| 4 | 369.89 | 0.00 | ±0.05 | 1152.70 | 0.00 | ±0.00 | 0.321 | 0.00000 | ±0.000 | Eigen | 0.00000011 |
| 6 | 1023.91 | 0.00 | ±0.03 | 3092.88 | 0.03 | ±0.20 | 0.331 | 0.00000 | ±0.000 | Eigen | 0.00000030 |
| 8 | 9379.84 | 0.00 | ±0.00 | 6122.98 | 0.00 | ±0.00 | 1.532 | 0.00000 | ±0.000 | CMSIS | 0.00000054 |
| 10 | 16336.93 | 0.00 | ±0.00 | 11354.98 | 0.00 | ±0.00 | 1.439 | 0.00000 | ±0.000 | CMSIS | 0.00000064 |
| 16 | 44432.92 | 0.00 | ±0.02 | 39964.98 | 0.00 | ±0.00 | 1.112 | 0.00000 | ±0.000 | CMSIS | 0.00000203 |
| 32 | 266538.93 | 0.00 | ±0.00 | 262112.98 | 0.00 | ±0.00 | 1.017 | 0.00000 | ±0.000 | CMSIS | 0.00000767 |
| 64 | 2040880.99 | 0.00 | ±0.01 | 1931103.00 | 0.00 | ±0.00 | 1.057 | 0.00000 | ±0.000 | CMSIS | 0.00000000 |

### 8.2 C2 inv
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 209.62 | 0.00 | ±0.05 | 1584.91 | 0.02 | ±0.17 | 0.132 | 0.00000 | ±0.000 | Eigen | 0.00000004 |
| 4 | 765.83 | 0.00 | ±0.01 | 2927.95 | 0.00 | ±0.05 | 0.262 | 0.00000 | ±0.000 | Eigen | 0.00000005 |
| 6 | 13946.95 | 0.00 | ±0.00 | 7680.00 | 0.00 | ±0.00 | 1.816 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 8 | 24064.95 | 0.00 | ±0.00 | 14824.00 | 0.00 | ±0.00 | 1.623 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 10 | 41017.31 | 0.00 | ±0.00 | 26835.00 | 0.00 | ±0.00 | 1.529 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |

### 8.3 C3 mul
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 280.87 | 0.00 | ±0.01 | 580.71 | 0.00 | ±0.01 | 0.484 | 0.00000 | ±0.000 | Eigen | 0.00000007 |
| 4 | 497.00 | 0.00 | ±0.00 | 1120.74 | 0.00 | ±0.00 | 0.443 | 0.00000 | ±0.000 | Eigen | 0.00000011 |
| 6 | 1255.96 | 0.00 | ±0.02 | 2916.83 | 0.02 | ±0.16 | 0.431 | 0.00000 | ±0.000 | Eigen | 0.00000030 |
| 8 | 8918.83 | 0.00 | ±0.00 | 5745.98 | 0.00 | ±0.00 | 1.552 | 0.00000 | ±0.000 | CMSIS | 0.00000054 |
| 10 | 15897.96 | 0.00 | ±0.00 | 10721.98 | 0.00 | ±0.00 | 1.483 | 0.00000 | ±0.000 | CMSIS | 0.00000064 |
| 16 | 42131.95 | 0.00 | ±0.01 | 35671.98 | 0.00 | ±0.00 | 1.181 | 0.00000 | ±0.000 | CMSIS | 0.00000203 |
| 32 | 246227.96 | 0.00 | ±0.00 | 255991.98 | 0.00 | ±0.00 | 0.962 | 0.00000 | ±0.000 | Eigen | 0.00000767 |
| 64 | 2032349.00 | 0.00 | ±0.00 | 1939254.00 | 0.00 | ±0.00 | 1.048 | 0.00000 | ±0.000 | CMSIS | 0.00000000 |

### 8.3 C3 inv
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 153.03 | 0.00 | ±0.00 | 1636.93 | 0.01 | ±0.08 | 0.093 | 0.00000 | ±0.000 | Eigen | 0.00000004 |
| 4 | 889.00 | 0.00 | ±0.00 | 2838.86 | 0.00 | ±0.01 | 0.313 | 0.00000 | ±0.000 | Eigen | 0.00000005 |
| 6 | 13396.00 | 0.00 | ±0.00 | 7273.00 | 0.00 | ±0.00 | 1.842 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 8 | 22100.46 | 0.00 | ±0.04 | 14017.00 | 0.00 | ±0.00 | 1.577 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 10 | 38580.79 | 0.00 | ±0.03 | 25061.00 | 0.00 | ±0.00 | 1.539 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |

### 8.4 C4 mul
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 188.93 | 0.00 | ±0.02 | 334.81 | 0.00 | ±0.00 | 0.564 | 0.00000 | ±0.000 | Eigen | 0.00000000 |
| 4 | 346.91 | 0.00 | ±0.00 | 1009.80 | 0.00 | ±0.00 | 0.344 | 0.00000 | ±0.000 | Eigen | 0.00000000 |
| 6 | 940.88 | 0.00 | ±0.00 | 2821.77 | 0.00 | ±0.01 | 0.333 | 0.00000 | ±0.000 | Eigen | 0.00000000 |
| 8 | 8169.87 | 0.00 | ±0.00 | 5590.98 | 0.00 | ±0.00 | 1.461 | 0.00000 | ±0.000 | CMSIS | 0.00000054 |
| 10 | 14696.93 | 0.00 | ±0.00 | 10630.98 | 0.00 | ±0.00 | 1.382 | 0.00000 | ±0.000 | CMSIS | 0.00000064 |
| 16 | 38198.93 | 0.00 | ±0.00 | 38115.98 | 0.00 | ±0.00 | 1.002 | 0.00000 | ±0.000 | CMSIS | 0.00000203 |
| 32 | 229621.93 | 0.00 | ±0.00 | 272243.98 | 0.00 | ±0.00 | 0.843 | 0.00000 | ±0.000 | Eigen | 0.00000767 |
| 64 | 1864672.98 | 0.00 | ±0.00 | 2053778.00 | 0.00 | ±0.00 | 0.908 | 0.00000 | ±0.000 | Eigen | 0.00000000 |

### 8.4 C4 inv
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 196.76 | 0.00 | ±0.00 | 1551.76 | 0.00 | ±0.00 | 0.127 | 0.00000 | ±0.000 | Eigen | 0.00000005 |
| 4 | 751.00 | 0.00 | ±0.00 | 2652.86 | 0.06 | ±0.27 | 0.283 | 0.00000 | ±0.000 | Eigen | 0.00000005 |
| 6 | 13032.95 | 0.00 | ±0.00 | 7147.00 | 0.00 | ±0.00 | 1.824 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 8 | 22284.56 | 0.00 | ±0.00 | 13319.00 | 0.00 | ±0.00 | 1.673 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 10 | 37957.65 | 0.00 | ±0.00 | 24639.00 | 0.00 | ±0.00 | 1.541 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |

### 8.5 C5 mul
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 188.92 | 0.00 | ±0.00 | 334.81 | 0.00 | ±0.00 | 0.564 | 0.00000 | ±0.000 | Eigen | 0.00000000 |
| 4 | 346.94 | 0.00 | ±0.06 | 1009.80 | 0.00 | ±0.00 | 0.344 | 0.00000 | ±0.000 | Eigen | 0.00000000 |
| 6 | 940.96 | 0.00 | ±0.08 | 2821.93 | 0.02 | ±0.14 | 0.333 | 0.00000 | ±0.000 | Eigen | 0.00000000 |
| 8 | 8169.87 | 0.00 | ±0.00 | 5590.98 | 0.00 | ±0.00 | 1.461 | 0.00000 | ±0.000 | CMSIS | 0.00000054 |
| 10 | 14696.93 | 0.00 | ±0.00 | 10630.98 | 0.00 | ±0.00 | 1.382 | 0.00000 | ±0.000 | CMSIS | 0.00000064 |
| 16 | 38198.93 | 0.00 | ±0.00 | 38115.98 | 0.00 | ±0.00 | 1.002 | 0.00000 | ±0.000 | CMSIS | 0.00000203 |
| 32 | 229621.93 | 0.00 | ±0.00 | 272243.98 | 0.00 | ±0.00 | 0.843 | 0.00000 | ±0.000 | Eigen | 0.00000767 |
| 64 | 1864672.97 | 0.00 | ±0.02 | 2053778.00 | 0.00 | ±0.00 | 0.908 | 0.00000 | ±0.000 | Eigen | 0.00000000 |

### 8.5 C5 inv
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 196.76 | 0.00 | ±0.00 | 1551.79 | 0.00 | ±0.06 | 0.127 | 0.00000 | ±0.000 | Eigen | 0.00000005 |
| 4 | 751.00 | 0.00 | ±0.00 | 2652.84 | 0.08 | ±0.32 | 0.283 | 0.00000 | ±0.000 | Eigen | 0.00000005 |
| 6 | 13032.95 | 0.00 | ±0.00 | 7147.00 | 0.00 | ±0.00 | 1.824 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 8 | 22284.56 | 0.00 | ±0.00 | 13319.00 | 0.00 | ±0.00 | 1.673 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 10 | 37957.65 | 0.00 | ±0.00 | 24639.00 | 0.00 | ±0.00 | 1.541 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |

### 8.6 C6 mul
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 196.93 | 0.00 | ±0.00 | 541.88 | 0.00 | ±0.00 | 0.363 | 0.00000 | ±0.000 | Eigen | 0.00000007 |
| 4 | 347.95 | 0.00 | ±0.05 | 983.89 | 0.00 | ±0.00 | 0.354 | 0.00000 | ±0.000 | Eigen | 0.00000011 |
| 6 | 1355.85 | 0.00 | ±0.05 | 2801.96 | 0.01 | ±0.08 | 0.484 | 0.00000 | ±0.000 | Eigen | 0.00000030 |
| 8 | 8548.79 | 0.00 | ±0.00 | 5718.98 | 0.00 | ±0.00 | 1.495 | 0.00000 | ±0.000 | CMSIS | 0.00000054 |
| 10 | 14629.85 | 0.00 | ±0.01 | 10849.98 | 0.00 | ±0.00 | 1.348 | 0.00000 | ±0.000 | CMSIS | 0.00000064 |
| 16 | 42139.88 | 0.00 | ±0.00 | 39782.98 | 0.00 | ±0.00 | 1.059 | 0.00000 | ±0.000 | CMSIS | 0.00000203 |
| 32 | 251453.95 | 0.00 | ±0.00 | 297605.00 | 0.00 | ±0.00 | 0.845 | 0.00000 | ±0.000 | Eigen | 0.00000767 |
| 64 | 3408694.76 | 0.00 | ±0.00 | 2303172.82 | 0.00 | ±0.00 | 1.480 | 0.00000 | ±0.000 | CMSIS | 0.00000000 |

### 8.6 C6 inv
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 205.02 | 0.00 | ±0.02 | 1297.81 | 0.03 | ±0.18 | 0.158 | 0.00000 | ±0.000 | Eigen | 0.00000004 |
| 4 | 763.97 | 0.00 | ±0.03 | 2489.88 | 0.01 | ±0.12 | 0.307 | 0.00000 | ±0.000 | Eigen | 0.00000005 |
| 6 | 11144.24 | 0.00 | ±0.03 | 6716.00 | 0.00 | ±0.00 | 1.659 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 8 | 20362.95 | 0.00 | ±0.01 | 14138.00 | 0.00 | ±0.00 | 1.440 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 10 | 34745.40 | 0.00 | ±0.01 | 25644.00 | 0.00 | ±0.00 | 1.355 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |

### 8.7 C7 mul
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 193.97 | 0.00 | ±0.01 | 465.00 | 0.00 | ±0.00 | 0.417 | 0.00000 | ±0.000 | Eigen | 0.00000007 |
| 4 | 360.88 | 0.00 | ±0.04 | 1019.00 | 0.00 | ±0.00 | 0.354 | 0.00000 | ±0.000 | Eigen | 0.00000011 |
| 6 | 1350.68 | 0.00 | ±0.01 | 2987.00 | 0.00 | ±0.00 | 0.452 | 0.00000 | ±0.000 | Eigen | 0.00000030 |
| 8 | 8881.63 | 0.00 | ±0.00 | 6035.00 | 0.00 | ±0.00 | 1.472 | 0.00000 | ±0.000 | CMSIS | 0.00000054 |
| 10 | 15549.87 | 0.00 | ±0.00 | 11635.00 | 0.00 | ±0.00 | 1.336 | 0.00000 | ±0.000 | CMSIS | 0.00000064 |
| 16 | 44311.74 | 0.00 | ±0.04 | 41987.00 | 0.00 | ±0.00 | 1.055 | 0.00000 | ±0.000 | CMSIS | 0.00000203 |
| 32 | 267995.98 | 0.00 | ±0.00 | 314339.00 | 0.00 | ±0.00 | 0.853 | 0.00000 | ±0.000 | Eigen | 0.00000767 |
| 64 | 3158826.91 | 0.00 | ±0.00 | 2434979.00 | 0.00 | ±0.00 | 1.297 | 0.00000 | ±0.000 | CMSIS | 0.00000000 |

### 8.7 C7 inv
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 191.99 | 0.00 | ±0.02 | 1381.66 | 0.00 | ±0.00 | 0.139 | 0.00000 | ±0.000 | Eigen | 0.00000004 |
| 4 | 763.97 | 0.00 | ±0.03 | 2612.95 | 0.01 | ±0.10 | 0.292 | 0.00000 | ±0.000 | Eigen | 0.00000005 |
| 6 | 11405.27 | 0.00 | ±0.01 | 6943.98 | 0.00 | ±0.00 | 1.642 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 8 | 20676.47 | 0.59 | ±0.87 | 14506.98 | 0.00 | ±0.00 | 1.425 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 10 | 35556.71 | 0.00 | ±0.01 | 26189.98 | 0.00 | ±0.00 | 1.358 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |

### 8.8 C8 mul
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 185.94 | 0.00 | ±0.02 | 353.83 | 0.00 | ±0.00 | 0.526 | 0.00000 | ±0.000 | Eigen | 0.00000007 |
| 4 | 356.87 | 0.00 | ±0.03 | 1062.80 | 0.00 | ±0.00 | 0.336 | 0.00000 | ±0.000 | Eigen | 0.00000011 |
| 6 | 1013.88 | 0.00 | ±0.06 | 2935.92 | 0.02 | ±0.16 | 0.345 | 0.00000 | ±0.000 | Eigen | 0.00000030 |
| 8 | 9362.87 | 0.00 | ±0.00 | 5787.98 | 0.00 | ±0.00 | 1.618 | 0.00000 | ±0.000 | CMSIS | 0.00000054 |
| 10 | 16369.93 | 0.00 | ±0.00 | 10936.98 | 0.00 | ±0.00 | 1.497 | 0.00000 | ±0.000 | CMSIS | 0.00000064 |
| 16 | 44312.93 | 0.00 | ±0.00 | 38635.98 | 0.00 | ±0.00 | 1.147 | 0.00000 | ±0.000 | CMSIS | 0.00000203 |
| 32 | 266131.93 | 0.00 | ±0.00 | 254848.98 | 0.00 | ±0.00 | 1.044 | 0.00000 | ±0.000 | CMSIS | 0.00000767 |
| 64 | 1864669.97 | 0.00 | ±0.02 | 1902238.00 | 0.00 | ±0.00 | 0.980 | 0.00000 | ±0.000 | Eigen | 0.00000000 |

### 8.8 C8 inv
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 193.76 | 0.00 | ±0.00 | 1584.83 | 0.00 | ±0.00 | 0.122 | 0.00000 | ±0.000 | Eigen | 0.00000004 |
| 4 | 763.00 | 0.00 | ±0.00 | 2913.97 | 0.00 | ±0.07 | 0.262 | 0.00000 | ±0.000 | Eigen | 0.00000005 |
| 6 | 13634.95 | 0.00 | ±0.00 | 7622.00 | 0.00 | ±0.00 | 1.789 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 8 | 23776.95 | 0.00 | ±0.00 | 14469.00 | 0.00 | ±0.00 | 1.643 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 10 | 40707.53 | 0.00 | ±0.00 | 26211.00 | 0.00 | ±0.00 | 1.553 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |

### 8.9 C9 mul
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 281.83 | 0.01 | ±0.10 | 677.79 | 0.02 | ±0.15 | 0.416 | 0.00000 | ±0.000 | Eigen | 0.00000007 |
| 4 | 545.96 | 0.00 | ±0.00 | 1010.90 | 0.01 | ±0.12 | 0.540 | 0.00000 | ±0.000 | Eigen | 0.00000011 |
| 6 | 1692.84 | 0.00 | ±0.01 | 2911.90 | 0.01 | ±0.08 | 0.581 | 0.00000 | ±0.000 | Eigen | 0.00000030 |
| 8 | 8975.90 | 0.00 | ±0.06 | 5382.98 | 0.00 | ±0.00 | 1.667 | 0.00000 | ±0.000 | CMSIS | 0.00000054 |
| 10 | 15788.90 | 0.00 | ±0.06 | 10766.98 | 0.00 | ±0.00 | 1.466 | 0.00000 | ±0.000 | CMSIS | 0.00000064 |
| 16 | 43557.93 | 0.00 | ±0.06 | 36582.98 | 0.00 | ±0.00 | 1.191 | 0.00000 | ±0.000 | CMSIS | 0.00000203 |
| 32 | 257396.96 | 0.00 | ±0.00 | 272166.98 | 0.00 | ±0.00 | 0.946 | 0.00000 | ±0.000 | Eigen | 0.00000767 |
| 64 | 3429076.00 | 0.00 | ±0.00 | 2102693.00 | 0.00 | ±0.00 | 1.631 | 0.00000 | ±0.000 | CMSIS | 0.00000000 |

### 8.9 C9 inv
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 153.03 | 0.00 | ±0.00 | 1553.50 | 0.00 | ±0.00 | 0.099 | 0.00000 | ±0.000 | Eigen | 0.00000004 |
| 4 | 878.93 | 0.00 | ±0.03 | 2820.85 | 0.02 | ±0.16 | 0.312 | 0.00000 | ±0.000 | Eigen | 0.00000005 |
| 6 | 12530.92 | 0.00 | ±0.01 | 7242.00 | 0.00 | ±0.00 | 1.730 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 8 | 21771.38 | 0.00 | ±0.03 | 14919.00 | 0.00 | ±0.00 | 1.459 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 10 | 38136.70 | 0.00 | ±0.03 | 26740.00 | 0.00 | ±0.00 | 1.426 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |

### 8.10 C10 mul
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 570.76 | 0.00 | ±0.01 | 567.83 | 0.00 | ±0.00 | 1.005 | 0.00000 | ±0.000 | CMSIS | 0.00000007 |
| 4 | 977.98 | 0.00 | ±0.00 | 981.88 | 0.01 | ±0.12 | 0.996 | 0.00000 | ±0.000 | Eigen | 0.00000011 |
| 6 | 1425.91 | 0.00 | ±0.07 | 2792.94 | 0.01 | ±0.12 | 0.511 | 0.00000 | ±0.000 | Eigen | 0.00000030 |
| 8 | 9872.99 | 0.00 | ±0.01 | 5698.00 | 0.00 | ±0.00 | 1.733 | 0.00000 | ±0.000 | CMSIS | 0.00000054 |
| 10 | 16654.90 | 0.00 | ±0.00 | 10825.00 | 0.00 | ±0.00 | 1.539 | 0.00000 | ±0.000 | CMSIS | 0.00000064 |
| 16 | 49646.98 | 0.00 | ±0.00 | 39226.00 | 0.00 | ±0.00 | 1.266 | 0.00000 | ±0.000 | CMSIS | 0.00000203 |
| 32 | 295745.00 | 0.00 | ±0.00 | 291370.00 | 0.00 | ±0.00 | 1.015 | 0.00000 | ±0.000 | CMSIS | 0.00000767 |
| 64 | 3441821.74 | 0.00 | ±0.00 | 2245641.86 | 0.00 | ±0.00 | 1.533 | 0.00000 | ±0.000 | CMSIS | 0.00000000 |

### 8.10 C10 inv
| n | eigen_mean | eigen_var | eigen_95%CI | cmsis_mean | cmsis_var | cmsis_95%CI | eigen_over_cmsis_mean | eigen_over_cmsis_var | eigen_over_cmsis_95%CI | leader | error_mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 3 | 202.01 | 0.00 | ±0.03 | 1309.73 | 0.00 | ±0.00 | 0.154 | 0.00000 | ±0.000 | Eigen | 0.00000004 |
| 4 | 791.97 | 0.00 | ±0.03 | 2541.87 | 0.01 | ±0.13 | 0.312 | 0.00000 | ±0.000 | Eigen | 0.00000005 |
| 6 | 14108.01 | 0.00 | ±0.00 | 7063.99 | 0.00 | ±0.00 | 1.997 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 8 | 23600.01 | 0.00 | ±0.01 | 15229.99 | 0.00 | ±0.00 | 1.550 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
| 10 | 39662.00 | 0.00 | ±0.01 | 28119.99 | 0.00 | ±0.00 | 1.410 | 0.00000 | ±0.000 | CMSIS | 0.00000002 |
