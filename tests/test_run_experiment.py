"""Safety and correctness tests for the held-out evaluation runner.

These tests use synthetic rows. They do not execute either policy on the real
thirty-case evaluation CSV, so the runner can be tested before the one-time
held-out comparison is performed.

Run from the repository root with:

    python -m unittest discover -s tests -v
"""

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


from agent import BaselineAgent, Policy1Agent  # noqa: E402
from run_experiment import (  # noqa: E402
    EXPECTED_EVALUATION_CASES,
    build_initial_evidence,
    calculate_metrics,
    compare_policies,
    read_evaluation_cases,
    run_baseline_evaluation,
    run_policy1_evaluation,
    write_comparison_summary,
    write_csv,
    write_json,
)


CSV_FIELDS = [
    "case_id",
    "split",
    "true_state",
    "amount_deviation",
    "device_location_context",
    "recent_velocity",
    "step_up_result_if_requested",
]


def make_row(
    number: int,
    *,
    split: str = "EVALUATION",
    true_state: str = "LEGITIMATE",
    amount: str = "NORMAL",
    context: str = "KNOWN_DEVICE_USUAL_LOCATION",
    velocity: str = "NORMAL",
    verification: str = "PASS",
) -> dict[str, str]:
    """Create one small synthetic evaluator row for a unit test."""

    return {
        "case_id": f"SYNTH-{number:03d}",
        "split": split,
        "true_state": true_state,
        "amount_deviation": amount,
        "device_location_context": context,
        "recent_velocity": velocity,
        "step_up_result_if_requested": verification,
    }


def make_thirty_rows() -> list[dict[str, str]]:
    """Return thirty unique valid rows without reading the real dataset."""

    return [make_row(number) for number in range(EXPECTED_EVALUATION_CASES)]


def write_dataset(path: Path, rows: list[dict[str, str]]) -> None:
    """Write synthetic rows to a temporary CSV for reader-validation tests."""

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


class TestEvaluationDatasetBoundary(unittest.TestCase):
    """Check that the runner accepts only the frozen evaluation boundary."""

    def test_exactly_thirty_evaluation_rows_are_accepted(self) -> None:
        """A valid synthetic thirty-row EVALUATION file must load."""

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evaluation.csv"
            write_dataset(path, make_thirty_rows())

            loaded = read_evaluation_cases(path)

        self.assertEqual(len(loaded), EXPECTED_EVALUATION_CASES)
        self.assertEqual(
            {row["split"] for row in loaded},
            {"EVALUATION"},
        )

    def test_wrong_case_count_is_rejected(self) -> None:
        """Twenty-nine rows must not silently become the evaluation set."""

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evaluation.csv"
            write_dataset(path, make_thirty_rows()[:-1])

            with self.assertRaisesRegex(ValueError, "Expected 30"):
                read_evaluation_cases(path)

    def test_development_row_is_rejected(self) -> None:
        """A DEVELOPMENT marker must stop the held-out runner."""

        rows = make_thirty_rows()
        rows[7]["split"] = "DEVELOPMENT"

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evaluation.csv"
            write_dataset(path, rows)

            with self.assertRaisesRegex(ValueError, "not an EVALUATION"):
                read_evaluation_cases(path)

    def test_duplicate_case_id_is_rejected(self) -> None:
        """Each of the thirty evaluation cases must be counted once."""

        rows = make_thirty_rows()
        rows[-1]["case_id"] = rows[0]["case_id"]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evaluation.csv"
            write_dataset(path, rows)

            with self.assertRaisesRegex(ValueError, "duplicate case IDs"):
                read_evaluation_cases(path)

    def test_invalid_verification_outcome_is_rejected(self) -> None:
        """The evaluator must use one of the four frozen outcomes."""

        rows = make_thirty_rows()
        rows[4]["step_up_result_if_requested"] = "MAYBE"

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evaluation.csv"
            write_dataset(path, rows)

            with self.assertRaisesRegex(ValueError, "invalid step-up"):
                read_evaluation_cases(path)


class RecordingBaseline:
    """Test double that records exactly what the baseline receives."""

    def __init__(self) -> None:
        self.inputs: list[dict[str, str]] = []
        self.real_agent = BaselineAgent()

    def decide(self, evidence: dict[str, str]):
        """Record the input and delegate the actual decision."""

        self.inputs.append(dict(evidence))
        return self.real_agent.decide(evidence)


class RecordingPolicy1:
    """Test double that records both Policy 1 stages."""

    def __init__(self) -> None:
        self.initial_inputs: list[dict[str, str]] = []
        self.final_inputs: list[str | None] = []
        self.real_agent = Policy1Agent()

    def decide_initial(self, evidence: dict[str, str]):
        """Record initial evidence and delegate to the real policy."""

        self.initial_inputs.append(dict(evidence))
        return self.real_agent.decide_initial(evidence)

    def finalize(self, initial_decision, verification_result=None):
        """Record whether verification was exposed, then finalize."""

        self.final_inputs.append(verification_result)
        return self.real_agent.finalize(initial_decision, verification_result)


class TrackingRow(dict[str, str]):
    """Dictionary that counts reads of the hidden verification field."""

    def __init__(self, values: dict[str, str]) -> None:
        super().__init__(values)
        self.verification_reads = 0

    def __getitem__(self, key: str) -> str:
        if key == "step_up_result_if_requested":
            self.verification_reads += 1
        return super().__getitem__(key)


class TestEvaluationLeakageProtection(unittest.TestCase):
    """Verify that agent inputs exclude labels, narratives, and early checks."""

    def test_initial_evidence_uses_exactly_three_fields(self) -> None:
        """The allow-list must omit true state and verification."""

        evidence = build_initial_evidence(make_row(1))

        self.assertEqual(
            set(evidence),
            {
                "amount_deviation",
                "device_location_context",
                "recent_velocity",
            },
        )

    def test_baseline_never_receives_verification_or_true_state(self) -> None:
        """The baseline must receive the same three fields used in development."""

        recording_agent = RecordingBaseline()
        run_baseline_evaluation([make_row(1)], recording_agent)

        self.assertEqual(len(recording_agent.inputs), 1)
        self.assertNotIn("true_state", recording_agent.inputs[0])
        self.assertNotIn(
            "step_up_result_if_requested",
            recording_agent.inputs[0],
        )

    def test_policy1_reads_verification_only_after_request(self) -> None:
        """Low risk gets no check; an uncertain score-two case gets one."""

        low_risk = TrackingRow(make_row(1, verification="FAIL"))
        uncertain = TrackingRow(
            make_row(
                2,
                amount="HIGH",
                verification="PASS",
            )
        )
        recording_agent = RecordingPolicy1()

        results = run_policy1_evaluation(
            [low_risk, uncertain],
            recording_agent,
        )

        self.assertEqual(low_risk.verification_reads, 0)
        self.assertEqual(uncertain.verification_reads, 1)
        self.assertEqual(recording_agent.final_inputs, [None, "PASS"])
        self.assertEqual(results[0]["verification_request_count"], 0)
        self.assertEqual(results[1]["verification_request_count"], 1)
        for supplied in recording_agent.initial_inputs:
            self.assertNotIn("true_state", supplied)
            self.assertNotIn("step_up_result_if_requested", supplied)


class TestEvaluationComparison(unittest.TestCase):
    """Check metric meanings and the predeclared better-policy decision."""

    def setUp(self) -> None:
        """Create two small result sets with a safe review reduction."""

        rows = [
            make_row(1),
            make_row(
                2,
                true_state="LEGITIMATE",
                amount="HIGH",
                verification="PASS",
            ),
            make_row(
                3,
                true_state="FRAUDULENT",
                amount="HIGH",
                context="NEW_DEVICE_UNUSUAL_LOCATION",
                verification="FAIL",
            ),
        ]
        self.baseline_results = run_baseline_evaluation(rows)
        self.policy_results = run_policy1_evaluation(rows)
        self.baseline_metrics = calculate_metrics(
            self.baseline_results,
            "synthetic baseline",
        )
        self.policy_metrics = calculate_metrics(
            self.policy_results,
            "synthetic policy",
        )

    def test_human_review_is_deferred_not_correct(self) -> None:
        """Automatic accuracy must exclude the baseline review row."""

        self.assertEqual(self.baseline_metrics["human_review"], 1)
        self.assertEqual(self.baseline_metrics["automatic_decisions"], 2)
        self.assertEqual(
            self.baseline_metrics["correct_automatic_decisions"],
            2,
        )
        self.assertEqual(self.baseline_metrics["automatic_accuracy"], 1.0)

    def test_policy_is_better_only_when_every_gate_passes(self) -> None:
        """Safe review reduction must pass the frozen comparison gates."""

        comparison = compare_policies(
            self.baseline_results,
            self.policy_results,
            self.baseline_metrics,
            self.policy_metrics,
        )

        self.assertTrue(comparison["policy1_better_for_stated_objective"])
        self.assertTrue(all(comparison["criteria"].values()))

    def test_different_case_order_is_rejected(self) -> None:
        """Policies cannot be compared on differently ordered cases."""

        reversed_policy = list(reversed(self.policy_results))

        with self.assertRaisesRegex(ValueError, "same cases"):
            compare_policies(
                self.baseline_results,
                reversed_policy,
                self.baseline_metrics,
                self.policy_metrics,
            )

    def test_result_artifacts_can_be_written_and_read(self) -> None:
        """CSV, JSON, and Markdown writers must produce usable files."""

        comparison = compare_policies(
            self.baseline_results,
            self.policy_results,
            self.baseline_metrics,
            self.policy_metrics,
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "decisions.csv"
            json_path = root / "metrics.json"
            summary_path = root / "summary.md"

            write_csv(csv_path, self.policy_results)
            write_json(json_path, self.policy_metrics)
            write_comparison_summary(
                summary_path,
                self.baseline_metrics,
                self.policy_metrics,
                comparison,
            )

            with csv_path.open("r", encoding="utf-8", newline="") as file:
                written_rows = list(csv.DictReader(file))
            with json_path.open("r", encoding="utf-8") as file:
                written_metrics = json.load(file)
            summary = summary_path.read_text(encoding="utf-8")

        self.assertEqual(len(written_rows), 3)
        self.assertEqual(written_metrics["dataset_split"], "EVALUATION")
        self.assertIn("Held-Out Evaluation", summary)


if __name__ == "__main__":
    unittest.main()
