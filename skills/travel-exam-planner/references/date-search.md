# Date and fare discovery

Use this process before constructing the final itinerary scenarios. Its purpose is to keep an attractive schedule from being chosen before the fare landscape is known.

## Flexible flight discovery

Use a connector's flexible-date function before enumerating exact date pairs:

- With Skyscanner, use `flights_indicative_prices_cheapest_flight_dates_in_month` with `is_return: true` for each calendar month intersecting the search horizon. Filter the returned trips so arrival satisfies the exam buffer and return occurs after the exam can finish.
- With Decolar, use `flight_search_carrousel` with `month`, the broad feasible `stay_range`, and `order_by: total_price_ascending`, leaving exact dates unset. Use this when Skyscanner is unavailable or as a cross-check.
- Do not use Decolar `flight_deals` for a fixed exam destination; that capability is intended for open-ended destination discovery.
- Use monthly price trends only as context. They do not prove the cheapest itinerary containing a particular exam date.

Derive a finite search horizon from hard constraints and any user limit. When no maximum absence is configured, use 30 days before through 30 days after the exam for flexible airfare discovery. Disclose the horizon. Search each intersecting calendar month and retain only returned date pairs whose stay contains the exam and mandatory arrival and departure buffers.

Call the result the **lowest indicative airfare found within the disclosed horizon**, rather than an unqualified absolute minimum. Airline inventory, connector coverage, market, baggage, and cached indicative prices can prevent proof of a universal minimum.

Do not discard a longer stay before calculating its complete cost. After flexible discovery, validate the leading date pairs with exact-date quotes. Skyscanner live search may be called only once per user prompt and must be the final action of that turn; reserve it for the leading pair or a later confirmation turn. Use Decolar exact-date search or direct provider sources for the other shortlisted pairs.

## Candidate discovery

If flexible-date discovery is unavailable or returns no usable dates, search materially distinct date pairs manually and state the reduced coverage. Check round trips and useful combinations of separate one-way tickets. Include nonstop and one-stop results when both are feasible. Check alternate airports only when their complete door-to-door result can improve.

For each result retained from discovery, record:

- outbound and return dates and times;
- airports or terminals, stops, and operator;
- transport fare including unavoidable taxes and fees;
- included baggage and material fare restrictions;
- quote status, verification timestamp, source, and usable handoff URL;
- number of lodging nights and complete estimated trip cost;
- hours away and affected workdays.

Keep enough rows to establish, with evidence:

1. the cheapest transport fare in the feasible window;
2. the lowest complete financial cost after lodging and other unavoidable expenses;
3. the shortest feasible absence;
4. any additional non-dominated combination that materially improves sleep, work continuity, or failure margin.

These results become the candidate pool for full normalization and scoring. The cheapest fare is a required candidate, not an automatic recommendation.

## Inventory limitations

Use exact-date quotes when inventory is on sale. A route page, typical fare, or unspecific estimate does not establish the cheapest date. If inventory is not yet open or a source prevents a reliable comparison, state that date optimization is unavailable, show the dates actually checked, and label the result as a preliminary planning envelope rather than a decision-ready optimum.

## Other transport modes

Evaluate every plausible long-distance mode as a complete itinerary. Do not require a bus or train to be cheaper before it can enter the candidate pool. Overnight ground travel may preserve a normal sleep period, avoid an airport-night disruption, reduce lodging nights, or reduce work impact even when its fare is not the lowest.

Assess sleep from the actual schedule, service class, seat or berth, transfers, and the user's sleep threshold. Do not assume that all overnight buses provide useful sleep. When an overnight segment credibly provides useful sleep, exclude those hours from `avoidable_hours`, record the sleep assumptions, and keep `low_sleep_events` at zero only if the expected useful sleep meets the configured threshold.

Normalize the mode when it is materially distinct on any complete-trip dimension: financial cost, useful sleep, work impact, total absence, operational simplicity, or concrete failure risk. Let hard constraints and Pareto dominance decide whether it survives. Greater duration or a different vehicle alone is not meaningful diversification.
