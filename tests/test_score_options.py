import importlib.util
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "travel-exam-planner"
    / "scripts"
    / "score_options.py"
)
SPEC = importlib.util.spec_from_file_location("score_options", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def option(option_id, **overrides):
    value = {
        "id": option_id,
        "label": option_id,
        "cost_brl": 1000,
        "cost_items": [],
        "hours_away": 48,
        "avoidable_hours": 4,
        "airport_nights": 0,
        "low_sleep_events": 0,
        "air_connections": 0,
        "airport_changes": 0,
        "partial_workdays": 0,
        "full_workdays": 0,
        "risk_items": [],
        "hard_constraints": [{"name": "arrive", "satisfied": True, "detail": "ok"}],
    }
    value.update(overrides)
    if "cost_items" not in overrides:
        value["cost_items"] = [
            {
                "category": "transport",
                "description": "Test transport",
                "provider": "Test provider",
                "quantity": 1,
                "unit_cost_brl": value["cost_brl"],
                "total_cost_brl": value["cost_brl"],
                "price_status": "quote",
                "purchase_url": "https://example.com/buy",
                "source_url": "https://example.com/source",
                "verified_at": "2026-09-17T18:00:00-03:00",
                "conditions": "test",
            }
        ]
    return value


class ScoreOptionsTest(unittest.TestCase):
    def test_default_score(self):
        result = MODULE.score_document({"options": [option("a")]})
        self.assertEqual(result["options"][0]["inconvenience_score"], 2.0)
        self.assertEqual(result["rankings"]["pareto_frontier"], ["a"])

    def test_infeasible_option_is_not_ranked(self):
        blocked = option(
            "blocked",
            cost_brl=1,
            hard_constraints=[{"name": "arrive", "satisfied": False, "detail": "late"}],
        )
        result = MODULE.score_document({"options": [blocked, option("valid")]})
        self.assertEqual(result["rankings"]["lowest_cost"], "valid")
        self.assertFalse(result["options"][0]["feasible"])

    def test_pareto_frontier_excludes_dominated_option(self):
        better = option("better", cost_brl=900, hours_away=40, avoidable_hours=2)
        worse = option("worse", cost_brl=1000, hours_away=48, avoidable_hours=4)
        result = MODULE.score_document({"options": [better, worse]})
        self.assertEqual(result["rankings"]["pareto_frontier"], ["better"])

    def test_negative_value_is_rejected(self):
        with self.assertRaises(MODULE.InputError):
            MODULE.score_document({"options": [option("a", cost_brl=-1)]})

    def test_cost_items_must_reconcile(self):
        with self.assertRaises(MODULE.InputError):
            MODULE.score_document(
                {
                    "options": [
                        option(
                            "a",
                            cost_items=[
                                {
                                    "category": "hotel",
                                    "description": "One night",
                                    "provider": "Test hotel",
                                    "quantity": 1,
                                    "unit_cost_brl": 900,
                                    "total_cost_brl": 900,
                                    "price_status": "quote",
                                    "purchase_url": None,
                                    "source_url": "https://example.com/hotel",
                                    "verified_at": "2026-09-17T18:00:00-03:00",
                                    "conditions": "test",
                                }
                            ],
                        )
                    ]
                }
            )

    def test_financial_impact_is_relative_to_cheapest(self):
        result = MODULE.score_document(
            {
                "objective": "best_value",
                "options": [
                    option("cheap", cost_brl=1000, hours_away=50),
                    option("fast", cost_brl=1300, hours_away=44),
                ],
            }
        )
        impact = result["options"][1]["financial_impact"]
        self.assertEqual(impact["additional_cost_brl"], 300)
        self.assertEqual(impact["hours_saved_vs_cheapest"], 6)
        self.assertEqual(impact["cost_per_hour_saved_brl"], 50)

    def test_lowest_cost_objective_selects_cheapest(self):
        result = MODULE.score_document(
            {
                "objective": "lowest_total_cost",
                "options": [option("cheap", cost_brl=900), option("other", cost_brl=1000)],
            }
        )
        self.assertEqual(result["objective_result"]["automatic_selection"], "cheap")

    def test_unknown_objective_is_rejected(self):
        with self.assertRaises(MODULE.InputError):
            MODULE.score_document({"objective": "fastest", "options": [option("a")]})


if __name__ == "__main__":
    unittest.main()
