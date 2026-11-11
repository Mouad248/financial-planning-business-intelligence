# Sales BI technical overview

## Business question

How much did the fictitious distributor sell, how profitable were the sales, and how did actuals compare with synthetic budgets and salesperson targets?

The analytical product consists of a SQL preparation layer, a Power BI semantic model and reports. Microsoft's Wide World Importers is sample data; budgets and targets are synthetic planning assumptions. No actual employer outcomes are claimed.

## Follow the data

1. The original relational database stores invoices, invoice lines, customers, products and people separately.
2. SQL views create an invoice-line fact and descriptive dimensions. `InvoiceLineID` is the fact grain. SQL source views now replace identity labels and suppress contacts.
3. Power Query imports SQL and planning files, unpivots monthly budget columns, assigns types and prepares the model.
4. Dimensions filter facts through relationships. Sales, company budgets and annual salesperson targets have different grains.
5. DAX measures calculate revenue/profit, ratios, time comparisons, rankings and target attainment. The report is a presentation over that model.

## Model assumptions

- **Grain:** one row per invoice line in sales, one per month in company budget, one per salesperson/year in targets. Joining them directly can duplicate values.
- **Additivity:** revenue and profit can be summed. Margin is total profit divided by total revenue, not an average of row margins.
- **Bridge:** products can belong to multiple stock groups. Filtering must avoid counting a sale multiple times across group totals.
- **Partial periods:** actual data ends during 2016. Comparing that partial year with a whole-year target can mislead; explain the exact comparable-period assumption.
- **Budget unpivot:** January–December columns become month rows; the supplied normalization script verifies annual totals first.
- **Anonymization boundary:** source masking does not rewrite a cached PBIX. Refresh every table, inspect metadata/filters and save a new file before sharing.
