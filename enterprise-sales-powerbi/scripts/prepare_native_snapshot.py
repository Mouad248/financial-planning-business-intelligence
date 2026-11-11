"""Prepare anonymous CSV refresh inputs for the original Power BI semantic model."""

from __future__ import annotations

import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M_TYPES = {"int64": "Int64.Type", "double": "type number", "decimal": "Currency.Type",
           "dateTime": "type datetime", "boolean": "type logical", "string": "type text"}


def prepare() -> dict:
    private = ROOT / ".private/native-work"
    raw = private / "raw-tables"
    counts = json.loads((raw / "counts.json").read_text(encoding="utf-8-sig"))
    if counts.get("FactSales") != 228265:
        raise ValueError("The full original fact table must be exported before recovery")
    original = json.loads((private / "original-model.json").read_text(encoding="utf-8-sig"))
    destination = ROOT / "data/model"
    destination.mkdir(parents=True, exist_ok=True)
    query_dir = ROOT / "powerbi/snapshot-queries"
    query_dir.mkdir(parents=True, exist_ok=True)
    replacements = {}
    mappings = {}
    report = {"source": "Original Power BI cached Wide World Importers sample + synthetic planning inputs",
              "tables": {}, "financial_totals": {}, "measures_preserved": 66,
              "relationships_preserved": 9}
    for table in original["model"]["tables"]:
        name = table["name"]
        if name not in counts:
            continue
        columns = [column for column in table["columns"] if column.get("type") != "rowNumber"]
        with (raw / f"{name}.csv").open(encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            fields = reader.fieldnames
            rows = list(reader)
        if len(rows) != counts[name] or fields != [column["name"] for column in columns]:
            raise ValueError(f"Native export schema/count mismatch: {name}")
        if name == "DimProduct":
            suppliers = {value: f"Supplier {index:03d}" for index, value in enumerate(sorted({r["SupplierName"] for r in rows if r["SupplierName"]}), 1)}
            for row in rows:
                if row["SupplierName"]:
                    replacements[row["SupplierName"]] = suppliers[row["SupplierName"]]
                    row["SupplierName"] = suppliers[row["SupplierName"]]
        elif name == "DimCustomer":
            groups = {value: f"Buying Group {index:03d}" for index, value in enumerate(sorted({r["BuyingGroup"] for r in rows if r["BuyingGroup"] and r["BuyingGroup"] != "No Buying Group"}), 1)}
            for row in rows:
                replacements[row["CustomerName"]] = f"Customer {row['CustomerID']}"
                row["CustomerName"] = f"Customer {row['CustomerID']}"
                if row["BuyingGroup"] in groups:
                    replacements[row["BuyingGroup"]] = groups[row["BuyingGroup"]]
                    row["BuyingGroup"] = groups[row["BuyingGroup"]]
        elif name == "DimSalesperson":
            for row in rows:
                label = f"Salesperson {row['SalespersonID']}"
                for key in ("FullName", "PreferredName", "EmailAddress", "PhoneNumber"):
                    if row[key]:
                        replacements[row[key]] = label if key in ("FullName", "PreferredName") else ""
                    row[key] = label if key in ("FullName", "PreferredName") else ""
        elif name == "FactSales":
            if len({row["InvoiceLineID"] for row in rows}) != len(rows):
                raise ValueError("Duplicate invoice-line keys")
            report["financial_totals"] = {
                column: str(sum((Decimal(row[column]) for row in rows), Decimal(0)))
                for column in ("NetSalesAmount", "GrossProfitAmount", "TaxAmount", "InvoiceValueAmount", "Quantity")
            }
        target = destination / f"{name}.csv"
        with target.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        assignments = ", ".join('{"' + column["name"] + '", ' + M_TYPES[column["dataType"]] + '}' for column in columns)
        expression = (
            'let\n    Source = Csv.Document(File.Contents(ProjectRoot & "\\data\\model\\' + name + '.csv"), '
            '[Delimiter=",", Columns=' + str(len(columns)) + ', Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n'
            '    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n'
            '    Typed = Table.TransformColumnTypes(Headers, {' + assignments + '}, "en-US")\nin\n    Typed'
        )
        if name in {"FactBudget", "FactSalespersonTarget"}:
            expression = (ROOT / "powerbi/queries" / f"{name}.pq").read_text(encoding="utf-8")
            if name == "FactBudget":
                for month in ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "AnnualTotal"):
                    expression = expression.replace('{"' + month + '", Int64.Type}', '{"' + month + '", Currency.Type}')
            else:
                expression = expression.replace("Encoding=1252", "Encoding=65001").replace("QuoteStyle=QuoteStyle.None", "QuoteStyle=QuoteStyle.Csv")
        mappings[name] = expression
        (query_dir / f"{name}.pq").write_text(expression, encoding="utf-8")
        report["tables"][name] = {"rows": len(rows), "columns": len(columns), "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
    if Decimal(report["financial_totals"]["NetSalesAmount"]) != Decimal("172261341.20"):
        raise ValueError("Original revenue did not reconcile")
    (private / "snapshot-partitions.json").write_text(json.dumps(mappings, indent=2), encoding="utf-8")
    (private / "identity-replacements.json").write_text(json.dumps(replacements, indent=2), encoding="utf-8")
    (destination / "manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (query_dir / "ProjectRoot.pq").write_text('"C:\\Projects\\EnterpriseSales" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]', encoding="utf-8")
    print(f"Prepared {len(report['tables'])} full native-model tables; original revenue reconciles.")
    return report


if __name__ == "__main__":
    prepare()
