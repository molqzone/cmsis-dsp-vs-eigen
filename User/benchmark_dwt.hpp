#pragma once

#include <cstdint>

#include "main.h"

namespace BenchmarkDwt
{

void InitDwtCycleCounter();
std::uint32_t MeasureTimerOverhead();

template <typename Func>
std::uint32_t MeasureCyclesCriticalSection(Func&& func)
{
  const std::uint32_t primask = __get_PRIMASK();
  __disable_irq();
  __DSB();
  __ISB();

  const std::uint32_t start = DWT->CYCCNT;
  func();
  const std::uint32_t end = DWT->CYCCNT;

  __DSB();
  __ISB();
  __set_PRIMASK(primask);
  return end - start;
}

}  // namespace BenchmarkDwt

