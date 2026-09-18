# Spreadsheet output

Create one `.xlsx` workbook after the itinerary analysis. Use the available spreadsheet authoring capability and follow its validation and rendering requirements. The workbook is part of the answer, not an optional appendix.

## Workbook structure

Use these worksheets unless the available data is too small to justify a separate itinerary sheet:

1. `Resumo`: configured objective, recommended option, scenario totals, difference from the cheapest feasible option, percentage difference, hours away, hours saved, cost per hour saved, inconvenience score, principal risks, and recommendation rationale.
2. `Pesquisa de datas`: one row per retained fare/date combination, including dates, times, provider, stops, transport fare, lodging nights, complete trip cost, hours away, work impact, quote status, verification timestamp, and source or handoff link. Record the flexible-search horizon and identify the lowest indicative airfare found, lowest complete cost, shortest absence, non-dominated candidates, and excluded dominated results.
3. `Custos`: one row per cost item with scenario, category, description, provider, quantity, unit cost, total cost, price status, important conditions, verification timestamp, purchase/reservation link, and source link.
4. `Roteiro`: chronological door-to-door events for each scenario, including local access, terminals, transport segments, lodging, exam buffer, and return home.

## Calculation and link rules

- Store currency, quantities, durations, dates, and timestamps as typed values rather than formatted text.
- Calculate scenario totals from the itemized cost rows. Reconcile each total to the normalized option total and resolve any mismatch before delivery.
- Use formulas for deltas, percentages, hours saved, and cost per hour saved. Leave cost per hour saved unavailable when no hours are saved.
- Format BRL consistently and keep enough precision to reconcile cents.
- Add real spreadsheet hyperlinks for purchase/reservation and source URLs. Label whether each purchase link is an exact offer, a booking handoff, or a provider search page.
- Never fabricate a deep link. If a connector does not expose a reusable URL, link to the closest verified provider page and state the limitation; leave the purchase link blank when no honest handoff is possible.
- Include fare, baggage, cancellation, check-in, tax, and availability conditions beside the relevant item.
- Freeze headers, enable filters on detail tables, fit columns, and visually verify every worksheet before export.

The final response must attach or link the workbook and summarize the configured objective and selected recommendation.
