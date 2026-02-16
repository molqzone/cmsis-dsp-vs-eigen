#include "benchmark_math.hpp"

#include <cmath>
#include <cstddef>
#include <cstdint>

#include <Eigen/Dense>

namespace
{

template <int N>
void EigenMultiplyFixed(const float* a, const float* b, float* out)
{
  using MatrixType = Eigen::Matrix<float, N, N, Eigen::RowMajor>;
  const Eigen::Map<const MatrixType> matrix_a(a);
  const Eigen::Map<const MatrixType> matrix_b(b);
  Eigen::Map<MatrixType> matrix_out(out);
  matrix_out.noalias() = matrix_a * matrix_b;
}

void EigenMultiplyDynamic(std::size_t n, const float* a, const float* b, float* out)
{
  using DynamicMatrix = Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
  const Eigen::Map<const DynamicMatrix> matrix_a(a, static_cast<Eigen::Index>(n),
                                                  static_cast<Eigen::Index>(n));
  const Eigen::Map<const DynamicMatrix> matrix_b(b, static_cast<Eigen::Index>(n),
                                                  static_cast<Eigen::Index>(n));
  Eigen::Map<DynamicMatrix> matrix_out(out, static_cast<Eigen::Index>(n),
                                       static_cast<Eigen::Index>(n));
  matrix_out = matrix_a.lazyProduct(matrix_b);
}

template <int N>
void EigenInverseFixed(const float* src, float* out)
{
  using MatrixType = Eigen::Matrix<float, N, N, Eigen::RowMajor>;
  const Eigen::Map<const MatrixType> matrix_src(src);
  Eigen::Map<MatrixType> matrix_out(out);
  matrix_out = matrix_src.inverse();
}

}  // namespace

namespace BenchmarkMath
{

bool RunEigenMultiply(std::size_t n, const float* a, const float* b, float* out)
{
  switch (n)
  {
    case 3:
      EigenMultiplyFixed<3>(a, b, out);
      return true;
    case 4:
      EigenMultiplyFixed<4>(a, b, out);
      return true;
    case 6:
      EigenMultiplyFixed<6>(a, b, out);
      return true;
    case 8:
      EigenMultiplyFixed<8>(a, b, out);
      return true;
    case 10:
      EigenMultiplyFixed<10>(a, b, out);
      return true;
    case 16:
      EigenMultiplyFixed<16>(a, b, out);
      return true;
    case 32:
      EigenMultiplyFixed<32>(a, b, out);
      return true;
    case 64:
      EigenMultiplyDynamic(n, a, b, out);
      return true;
    default:
      return false;
  }
}

bool RunEigenInverse(std::size_t n, const float* src, float* out)
{
  switch (n)
  {
    case 3:
      EigenInverseFixed<3>(src, out);
      return true;
    case 4:
      EigenInverseFixed<4>(src, out);
      return true;
    case 6:
      EigenInverseFixed<6>(src, out);
      return true;
    case 8:
      EigenInverseFixed<8>(src, out);
      return true;
    case 10:
      EigenInverseFixed<10>(src, out);
      return true;
    default:
      return false;
  }
}

arm_status RunCmsisMultiply(std::size_t n, const float* a, const float* b, float* out)
{
  arm_matrix_instance_f32 matrix_a{};
  arm_matrix_instance_f32 matrix_b{};
  arm_matrix_instance_f32 matrix_out{};

  arm_mat_init_f32(&matrix_a, static_cast<std::uint16_t>(n), static_cast<std::uint16_t>(n),
                   const_cast<float*>(a));
  arm_mat_init_f32(&matrix_b, static_cast<std::uint16_t>(n), static_cast<std::uint16_t>(n),
                   const_cast<float*>(b));
  arm_mat_init_f32(&matrix_out, static_cast<std::uint16_t>(n),
                   static_cast<std::uint16_t>(n), out);

  return arm_mat_mult_f32(&matrix_a, &matrix_b, &matrix_out);
}

arm_status RunCmsisInverse(std::size_t n, float* src_mutable, float* out)
{
  arm_matrix_instance_f32 matrix_src{};
  arm_matrix_instance_f32 matrix_out{};

  arm_mat_init_f32(&matrix_src, static_cast<std::uint16_t>(n),
                   static_cast<std::uint16_t>(n), src_mutable);
  arm_mat_init_f32(&matrix_out, static_cast<std::uint16_t>(n),
                   static_cast<std::uint16_t>(n), out);

  return arm_mat_inverse_f32(&matrix_src, &matrix_out);
}

float ComputeFrobeniusError(std::size_t n, const float* lhs, const float* rhs)
{
  const std::size_t elements = n * n;
  double sum = 0.0;
  for (std::size_t i = 0; i < elements; ++i)
  {
    const double delta = static_cast<double>(lhs[i]) - static_cast<double>(rhs[i]);
    sum += delta * delta;
  }
  return static_cast<float>(std::sqrt(sum));
}

bool IsMatrixFinite(std::size_t n, const float* data)
{
  const std::size_t elements = n * n;
  for (std::size_t i = 0; i < elements; ++i)
  {
    if (!std::isfinite(data[i]))
    {
      return false;
    }
  }
  return true;
}

}  // namespace BenchmarkMath
