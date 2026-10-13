"""Run the repository clinical benchmark against the authoritative engine."""
import json
from pathlib import Path

from clinical_rules import evaluate


def test_clinical_benchmarks():
    data = json.loads((Path(__file__).resolve().parent.parent / "benchmark_dataset.json").read_text(encoding="utf-8"))
    for case in data["test_cases"]:
        result = evaluate(**case["input"])
        assert result["outcome"] == case["expected_outcome"], case["id"]
