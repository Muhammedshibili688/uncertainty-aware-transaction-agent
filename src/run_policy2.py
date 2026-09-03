"""Run frozen Policy 2 on only the ten v0.2 development cases.

The runner also calculates baseline and Policy 1 results on those same new
development cases so Policy 2's frozen success criteria can be checked fairly.
It never opens or executes the reserved v0.2 evaluation split.
"""

import csv
import json
from pathlib import Path
from typing import Any

from agent import (
    POLICY_2_INDEPENDENCE_VALUES,
    POLICY_2_MAXIMUM_VERIFICATION_REQUESTS,
    POLICY_2_NAME,
    POLICY_2_VERIFICATION_RESULTS,
    BaselineAgent,
    Policy1Agent,
    Policy2Agent,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "cases-development-v0.2.csv"
CONFIG_FILE = PROJECT_ROOT / "config" / "v0.2-parameters.json"
RESULTS_DIRECTORY = PROJECT_ROOT / "results" / "v0.2"
DECISIONS_FILE = RESULTS_DIRECTORY / "policy2-development-decisions.csv"
METRICS_FILE = RESULTS_DIRECTORY / "policy2-development-metrics.json"
SUMMARY_FILE = RESULTS_DIRECTORY / "policy2-development-summary.md"

EXPECTED_DEVELOPMENT_CASES = 10
INITIAL_FIELDS = (
    "amount_deviation",
    "device_location_context",
    "recent_velocity",
)

RESULT_COLUMNS = [
    "case_id",
    "split",
    "policy_name",
    "amount_deviation",
    "device_location_context",
    "recent_velocity",
    "amount_points",
    "device_location_points",
    "velocity_points",
    "initial_risk_score",
    "initial_action",
    "verification_requested",
    "verification_request_count",
    "verification_result_observed",
    "verification_independence_observed",
    "verification_score_adjustment",
    "final_risk_score",
    "final_action",
    "predicted_state",
    "true_state",
    "automatic_correct",
    "reason",
]


def load_and_validate_config(file_path: Path) -> dict[str, Any]:
    """Load the frozen v0.2 parameters and check code/config agreement.

    Input:
        Path to ``config/v0.2-parameters.json``.

    Returns:
        The parsed configuration dictionary when every frozen value agrees
        with the implementation.

    What happens inside:
        The policy name, allowed verification categories, one-request limit and
        all asymmetric point updates are compared with the executable policy.
        A mismatch stops the experiment before any case is processed.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"Policy 2 configuration not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    policy = config.get("policy_2")
    if not isinstance(policy, dict):
        raise ValueError("Configuration is missing the policy_2 object.")
    if policy.get("policy_name") != POLICY_2_NAME:
        raise ValueError("Policy 2 name differs between config and code.")
    if set(policy.get("verification_results", [])) != POLICY_2_VERIFICATION_RESULTS:
        raise ValueError("Policy 2 verification results differ from code.")
    if (
        set(policy.get("verification_independence_values", []))
        != POLICY_2_INDEPENDENCE_VALUES
    ):
        raise ValueError("Policy 2 independence values differ from code.")
    if (
        policy.get("maximum_verification_requests")
        != POLICY_2_MAXIMUM_VERIFICATION_REQUESTS
    ):
        raise ValueError("Policy 2 request limit differs from code.")

    expected_rules = {
        "independent_pass": -1,
        "same_channel_pass": 0,
        "unknown_independence_pass": 0,
        "fail": 1,
        "inconclusive": 0,
        "unavailable": 0,
    }
    if policy.get("evidence_update_rules") != expected_rules:
        raise ValueError("Policy 2 evidence-update rules differ from code.")

    return config


def read_development_cases(file_path: Path) -> list[dict[str, str]]:
    """Read exactly ten v0.2 DEVELOPMENT rows and reject evaluation data.

    The function checks required columns, unique IDs, hidden-state categories
    and both additional-evidence categories. It does not open the separate
    evaluation file.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"Policy 2 development data not found: {file_path}")

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("Policy 2 development CSV has no header.")
        fieldnames = set(reader.fieldnames)
        rows = list(reader)

    required = {
        "case_id",
        "split",
        "true_state",
        "step_up_result_if_requested",
        "verification_independence_if_requested",
        *INITIAL_FIELDS,
    }
    missing = required - fieldnames
    if missing:
        raise ValueError(f"Policy 2 dataset columns are missing: {sorted(missing)}")
    if len(rows) != EXPECTED_DEVELOPMENT_CASES:
        raise ValueError(
            f"Expected {EXPECTED_DEVELOPMENT_CASES} Policy 2 development "
            f"cases but found {len(rows)}."
        )

    case_ids = [row["case_id"].strip() for row in rows]
    if any(not case_id for case_id in case_ids):
        raise ValueError("Policy 2 development data contains an empty case ID.")
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Policy 2 development data contains duplicate case IDs.")

    for row in rows:
        case_id = row["case_id"]
        if row["split"].strip().upper() != "DEVELOPMENT":
            raise ValueError(
                f"{case_id} is not DEVELOPMENT. Reserved evaluation cases "
                "cannot be used to build Policy 2."
            )
        if row["true_state"].strip().upper() not in {
            "LEGITIMATE",
            "FRAUDULENT",
        }:
            raise ValueError(f"{case_id} has an invalid hidden true state.")
        if (
            row["step_up_result_if_requested"].strip().upper()
            not in POLICY_2_VERIFICATION_RESULTS
        ):
            raise ValueError(f"{case_id} has an invalid verification result.")
        if (
            row["verification_independence_if_requested"].strip().upper()
            not in POLICY_2_INDEPENDENCE_VALUES
        ):
            raise ValueError(f"{case_id} has invalid verification independence.")

    return rows


def initial_evidence(row: dict[str, str]) -> dict[str, str]:
    """Copy exactly the three initial fields into a new agent input."""

    return {field: row[field] for field in INITIAL_FIELDS}


def evaluator_result(
    case_id: str,
    final_action: str,
    predicted_state: str | None,
    true_state_value: str,
) -> tuple[str, bool | str]:
    """Reveal and validate the hidden state after a final decision.

    Returns the normalized true state and automatic-correctness value.
    HUMAN_REVIEW returns a blank correctness value because it is deferred.
    """

    true_state = true_state_value.strip().upper()
    if true_state not in {"LEGITIMATE", "FRAUDULENT"}:
        raise ValueError(f"{case_id} has an invalid hidden true state.")
    if final_action == "HUMAN_REVIEW" or predicted_state is None:
        return true_state, ""
    return true_state, predicted_state == true_state


def run_baseline(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Run the unchanged baseline on the new development cases.

    This comparator receives only the three initial fields. It never sees either
    verification column. The output is used only to calculate fair development
    comparison metrics.
    """

    agent = BaselineAgent()
    results = []
    for row in rows:
        evidence = initial_evidence(row)
        decision = agent.decide(evidence)
        true_state, correct = evaluator_result(
            row["case_id"],
            decision.final_action,
            decision.predicted_state,
            row["true_state"],
        )
        results.append(
            {
                "case_id": row["case_id"],
                "policy_name": decision.policy_name,
                "initial_risk_score": decision.risk_score,
                "initial_action": decision.final_action,
                "verification_requested": False,
                "verification_request_count": 0,
                "verification_result_observed": "NOT_REQUESTED",
                "verification_independence_observed": "NOT_REQUESTED",
                "verification_score_adjustment": 0,
                "final_risk_score": decision.risk_score,
                "final_action": decision.final_action,
                "predicted_state": decision.predicted_state,
                "true_state": true_state,
                "automatic_correct": correct,
            }
        )
    return results


def run_policy1(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Run frozen Policy 1 on the same new development rows.

    Policy 1 receives the verification result only after requesting it and never
    receives the new independence field. This preserves a fair historical
    comparator rather than quietly giving Policy 1 Policy 2's capability.
    """

    agent = Policy1Agent()
    results = []
    for row in rows:
        evidence = initial_evidence(row)
        initial = agent.decide_initial(evidence)
        if initial.verification_requested:
            decision = agent.finalize(
                initial,
                row["step_up_result_if_requested"],
            )
            request_count = 1
        else:
            decision = agent.finalize(initial)
            request_count = 0
        true_state, correct = evaluator_result(
            row["case_id"],
            decision.final_action,
            decision.predicted_state,
            row["true_state"],
        )
        results.append(
            {
                "case_id": row["case_id"],
                "policy_name": decision.policy_name,
                "initial_risk_score": decision.initial_risk_score,
                "initial_action": decision.initial_action,
                "verification_requested": decision.verification_requested,
                "verification_request_count": request_count,
                "verification_result_observed": (
                    decision.verification_result_observed
                ),
                "verification_independence_observed": "NOT_AVAILABLE_TO_POLICY_1",
                "verification_score_adjustment": (
                    decision.verification_score_adjustment
                ),
                "final_risk_score": decision.final_risk_score,
                "final_action": decision.final_action,
                "predicted_state": decision.predicted_state,
                "true_state": true_state,
                "automatic_correct": correct,
            }
        )
    return results


def run_policy2(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Run Policy 2 with conditional access to both additional fields.

    The hidden verification result and independence value are accessed only
    after GET_MORE_EVIDENCE. The true state is read only after ``finalize`` has
    returned a terminal decision.
    """

    agent = Policy2Agent()
    results: list[dict[str, Any]] = []

    for row in rows:
        evidence = initial_evidence(row)
        initial = agent.decide_initial(evidence)

        if initial.verification_requested:
            decision = agent.finalize(
                initial,
                row["step_up_result_if_requested"],
                row["verification_independence_if_requested"],
            )
            request_count = 1
        else:
            decision = agent.finalize(initial)
            request_count = 0

        true_state, correct = evaluator_result(
            row["case_id"],
            decision.final_action,
            decision.predicted_state,
            row["true_state"],
        )
        predicted_state = decision.predicted_state or "DEFERRED"

        results.append(
            {
                "case_id": row["case_id"],
                "split": row["split"],
                "policy_name": decision.policy_name,
                **evidence,
                "amount_points": decision.amount_points,
                "device_location_points": decision.device_location_points,
                "velocity_points": decision.velocity_points,
                "initial_risk_score": decision.initial_risk_score,
                "initial_action": decision.initial_action,
                "verification_requested": decision.verification_requested,
                "verification_request_count": request_count,
                "verification_result_observed": (
                    decision.verification_result_observed
                ),
                "verification_independence_observed": (
                    decision.verification_independence_observed
                ),
                "verification_score_adjustment": (
                    decision.verification_score_adjustment
                ),
                "final_risk_score": decision.final_risk_score,
                "final_action": decision.final_action,
                "predicted_state": predicted_state,
                "true_state": true_state,
                "automatic_correct": correct,
                "reason": decision.reason,
            }
        )

    return results


def rate(numerator: int, denominator: int) -> float:
    """Return a four-decimal fraction and safely handle a zero denominator."""

    return round(numerator / denominator, 4) if denominator else 0.0


def calculate_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate identical development metrics for any of the three policies."""

    total = len(results)
    if total == 0:
        raise ValueError("Cannot calculate metrics from no results.")
    legitimate = [row for row in results if row["true_state"] == "LEGITIMATE"]
    fraudulent = [row for row in results if row["true_state"] == "FRAUDULENT"]
    automatic = [
        row for row in results if row["final_action"] in {"APPROVE", "STOP"}
    ]
    approved = sum(row["final_action"] == "APPROVE" for row in results)
    reviewed = sum(row["final_action"] == "HUMAN_REVIEW" for row in results)
    stopped = sum(row["final_action"] == "STOP" for row in results)
    requests = sum(int(row["verification_request_count"]) for row in results)
    correct = sum(row["automatic_correct"] is True for row in automatic)
    false_approvals = sum(
        row["final_action"] == "APPROVE"
        and row["true_state"] == "FRAUDULENT"
        for row in results
    )
    false_stops = sum(
        row["final_action"] == "STOP"
        and row["true_state"] == "LEGITIMATE"
        for row in results
    )
    stopped_fraud = sum(
        row["final_action"] == "STOP"
        and row["true_state"] == "FRAUDULENT"
        for row in results
    )

    return {
        "policy_name": results[0]["policy_name"],
        "total_cases": total,
        "legitimate_cases": len(legitimate),
        "fraudulent_cases": len(fraudulent),
        "approved": approved,
        "human_review": reviewed,
        "stopped": stopped,
        "verification_requests": requests,
        "automatic_decisions": len(automatic),
        "correct_automatic_decisions": correct,
        "false_approvals": false_approvals,
        "false_stops": false_stops,
        "automatic_coverage": rate(len(automatic), total),
        "automatic_accuracy": rate(correct, len(automatic)),
        "human_review_rate": rate(reviewed, total),
        "verification_request_rate": rate(requests, total),
        "fraud_recall": rate(stopped_fraud, len(fraudulent)),
    }


def check_success_criteria(
    baseline_metrics: dict[str, Any],
    policy1_metrics: dict[str, Any],
    policy2_metrics: dict[str, Any],
    policy2_results: list[dict[str, Any]],
) -> dict[str, bool]:
    """Evaluate every success criterion frozen in the Policy 2 hypothesis."""

    independent_legitimate_approval = any(
        row["true_state"] == "LEGITIMATE"
        and row["verification_result_observed"] == "PASS"
        and row["verification_independence_observed"] == "INDEPENDENT"
        and row["initial_risk_score"] == 2
        and row["final_action"] == "APPROVE"
        for row in policy2_results
    )
    unreliable_pass_never_lowers = all(
        row["verification_result_observed"] != "PASS"
        or row["verification_independence_observed"] == "INDEPENDENT"
        or row["verification_score_adjustment"] == 0
        for row in policy2_results
    )

    return {
        "fewer_false_approvals_than_policy1": (
            policy2_metrics["false_approvals"] < policy1_metrics["false_approvals"]
        ),
        "false_approvals_not_higher_than_baseline": (
            policy2_metrics["false_approvals"]
            <= baseline_metrics["false_approvals"]
        ),
        "false_stops_not_higher_than_baseline": (
            policy2_metrics["false_stops"] <= baseline_metrics["false_stops"]
        ),
        "human_review_lower_than_baseline": (
            policy2_metrics["human_review_rate"]
            < baseline_metrics["human_review_rate"]
        ),
        "independent_pass_can_resolve_legitimate_score_two": (
            independent_legitimate_approval
        ),
        "unreliable_pass_never_lowers_risk": unreliable_pass_never_lowers,
        "verification_only_for_scores_two_and_three": all(
            not row["verification_requested"]
            or row["initial_risk_score"] in {2, 3}
            for row in policy2_results
        ),
        "maximum_one_request_per_case": all(
            row["verification_request_count"] <= 1 for row in policy2_results
        ),
        "all_final_actions_terminal": all(
            row["final_action"] in {"APPROVE", "HUMAN_REVIEW", "STOP"}
            for row in policy2_results
        ),
    }


def write_decisions(file_path: Path, results: list[dict[str, Any]]) -> None:
    """Write Policy 2's auditable development decisions to CSV."""

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)


def write_metrics(file_path: Path, metrics: dict[str, Any]) -> None:
    """Write the versioned development metrics and comparator results."""

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)
        file.write("\n")


def percent(value: float) -> str:
    """Format a decimal rate as a one-decimal percentage."""

    return f"{value * 100:.1f}%"


def write_summary(
    file_path: Path,
    baseline: dict[str, Any],
    policy1: dict[str, Any],
    policy2: dict[str, Any],
    criteria: dict[str, bool],
    policy2_results: list[dict[str, Any]],
) -> None:
    """Write a human-readable development comparison and freeze conclusion."""

    rows = [
        ("Approved", "approved", False),
        ("Human review", "human_review", False),
        ("Stopped", "stopped", False),
        ("Verification requests", "verification_requests", False),
        ("False approvals", "false_approvals", False),
        ("False stops", "false_stops", False),
        ("Automatic coverage", "automatic_coverage", True),
        ("Automatic accuracy", "automatic_accuracy", True),
        ("Human-review rate", "human_review_rate", True),
        ("Fraud recall", "fraud_recall", True),
    ]
    metric_lines = []
    for label, key, is_rate in rows:
        values = [baseline[key], policy1[key], policy2[key]]
        shown = [percent(value) if is_rate else str(value) for value in values]
        metric_lines.append(
            f"| {label} | {shown[0]} | {shown[1]} | {shown[2]} |"
        )

    criterion_lines = [
        f"| {name.replace('_', ' ').capitalize()} | "
        f"{'PASS' if passed else 'FAIL'} |"
        for name, passed in criteria.items()
    ]
    case_lines = [
        "| {case_id} | {true_state} | {initial_risk_score} | "
        "{verification_result_observed} | "
        "{verification_independence_observed} | "
        "{final_risk_score} | {final_action} |".format(**row)
        for row in policy2_results
    ]
    all_passed = all(criteria.values())
    conclusion = (
        "Policy 2 met every frozen development success criterion and is now "
        "frozen before evaluation."
        if all_passed
        else "Policy 2 did not meet every frozen development criterion and "
        "must not be presented as ready for held-out evaluation."
    )

    text = f"""# Policy 2 v0.2 Development Result

## Run boundary

The baseline, frozen Policy 1 and Policy 2 were compared on the same ten new
v0.2 DEVELOPMENT cases. The thirty v0.2 EVALUATION cases were not executed.

## Comparison

| Metric | Baseline | Policy 1 | Policy 2 |
|---|---:|---:|---:|
{chr(10).join(metric_lines)}

Automatic accuracy excludes HUMAN_REVIEW. Risk values are points rather than
probabilities.

## Frozen success criteria

| Criterion | Result |
|---|---|
{chr(10).join(criterion_lines)}

## Policy 2 decisions

| Case | True state | Initial score | Verification | Independence | Final score | Final action |
|---|---|---:|---|---|---:|---|
{chr(10).join(case_lines)}

## Conclusion

{conclusion}

SAME_CHANNEL and UNKNOWN PASS are deliberately treated as unresolved rather
than as proof of legitimacy. Low-score familiar-context fraud remains an
explicit limitation. Development success does not establish held-out
performance.
"""

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(text, encoding="utf-8")


def main() -> None:
    """Validate, run and record the complete Policy 2 development experiment."""

    load_and_validate_config(CONFIG_FILE)
    rows = read_development_cases(DATA_FILE)

    baseline_results = run_baseline(rows)
    policy1_results = run_policy1(rows)
    policy2_results = run_policy2(rows)

    baseline_metrics = calculate_metrics(baseline_results)
    policy1_metrics = calculate_metrics(policy1_results)
    policy2_metrics = calculate_metrics(policy2_results)
    criteria = check_success_criteria(
        baseline_metrics,
        policy1_metrics,
        policy2_metrics,
        policy2_results,
    )

    complete_metrics = {
        "experiment_name": "Policy 2 v0.2 development experiment",
        "dataset_version": "v0.2",
        "dataset_split": "DEVELOPMENT",
        "policy_2": policy2_metrics,
        "comparators_on_same_cases": {
            "baseline": baseline_metrics,
            "policy_1": policy1_metrics,
        },
        "success_criteria": criteria,
        "all_success_criteria_met": all(criteria.values()),
        "notes": [
            "The thirty v0.2 evaluation cases were not executed.",
            "HUMAN_REVIEW is deferred.",
            "Risk updates are points rather than probabilities.",
        ],
    }

    write_decisions(DECISIONS_FILE, policy2_results)
    write_metrics(METRICS_FILE, complete_metrics)
    write_summary(
        SUMMARY_FILE,
        baseline_metrics,
        policy1_metrics,
        policy2_metrics,
        criteria,
        policy2_results,
    )

    print("\nPolicy 2 v0.2 development summary")
    print("---------------------------------")
    print(f"Cases: {policy2_metrics['total_cases']}")
    print(f"Approved: {policy2_metrics['approved']}")
    print(f"Human review: {policy2_metrics['human_review']}")
    print(f"Stopped: {policy2_metrics['stopped']}")
    print(f"Verification requests: {policy2_metrics['verification_requests']}")
    print(f"False approvals: {policy2_metrics['false_approvals']}")
    print(f"False stops: {policy2_metrics['false_stops']}")
    print(f"All success criteria met: {all(criteria.values())}")
    print("Reserved evaluation cases executed: 0")
    print(f"\nSaved decisions to: {DECISIONS_FILE}")
    print(f"Saved metrics to: {METRICS_FILE}")
    print(f"Saved summary to: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
