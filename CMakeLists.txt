cmake_minimum_required(VERSION 3.22)

#
# This file is generated only once,
# and is not re-generated if converter is called multiple times.
#
# User is free to modify the file as much as necessary
#

# Setup compiler settings
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS ON)


# Define the build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Debug")
endif()

option(BENCHMARK_PERF_MODE "Enable O3+LTO for benchmark performance runs" OFF)
option(BENCHMARK_AUTORUN "Enable autorun loop for benchmark capture" OFF)
set(BENCHMARK_AUTORUN_COUNT "10" CACHE STRING "Autorun loop count for benchmarks")
option(BENCHMARK_AUTORUN_FORCE "Autorun without waiting for DTR" OFF)

# Set the project name
set(CMAKE_PROJECT_NAME cmsis-dsp-vs-eigen)

# Enable compile command to ease indexing with e.g. clangd
set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

# Core project settings
project(${CMAKE_PROJECT_NAME})
message("Build type: " ${CMAKE_BUILD_TYPE})

# Enable CMake support for ASM and C languages
enable_language(C ASM)

# Create an executable object type
add_executable(${CMAKE_PROJECT_NAME})

# Add STM32CubeMX generated sources
add_subdirectory(cmake/stm32cubemx)

# Link directories setup
target_link_directories(${CMAKE_PROJECT_NAME} PRIVATE
    # Add user defined library search paths
)

# Add sources to executable
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    # Add user sources here
    Drivers/CMSIS/DSP/Source/MatrixFunctions/arm_mat_init_f32.c
    Drivers/CMSIS/DSP/Source/MatrixFunctions/arm_mat_mult_f32.c
    Drivers/CMSIS/DSP/Source/MatrixFunctions/arm_mat_inverse_f32.c
)

# Add include paths
target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
    # Add user defined include paths
    Drivers/CMSIS/DSP/Include
)

# Add project symbols (macros)
target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE
    # Add user defined symbols
    ARM_MATH_LOOPUNROLL
    $<$<CONFIG:Release>:NDEBUG>
)

if(BENCHMARK_AUTORUN)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE BENCHMARK_AUTORUN)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE BENCHMARK_AUTORUN_COUNT=${BENCHMARK_AUTORUN_COUNT})
    if(BENCHMARK_AUTORUN_FORCE)
        target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE BENCHMARK_AUTORUN_FORCE)
    endif()
endif()

# Remove wrong libob.a library dependency when using cpp files
list(REMOVE_ITEM CMAKE_C_IMPLICIT_LINK_LIBRARIES ob)

# Add linked libraries
target_link_libraries(${CMAKE_PROJECT_NAME}
    stm32cubemx

    # Add user defined libraries
)

# Enable floating-point formatting for printf in newlib-nano.
target_link_options(${CMAKE_PROJECT_NAME} PRIVATE -u _printf_float)

# Add LibXR
include(${CMAKE_CURRENT_LIST_DIR}/cmake/LibXR.CMake)

if(BENCHMARK_PERF_MODE)
    message(STATUS "BENCHMARK_PERF_MODE is ON: enabling unified -O3 -flto")

    # Keep benchmark flags explicit and avoid mixing size-oriented Release defaults
    # (for example -Oz from some toolchains) with performance sampling settings.
    set(CMAKE_C_FLAGS_RELEASE "-g0" CACHE STRING "" FORCE)
    set(CMAKE_CXX_FLAGS_RELEASE "-g0" CACHE STRING "" FORCE)

    target_compile_options(${CMAKE_PROJECT_NAME} PRIVATE -O3 -flto)
    # Keep FreeRTOS context switch symbol alive under full LTO.
    target_link_options(${CMAKE_PROJECT_NAME} PRIVATE -flto -Wl,--undefined=vTaskSwitchContext)

    foreach(_bench_target IN ITEMS xr STM32_Drivers FreeRTOS USB_Device_Library)
        if(TARGET ${_bench_target})
            target_compile_options(${_bench_target} PRIVATE -O3 -flto)
            if(_bench_target STREQUAL "USB_Device_Library")
                target_link_options(${_bench_target} PRIVATE -flto)
            endif()
        endif()
    endforeach()

    # GNU toolchain may fail FreeRTOS PendSV relocation under LTO.
    # For STARM clang we keep FreeRTOS in LTO path.
    if(TARGET FreeRTOS AND CMAKE_C_COMPILER_ID STREQUAL "GNU")
        target_compile_options(FreeRTOS PRIVATE -O3 -fno-lto)
    endif()
endif()
