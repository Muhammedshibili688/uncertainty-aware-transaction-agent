"""
Run the static v0.1 baseline on the 10 development cases.

This file is responsible for the experiment workflow. It loads the
development CSV, gives only permitted evidence to the agent, collects
the decision, and reveals the hidden true state only after the decision
is complete.

It writes a decision record that can be manually inspected.

This file must not be used to tune the baseline against the 30
evaluation cases.
"""

import argparse
import csv
from pathlib import Path
from typing import Any

from agent import BaselineAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_INPUT = (
    PROJECT_ROOT
    / "data"
    / "cases-development-v0.1.csv"
)

DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "results"
    / "v0.1"
    / "baseline-development-decisions.csv"
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
    "risk_score",
    "verification_requested",
    "final_action",
    "predicted_state",
    "true_state",
    "automatic_correct",
    "reason",
]


def read_cases(
    file_path: Path,
) -> list[dict[str, str]]:
    """
    Read transaction cases from a CSV file.

    Input:
        file_path:
            Path pointing to the development CSV file.

    Returns:
        list[dict[str, str]]:
            A list of rows.

            Each row is represented as a dictionary where the CSV
            column name is the key and the cell content is the value.

    What happens inside:
        1. Confirm that the CSV file exists.
        2. Open it using UTF-8-compatible encoding.
        3. Read the first row as column names.
        4. Convert every remaining CSV row into a dictionary.
        5. Confirm that at least one case was loaded.
        6. Return all loaded cases.

    Raises:
        FileNotFoundError:
            Raised when the expected CSV does not exist.

        ValueError:
            Raised when the file has no header or contains no cases.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Development dataset not found: {file_path}\n"
            "Run scripts/split_cases.py first."
        )

    with file_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                "The input CSV does not contain a header row."
            )

        rows = list(reader)

    if not rows:
        raise ValueError(
            "The development CSV does not contain any cases."
        )

    return rows


def validate_development_cases(
    rows: list[dict[str, str]],
) -> None:
    """
    Check that the loaded rows are the expected development dataset.

    Input:
        rows:
            List of CSV case dictionaries returned by read_cases().

    Returns:
        None:
            Nothing is returned when the data is valid.

    What happens inside:
        1. Confirm that the required columns exist.
        2. Confirm that exactly 10 cases were loaded.
        3. Confirm that every row is marked DEVELOPMENT.
        4. Stop the experiment if an evaluation case was accidentally
           included.

    Why this is important:
        The baseline may be changed after examining development results.
        It must not be changed after seeing the held-out evaluation
        results.

    Raises:
        ValueError:
            Raised when columns are missing, the case count is not 10,
            or an evaluation case appears in the file.
    """

    required_columns = {
        "case_id",
        "split",
        "true_state",
        "amount_deviation",
        "device_location_context",
        "recent_velocity",
    }

    missing_columns = required_columns - set(rows[0].keys())

    if missing_columns:
        raise ValueError(
            "Dataset columns are missing: "
            f"{sorted(missing_columns)}"
        )

    if len(rows) != 10:
        raise ValueError(
            f"Expected 10 development cases, "
            f"but found {len(rows)}."
        )

    invalid_splits = [
        row["case_id"]
        for row in rows
        if row["split"].strip().upper() != "DEVELOPMENT"
    ]

    if invalid_splits:
        raise ValueError(
            "Evaluation cases were found in the development file: "
            f"{invalid_splits}"
        )


def run_baseline(
    rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """
    Run the baseline agent once for every development case.

    Input:
        rows:
            Validated development-case dictionaries.

            The complete rows include evaluator information such as
            true_state, but that information must remain outside the
            agent.

    Returns:
        list[dict[str, Any]]:
            One result dictionary for every input case.

            Each result contains the evidence, score, action, hidden
            state, correctness indicator, and explanation.

    What happens inside:
        1. Create one BaselineAgent.
        2. Process the cases one at a time.
        3. Create a new agent_input dictionary containing only the three
           permitted evidence fields.
        4. Ask the agent to make its decision.
        5. Read true_state only after the decision is returned.
        6. Compare automatic predictions with the hidden state.
        7. Keep HUMAN_REVIEW as DEFERRED rather than calling it correct.
        8. Add the complete evaluator result to the result list.
        9. Return all results.

    Leakage protection:
        case_id, true_state, scenario descriptions, research fields,
        explanations, and verification results are never included in
        agent_input.

    Raises:
        ValueError:
            Raised when a case contains an invalid true state or the
            agent receives invalid evidence.
    """

    agent = BaselineAgent()
    results: list[dict[str, Any]] = []

    for row in rows:
        agent_input = {
            "amount_deviation": row["amount_deviation"],
            "device_location_context": row[
                "device_location_context"
            ],
            "recent_velocity": row["recent_velocity"],
        }

        decision = agent.decide(agent_input)

        # This happens only after the agent has completed its decision.
        true_state = row["true_state"].strip().upper()

        if true_state not in {
            "LEGITIMATE",
            "FRAUDULENT",
        }:
            raise ValueError(
                f"{row['case_id']} has invalid true_state: "
                f"{true_state!r}"
            )

        if decision.predicted_state is None:
            automatic_correct: bool | str = ""
        else:
            automatic_correct = (
                decision.predicted_state == true_state
            )

        results.append(
            {
                "case_id": row["case_id"],
                "split": row["split"],
                "policy_name": decision.policy_name,
                "amount_deviation": agent_input[
                    "amount_deviation"
                ],
                "device_location_context": agent_input[
                    "device_location_context"
                ],
                "recent_velocity": agent_input[
                    "recent_velocity"
                ],
                "amount_points": decision.amount_points,
                "device_location_points": (
                    decision.device_location_points
                ),
                "velocity_points": decision.velocity_points,
                "risk_score": decision.risk_score,
                "verification_requested": False,
                "final_action": decision.final_action,
                "predicted_state": (
                    decision.predicted_state or "DEFERRED"
                ),
                "true_state": true_state,
                "automatic_correct": automatic_correct,
                "reason": decision.reason,
            }
        )

    return results


def write_results(
    file_path: Path,
    results: list[dict[str, Any]],
) -> None:
    """
    Write baseline decisions to a CSV file.

    Input:
        file_path:
            Destination path for the results CSV.

        results:
            Decision dictionaries returned by run_baseline().

    Returns:
        None:
            The function writes the file and does not return a value.

    What happens inside:
        1. Create the output directory if it does not exist.
        2. Open the output CSV using UTF-8 encoding.
        3. Write the result column names.
        4. Write one row for every baseline decision.
        5. Close the file automatically.

    Important:
        This function may overwrite an existing baseline-development
        results file at the same path.
    """

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with file_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=RESULT_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(results)


def print_summary(
    results: list[dict[str, Any]],
) -> None:
    """
    Print a small baseline summary in the terminal.

    Input:
        results:
            List of baseline result dictionaries.

    Returns:
        None:
            The function only prints information.

    What happens inside:
        1. Count APPROVE decisions.
        2. Count HUMAN_REVIEW decisions.
        3. Count STOP decisions.
        4. Count decisions made automatically.
        5. Count correct automatic decisions.
        6. Count false approvals.
        7. Count false stops.
        8. Print the totals.

    Definitions:
        False approval:
            The agent approved a fraudulent transaction.

        False stop:
            The agent stopped a legitimate transaction.

        Automatic decision:
            APPROVE or STOP. HUMAN_REVIEW is excluded because the agent
            did not make a final legitimacy prediction.
    """

    approved = sum(
        row["final_action"] == "APPROVE"
        for row in results
    )

    human_review = sum(
        row["final_action"] == "HUMAN_REVIEW"
        for row in results
    )

    stopped = sum(
        row["final_action"] == "STOP"
        for row in results
    )

    automatic_decisions = [
        row
        for row in results
        if row["predicted_state"] != "DEFERRED"
    ]

    correct_automatic = sum(
        row["automatic_correct"] is True
        for row in automatic_decisions
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

    print("\nBaseline development summary")
    print("--------------------------------")
    print(f"Total cases: {len(results)}")
    print(f"Approved: {approved}")
    print(f"Human review: {human_review}")
    print(f"Stopped: {stopped}")
    print(
        f"Automatic decisions: "
        f"{len(automatic_decisions)}"
    )
    print(
        f"Correct automatic decisions: "
        f"{correct_automatic}"
    )
    print(f"False approvals: {false_approvals}")
    print(f"False stops: {false_stops}")


def parse_arguments() -> argparse.Namespace:
    """
    Read optional command-line arguments.

    Input:
        No direct Python arguments.

        The function reads arguments written after the script name in
        the terminal.

        Supported options:

        --data:
            Alternative input CSV path.

        --output:
            Alternative output CSV path.

    Returns:
        argparse.Namespace:
            Object containing the selected data and output paths.

    What happens inside:
        1. Create a command-line argument parser.
        2. Define the --data option.
        3. Define the --output option.
        4. Use default paths when no options are supplied.
        5. Return the parsed settings.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Run the static v0.1 baseline on development cases."
        )
    )

    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to the development CSV.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path for the baseline result CSV.",
    )

    return parser.parse_args()


def main() -> None:
    """
    Execute the complete baseline development experiment.

    Input:
        No direct Python arguments.

        Optional file paths may be supplied through --data and --output.

    Returns:
        None:
            The function creates a CSV and prints a terminal summary.

    What happens inside:
        1. Read command-line settings.
        2. Load the development CSV.
        3. Validate that it contains exactly 10 development cases.
        4. Run the baseline on each case.
        5. Write all decisions to the output CSV.
        6. Print a summary.
        7. Print the output location.
    """

    arguments = parse_arguments()

    rows = read_cases(arguments.data)

    validate_development_cases(rows)

    results = run_baseline(rows)

    write_results(
        arguments.output,
        results,
    )

    print_summary(results)

    print(
        f"\nSaved decisions to: "
        f"{arguments.output}"
    )


if __name__ == "__main__":
    main()