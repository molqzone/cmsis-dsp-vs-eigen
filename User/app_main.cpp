#include "app_main.h"

#include <cstdint>

#include "benchmark_runner.hpp"
#include "cdc_uart.hpp"
#include "cmsis_os2.h"
#include "libxr.hpp"
#include "main.h"
#include "stm32_timebase.hpp"
#include "stm32_usb_dev.hpp"

extern "C"
{
#include "FreeRTOSConfig.h"
}

using namespace LibXR;

extern PCD_HandleTypeDef hpcd_USB_OTG_FS;
extern TIM_HandleTypeDef htim1;

namespace
{
constexpr auto kLangEnUs = USB::DescriptorStrings::MakeLanguagePack(
    USB::DescriptorStrings::Language::EN_US, "XRobot",
    "CMSIS-Eigen-Bench", "CMSIS-Eigen-");

constexpr std::uint16_t kUsbVid = 0xCAFE;
constexpr std::uint16_t kUsbPid = 0x4010;
constexpr std::uint16_t kUsbBcd = 0x0100;

STM32USBDeviceOtgFS* g_usb_device = nullptr;

USB::CDCUart& InitUsbCdc()
{
  alignas(4) static std::uint8_t usb_fs_ep0_out_buffer[8];
  alignas(4) static std::uint8_t usb_fs_ep1_out_buffer[128];
  alignas(4) static std::uint8_t usb_fs_ep0_in_buffer[8];
  alignas(4) static std::uint8_t usb_fs_ep1_in_buffer[128];
  alignas(4) static std::uint8_t usb_fs_ep2_in_buffer[16];

  static USB::CDCUart cdc_uart(128, 128, 3);

  static STM32USBDeviceOtgFS usb_device(
      &hpcd_USB_OTG_FS, 256,
      {
          RawData(usb_fs_ep0_out_buffer, sizeof(usb_fs_ep0_out_buffer)),
          RawData(usb_fs_ep1_out_buffer, sizeof(usb_fs_ep1_out_buffer)),
      },
      {
          STM32USBDeviceOtgFS::EPInConfig{
              RawData(usb_fs_ep0_in_buffer, sizeof(usb_fs_ep0_in_buffer)), 8},
          STM32USBDeviceOtgFS::EPInConfig{
              RawData(usb_fs_ep1_in_buffer, sizeof(usb_fs_ep1_in_buffer)), 128},
          STM32USBDeviceOtgFS::EPInConfig{
              RawData(usb_fs_ep2_in_buffer, sizeof(usb_fs_ep2_in_buffer)), 16},
      },
      USB::DeviceDescriptor::PacketSize0::SIZE_8, kUsbVid, kUsbPid, kUsbBcd,
      {&kLangEnUs}, {{&cdc_uart}}, {reinterpret_cast<void*>(UID_BASE), 12});

  usb_device.Init(false);
  usb_device.Start(false);
  g_usb_device = &usb_device;
  STDIO::read_ = cdc_uart.read_port_;
  STDIO::write_ = cdc_uart.write_port_;
  return cdc_uart;
}

void ForceUsbReconnect()
{
  if (g_usb_device == nullptr)
  {
    return;
  }
  g_usb_device->Stop(false);
  osDelay(100);
  g_usb_device->Start(false);
}

const char* GetBuildMode()
{
#if defined(NDEBUG)
  return "Release";
#else
  return "Debug";
#endif
}
}  // namespace

extern "C"
{
__attribute__((aligned(8))) uint8_t ucHeap[configTOTAL_HEAP_SIZE];
}

extern "C" void app_main(void)
{
  STM32TimerTimebase timebase(&htim1);
  PlatformInit(2, 1024);
  USB::CDCUart& cdc_uart = InitUsbCdc();

  ForceUsbReconnect();

#if defined(BENCHMARK_AUTORUN)
  osDelay(200);
#if defined(BENCHMARK_AUTORUN_FORCE)
  // Give host-side serial collector time to reopen after flashing/reset.
  for (int wait_tick = 0; wait_tick < 300; ++wait_tick)
  {
    if (cdc_uart.IsDtrSet())
    {
      break;
    }
    osDelay(10);
  }
  STDIO::Printf("autorun-force\n");
#else
  while (!cdc_uart.IsDtrSet())
  {
    osDelay(10);
  }
  STDIO::Printf("autorun-start\n");
#endif
  int runs = 10;
#if defined(BENCHMARK_AUTORUN_COUNT)
  runs = BENCHMARK_AUTORUN_COUNT;
#endif
  for (int run = 0; run < runs; ++run)
  {
    BenchmarkRunner::RunAllBenchmarks(GetBuildMode());
    osDelay(200);
  }
#else
  while (!cdc_uart.IsDtrSet())
  {
    osDelay(10);
  }
  osDelay(200);

  BenchmarkRunner::RunAllBenchmarks(GetBuildMode());
#endif

  while (1)
  {
    osDelay(1000);
  }
}
