#include "benchmark_rng.hpp"

#include <cstddef>
#include <cstdint>

namespace
{
constexpr std::uint32_t kLcgMultiplier = 1664525U;
constexpr std::uint32_t kLcgIncrement = 1013904223U;
constexpr float kU24Scale = 1.0F / 16777216.0F;
}  // namespace

namespace BenchmarkRng
{

std::uint32_t LcgRng::NextU32()
{
  state_ = state_ * kLcgMultiplier + kLcgIncrement;
  return state_;
}

float LcgRng::NextFloatSigned()
{
  const std::uint32_t u24 = (NextU32() >> 8U) & 0x00FFFFFFU;
  const float unit = static_cast<float>(u24) * kU24Scale;
  return (unit * 2.0F) - 1.0F;
}

void LcgRng::FillMatrix(float* dst, std::size_t n)
{
  const std::size_t elements = n * n;
  for (std::size_t i = 0; i < elements; ++i)
  {
    dst[i] = NextFloatSigned();
  }
}

void LcgRng::FillInvertibleMatrix(float* dst, std::size_t n)
{
  FillMatrix(dst, n);
  for (std::size_t row = 0; row < n; ++row)
  {
    dst[row * n + row] += static_cast<float>(n);
  }
}

}  // namespace BenchmarkRng

