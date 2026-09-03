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


# Policy 1 keeps the baseline's initial score so that the comparison changes
# only one capability: selective access to a single step-up verification.
POLICY_1_NAME = "policy1_step_up_v0.1"
POLICY_1_REQUEST_MINIMUM_SCORE = 2
POLICY_1_REQUEST_MAXIMUM_SCORE = 3
POLICY_1_MAXIMUM_VERIFICATION_REQUESTS = 1

VERIFICATION_SCORE_ADJUSTMENTS = {
    "PASS": -1,
    "FAIL": 1,
    "INCONCLUSIVE": 0,
    "UNAVAILABLE": 0,
}


@dataclass(frozen=True)
class Policy1InitialDecision:
    """
    Store Policy 1's decision before additional evidence is revealed.

    The object contains the baseline-derived evidence points and initial score,
    plus the action selected at the first decision point.  A score of two or
    three produces GET_MORE_EVIDENCE.  Low- and high-risk scores are terminal
    immediately and therefore do not receive the hidden verification result.
    """

    policy_name: str
    amount_points: int
    device_location_points: int
    velocity_points: int
    initial_risk_score: int
    initial_action: str
    verification_requested: bool
    reason: str


@dataclass(frozen=True)
class Policy1Decision:
    """
    Store the complete and auditable result of one Policy 1 decision.

    Attributes record both decision stages.  ``verification_result_observed``
    is NOT_REQUESTED for terminal initial actions.  For uncertain cases it is
    PASS, FAIL, INCONCLUSIVE, or UNAVAILABLE.  The final action is always
    APPROVE, HUMAN_REVIEW, or STOP; Policy 1 cannot request a second check.
    """

    policy_name: str
    amount_points: int
    device_location_points: int
    velocity_points: int
    initial_risk_score: int
    initial_action: str
    verification_requested: bool
    verification_result_observed: str
    verification_score_adjustment: int
    final_risk_score: int
    final_action: str
    predicted_state: Optional[str]
    reason: str


class Policy1Agent:
    """
    Add one selective step-up verification to the frozen baseline score.

    Input:
        The first stage receives exactly the same three initial evidence fields
        as the baseline.  The second stage receives a verification result only
        when the first stage returned GET_MORE_EVIDENCE.

    Output:
        ``decide_initial`` returns ``Policy1InitialDecision``.
        ``finalize`` returns ``Policy1Decision`` with a terminal action.

    What happens inside:
        1. Reuse the frozen baseline calculation to obtain an initial score.
        2. Approve scores zero to one without requesting verification.
        3. Request verification for scores two to three.
        4. Stop scores four to six without requesting verification.
        5. When verification was requested, adjust the score by one point for
           PASS or FAIL, and by zero for INCONCLUSIVE or UNAVAILABLE.
        6. Apply the original baseline terminal thresholds to the updated score.

    Important limitation:
        The verification adjustments are transparent simulation assumptions.
        They are not calibrated probabilities.  PASS and FAIL are deliberately
        not treated as proof of legitimacy or fraud.
    """

    def __init__(self) -> None:
        """Create Policy 1 with a private frozen-baseline score calculator."""

        self._baseline = BaselineAgent()

    def decide_initial(
        self,
        evidence: Mapping[str, str],
    ) -> Policy1InitialDecision:
        """
        Select Policy 1's first action from the three initial evidence fields.

        Input:
            ``evidence`` must contain exactly amount_deviation,
            device_location_context, and recent_velocity.  Hidden labels,
            narratives, and verification results are rejected by the baseline
            validation reused here.

        Returns:
            ``Policy1InitialDecision`` containing point contributions, initial
            score, the first action, and whether verification was requested.

        What happens inside:
            The frozen baseline calculates the score.  Policy 1 changes only
            the middle action: scores two and three request more evidence
            instead of immediately going to a human.
        """

        baseline_decision = self._baseline.decide(evidence)
        initial_score = baseline_decision.risk_score

        if initial_score <= APPROVE_MAXIMUM_SCORE:
            initial_action = "APPROVE"
            verification_requested = False
        elif initial_score <= POLICY_1_REQUEST_MAXIMUM_SCORE:
            initial_action = "GET_MORE_EVIDENCE"
            verification_requested = True
        else:
            initial_action = "STOP"
            verification_requested = False

        reason = (
            f"The frozen baseline evidence score was {initial_score}. "
            f"Policy 1 selected {initial_action}. "
            f"Verification requested: {verification_requested}."
        )

        return Policy1InitialDecision(
            policy_name=POLICY_1_NAME,
            amount_points=baseline_decision.amount_points,
            device_location_points=(
                baseline_decision.device_location_points
            ),
            velocity_points=baseline_decision.velocity_points,
            initial_risk_score=initial_score,
            initial_action=initial_action,
            verification_requested=verification_requested,
            reason=reason,
        )

    def finalize(
        self,
        initial_decision: Policy1InitialDecision,
        verification_result: Optional[str] = None,
    ) -> Policy1Decision:
        """
        Finish the decision, revealing verification only when it was requested.

        Input:
            ``initial_decision`` is returned by ``decide_initial``.
            ``verification_result`` must be supplied only for an initial
            GET_MORE_EVIDENCE action.  Its allowed values are PASS, FAIL,
            INCONCLUSIVE, and UNAVAILABLE.

        Returns:
            ``Policy1Decision`` containing both stages, the observed additional
            evidence, score adjustment, final score, and terminal action.

        What happens inside:
            Terminal initial actions keep their score and are marked
            NOT_REQUESTED.  An uncertain case validates and applies its
            verification adjustment.  The adjusted score is kept between zero
            and six, then converted to a terminal action using the frozen
            baseline thresholds.

        Raises:
            ValueError if verification is missing when requested, supplied when
            not requested, invalid, or if the initial object is inconsistent.
        """

        if initial_decision.policy_name != POLICY_1_NAME:
            raise ValueError(
                "Policy 1 can finalize only its own initial decisions."
            )

        if initial_decision.verification_requested:
            if initial_decision.initial_action != "GET_MORE_EVIDENCE":
                raise ValueError(
                    "A verification request must follow GET_MORE_EVIDENCE."
                )
            if verification_result is None:
                raise ValueError(
                    "A verification result is required after "
                    "GET_MORE_EVIDENCE."
                )

            observed_result = verification_result.strip().upper()
            if observed_result not in VERIFICATION_SCORE_ADJUSTMENTS:
                raise ValueError(
                    f"Invalid verification result: {observed_result!r}. "
                    "Allowed values: "
                    f"{sorted(VERIFICATION_SCORE_ADJUSTMENTS)}"
                )

            adjustment = VERIFICATION_SCORE_ADJUSTMENTS[observed_result]
            final_score = max(
                0,
                min(
                    MAXIMUM_RISK_SCORE,
                    initial_decision.initial_risk_score + adjustment,
                ),
            )
            final_action, predicted_state = score_to_action(final_score)
        else:
            if verification_result is not None:
                raise ValueError(
                    "Verification evidence cannot be supplied when Policy 1 "
                    "did not request it."
                )

            observed_result = "NOT_REQUESTED"
            adjustment = 0
            final_score = initial_decision.initial_risk_score

            if initial_decision.initial_action == "APPROVE":
                final_action = "APPROVE"
                predicted_state = "LEGITIMATE"
            elif initial_decision.initial_action == "STOP":
                final_action = "STOP"
                predicted_state = "FRAUDULENT"
            else:
                raise ValueError(
                    "A non-terminal initial action must request verification."
                )

        reason = (
            f"Initial score {initial_decision.initial_risk_score} produced "
            f"{initial_decision.initial_action}. Verification result: "
            f"{observed_result}. Score adjustment: {adjustment:+d}. "
            f"Final score: {final_score}. Final action: {final_action}."
        )

        return Policy1Decision(
            policy_name=POLICY_1_NAME,
            amount_points=initial_decision.amount_points,
            device_location_points=(
                initial_decision.device_location_points
            ),
            velocity_points=initial_decision.velocity_points,
            initial_risk_score=initial_decision.initial_risk_score,
            initial_action=initial_decision.initial_action,
            verification_requested=(
                initial_decision.verification_requested
            ),
            verification_result_observed=observed_result,
            verification_score_adjustment=adjustment,
            final_risk_score=final_score,
            final_action=final_action,
            predicted_state=predicted_state,
            reason=reason,
        )


# Policy 2 changes only the interpretation of a successful verification. A
# PASS lowers risk only when it comes from an independent evidence channel.
POLICY_2_NAME = "policy2_reliability_aware_v0.2"
POLICY_2_REQUEST_MINIMUM_SCORE = 2
POLICY_2_REQUEST_MAXIMUM_SCORE = 3
POLICY_2_MAXIMUM_VERIFICATION_REQUESTS = 1

POLICY_2_VERIFICATION_RESULTS = {
    "PASS",
    "FAIL",
    "INCONCLUSIVE",
    "UNAVAILABLE",
}

POLICY_2_INDEPENDENCE_VALUES = {
    "INDEPENDENT",
    "SAME_CHANNEL",
    "UNKNOWN",
}


@dataclass(frozen=True)
class Policy2InitialDecision:
    """Store Policy 2's decision before additional evidence is revealed.

    Input represented by this object:
        The three baseline point contributions and their total risk score.

    Output represented by this object:
        The first action and whether the runner is permitted to reveal the two
        verification fields.

    Why this separate object exists:
        Keeping the initial and final stages separate makes it difficult for a
        runner to expose verification evidence before Policy 2 asks for it.
    """

    policy_name: str
    amount_points: int
    device_location_points: int
    velocity_points: int
    initial_risk_score: int
    initial_action: str
    verification_requested: bool
    reason: str


@dataclass(frozen=True)
class Policy2Decision:
    """Store the complete terminal result of one Policy 2 decision.

    The record preserves both stages for auditing. It says whether evidence was
    requested, which result and independence category were observed, how the
    risk points changed, and which final terminal action was selected.
    """

    policy_name: str
    amount_points: int
    device_location_points: int
    velocity_points: int
    initial_risk_score: int
    initial_action: str
    verification_requested: bool
    verification_result_observed: str
    verification_independence_observed: str
    verification_score_adjustment: int
    final_risk_score: int
    final_action: str
    predicted_state: Optional[str]
    reason: str


def policy2_verification_adjustment(
    verification_result: str,
    verification_independence: str,
) -> int:
    """Convert Policy 2's additional evidence into a risk-point change.

    Input:
        ``verification_result`` must be PASS, FAIL, INCONCLUSIVE or
        UNAVAILABLE. ``verification_independence`` must be INDEPENDENT,
        SAME_CHANNEL or UNKNOWN.

    Returns:
        ``-1`` for an independent PASS, ``+1`` for any FAIL, and ``0`` for
        every other valid combination.

    What happens inside:
        Values are normalized and validated. FAIL is treated conservatively as
        warning evidence. PASS becomes reassuring only when the source is
        independent. A same-channel or unknown PASS is not considered strong
        enough to reduce the score.

    Important:
        This function returns risk points, not a probability.
    """

    result = verification_result.strip().upper()
    independence = verification_independence.strip().upper()

    if result not in POLICY_2_VERIFICATION_RESULTS:
        raise ValueError(
            f"Invalid Policy 2 verification result: {result!r}. "
            f"Allowed values: {sorted(POLICY_2_VERIFICATION_RESULTS)}"
        )
    if independence not in POLICY_2_INDEPENDENCE_VALUES:
        raise ValueError(
            "Invalid Policy 2 verification independence: "
            f"{independence!r}. Allowed values: "
            f"{sorted(POLICY_2_INDEPENDENCE_VALUES)}"
        )

    if result == "FAIL":
        return 1
    if result == "PASS" and independence == "INDEPENDENT":
        return -1
    return 0


class Policy2Agent:
    """Interpret verification according to its reliability and independence.

    Initial input:
        Exactly ``amount_deviation``, ``device_location_context`` and
        ``recent_velocity``. The class reuses the frozen baseline to validate
        these fields and calculate the zero-to-six initial risk index.

    Additional input:
        A verification result and an independence category may be supplied only
        after an initial score of two or three requests more evidence.

    Returns:
        ``decide_initial`` returns ``Policy2InitialDecision``.
        ``finalize`` returns ``Policy2Decision`` with APPROVE, HUMAN_REVIEW or
        STOP. It never returns a second GET_MORE_EVIDENCE action.

    What happens inside:
        Low scores are approved and high scores are stopped immediately. Scores
        two and three request one check. An independent PASS subtracts one
        point, FAIL adds one point, and all other valid combinations leave the
        score unchanged. The frozen baseline terminal thresholds are then
        applied.
    """

    def __init__(self) -> None:
        """Create Policy 2 with a private frozen-baseline score calculator."""

        self._baseline = BaselineAgent()

    def decide_initial(
        self,
        evidence: Mapping[str, str],
    ) -> Policy2InitialDecision:
        """Choose the first action without seeing verification evidence.

        Input:
            A dictionary containing exactly the three frozen initial fields.

        Returns:
            The baseline-derived score and either APPROVE,
            GET_MORE_EVIDENCE or STOP.

        What happens inside:
            The baseline validates the exact evidence allow-list and calculates
            points. Policy 2 changes only the middle action: scores two and
            three request one verification result plus its independence.
        """

        baseline_decision = self._baseline.decide(evidence)
        initial_score = baseline_decision.risk_score

        if initial_score <= APPROVE_MAXIMUM_SCORE:
            initial_action = "APPROVE"
            verification_requested = False
        elif initial_score <= POLICY_2_REQUEST_MAXIMUM_SCORE:
            initial_action = "GET_MORE_EVIDENCE"
            verification_requested = True
        else:
            initial_action = "STOP"
            verification_requested = False

        reason = (
            f"The frozen initial evidence score was {initial_score}. "
            f"Policy 2 selected {initial_action}. Verification requested: "
            f"{verification_requested}."
        )

        return Policy2InitialDecision(
            policy_name=POLICY_2_NAME,
            amount_points=baseline_decision.amount_points,
            device_location_points=baseline_decision.device_location_points,
            velocity_points=baseline_decision.velocity_points,
            initial_risk_score=initial_score,
            initial_action=initial_action,
            verification_requested=verification_requested,
            reason=reason,
        )

    def finalize(
        self,
        initial_decision: Policy2InitialDecision,
        verification_result: Optional[str] = None,
        verification_independence: Optional[str] = None,
    ) -> Policy2Decision:
        """Finish Policy 2 after conditionally receiving additional evidence.

        Input:
            ``initial_decision`` must come from this policy. If it requested
            evidence, both verification values are required. If it did not
            request evidence, neither value may be supplied.

        Returns:
            A terminal ``Policy2Decision`` containing the observed evidence,
            point update, final score, action and optional predicted state.

        What happens inside:
            Requested values are normalized and converted into an asymmetric
            point change. The score is clamped to zero through six and passed
            through the frozen terminal thresholds. Unrequested values are
            marked NOT_REQUESTED and the initial terminal action is preserved.

        Raises:
            ``ValueError`` for missing, unexpected or invalid additional
            evidence and for an inconsistent initial decision object.
        """

        if initial_decision.policy_name != POLICY_2_NAME:
            raise ValueError(
                "Policy 2 can finalize only its own initial decisions."
            )

        if initial_decision.verification_requested:
            if initial_decision.initial_action != "GET_MORE_EVIDENCE":
                raise ValueError(
                    "A Policy 2 request must follow GET_MORE_EVIDENCE."
                )
            if verification_result is None:
                raise ValueError(
                    "A verification result is required after "
                    "GET_MORE_EVIDENCE."
                )
            if verification_independence is None:
                raise ValueError(
                    "Verification independence is required after "
                    "GET_MORE_EVIDENCE."
                )

            observed_result = verification_result.strip().upper()
            observed_independence = (
                verification_independence.strip().upper()
            )
            adjustment = policy2_verification_adjustment(
                observed_result,
                observed_independence,
            )
            final_score = max(
                0,
                min(
                    MAXIMUM_RISK_SCORE,
                    initial_decision.initial_risk_score + adjustment,
                ),
            )
            final_action, predicted_state = score_to_action(final_score)
        else:
            if verification_result is not None:
                raise ValueError(
                    "A verification result cannot be supplied when Policy 2 "
                    "did not request it."
                )
            if verification_independence is not None:
                raise ValueError(
                    "Verification independence cannot be supplied when "
                    "Policy 2 did not request it."
                )

            observed_result = "NOT_REQUESTED"
            observed_independence = "NOT_REQUESTED"
            adjustment = 0
            final_score = initial_decision.initial_risk_score

            if initial_decision.initial_action == "APPROVE":
                final_action = "APPROVE"
                predicted_state = "LEGITIMATE"
            elif initial_decision.initial_action == "STOP":
                final_action = "STOP"
                predicted_state = "FRAUDULENT"
            else:
                raise ValueError(
                    "A non-terminal initial action must request verification."
                )

        reason = (
            f"Initial score {initial_decision.initial_risk_score} produced "
            f"{initial_decision.initial_action}. Verification result: "
            f"{observed_result}. Independence: {observed_independence}. "
            f"Score adjustment: {adjustment:+d}. Final score: {final_score}. "
            f"Final action: {final_action}."
        )

        return Policy2Decision(
            policy_name=POLICY_2_NAME,
            amount_points=initial_decision.amount_points,
            device_location_points=initial_decision.device_location_points,
            velocity_points=initial_decision.velocity_points,
            initial_risk_score=initial_decision.initial_risk_score,
            initial_action=initial_decision.initial_action,
            verification_requested=initial_decision.verification_requested,
            verification_result_observed=observed_result,
            verification_independence_observed=observed_independence,
            verification_score_adjustment=adjustment,
            final_risk_score=final_score,
            final_action=final_action,
            predicted_state=predicted_state,
            reason=reason,
        )
