"""Tests for the v0.2 held-out runner that never execute real evaluation data."""

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"
if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))


from run_policy2 import (  # noqa: E402
    calculate_metrics,
    run_baseline,
    run_policy1,
    run_policy2,
)
from run_policy2_evaluation import (  # noqa: E402
    EXPECTED_EVALUATION_CASES,
    compare_policies,
    read_evaluation_cases,
    refuse_existing_outputs,
    sha256_file,
    validate_freeze_manifest,
)


CSV_FIELDS = [
    "case_id",
    "split",
    "true_state",
    "amount_deviation",
    "device_location_context",
    "recent_velocity",
    "step_up_result_if_requested",
    "verification_independence_if_requested",
]


def make_row(
    number: int,
    *,
    split: str = "EVALUATION",
    true_state: str = "LEGITIMATE",
    amount: str = "NORMAL",
    context: str = "KNOWN_DEVICE_USUAL_LOCATION",
    velocity: str = "NORMAL",
    result: str = "PASS",
    independence: str = "INDEPENDENT",
) -> dict[str, str]:
    """Create one synthetic row unrelated to the held-out CSV."""

    return {
        "case_id": f"TEST-{number:03d}",
        "split": split,
        "true_state": true_state,
        "amount_deviation": amount,
        "device_location_context": context,
        "recent_velocity": velocity,
        "step_up_result_if_requested": result,
        "verification_independence_if_requested": independence,
    }


def write_rows(file_path: Path, rows: list[dict[str, str]]) -> None:
    """Write a temporary CSV for validation tests."""

    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


class TestPolicy2EvaluationDataset(unittest.TestCase):
    """Check the exact held-out input boundary using synthetic files."""

    def test_exactly_thirty_evaluation_rows_are_accepted(self) -> None:
        """A valid synthetic evaluation dataset should load without execution."""

        rows = [make_row(index) for index in range(EXPECTED_EVALUATION_CASES)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evaluation.csv"
            write_rows(path, rows)
            loaded = read_evaluation_cases(path)

        self.assertEqual(len(loaded), EXPECTED_EVALUATION_CASES)

    def test_wrong_count_development_row_and_duplicate_are_rejected(self) -> None:
        """All three common ways to cross the split boundary must fail."""

        valid = [make_row(index) for index in range(EXPECTED_EVALUATION_CASES)]
        variants = {
            "Expected 30": valid[:-1],
            "not an EVALUATION": [dict(row) for row in valid],
            "duplicate case IDs": [dict(row) for row in valid],
        }
        variants["not an EVALUATION"][0]["split"] = "DEVELOPMENT"
        variants["duplicate case IDs"][-1]["case_id"] = valid[0]["case_id"]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, (message, rows) in enumerate(variants.items()):
                with self.subTest(message=message):
                    path = root / f"invalid-{index}.csv"
                    write_rows(path, rows)
                    with self.assertRaisesRegex(ValueError, message):
                        read_evaluation_cases(path)


class TestFreezeProtection(unittest.TestCase):
    """Check hash-based freezing and one-time output protection."""

    def test_matching_freeze_hash_is_accepted(self) -> None:
        """An unchanged frozen file must pass manifest validation."""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frozen_file = root / "policy.txt"
            frozen_file.write_text("frozen", encoding="utf-8")
            manifest_path = root / "freeze.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "status": "FROZEN_BEFORE_HELD_OUT_EVALUATION",
                        "sha256": {"policy.txt": sha256_file(frozen_file)},
                    }
                ),
                encoding="utf-8",
            )

            manifest = validate_freeze_manifest(manifest_path, root)

        self.assertIn("policy.txt", manifest["sha256"])

    def test_changed_frozen_file_is_rejected(self) -> None:
        """Any post-freeze change must stop evaluation before execution."""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frozen_file = root / "policy.txt"
            frozen_file.write_text("before", encoding="utf-8")
            original_hash = sha256_file(frozen_file)
            manifest_path = root / "freeze.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "status": "FROZEN_BEFORE_HELD_OUT_EVALUATION",
                        "sha256": {"policy.txt": original_hash},
                    }
                ),
                encoding="utf-8",
            )
            frozen_file.write_text("after", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "changed before evaluation"):
                validate_freeze_manifest(manifest_path, root)

    def test_existing_output_is_never_overwritten(self) -> None:
        """A second held-out run must stop when an artifact already exists."""

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            output.write_text("existing", encoding="utf-8")

            with self.assertRaisesRegex(FileExistsError, "will not be overwritten"):
                refuse_existing_outputs((output,))


class TrackingRow(dict[str, str]):
    """Count reads of evidence that older policies must not receive."""

    def __init__(self, values: dict[str, str]) -> None:
        super().__init__(values)
        self.result_reads = 0
        self.independence_reads = 0

    def __getitem__(self, key: str) -> str:
        if key == "step_up_result_if_requested":
            self.result_reads += 1
        if key == "verification_independence_if_requested":
            self.independence_reads += 1
        return super().__getitem__(key)


class TestThreePolicyComparison(unittest.TestCase):
    """Verify evidence isolation and the final comparison rule."""

    def test_older_policies_do_not_receive_policy2_independence(self) -> None:
        """Baseline reads neither check; Policy 1 reads only its result."""

        baseline_row = TrackingRow(make_row(1, amount="HIGH"))
        policy1_row = TrackingRow(make_row(1, amount="HIGH"))

        run_baseline([baseline_row])
        run_policy1([policy1_row])

        self.assertEqual(
            (baseline_row.result_reads, baseline_row.independence_reads),
            (0, 0),
        )
        self.assertEqual(
            (policy1_row.result_reads, policy1_row.independence_reads),
            (1, 0),
        )

    def test_policy2_can_pass_every_frozen_gate(self) -> None:
        """A safe synthetic review reduction must be classified as better."""

        rows = [
            make_row(1, amount="HIGH", result="PASS", independence="INDEPENDENT"),
            make_row(
                2,
                true_state="FRAUDULENT",
                amount="HIGH",
                result="PASS",
                independence="SAME_CHANNEL",
            ),
            make_row(
                3,
                true_state="FRAUDULENT",
                amount="HIGH",
                context="KNOWN_DEVICE_UNUSUAL_LOCATION",
                result="FAIL",
                independence="INDEPENDENT",
            ),
            make_row(4),
        ]
        baseline_results = run_baseline(rows)
        policy1_results = run_policy1(rows)
        policy2_results = run_policy2(rows)

        comparison = compare_policies(
            baseline_results,
            policy1_results,
            policy2_results,
            calculate_metrics(baseline_results),
            calculate_metrics(policy1_results),
            calculate_metrics(policy2_results),
        )

        self.assertTrue(comparison["all_success_criteria_met"])
        self.assertEqual(
            comparison["conclusion"],
            "POLICY_2_BETTER_FOR_FROZEN_OBJECTIVE",
        )

    def test_different_case_order_is_rejected(self) -> None:
        """All policy metrics must come from identical ordered cases."""

        rows = [make_row(1), make_row(2)]
        baseline_results = run_baseline(rows)
        policy1_results = run_policy1(rows)
        policy2_results = list(reversed(run_policy2(rows)))

        with self.assertRaisesRegex(ValueError, "same cases"):
            compare_policies(
                baseline_results,
                policy1_results,
                policy2_results,
                calculate_metrics(baseline_results),
                calculate_metrics(policy1_results),
                calculate_metrics(policy2_results),
            )


if __name__ == "__main__":
    unittest.main()
