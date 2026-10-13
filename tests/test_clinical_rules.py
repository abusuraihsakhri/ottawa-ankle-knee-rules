"""Clinical decision table and safety regression cases."""
import csv
import pytest

from clinical_rules import evaluate, SITE_FIELDS
from ottawa_rules import process_batch, calculate_metrics, main


BASE = dict(site="ankle", age=34, pain_present=True, acute_blunt_trauma=True, reliable_exam=True,
            unable_four_steps_immediately=False, unable_four_steps_at_assessment=False)


def eval_site(site, **changes):
    values = {**BASE, "site": site}
    values.update({key: False for key in SITE_FIELDS[site]})
    values.update(changes)
    return evaluate(**values)


@pytest.mark.parametrize("site,criterion", [(s, c) for s, cs in SITE_FIELDS.items() for c in cs])
def test_local_tenderness_and_knee_mobility(site, criterion):
    assert eval_site(site, **{criterion: True})["outcome"] == "radiography_indicated"


@pytest.mark.parametrize("site", ("ankle", "midfoot", "knee"))
def test_negative_complete(site):
    result = eval_site(site)
    assert result["outcome"] == "radiography_not_indicated"
    assert result["radiography_indicated"] is False


def test_knee_age_boundary():
    assert eval_site("knee", age=54)["outcome"] == "radiography_not_indicated"
    assert eval_site("knee", age=55)["outcome"] == "radiography_indicated"
    assert eval_site("ankle", age=60)["outcome"] == "radiography_not_indicated"


def test_weight_bearing_requires_inability_at_both_times():
    for site in ("ankle", "midfoot", "knee"):
        assert eval_site(site, unable_four_steps_immediately=True, unable_four_steps_at_assessment=True)["radiography_indicated"] is True
        assert eval_site(site, unable_four_steps_immediately=True, unable_four_steps_at_assessment=False)["radiography_indicated"] is False
        assert eval_site(site, unable_four_steps_immediately=False, unable_four_steps_at_assessment=True)["radiography_indicated"] is False


def test_missing_fields_not_a_negative():
    assert evaluate(**BASE)["outcome"] == "insufficient_information"
    assert eval_site("midfoot", navicular_tenderness=None)["outcome"] == "insufficient_information"
    assert eval_site("knee", isolated_patellar_tenderness=None, age=55)["outcome"] == "radiography_indicated"
    assert eval_site("ankle", unable_four_steps_immediately=None, unable_four_steps_at_assessment=False)["outcome"] == "radiography_not_indicated"
    assert eval_site("ankle", unable_four_steps_immediately=None, unable_four_steps_at_assessment=True)["outcome"] == "insufficient_information"


@pytest.mark.parametrize("reason,kwargs", [
    ("age", {"age": 17}), ("pain", {"pain_present": False}),
    ("trauma", {"acute_blunt_trauma": False}), ("unreliable", {"reliable_exam": False}),
])
def test_not_applicable(reason, kwargs):
    assert eval_site("ankle", **kwargs)["outcome"] == "not_applicable"


@pytest.mark.parametrize("kwargs", [
    {"age": True}, {"age": -1}, {"age": 121}, {"pain_present": "false"},
    {"posterior_lateral_malleolus_tenderness": "false"}, {"nonsense": True},
])
def test_reject_bad_types(kwargs):
    with pytest.raises(ValueError):
        eval_site("ankle", **kwargs)


def test_invalid_site():
    with pytest.raises(ValueError):
        evaluate(**{**BASE, "site": "elbow"})


def test_csv_validation_and_results(tmp_path):
    inp, out = tmp_path / "input.csv", tmp_path / "output.csv"
    inp.write_text("site,age,pain_present,acute_blunt_trauma,reliable_exam,posterior_lateral_malleolus_tenderness,posterior_medial_malleolus_tenderness,unable_four_steps_immediately,unable_four_steps_at_assessment\nankle,45,yes,yes,yes,no,no,no,no\nankle,40,yes,yes,yes,yes,no,no,no\nankle,40,yes,yes,yes,garbage,no,no,no\n", encoding="utf-8")
    assert process_batch(str(inp), str(out)) == 3
    with out.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert [r["outcome"] for r in rows] == ["radiography_not_indicated", "radiography_indicated", "error"]
    assert rows[-1]["error"]
    with pytest.raises(ValueError):
        process_batch(str(inp), str(inp))


def test_legacy_generic_scores_rejected():
    with pytest.raises((KeyError, ValueError)):
        calculate_metrics(v1=12, v2=4)


def test_cli_single(capsys):
    assert main(["single", "--site", "knee", "--age", "60", "--pain-present", "yes", "--acute-blunt-trauma", "yes", "--reliable-exam", "yes"]) == 0
    assert '"outcome": "radiography_indicated"' in capsys.readouterr().out
