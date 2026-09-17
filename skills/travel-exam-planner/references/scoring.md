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

Examples of risk items include arrival on the exam day, a connection with little recovery margin, a return too close to the expected end of the exam, or an inflexible ticket bought before the exam schedule is confirmed.

Do not add a risk item merely because an itinerary is unfamiliar. State the concrete failure mode.

## Selection

Do not combine BRL and inconvenience points into a hidden universal score. Use the Pareto frontier over cost, hours away, and inconvenience, then explain the judgment used for the three recommendations.

When two options are similar, quantify what the additional money buys, such as hours saved, a normal night's sleep, a direct flight, or a larger disruption buffer.
