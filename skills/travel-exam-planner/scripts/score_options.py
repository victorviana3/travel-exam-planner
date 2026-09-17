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


class InputError(ValueError):
    pass


def non_negative_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{field} must be a number")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise InputError(f"{field} must be finite and non-negative")
    return number


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
        "hours_away": round(values["hours_away"], 2),
        "inconvenience_score": total,
        "score_breakdown": breakdown,
        "risk_items": normalized_risks,
    }


def pareto_frontier(options: list[dict[str, Any]]) -> list[str]:
    feasible = [option for option in options if option["feasible"]]
    frontier: list[str] = []
    for candidate in feasible:
        dominated = False
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
                dominated = True
                break
        if not dominated:
            frontier.append(candidate["id"])
    return frontier


def best_id(options: list[dict[str, Any]], key: str) -> str | None:
    feasible = [option for option in options if option["feasible"]]
    if not feasible:
        return None
    return min(feasible, key=lambda option: (option[key], option["id"]))["id"]


def score_document(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise InputError("input must be a JSON object")
    raw_options = document.get("options")
    if not isinstance(raw_options, list) or not raw_options:
        raise InputError("options must be a non-empty array")
    weights = load_weights(document.get("weights"))
    options = [score_option(raw, weights) for raw in raw_options]
    ids = [option["id"] for option in options]
    if len(ids) != len(set(ids)):
        raise InputError("option ids must be unique")
    return {
        "weights": weights,
        "options": options,
        "rankings": {
            "lowest_cost": best_id(options, "cost_brl"),
            "shortest_absence": best_id(options, "hours_away"),
            "lowest_inconvenience": best_id(options, "inconvenience_score"),
            "pareto_frontier": pareto_frontier(options),
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
