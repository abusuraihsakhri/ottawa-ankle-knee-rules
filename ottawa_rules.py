#!/usr/bin/env python3
"""Single-case and CSV batch CLI for the Ottawa radiography decision rules."""
import argparse
import csv
import json
from pathlib import Path

from clinical_rules import ALL_FINDINGS, evaluate_record


def calculate_metrics(**kwargs):
    """Compatibility entrypoint, now evaluating actual Ottawa criteria.

    Arbitrary v1/v2/v3 numeric scores are intentionally unsupported.
    """
    return evaluate_record(kwargs)


def process_batch(input_csv: str, output_csv: str) -> int:
    source, destination = Path(input_csv).resolve(), Path(output_csv).resolve()
    if source == destination:
        raise ValueError("Input and output paths must differ")
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        if not fields or not {"site", "age", "pain_present", "acute_blunt_trauma", "reliable_exam"}.issubset(fields):
            raise ValueError("CSV requires site, age, pain_present, acute_blunt_trauma, reliable_exam headers")
        rows = list(reader)
    output_fields = list(dict.fromkeys(fields + ["outcome", "radiography_indicated", "positive_criteria", "missing_findings", "error"]))
    for row in rows:
        try:
            result = evaluate_record(row)
            row.update({
                "outcome": result["outcome"],
                "radiography_indicated": result["radiography_indicated"],
                "positive_criteria": "; ".join(result["positive_criteria"]),
                "missing_findings": "; ".join(result["missing_findings"]),
                "error": "",
            })
        except (ValueError, TypeError, KeyError) as exc:
            row.update({"outcome": "error", "radiography_indicated": "", "positive_criteria": "", "missing_findings": "", "error": str(exc)})
    with destination.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Adult Ottawa ankle, midfoot and knee radiography criteria")
    commands = parser.add_subparsers(dest="command", required=True)
    single = commands.add_parser("single", help="Evaluate an injury from supplied clinical findings")
    single.add_argument("--site", required=True, choices=("ankle", "midfoot", "knee"))
    single.add_argument("--age", required=True, type=int)
    for key in ("pain_present", "acute_blunt_trauma", "reliable_exam") + tuple(sorted(ALL_FINDINGS)):
        single.add_argument("--" + key.replace("_", "-"), choices=("yes", "no", "unknown"), required=key in ("pain_present", "acute_blunt_trauma", "reliable_exam"))
    batch = commands.add_parser("batch", help="Evaluate CSV rows")
    batch.add_argument("-i", "--input", required=True)
    batch.add_argument("-o", "--output", default="results.csv")
    args = parser.parse_args(argv)
    if args.command == "single":
        values = vars(args)
        values.pop("command")
        for key, value in tuple(values.items()):
            if value in ("yes", "no", "unknown"):
                values[key] = {"yes": "true", "no": "false", "unknown": ""}[value]
        try:
            print(json.dumps(calculate_metrics(**values), indent=2))
        except ValueError as exc:
            parser.error(str(exc))
    else:
        try:
            count = process_batch(args.input, args.output)
        except (ValueError, OSError) as exc:
            parser.error(str(exc))
        print(f"Processed {count} records -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
