"""Deterministic adult Ottawa Ankle, Midfoot and Knee radiography decision rules.

The rules indicate whether radiographs are recommended, not fracture probability.
No patient data are logged, stored or transmitted by this module.
"""

from __future__ import annotations

from typing import Any

SITES = ("ankle", "midfoot", "knee")
WEIGHT_FIELDS = ("unable_four_steps_immediately", "unable_four_steps_at_assessment")
SITE_FIELDS = {
    "ankle": ("posterior_lateral_malleolus_tenderness", "posterior_medial_malleolus_tenderness"),
    "midfoot": ("navicular_tenderness", "fifth_metatarsal_base_tenderness"),
    "knee": ("fibular_head_tenderness", "isolated_patellar_tenderness", "cannot_flex_90"),
}
ALL_FINDINGS = frozenset(WEIGHT_FIELDS + sum(SITE_FIELDS.values(), ()))
OUTCOMES = {
    "radiography_indicated": "At least one Ottawa criterion is positive; radiography is indicated.",
    "radiography_not_indicated": "All applicable Ottawa criteria are negative; radiography is not indicated by this rule.",
    "insufficient_information": "Complete all applicable findings before interpreting a negative rule.",
    "not_applicable": "Do not use the Ottawa rules to exclude fracture in this presentation.",
}


def _require_boolean(name: str, value: Any, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if type(value) is not bool:
        raise ValueError(f"{name} must be true or false" + (" (or null)" if nullable else ""))


def evaluate(
    *,
    site: str,
    age: int,
    pain_present: bool,
    acute_blunt_trauma: bool,
    reliable_exam: bool,
    **findings: bool | None,
) -> dict[str, Any]:
    """Assess one adult acute injury. None means a finding was not assessed.

    Four-step inability requires failure *both* immediately and at assessment;
    an unknown finding never produces a rule-negative decision.
    """
    if site not in SITES:
        raise ValueError(f"site must be one of: {', '.join(SITES)}")
    if type(age) is not int or not 0 <= age <= 120:
        raise ValueError("age must be an integer between 0 and 120")
    for field, value in (("pain_present", pain_present), ("acute_blunt_trauma", acute_blunt_trauma), ("reliable_exam", reliable_exam)):
        _require_boolean(field, value)
    unknown = set(findings) - ALL_FINDINGS
    if unknown:
        raise ValueError(f"Unknown findings: {', '.join(sorted(unknown))}")
    for name, value in findings.items():
        _require_boolean(name, value, nullable=True)

    if age < 18 or not pain_present or not acute_blunt_trauma or not reliable_exam:
        details = []
        if age < 18:
            details.append("This implementation is limited to adults aged 18 or older")
        if not pain_present:
            details.append(f"No pain reported in the {site} zone")
        if not acute_blunt_trauma:
            details.append("Presentation is not an acute blunt injury")
        if not reliable_exam:
            details.append("Examination is unreliable or exclusion criteria are present")
        return _result(site, "not_applicable", details, [])

    relevant = SITE_FIELDS[site] + WEIGHT_FIELDS
    missing = [key for key in relevant if findings.get(key) is None]
    positives = [key for key in SITE_FIELDS[site] if findings.get(key) is True]
    if site == "knee" and age >= 55:
        positives.insert(0, "age_55_or_over")

    # Inability to bear weight is positive only if both time points are positive.
    at_injury = findings.get(WEIGHT_FIELDS[0])
    at_assessment = findings.get(WEIGHT_FIELDS[1])
    if at_injury is True and at_assessment is True:
        positives.append("unable_four_steps_both_times")

    # Missing weight-bearing timepoint is irrelevant when the other is known false.
    if (at_injury is False or at_assessment is False):
        missing = [key for key in missing if key not in WEIGHT_FIELDS]

    if positives:
        return _result(site, "radiography_indicated", positives, missing)
    if missing:
        return _result(site, "insufficient_information", [], missing)
    return _result(site, "radiography_not_indicated", [], [])


def _result(site: str, outcome: str, reasons: list[str], missing: list[str]) -> dict[str, Any]:
    return {
        "site": site,
        "outcome": outcome,
        "radiography_indicated": (True if outcome == "radiography_indicated" else False if outcome == "radiography_not_indicated" else None),
        "message": OUTCOMES[outcome],
        "positive_criteria": reasons if outcome == "radiography_indicated" else [],
        "missing_findings": missing,
        "applicability_notes": reasons if outcome == "not_applicable" else [],
    }


def parse_boolean(value: str | bool | None, *, nullable: bool = False) -> bool | None:
    """Parse explicit CSV/CLI booleans; never treat non-empty strings as true."""
    if type(value) is bool:
        return value
    if value is None or (isinstance(value, str) and not value.strip()):
        if nullable:
            return None
        raise ValueError("A required yes/no value is missing")
    lowered = str(value).strip().lower()
    if lowered in ("true", "yes", "1"):
        return True
    if lowered in ("false", "no", "0"):
        return False
    raise ValueError(f"Invalid yes/no value: {value!r}")


def evaluate_record(record: dict[str, Any]) -> dict[str, Any]:
    """Evaluate a CSV/JSON record; optional findings default to unknown."""
    return evaluate(
        site=str(record.get("site", "")).strip().lower(),
        age=int(str(record["age"]).strip()),
        pain_present=parse_boolean(record.get("pain_present")),
        acute_blunt_trauma=parse_boolean(record.get("acute_blunt_trauma")),
        reliable_exam=parse_boolean(record.get("reliable_exam")),
        **{name: parse_boolean(record.get(name), nullable=True) for name in ALL_FINDINGS},
    )
