# Scoring model

Use hard constraints before scoring. An option that misses the exam, requires an impossible connection, or violates another declared absolute constraint is infeasible regardless of price.

Keep these dimensions visible and separate:

- total financial cost in BRL;
- total hours away from the real origin;
- inconvenience points;
- material uncertainty and unpriced risk.

## Default inconvenience weights

The deterministic script applies:

- 0.5 point per avoidable hour of travel, waiting, or dead time;
- 8 points per night in an airport;
- 5 points per event leaving fewer than the configured useful sleep threshold before the exam or work;
- 3 points per additional air connection;
- 5 points per airport change;
- 4 points per partially affected workday requiring negotiation;
- 12 points per fully affected workday requiring negotiation;
- explicit evidence-backed risk items, each with a reason and point value.

`avoidable_hours` represents travel, waiting, or dead time that does not provide another necessary function. Overnight transit that overlaps the user's normal sleep period may be excluded from avoidable hours only when the seat or berth, uninterrupted duration, transfers, and user profile support an `adequate` sleep assessment. Continue to count all elapsed time in `hours_away`.

Examples of risk items include arrival on the exam day, a connection with little recovery margin, a return too close to the expected end of the exam, or an inflexible ticket bought before the exam schedule is confirmed.

Do not add a risk item merely because an itinerary is unfamiliar. State the concrete failure mode.

## Selection

Do not combine BRL and inconvenience points into a hidden universal score.

- With `best_value`, use the Pareto frontier over cost, hours away, and inconvenience. Recommend the option whose incremental spending has the strongest practical return in saved time, sleep, work continuity, and reduced failure risk.
- With `lowest_total_cost`, recommend the cheapest feasible option. Hard constraints and mandatory exam buffers still apply; the objective does not authorize an unsafe or infeasible itinerary.

The script marks an option as dominated when another feasible option is no more expensive, no longer, and no more inconvenient, while being strictly better in at least one of those dimensions. Use `objective_result.candidates` as the final scenario pool. Do not present entries from `objective_result.excluded_dominated` as decision-ready alternatives.

A dominated itinerary may be mentioned outside the scenario pool only when it is useful to explain an exclusion. It may be retained as a separately labeled contingency only if it mitigates a specific verified failure mode that none of the eligible options mitigate; state that reason explicitly.

When two options are similar, quantify what the additional money buys, such as hours saved, a normal night's sleep, a direct flight, or a larger disruption buffer.

For every selected option, explain the financial impact relative to the cheapest feasible option. A saving is not self-explanatory: name the extra travel time, reduced sleep, work impact, connection exposure, or tighter buffer accepted in exchange.
