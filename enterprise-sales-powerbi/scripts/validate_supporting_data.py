"""Validate and normalize bundled synthetic planning inputs; no SQL Server needed."""
from pathlib import Path
from datetime import date
from decimal import Decimal
import csv
import json

ROOT = Path(__file__).resolve().parents[1]


def validate():
    from openpyxl import load_workbook
    book = load_workbook(ROOT / "data/budget/Monthly_Budget.xlsx", data_only=True)
    rows = list(book.active.values)
    if rows[0][0] != "Year" or len(rows[0]) != 14:
        raise ValueError("Expected Year, twelve month columns and AnnualTotal")
    monthly, seen_years = [], set()
    for row in rows[1:]:
        year = int(row[0])
        if year in seen_years:
            raise ValueError("Duplicate budget year")
        seen_years.add(year)
        values = [Decimal(str(value)) for value in row[1:13]]
        if any(not amount.is_finite() or amount < 0 for amount in values):
            raise ValueError("Budget values must be finite and non-negative")
        if abs(sum(values) - Decimal(str(row[13]))) > Decimal("0.01"):
            raise ValueError(f"Monthly budget does not reconcile in {year}")
        monthly.extend({"BudgetMonth": date(year, month, 1).isoformat(), "BudgetAmount": str(value)} for month, value in enumerate(values, 1))
    target_file = ROOT / "data/targets/Salesperson_Targets.csv"
    with target_file.open(encoding="utf-8-sig", newline="") as source:
        targets = list(csv.DictReader(source))
    seen = set()
    for row in targets:
        key = (int(row["SalespersonID"]), int(row["Year"]))
        value = Decimal(row["TargetAmount"])
        if key in seen or key[1] not in seen_years or not value.is_finite() or value < 0:
            raise ValueError("Invalid or duplicate salesperson/year target")
        seen.add(key)
    if not seen or any((person, year) not in seen for person, _ in seen for year in seen_years):
        raise ValueError("Target coverage incomplete for a salesperson/year")
    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    with (out / "monthly_budget_normalized.csv").open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=["BudgetMonth", "BudgetAmount"])
        writer.writeheader()
        writer.writerows(monthly)
    result = {"data_kind": "synthetic planning inputs", "budget_months": len(monthly),
              "budget_years": sorted(seen_years), "target_rows": len(targets),
              "salespeople": len({person for person, _ in seen}),
              "checks": ["annual budget reconciliation", "non-negative finite amounts", "unique salesperson/year", "complete year coverage"],
              "unverified": ["targets versus previous-year source actuals", "SQL execution", "DAX execution", "Power BI refresh"]}
    (out / "supporting_data_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
