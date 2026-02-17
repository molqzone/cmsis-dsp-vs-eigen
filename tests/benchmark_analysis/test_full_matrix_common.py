from __future__ import annotations

import sys
from pathlib import Path
import unittest

import pandas as pd


REPO_DIR = Path(__file__).resolve().parents[2]
ANALYSIS_DIR = REPO_DIR / "benchmark_analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

from full_matrix_common import EXPECTED_INV_SIZES
from full_matrix_common import EXPECTED_MUL_SIZES
from full_matrix_common import build_profile_phenomenon_signature
from full_matrix_common import classify_speedup_band
from full_matrix_common import default_profiles
from full_matrix_common import detect_crossover
from full_matrix_common import group_profiles_by_phenomenon
from full_matrix_common import parse_run_lines
from full_matrix_common import split_serial_into_runs
from full_matrix_common import validate_records
from generate_full_matrix_report import classify_leader
from generate_full_matrix_report import group_profiles_for_plot
from generate_full_matrix_report import to_cmsis_over_eigen


def _sample_line(op: str, n: int, repeat: int = 100, mode: str = "Release") -> str:
    if op == "mul":
        ratio = 1.5 if n <= 6 else 0.8
    else:
        ratio = 1.2 if n <= 4 else 0.7
    return (
        f"{op},{n},{repeat},1,100.0,120.0,{ratio:.6f},0.00001000,100,0,{mode}"
    )


def _build_one_run_lines() -> list[str]:
    lines = [
        "op,n,repeat,warmup,eigen_avg_cycles,cmsis_avg_cycles,cmsis_over_eigen,"
        "error_l2,valid,invalid,build_mode"
    ]
    for n in EXPECTED_MUL_SIZES:
        lines.append(_sample_line("mul", n))
    for n in EXPECTED_INV_SIZES:
        lines.append(_sample_line("inv", n))
    lines.append("done")
    return lines


class FullMatrixCommonTests(unittest.TestCase):
    def test_plot_grouping_merges_identical_curves(self) -> None:
        df = pd.DataFrame(
            [
                {"profile": "C1", "op": "mul", "n": 3, "eigen_over_cmsis_mean": 2.0},
                {"profile": "C1", "op": "mul", "n": 4, "eigen_over_cmsis_mean": 1.5},
                {"profile": "C2", "op": "mul", "n": 3, "eigen_over_cmsis_mean": 2.0000004},
                {"profile": "C2", "op": "mul", "n": 4, "eigen_over_cmsis_mean": 1.5000004},
                {"profile": "C3", "op": "mul", "n": 3, "eigen_over_cmsis_mean": 0.9},
                {"profile": "C3", "op": "mul", "n": 4, "eigen_over_cmsis_mean": 0.8},
            ]
        )
        grouped = group_profiles_for_plot(
            stats=df,
            profiles=["C1", "C2", "C3"],
            op="mul",
            value_col="eigen_over_cmsis_mean",
        )
        self.assertEqual(len(grouped), 2)
        self.assertEqual(grouped[0][0], ["C1", "C2"])
        self.assertEqual(grouped[1][0], ["C3"])

    def test_phenomenon_grouping_signature(self) -> None:
        points_a = [
            ("mul", 3, 1.12),
            ("mul", 4, 1.10),
            ("mul", 6, 0.96),
            ("inv", 3, 1.09),
            ("inv", 4, 0.99),
        ]
        points_b = [
            ("mul", 3, 1.11),
            ("mul", 4, 1.08),
            ("mul", 6, 0.95),
            ("inv", 3, 1.07),
            ("inv", 4, 0.99),
        ]
        points_c = [
            ("mul", 3, 0.90),
            ("mul", 4, 0.91),
            ("mul", 6, 0.93),
            ("inv", 3, 0.88),
            ("inv", 4, 0.89),
        ]
        sig_a = build_profile_phenomenon_signature(points_a, tolerance=0.02)
        sig_b = build_profile_phenomenon_signature(points_b, tolerance=0.02)
        sig_c = build_profile_phenomenon_signature(points_c, tolerance=0.02)
        self.assertEqual(sig_a, sig_b)
        self.assertNotEqual(sig_a, sig_c)

        grouped = group_profiles_by_phenomenon(
            {"C1": points_a, "C2": points_b, "C3": points_c},
            tolerance=0.02,
        )
        self.assertEqual(len(grouped), 2)
        self.assertEqual(set(grouped[0][1]), {"C1", "C2"})
        self.assertEqual(classify_speedup_band(1.01, tolerance=0.02), "T")
        self.assertEqual(classify_speedup_band(1.2, tolerance=0.02), "C")
        self.assertEqual(classify_speedup_band(0.8, tolerance=0.02), "E")

    def test_ratio_semantics_for_leader_and_speedup(self) -> None:
        self.assertEqual(classify_leader(1.2), "CMSIS")
        self.assertEqual(classify_leader(0.8), "Eigen")
        self.assertEqual(classify_leader(1.0), "Tie")
        self.assertAlmostEqual(to_cmsis_over_eigen(1.25), 0.8)
        self.assertAlmostEqual(to_cmsis_over_eigen(0.8), 1.25)

    def test_default_profiles_include_og_oz_without_c11(self) -> None:
        profiles = default_profiles()
        self.assertIn("C9", profiles)
        self.assertIn("C10", profiles)
        self.assertNotIn("C11", profiles)
        self.assertIn("-Og", profiles["C9"].cflags)
        self.assertIn("-Oz", profiles["C10"].cflags)

    def test_parse_and_validate_normal_run(self) -> None:
        lines = _build_one_run_lines()
        records = parse_run_lines(lines)
        self.assertEqual(len(records), len(EXPECTED_MUL_SIZES) + len(EXPECTED_INV_SIZES))
        validate_records(records, expected_repeat=100)

    def test_split_runs_boundary_with_noise(self) -> None:
        run1 = _build_one_run_lines()
        run2 = _build_one_run_lines()
        merged = ["autorun-start", "WARNING: debug build"] + run1 + ["", "noise"] + run2
        runs = split_serial_into_runs(merged, expected_runs=2)
        self.assertEqual(len(runs), 2)
        self.assertTrue(any(line.strip().lower() == "done" for line in runs[0]))
        self.assertTrue(any(line.strip().lower() == "done" for line in runs[1]))

    def test_detect_crossover_boundary(self) -> None:
        self.assertEqual(detect_crossover([(3, 2.0), (4, 1.2), (6, 0.9), (8, 0.7)]), 6)
        self.assertIsNone(detect_crossover([(3, 2.0), (4, 1.5), (6, 1.1)]))

    def test_validate_records_exception(self) -> None:
        lines = _build_one_run_lines()
        records = parse_run_lines(lines)
        bad = records[0]
        bad_line = (
            f"{bad.op},{bad.n},{bad.repeat},{bad.warmup},{bad.eigen_avg_cycles},"
            f"{bad.cmsis_avg_cycles},{bad.cmsis_over_eigen},{bad.error_l2},50,0,{bad.build_mode}"
        )
        mutated_lines = [bad_line] + lines[1:]
        mutated_records = parse_run_lines(mutated_lines)
        with self.assertRaises(ValueError):
            validate_records(mutated_records, expected_repeat=100)


if __name__ == "__main__":
    unittest.main()
