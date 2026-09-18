# Data model

## Private profile

The optional private profile comes from the path in `TRAVEL_EXAM_PLANNER_PROFILE` or, by default, `~/.config/travel-exam-planner/profile.json`. It stays outside the plugin package. Its main fields are:

- `home_base`: real city, state, and country from which door-to-door timing begins;
- `work`: where schedule constraints come from and whether negotiation is possible;
- `sleep`: threshold used to identify a materially short night;
- `preferences`: currency, lodging, baggage, and airport-overnight preferences.
- `optimization.objective`: `best_value` or `lowest_total_cost`; defaults to `best_value`.

Do not infer an exact address, normal work schedule, baggage requirement, or approved leave from an empty field.

## Scoring input

The script accepts a JSON object containing `options`, an optional `weights` object, and an optional `objective` (`best_value` or `lowest_total_cost`). Build `options` from the date-search candidate pool described in [date-search.md](date-search.md), rather than from dates selected in advance.

Each option requires:

```json
{
  "id": "option-a",
  "label": "Direct flight and Sunday return",
  "cost_brl": 2492.0,
  "cost_items": [
    {
      "category": "flight",
      "description": "Round-trip direct flight",
      "provider": "Airline or agency",
      "quantity": 1,
      "unit_cost_brl": 1800.0,
      "total_cost_brl": 1800.0,
      "price_status": "quote",
      "purchase_url": "https://provider.example/offer",
      "source_url": "https://provider.example/offer",
      "verified_at": "2026-09-17T18:00:00-03:00",
      "conditions": "Personal item included; checked baggage excluded"
    }
  ],
  "hours_away": 52.0,
  "avoidable_hours": 4.0,
  "airport_nights": 0,
  "low_sleep_events": 0,
  "sleep_assessment": {
    "quality": "adequate",
    "usable_sleep_hours": 7.0,
    "normal_sleep_hours_covered": 7.0,
    "detail": "Overnight semi-sleeper segment without transfers"
  },
  "air_connections": 1,
  "airport_changes": 0,
  "partial_workdays": 0,
  "full_workdays": 0,
  "risk_items": [
    {"reason": "Return leaves limited delay margin", "points": 2.0}
  ],
  "hard_constraints": [
    {"name": "Arrive before exam buffer", "satisfied": true, "detail": "Arrives one day earlier"}
  ]
}
```

All numeric counts and durations must be non-negative. `air_connections` means additional connections, not flight segments. `low_sleep_events` counts distinct exam or work mornings below the profile's useful-sleep threshold.

`sleep_assessment` is optional. Use `quality` values `poor`, `limited`, or `adequate`; record expected usable sleep hours, how much of the user's normal sleep period the itinerary covers, and the concrete assumption behind the assessment. Do not infer sleep quality from the transport mode alone. `avoidable_hours` may exclude in-transit hours only when they overlap the normal sleep period and the assessment supports useful sleep.

`cost_items` must contain every unavoidable expense. Supported `price_status` values are `quote`, `estimate`, and `confirmed`. Use `purchase_url: null` when an item has no useful purchase or reservation handoff. Use `source_url` for the evidence behind the price. Both URL fields must use HTTPS when present. `cost_brl` must equal the sum of `total_cost_brl` across all cost items within one cent.

`risk_items` are judgments made from verified itinerary facts. Their reasons must be specific. `hard_constraints` must include each declared absolute constraint, including arrival buffer and any non-negotiable work commitment.

The output contains feasibility, normalized cost items, blocking constraints, a score breakdown, convenience rankings, the Pareto frontier, dominance evidence, selection eligibility, and financial impact versus the cheapest feasible option. `objective_result.candidates` is the eligible final scenario pool. `objective_result.excluded_dominated` identifies options that must not be used to fill the requested scenario count. For a more expensive option it reports additional cost, percentage above the cheapest, hours saved, and cost per hour saved when applicable.
