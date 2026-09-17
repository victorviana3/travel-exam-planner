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


if __name__ == "__main__":
    unittest.main()
