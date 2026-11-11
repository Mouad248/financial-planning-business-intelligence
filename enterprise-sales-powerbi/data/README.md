# Supporting Data

This folder contains synthetic planning data created specifically for the portfolio project.

## Monthly Budget

`budget/Monthly_Budget.xlsx`

Monthly company-level revenue budgets for 2014–2016.

The budget data is synthetic and was created for demonstrating:

- multi-source Power BI modelling
- Power Query transformations
- budget vs actual analysis
- comparable-period reporting

## Salesperson Targets

`targets/Salesperson_Targets.csv`

Annual salesperson revenue targets for 2014–2016.

Targets were generated from prior-year actual revenue using the following planning assumptions:

- 2014 target = 2013 actual × 1.05
- 2015 target = 2014 actual × 1.06
- 2016 target = 2015 actual × 1.07

These targets are synthetic and are not part of the original Wide World Importers dataset.

2016 sales actuals end on 31 May 2016. The Power BI model therefore includes comparable-period logic to avoid comparing five months of actual sales directly with a full-year target.