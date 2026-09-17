# Data model

## Private profile

The optional private profile comes from the path in `TRAVEL_EXAM_PLANNER_PROFILE` or, by default, `~/.config/travel-exam-planner/profile.json`. It stays outside the plugin package. Its main fields are:

- `home_base`: real city, state, and country from which door-to-door timing begins;
- `work`: where schedule constraints come from and whether negotiation is possible;
- `sleep`: threshold used to identify a materially short night;
- `preferences`: currency, lodging, baggage, and airport-overnight preferences.

Do not infer an exact address, normal work schedule, baggage requirement, or approved leave from an empty field.

## Scoring input

The script accepts a JSON object containing `options` and an optional `weights` object.

Each option requires:

```json
{
  "id": "option-a",
  "label": "Direct flight and Sunday return",
  "cost_brl": 2492.0,
  "hours_away": 52.0,
  "avoidable_hours": 4.0,
  "airport_nights": 0,
  "low_sleep_events": 0,
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

`risk_items` are judgments made from verified itinerary facts. Their reasons must be specific. `hard_constraints` must include each declared absolute constraint, including arrival buffer and any non-negotiable work commitment.

The output contains feasibility, blocking constraints, a score breakdown, convenience rankings, and the Pareto frontier over cost, hours away, and inconvenience.
