#pragma once

#include <cstddef>

#include "arm_math.h"

namespace BenchmarkMath
{

bool RunEigenMultiply(std::size_t n, const float* a, const float* b, float* out);
bool RunEigenInverse(std::size_t n, const float* src, float* out);

arm_status RunCmsisMultiply(std::size_t n, const float* a, const float* b, float* out);
arm_status RunCmsisInverse(std::size_t n, float* src_mutable, float* out);

float ComputeFrobeniusError(std::size_t n, const float* lhs, const float* rhs);
bool IsMatrixFinite(std::size_t n, const float* data);

}  // namespace BenchmarkMath

