"""
Static baseline transaction agent for the v0.1 experiment.

This module contains the decision-making logic for the first baseline
agent.

The baseline receives only three pieces of information:

1. How unusual the transaction amount is.
2. Whether the device and location are familiar.
3. Whether there have been an unusual number of recent attempts.

Each piece of evidence is converted into a small number of risk points.
The points are added together, and the total score determines the
action.

This is intentionally a simple baseline. It does not:

- request additional verification;
- calculate a real fraud probability;
- learn from historical cases;
- use the hidden true state;
- treat correlated evidence specially.

The purpose of the baseline is to give us a realistic starting system
that can later be compared with Policy 1 and Policy 2.
"""

from dataclasses import dataclass
from typing import Mapping, Optional, Tuple


POLICY_NAME = "baseline_static_v0.1"

# These are the only fields that the baseline agent is permitted to see.
REQUIRED_EVIDENCE = {
    "amount_deviation",
    "device_location_context",
    "recent_velocity",
}


# Risk points assigned to the amount category.
#
# NORMAL receives zero because the amount is inside the expected range.
# MODERATE receives one because it is unusual but not extremely unusual.
# HIGH receives two because it is strongly different from past behaviour.
# UNKNOWN receives one because missing information should not be treated
# as completely safe or definitely fraudulent.
AMOUNT_POINTS = {
    "NORMAL": 0,
    "MODERATE": 1,
    "HIGH": 2,
    "UNKNOWN": 1,
}


# Risk points assigned to the combined device and location category.
#
# A known device at the usual location receives zero points.
# A new device or unusual location creates one mild warning.
# A new device together with an unusual location creates two points.
# UNKNOWN receives one point because the missing information creates
# uncertainty.
DEVICE_LOCATION_POINTS = {
    "KNOWN_DEVICE_USUAL_LOCATION": 0,
    "KNOWN_DEVICE_UNUSUAL_LOCATION": 1,
    "NEW_DEVICE_USUAL_LOCATION": 1,
    "NEW_DEVICE_UNUSUAL_LOCATION": 2,
    "UNKNOWN": 1,
}


# Risk points assigned to recent transaction velocity.
#
# NORMAL means the recent activity is within the customer's usual range.
# ELEVATED is unusual but not extreme.
# HIGH means the activity is much faster than normal.
# UNKNOWN represents missing historical or current velocity information.
VELOCITY_POINTS = {
    "NORMAL": 0,
    "ELEVATED": 1,
    "HIGH": 2,
    "UNKNOWN": 1,
}


# The three evidence groups can contribute a maximum of two points each.
MAXIMUM_RISK_SCORE = 6

# Scores from zero to one are approved automatically.
APPROVE_MAXIMUM_SCORE = 1

# Scores from two to three are sent to a person for review.
HUMAN_REVIEW_MAXIMUM_SCORE = 3

# A score above three, meaning four to six, is stopped.
STOP_MINIMUM_SCORE = 4


@dataclass(frozen=True)
class BaselineDecision:
    """
    Store one complete decision made by the baseline agent.

    This class is only a structured container. It does not make the
    decision itself. The BaselineAgent creates and returns one instance
    of this class for every transaction.

    Attributes:
        policy_name:
            Name and version of the policy that produced the decision.
            This allows us to distinguish baseline results from Policy 1
            and Policy 2 results later.

        amount_points:
            Risk points contributed by the amount category.

        device_location_points:
            Risk points contributed by the combined device and location
            category.

        velocity_points:
            Risk points contributed by the recent-velocity category.

        risk_score:
            Total risk score after adding the three point values.

        final_action:
            Action selected by the baseline. It will be APPROVE,
            HUMAN_REVIEW, or STOP.

        predicted_state:
            State implied by an automatic action.

            APPROVE means predicted LEGITIMATE.
            STOP means predicted FRAUDULENT.
            HUMAN_REVIEW has no automatic prediction, so the value is
            None.

        reason:
            Human-readable explanation showing how the score and action
            were produced.
    """

    policy_name: str
    amount_points: int
    device_location_points: int
    velocity_points: int
    risk_score: int
    final_action: str
    predicted_state: Optional[str]
    reason: str


def score_to_action(
    risk_score: int,
) -> Tuple[str, Optional[str]]:
    """
    Convert the total risk score into an action and predicted state.

    Input:
        risk_score:
            Integer risk score calculated by adding amount points,
            device/location points, and velocity points.

            The lowest valid value is zero.
            The highest valid value is six.

    Returns:
        A two-item tuple containing:

        1. final_action:
           APPROVE, HUMAN_REVIEW, or STOP.

        2. predicted_state:
           LEGITIMATE when the action is APPROVE.
           FRAUDULENT when the action is STOP.
           None when the action is HUMAN_REVIEW.

    What happens inside:
        1. The function first checks that the score is inside the valid
           range of zero to six.
        2. Scores zero and one are treated as low risk.
        3. Scores two and three are treated as uncertain.
        4. Scores four to six are treated as high risk.

    Raises:
        ValueError:
            Raised when the score is below zero or above six. Such a
            value would mean that there is an error in the scoring
            logic.
    """

    if not 0 <= risk_score <= MAXIMUM_RISK_SCORE:
        raise ValueError(
            f"Risk score must be between 0 and "
            f"{MAXIMUM_RISK_SCORE}, but received {risk_score}."
        )

    if risk_score <= APPROVE_MAXIMUM_SCORE:
        return "APPROVE", "LEGITIMATE"

    if risk_score <= HUMAN_REVIEW_MAXIMUM_SCORE:
        return "HUMAN_REVIEW", None

    return "STOP", "FRAUDULENT"


class BaselineAgent:
    """
    Make a transaction decision using a static risk-score baseline.

    Input:
        The agent receives a dictionary containing exactly three
        evidence fields:

        - amount_deviation
        - device_location_context
        - recent_velocity

    Output:
        The agent returns a BaselineDecision object containing:

        - evidence-point contributions;
        - total risk score;
        - selected action;
        - predicted state, if automatically decided;
        - explanation of the decision.

    What happens inside:
        1. The agent checks that it received exactly the allowed fields.
        2. It cleans each value by removing extra spaces and converting
           it to uppercase.
        3. It checks that every value belongs to the frozen v0.1
           categories.
        4. It converts each evidence value into risk points.
        5. It adds the points.
        6. It converts the total score into an action.
        7. It returns an auditable decision record.

    Important limitation:
        The agent assumes that points can simply be added together.
        This may incorrectly double-count correlated evidence. That is
        an intentional baseline limitation that a later policy may
        address.
    """

    def decide(
        self,
        evidence: Mapping[str, str],
    ) -> BaselineDecision:
        """
        Make one baseline decision from the initial evidence.

        Input:
            evidence:
                Dictionary containing exactly these keys:

                {
                    "amount_deviation": str,
                    "device_location_context": str,
                    "recent_velocity": str
                }

                The dictionary must not contain true_state, scenario
                description, verification result, case name, or any
                other hidden information.

        Returns:
            BaselineDecision:
                An object containing the point contributions, total
                score, final action, predicted state, and explanation.

        What happens inside:
            1. Compare the received field names with the permitted field
               names.
            2. Reject missing or unexpected fields.
            3. Standardize each category value.
            4. Validate each category.
            5. Look up the risk points for each category.
            6. Add the three point values.
            7. Pass the total to score_to_action().
            8. Prepare a readable explanation.
            9. Return the completed BaselineDecision.

        Raises:
            ValueError:
                Raised when a required field is missing, an unexpected
                field is supplied, or an evidence value is invalid.
        """

        received_fields = set(evidence.keys())

        missing_fields = REQUIRED_EVIDENCE - received_fields
        unexpected_fields = received_fields - REQUIRED_EVIDENCE

        if missing_fields:
            raise ValueError(
                "Missing agent evidence fields: "
                f"{sorted(missing_fields)}"
            )

        if unexpected_fields:
            raise ValueError(
                "The baseline received fields it is not allowed to see: "
                f"{sorted(unexpected_fields)}"
            )

        amount = evidence["amount_deviation"].strip().upper()

        device_location = (
            evidence["device_location_context"]
            .strip()
            .upper()
        )

        velocity = (
            evidence["recent_velocity"]
            .strip()
            .upper()
        )

        self._validate_value(
            field_name="amount_deviation",
            value=amount,
            allowed_values=AMOUNT_POINTS,
        )

        self._validate_value(
            field_name="device_location_context",
            value=device_location,
            allowed_values=DEVICE_LOCATION_POINTS,
        )

        self._validate_value(
            field_name="recent_velocity",
            value=velocity,
            allowed_values=VELOCITY_POINTS,
        )

        amount_points = AMOUNT_POINTS[amount]

        device_location_points = (
            DEVICE_LOCATION_POINTS[device_location]
        )

        velocity_points = VELOCITY_POINTS[velocity]

        risk_score = (
            amount_points
            + device_location_points
            + velocity_points
        )

        final_action, predicted_state = score_to_action(
            risk_score
        )

        reason = (
            f"Amount category {amount} contributed "
            f"{amount_points} point(s). "
            f"Device/location category {device_location} "
            f"contributed {device_location_points} point(s). "
            f"Velocity category {velocity} contributed "
            f"{velocity_points} point(s). "
            f"The total risk score was {risk_score} out of "
            f"{MAXIMUM_RISK_SCORE}. "
            f"The selected action was {final_action}."
        )

        return BaselineDecision(
            policy_name=POLICY_NAME,
            amount_points=amount_points,
            device_location_points=device_location_points,
            velocity_points=velocity_points,
            risk_score=risk_score,
            final_action=final_action,
            predicted_state=predicted_state,
            reason=reason,
        )

    @staticmethod
    def _validate_value(
        field_name: str,
        value: str,
        allowed_values: Mapping[str, int],
    ) -> None:
        """
        Check whether one evidence value belongs to its allowed categories.

        Input:
            field_name:
                Name of the evidence field being checked. This is used
                to create a useful error message.

            value:
                Evidence value received from the CSV after it has been
                converted to uppercase.

            allowed_values:
                Dictionary containing the valid category names. The
                dictionary values contain their assigned risk points.

        Returns:
            None:
                The function returns nothing when the value is valid.
                Successful completion means the caller can safely use
                the value.

        What happens inside:
            1. Check whether the supplied value exists as a key in the
               allowed-values dictionary.
            2. If it exists, allow the program to continue.
            3. If it does not exist, stop the decision and raise an
               informative error.

        Raises:
            ValueError:
                Raised when the evidence value is not part of the frozen
                v0.1 categories.
        """

        if value not in allowed_values:
            raise ValueError(
                f"Invalid {field_name} value: {value!r}. "
                f"Allowed values: {sorted(allowed_values)}"
            )