"""Regression tests for the public Ottawa CLI entry points."""
import csv
import pytest
from ottawa_rules import calculate_metrics, process_batch


def test_single_knee_rule():
    result = calculate_metrics(
        site="knee", age=55, pain_present=True, acute_blunt_trauma=True,
        reliable_exam=True, fibular_head_tenderness="no",
        isolated_patellar_tenderness="no", cannot_flex_90="no",
        unable_four_steps_immediately="no", unable_four_steps_at_assessment="no",
    )
    assert result["outcome"] == "radiography_indicated"
    assert result["radiography_indicated"] is True


def test_batch_csv(tmp_path):
    source = tmp_path / "cases.csv"
    output = tmp_path / "results.csv"
    source.write_text(
        "site,age,pain_present,acute_blunt_trauma,reliable_exam,"
        "navicular_tenderness,fifth_metatarsal_base_tenderness,"
        "unable_four_steps_immediately,unable_four_steps_at_assessment\n"
        "midfoot,30,yes,yes,yes,no,no,no,no\n"
        "midfoot,30,yes,yes,yes,yes,no,no,no\n",
        encoding="utf-8",
    )
    assert process_batch(str(source), str(output)) == 2
    with output.open(encoding="utf-8", newline="") as stream:
        records = list(csv.DictReader(stream))
    assert [row["outcome"] for row in records] == [
        "radiography_not_indicated", "radiography_indicated"
    ]


def test_old_unsupported_numeric_scores_fail_closed():
    with pytest.raises((ValueError, KeyError)):
        calculate_metrics(v1=12, v2=4)
