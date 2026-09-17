---
name: travel-exam-planner
description: Plan door-to-door travel for in-person exams and concursos by combining the user's profile, calendar constraints, official exam details, current transport and lodging research, and a transparent comparison of cost, time, sleep, work impact, and risk. Use when planning, comparing, revising, or monitoring exam travel; do not use for ordinary leisure travel.
---

# Travel Exam Planner

Plan a feasible trip from the user's real origin to an in-person exam. Optimize the whole journey rather than an isolated airfare or hotel price. Use the configured objective to prioritize either best cost-benefit or lowest total cost.

## Boundaries

- Treat planning as read-only. Do not book, purchase, send messages, change calendar events, write to Drive, or create monitoring automations without explicit authorization for that action.
- Ask when a missing fact would materially change the result and cannot be handled safely with scenarios.
- Do not stop merely because the exam time or venue is unknown. Build explicit scenarios, identify decisions that are safe now, and identify decisions that should wait.
- Never assume that negotiable work leave has been approved.
- Keep financial cost in BRL separate from inconvenience points. Do not invent a monetary conversion for time, sleep, or risk.
- Treat purchase and reservation URLs as decision handoffs. Never claim that a link locks a price, inventory, or reservation.

## Profile and request

If `TRAVEL_EXAM_PLANNER_PROFILE` names a readable file, use it as the private profile. Otherwise, look for `~/.config/travel-exam-planner/profile.json`. Never publish, copy, or include the private profile in an artifact without permission. If no private profile is available, use `config/profile.example.json` only as a field guide and ask for material missing values.

For schemas and field meanings, read [references/data-model.md](references/data-model.md).

Use `optimization.objective` from the private profile when present. Supported values are `best_value` and `lowest_total_cost`; default to `best_value`. A request-specific objective overrides the profile for that request. If the user's wording does not resolve a material conflict between the two modes, state which configured mode is being applied.

## Tool routing

- Use Google Calendar to read schedule constraints when it is connected and the user asks to include their calendar. Calendar reads do not authorize event changes.
- Use Gmail only when the user asks to inspect exam notices, tickets, or reservations in email. Do not search unrelated mail.
- Prefer Decolar and Skyscanner for current flight discovery and Booking.com for lodging when those apps are available. Treat app results as quotes or booking handoffs, not completed purchases.
- Use direct carrier, bus-operator, hotel, airport, urban-transit, and organizing-body pages to verify decision-critical details. Use web search when a dedicated connector is unavailable or incomplete.
- Do not claim that a connector was checked if it was unavailable, unauthenticated, or returned no usable result. State the fallback used.

## Workflow

1. Identify the exam from the request and calendar. Confirm date, city, venue, start time, duration, and official notices from authoritative sources.
2. Establish hard constraints, negotiable constraints, and preferences. Calculate from the user's real origin, including access to the departure terminal and the final return home.
3. Generate scenarios for unresolved facts such as morning versus afternoon exams. Do not blend incompatible scenarios.
4. Research current flights, intercity buses, lodging, and local transport using the routing rules above, available connected tools, and direct web sources. Follow [references/source-policy.md](references/source-policy.md).
5. Normalize every viable option into the schema in [references/data-model.md](references/data-model.md). Include every unavoidable cost created by the itinerary as a separate cost item, including terminal access, fares, baggage, lodging nights, taxes, local transport, meals created by the itinerary, and booking fees.
6. Filter options that violate hard constraints. Score the remaining options with `scripts/score_options.py` and the rules in [references/scoring.md](references/scoring.md).
7. Apply the configured optimization objective:
   - `best_value`: choose the strongest option on the Pareto frontier after comparing the additional money with hours saved, sleep preserved, work disruption avoided, and risk reduced. Do not collapse BRL and inconvenience points into one hidden score.
   - `lowest_total_cost`: recommend the lowest-cost feasible option after hard constraints and mandatory buffers. Do not buy a lower price by making the itinerary infeasible; explain the operational inconvenience and risk retained.
8. Keep the other selected options as meaningful alternatives, including the cheapest feasible and shortest-absence options when they differ from the recommendation.
9. State what was verified, when it was verified, what remains uncertain, and whether each decision is safe now or should wait.
10. Create the final spreadsheet according to [references/spreadsheet-output.md](references/spreadsheet-output.md). Do not finish with prose alone.

## Required output

Return three decision-ready itinerary options by default. Return more only when distinct scenario branches or contingencies cannot be represented responsibly in three options. Return fewer only when fewer than three feasible, materially different itineraries exist. Never invent, duplicate, or lightly repackage options merely to reach a target count. When returning a number other than three, state briefly why.

For each selected option, provide:

- a door-to-door timeline;
- total estimated cost and every cost component;
- financial impact versus the cheapest feasible option, including the additional amount, percentage difference, hours saved, and cost per hour saved when meaningful;
- a plain-language explanation of what the extra spending buys or what inconvenience the savings require;
- nights of lodging and any early-arrival check-in issue;
- total hours away from the real origin;
- sleep and work impact;
- risk factors and contingency margin;
- inconvenience score with a short breakdown;
- source timestamps and important fare or cancellation conditions;
- purchase or reservation links for each item when a usable handoff URL exists, clearly distinguishing an exact offer from a provider search page;
- the next decision and its deadline, without performing it.

Do not dump an unfiltered list of fares. Briefly explain dominated alternatives only when their exclusion is not obvious.

Attach one verified `.xlsx` workbook containing the recommendation, scenario comparison, itemized costs, itinerary details, sources, and usable purchase/reservation links. If workbook creation is technically unavailable, state the limitation and provide the same tables as a CSV fallback; do not silently omit the spreadsheet.

## Deterministic scoring

Prepare a JSON document matching the option schema, then run from this skill directory:

```bash
python3 scripts/score_options.py input.json --pretty
```

Use the script's hard-constraint results, score breakdown, and Pareto frontier as evidence. The script does not choose the final itinerary and does not replace source verification.
