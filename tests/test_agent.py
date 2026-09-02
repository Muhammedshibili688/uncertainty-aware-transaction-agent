"""
Unit tests for the frozen v0.1 static baseline transaction agent.

These tests check the behaviour and safety boundaries of the baseline.
They do not test whether the agent is accurate on the complete dataset.
Dataset-level accuracy is measured separately by run_baseline.py.

The tests cover:

1. Risk-score boundaries.
2. APPROVE, HUMAN_REVIEW, and STOP actions.
3. Evidence point calculations.
4. Missing and unknown evidence.
5. Invalid evidence values.
6. Hidden-label leakage protection.
7. Deterministic behaviour.
8. Human-readable decision explanations.

Run from the project root with:

    python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path


# Add the project's src directory to Python's import path.
#
# When unittest starts from the repository root, Python does not
# automatically search inside src. Adding it here allows us to import
# agent.py without turning src into an installed Python package.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))


from agent import (  # noqa: E402
    BaselineAgent,
    BaselineDecision,
    MAXIMUM_RISK_SCORE,
    POLICY_NAME,
    POLICY_1_NAME,
    Policy1Agent,
    Policy1Decision,
    Policy1InitialDecision,
    score_to_action,
)


class TestScoreToAction(unittest.TestCase):
    """
    Test the function that converts a risk score into an action.

    These tests focus only on score thresholds. They do not test how
    evidence categories produce those scores.
    """

    def test_all_valid_score_boundaries(self) -> None:
        """
        Check every valid score from zero through six.

        Input:
            Risk scores from 0 to 6.

        Expected return:
            Scores 0–1 return APPROVE and LEGITIMATE.
            Scores 2–3 return HUMAN_REVIEW and None.
            Scores 4–6 return STOP and FRAUDULENT.

        What the test does:
            It calls score_to_action() for every possible score and
            compares the returned action and state with the frozen
            baseline thresholds.
        """

        expected_results = {
            0: ("APPROVE", "LEGITIMATE"),
            1: ("APPROVE", "LEGITIMATE"),
            2: ("HUMAN_REVIEW", None),
            3: ("HUMAN_REVIEW", None),
            4: ("STOP", "FRAUDULENT"),
            5: ("STOP", "FRAUDULENT"),
            6: ("STOP", "FRAUDULENT"),
        }

        for risk_score, expected in expected_results.items():
            with self.subTest(risk_score=risk_score):
                actual = score_to_action(risk_score)
                self.assertEqual(actual, expected)

    def test_negative_score_is_rejected(self) -> None:
        """
        Check that a score below zero raises an error.

        Input:
            Risk score -1.

        Expected return:
            No normal return value. ValueError must be raised.

        Why:
            Evidence points cannot create a negative baseline score.
            Accepting one would hide a scoring bug.
        """

        with self.assertRaisesRegex(
            ValueError,
            "Risk score must be between",
        ):
            score_to_action(-1)

    def test_score_above_maximum_is_rejected(self) -> None:
        """
        Check that a score above six raises an error.

        Input:
            Risk score 7.

        Expected return:
            No normal return value. ValueError must be raised.

        Why:
            Three evidence groups with a maximum of two points each
            cannot produce a score above six.
        """

        with self.assertRaisesRegex(
            ValueError,
            "Risk score must be between",
        ):
            score_to_action(MAXIMUM_RISK_SCORE + 1)


class TestBaselineAgent(unittest.TestCase):
    """
    Test the complete BaselineAgent decision process.

    Every test supplies only the three permitted initial evidence
    fields unless it is deliberately testing the leakage protection.
    """

    def setUp(self) -> None:
        """
        Create a fresh baseline agent before each test.

        Input:
            None.

        Returns:
            None.

        What happens:
            unittest automatically calls this method before every test
            method. Each test therefore starts with a clean agent.
        """

        self.agent = BaselineAgent()

    @staticmethod
    def normal_evidence() -> dict[str, str]:
        """
        Create a reusable normal-evidence example.

        Input:
            None.

        Returns:
            A dictionary containing:

            - NORMAL amount;
            - known device and usual location;
            - NORMAL recent velocity.

        Expected score:
            0 + 0 + 0 = 0.
        """

        return {
            "amount_deviation": "NORMAL",
            "device_location_context": (
                "KNOWN_DEVICE_USUAL_LOCATION"
            ),
            "recent_velocity": "NORMAL",
        }

    def test_normal_evidence_is_approved(self) -> None:
        """
        Check the lowest-risk baseline decision.

        Input:
            Normal amount, familiar context, and normal velocity.

        Expected return:
            Risk score 0.
            Action APPROVE.
            Predicted state LEGITIMATE.
        """

        decision = self.agent.decide(
            self.normal_evidence()
        )

        self.assertIsInstance(
            decision,
            BaselineDecision,
        )
        self.assertEqual(decision.policy_name, POLICY_NAME)
        self.assertEqual(decision.amount_points, 0)
        self.assertEqual(
            decision.device_location_points,
            0,
        )
        self.assertEqual(decision.velocity_points, 0)
        self.assertEqual(decision.risk_score, 0)
        self.assertEqual(decision.final_action, "APPROVE")
        self.assertEqual(
            decision.predicted_state,
            "LEGITIMATE",
        )

    def test_one_mild_warning_is_approved(self) -> None:
        """
        Check the highest score still permitted for approval.

        Input:
            Moderate amount, familiar context, and normal velocity.

        Expected return:
            Score 1.
            Action APPROVE.
            Predicted state LEGITIMATE.

        Why:
            One mild warning is not enough for the baseline to defer or
            stop the transaction.
        """

        evidence = self.normal_evidence()
        evidence["amount_deviation"] = "MODERATE"

        decision = self.agent.decide(evidence)

        self.assertEqual(decision.risk_score, 1)
        self.assertEqual(decision.final_action, "APPROVE")
        self.assertEqual(
            decision.predicted_state,
            "LEGITIMATE",
        )

    def test_one_strong_warning_is_sent_to_review(self) -> None:
        """
        Check that one strong warning creates uncertainty.

        Input:
            High amount, familiar context, and normal velocity.

        Expected return:
            Score 2.
            Action HUMAN_REVIEW.
            No automatic predicted state.

        Why:
            A high amount alone is not enough to declare fraud, but it
            is unusual enough to prevent automatic approval.
        """

        evidence = self.normal_evidence()
        evidence["amount_deviation"] = "HIGH"

        decision = self.agent.decide(evidence)

        self.assertEqual(decision.risk_score, 2)
        self.assertEqual(
            decision.final_action,
            "HUMAN_REVIEW",
        )
        self.assertIsNone(decision.predicted_state)

    def test_score_three_is_sent_to_review(self) -> None:
        """
        Check the upper human-review boundary.

        Input:
            High amount, known device at an unusual location, and
            normal velocity.

        Calculation:
            Amount HIGH = 2.
            Known device and unusual location = 1.
            Velocity NORMAL = 0.
            Total = 3.

        Expected return:
            HUMAN_REVIEW with no automatic predicted state.
        """

        evidence = {
            "amount_deviation": "HIGH",
            "device_location_context": (
                "KNOWN_DEVICE_UNUSUAL_LOCATION"
            ),
            "recent_velocity": "NORMAL",
        }

        decision = self.agent.decide(evidence)

        self.assertEqual(decision.risk_score, 3)
        self.assertEqual(
            decision.final_action,
            "HUMAN_REVIEW",
        )
        self.assertIsNone(decision.predicted_state)

    def test_score_four_is_stopped(self) -> None:
        """
        Check the minimum score required for STOP.

        Input:
            High amount, new device at an unusual location, and normal
            velocity.

        Calculation:
            Amount HIGH = 2.
            New device and unusual location = 2.
            Velocity NORMAL = 0.
            Total = 4.

        Expected return:
            STOP with predicted state FRAUDULENT.
        """

        evidence = {
            "amount_deviation": "HIGH",
            "device_location_context": (
                "NEW_DEVICE_UNUSUAL_LOCATION"
            ),
            "recent_velocity": "NORMAL",
        }

        decision = self.agent.decide(evidence)

        self.assertEqual(decision.risk_score, 4)
        self.assertEqual(decision.final_action, "STOP")
        self.assertEqual(
            decision.predicted_state,
            "FRAUDULENT",
        )

    def test_maximum_score_is_stopped(self) -> None:
        """
        Check the maximum possible baseline risk score.

        Input:
            High amount, new device at an unusual location, and high
            velocity.

        Calculation:
            2 + 2 + 2 = 6.

        Expected return:
            Risk score 6.
            STOP.
            Predicted state FRAUDULENT.
        """

        evidence = {
            "amount_deviation": "HIGH",
            "device_location_context": (
                "NEW_DEVICE_UNUSUAL_LOCATION"
            ),
            "recent_velocity": "HIGH",
        }

        decision = self.agent.decide(evidence)

        self.assertEqual(decision.amount_points, 2)
        self.assertEqual(
            decision.device_location_points,
            2,
        )
        self.assertEqual(decision.velocity_points, 2)
        self.assertEqual(decision.risk_score, 6)
        self.assertEqual(decision.final_action, "STOP")
        self.assertEqual(
            decision.predicted_state,
            "FRAUDULENT",
        )

    def test_unknown_evidence_is_accepted(self) -> None:
        """
        Check how the baseline handles completely missing evidence.

        Input:
            UNKNOWN for all three evidence groups.

        Calculation:
            UNKNOWN amount = 1.
            UNKNOWN device/location = 1.
            UNKNOWN velocity = 1.
            Total = 3.

        Expected return:
            HUMAN_REVIEW.

        Why:
            Missing information is treated as uncertainty. It is not
            silently converted into normal or fraudulent evidence.
        """

        evidence = {
            "amount_deviation": "UNKNOWN",
            "device_location_context": "UNKNOWN",
            "recent_velocity": "UNKNOWN",
        }

        decision = self.agent.decide(evidence)

        self.assertEqual(decision.amount_points, 1)
        self.assertEqual(
            decision.device_location_points,
            1,
        )
        self.assertEqual(decision.velocity_points, 1)
        self.assertEqual(decision.risk_score, 3)
        self.assertEqual(
            decision.final_action,
            "HUMAN_REVIEW",
        )
        self.assertIsNone(decision.predicted_state)

    def test_lowercase_and_spaces_are_normalized(self) -> None:
        """
        Check that harmless text formatting differences are accepted.

        Input:
            Valid category names written in lowercase with extra spaces.

        Expected return:
            The same result as clean uppercase evidence.

        What happens:
            BaselineAgent strips surrounding spaces and converts values
            to uppercase before validation.
        """

        evidence = {
            "amount_deviation": " normal ",
            "device_location_context": (
                " known_device_usual_location "
            ),
            "recent_velocity": " normal ",
        }

        decision = self.agent.decide(evidence)

        self.assertEqual(decision.risk_score, 0)
        self.assertEqual(decision.final_action, "APPROVE")

    def test_missing_evidence_field_is_rejected(self) -> None:
        """
        Check that the agent rejects incomplete input dictionaries.

        Input:
            Evidence without recent_velocity.

        Expected return:
            ValueError mentioning missing evidence fields.

        Why:
            The runner must supply all three frozen initial evidence
            fields, even when the field value is UNKNOWN.
        """

        incomplete_evidence = {
            "amount_deviation": "NORMAL",
            "device_location_context": (
                "KNOWN_DEVICE_USUAL_LOCATION"
            ),
        }

        with self.assertRaisesRegex(
            ValueError,
            "Missing agent evidence fields",
        ):
            self.agent.decide(incomplete_evidence)

    def test_hidden_true_state_is_rejected(self) -> None:
        """
        Check the protection against hidden-label leakage.

        Input:
            The three permitted evidence fields plus true_state.

        Expected return:
            ValueError explaining that an unexpected field was supplied.

        Why:
            The agent must make its decision before the evaluator reveals
            the correct hidden state.
        """

        leaked_evidence = self.normal_evidence()
        leaked_evidence["true_state"] = "FRAUDULENT"

        with self.assertRaisesRegex(
            ValueError,
            "not allowed to see",
        ):
            self.agent.decide(leaked_evidence)

    def test_verification_result_is_rejected(self) -> None:
        """
        Check that the baseline cannot access additional verification.

        Input:
            Normal initial evidence plus a step-up result.

        Expected return:
            ValueError because the baseline is not allowed to request or
            consume additional evidence.

        Why:
            Verification is reserved for Policy 1. Allowing it here
            would make the baseline comparison unfair.
        """

        leaked_evidence = self.normal_evidence()
        leaked_evidence[
            "step_up_result_if_requested"
        ] = "PASS"

        with self.assertRaisesRegex(
            ValueError,
            "not allowed to see",
        ):
            self.agent.decide(leaked_evidence)

    def test_invalid_category_values_are_rejected(self) -> None:
        """
        Check invalid values for each of the three evidence fields.

        Input:
            Three separate examples containing an unsupported category.

        Expected return:
            ValueError for every example.

        What happens:
            A subtest is run for amount, device/location, and velocity.
            Using subtests makes it clear which field failed if the test
            does not pass.
        """

        invalid_examples = [
            (
                "amount_deviation",
                "EXTREME",
            ),
            (
                "device_location_context",
                "FAMILIAR_DEVICE",
            ),
            (
                "recent_velocity",
                "VERY_HIGH",
            ),
        ]

        for field_name, invalid_value in invalid_examples:
            with self.subTest(
                field_name=field_name,
                invalid_value=invalid_value,
            ):
                evidence = self.normal_evidence()
                evidence[field_name] = invalid_value

                with self.assertRaisesRegex(
                    ValueError,
                    f"Invalid {field_name} value",
                ):
                    self.agent.decide(evidence)

    def test_repeated_decisions_are_deterministic(self) -> None:
        """
        Check that identical evidence always produces identical output.

        Input:
            The same evidence dictionary supplied twice.

        Expected return:
            Two equal BaselineDecision objects.

        Why:
            The baseline does not contain randomness. Reproducibility is
            necessary for comparing later policies fairly.
        """

        evidence = {
            "amount_deviation": "MODERATE",
            "device_location_context": (
                "NEW_DEVICE_USUAL_LOCATION"
            ),
            "recent_velocity": "ELEVATED",
        }

        first_decision = self.agent.decide(evidence)
        second_decision = self.agent.decide(evidence)

        self.assertEqual(
            first_decision,
            second_decision,
        )

    def test_decision_reason_contains_audit_information(self) -> None:
        """
        Check that the explanation records the important calculation.

        Input:
            High amount, unfamiliar context, and high velocity.

        Expected return:
            A reason containing each normalized evidence category,
            the total score, and the selected action.

        Why:
            The output must be understandable and auditable rather than
            returning only an unexplained action.
        """

        evidence = {
            "amount_deviation": "HIGH",
            "device_location_context": (
                "NEW_DEVICE_UNUSUAL_LOCATION"
            ),
            "recent_velocity": "HIGH",
        }

        decision = self.agent.decide(evidence)

        self.assertIn(
            "Amount category HIGH",
            decision.reason,
        )
        self.assertIn(
            "NEW_DEVICE_UNUSUAL_LOCATION",
            decision.reason,
        )
        self.assertIn(
            "Velocity category HIGH",
            decision.reason,
        )
        self.assertIn(
            "total risk score was 6",
            decision.reason,
        )
        self.assertIn(
            "selected action was STOP",
            decision.reason,
        )


class TestPolicy1Agent(unittest.TestCase):
    """Test Policy 1's selective, single-verification decision sequence."""

    def setUp(self) -> None:
        """Create a new Policy 1 agent for every unit test."""

        self.agent = Policy1Agent()

    @staticmethod
    def evidence_for_score(
        amount: str,
        context: str,
        velocity: str,
    ) -> dict[str, str]:
        """Return an initial-evidence dictionary for a chosen test pattern."""

        return {
            "amount_deviation": amount,
            "device_location_context": context,
            "recent_velocity": velocity,
        }

    def test_low_score_is_terminal_without_verification(self) -> None:
        """Score zero must approve without exposing step-up evidence."""

        evidence = self.evidence_for_score(
            "NORMAL",
            "KNOWN_DEVICE_USUAL_LOCATION",
            "NORMAL",
        )

        initial = self.agent.decide_initial(evidence)
        final = self.agent.finalize(initial)

        self.assertIsInstance(initial, Policy1InitialDecision)
        self.assertIsInstance(final, Policy1Decision)
        self.assertEqual(initial.policy_name, POLICY_1_NAME)
        self.assertEqual(initial.initial_action, "APPROVE")
        self.assertFalse(initial.verification_requested)
        self.assertEqual(
            final.verification_result_observed,
            "NOT_REQUESTED",
        )
        self.assertEqual(final.final_action, "APPROVE")
        self.assertEqual(final.predicted_state, "LEGITIMATE")

    def test_score_two_requests_verification(self) -> None:
        """The lower uncertain boundary must request the one extra check."""

        evidence = self.evidence_for_score(
            "HIGH",
            "KNOWN_DEVICE_USUAL_LOCATION",
            "NORMAL",
        )

        initial = self.agent.decide_initial(evidence)

        self.assertEqual(initial.initial_risk_score, 2)
        self.assertEqual(initial.initial_action, "GET_MORE_EVIDENCE")
        self.assertTrue(initial.verification_requested)

    def test_score_three_requests_verification(self) -> None:
        """The upper uncertain boundary must request the one extra check."""

        evidence = self.evidence_for_score(
            "HIGH",
            "KNOWN_DEVICE_UNUSUAL_LOCATION",
            "NORMAL",
        )

        initial = self.agent.decide_initial(evidence)

        self.assertEqual(initial.initial_risk_score, 3)
        self.assertEqual(initial.initial_action, "GET_MORE_EVIDENCE")
        self.assertTrue(initial.verification_requested)

    def test_high_score_is_terminal_without_verification(self) -> None:
        """Score four must stop without exposing unnecessary evidence."""

        evidence = self.evidence_for_score(
            "HIGH",
            "NEW_DEVICE_UNUSUAL_LOCATION",
            "NORMAL",
        )

        initial = self.agent.decide_initial(evidence)
        final = self.agent.finalize(initial)

        self.assertEqual(initial.initial_risk_score, 4)
        self.assertEqual(initial.initial_action, "STOP")
        self.assertFalse(initial.verification_requested)
        self.assertEqual(
            final.verification_result_observed,
            "NOT_REQUESTED",
        )
        self.assertEqual(final.final_action, "STOP")
        self.assertEqual(final.predicted_state, "FRAUDULENT")

    def test_pass_subtracts_one_point(self) -> None:
        """PASS must reduce score two to one without proving legitimacy."""

        evidence = self.evidence_for_score(
            "HIGH",
            "KNOWN_DEVICE_USUAL_LOCATION",
            "NORMAL",
        )

        initial = self.agent.decide_initial(evidence)
        final = self.agent.finalize(initial, "PASS")

        self.assertEqual(final.verification_score_adjustment, -1)
        self.assertEqual(final.final_risk_score, 1)
        self.assertEqual(final.final_action, "APPROVE")
        self.assertEqual(final.predicted_state, "LEGITIMATE")

    def test_pass_does_not_automatically_approve_score_three(self) -> None:
        """PASS lowers score three to two, which still needs human review."""

        evidence = self.evidence_for_score(
            "HIGH",
            "KNOWN_DEVICE_UNUSUAL_LOCATION",
            "NORMAL",
        )

        initial = self.agent.decide_initial(evidence)
        final = self.agent.finalize(initial, "PASS")

        self.assertEqual(final.final_risk_score, 2)
        self.assertEqual(final.final_action, "HUMAN_REVIEW")
        self.assertIsNone(final.predicted_state)

    def test_fail_adds_one_point(self) -> None:
        """FAIL must increase score three to four and produce STOP."""

        evidence = self.evidence_for_score(
            "HIGH",
            "KNOWN_DEVICE_UNUSUAL_LOCATION",
            "NORMAL",
        )

        initial = self.agent.decide_initial(evidence)
        final = self.agent.finalize(initial, "FAIL")

        self.assertEqual(final.verification_score_adjustment, 1)
        self.assertEqual(final.final_risk_score, 4)
        self.assertEqual(final.final_action, "STOP")
        self.assertEqual(final.predicted_state, "FRAUDULENT")

    def test_inconclusive_and_unavailable_leave_score_unchanged(self) -> None:
        """Non-resolving outcomes must keep an uncertain case in review."""

        evidence = self.evidence_for_score(
            "HIGH",
            "KNOWN_DEVICE_USUAL_LOCATION",
            "NORMAL",
        )
        initial = self.agent.decide_initial(evidence)

        for result in ("INCONCLUSIVE", "UNAVAILABLE"):
            with self.subTest(result=result):
                final = self.agent.finalize(initial, result)
                self.assertEqual(final.verification_score_adjustment, 0)
                self.assertEqual(final.final_risk_score, 2)
                self.assertEqual(final.final_action, "HUMAN_REVIEW")
                self.assertIsNone(final.predicted_state)

    def test_requested_verification_result_is_required(self) -> None:
        """An initial evidence request cannot be finalized with no result."""

        evidence = self.evidence_for_score(
            "HIGH",
            "KNOWN_DEVICE_USUAL_LOCATION",
            "NORMAL",
        )
        initial = self.agent.decide_initial(evidence)

        with self.assertRaisesRegex(
            ValueError,
            "verification result is required",
        ):
            self.agent.finalize(initial)

    def test_unrequested_verification_is_rejected(self) -> None:
        """A terminal low-risk case must not receive hidden step-up evidence."""

        evidence = self.evidence_for_score(
            "NORMAL",
            "KNOWN_DEVICE_USUAL_LOCATION",
            "NORMAL",
        )
        initial = self.agent.decide_initial(evidence)

        with self.assertRaisesRegex(
            ValueError,
            "cannot be supplied",
        ):
            self.agent.finalize(initial, "PASS")

    def test_invalid_verification_result_is_rejected(self) -> None:
        """Only the four frozen observed verification values are accepted."""

        evidence = self.evidence_for_score(
            "HIGH",
            "KNOWN_DEVICE_USUAL_LOCATION",
            "NORMAL",
        )
        initial = self.agent.decide_initial(evidence)

        with self.assertRaisesRegex(
            ValueError,
            "Invalid verification result",
        ):
            self.agent.finalize(initial, "SUCCESS")

    def test_hidden_true_state_is_rejected_at_initial_stage(self) -> None:
        """Policy 1 must retain the baseline's hidden-label leakage guard."""

        evidence = self.evidence_for_score(
            "NORMAL",
            "KNOWN_DEVICE_USUAL_LOCATION",
            "NORMAL",
        )
        evidence["true_state"] = "FRAUDULENT"

        with self.assertRaisesRegex(ValueError, "not allowed to see"):
            self.agent.decide_initial(evidence)

    def test_every_verification_outcome_is_terminal(self) -> None:
        """Policy 1 must never request a second verification."""

        evidence = self.evidence_for_score(
            "HIGH",
            "KNOWN_DEVICE_USUAL_LOCATION",
            "NORMAL",
        )
        initial = self.agent.decide_initial(evidence)

        for result in ("PASS", "FAIL", "INCONCLUSIVE", "UNAVAILABLE"):
            with self.subTest(result=result):
                final = self.agent.finalize(initial, result)
                self.assertIn(
                    final.final_action,
                    {"APPROVE", "HUMAN_REVIEW", "STOP"},
                )
                self.assertNotEqual(
                    final.final_action,
                    "GET_MORE_EVIDENCE",
                )

    def test_policy_1_is_deterministic(self) -> None:
        """Identical initial and verification evidence must repeat exactly."""

        evidence = self.evidence_for_score(
            "MODERATE",
            "NEW_DEVICE_USUAL_LOCATION",
            "NORMAL",
        )

        first_initial = self.agent.decide_initial(evidence)
        first_final = self.agent.finalize(first_initial, "PASS")
        second_initial = self.agent.decide_initial(evidence)
        second_final = self.agent.finalize(second_initial, "PASS")

        self.assertEqual(first_initial, second_initial)
        self.assertEqual(first_final, second_final)


if __name__ == "__main__":
    unittest.main()
