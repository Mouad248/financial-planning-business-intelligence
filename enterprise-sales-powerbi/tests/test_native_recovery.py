import csv
import io
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile
from decimal import Decimal
from pathlib import Path

from scripts import open_native_report, prepare_dax_checks
from scripts.repair_budget_metadata import repair

ROOT = Path(__file__).resolve().parents[1]


def test_original_dax_and_model_relationships_are_preserved():
    model = json.loads((ROOT / "powerbi/native/EnterpriseSales.SemanticModel/model.bim").read_text(encoding="utf-8"))["model"]
    actual = {(table["name"], measure["name"]): measure["expression"].strip()
              for table in model["tables"] for measure in table.get("measures", [])}
    with (ROOT / "reports/archived_dax_measures.csv").open(encoding="utf-8-sig", newline="") as stream:
        expected = {(row["TableName"], row["Name"]): row["Expression"].strip() for row in csv.DictReader(stream)}
    assert actual == expected and len(actual) == 66
    assert len(model["tables"]) == 14 and len(model["relationships"]) == 9
    bridge = next(r for r in model["relationships"] if r["fromTable"] == "BridgeProductStockGroup" and r["toTable"] == "DimProduct")
    assert bridge["crossFilteringBehavior"] == "bothDirections"
    partitions = {table["name"]: table["partitions"][0]["source"]["expression"] for table in model["tables"]}
    assert "Monthly_Budget.xlsx" in partitions["FactBudget"]
    assert "Salesperson_Targets.csv" in partitions["FactSalespersonTarget"]
    assert "Currency.Type" in partitions["FactBudget"]


def test_full_invoice_line_snapshot_reconciles_and_has_valid_keys():
    data = ROOT / "data/model"
    keys = {}
    for table, key in (("DimCustomer", "CustomerID"), ("DimProduct", "ProductID"), ("DimSalesperson", "SalespersonID")):
        with (data / f"{table}.csv").open(encoding="utf-8", newline="") as stream:
            keys[key] = {row[key] for row in csv.DictReader(stream)}
    seen, totals = set(), {"NetSalesAmount": Decimal(0), "GrossProfitAmount": Decimal(0)}
    with (data / "FactSales.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            assert row["InvoiceLineID"] not in seen
            seen.add(row["InvoiceLineID"])
            for key, values in keys.items():
                assert row[key] in values
            for column in totals:
                totals[column] += Decimal(row[column])
    assert len(seen) == 228265
    assert totals == {"NetSalesAmount": Decimal("172261341.20"), "GrossProfitAmount": Decimal("85729180.90")}


def test_anonymous_person_entities_and_contacts():
    data = ROOT / "data/model"
    with (data / "DimSalesperson.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            assert row["FullName"] == row["PreferredName"] == "Salesperson " + row["SalespersonID"]
            assert not row["EmailAddress"] and not row["PhoneNumber"]
    with (data / "DimCustomer.csv").open(encoding="utf-8", newline="") as stream:
        assert all(row["CustomerName"] == "Customer " + row["CustomerID"] for row in csv.DictReader(stream))


def test_workbook_metadata_type_prefixes_are_bound_and_repair_keeps_sheets(tmp_path):
    source = ROOT / "data/budget/Monthly_Budget.xlsx"
    with zipfile.ZipFile(source) as archive:
        core = archive.read("docProps/core.xml")
        namespaces = dict(item[1] for item in ET.iterparse(io.BytesIO(core), events=["start-ns"]))
        assert namespaces["dcterms"] == "http://purl.org/dc/terms/"
        sheets = {name: archive.read(name) for name in archive.namelist() if name.startswith("xl/")}
    target = tmp_path / "budget.xlsx"
    shutil.copy2(source, target)
    repair(target)
    with zipfile.ZipFile(target) as archive:
        assert all(archive.read(name) == body for name, body in sheets.items())


def test_opening_configures_only_a_private_machine_copy(tmp_path, monkeypatch):
    folder = tmp_path / "project"
    shutil.copytree(ROOT / "powerbi/native", folder / "powerbi/native")
    path = folder / "powerbi/native/EnterpriseSales.SemanticModel/model.bim"
    original = path.read_bytes()
    monkeypatch.setattr(open_native_report, "ROOT", folder)
    report = open_native_report.prepare_copy()
    assert report.is_relative_to(folder / ".private")
    assert path.read_bytes() == original
    model = json.loads((report.parent / "EnterpriseSales.SemanticModel/model.bim").read_text(encoding="utf-8"))
    expression = next(e["expression"] for e in model["model"]["expressions"] if e["name"] == "ProjectRoot")
    assert str(folder) in expression


def test_dax_reference_generation_works_in_a_fresh_extraction(tmp_path, monkeypatch):
    folder = tmp_path / "fresh-release"
    shutil.copytree(ROOT / "data/model", folder / "data/model")
    monkeypatch.setattr(prepare_dax_checks, "ROOT", folder)
    checks = prepare_dax_checks.prepare()
    assert len(checks) == 56
    assert (folder / ".private/native-work/dax-checks.dax").is_file()


def test_executive_budget_card_uses_comparable_period_measure():
    layout = json.loads((ROOT / "powerbi/native/EnterpriseSales.Report/report.json").read_text(encoding="utf-8"))
    page = next(p for p in layout["sections"] if p["displayName"] == "01_Executive Overview")
    properties = []

    def visit(value):
        if isinstance(value, dict):
            if "Measure" in value:
                properties.append(value["Measure"].get("Property"))
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, str) and value[:1] in {"{", "["}:
            try:
                visit(json.loads(value))
            except ValueError:
                pass

    visit(page)
    assert "Comparable Budget Attainment %" in properties
    assert "Budget Attainment %" not in properties
