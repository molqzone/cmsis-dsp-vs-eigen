#include "benchmark_runner.hpp"

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>

#include "benchmark_config.hpp"
#include "benchmark_dwt.hpp"
#include "benchmark_math.hpp"
#include "benchmark_rng.hpp"
#include "libxr.hpp"

extern "C"
{
volatile std::uint32_t g_bench_progress_op = 0;    // 0=idle, 1=mul, 2=inv
volatile std::uint32_t g_bench_progress_n = 0;
volatile std::uint32_t g_bench_progress_line = 0;
volatile std::uint32_t g_bench_progress_done = 0;
}

namespace
{
using BenchmarkConfig::kErrThreshold;
using BenchmarkConfig::kInvSizes;
using BenchmarkConfig::kMaxElements;
using BenchmarkConfig::kMulSizes;
using BenchmarkConfig::kRepeat;
using BenchmarkConfig::kWarmup;

constexpr std::uint32_t kPow10[] = {1u,        10u,       100u,      1000u,
                                    10000u,   100000u,   1000000u,  10000000u,
                                    100000000u};

alignas(4) static float g_matrix_a[kMaxElements];
alignas(4) static float g_matrix_b[kMaxElements];
alignas(4) static float g_matrix_work[kMaxElements];
alignas(4) static float g_result_eigen[kMaxElements];
alignas(4) static float g_result_cmsis[kMaxElements];

struct BenchAggregate
{
  double eigen_cycles_sum = 0.0;
  double cmsis_cycles_sum = 0.0;
  double error_sum = 0.0;
  std::uint32_t valid = 0;
  std::uint32_t invalid = 0;
};

std::uint32_t StripOverhead(std::uint32_t cycles, std::uint32_t overhead)
{
  return (cycles > overhead) ? (cycles - overhead) : 0U;
}

bool WriteRaw(const char* data, std::size_t len)
{
  if (!LibXR::STDIO::write_ || !LibXR::STDIO::write_->Writable())
  {
    return false;
  }
  static LibXR::WriteOperation op;  // NOLINT
  const LibXR::ConstRawData raw{reinterpret_cast<const std::uint8_t*>(data), len};
  return (LibXR::STDIO::write_->operator()(raw, op) == LibXR::ErrorCode::OK);
}

void AppendChar(char* buf, std::size_t cap, std::size_t& idx, char c)
{
  if (idx + 1 >= cap)
  {
    return;
  }
  buf[idx++] = c;
}

void AppendCStr(char* buf, std::size_t cap, std::size_t& idx, const char* s)
{
  if (s == nullptr)
  {
    return;
  }
  while (*s != '\0' && idx + 1 < cap)
  {
    buf[idx++] = *s++;
  }
}

void AppendUInt(char* buf, std::size_t cap, std::size_t& idx, std::uint64_t v)
{
  char tmp[24];
  std::size_t n = 0;
  do
  {
    tmp[n++] = static_cast<char>('0' + (v % 10u));
    v /= 10u;
  } while (v != 0u && n < sizeof(tmp));

  while (n > 0 && idx + 1 < cap)
  {
    buf[idx++] = tmp[--n];
  }
}

void AppendFixed(char* buf, std::size_t cap, std::size_t& idx, double v,
                 std::uint32_t decimals)
{
  if (decimals >= (sizeof(kPow10) / sizeof(kPow10[0])))
  {
    decimals = static_cast<std::uint32_t>((sizeof(kPow10) / sizeof(kPow10[0])) - 1);
  }
  if (v < 0.0)
  {
    AppendChar(buf, cap, idx, '-');
    v = -v;
  }
  const std::uint64_t scale = kPow10[decimals];
  std::uint64_t int_part = static_cast<std::uint64_t>(v);
  double frac = v - static_cast<double>(int_part);
  std::uint64_t frac_part = static_cast<std::uint64_t>(std::llround(frac * scale));
  if (frac_part >= scale)
  {
    int_part += 1u;
    frac_part -= scale;
  }
  AppendUInt(buf, cap, idx, int_part);
  if (decimals == 0)
  {
    return;
  }
  AppendChar(buf, cap, idx, '.');
  std::uint64_t pad = scale / 10u;
  while (pad > 0 && frac_part < pad)
  {
    AppendChar(buf, cap, idx, '0');
    pad /= 10u;
  }
  AppendUInt(buf, cap, idx, frac_part);
}

void PrintCsvHeader()
{
  static const char kHeader[] =
      "op,n,repeat,warmup,eigen_avg_cycles,cmsis_avg_cycles,cmsis_over_eigen,error_l2,"
      "valid,invalid,build_mode\r\n";
  WriteRaw(kHeader, sizeof(kHeader) - 1);
}

void PrintAggregateLine(const char* op, std::size_t n, const BenchAggregate& agg,
                        const char* build_mode)
{
  const double denom = (agg.valid > 0U) ? static_cast<double>(agg.valid) : 1.0;
  const double eigen_avg = (agg.valid > 0U) ? (agg.eigen_cycles_sum / denom) : 0.0;
  const double cmsis_avg = (agg.valid > 0U) ? (agg.cmsis_cycles_sum / denom) : 0.0;
  const double ratio = (eigen_avg > 0.0) ? (cmsis_avg / eigen_avg) : 0.0;
  const double error_l2 = (agg.valid > 0U) ? (agg.error_sum / denom) : 0.0;

  char line[256];
  std::size_t idx = 0;
  AppendCStr(line, sizeof(line), idx, op);
  AppendChar(line, sizeof(line), idx, ',');
  AppendUInt(line, sizeof(line), idx, static_cast<std::uint64_t>(n));
  AppendChar(line, sizeof(line), idx, ',');
  AppendUInt(line, sizeof(line), idx, static_cast<std::uint64_t>(kRepeat));
  AppendChar(line, sizeof(line), idx, ',');
  AppendUInt(line, sizeof(line), idx, static_cast<std::uint64_t>(kWarmup));
  AppendChar(line, sizeof(line), idx, ',');
  AppendFixed(line, sizeof(line), idx, eigen_avg, 2);
  AppendChar(line, sizeof(line), idx, ',');
  AppendFixed(line, sizeof(line), idx, cmsis_avg, 2);
  AppendChar(line, sizeof(line), idx, ',');
  AppendFixed(line, sizeof(line), idx, ratio, 6);
  AppendChar(line, sizeof(line), idx, ',');
  AppendFixed(line, sizeof(line), idx, error_l2, 8);
  AppendChar(line, sizeof(line), idx, ',');
  AppendUInt(line, sizeof(line), idx, static_cast<std::uint64_t>(agg.valid));
  AppendChar(line, sizeof(line), idx, ',');
  AppendUInt(line, sizeof(line), idx, static_cast<std::uint64_t>(agg.invalid));
  AppendChar(line, sizeof(line), idx, ',');
  AppendCStr(line, sizeof(line), idx, build_mode);
  AppendChar(line, sizeof(line), idx, '\r');
  AppendChar(line, sizeof(line), idx, '\n');
  WriteRaw(line, idx);
}

BenchAggregate RunMultiplyForSize(std::size_t n, std::uint32_t timer_overhead,
                                  BenchmarkRng::LcgRng& rng)
{
  BenchAggregate aggregate{};
  const std::size_t bytes = n * n * sizeof(float);

  for (std::uint32_t warm = 0; warm < kWarmup; ++warm)
  {
    rng.FillMatrix(g_matrix_a, n);
    rng.FillMatrix(g_matrix_b, n);
    (void)BenchmarkMath::RunCmsisMultiply(n, g_matrix_a, g_matrix_b, g_result_cmsis);
    (void)BenchmarkMath::RunEigenMultiply(n, g_matrix_a, g_matrix_b, g_result_eigen);
  }

  for (std::uint32_t round = 0; round < kRepeat; ++round)
  {
    rng.FillMatrix(g_matrix_a, n);
    rng.FillMatrix(g_matrix_b, n);

    arm_status cmsis_status = ARM_MATH_SUCCESS;
    const std::uint32_t cmsis_cycles_raw = BenchmarkDwt::MeasureCyclesCriticalSection(
        [&]()
        {
          cmsis_status =
              BenchmarkMath::RunCmsisMultiply(n, g_matrix_a, g_matrix_b, g_result_cmsis);
        });

    bool eigen_ok = false;
    const std::uint32_t eigen_cycles_raw = BenchmarkDwt::MeasureCyclesCriticalSection(
        [&]()
        {
          eigen_ok =
              BenchmarkMath::RunEigenMultiply(n, g_matrix_a, g_matrix_b, g_result_eigen);
        });

    if (cmsis_status != ARM_MATH_SUCCESS || !eigen_ok)
    {
      aggregate.invalid++;
      continue;
    }

    if (!BenchmarkMath::IsMatrixFinite(n, g_result_cmsis) ||
        !BenchmarkMath::IsMatrixFinite(n, g_result_eigen))
    {
      aggregate.invalid++;
      continue;
    }

    const float error =
        BenchmarkMath::ComputeFrobeniusError(n, g_result_eigen, g_result_cmsis);
    if (error > kErrThreshold)
    {
      aggregate.invalid++;
      continue;
    }

    aggregate.valid++;
    aggregate.eigen_cycles_sum += StripOverhead(eigen_cycles_raw, timer_overhead);
    aggregate.cmsis_cycles_sum += StripOverhead(cmsis_cycles_raw, timer_overhead);
    aggregate.error_sum += static_cast<double>(error);
  }

  if (aggregate.valid + aggregate.invalid != kRepeat)
  {
    aggregate.invalid += (kRepeat - (aggregate.valid + aggregate.invalid));
  }

  (void)bytes;
  return aggregate;
}

BenchAggregate RunInverseForSize(std::size_t n, std::uint32_t timer_overhead,
                                 BenchmarkRng::LcgRng& rng)
{
  BenchAggregate aggregate{};
  const std::size_t bytes = n * n * sizeof(float);

  for (std::uint32_t warm = 0; warm < kWarmup; ++warm)
  {
    rng.FillInvertibleMatrix(g_matrix_a, n);
    std::memcpy(g_matrix_work, g_matrix_a, bytes);
    (void)BenchmarkMath::RunCmsisInverse(n, g_matrix_work, g_result_cmsis);
    (void)BenchmarkMath::RunEigenInverse(n, g_matrix_a, g_result_eigen);
  }

  for (std::uint32_t round = 0; round < kRepeat; ++round)
  {
    rng.FillInvertibleMatrix(g_matrix_a, n);
    std::memcpy(g_matrix_work, g_matrix_a, bytes);

    arm_status cmsis_status = ARM_MATH_SUCCESS;
    const std::uint32_t cmsis_cycles_raw = BenchmarkDwt::MeasureCyclesCriticalSection(
        [&]()
        {
          cmsis_status = BenchmarkMath::RunCmsisInverse(n, g_matrix_work, g_result_cmsis);
        });

    bool eigen_ok = false;
    const std::uint32_t eigen_cycles_raw = BenchmarkDwt::MeasureCyclesCriticalSection(
        [&]()
        { eigen_ok = BenchmarkMath::RunEigenInverse(n, g_matrix_a, g_result_eigen); });

    if (cmsis_status == ARM_MATH_SINGULAR || cmsis_status != ARM_MATH_SUCCESS ||
        !eigen_ok)
    {
      aggregate.invalid++;
      continue;
    }

    if (!BenchmarkMath::IsMatrixFinite(n, g_result_cmsis) ||
        !BenchmarkMath::IsMatrixFinite(n, g_result_eigen))
    {
      aggregate.invalid++;
      continue;
    }

    const float error =
        BenchmarkMath::ComputeFrobeniusError(n, g_result_eigen, g_result_cmsis);
    if (error > kErrThreshold)
    {
      aggregate.invalid++;
      continue;
    }

    aggregate.valid++;
    aggregate.eigen_cycles_sum += StripOverhead(eigen_cycles_raw, timer_overhead);
    aggregate.cmsis_cycles_sum += StripOverhead(cmsis_cycles_raw, timer_overhead);
    aggregate.error_sum += static_cast<double>(error);
  }

  if (aggregate.valid + aggregate.invalid != kRepeat)
  {
    aggregate.invalid += (kRepeat - (aggregate.valid + aggregate.invalid));
  }

  return aggregate;
}

}  // namespace

namespace BenchmarkRunner
{

void RunAllBenchmarks(const char* build_mode)
{
  g_bench_progress_op = 0;
  g_bench_progress_n = 0;
  g_bench_progress_line = 0;
  g_bench_progress_done = 0;

  BenchmarkDwt::InitDwtCycleCounter();
  const std::uint32_t timer_overhead = BenchmarkDwt::MeasureTimerOverhead();
  BenchmarkRng::LcgRng rng(0x12345678U);

  if (build_mode != nullptr && std::strcmp(build_mode, "Debug") == 0)
  {
    static const char kWarn[] =
        "WARNING: debug build, no formal performance conclusion\r\n";
    WriteRaw(kWarn, sizeof(kWarn) - 1);
  }

  PrintCsvHeader();

  for (std::size_t n : kMulSizes)
  {
    g_bench_progress_op = 1;
    g_bench_progress_n = static_cast<std::uint32_t>(n);
    const BenchAggregate aggregate = RunMultiplyForSize(n, timer_overhead, rng);
    PrintAggregateLine("mul", n, aggregate, build_mode);
    g_bench_progress_line++;
  }

  for (std::size_t n : kInvSizes)
  {
    g_bench_progress_op = 2;
    g_bench_progress_n = static_cast<std::uint32_t>(n);
    const BenchAggregate aggregate = RunInverseForSize(n, timer_overhead, rng);
    PrintAggregateLine("inv", n, aggregate, build_mode);
    g_bench_progress_line++;
  }

  g_bench_progress_done = 1;
  static const char kDone[] = "done\r\n";
  WriteRaw(kDone, sizeof(kDone) - 1);
}

}  // namespace BenchmarkRunner
