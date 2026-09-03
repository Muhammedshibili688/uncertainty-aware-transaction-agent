"""Unit and development-boundary tests for Policy 2 v0.2.

These tests do not open or execute the v0.2 evaluation CSV.
"""

import csv
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"
if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))


from agent import (  # noqa: E402
    POLICY_2_NAME,
    Policy2Agent,
    policy2_verification_adjustment,
)
from run_policy2 import (  # noqa: E402
    CONFIG_FILE,
    DATA_FILE,
    check_success_criteria,
    calculate_metrics,
    initial_evidence,
    load_and_validate_config,
    read_development_cases,
    run_baseline,
    run_policy1,
    run_policy2,
)


class TestPolicy2Agent(unittest.TestCase):
    """Check Policy 2's complete two-stage decision contract."""

    def setUp(self) -> None:
        """Create a fresh deterministic policy for every test."""

        self.agent = Policy2Agent()

    @staticmethod
    def evidence(
        amount: str = "NORMAL",
        context: str = "KNOWN_DEVICE_USUAL_LOCATION",
        velocity: str = "NORMAL",
    ) -> dict[str, str]:
        """Return exactly the three permitted initial evidence fields."""

        return {
            "amount_deviation": amount,
            "device_location_context": context,
            "recent_velocity": velocity,
        }

    def test_low_score_approves_without_verification(self) -> None:
        """Score zero must remain a terminal approval."""

        initial = self.agent.decide_initial(self.evidence())
        final = self.agent.finalize(initial)

        self.assertEqual(initial.policy_name, POLICY_2_NAME)
        self.assertEqual(initial.initial_risk_score, 0)
        self.assertEqual(initial.initial_action, "APPROVE")
        self.assertFalse(initial.verification_requested)
        self.assertEqual(final.final_action, "APPROVE")
        self.assertEqual(
            final.verification_independence_observed,
            "NOT_REQUESTED",
        )

    def test_scores_two_and_three_request_verification(self) -> None:
        """Both uncertain score boundaries must request one check."""

        score_two = self.agent.decide_initial(self.evidence(amount="HIGH"))
        score_three = self.agent.decide_initial(
            self.evidence(
                amount="HIGH",
                context="KNOWN_DEVICE_UNUSUAL_LOCATION",
            )
        )

        self.assertEqual(score_two.initial_risk_score, 2)
        self.assertTrue(score_two.verification_requested)
        self.assertEqual(score_three.initial_risk_score, 3)
        self.assertTrue(score_three.verification_requested)

    def test_high_score_stops_without_verification(self) -> None:
        """Score four must remain a terminal stop."""

        initial = self.agent.decide_initial(
            self.evidence(
                amount="HIGH",
                context="NEW_DEVICE_UNUSUAL_LOCATION",
            )
        )
        final = self.agent.finalize(initial)

        self.assertEqual(initial.initial_risk_score, 4)
        self.assertFalse(initial.verification_requested)
        self.assertEqual(final.final_action, "STOP")
        self.assertEqual(final.predicted_state, "FRAUDULENT")

    def test_independent_pass_can_lower_score(self) -> None:
        """An independent PASS must move score two to approval score one."""

        initial = self.agent.decide_initial(self.evidence(amount="HIGH"))
        final = self.agent.finalize(initial, "PASS", "INDEPENDENT")

        self.assertEqual(final.verification_score_adjustment, -1)
        self.assertEqual(final.final_risk_score, 1)
        self.assertEqual(final.final_action, "APPROVE")

    def test_same_channel_pass_does_not_lower_score(self) -> None:
        """A same-channel PASS must leave score two in human review."""

        initial = self.agent.decide_initial(self.evidence(amount="HIGH"))
        final = self.agent.finalize(initial, "PASS", "SAME_CHANNEL")

        self.assertEqual(final.verification_score_adjustment, 0)
        self.assertEqual(final.final_risk_score, 2)
        self.assertEqual(final.final_action, "HUMAN_REVIEW")

    def test_unknown_independence_pass_does_not_lower_score(self) -> None:
        """An unverified source relationship must not create reassurance."""

        initial = self.agent.decide_initial(self.evidence(amount="HIGH"))
        final = self.agent.finalize(initial, "PASS", "UNKNOWN")

        self.assertEqual(final.verification_score_adjustment, 0)
        self.assertEqual(final.final_action, "HUMAN_REVIEW")

    def test_fail_adds_one_regardless_of_independence(self) -> None:
        """Every valid FAIL source must increase risk by one point."""

        for independence in ("INDEPENDENT", "SAME_CHANNEL", "UNKNOWN"):
            with self.subTest(independence=independence):
                initial = self.agent.decide_initial(
                    self.evidence(
                        amount="HIGH",
                        context="KNOWN_DEVICE_UNUSUAL_LOCATION",
                    )
                )
                final = self.agent.finalize(
                    initial,
                    "FAIL",
                    independence,
                )
                self.assertEqual(final.verification_score_adjustment, 1)
                self.assertEqual(final.final_risk_score, 4)
                self.assertEqual(final.final_action, "STOP")

    def test_unresolved_results_leave_score_unchanged(self) -> None:
        """INCONCLUSIVE and UNAVAILABLE must preserve the initial score."""

        for result in ("INCONCLUSIVE", "UNAVAILABLE"):
            with self.subTest(result=result):
                initial = self.agent.decide_initial(self.evidence(amount="HIGH"))
                final = self.agent.finalize(initial, result, "UNKNOWN")
                self.assertEqual(final.verification_score_adjustment, 0)
                self.assertEqual(final.final_risk_score, 2)
                self.assertEqual(final.final_action, "HUMAN_REVIEW")

    def test_both_requested_values_are_required(self) -> None:
        """A requested check cannot finish with either value missing."""

        initial = self.agent.decide_initial(self.evidence(amount="HIGH"))

        with self.assertRaisesRegex(ValueError, "result is required"):
            self.agent.finalize(initial)
        with self.assertRaisesRegex(ValueError, "independence is required"):
            self.agent.finalize(initial, "PASS")

    def test_unrequested_additional_evidence_is_rejected(self) -> None:
        """Terminal low-risk decisions must not receive hidden evidence."""

        initial = self.agent.decide_initial(self.evidence())

        with self.assertRaisesRegex(ValueError, "cannot be supplied"):
            self.agent.finalize(initial, "PASS", "INDEPENDENT")

    def test_invalid_additional_categories_are_rejected(self) -> None:
        """Unknown result and independence labels must raise clear errors."""

        initial = self.agent.decide_initial(self.evidence(amount="HIGH"))

        with self.assertRaisesRegex(ValueError, "Invalid Policy 2 verification"):
            self.agent.finalize(initial, "SUCCESS", "INDEPENDENT")
        with self.assertRaisesRegex(ValueError, "Invalid Policy 2 verification"):
            self.agent.finalize(initial, "PASS", "DEPENDENT")

    def test_hidden_true_state_is_rejected(self) -> None:
        """Policy 2 must preserve the baseline hidden-label guard."""

        evidence = self.evidence()
        evidence["true_state"] = "FRAUDULENT"

        with self.assertRaisesRegex(ValueError, "not allowed to see"):
            self.agent.decide_initial(evidence)

    def test_every_verification_combination_is_terminal(self) -> None:
        """Policy 2 must never ask for a second check."""

        for result in ("PASS", "FAIL", "INCONCLUSIVE", "UNAVAILABLE"):
            for independence in ("INDEPENDENT", "SAME_CHANNEL", "UNKNOWN"):
                with self.subTest(result=result, independence=independence):
                    initial = self.agent.decide_initial(
                        self.evidence(amount="HIGH")
                    )
                    final = self.agent.finalize(
                        initial,
                        result,
                        independence,
                    )
                    self.assertIn(
                        final.final_action,
                        {"APPROVE", "HUMAN_REVIEW", "STOP"},
                    )

    def test_adjustment_helper_is_case_insensitive(self) -> None:
        """Harmless spaces and lowercase text must be normalized."""

        self.assertEqual(
            policy2_verification_adjustment(" pass ", " independent "),
            -1,
        )


class TrackingRow(dict[str, str]):
    """Count attempts to read the two conditionally hidden columns."""

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


class TestPolicy2DevelopmentRunner(unittest.TestCase):
    """Check the development-only data and leakage boundaries."""

    def test_frozen_config_matches_code(self) -> None:
        """The checked-in parameter file must agree with the implementation."""

        config = load_and_validate_config(CONFIG_FILE)
        self.assertEqual(config["dataset_version"], "v0.2")

    def test_real_development_file_has_only_ten_development_rows(self) -> None:
        """Validate the intended development input without opening evaluation."""

        rows = read_development_cases(DATA_FILE)
        self.assertEqual(len(rows), 10)
        self.assertEqual({row["split"] for row in rows}, {"DEVELOPMENT"})

    def test_initial_allow_list_contains_only_three_fields(self) -> None:
        """No hidden or narrative field may enter the first agent call."""

        row = read_development_cases(DATA_FILE)[0]
        evidence = initial_evidence(row)

        self.assertEqual(
            set(evidence),
            {
                "amount_deviation",
                "device_location_context",
                "recent_velocity",
            },
        )

    def test_policy2_reads_additional_evidence_only_after_request(self) -> None:
        """Score zero reads nothing; score two reads both fields once."""

        common = {
            "split": "DEVELOPMENT",
            "true_state": "LEGITIMATE",
            "device_location_context": "KNOWN_DEVICE_USUAL_LOCATION",
            "recent_velocity": "NORMAL",
            "step_up_result_if_requested": "PASS",
            "verification_independence_if_requested": "INDEPENDENT",
        }
        low = TrackingRow(
            {"case_id": "LOW", "amount_deviation": "NORMAL", **common}
        )
        uncertain = TrackingRow(
            {"case_id": "UNCERTAIN", "amount_deviation": "HIGH", **common}
        )

        run_policy2([low, uncertain])

        self.assertEqual((low.result_reads, low.independence_reads), (0, 0))
        self.assertEqual(
            (uncertain.result_reads, uncertain.independence_reads),
            (1, 1),
        )

    def test_reader_rejects_evaluation_rows_and_duplicates(self) -> None:
        """Synthetic invalid files must not cross the development boundary."""

        rows = read_development_cases(DATA_FILE)
        fieldnames = list(rows[0].keys())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evaluation_path = root / "evaluation-row.csv"
            duplicate_path = root / "duplicates.csv"

            evaluation_rows = [dict(row) for row in rows]
            evaluation_rows[0]["split"] = "EVALUATION"
            with evaluation_path.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(evaluation_rows)

            duplicate_rows = [dict(row) for row in rows]
            duplicate_rows[-1]["case_id"] = duplicate_rows[0]["case_id"]
            with duplicate_path.open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(duplicate_rows)

            with self.assertRaisesRegex(ValueError, "not DEVELOPMENT"):
                read_development_cases(evaluation_path)
            with self.assertRaisesRegex(ValueError, "duplicate case IDs"):
                read_development_cases(duplicate_path)

    def test_frozen_development_criteria_are_machine_checkable(self) -> None:
        """The three policies must produce a complete criteria dictionary."""

        rows = read_development_cases(DATA_FILE)
        baseline_results = run_baseline(rows)
        policy1_results = run_policy1(rows)
        policy2_results = run_policy2(rows)
        criteria = check_success_criteria(
            calculate_metrics(baseline_results),
            calculate_metrics(policy1_results),
            calculate_metrics(policy2_results),
            policy2_results,
        )

        self.assertEqual(len(criteria), 9)
        self.assertEqual(
            set(criteria.values()).issubset({True, False}),
            True,
        )


if __name__ == "__main__":
    unittest.main()
