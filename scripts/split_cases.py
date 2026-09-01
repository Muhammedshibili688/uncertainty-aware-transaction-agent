"""Split the frozen v0.1 cases into development and evaluation CSV files."""

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "data" / "cases-v0.1.csv"

DEVELOPMENT_FILE = (
    PROJECT_ROOT / "data" / "cases-development-v0.1.csv"
)

EVALUATION_FILE = (
    PROJECT_ROOT / "data" / "cases-evaluation-v0.1.csv"
)

EXPECTED_DEVELOPMENT_CASES = 10
EXPECTED_EVALUATION_CASES = 30
EXPECTED_TOTAL_CASES = 40


def read_cases(file_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not file_path.exists():
        raise FileNotFoundError(f"Input dataset not found: {file_path}")

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("The input CSV does not contain a header row.")

        rows = list(reader)

    return reader.fieldnames, rows


def validate_cases(rows: list[dict[str, str]]) -> None:
    if len(rows) != EXPECTED_TOTAL_CASES:
        raise ValueError(
            f"Expected {EXPECTED_TOTAL_CASES} cases, but found {len(rows)}."
        )

    required_columns = {"case_id", "split", "true_state"}

    missing_columns = required_columns - set(rows[0].keys())

    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {sorted(missing_columns)}"
        )

    case_ids = [row["case_id"].strip() for row in rows]

    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Duplicate case IDs were found.")

    allowed_splits = {"DEVELOPMENT", "EVALUATION"}

    invalid_splits = [
        row["case_id"]
        for row in rows
        if row["split"].strip().upper() not in allowed_splits
    ]

    if invalid_splits:
        raise ValueError(
            f"Cases with invalid split values: {invalid_splits}"
        )


def write_cases(
    file_path: Path,
    fieldnames: list[str],
    rows: list[dict[str, str]],
) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    fieldnames, all_cases = read_cases(INPUT_FILE)

    validate_cases(all_cases)

    development_cases = [
        row
        for row in all_cases
        if row["split"].strip().upper() == "DEVELOPMENT"
    ]

    evaluation_cases = [
        row
        for row in all_cases
        if row["split"].strip().upper() == "EVALUATION"
    ]

    if len(development_cases) != EXPECTED_DEVELOPMENT_CASES:
        raise ValueError(
            "Expected "
            f"{EXPECTED_DEVELOPMENT_CASES} development cases, "
            f"but found {len(development_cases)}."
        )

    if len(evaluation_cases) != EXPECTED_EVALUATION_CASES:
        raise ValueError(
            "Expected "
            f"{EXPECTED_EVALUATION_CASES} evaluation cases, "
            f"but found {len(evaluation_cases)}."
        )

    write_cases(DEVELOPMENT_FILE, fieldnames, development_cases)
    write_cases(EVALUATION_FILE, fieldnames, evaluation_cases)

    print(f"Input cases: {len(all_cases)}")
    print(f"Development cases: {len(development_cases)}")
    print(f"Evaluation cases: {len(evaluation_cases)}")
    print(f"Created: {DEVELOPMENT_FILE}")
    print(f"Created: {EVALUATION_FILE}")


if __name__ == "__main__":
    main()