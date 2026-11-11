# Recovered DAX and Power Query

The original 66 DAX measures are retained unchanged in the reconstructed native Power BI project. Native refresh succeeded and 56 DAX/filter-context checks passed. The archived SQL-source M queries are preserved separately from the self-contained snapshot refresh mode. See `reports/archived_dax_measures.csv`, `reports/parameterized_power_query.csv` and individual `.pq` files under `powerbi/queries/`.

## Five useful measures to understand

**Revenue:** `SUM(FactSales[NetSalesAmount])`. It sums the invoice-line fact in the current filter context.

**Gross Margin %:** `DIVIDE([Gross Profit], [Revenue])`. It is a ratio of aggregate measures, not an average of row percentages. `DIVIDE` handles a zero denominator.

**Revenue PY:** `CALCULATE([Revenue], SAMEPERIODLASTYEAR(DimDate[Date]))`. It changes date filter context to the previous-year period. Correct results depend on the date table, relationships and selected period.

**Salesperson Revenue Rank:** uses `ISINSCOPE`, `RANKX` and `ALLSELECTED` over salesperson labels. It ranks within the selected context and suppresses totals outside the displayed salesperson level.

**Comparable Salesperson Target:** selects one year, computes months up to the latest sales date, and multiplies the annual target by months/12. This assumes uniform monthly target allocation. It deliberately returns blank without a single selected year; multi-year totals and within-month cutoffs need explicit review.

Other implemented expressions include YTD/PYTD, rolling 12-month revenue, loss-making activity, budget variance, selected metric titles and Top-N filters. Formula presence does not prove every slicer/bridge combination is correct.

## M transformations

The actual extracted queries import SQL BI views, convert monetary types, replace missing descriptive categories, construct a calendar, unpivot budget month columns and assign target-year dates. The recovered file paths and SQL host are parameterized to remove personal machine details.

Create `ProjectRoot` and `SqlServerInstance` text parameters in Power Query before using the `.pq` expressions. Example parameter files are provided; edit their placeholder values. They have not been evaluated by Power Query during this recovery. All table/column names remain aligned with the SQL views and extracted measures.

## What was independently checked outside Power BI

The parser decoded the cached 228,265-row fact table. Python reproduced the documented revenue, gross profit, tax, invoice value, quantity, invoice-count and loss-making totals. All 30 synthetic targets reconcile, to cents, to cached prior-year salesperson sales multiplied by the stated growth factors. The latest cached date is 2016-05-31.

`reports/cached_monthly_actuals.csv` contains anonymous monthly aggregates for inspection, not a refreshed Power BI report or replacement for live filter-context testing.
