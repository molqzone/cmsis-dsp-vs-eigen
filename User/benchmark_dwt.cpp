#include "benchmark_dwt.hpp"

#include <cstdint>

namespace
{
constexpr std::uint32_t kDwtUnlockKey = 0xC5ACCE55UL;
constexpr std::uint32_t kOverheadSamples = 64;
}  // namespace

namespace BenchmarkDwt
{

void InitDwtCycleCounter()
{
  CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
#if defined(DWT_LAR)
  DWT->LAR = kDwtUnlockKey;
#endif
  DWT->CYCCNT = 0;
  DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

std::uint32_t MeasureTimerOverhead()
{
  std::uint32_t min_delta = UINT32_MAX;
  for (std::uint32_t i = 0; i < kOverheadSamples; ++i)
  {
    __DSB();
    __ISB();
    const std::uint32_t start = DWT->CYCCNT;
    const std::uint32_t end = DWT->CYCCNT;
    const std::uint32_t delta = end - start;
    if (delta < min_delta)
    {
      min_delta = delta;
    }
  }

  return (min_delta == UINT32_MAX) ? 0U : min_delta;
}

}  // namespace BenchmarkDwt

