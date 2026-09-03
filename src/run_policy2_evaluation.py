"""Run the one-time v0.2 held-out comparison of all three frozen policies.

The runner verifies the pre-evaluation SHA-256 freeze, requires exactly thirty
EVALUATION rows, and refuses to overwrite existing evaluation artifacts. It
then runs the baseline, Policy 1 and Policy 2 on identical cases while keeping
hidden labels and unrequested evidence outside each policy.
"""

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from agent import POLICY_2_INDEPENDENCE_VALUES, POLICY_2_VERIFICATION_RESULTS
from run_policy2 import (
    calculate_metrics,
    check_success_criteria,
    load_and_validate_config,
    run_baseline,
    run_policy1,
    run_policy2,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "cases-evaluation-v0.2.csv"
CONFIG_FILE = PROJECT_ROOT / "config" / "v0.2-parameters.json"
FREEZE_FILE = (
    PROJECT_ROOT / "results" / "v0.2" / "policy2-pre-evaluation-freeze.json"
)
RESULTS_DIRECTORY = PROJECT_ROOT / "results" / "v0.2"

BASELINE_DECISIONS_FILE = RESULTS_DIRECTORY / "baseline-evaluation-decisions.csv"
BASELINE_METRICS_FILE = RESULTS_DIRECTORY / "baseline-evaluation-metrics.json"
POLICY1_DECISIONS_FILE = RESULTS_DIRECTORY / "policy1-evaluation-decisions.csv"
POLICY1_METRICS_FILE = RESULTS_DIRECTORY / "policy1-evaluation-metrics.json"
POLICY2_DECISIONS_FILE = RESULTS_DIRECTORY / "policy2-evaluation-decisions.csv"
POLICY2_METRICS_FILE = RESULTS_DIRECTORY / "policy2-evaluation-metrics.json"
COMPARISON_JSON_FILE = RESULTS_DIRECTORY / "policy-comparison-evaluation.json"
COMPARISON_SUMMARY_FILE = (
    RESULTS_DIRECTORY / "baseline-vs-policy1-vs-policy2-evaluation-summary.md"
)

EXPECTED_EVALUATION_CASES = 30
INITIAL_FIELDS = {
    "amount_deviation",
    "device_location_context",
    "recent_velocity",
}

OUTPUT_FILES = (
    BASELINE_DECISIONS_FILE,
    BASELINE_METRICS_FILE,
    POLICY1_DECISIONS_FILE,
    POLICY1_METRICS_FILE,
    POLICY2_DECISIONS_FILE,
    POLICY2_METRICS_FILE,
    COMPARISON_JSON_FILE,
    COMPARISON_SUMMARY_FILE,
)


def sha256_file(file_path: Path) -> str:
    """Return the lowercase SHA-256 digest of one file.

    The file is read in small binary chunks, so the function works for both
    code and data without changing line endings or file contents.
    """

    digest = hashlib.sha256()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_freeze_manifest(
    manifest_path: Path,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Prove that Policy 2 and its data match the pre-evaluation freeze.

    Input:
        ``manifest_path`` points to the JSON freeze record. ``project_root`` is
        injectable for unit tests.

    Returns:
        The parsed freeze manifest after every recorded hash matches.

    What happens inside:
        The function validates the frozen status, resolves each relative path,
        rejects paths outside the project, checks file existence, calculates a
        fresh SHA-256 digest and compares it with the recorded value. Any drift
        stops evaluation before a policy sees a case.
    """

    if not manifest_path.exists():
        raise FileNotFoundError(f"Pre-evaluation freeze not found: {manifest_path}")

    with manifest_path.open("r", encoding="utf-8") as file:
        manifest = json.load(file)

    if manifest.get("status") != "FROZEN_BEFORE_HELD_OUT_EVALUATION":
        raise ValueError("Policy 2 freeze status is not ready for evaluation.")
    hashes = manifest.get("sha256")
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError("Policy 2 freeze does not contain file hashes.")

    resolved_root = project_root.resolve()
    for relative_name, expected_hash in hashes.items():
        file_path = (resolved_root / relative_name).resolve()
        if resolved_root not in file_path.parents:
            raise ValueError(f"Freeze path escapes the project: {relative_name}")
        if not file_path.exists():
            raise FileNotFoundError(f"Frozen file is missing: {relative_name}")
        actual_hash = sha256_file(file_path)
        if actual_hash != expected_hash:
            raise ValueError(
                f"Frozen file changed before evaluation: {relative_name}"
            )

    return manifest


def read_evaluation_cases(file_path: Path) -> list[dict[str, str]]:
    """Read exactly thirty unique v0.2 EVALUATION cases.

    The validator checks the schema, split, hidden states and additional
    evidence categories. Validation can inspect evaluator-owned values, but the
    policy runners receive only their explicit allow-listed evidence.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"v0.2 evaluation data not found: {file_path}")

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("v0.2 evaluation CSV has no header.")
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
        raise ValueError(f"v0.2 evaluation columns are missing: {sorted(missing)}")
    if len(rows) != EXPECTED_EVALUATION_CASES:
        raise ValueError(
            f"Expected {EXPECTED_EVALUATION_CASES} v0.2 evaluation cases but "
            f"found {len(rows)}."
        )

    case_ids = [row["case_id"].strip() for row in rows]
    if any(not case_id for case_id in case_ids):
        raise ValueError("v0.2 evaluation data contains an empty case ID.")
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("v0.2 evaluation data contains duplicate case IDs.")

    for row in rows:
        case_id = row["case_id"]
        if row["split"].strip().upper() != "EVALUATION":
            raise ValueError(f"{case_id} is not an EVALUATION case.")
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


def refuse_existing_outputs(output_files: tuple[Path, ...]) -> None:
    """Prevent accidental replacement or repeated use of held-out results."""

    existing = [str(path) for path in output_files if path.exists()]
    if existing:
        raise FileExistsError(
            "Evaluation output already exists. The held-out run will not be "
            f"overwritten: {existing}"
        )


def action_by_true_state(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Create an auditable three-action table for each hidden state."""

    table: dict[str, Any] = {}
    for state in ("LEGITIMATE", "FRAUDULENT"):
        state_rows = [row for row in results if row["true_state"] == state]
        table[state] = {
            "APPROVE": sum(row["final_action"] == "APPROVE" for row in state_rows),
            "HUMAN_REVIEW": sum(
                row["final_action"] == "HUMAN_REVIEW" for row in state_rows
            ),
            "STOP": sum(row["final_action"] == "STOP" for row in state_rows),
        }
    return table


def evaluation_metrics(
    results: list[dict[str, Any]],
    experiment_name: str,
) -> dict[str, Any]:
    """Add held-out metadata and an action table to common policy metrics."""

    metrics = calculate_metrics(results)
    return {
        "experiment_name": experiment_name,
        "dataset_version": "v0.2",
        "dataset_split": "EVALUATION",
        **metrics,
        "action_by_true_state": action_by_true_state(results),
        "notes": [
            "Automatic accuracy excludes HUMAN_REVIEW.",
            "HUMAN_REVIEW is deferred.",
            "Risk updates are points rather than probabilities.",
            "These are one-time held-out v0.2 results.",
        ],
    }


def compare_policies(
    baseline_results: list[dict[str, Any]],
    policy1_results: list[dict[str, Any]],
    policy2_results: list[dict[str, Any]],
    baseline_metrics: dict[str, Any],
    policy1_metrics: dict[str, Any],
    policy2_metrics: dict[str, Any],
) -> dict[str, Any]:
    """Apply the frozen Policy 2 gates to three identical result sets."""

    baseline_ids = [row["case_id"] for row in baseline_results]
    policy1_ids = [row["case_id"] for row in policy1_results]
    policy2_ids = [row["case_id"] for row in policy2_results]
    if not (baseline_ids == policy1_ids == policy2_ids):
        raise ValueError("All policies must evaluate the same cases in the same order.")

    criteria = check_success_criteria(
        baseline_metrics,
        policy1_metrics,
        policy2_metrics,
        policy2_results,
    )
    changed_from_policy1 = []
    for policy1_row, policy2_row in zip(policy1_results, policy2_results):
        if policy1_row["final_action"] != policy2_row["final_action"]:
            changed_from_policy1.append(
                {
                    "case_id": policy2_row["case_id"],
                    "true_state": policy2_row["true_state"],
                    "policy1_action": policy1_row["final_action"],
                    "policy2_action": policy2_row["final_action"],
                    "verification_result": policy2_row[
                        "verification_result_observed"
                    ],
                    "verification_independence": policy2_row[
                        "verification_independence_observed"
                    ],
                }
            )

    policy2_errors = [
        {
            "case_id": row["case_id"],
            "true_state": row["true_state"],
            "final_action": row["final_action"],
            "initial_risk_score": row["initial_risk_score"],
            "verification_result": row["verification_result_observed"],
            "verification_independence": row[
                "verification_independence_observed"
            ],
        }
        for row in policy2_results
        if row["automatic_correct"] is False
    ]

    passed = all(criteria.values())
    return {
        "success_criteria": criteria,
        "all_success_criteria_met": passed,
        "conclusion": (
            "POLICY_2_BETTER_FOR_FROZEN_OBJECTIVE"
            if passed
            else "POLICY_2_NOT_BETTER_FOR_FROZEN_OBJECTIVE"
        ),
        "changed_from_policy1": changed_from_policy1,
        "policy2_automatic_errors": policy2_errors,
    }


def write_csv(file_path: Path, results: list[dict[str, Any]]) -> None:
    """Write one policy's complete available decision dictionaries to CSV."""

    if not results:
        raise ValueError("Cannot write an empty decision list.")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("x", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)


def write_json(file_path: Path, data: dict[str, Any]) -> None:
    """Create one non-overwriting JSON evaluation artifact."""

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("x", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def percent(value: float) -> str:
    """Display a decimal rate as a one-decimal percentage."""

    return f"{value * 100:.1f}%"


def write_summary(
    file_path: Path,
    baseline: dict[str, Any],
    policy1: dict[str, Any],
    policy2: dict[str, Any],
    comparison: dict[str, Any],
) -> None:
    """Create the held-out comparison report without overwriting prior work."""

    metric_rows = [
        ("Approved", "approved", False),
        ("Human review", "human_review", False),
        ("Stopped", "stopped", False),
        ("Verification requests", "verification_requests", False),
        ("Automatic decisions", "automatic_decisions", False),
        ("Correct automatic decisions", "correct_automatic_decisions", False),
        ("False approvals", "false_approvals", False),
        ("False stops", "false_stops", False),
        ("Automatic coverage", "automatic_coverage", True),
        ("Automatic accuracy", "automatic_accuracy", True),
        ("Human-review rate", "human_review_rate", True),
        ("Fraud recall", "fraud_recall", True),
    ]
    metric_lines = []
    for label, key, is_rate in metric_rows:
        values = [baseline[key], policy1[key], policy2[key]]
        shown = [percent(value) if is_rate else str(value) for value in values]
        metric_lines.append(
            f"| {label} | {shown[0]} | {shown[1]} | {shown[2]} |"
        )

    criteria_lines = [
        f"| {name.replace('_', ' ').capitalize()} | "
        f"{'PASS' if passed else 'FAIL'} |"
        for name, passed in comparison["success_criteria"].items()
    ]
    changed_lines = [
        "| {case_id} | {true_state} | {policy1_action} | {verification_result} "
        "| {verification_independence} | {policy2_action} |".format(**row)
        for row in comparison["changed_from_policy1"]
    ] or ["| None | - | - | - | - | - |"]
    error_lines = [
        "| {case_id} | {true_state} | {initial_risk_score} | "
        "{verification_result} | {verification_independence} | "
        "{final_action} |".format(**row)
        for row in comparison["policy2_automatic_errors"]
    ] or ["| None | - | - | - | - | - |"]

    if comparison["all_success_criteria_met"]:
        conclusion = (
            "Policy 2 met every frozen held-out criterion and is better for "
            "the stated experimental objective on this simulated dataset."
        )
    else:
        conclusion = (
            "Policy 2 failed at least one frozen held-out criterion and cannot "
            "be called better for the complete stated objective."
        )

    text = f"""# v0.2 Held-Out Evaluation: Baseline vs Policy 1 vs Policy 2

## Run boundary

All three frozen policies processed the same thirty v0.2 EVALUATION cases once.
The pre-evaluation policy and dataset hashes were verified before execution.
The baseline saw no verification. Policy 1 saw only a requested verification
result. Policy 2 saw a requested result and independence value. Hidden states
were used only after final actions.

## Metrics

| Metric | Baseline | Policy 1 | Policy 2 |
|---|---:|---:|---:|
{chr(10).join(metric_lines)}

Automatic accuracy excludes HUMAN_REVIEW because review is deferred. Risk
values are points rather than calibrated probabilities.

## Frozen success criteria

| Criterion | Result |
|---|---|
{chr(10).join(criteria_lines)}

## Policy 1 to Policy 2 action changes

| Case | True state | Policy 1 | Verification | Independence | Policy 2 |
|---|---|---|---|---|---|
{chr(10).join(changed_lines)}

## Policy 2 automatic errors

| Case | True state | Initial score | Verification | Independence | Action |
|---|---|---:|---|---|---|
{chr(10).join(error_lines)}

## Conclusion

{conclusion}

These cases are now used evaluation evidence. Policy 2 must not be changed and
rerun on them as though they were unseen. Any later change requires a new
version and new evaluation cases.
"""

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(text, encoding="utf-8", errors="strict")


def execute_evaluation(
    data_file: Path = DATA_FILE,
    freeze_file: Path = FREEZE_FILE,
    output_files: tuple[Path, ...] = OUTPUT_FILES,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Verify, execute once, and save the complete held-out comparison."""

    refuse_existing_outputs(output_files)
    freeze = validate_freeze_manifest(freeze_file)
    load_and_validate_config(CONFIG_FILE)
    rows = read_evaluation_cases(data_file)

    baseline_results = run_baseline(rows)
    policy1_results = run_policy1(rows)
    policy2_results = run_policy2(rows)

    baseline_metrics = evaluation_metrics(
        baseline_results,
        "baseline v0.2 held-out evaluation",
    )
    policy1_metrics = evaluation_metrics(
        policy1_results,
        "policy 1 v0.2 held-out evaluation",
    )
    policy2_metrics = evaluation_metrics(
        policy2_results,
        "policy 2 v0.2 held-out evaluation",
    )
    comparison = compare_policies(
        baseline_results,
        policy1_results,
        policy2_results,
        baseline_metrics,
        policy1_metrics,
        policy2_metrics,
    )
    comparison.update(
        {
            "experiment_name": "v0.2 three-policy held-out comparison",
            "dataset_version": "v0.2",
            "dataset_split": "EVALUATION",
            "total_cases": len(rows),
            "policy_freeze_name": freeze["freeze_name"],
            "policy_freeze_manifest_sha256": sha256_file(freeze_file),
            "evaluation_runner_sha256": sha256_file(Path(__file__)),
        }
    )

    write_csv(BASELINE_DECISIONS_FILE, baseline_results)
    write_json(BASELINE_METRICS_FILE, baseline_metrics)
    write_csv(POLICY1_DECISIONS_FILE, policy1_results)
    write_json(POLICY1_METRICS_FILE, policy1_metrics)
    write_csv(POLICY2_DECISIONS_FILE, policy2_results)
    write_json(POLICY2_METRICS_FILE, policy2_metrics)
    write_json(COMPARISON_JSON_FILE, comparison)
    write_summary(
        COMPARISON_SUMMARY_FILE,
        baseline_metrics,
        policy1_metrics,
        policy2_metrics,
        comparison,
    )

    return baseline_metrics, policy1_metrics, policy2_metrics, comparison


def main() -> None:
    """Run the one-time evaluation and print its central outcome."""

    baseline, policy1, policy2, comparison = execute_evaluation()

    print("\nv0.2 held-out evaluation")
    print("--------------------------")
    print(f"Cases evaluated: {policy2['total_cases']}")
    print(
        "False approvals (baseline / Policy 1 / Policy 2): "
        f"{baseline['false_approvals']} / {policy1['false_approvals']} / "
        f"{policy2['false_approvals']}"
    )
    print(
        "Human review (baseline / Policy 1 / Policy 2): "
        f"{baseline['human_review']} / {policy1['human_review']} / "
        f"{policy2['human_review']}"
    )
    print(
        "False stops (baseline / Policy 1 / Policy 2): "
        f"{baseline['false_stops']} / {policy1['false_stops']} / "
        f"{policy2['false_stops']}"
    )
    print(f"Conclusion: {comparison['conclusion']}")
    print(f"Saved summary to: {COMPARISON_SUMMARY_FILE}")


if __name__ == "__main__":
    main()
