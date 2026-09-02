"""Run Policy 1 on only the ten v0.1 development cases.

The runner protects the experiment boundary by validating that every input row
is marked DEVELOPMENT.  It passes only the three initial evidence fields to
Policy 1, reveals the simulated step-up result only after the policy requests
it, and reads the hidden true state only after the final action is returned.

The run produces a decision CSV, a metrics JSON file, and a human-readable
Markdown summary under ``results/v0.1``.
"""

import csv
import json
from pathlib import Path
from typing import Any

from agent import (
    POLICY_1_MAXIMUM_VERIFICATION_REQUESTS,
    POLICY_1_NAME,
    VERIFICATION_SCORE_ADJUSTMENTS,
    Policy1Agent,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "cases-development-v0.1.csv"
CONFIG_FILE = PROJECT_ROOT / "config" / "v0.1-parameters.json"
RESULTS_DIRECTORY = PROJECT_ROOT / "results" / "v0.1"
DECISIONS_FILE = RESULTS_DIRECTORY / "policy1-development-decisions.csv"
METRICS_FILE = RESULTS_DIRECTORY / "policy1-development-metrics.json"
SUMMARY_FILE = RESULTS_DIRECTORY / "policy1-development-summary.md"

EXPECTED_DEVELOPMENT_CASES = 10

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
    "verification_result_observed",
    "verification_score_adjustment",
    "final_risk_score",
    "final_action",
    "predicted_state",
    "true_state",
    "automatic_correct",
    "reason",
]


def load_and_validate_config(file_path: Path) -> dict[str, Any]:
    """Load Policy 1's recorded parameters and check code/config agreement.

    Input:
        Path to the v0.1 JSON parameter record.

    Returns:
        The parsed configuration dictionary.

    What happens inside:
        The function confirms that the file exists, parses valid JSON, and
        checks the policy name, maximum request count, and all four verification
        score adjustments against the implementation constants.  This prevents
        the documentation and executable policy from silently drifting apart.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"Policy configuration not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    policy_config = config.get("policy_1")
    if not isinstance(policy_config, dict):
        raise ValueError("Configuration is missing the policy_1 object.")

    if policy_config.get("policy_name") != POLICY_1_NAME:
        raise ValueError("Policy 1 name differs between config and code.")

    if (
        policy_config.get("maximum_verification_requests")
        != POLICY_1_MAXIMUM_VERIFICATION_REQUESTS
    ):
        raise ValueError(
            "Maximum verification requests differ between config and code."
        )

    if (
        policy_config.get("verification_score_adjustments")
        != VERIFICATION_SCORE_ADJUSTMENTS
    ):
        raise ValueError(
            "Verification score adjustments differ between config and code."
        )

    return config


def read_development_cases(file_path: Path) -> list[dict[str, str]]:
    """Read and validate the ten development cases.

    Input:
        Path to ``cases-development-v0.1.csv``.

    Returns:
        A list of ten CSV-row dictionaries.

    What happens inside:
        The function validates the file, required columns, exact case count,
        unique case IDs, DEVELOPMENT split marker, and hidden-state values.  It
        refuses to run if evaluation cases are present.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"Development dataset not found: {file_path}")

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("Development CSV has no header row.")
        rows = list(reader)
        fieldnames = set(reader.fieldnames)

    required_columns = {
        "case_id",
        "split",
        "true_state",
        "amount_deviation",
        "device_location_context",
        "recent_velocity",
        "step_up_result_if_requested",
    }
    missing_columns = required_columns - fieldnames
    if missing_columns:
        raise ValueError(f"Missing dataset columns: {sorted(missing_columns)}")

    if len(rows) != EXPECTED_DEVELOPMENT_CASES:
        raise ValueError(
            f"Expected {EXPECTED_DEVELOPMENT_CASES} development cases, "
            f"found {len(rows)}."
        )

    case_ids = [row["case_id"].strip() for row in rows]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Development dataset contains duplicate case IDs.")

    for row in rows:
        if row["split"].strip().upper() != "DEVELOPMENT":
            raise ValueError(
                f"{row['case_id']} is not a DEVELOPMENT case. "
                "Policy 1 development must not use evaluation cases."
            )
        if row["true_state"].strip().upper() not in {
            "LEGITIMATE",
            "FRAUDULENT",
        }:
            raise ValueError(
                f"{row['case_id']} has an invalid hidden true state."
            )

    return rows


def run_policy1(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Run the two-stage Policy 1 sequence for every development case.

    Input:
        Validated development rows containing visible evidence, a hidden
        counterfactual verification result, and an evaluator-only true state.

    Returns:
        One auditable result dictionary per case.

    What happens inside:
        For each row, the agent first receives only the three frozen evidence
        fields.  The runner accesses ``step_up_result_if_requested`` only if the
        initial action is GET_MORE_EVIDENCE.  The hidden true state is read only
        after the policy returns its terminal action.  HUMAN_REVIEW is recorded
        as DEFERRED rather than counted as a correct automatic classification.
    """

    agent = Policy1Agent()
    results: list[dict[str, Any]] = []

    for row in rows:
        agent_input = {
            "amount_deviation": row["amount_deviation"],
            "device_location_context": row["device_location_context"],
            "recent_velocity": row["recent_velocity"],
        }

        initial_decision = agent.decide_initial(agent_input)

        if initial_decision.verification_requested:
            decision = agent.finalize(
                initial_decision,
                row["step_up_result_if_requested"],
            )
        else:
            decision = agent.finalize(initial_decision)

        true_state = row["true_state"].strip().upper()
        if decision.predicted_state is None:
            predicted_state = "DEFERRED"
            automatic_correct: bool | str = ""
        else:
            predicted_state = decision.predicted_state
            automatic_correct = predicted_state == true_state

        results.append(
            {
                "case_id": row["case_id"],
                "split": row["split"],
                "policy_name": decision.policy_name,
                "amount_deviation": agent_input["amount_deviation"],
                "device_location_context": agent_input[
                    "device_location_context"
                ],
                "recent_velocity": agent_input["recent_velocity"],
                "amount_points": decision.amount_points,
                "device_location_points": decision.device_location_points,
                "velocity_points": decision.velocity_points,
                "initial_risk_score": decision.initial_risk_score,
                "initial_action": decision.initial_action,
                "verification_requested": decision.verification_requested,
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


def calculate_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate transparent development metrics from Policy 1 decisions.

    HUMAN_REVIEW remains deferred.  Automatic accuracy therefore uses only
    APPROVE and STOP rows, while review and verification rates use all ten
    development cases.
    """

    total = len(results)
    legitimate = [row for row in results if row["true_state"] == "LEGITIMATE"]
    fraudulent = [row for row in results if row["true_state"] == "FRAUDULENT"]
    automatic = [row for row in results if row["predicted_state"] != "DEFERRED"]

    approved = sum(row["final_action"] == "APPROVE" for row in results)
    reviewed = sum(row["final_action"] == "HUMAN_REVIEW" for row in results)
    stopped = sum(row["final_action"] == "STOP" for row in results)
    verification_requests = sum(
        bool(row["verification_requested"]) for row in results
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
    fraud_stops = sum(
        row["final_action"] == "STOP"
        and row["true_state"] == "FRAUDULENT"
        for row in results
    )
    legitimate_reviews = sum(
        row["final_action"] == "HUMAN_REVIEW"
        and row["true_state"] == "LEGITIMATE"
        for row in results
    )

    def rate(numerator: int, denominator: int) -> float:
        """Return a four-decimal rate, or zero when no denominator exists."""

        return round(numerator / denominator, 4) if denominator else 0.0

    return {
        "experiment_name": "policy 1 development experiment",
        "dataset_version": "v0.1",
        "dataset_split": "DEVELOPMENT",
        "policy_name": POLICY_1_NAME,
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
        "automatic_coverage": rate(len(automatic), total),
        "automatic_accuracy": rate(correct_automatic, len(automatic)),
        "human_review_rate": rate(reviewed, total),
        "verification_request_rate": rate(verification_requests, total),
        "fraud_recall": rate(fraud_stops, len(fraudulent)),
        "legitimate_review_rate": rate(
            legitimate_reviews,
            len(legitimate),
        ),
        "notes": [
            "Automatic accuracy uses only APPROVE and STOP decisions.",
            "HUMAN_REVIEW is recorded as deferred.",
            "These are development results, not held-out evaluation results.",
            "Policy 1 verification adjustments are risk points, not probabilities.",
        ],
    }


def write_decisions(file_path: Path, results: list[dict[str, Any]]) -> None:
    """Write all per-case Policy 1 decisions to a UTF-8 CSV file."""

    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)


def write_metrics(file_path: Path, metrics: dict[str, Any]) -> None:
    """Write Policy 1 aggregate metrics as readable, valid JSON."""

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)
        file.write("\n")


def write_summary(
    file_path: Path,
    results: list[dict[str, Any]],
    metrics: dict[str, Any],
) -> None:
    """Write a human-readable Policy 1 result and baseline comparison."""

    case_rows = "\n".join(
        "| {case_id} | {initial_risk_score} | {initial_action} | "
        "{verification_result_observed} | {final_risk_score} | "
        "{final_action} | {true_state} |".format(**row)
        for row in results
    )

    markdown = f"""# Policy 1 Development Results

## Experiment information

- Dataset version: v0.1
- Split: DEVELOPMENT
- Cases: {metrics['total_cases']}
- Policy: `{POLICY_1_NAME}`
- Initial evidence: amount deviation, device/location context, recent velocity
- Additional evidence: one step-up verification, only when requested

## Policy tested

Policy 1 preserves the baseline score. Scores zero to one are approved, scores
two to three request step-up verification, and scores four to six are stopped.
PASS subtracts one point, FAIL adds one point, and INCONCLUSIVE or UNAVAILABLE
leave the score unchanged. The original terminal thresholds are then applied.

These point changes are simulation assumptions, not calibrated probabilities.
PASS and FAIL are evidence rather than proof of the hidden state.

## Results

| Measurement | Policy 1 | Frozen baseline |
|---|---:|---:|
| Total cases | {metrics['total_cases']} | 10 |
| Approved | {metrics['approved']} | 3 |
| Human review | {metrics['human_review']} | 5 |
| Stopped | {metrics['stopped']} | 2 |
| Verification requests | {metrics['verification_requests']} | 0 |
| Automatic decisions | {metrics['automatic_decisions']} | 5 |
| Correct automatic decisions | {metrics['correct_automatic_decisions']} | 4 |
| False approvals | {metrics['false_approvals']} | 1 |
| False stops | {metrics['false_stops']} | 0 |
| Automatic coverage | {metrics['automatic_coverage']:.1%} | 50.0% |
| Automatic accuracy | {metrics['automatic_accuracy']:.1%} | 80.0% |
| Human-review rate | {metrics['human_review_rate']:.1%} | 50.0% |
| Fraud recall | {metrics['fraud_recall']:.1%} | 66.7% |

Automatic accuracy excludes HUMAN_REVIEW because review is a deferred action,
not a predicted hidden state.

## Case-level decisions

| Case | Initial score | Initial action | Verification observed | Final score | Final action | Hidden state |
|---|---:|---|---|---:|---|---|
{case_rows}

## Interpretation

This development run tests one change only: replacing immediate human review
for score-two and score-three cases with one selective verification. The raw
decision CSV remains the authoritative case-level record. Any improvement is a
development finding and must not be described as held-out performance.

Policy 1 retains the known v0.1 limitation that familiar-context fraud can be
indistinguishable from legitimate behaviour when the initial evidence and
verification evidence look the same.
"""

    file_path.write_text(markdown, encoding="utf-8")


def main() -> None:
    """Validate inputs, run Policy 1, and write all development artifacts."""

    load_and_validate_config(CONFIG_FILE)
    rows = read_development_cases(DATA_FILE)
    results = run_policy1(rows)
    metrics = calculate_metrics(results)

    RESULTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    write_decisions(DECISIONS_FILE, results)
    write_metrics(METRICS_FILE, metrics)
    write_summary(SUMMARY_FILE, results, metrics)

    print("\nPolicy 1 development summary")
    print("--------------------------------")
    print(f"Total cases: {metrics['total_cases']}")
    print(f"Approved: {metrics['approved']}")
    print(f"Human review: {metrics['human_review']}")
    print(f"Stopped: {metrics['stopped']}")
    print(f"Verification requests: {metrics['verification_requests']}")
    print(f"Automatic decisions: {metrics['automatic_decisions']}")
    print(
        "Correct automatic decisions: "
        f"{metrics['correct_automatic_decisions']}"
    )
    print(f"False approvals: {metrics['false_approvals']}")
    print(f"False stops: {metrics['false_stops']}")
    print(f"\nSaved decisions to: {DECISIONS_FILE}")
    print(f"Saved metrics to: {METRICS_FILE}")
    print(f"Saved summary to: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
