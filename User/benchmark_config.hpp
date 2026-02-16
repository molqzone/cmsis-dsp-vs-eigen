#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace BenchmarkConfig
{

inline constexpr std::array<std::size_t, 8> kMulSizes = {3, 4, 6, 8, 10, 16, 32, 64};
inline constexpr std::array<std::size_t, 5> kInvSizes = {3, 4, 6, 8, 10};

inline constexpr std::uint32_t kWarmup = 1;
inline constexpr std::uint32_t kRepeat = 100;
inline constexpr float kErrThreshold = 1e-4F;

inline constexpr std::size_t kMaxN = 64;
inline constexpr std::size_t kMaxElements = kMaxN * kMaxN;

}  // namespace BenchmarkConfig

