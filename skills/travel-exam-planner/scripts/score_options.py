#!/usr/bin/env python3
"""Validate and score normalized exam-travel options."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


DEFAULT_WEIGHTS = {
    "avoidable_hour": 0.5,
    "airport_night": 8.0,
    "low_sleep_event": 5.0,
    "air_connection": 3.0,
    "airport_change": 5.0,
    "partial_workday": 4.0,
    "full_workday": 12.0,
}

NUMERIC_FIELDS = (
    "cost_brl",
    "hours_away",
    "avoidable_hours",
    "airport_nights",
    "low_sleep_events",
    "air_connections",
    "airport_changes",
    "partial_workdays",
    "full_workdays",
)

SCORE_FIELDS = {
    "avoidable_hours": "avoidable_hour",
    "airport_nights": "airport_night",
    "low_sleep_events": "low_sleep_event",
    "air_connections": "air_connection",
    "airport_changes": "airport_change",
    "partial_workdays": "partial_workday",
    "full_workdays": "full_workday",
}

VALID_OBJECTIVES = {"best_value", "lowest_total_cost"}
VALID_PRICE_STATUSES = {"quote", "estimate", "confirmed"}
VALID_SLEEP_QUALITIES = {"poor", "limited", "adequate"}


class InputError(ValueError):
    pass


def non_negative_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{field} must be a number")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise InputError(f"{field} must be finite and non-negative")
    return number


def positive_number(value: Any, field: str) -> float:
    number = non_negative_number(value, field)
    if number == 0:
        raise InputError(f"{field} must be greater than zero")
    return number


def optional_https_url(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.startswith("https://"):
        raise InputError(f"{field} must be null or an https URL")
    return value


def load_objective(raw: Any) -> str:
    if raw is None:
        return "best_value"
    if not isinstance(raw, str) or raw not in VALID_OBJECTIVES:
        allowed = ", ".join(sorted(VALID_OBJECTIVES))
        raise InputError(f"objective must be one of: {allowed}")
    return raw


def normalize_cost_items(raw: Any, option_id: str) -> tuple[list[dict[str, Any]], float]:
    if not isinstance(raw, list) or not raw:
        raise InputError(f"{option_id}.cost_items must be a non-empty array")
    normalized: list[dict[str, Any]] = []
    total = 0.0
    for index, item in enumerate(raw):
        field = f"{option_id}.cost_items[{index}]"
        if not isinstance(item, dict):
            raise InputError(f"{field} must be an object")
        category = item.get("category")
        description = item.get("description")
        provider = item.get("provider", "")
        price_status = item.get("price_status")
        verified_at = item.get("verified_at")
        conditions = item.get("conditions", "")
        for name, value in (
            ("category", category),
            ("description", description),
            ("price_status", price_status),
            ("verified_at", verified_at),
        ):
            if not isinstance(value, str) or not value.strip():
                raise InputError(f"{field}.{name} must be a non-empty string")
        if price_status not in VALID_PRICE_STATUSES:
            allowed = ", ".join(sorted(VALID_PRICE_STATUSES))
            raise InputError(f"{field}.price_status must be one of: {allowed}")
        if not isinstance(provider, str):
            raise InputError(f"{field}.provider must be a string")
        if not isinstance(conditions, str):
            raise InputError(f"{field}.conditions must be a string")
        quantity = positive_number(item.get("quantity"), f"{field}.quantity")
        unit_cost = non_negative_number(
            item.get("unit_cost_brl"), f"{field}.unit_cost_brl"
        )
        item_total = non_negative_number(
            item.get("total_cost_brl"), f"{field}.total_cost_brl"
        )
        calculated = round(quantity * unit_cost, 2)
        if not math.isclose(item_total, calculated, abs_tol=0.01):
            raise InputError(
                f"{field}.total_cost_brl must equal quantity * unit_cost_brl"
            )
        normalized.append(
            {
                "category": category,
                "description": description,
                "provider": provider,
                "quantity": round(quantity, 2),
                "unit_cost_brl": round(unit_cost, 2),
                "total_cost_brl": round(item_total, 2),
                "price_status": price_status,
                "purchase_url": optional_https_url(
                    item.get("purchase_url"), f"{field}.purchase_url"
                ),
                "source_url": optional_https_url(
                    item.get("source_url"), f"{field}.source_url"
                ),
                "verified_at": verified_at,
                "conditions": conditions,
            }
        )
        total += item_total
    return normalized, round(total, 2)


def load_weights(raw: Any) -> dict[str, float]:
    if raw is None:
        return dict(DEFAULT_WEIGHTS)
    if not isinstance(raw, dict):
        raise InputError("weights must be an object")
    unknown = sorted(set(raw) - set(DEFAULT_WEIGHTS))
    if unknown:
        raise InputError(f"unknown weight fields: {', '.join(unknown)}")
    weights = dict(DEFAULT_WEIGHTS)
    for key, value in raw.items():
        weights[key] = non_negative_number(value, f"weights.{key}")
    return weights


def normalize_sleep_assessment(raw: Any, option_id: str) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise InputError(f"{option_id}.sleep_assessment must be an object")
    quality = raw.get("quality")
    if quality not in VALID_SLEEP_QUALITIES:
        allowed = ", ".join(sorted(VALID_SLEEP_QUALITIES))
        raise InputError(
            f"{option_id}.sleep_assessment.quality must be one of: {allowed}"
        )
    detail = raw.get("detail")
    if not isinstance(detail, str) or not detail.strip():
        raise InputError(f"{option_id}.sleep_assessment.detail must be a non-empty string")
    return {
        "quality": quality,
        "usable_sleep_hours": round(
            non_negative_number(
                raw.get("usable_sleep_hours"),
                f"{option_id}.sleep_assessment.usable_sleep_hours",
            ),
            2,
        ),
        "normal_sleep_hours_covered": round(
            non_negative_number(
                raw.get("normal_sleep_hours_covered"),
                f"{option_id}.sleep_assessment.normal_sleep_hours_covered",
            ),
            2,
        ),
        "detail": detail,
    }


def score_option(raw: Any, weights: dict[str, float]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise InputError("each option must be an object")
    option_id = raw.get("id")
    label = raw.get("label")
    if not isinstance(option_id, str) or not option_id.strip():
        raise InputError("option.id must be a non-empty string")
    if not isinstance(label, str) or not label.strip():
        raise InputError(f"{option_id}.label must be a non-empty string")

    values = {
        field: non_negative_number(raw.get(field), f"{option_id}.{field}")
        for field in NUMERIC_FIELDS
    }
    sleep_assessment = normalize_sleep_assessment(
        raw.get("sleep_assessment"), option_id
    )
    cost_items, itemized_total = normalize_cost_items(raw.get("cost_items"), option_id)
    if not math.isclose(values["cost_brl"], itemized_total, abs_tol=0.01):
        raise InputError(f"{option_id}.cost_brl must equal the cost_items total")

    constraints = raw.get("hard_constraints", [])
    if not isinstance(constraints, list):
        raise InputError(f"{option_id}.hard_constraints must be an array")
    blockers: list[dict[str, str]] = []
    normalized_constraints: list[dict[str, Any]] = []
    for index, item in enumerate(constraints):
        if not isinstance(item, dict):
            raise InputError(f"{option_id}.hard_constraints[{index}] must be an object")
        name = item.get("name")
        satisfied = item.get("satisfied")
        detail = item.get("detail", "")
        if not isinstance(name, str) or not name.strip():
            raise InputError(f"{option_id}.hard_constraints[{index}].name is required")
        if not isinstance(satisfied, bool):
            raise InputError(f"{option_id}.hard_constraints[{index}].satisfied must be boolean")
        if not isinstance(detail, str):
            raise InputError(f"{option_id}.hard_constraints[{index}].detail must be a string")
        normalized = {"name": name, "satisfied": satisfied, "detail": detail}
        normalized_constraints.append(normalized)
        if not satisfied:
            blockers.append({"name": name, "detail": detail})

    risk_items = raw.get("risk_items", [])
    if not isinstance(risk_items, list):
        raise InputError(f"{option_id}.risk_items must be an array")
    normalized_risks: list[dict[str, Any]] = []
    risk_total = 0.0
    for index, item in enumerate(risk_items):
        if not isinstance(item, dict):
            raise InputError(f"{option_id}.risk_items[{index}] must be an object")
        reason = item.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise InputError(f"{option_id}.risk_items[{index}].reason is required")
        points = non_negative_number(item.get("points"), f"{option_id}.risk_items[{index}].points")
        normalized_risks.append({"reason": reason, "points": points})
        risk_total += points

    breakdown = {
        field: round(values[field] * weights[weight_key], 2)
        for field, weight_key in SCORE_FIELDS.items()
    }
    breakdown["risk_items"] = round(risk_total, 2)
    total = round(sum(breakdown.values()), 2)

    return {
        "id": option_id,
        "label": label,
        "feasible": not blockers,
        "blocking_constraints": blockers,
        "hard_constraints": normalized_constraints,
        "cost_brl": round(values["cost_brl"], 2),
        "cost_items": cost_items,
        "hours_away": round(values["hours_away"], 2),
        "sleep_assessment": sleep_assessment,
        "inconvenience_score": total,
        "score_breakdown": breakdown,
        "risk_items": normalized_risks,
    }


def dominance_map(options: list[dict[str, Any]]) -> dict[str, list[str]]:
    feasible = [option for option in options if option["feasible"]]
    dominated_by: dict[str, list[str]] = {option["id"]: [] for option in options}
    for candidate in feasible:
        for other in feasible:
            if other is candidate:
                continue
            no_worse = (
                other["cost_brl"] <= candidate["cost_brl"]
                and other["hours_away"] <= candidate["hours_away"]
                and other["inconvenience_score"] <= candidate["inconvenience_score"]
            )
            strictly_better = (
                other["cost_brl"] < candidate["cost_brl"]
                or other["hours_away"] < candidate["hours_away"]
                or other["inconvenience_score"] < candidate["inconvenience_score"]
            )
            if no_worse and strictly_better:
                dominated_by[candidate["id"]].append(other["id"])
        dominated_by[candidate["id"]].sort()
    return dominated_by


def apply_dominance(options: list[dict[str, Any]]) -> tuple[list[str], dict[str, list[str]]]:
    dominated_by = dominance_map(options)
    frontier: list[str] = []
    for option in options:
        option["dominated_by"] = dominated_by[option["id"]]
        if not option["feasible"]:
            option["selection_status"] = "infeasible"
        elif option["dominated_by"]:
            option["selection_status"] = "dominated"
        else:
            option["selection_status"] = "eligible"
            frontier.append(option["id"])
    return frontier, dominated_by


def best_id(options: list[dict[str, Any]], key: str) -> str | None:
    feasible = [option for option in options if option["feasible"]]
    if not feasible:
        return None
    return min(feasible, key=lambda option: (option[key], option["id"]))["id"]


def lowest_cost_id(options: list[dict[str, Any]]) -> str | None:
    feasible = [option for option in options if option["feasible"]]
    if not feasible:
        return None
    return min(
        feasible,
        key=lambda option: (
            option["cost_brl"],
            option["inconvenience_score"],
            option["hours_away"],
            option["id"],
        ),
    )["id"]


def add_financial_impacts(options: list[dict[str, Any]]) -> None:
    feasible = [option for option in options if option["feasible"]]
    cheapest = min(feasible, key=lambda option: (option["cost_brl"], option["id"])) if feasible else None
    for option in options:
        if cheapest is None or not option["feasible"]:
            option["financial_impact"] = None
            continue
        additional_cost = round(option["cost_brl"] - cheapest["cost_brl"], 2)
        percentage = (
            round(additional_cost / cheapest["cost_brl"] * 100, 2)
            if cheapest["cost_brl"] > 0
            else None
        )
        hours_saved = round(cheapest["hours_away"] - option["hours_away"], 2)
        cost_per_hour = (
            round(additional_cost / hours_saved, 2)
            if additional_cost > 0 and hours_saved > 0
            else None
        )
        option["financial_impact"] = {
            "baseline_option_id": cheapest["id"],
            "additional_cost_brl": additional_cost,
            "percentage_above_cheapest": percentage,
            "hours_saved_vs_cheapest": hours_saved,
            "cost_per_hour_saved_brl": cost_per_hour,
        }


def score_document(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise InputError("input must be a JSON object")
    raw_options = document.get("options")
    if not isinstance(raw_options, list) or not raw_options:
        raise InputError("options must be a non-empty array")
    objective = load_objective(document.get("objective"))
    weights = load_weights(document.get("weights"))
    options = [score_option(raw, weights) for raw in raw_options]
    ids = [option["id"] for option in options]
    if len(ids) != len(set(ids)):
        raise InputError("option ids must be unique")
    add_financial_impacts(options)
    lowest_cost = lowest_cost_id(options)
    frontier, dominated_by = apply_dominance(options)
    excluded_dominated = [
        {"id": option["id"], "dominated_by": dominated_by[option["id"]]}
        for option in options
        if option["selection_status"] == "dominated"
    ]
    return {
        "objective": objective,
        "weights": weights,
        "options": options,
        "rankings": {
            "lowest_cost": lowest_cost,
            "shortest_absence": best_id(options, "hours_away"),
            "lowest_inconvenience": best_id(options, "inconvenience_score"),
            "pareto_frontier": frontier,
            "dominated": excluded_dominated,
        },
        "objective_result": {
            "mode": objective,
            "automatic_selection": lowest_cost if objective == "lowest_total_cost" else None,
            "candidates": [lowest_cost] if objective == "lowest_total_cost" and lowest_cost else frontier,
            "excluded_dominated": excluded_dominated,
            "maximum_decision_ready_options": (
                1 if objective == "lowest_total_cost" and lowest_cost else len(frontier)
            ),
            "requires_cost_benefit_judgment": objective == "best_value",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON file containing normalized options")
    parser.add_argument("--pretty", action="store_true", help="pretty-print JSON output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        result = score_document(document)
    except (OSError, json.JSONDecodeError, InputError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
