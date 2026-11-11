"""Prepare independent expected values for native DAX/filter-context regression checks."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def prepare() -> list[dict]:
    data = ROOT / "data/model"
    yearly = defaultdict(lambda: defaultdict(Decimal))
    people = defaultdict(Decimal)
    products = defaultdict(Decimal)
    monthly = defaultdict(Decimal)
    totals = defaultdict(Decimal)
    invoices = set()
    with (data / "FactSales.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            year = int(row["InvoiceDate"][:4])
            for name in ("NetSalesAmount", "GrossProfitAmount", "CostAmount", "Quantity"):
                amount = Decimal(row[name])
                yearly[year][name] += amount
                totals[name] += amount
            revenue = Decimal(row["NetSalesAmount"])
            people[int(row["SalespersonID"])] += revenue
            products[int(row["ProductID"])] += revenue
            monthly[row["InvoiceDate"][:7]] += revenue
            invoices.add(row["InvoiceID"])
    budget, targets = defaultdict(Decimal), defaultdict(Decimal)
    budget_to_cutoff = Decimal(0)
    comparable_budget = Decimal(0)
    for name, field, output in (("FactBudget", "BudgetAmount", budget), ("FactSalespersonTarget", "TargetAmount", targets)):
        with (data / f"{name}.csv").open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream):
                output[int(row["Year"])] += Decimal(row[field])
                if name == "FactBudget" and "2016-01" <= row["BudgetMonth"][:7] <= "2016-05":
                    budget_to_cutoff += Decimal(row[field])
                if name == "FactBudget" and row["BudgetMonth"][:7] <= "2016-05":
                    comparable_budget += Decimal(row[field])
    cases = []

    def add(name, expression, expected, tolerance="0.005"):
        cases.append({"name": name, "expression": expression,
                      "expected": None if expected is None else str(expected), "tolerance": tolerance})

    for column, measure in (("NetSalesAmount", "Revenue"), ("GrossProfitAmount", "Gross Profit"), ("CostAmount", "Cost of Goods Sold"), ("Quantity", "Units Sold")):
        add(f"total/{measure}", f"[{measure}]", totals[column])
    add("total/invoice-count", "[Invoice Count]", len(invoices))
    add("total/weighted-margin", "[Gross Margin %]", totals["GrossProfitAmount"] / totals["NetSalesAmount"], "0.000000001")
    for year in sorted(yearly):
        for column, measure in (("NetSalesAmount", "Revenue"), ("GrossProfitAmount", "Gross Profit")):
            add(f"year/{year}/{measure}", f"CALCULATE([{measure}], TREATAS({{{year}}}, DimDate[Year]))", yearly[year][column])
        add(f"year/{year}/budget", f"CALCULATE([Budget], TREATAS({{{year}}}, DimDate[Year]))", budget.get(year))
        add(f"year/{year}/target", f"CALCULATE([Salesperson Target], TREATAS({{{year}}}, DimDate[Year]))", targets.get(year))
        if year - 1 in yearly:
            add(f"year/{year}/previous-year", f"CALCULATE([Revenue PY], TREATAS({{{year}}}, DimDate[Year]))", yearly[year - 1]["NetSalesAmount"])
    pytd = sum((value for month, value in monthly.items() if "2015-01" <= month <= "2015-05"), Decimal(0))
    add("partial-period/2016-PYTD", "CALCULATE([Revenue PYTD], TREATAS({2016}, DimDate[Year]))", pytd)
    add("partial-period/2016-budget-cutoff", "CALCULATE([Current Year Budget to Cutoff], TREATAS({2016}, DimDate[Year]))", budget_to_cutoff)
    add("partial-period/2016-comparable-target", "CALCULATE([Comparable Salesperson Target], TREATAS({2016}, DimDate[Year]))", targets[2016] * Decimal(5) / Decimal(12))
    add("partial-period/multiyear-target-blank", "[Comparable Salesperson Target]", None)
    comparable_revenue = sum((value for month, value in monthly.items() if "2014-01" <= month <= "2016-05"), Decimal(0))
    add("budget/comparable-revenue", "[Comparable Revenue]", comparable_revenue)
    add("budget/comparable-budget", "[Comparable Budget]", comparable_budget)
    add("budget/comparable-attainment", "[Comparable Budget Attainment %]", comparable_revenue / comparable_budget, "0.000000001")
    rolling = sum((value for month, value in monthly.items() if "2015-06" <= month <= "2016-05"), Decimal(0))
    add("time/rolling-12-months", "CALCULATE([Rolling 12M Revenue], FILTER(ALL(DimDate), DimDate[Date] = DATE(2016,5,31)))", rolling)
    add("time/rolling-future-blank", "CALCULATE([Rolling 12M Revenue], FILTER(ALL(DimDate), DimDate[Date] = DATE(2016,12,31)))", None)
    for person, revenue in sorted(people.items()):
        add(f"salesperson/{person}", f"CALCULATE([Revenue], TREATAS({{{person}}}, DimSalesperson[SalespersonID]))", revenue)
    groups = defaultdict(set)
    with (data / "BridgeProductStockGroup.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            groups[int(row["StockGroupID"])].add(int(row["ProductID"]))
    for group, members in sorted(groups.items()):
        add(f"bridge/group-{group}", f"CALCULATE([Revenue], TREATAS({{{group}}}, DimStockGroup[StockGroupID]))", sum((products[p] for p in members), Decimal(0)))
    selected = sorted(groups)[:2]
    members = groups[selected[0]] | groups[selected[1]]
    add("bridge/multiselect-union", "CALCULATE([Revenue], TREATAS({" + ",".join(map(str, selected)) + "}, DimStockGroup[StockGroupID]))", sum((products[p] for p in members), Decimal(0)))
    add("privacy/salesperson-labels-and-contacts", 'COALESCE(COUNTROWS(FILTER(DimSalesperson, LEFT(DimSalesperson[FullName],12) <> "Salesperson " || LEN(COALESCE(DimSalesperson[EmailAddress],"")) > 0 || LEN(COALESCE(DimSalesperson[PhoneNumber],"")) > 0)),0)', 0)
    add("privacy/customer-labels", 'COALESCE(COUNTROWS(FILTER(DimCustomer, DimCustomer[CustomerName] <> "Customer " & FORMAT(DimCustomer[CustomerID],"0"))),0)', 0)
    folder = ROOT / ".private/native-work"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "dax-checks.json").write_text(json.dumps(cases, indent=2), encoding="utf-8")
    query = "EVALUATE UNION(\n" + ",\n".join('ROW("Check", "' + case["name"] + '", "Actual", ' + case["expression"] + ')' for case in cases) + "\n)"
    (folder / "dax-checks.dax").write_text(query, encoding="utf-8")
    print(f"Prepared {len(cases)} native DAX cases with independent CSV/Decimal reference values.")
    return cases


if __name__ == "__main__":
    prepare()
