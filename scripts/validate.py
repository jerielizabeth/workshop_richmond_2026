"""Check a transcription and prepare a blank human-review record.

Reads immutable cell CSV and metadata in data/transcriptions/. Writes generated
Markdown and CSV checks to data/validation/ and creates a review template only
if none exists. Never edits transcription or existing human-review files.
Run: .venv/bin/python scripts/validate.py --year 1871 --run asr_1871_run01 --expected-rows 14 --expected-columns 10
"""

import argparse
import csv
import json
import re
from decimal import Decimal
from pathlib import Path


def parse_number(value, money):
    if value in ("", "[illegible]"):
        return None
    pattern = r"(?:\$\s*)?(?:\d+\.\d{2}|\d{1,3}(?:,\d{3})+ \d{2}|\d+ \d{2})" if money else r"\d+"
    if not re.fullmatch(pattern, value):
        raise ValueError("Invalid money format" if money else "Invalid whole-number format")
    clean = value.replace("$", "").strip().replace(",", "")
    if money and "." not in clean:
        clean = clean.replace(" ", ".")
    return Decimal(clean)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument("--run", required=True)
    parser.add_argument("--expected-rows", type=int, required=True)
    parser.add_argument("--expected-columns", type=int, required=True)
    parser.add_argument("--count-columns", type=int, nargs="+", default=[1, 2, 3, 4])
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    if not re.fullmatch(rf"asr_{args.year}_run\d+", args.run):
        parser.error("Run ID must match the selected year.")
    transcription = args.root / "data/transcriptions"
    with (transcription / f"{args.run}_cells.csv").open(encoding="utf-8", newline="") as stream:
        cells = list(csv.DictReader(stream))
    metadata = json.loads((transcription / f"{args.run}_meta.json").read_text())
    output = args.root / "data/validation"
    output.mkdir(parents=True, exist_ok=True)
    report = output / f"{args.run}_validation.md"
    check_file = output / f"{args.run}_checks.csv"
    if not args.force and (report.exists() or check_file.exists()):
        parser.error("Validation outputs already exist. Use --force to regenerate them.")
    checks = []
    priority = set()

    def add(kind, status, row, column, message, flags=""):
        checks.append(dict(check=kind, status=status, row_index=row, column_index=column, flags=flags, message=message))

    by_position = {}
    for cell in cells:
        position = (int(cell["row_index"]), int(cell["column_index"]))
        if position in by_position:
            add("duplicate", "fail", *position, "Duplicate cell position")
        by_position[position] = cell
    expected = {(row, column) for row in range(1, args.expected_rows + 1) for column in range(args.expected_columns)}
    actual = set(by_position)
    complete = expected == actual and len(cells) == len(expected)
    add("completeness", "pass" if complete else "fail", "", "", f"Expected {len(expected)} cells; found {len(cells)}. Missing: {sorted(expected - actual)}. Extra: {sorted(actual - expected)}.")
    values = {}
    for position, cell in by_position.items():
        row, column = position
        if cell["run_id"] != args.run or cell["source_file"] != f"ASR{args.year}.pdf":
            add("provenance", "fail", row, column, "Cell provenance disagrees with selected run/year")
            priority.add(position)
        if not cell["row_label"] or not cell["column_heading"]:
            add("labels", "fail", row, column, "Missing row label or column heading")
            priority.add(position)
        name = by_position.get((row, 0))
        if name and cell["row_label"] != name["value"]:
            add("labels", "fail", row, column, "Row label differs from name cell")
            priority.add(position)
        first = by_position.get((1, column))
        if first and cell["column_heading"] != first["column_heading"]:
            add("headings", "fail", row, column, "Heading differs within column")
            priority.add(position)
        if cell["flags"]:
            add("model_flag", "review", row, column, cell["note"], cell["flags"])
            priority.add(position)
        if column == 0:
            continue
        try:
            values[position] = parse_number(cell["value"], column not in args.count_columns)
            if cell["value"] == "":
                add("blank", "review", row, column, "Blank preserved; reviewer must confirm nothing is printed.")
            elif cell["value"] == "[illegible]":
                add("format", "review", row, column, "Illegible; cannot parse")
                priority.add(position)
        except ValueError as error:
            values[position] = None
            add("format", "fail", row, column, str(error))
            priority.add(position)
    total_rows = {row for (row, column), cell in by_position.items() if column == 0 and cell["value"].strip().lower().rstrip(".") == "total"}
    if len(total_rows) != 1:
        add("arithmetic", "review", "", "", "Expected one clearly labelled Total row; arithmetic not run.")
    else:
        total_row = next(iter(total_rows))
        for column in range(1, args.expected_columns):
            heading = by_position.get((1, column), {}).get("column_heading", f"Column {column}")
            participants = [(row, column) for row in range(1, args.expected_rows + 1) if row != total_row]
            invalid = [position for position in participants if position not in by_position or by_position[position]["value"] == "[illegible]" or (by_position[position]["value"] and values.get(position) is None)]
            printed = values.get((total_row, column))
            if invalid or printed is None:
                add("arithmetic", "review", total_row, column, f"{heading}: cannot calculate from missing or unreadable values.")
                continue
            # Blanks contribute nothing to this sum of reported values, but remain
            # missing observations; this does not assert that blanks mean zero.
            summed = sum((values[position] for position in participants if values.get(position) is not None), Decimal(0))
            difference = summed - printed
            add("arithmetic", "pass" if difference == 0 else "fail", total_row, column,
                f"{heading}: sum of reported entries {summed}; printed total {printed}; difference (sum minus total) {difference}.",
                "total_mismatch" if difference else "")
            if difference:
                priority.update(participants + [(total_row, column)])
    if args.year == 1871 and not metadata["page_text"]["notes"] and not metadata["page_text"]["intro"]:
        add("narrative", "not_applicable", "", "", "1871 has no narrative figures to compare.")
    else:
        add("narrative", "review", "", "", "Automatic narrative comparison not implemented for this page; inspect page text manually.")
    with check_file.open("w" if args.force else "x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["check", "status", "row_index", "column_index", "flags", "message"])
        writer.writeheader()
        writer.writerows(checks)
    lines = [f"# Validation: {args.run}", "", "Generated report. Record human judgements only in the review CSV.", "", "## Completeness and arithmetic", ""]
    for check in checks:
        if check["check"] in {"completeness", "arithmetic", "narrative"} or check["status"] == "fail":
            lines.append(f"- {check['status']}: {check['message']}")
    lines += ["", "Blank cells are listed in the checks CSV for review. Arithmetic sums reported entries only; it does not assign zero to missing observations.", "", "## Cells to review first", "", "All cells require human review for the pilot. These cells have model flags or participate in failed checks.", ""]
    for position in sorted(priority):
        cell = by_position[position]
        lines.append(f"- Row {position[0]}, column {position[1]}: {cell['row_label']} / {cell['column_heading']} = `{cell['value']}`. {cell['flags']} {cell['note']}")
    with report.open("w" if args.force else "x", encoding="utf-8") as stream:
        stream.write("\n".join(lines) + "\n")
    review = args.root / "data/review" / f"{args.run}_review.csv"
    review.parent.mkdir(parents=True, exist_ok=True)
    try:
        with review.open("x", newline="", encoding="utf-8") as stream:
            fields = ["run_id", "row_index", "column_index", "row_label", "column_heading", "value_transcribed", "reviewer", "review_date", "verdict", "corrected_reading", "reason"]
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for cell in sorted(cells, key=lambda cell: (int(cell["row_index"]), int(cell["column_index"]))):
                writer.writerow({**{key: cell[key] for key in fields[:5]}, "value_transcribed": cell["value"]})
        print(f"Created blank human-review template: {review}")
    except FileExistsError:
        print(f"Preserved existing human-review file: {review}")
    print(f"Validation: {len(cells)} cells; {sum(check['status'] == 'fail' for check in checks)} failed checks. Human review pending.")
    print(report)


if __name__ == "__main__":
    main()
