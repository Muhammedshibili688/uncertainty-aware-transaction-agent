"""Compare the frozen baseline and Policy 1 on held-out evaluation cases.

This is the one-time v0.1 evaluation runner.  It gives both policies the same
thirty EVALUATION cases, keeps evaluator-only labels outside the agents, and
reveals step-up verification to Policy 1 only after the policy requests it.

The runner does not tune either policy.  It records separate decision CSVs,
separate metric JSON files, and one human-readable comparison summary.
"""

import csv
import json
from pathlib import Path
from typing import Any, Mapping

from agent import BaselineAgent, Policy1Agent, VERIFICATION_SCORE_ADJUSTMENTS
from run_policy1 import load_and_validate_config


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "cases-evaluation-v0.1.csv"
CONFIG_FILE = PROJECT_ROOT / "config" / "v0.1-parameters.json"
RESULTS_DIRECTORY = PROJECT_ROOT / "results" / "v0.1"

BASELINE_DECISIONS_FILE = (
    RESULTS_DIRECTORY / "baseline-evaluation-decisions.csv"
)
BASELINE_METRICS_FILE = RESULTS_DIRECTORY / "baseline-evaluation-metrics.json"
POLICY1_DECISIONS_FILE = RESULTS_DIRECTORY / "policy1-evaluation-decisions.csv"
POLICY1_METRICS_FILE = RESULTS_DIRECTORY / "policy1-evaluation-metrics.json"
COMPARISON_FILE = (
    RESULTS_DIRECTORY / "baseline-vs-policy1-evaluation-summary.md"
)

EXPECTED_EVALUATION_CASES = 30
ALLOWED_TRUE_STATES = {"LEGITIMATE", "FRAUDULENT"}
INITIAL_EVIDENCE_FIELDS = (
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
    "verification_score_adjustment",
    "final_risk_score",
    "final_action",
    "predicted_state",
    "true_state",
    "automatic_correct",
    "reason",
]


def read_evaluation_cases(file_path: Path) -> list[dict[str, str]]:
    """Read and protect the held-out evaluation dataset.

    Input:
        ``file_path`` is the path to the evaluation CSV.

    Returns:
        A list containing exactly thirty validated case dictionaries.

    What happens inside:
        The function checks that the file exists, has all required columns,
        contains exactly thirty rows, uses unique non-empty case IDs, marks
        every row EVALUATION, and contains only supported hidden states and
        verification outcomes.  These checks prevent accidental mixing of
        development and evaluation data.

    Important:
        Validation may inspect evaluator-owned columns.  Those columns are not
        passed to either agent when decisions are made.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"Evaluation dataset not found: {file_path}")

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("Evaluation CSV has no header row.")
        rows = list(reader)
        fieldnames = set(reader.fieldnames)

    required_columns = {
        "case_id",
        "split",
        "true_state",
        "step_up_result_if_requested",
        *INITIAL_EVIDENCE_FIELDS,
    }
    missing_columns = required_columns - fieldnames
    if missing_columns:
        raise ValueError(
            f"Evaluation dataset columns are missing: {sorted(missing_columns)}"
        )

    if len(rows) != EXPECTED_EVALUATION_CASES:
        raise ValueError(
            f"Expected {EXPECTED_EVALUATION_CASES} evaluation cases, "
            f"but found {len(rows)}."
        )

    case_ids = [row["case_id"].strip() for row in rows]
    if any(not case_id for case_id in case_ids):
        raise ValueError("Evaluation dataset contains an empty case ID.")
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Evaluation dataset contains duplicate case IDs.")

    for row in rows:
        case_id = row["case_id"].strip()
        split = row["split"].strip().upper()
        true_state = row["true_state"].strip().upper()
        verification = row["step_up_result_if_requested"].strip().upper()

        if split != "EVALUATION":
            raise ValueError(
                f"{case_id} is not an EVALUATION case. Development cases "
                "cannot be used in the held-out comparison."
            )
        if true_state not in ALLOWED_TRUE_STATES:
            raise ValueError(f"{case_id} has an invalid hidden true state.")
        if verification not in VERIFICATION_SCORE_ADJUSTMENTS:
            raise ValueError(
                f"{case_id} has an invalid step-up verification outcome."
            )

    return rows


def build_initial_evidence(row: Mapping[str, str]) -> dict[str, str]:
    """Create the only input dictionary either agent may initially observe.

    Input:
        One complete evaluator row.  It may contain case descriptions, the
        hidden true state, and a simulated verification result.

    Returns:
        A new dictionary containing exactly the three frozen initial evidence
        fields: amount deviation, device/location context, and velocity.

    What happens inside:
        The function copies only an explicit allow-list.  Because it builds a
        new dictionary, hidden labels and narrative clues cannot accidentally
        travel into the agent call.
    """

    return {field: row[field] for field in INITIAL_EVIDENCE_FIELDS}


def run_baseline_evaluation(
    rows: list[dict[str, str]],
    agent: Any | None = None,
) -> list[dict[str, Any]]:
    """Run the frozen baseline on all evaluation rows.

    Input:
        ``rows`` contains validated evaluation dictionaries. ``agent`` is an
        optional compatible object used by unit tests; normal execution creates
        ``BaselineAgent``.

    Returns:
        One auditable result dictionary per case using the common evaluation
        result schema.

    What happens inside:
        For each case, the function constructs the three-field allow-listed
        input and asks the baseline for a decision.  Only after that decision
        returns does the evaluator read ``true_state`` and calculate automatic
        correctness.  The baseline never sees or requests step-up evidence.
    """

    baseline = agent if agent is not None else BaselineAgent()
    results: list[dict[str, Any]] = []

    for row in rows:
        evidence = build_initial_evidence(row)
        decision = baseline.decide(evidence)

        # Evaluator-only label access deliberately occurs after the decision.
        true_state = row["true_state"].strip().upper()
        predicted_state = decision.predicted_state or "DEFERRED"
        automatic_correct: bool | str
        if predicted_state == "DEFERRED":
            automatic_correct = ""
        else:
            automatic_correct = predicted_state == true_state

        results.append(
            {
                "case_id": row["case_id"],
                "split": row["split"],
                "policy_name": decision.policy_name,
                **evidence,
                "amount_points": decision.amount_points,
                "device_location_points": decision.device_location_points,
                "velocity_points": decision.velocity_points,
                "initial_risk_score": decision.risk_score,
                "initial_action": decision.final_action,
                "verification_requested": False,
                "verification_request_count": 0,
                "verification_result_observed": "NOT_REQUESTED",
                "verification_score_adjustment": 0,
                "final_risk_score": decision.risk_score,
                "final_action": decision.final_action,
                "predicted_state": predicted_state,
                "true_state": true_state,
                "automatic_correct": automatic_correct,
                "reason": decision.reason,
            }
        )

    return results


def run_policy1_evaluation(
    rows: list[dict[str, str]],
    agent: Any | None = None,
) -> list[dict[str, Any]]:
    """Run frozen Policy 1 without leaking unrequested evidence.

    Input:
        ``rows`` contains validated evaluation dictionaries. ``agent`` is an
        optional compatible object used by unit tests; normal execution creates
        ``Policy1Agent``.

    Returns:
        One result dictionary per case containing the initial decision,
        optionally observed verification, final decision, and later evaluator
        comparison with the hidden state.

    What happens inside:
        Policy 1 first receives only the three initial evidence fields.  The
        runner accesses ``step_up_result_if_requested`` only when the returned
        initial decision explicitly requests verification.  The hidden true
        state is accessed only after ``finalize`` returns a terminal action.
    """

    policy = agent if agent is not None else Policy1Agent()
    results: list[dict[str, Any]] = []

    for row in rows:
        evidence = build_initial_evidence(row)
        initial = policy.decide_initial(evidence)

        if initial.verification_requested:
            verification_result = row["step_up_result_if_requested"]
            decision = policy.finalize(initial, verification_result)
            request_count = 1
        else:
            decision = policy.finalize(initial)
            request_count = 0

        # Evaluator-only label access deliberately occurs after finalization.
        true_state = row["true_state"].strip().upper()
        predicted_state = decision.predicted_state or "DEFERRED"
        automatic_correct: bool | str
        if predicted_state == "DEFERRED":
            automatic_correct = ""
        else:
            automatic_correct = predicted_state == true_state

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
                "verification_score_adjustment": (
                    decision.verification_score_adjustment
                ),
                "final_risk_score": decision.final_risk_score,
                "final_action": decision.final_action,
                "predicted_state": predicted_state,
                "true_state": true_state,
                "automatic_correct": automatic_correct,
                "reason": decision.reason,
            }
        )

    return results


def safe_rate(numerator: int, denominator: int) -> float:
    """Return a four-decimal rate, or zero when no denominator exists."""

    return round(numerator / denominator, 4) if denominator else 0.0


def calculate_metrics(
    results: list[dict[str, Any]],
    experiment_name: str,
) -> dict[str, Any]:
    """Calculate the same metrics for either policy.

    Input:
        ``results`` is one policy's complete result list. ``experiment_name``
        is a human-readable label stored in the JSON artifact.

    Returns:
        A serializable dictionary containing action counts, costly errors,
        automatic coverage and accuracy, review burden, verification burden,
        and fraud recall.

    Important definition:
        Automatic accuracy uses only APPROVE and STOP rows. HUMAN_REVIEW is
        deferred and is never silently counted as correct.
    """

    if not results:
        raise ValueError("Cannot calculate metrics from an empty result list.")

    total = len(results)
    legitimate = [row for row in results if row["true_state"] == "LEGITIMATE"]
    fraudulent = [row for row in results if row["true_state"] == "FRAUDULENT"]
    automatic = [
        row for row in results if row["final_action"] in {"APPROVE", "STOP"}
    ]

    approved = sum(row["final_action"] == "APPROVE" for row in results)
    reviewed = sum(row["final_action"] == "HUMAN_REVIEW" for row in results)
    stopped = sum(row["final_action"] == "STOP" for row in results)
    verification_requests = sum(
        int(row["verification_request_count"]) for row in results
    )
    correct_automatic = sum(
        row["automatic_correct"] is True for row in automatic
    )
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
    reviewed_legitimate = sum(
        row["final_action"] == "HUMAN_REVIEW"
        and row["true_state"] == "LEGITIMATE"
        for row in results
    )

    return {
        "experiment_name": experiment_name,
        "dataset_version": "v0.1",
        "dataset_split": "EVALUATION",
        "policy_name": results[0]["policy_name"],
        "total_cases": total,
        "legitimate_cases": len(legitimate),
        "fraudulent_cases": len(fraudulent),
        "approved": approved,
        "human_review": reviewed,
        "stopped": stopped,
        "verification_requests": verification_requests,
        "automatic_decisions": len(automatic),
        "correct_automatic_decisions": correct_automatic,
        "false_approvals": false_approvals,
        "false_stops": false_stops,
        "automatic_coverage": safe_rate(len(automatic), total),
        "automatic_accuracy": safe_rate(correct_automatic, len(automatic)),
        "human_review_rate": safe_rate(reviewed, total),
        "verification_request_rate": safe_rate(verification_requests, total),
        "fraud_recall": safe_rate(stopped_fraud, len(fraudulent)),
        "legitimate_review_rate": safe_rate(
            reviewed_legitimate,
            len(legitimate),
        ),
        "notes": [
            "Automatic accuracy uses only APPROVE and STOP decisions.",
            "HUMAN_REVIEW is recorded as deferred.",
            "These are held-out v0.1 evaluation results.",
            "Policy 1 adjustments are risk points, not probabilities.",
        ],
    }


def compare_policies(
    baseline_results: list[dict[str, Any]],
    policy1_results: list[dict[str, Any]],
    baseline_metrics: dict[str, Any],
    policy1_metrics: dict[str, Any],
) -> dict[str, Any]:
    """Apply the predeclared comparison criteria to both result sets.

    The policies must have processed identical case IDs in identical order.
    Policy 1 is better for the stated objective only when it lowers human
    review without increasing false approvals or false stops and respects both
    verification safeguards.
    """

    baseline_ids = [row["case_id"] for row in baseline_results]
    policy1_ids = [row["case_id"] for row in policy1_results]
    if baseline_ids != policy1_ids:
        raise ValueError(
            "Baseline and Policy 1 must evaluate the same cases in the same "
            "order."
        )

    verification_only_for_uncertain_scores = all(
        not row["verification_requested"]
        or row["initial_risk_score"] in {2, 3}
        for row in policy1_results
    )
    maximum_one_verification = all(
        int(row["verification_request_count"]) <= 1
        for row in policy1_results
    )
    no_second_request = all(
        row["final_action"] != "GET_MORE_EVIDENCE" for row in policy1_results
    )

    criteria = {
        "lower_human_review_rate": (
            policy1_metrics["human_review_rate"]
            < baseline_metrics["human_review_rate"]
        ),
        "false_approvals_not_higher": (
            policy1_metrics["false_approvals"]
            <= baseline_metrics["false_approvals"]
        ),
        "false_stops_not_higher": (
            policy1_metrics["false_stops"] <= baseline_metrics["false_stops"]
        ),
        "verification_only_for_scores_2_and_3": (
            verification_only_for_uncertain_scores
        ),
        "maximum_one_verification_per_case": maximum_one_verification,
        "all_final_actions_are_terminal": no_second_request,
    }
    passed = all(criteria.values())

    changed_cases = []
    for baseline_row, policy1_row in zip(baseline_results, policy1_results):
        if baseline_row["final_action"] != policy1_row["final_action"]:
            changed_cases.append(
                {
                    "case_id": baseline_row["case_id"],
                    "true_state": baseline_row["true_state"],
                    "baseline_action": baseline_row["final_action"],
                    "policy1_action": policy1_row["final_action"],
                    "verification_result": policy1_row[
                        "verification_result_observed"
                    ],
                }
            )

    return {
        "criteria": criteria,
        "policy1_better_for_stated_objective": passed,
        "conclusion": (
            "POLICY_1_BETTER_FOR_STATED_OBJECTIVE"
            if passed
            else "POLICY_1_NOT_BETTER_FOR_STATED_OBJECTIVE"
        ),
        "changed_cases": changed_cases,
    }


def write_csv(file_path: Path, results: list[dict[str, Any]]) -> None:
    """Write one policy's evaluation decisions using the common schema."""

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)


def write_json(file_path: Path, data: dict[str, Any]) -> None:
    """Write a readable, deterministic JSON result artifact."""

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def percentage(value: float) -> str:
    """Format a decimal rate as a percentage with one decimal place."""

    return f"{value * 100:.1f}%"


def write_comparison_summary(
    file_path: Path,
    baseline_metrics: dict[str, Any],
    policy1_metrics: dict[str, Any],
    comparison: dict[str, Any],
) -> None:
    """Write the evaluation conclusion in plain-language Markdown."""

    count_metrics = [
        ("Approved", "approved"),
        ("Human review", "human_review"),
        ("Stopped", "stopped"),
        ("Verification requests", "verification_requests"),
        ("Automatic decisions", "automatic_decisions"),
        ("Correct automatic decisions", "correct_automatic_decisions"),
        ("False approvals", "false_approvals"),
        ("False stops", "false_stops"),
    ]
    rate_metrics = [
        ("Automatic coverage", "automatic_coverage"),
        ("Automatic accuracy", "automatic_accuracy"),
        ("Human-review rate", "human_review_rate"),
        ("Verification-request rate", "verification_request_rate"),
        ("Fraud recall", "fraud_recall"),
        ("Legitimate review rate", "legitimate_review_rate"),
    ]

    metric_lines = []
    for label, key in count_metrics:
        baseline_value = baseline_metrics[key]
        policy_value = policy1_metrics[key]
        metric_lines.append(
            f"| {label} | {baseline_value} | {policy_value} | "
            f"{policy_value - baseline_value:+d} |"
        )
    for label, key in rate_metrics:
        baseline_value = baseline_metrics[key]
        policy_value = policy1_metrics[key]
        difference = (policy_value - baseline_value) * 100
        metric_lines.append(
            f"| {label} | {percentage(baseline_value)} | "
            f"{percentage(policy_value)} | {difference:+.1f} percentage points |"
        )

    criterion_labels = {
        "lower_human_review_rate": "Policy 1 lowers human review",
        "false_approvals_not_higher": "False approvals do not increase",
        "false_stops_not_higher": "False stops do not increase",
        "verification_only_for_scores_2_and_3": (
            "Verification is requested only for initial scores 2-3"
        ),
        "maximum_one_verification_per_case": (
            "No case receives more than one verification"
        ),
        "all_final_actions_are_terminal": "Every final action is terminal",
    }
    criterion_lines = [
        f"| {criterion_labels[key]} | {'PASS' if value else 'FAIL'} |"
        for key, value in comparison["criteria"].items()
    ]

    changed_lines = []
    for row in comparison["changed_cases"]:
        changed_lines.append(
            "| {case_id} | {true_state} | {baseline_action} | "
            "{verification_result} | {policy1_action} |".format(**row)
        )
    if not changed_lines:
        changed_lines.append("| None | - | - | - | - |")

    if comparison["policy1_better_for_stated_objective"]:
        conclusion = (
            "Policy 1 is better than the baseline for the frozen v0.1 "
            "objective: it reduced human review without increasing either "
            "costly automatic error."
        )
    else:
        conclusion = (
            "Policy 1 is not better than the baseline under every frozen "
            "v0.1 success criterion. The failed criteria must be reported as "
            "evaluation findings rather than repaired using these same cases."
        )

    text = f"""# Baseline vs Policy 1: v0.1 Held-Out Evaluation

## Run boundary

Both frozen policies were run once on the same 30 EVALUATION cases. The agents
received only the three initial evidence categories. Policy 1 received a
step-up result only after requesting it, and the evaluator revealed the hidden
state only after each final action.

## Metric comparison

| Metric | Baseline | Policy 1 | Difference (Policy 1 - baseline) |
|---|---:|---:|---:|
{chr(10).join(metric_lines)}

Automatic accuracy excludes HUMAN_REVIEW because those decisions are deferred.
The risk score and its verification adjustments are points, not probabilities.

## Predeclared success criteria

| Criterion | Result |
|---|---|
{chr(10).join(criterion_lines)}

## Cases whose final action changed

| Case | True state | Baseline | Verification observed | Policy 1 |
|---|---|---|---|---|
{chr(10).join(changed_lines)}

## Conclusion

{conclusion}

Policy 1 requested {policy1_metrics['verification_requests']} automated checks.
This extra evidence cost is reported separately from human review rather than
being treated as free. These 30 cases are now used evaluation data and must not
be reused as unseen evidence for a modified policy.
"""

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(text, encoding="utf-8")


def execute_evaluation() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    """Run and save the complete frozen v0.1 held-out comparison.

    Returns:
        Baseline metrics, Policy 1 metrics, and the comparison conclusion.

    What happens inside:
        The function verifies code/config agreement, validates the evaluation
        data, executes both policies on identical rows, calculates metrics,
        applies the predeclared criteria, and writes all five artifacts.
    """

    load_and_validate_config(CONFIG_FILE)
    rows = read_evaluation_cases(DATA_FILE)

    baseline_results = run_baseline_evaluation(rows)
    policy1_results = run_policy1_evaluation(rows)

    baseline_metrics = calculate_metrics(
        baseline_results,
        "baseline held-out evaluation",
    )
    policy1_metrics = calculate_metrics(
        policy1_results,
        "policy 1 held-out evaluation",
    )
    comparison = compare_policies(
        baseline_results,
        policy1_results,
        baseline_metrics,
        policy1_metrics,
    )

    write_csv(BASELINE_DECISIONS_FILE, baseline_results)
    write_json(BASELINE_METRICS_FILE, baseline_metrics)
    write_csv(POLICY1_DECISIONS_FILE, policy1_results)
    write_json(POLICY1_METRICS_FILE, policy1_metrics)
    write_comparison_summary(
        COMPARISON_FILE,
        baseline_metrics,
        policy1_metrics,
        comparison,
    )

    return baseline_metrics, policy1_metrics, comparison


def main() -> None:
    """Execute the held-out comparison and print its essential result."""

    baseline, policy1, comparison = execute_evaluation()

    print("\nHeld-out evaluation: baseline vs Policy 1")
    print("------------------------------------------")
    print(f"Cases evaluated: {baseline['total_cases']}")
    print(
        "Human review: "
        f"baseline {baseline['human_review']} -> Policy 1 "
        f"{policy1['human_review']}"
    )
    print(
        "False approvals: "
        f"baseline {baseline['false_approvals']} -> Policy 1 "
        f"{policy1['false_approvals']}"
    )
    print(
        "False stops: "
        f"baseline {baseline['false_stops']} -> Policy 1 "
        f"{policy1['false_stops']}"
    )
    print(f"Verification requests: {policy1['verification_requests']}")
    print(f"Conclusion: {comparison['conclusion']}")
    print(f"\nSaved comparison to: {COMPARISON_FILE}")


if __name__ == "__main__":
    main()
