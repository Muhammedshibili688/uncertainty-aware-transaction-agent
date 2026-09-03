"""Validate the v0.2 master CSV and create reproducible split files."""

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MASTER_FILE = PROJECT_ROOT / "data" / "cases-v0.2.csv"
DEVELOPMENT_FILE = PROJECT_ROOT / "data" / "cases-development-v0.2.csv"
EVALUATION_FILE = PROJECT_ROOT / "data" / "cases-evaluation-v0.2.csv"

EXPECTED_TOTAL = 40
EXPECTED_DEVELOPMENT = 10
EXPECTED_EVALUATION = 30

ALLOWED_SPLITS = {"DEVELOPMENT", "EVALUATION"}
ALLOWED_STATES = {"LEGITIMATE", "FRAUDULENT"}
ALLOWED_AMOUNTS = {"NORMAL", "MODERATE", "HIGH", "UNKNOWN"}
ALLOWED_CONTEXTS = {
    "KNOWN_DEVICE_USUAL_LOCATION",
    "KNOWN_DEVICE_UNUSUAL_LOCATION",
    "NEW_DEVICE_USUAL_LOCATION",
    "NEW_DEVICE_UNUSUAL_LOCATION",
    "UNKNOWN",
}
ALLOWED_VELOCITIES = {"NORMAL", "ELEVATED", "HIGH", "UNKNOWN"}
ALLOWED_RESULTS = {"PASS", "FAIL", "INCONCLUSIVE", "UNAVAILABLE"}
ALLOWED_INDEPENDENCE = {"INDEPENDENT", "SAME_CHANNEL", "UNKNOWN"}


def read_and_validate_master(file_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read all forty cases and reject structural or category mistakes.

    Input:
        Path to the canonical v0.2 master CSV.

    Returns:
        The original ordered column names and all validated row dictionaries.

    What happens inside:
        The function checks the exact total and split sizes, unique non-empty
        case IDs, allowed hidden states and every policy-visible category. It
        does not execute an agent or calculate evaluation performance.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"v0.2 master dataset not found: {file_path}")

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("v0.2 master CSV has no header.")
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    if len(rows) != EXPECTED_TOTAL:
        raise ValueError(f"Expected {EXPECTED_TOTAL} cases but found {len(rows)}.")

    case_ids = [row["case_id"].strip() for row in rows]
    if any(not case_id for case_id in case_ids):
        raise ValueError("A v0.2 case ID is empty.")
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("v0.2 case IDs must be unique.")

    allowed_by_column = {
        "split": ALLOWED_SPLITS,
        "true_state": ALLOWED_STATES,
        "amount_deviation": ALLOWED_AMOUNTS,
        "device_location_context": ALLOWED_CONTEXTS,
        "recent_velocity": ALLOWED_VELOCITIES,
        "step_up_result_if_requested": ALLOWED_RESULTS,
        "verification_independence_if_requested": ALLOWED_INDEPENDENCE,
    }
    for row in rows:
        for column, allowed_values in allowed_by_column.items():
            value = row[column].strip().upper()
            if value not in allowed_values:
                raise ValueError(
                    f"{row['case_id']} has invalid {column}: {value!r}."
                )

    development = [row for row in rows if row["split"] == "DEVELOPMENT"]
    evaluation = [row for row in rows if row["split"] == "EVALUATION"]
    if len(development) != EXPECTED_DEVELOPMENT:
        raise ValueError(
            f"Expected {EXPECTED_DEVELOPMENT} development cases but found "
            f"{len(development)}."
        )
    if len(evaluation) != EXPECTED_EVALUATION:
        raise ValueError(
            f"Expected {EXPECTED_EVALUATION} evaluation cases but found "
            f"{len(evaluation)}."
        )

    return fieldnames, rows


def write_split(
    file_path: Path,
    fieldnames: list[str],
    rows: list[dict[str, str]],
) -> None:
    """Write one validated split while preserving canonical column order."""

    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Validate the master data and regenerate both versioned split files."""

    fieldnames, rows = read_and_validate_master(MASTER_FILE)
    development = [row for row in rows if row["split"] == "DEVELOPMENT"]
    evaluation = [row for row in rows if row["split"] == "EVALUATION"]

    write_split(DEVELOPMENT_FILE, fieldnames, development)
    write_split(EVALUATION_FILE, fieldnames, evaluation)

    print(f"Validated {len(rows)} v0.2 cases.")
    print(f"Development cases: {len(development)} -> {DEVELOPMENT_FILE}")
    print(f"Evaluation cases: {len(evaluation)} -> {EVALUATION_FILE}")
    print("No policy was executed.")


if __name__ == "__main__":
    main()
