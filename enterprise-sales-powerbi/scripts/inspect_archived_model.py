"""Read a private PBIX without rewriting it; export sanitized formulas and aggregates."""
from pathlib import Path
from decimal import Decimal
import argparse
import csv
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def sanitize_expression(text):
    text = re.sub(r'(?i)([A-Z]:\\Users\\)[^\\"\r\n]+', r'\1Anonymous', str(text))
    text = re.sub(r'Sql\.Database\("[^"]+"', 'Sql.Database(SqlServerInstance', text)
    text = re.sub(r'File\.Contents\("[^"\r\n]*Monthly_Budget\.xlsx"\)',
                  lambda _: 'File.Contents(ProjectRoot & "\\data\\budget\\Monthly_Budget.xlsx")', text)
    text = re.sub(r'File\.Contents\("[^"\r\n]*Salesperson_Target[^"\r\n]*"\)',
                  lambda _: 'File.Contents(ProjectRoot & "\\data\\targets\\Salesperson_Targets.csv")', text)
    return text


def inspect(path):
    from pbixray import PBIXRay
    model = PBIXRay(str(path))
    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    measures = model.dax_measures
    measures.to_csv(out / "archived_dax_measures.csv", index=False)
    queries = model.power_query.copy()
    for column in queries.columns:
        queries[column] = queries[column].map(sanitize_expression)
    queries.to_csv(out / "parameterized_power_query.csv", index=False)
    query_dir = ROOT / "powerbi" / "queries"
    query_dir.mkdir(exist_ok=True)
    for _, row in queries.iterrows():
        name = re.sub(r"[^A-Za-z0-9_-]", "_", str(row["TableName"]))
        (query_dir / (name + ".pq")).write_text(str(row["Expression"]), encoding="utf-8")
    (query_dir / "ProjectRoot.pq").write_text('"C:\\PROJECTS\\enterprise-sales-powerbi" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]', encoding="utf-8")
    (query_dir / "SqlServerInstance.pq").write_text('"localhost" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]', encoding="utf-8")
    model.schema.to_csv(out / "archived_model_schema.csv", index=False)
    totals = {}
    # Decode only the sales fact. No raw customer/person records are exported.
    sales = model.get_table("FactSales")
    totals["fact_rows"] = len(sales)
    for column in ["NetSalesAmount", "GrossProfitAmount", "TaxAmount", "InvoiceValueAmount", "Quantity"]:
        if column in sales:
            totals[column] = str(sum((Decimal(str(value)) for value in sales[column].dropna()), Decimal(0)))
    if "InvoiceID" in sales:
        totals["invoice_count"] = int(sales["InvoiceID"].nunique())
    import pandas as pd
    sales["InvoiceDate"] = pd.to_datetime(sales["InvoiceDate"])
    sales["Year"] = sales["InvoiceDate"].dt.year
    sales["YearMonth"] = sales["InvoiceDate"].dt.strftime("%Y-%m")
    monthly = sales.groupby("YearMonth")[["NetSalesAmount", "GrossProfitAmount", "Quantity"]].sum().reset_index()
    monthly.to_csv(out / "cached_monthly_actuals.csv", index=False)
    annual = sales.groupby(["SalespersonID", "Year"])["NetSalesAmount"].sum()
    mismatches = []
    with (ROOT / "data/targets/Salesperson_Targets.csv").open(encoding="utf-8-sig", newline="") as source:
        for target in csv.DictReader(source):
            person, year = int(target["SalespersonID"]), int(target["Year"])
            factor = {2014: Decimal("1.05"), 2015: Decimal("1.06"), 2016: Decimal("1.07")}[year]
            previous = annual.get((person, year - 1))
            expected = None if previous is None else (Decimal(str(previous)) * factor).quantize(Decimal("0.01"))
            if expected is None or abs(expected - Decimal(target["TargetAmount"])) > Decimal("0.01"):
                mismatches.append({"salesperson_label": f"Salesperson {person}", "year": year})
    if "IsLossMaking" in sales:
        loss = sales[sales["IsLossMaking"] == 1]
        totals["loss_making_lines"] = len(loss)
        totals["loss_making_revenue"] = str(sum((Decimal(str(v)) for v in loss["NetSalesAmount"]), Decimal(0)))
    result = {"inspection": "decoded cached import data and extracted formulas; no live SQL or DAX engine execution",
              "dax_measure_count": len(measures), "power_query_count": len(queries),
              "tables": sorted(set(str(value) for value in model.tables)), "cached_fact_totals": totals,
              "target_derivation_matches_cached_previous_year_actuals": not mismatches,
              "target_derivation_mismatches": mismatches,
              "latest_cached_sales_date": str(sales["InvoiceDate"].max().date()),
              "anonymity": "Original PBIX retained privately; exported formulas/metadata inspected separately. Refresh/save remains outstanding."}
    (out / "archived_model_inspection.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pbix", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.pbix), indent=2))
