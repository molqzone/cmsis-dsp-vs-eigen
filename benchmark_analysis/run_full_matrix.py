from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Sequence

try:
    import serial
    _SERIAL_IMPORT_ERROR: Exception | None = None
except ImportError as exc:  # pragma: no cover - runtime dependency
    serial = None  # type: ignore[assignment]
    _SERIAL_IMPORT_ERROR = exc

from full_matrix_common import BuildProfile
from full_matrix_common import RunConfig
from full_matrix_common import SampleRecord
from full_matrix_common import default_profiles
from full_matrix_common import parse_profile_names
from full_matrix_common import parse_run_lines
from full_matrix_common import profiles_to_dict
from full_matrix_common import validate_records


@dataclass(frozen=True)
class ToolchainPaths:
    """Defines absolute toolchain paths required by the pipeline."""

    cube_cmake: Path
    cube: Path
    toolchain_bin: Path
    jlink: Path


def iso_utc_now() -> str:
    """Returns UTC ISO8601 timestamp with explicit timezone."""

    return datetime.now(timezone.utc).isoformat()


def to_jsonable(value: object) -> object:
    """Recursively converts objects into JSON-serializable structures."""

    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    return value


def parse_args() -> argparse.Namespace:
    """Parses command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Build/flash/capture C1~C10 matrix and generate report_full_matrix.md"
    )
    parser.add_argument("--profiles", default="C1,C2,C3,C4,C5,C6,C7,C8,C9,C10")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--port", default="/dev/ttyACM0")
    parser.add_argument("--jlink", default="/usr/bin/JLinkExe")
    parser.add_argument(
        "--cube-cmake",
        default=(
            "/home/keruth/.vscode/extensions/"
            "stmicroelectronics.stm32cube-ide-build-cmake-1.43.0/"
            "resources/cube-cmake/linux/cube-cmake"
        ),
    )
    parser.add_argument(
        "--cube",
        default=(
            "/home/keruth/.vscode/extensions/"
            "stmicroelectronics.stm32cube-ide-core-1.1.0/"
            "resources/binaries/linux/x86_64/cube"
        ),
    )
    parser.add_argument(
        "--toolchain-bin",
        default=(
            "/home/keruth/.local/share/stm32cube/bundles/"
            "st-arm-clang/19.1.6+st.10/bin"
        ),
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--timeout-sec", type=int, default=420)
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--device", default="STM32F407ZG")
    parser.add_argument("--swd-speed", default="4000")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def run_command(
    cmd: Sequence[str],
    cwd: Path,
    env: dict[str, str],
    log_path: Path,
) -> None:
    """Runs a command, streaming output to stdout and a log file."""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_fp:
        log_fp.write(f"$ {' '.join(cmd)}\n")
        process = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
            log_fp.write(line)
        ret = process.wait()
        if ret != 0:
            raise RuntimeError(
                f"Command failed (exit={ret}): {' '.join(cmd)}. See {log_path}."
            )


def verify_tools(paths: ToolchainPaths) -> None:
    """Checks required toolchain executables."""

    for path in (paths.cube_cmake, paths.cube, paths.jlink):
        if not path.is_file():
            raise FileNotFoundError(f"Tool not found: {path}")
    if not paths.toolchain_bin.is_dir():
        raise FileNotFoundError(f"toolchain-bin directory not found: {paths.toolchain_bin}")

    starm_clang = paths.toolchain_bin / "starm-clang"
    if not starm_clang.is_file():
        raise FileNotFoundError(f"starm-clang not found: {starm_clang}")


def build_env(paths: ToolchainPaths) -> dict[str, str]:
    """Creates process environment with required toolchain PATH entries."""

    env = dict(os.environ)
    extra = [
        str(paths.cube.parent),
        str(paths.cube_cmake.parent),
        str(paths.toolchain_bin),
    ]
    env["PATH"] = ":".join(extra + [env.get("PATH", "")])
    return env


def parse_size_sections(output_text: str) -> dict[str, int]:
    """Parses `.text/.rodata/.data/.bss` sizes from `starm-size -A` output."""

    sections = {"text": 0, "rodata": 0, "data": 0, "bss": 0}
    pat = re.compile(r"^\.(text|rodata|data|bss)\s+(\d+)\b")
    for line in output_text.splitlines():
        match = pat.match(line.strip())
        if not match:
            continue
        section, size = match.group(1), int(match.group(2))
        sections[section] = size
    return sections


def collect_memory_metrics(
    toolchain_bin: Path,
    elf_path: Path,
    cwd: Path,
    env: dict[str, str],
    log_path: Path,
) -> dict[str, int]:
    """Collects section sizes via `starm-size -A`."""

    size_tool = toolchain_bin / "starm-size"
    if not size_tool.is_file():
        raise FileNotFoundError(f"starm-size not found: {size_tool}")
    cmd = [str(size_tool), "-A", str(elf_path)]
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fp:
        fp.write(f"$ {' '.join(cmd)}\n")
        fp.write(result.stdout)
        fp.write("\n")
    if result.returncode != 0:
        raise RuntimeError(f"starm-size failed for {elf_path}. See {log_path}.")
    return parse_size_sections(result.stdout)


def configure_and_build(
    repo_dir: Path,
    build_dir: Path,
    profile: BuildProfile,
    cfg: RunConfig,
    paths: ToolchainPaths,
    env: dict[str, str],
    jobs: int,
    log_path: Path,
) -> Path:
    """Configures and builds one profile, returning produced ELF path."""

    build_dir.mkdir(parents=True, exist_ok=True)
    configure_cmd = [
        str(paths.cube_cmake),
        "-S",
        str(repo_dir),
        "-B",
        str(build_dir),
        "-G",
        "Ninja",
        f"-DCMAKE_TOOLCHAIN_FILE={repo_dir / 'cmake' / 'starm-clang.cmake'}",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DBENCHMARK_AUTORUN=ON",
        f"-DBENCHMARK_AUTORUN_COUNT={cfg.runs}",
        "-DBENCHMARK_AUTORUN_FORCE=ON",
        f"-DCMAKE_C_FLAGS={profile.cflags}",
        f"-DCMAKE_CXX_FLAGS={profile.cxxflags}",
        f"-DCMAKE_EXE_LINKER_FLAGS={profile.ldflags}",
        f"-DCMAKE_C_FLAGS_RELEASE={profile.cflags}",
        f"-DCMAKE_CXX_FLAGS_RELEASE={profile.cxxflags}",
        f"-DCMAKE_EXE_LINKER_FLAGS_RELEASE={profile.ldflags}",
    ]
    run_command(configure_cmd, cwd=repo_dir, env=env, log_path=log_path)

    build_cmd = [str(paths.cube_cmake), "--build", str(build_dir), "-j", str(jobs)]
    run_command(build_cmd, cwd=repo_dir, env=env, log_path=log_path)

    elf_path = build_dir / "cmsis-dsp-vs-eigen.elf"
    if not elf_path.is_file():
        raise FileNotFoundError(f"ELF not found after build: {elf_path}")
    return elf_path


def flash_with_jlink(
    elf_path: Path,
    profile_dir: Path,
    paths: ToolchainPaths,
    device: str,
    swd_speed: str,
    env: dict[str, str],
    log_path: Path,
) -> None:
    """Flashes ELF to target via JLink commander script."""

    cmd_file = profile_dir / "logs" / "flash.jlink"
    cmd_file.parent.mkdir(parents=True, exist_ok=True)
    cmd_file.write_text(
        "\n".join(["r", "h", f"loadfile {elf_path}", "r", "g", "q", ""]),
        encoding="utf-8",
    )

    cmd = [
        str(paths.jlink),
        "-device",
        device,
        "-if",
        "SWD",
        "-speed",
        swd_speed,
        "-autoconnect",
        "1",
        "-CommanderScript",
        str(cmd_file),
    ]
    run_command(cmd, cwd=profile_dir, env=env, log_path=log_path)

    text = log_path.read_text(encoding="utf-8", errors="ignore")
    critical_markers = (
        "Cannot connect",
        "Could not connect",
        "Error while programming",
        "Downloading file failed",
        "Failed to execute script command",
    )
    for marker in critical_markers:
        if marker in text:
            raise RuntimeError(f"JLink flash failed ({marker}). See {log_path}.")


def write_run_file(run_lines: Sequence[str], run_index: int, samples_dir: Path) -> Path:
    """Writes one run file with normalized LF line endings."""

    samples_dir.mkdir(parents=True, exist_ok=True)
    file_path = samples_dir / f"run_{run_index:03d}.csv"
    normalized = "\n".join(line.rstrip("\r\n") for line in run_lines) + "\n"
    file_path.write_text(normalized, encoding="utf-8")
    return file_path


def candidate_serial_ports(preferred_port: str) -> list[str]:
    """Returns ordered candidate serial device paths for CDC reconnect scenarios."""

    candidates: list[str] = [preferred_port]
    if preferred_port.startswith("/dev/ttyACM"):
        candidates.extend(sorted(glob.glob("/dev/ttyACM*")))
    elif preferred_port.startswith("/dev/ttyUSB"):
        candidates.extend(sorted(glob.glob("/dev/ttyUSB*")))

    seen: set[str] = set()
    ordered: list[str] = []
    for item in candidates:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def open_serial_with_retry(
    preferred_port: str,
    baudrate: int,
    wait_timeout_sec: int,
    log_fp,
):
    """Opens serial port with retry and ACM/USB fallback scanning."""

    deadline = time.monotonic() + wait_timeout_sec
    last_error: Exception | None = None
    attempt = 0

    while time.monotonic() <= deadline:
        attempt += 1
        ports = candidate_serial_ports(preferred_port)
        for port in ports:
            try:
                ser = serial.Serial(port=port, baudrate=baudrate, timeout=1)  # type: ignore[arg-type]
                log_fp.write(
                    f"# serial open success: port={port}, attempt={attempt}, "
                    f"time={iso_utc_now()}\n"
                )
                return ser, port
            except Exception as exc:  # pragma: no cover - hardware dependent
                last_error = exc
                continue

        if attempt == 1 or attempt % 5 == 0:
            log_fp.write(
                f"# serial open retry: attempt={attempt}, candidates={ports}, "
                f"time={iso_utc_now()}\n"
            )
        time.sleep(0.5)

    raise RuntimeError(
        f"Failed to open serial port within {wait_timeout_sec}s. "
        f"preferred={preferred_port}, last_error={last_error}"
    ) from last_error


def capture_serial_runs(
    port: str,
    baudrate: int,
    expected_runs: int,
    timeout_sec: int,
    samples_dir: Path,
    log_path: Path,
) -> None:
    """Captures benchmark CSV blocks from serial until expected runs are collected."""

    if serial is None:
        raise RuntimeError(
            "pyserial is required. Install dependencies in benchmark_analysis first."
        ) from _SERIAL_IMPORT_ERROR

    samples_dir.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    run_index = 1
    current_lines: list[str] = []
    last_rx_at = time.monotonic()

    serial_wait_timeout = max(20, min(120, timeout_sec // 3))
    with log_path.open("a", encoding="utf-8") as fp:
        ser, actual_port = open_serial_with_retry(
            preferred_port=port,
            baudrate=baudrate,
            wait_timeout_sec=serial_wait_timeout,
            log_fp=fp,
        )
        with ser:
            # Clear any stale bytes before asserting DTR to avoid dropping run head lines.
            ser.reset_input_buffer()
            # Firmware side requires host DTR asserted before benchmark output.
            try:
                ser.setDTR(True)
            except Exception:
                pass
            try:
                ser.setRTS(True)
            except Exception:
                pass
            time.sleep(0.2)
            fp.write(f"# serial capture started at {iso_utc_now()}\n")
            fp.write(f"# serial capture port={actual_port}\n")
            fp.flush()
            while run_index <= expected_runs:
                if (time.monotonic() - last_rx_at) > timeout_sec:
                    raise TimeoutError(
                        f"Serial capture idle-timeout ({timeout_sec}s), got "
                        f"{run_index - 1}/{expected_runs} runs."
                    )

                raw = ser.readline()
                if not raw:
                    continue
                last_rx_at = time.monotonic()
                line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                fp.write(line + "\n")
                fp.flush()
                current_lines.append(line)

                if line.strip().lower() != "done":
                    continue

                records = parse_run_lines(current_lines)
                expected_repeat = records[0].repeat
                validate_records(records, expected_repeat=expected_repeat)
                write_run_file(current_lines, run_index, samples_dir)
                current_lines = []
                run_index += 1


def profile_complete(profile_dir: Path, expected_runs: int) -> bool:
    """Checks whether a profile already has complete run files and marker metadata."""

    marker = profile_dir / "profile_meta.json"
    samples_dir = profile_dir / "samples_release"
    if not marker.is_file() or not samples_dir.is_dir():
        return False

    try:
        meta = json.loads(marker.read_text(encoding="utf-8"))
    except Exception:
        return False

    if meta.get("status") != "completed":
        return False
    if int(meta.get("runs", 0)) != expected_runs:
        return False

    for idx in range(1, expected_runs + 1):
        f = samples_dir / f"run_{idx:03d}.csv"
        if not f.is_file():
            return False
        records = parse_run_lines(f.read_text(encoding="utf-8").splitlines())
        validate_records(records, expected_repeat=records[0].repeat)
    return True


def run_profile(
    repo_dir: Path,
    cfg: RunConfig,
    profile: BuildProfile,
    paths: ToolchainPaths,
    env: dict[str, str],
    args: argparse.Namespace,
) -> dict[str, object]:
    """Executes build/flash/capture for one profile."""

    profile_dir = cfg.build_root / profile.name
    build_dir = profile_dir / "build"
    logs_dir = profile_dir / "logs"
    samples_dir = profile_dir / "samples_release"
    logs_dir.mkdir(parents=True, exist_ok=True)

    if args.resume and profile_complete(profile_dir, cfg.runs):
        print(f"[{profile.name}] already completed, skip (--resume).")
        return json.loads((profile_dir / "profile_meta.json").read_text(encoding="utf-8"))

    if not args.resume:
        if profile_dir.exists():
            shutil.rmtree(profile_dir)
        logs_dir.mkdir(parents=True, exist_ok=True)

    cfg_log = logs_dir / "configure_build.log"
    jlink_log = logs_dir / "jlink_flash.log"
    serial_log = logs_dir / "serial_capture.log"
    size_log = logs_dir / "size.log"

    if args.dry_run:
        print(f"[{profile.name}] dry-run only: skip build/flash/capture.")
        return {
            "profile": profile.name,
            "status": "dry-run",
            "runs": cfg.runs,
            "cflags": profile.cflags,
            "cxxflags": profile.cxxflags,
            "ldflags": profile.ldflags,
        }

    elf_path = configure_and_build(
        repo_dir=repo_dir,
        build_dir=build_dir,
        profile=profile,
        cfg=cfg,
        paths=paths,
        env=env,
        jobs=args.jobs,
        log_path=cfg_log,
    )
    memory = collect_memory_metrics(
        toolchain_bin=paths.toolchain_bin,
        elf_path=elf_path,
        cwd=repo_dir,
        env=env,
        log_path=size_log,
    )
    flash_with_jlink(
        elf_path=elf_path,
        profile_dir=profile_dir,
        paths=paths,
        device=args.device,
        swd_speed=args.swd_speed,
        env=env,
        log_path=jlink_log,
    )
    capture_serial_runs(
        port=cfg.serial_port,
        baudrate=args.baudrate,
        expected_runs=cfg.runs,
        timeout_sec=cfg.timeout_sec,
        samples_dir=samples_dir,
        log_path=serial_log,
    )

    meta = {
        "profile": profile.name,
        "status": "completed",
        "runs": cfg.runs,
        "captured_at": iso_utc_now(),
        "cflags": profile.cflags,
        "cxxflags": profile.cxxflags,
        "ldflags": profile.ldflags,
        "uses_lto": profile.uses_lto,
        "tools": {
            "cube_cmake": str(paths.cube_cmake),
            "cube": str(paths.cube),
            "starm_clang": str(paths.toolchain_bin / "starm-clang"),
            "jlink": str(paths.jlink),
        },
        "memory": memory,
        "paths": {
            "profile_dir": str(profile_dir),
            "build_dir": str(build_dir),
            "samples_dir": str(samples_dir),
            "elf": str(elf_path),
            "configure_build_log": str(cfg_log),
            "jlink_flash_log": str(jlink_log),
            "serial_capture_log": str(serial_log),
            "size_log": str(size_log),
        },
    }
    (profile_dir / "profile_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return meta


def invoke_report_generator(
    repo_dir: Path,
    input_root: Path,
    output_md: Path,
    output_dir: Path,
    profiles: Sequence[BuildProfile],
) -> None:
    """Calls report generator script after all profiles succeed."""

    cmd = [
        sys.executable,
        str(repo_dir / "benchmark_analysis" / "generate_full_matrix_report.py"),
        "--input-root",
        str(input_root),
        "--output-md",
        str(output_md),
        "--output-dir",
        str(output_dir),
        "--profiles",
        ",".join(p.name for p in profiles),
        "--strict",
    ]
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        raise RuntimeError("Report generator failed.")


def main() -> None:
    """Entry point for full matrix benchmark pipeline."""

    args = parse_args()
    repo_dir = Path(__file__).resolve().parents[1]
    profiles_map = default_profiles()
    selected_names = parse_profile_names(args.profiles)

    selected_profiles: list[BuildProfile] = []
    for name in selected_names:
        if name not in profiles_map:
            raise ValueError(f"Unknown profile: {name}")
        selected_profiles.append(profiles_map[name])

    cfg = RunConfig(
        repo_dir=repo_dir,
        build_root=repo_dir / "build" / "bench_matrix",
        serial_port=args.port,
        runs=args.runs,
        timeout_sec=args.timeout_sec,
    )
    paths = ToolchainPaths(
        cube_cmake=Path(args.cube_cmake).resolve(),
        cube=Path(args.cube).resolve(),
        toolchain_bin=Path(args.toolchain_bin).resolve(),
        jlink=Path(args.jlink).resolve(),
    )
    verify_tools(paths)
    env = build_env(paths)

    cfg.build_root.mkdir(parents=True, exist_ok=True)
    manifest_path = cfg.build_root / "matrix_manifest.json"
    manifest = {
        "generated_at": iso_utc_now(),
        "profiles": profiles_to_dict(selected_profiles),
        "run_config": to_jsonable(asdict(cfg)),
        "tools": to_jsonable(asdict(paths)),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    completed: list[dict[str, object]] = []
    for profile in selected_profiles:
        print(f"\n===== [{profile.name}] start =====")
        try:
            meta = run_profile(
                repo_dir=repo_dir,
                cfg=cfg,
                profile=profile,
                paths=paths,
                env=env,
                args=args,
            )
            completed.append(meta)
            print(f"===== [{profile.name}] success =====")
        except Exception as exc:
            print(f"===== [{profile.name}] failed: {exc} =====")
            raise SystemExit(1) from exc

    if args.dry_run:
        print("Dry-run complete.")
        return

    invoke_report_generator(
        repo_dir=repo_dir,
        input_root=cfg.build_root,
        output_md=repo_dir / "report_full_matrix.md",
        output_dir=repo_dir / "benchmark_analysis" / "output" / "full_matrix",
        profiles=selected_profiles,
    )
    shutil.copyfile(repo_dir / "report_full_matrix.md", repo_dir / "report.md")
    print("Full matrix pipeline finished successfully.")


if __name__ == "__main__":
    main()
