#pragma once

#include <cstddef>
#include <cstdint>

namespace BenchmarkRng
{

class LcgRng
{
 public:
  explicit LcgRng(std::uint32_t seed) : state_(seed) {}

  std::uint32_t NextU32();
  float NextFloatSigned();

  void FillMatrix(float* dst, std::size_t n);
  void FillInvertibleMatrix(float* dst, std::size_t n);

 private:
  std::uint32_t state_;
};

}  // namespace BenchmarkRng

