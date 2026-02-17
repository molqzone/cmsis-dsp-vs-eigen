from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
import math
from pathlib import Path
from typing import Iterable
from typing import Mapping
from typing import Sequence


EXPECTED_MUL_SIZES: tuple[int, ...] = (3, 4, 6, 8, 10, 16, 32, 64)
EXPECTED_INV_SIZES: tuple[int, ...] = (3, 4, 6, 8, 10)


@dataclass(frozen=True)
class BuildProfile:
    """Defines a single benchmark compiler profile.

    Args:
        name: Profile name (for example `C1`).
        cflags: Release C compiler flags.
        cxxflags: Release C++ compiler flags.
        ldflags: Additional Release linker flags.
        uses_lto: Whether this profile enables LTO.
    """

    name: str
    cflags: str
    cxxflags: str
    ldflags: str
    uses_lto: bool


@dataclass(frozen=True)
class RunConfig:
    """Runtime configuration for the full-matrix benchmark pipeline.

    Args:
        repo_dir: Repository root directory.
        build_root: Root directory for per-profile build artifacts.
        serial_port: Serial device path (for example `/dev/ttyACM0`).
        runs: Number of outer runs to collect.
        timeout_sec: Capture timeout in seconds.
    """

    repo_dir: Path
    build_root: Path
    serial_port: str
    runs: int
    timeout_sec: int


@dataclass(frozen=True)
class SampleRecord:
    """Represents one CSV benchmark record line."""

    op: str
    n: int
    repeat: int
    warmup: int
    eigen_avg_cycles: float
    cmsis_avg_cycles: float
    cmsis_over_eigen: float
    error_l2: float
    valid: int
    invalid: int
    build_mode: str


def default_profiles() -> dict[str, BuildProfile]:
    """Returns the fixed C1~C10 profile matrix from PLAN.md."""

    return {
        "C1": BuildProfile(
            name="C1",
            cflags="-g0 -O3 -flto -DNDEBUG",
            cxxflags="-g0 -O3 -flto -DNDEBUG",
            ldflags="-flto -Wl,--undefined=vTaskSwitchContext",
            uses_lto=True,
        ),
        "C2": BuildProfile(
            name="C2",
            cflags="-g0 -O2 -flto -DNDEBUG",
            cxxflags="-g0 -O2 -flto -DNDEBUG",
            ldflags="-flto -Wl,--undefined=vTaskSwitchContext",
            uses_lto=True,
        ),
        "C3": BuildProfile(
            name="C3",
            cflags="-g0 -O3 -DNDEBUG",
            cxxflags="-g0 -O3 -DNDEBUG",
            ldflags="-Wl,--undefined=vTaskSwitchContext",
            uses_lto=False,
        ),
        "C4": BuildProfile(
            name="C4",
            cflags="-g0 -O3 -flto -ffast-math -DNDEBUG",
            cxxflags="-g0 -O3 -flto -ffast-math -DNDEBUG",
            ldflags="-flto -Wl,--undefined=vTaskSwitchContext",
            uses_lto=True,
        ),
        "C5": BuildProfile(
            name="C5",
            cflags="-g0 -Ofast -flto -DNDEBUG",
            cxxflags="-g0 -Ofast -flto -DNDEBUG",
            ldflags="-flto -Wl,--undefined=vTaskSwitchContext",
            uses_lto=True,
        ),
        "C6": BuildProfile(
            name="C6",
            cflags="-g0 -Os -flto -DNDEBUG",
            cxxflags="-g0 -Os -flto -DNDEBUG",
            ldflags="-flto -Wl,--undefined=vTaskSwitchContext",
            uses_lto=True,
        ),
        "C7": BuildProfile(
            name="C7",
            cflags="-g0 -O3 -flto -fno-unroll-loops -DNDEBUG",
            cxxflags="-g0 -O3 -flto -fno-unroll-loops -DNDEBUG",
            ldflags="-flto -Wl,--undefined=vTaskSwitchContext",
            uses_lto=True,
        ),
        "C8": BuildProfile(
            name="C8",
            cflags="-g0 -O3 -flto -fno-inline-functions-called-once -DNDEBUG",
            cxxflags="-g0 -O3 -flto -fno-inline-functions-called-once -DNDEBUG",
            ldflags="-flto -Wl,--undefined=vTaskSwitchContext",
            uses_lto=True,
        ),
        "C9": BuildProfile(
            name="C9",
            cflags="-g -Og -flto -DNDEBUG",
            cxxflags="-g -Og -flto -DNDEBUG",
            ldflags="-flto -Wl,--undefined=vTaskSwitchContext",
            uses_lto=True,
        ),
        "C10": BuildProfile(
            name="C10",
            cflags="-g0 -Oz -flto -DNDEBUG",
            cxxflags="-g0 -Oz -flto -DNDEBUG",
            ldflags="-flto -Wl,--undefined=vTaskSwitchContext",
            uses_lto=True,
        ),
    }


def profiles_to_dict(profiles: Sequence[BuildProfile]) -> list[dict[str, object]]:
    """Converts profiles to serializable dicts."""

    return [asdict(profile) for profile in profiles]


def parse_profile_names(text: str) -> list[str]:
    """Parses a comma-separated profile list."""

    return [name.strip().upper() for name in text.split(",") if name.strip()]


def parse_csv_record_line(line: str) -> SampleRecord | None:
    """Parses a CSV benchmark line.

    Args:
        line: Raw input line.

    Returns:
        Parsed `SampleRecord` for valid data lines, otherwise `None`.
    """

    stripped = line.strip()
    if not stripped:
        return None
    if stripped.lower() == "done":
        return None

    cols = stripped.split(",")
    first = cols[0].lstrip("\ufeff")
    if first == "op":
        return None
    if len(cols) != 11:
        return None

    return SampleRecord(
        op=first,
        n=int(cols[1]),
        repeat=int(cols[2]),
        warmup=int(cols[3]),
        eigen_avg_cycles=float(cols[4]),
        cmsis_avg_cycles=float(cols[5]),
        cmsis_over_eigen=float(cols[6]),
        error_l2=float(cols[7]),
        valid=int(cols[8]),
        invalid=int(cols[9]),
        build_mode=cols[10],
    )


def parse_run_lines(lines: Iterable[str]) -> list[SampleRecord]:
    """Parses one benchmark run text block into records."""

    records: list[SampleRecord] = []
    for line in lines:
        rec = parse_csv_record_line(line)
        if rec is not None:
            records.append(rec)
    if not records:
        raise ValueError("No valid benchmark records found in run content.")
    return records


def split_serial_into_runs(lines: Sequence[str], expected_runs: int) -> list[list[str]]:
    """Splits serial output into run blocks ending with `done`."""

    if expected_runs <= 0:
        raise ValueError("expected_runs must be positive.")

    runs: list[list[str]] = []
    current: list[str] = []
    for raw in lines:
        line = raw.rstrip("\r\n")
        current.append(line)
        if line.strip().lower() == "done":
            runs.append(current)
            current = []

    if len(runs) < expected_runs:
        raise ValueError(
            f"Incomplete run capture: expected {expected_runs}, got {len(runs)}."
        )
    if len(runs) > expected_runs:
        runs = runs[:expected_runs]
    return runs


def validate_records(records: Sequence[SampleRecord], expected_repeat: int) -> None:
    """Validates one benchmark run record list.

    Validation covers:
    - Expected mul/inv matrix sizes.
    - `repeat` consistency.
    - `valid + invalid == repeat`.
    - `error_l2 <= 1e-4`.
    """

    if expected_repeat <= 0:
        raise ValueError("expected_repeat must be positive.")
    if not records:
        raise ValueError("No benchmark records to validate.")

    mul_sizes = sorted([r.n for r in records if r.op == "mul"])
    inv_sizes = sorted([r.n for r in records if r.op == "inv"])
    if tuple(mul_sizes) != EXPECTED_MUL_SIZES:
        raise ValueError(
            f"Unexpected mul sizes: {mul_sizes}, expected {list(EXPECTED_MUL_SIZES)}."
        )
    if tuple(inv_sizes) != EXPECTED_INV_SIZES:
        raise ValueError(
            f"Unexpected inv sizes: {inv_sizes}, expected {list(EXPECTED_INV_SIZES)}."
        )

    for rec in records:
        if rec.repeat != expected_repeat:
            raise ValueError(
                f"Unexpected repeat value for {rec.op}-{rec.n}: {rec.repeat}, "
                f"expected {expected_repeat}."
            )
        if rec.valid + rec.invalid != rec.repeat:
            raise ValueError(
                f"Invalid valid/invalid sum for {rec.op}-{rec.n}: "
                f"{rec.valid}+{rec.invalid}!={rec.repeat}."
            )
        if rec.error_l2 > 1e-4:
            raise ValueError(
                f"error_l2 out of threshold for {rec.op}-{rec.n}: {rec.error_l2}."
            )


def detect_crossover(pairs: Sequence[tuple[int, float]]) -> int | None:
    """Finds first N where CMSIS/Eigen ratio crosses to <= 1."""

    for n, ratio in sorted(pairs, key=lambda item: item[0]):
        if ratio <= 1.0:
            return n
    return None


def classify_speedup_band(speedup: float, tolerance: float = 0.02) -> str:
    """Classifies one speedup point into CMSIS/Eigen/Tie band.

    Args:
        speedup: Eigen/CMSIS ratio. `>1` means CMSIS faster.
        tolerance: Tie band around 1.0.

    Returns:
        `C` for CMSIS-leading, `E` for Eigen-leading, `T` for near-tie.
    """

    if math.isclose(speedup, 1.0, abs_tol=tolerance):
        return "T"
    return "C" if speedup > 1.0 else "E"


def build_profile_phenomenon_signature(
    points: Sequence[tuple[str, int, float]],
    tolerance: float = 0.02,
) -> str:
    """Builds a stable phenomenon signature from profile speedup points.

    Args:
        points: Sequence of `(op, n, eigen_over_cmsis)` points.
        tolerance: Tie-band tolerance used by `classify_speedup_band`.

    Returns:
        String signature combining winner patterns and crossover points.
    """

    by_op: dict[str, list[tuple[int, float]]] = {"mul": [], "inv": []}
    for op, n, speedup in points:
        if op in by_op:
            by_op[op].append((n, speedup))

    segments: list[str] = []
    for op in ("mul", "inv"):
        ordered = sorted(by_op[op], key=lambda item: item[0])
        pattern = "".join(classify_speedup_band(speedup, tolerance) for _, speedup in ordered)
        crossover = detect_crossover([(n, speedup) for n, speedup in ordered])
        cross_text = str(crossover) if crossover is not None else "none"
        segments.append(f"{op}:{pattern}:cross={cross_text}")
    return "|".join(segments)


def group_profiles_by_phenomenon(
    profile_points: Mapping[str, Sequence[tuple[str, int, float]]],
    tolerance: float = 0.02,
) -> list[tuple[str, list[str]]]:
    """Groups profiles with the same phenomenon signature.

    Args:
        profile_points: Mapping from profile name to speedup points.
        tolerance: Tie-band tolerance passed to signature builder.

    Returns:
        List of `(signature, profiles)` sorted by group size (desc) then name.
    """

    grouped: dict[str, list[str]] = {}
    for profile in sorted(profile_points.keys()):
        signature = build_profile_phenomenon_signature(
            profile_points[profile], tolerance=tolerance
        )
        grouped.setdefault(signature, []).append(profile)
    return sorted(grouped.items(), key=lambda item: (-len(item[1]), item[1][0]))
