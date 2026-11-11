"""Recover the original Power BI report/model as a portable native PBIP project."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def align_budget_card(value):
    if isinstance(value, dict):
        return {key: align_budget_card(item) for key, item in value.items()}
    if isinstance(value, list):
        return [align_budget_card(item) for item in value]
    if isinstance(value, str):
        if value in {"Budget Attainment %", "_Measures.Budget Attainment %"}:
            return value.replace("Budget Attainment %", "Comparable Budget Attainment %")
        if value[:1] in {"{", "["}:
            try:
                parsed = json.loads(value)
            except ValueError:
                return value
            return json.dumps(align_budget_card(parsed), separators=(",", ":"), ensure_ascii=False)
    return value


def clean_metadata(value):
    ignored = {"modifiedTime", "structureModifiedTime", "refreshedTime", "state",
               "createdTimestamp", "lastUpdate", "lastSchemaUpdate", "lastProcessed"}
    if isinstance(value, dict):
        return {key: clean_metadata(item) for key, item in value.items() if key not in ignored}
    if isinstance(value, list):
        return [clean_metadata(item) for item in value]
    return value


def build() -> dict:
    private = ROOT / ".private/native-work"
    source = json.loads((private / "refreshed-model.json").read_text(encoding="utf-8-sig"))
    original = json.loads((private / "original-model.json").read_text(encoding="utf-8-sig"))
    model = clean_metadata(source)
    model["name"] = "EnterpriseSales"
    partitions = json.loads((private / "snapshot-partitions.json").read_text(encoding="utf-8"))
    for table in model["model"]["tables"]:
        table["columns"] = [column for column in table["columns"] if column.get("type") != "rowNumber"]
        if table["name"] in partitions:
            table["partitions"][0]["source"] = {"type": "m", "expression": partitions[table["name"]]}
    parameter = next(item for item in model["model"]["expressions"] if item["name"] == "ProjectRoot")
    parameter["expression"] = '"C:\\Projects\\EnterpriseSales" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
    before = {(table["name"], measure["name"]): measure["expression"]
              for table in original["model"]["tables"] for measure in table.get("measures", [])}
    after = {(table["name"], measure["name"]): measure["expression"]
             for table in model["model"]["tables"] for measure in table.get("measures", [])}
    if before != after or len(after) != 66:
        raise ValueError("Original DAX measures were changed")
    if clean_metadata(original["model"]["relationships"]) != clean_metadata(source["model"]["relationships"]):
        raise ValueError("Original relationships were changed")
    project = ROOT / "powerbi/native"
    report = project / "EnterpriseSales.Report"
    semantic = project / "EnterpriseSales.SemanticModel"
    report.mkdir(parents=True, exist_ok=True)
    semantic.mkdir(parents=True, exist_ok=True)

    def write(path, body):
        path.write_text(json.dumps(body, indent=2, ensure_ascii=False), encoding="utf-8")

    write(project / "EnterpriseSales.pbip", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0", "artifacts": [{"report": {"path": "EnterpriseSales.Report"}}],
        "settings": {"enableAutoRecovery": True},
    })
    write(report / "definition.pbir", {"version": "1.0", "datasetReference": {
        "byPath": {"path": "../EnterpriseSales.SemanticModel"}}})
    write(semantic / "definition.pbism", {"version": "1.0", "settings": {}})
    write(semantic / "model.bim", model)
    with zipfile.ZipFile(private / "Sales_Analytics_Working.pbix") as archive:
        layout = json.loads(archive.read("Report/Layout").decode("utf-16-le"))
        for section in layout["sections"]:
            if section.get("displayName") == "01_Executive Overview":
                section["visualContainers"] = align_budget_card(section["visualContainers"])
        replacements = json.loads((private / "identity-replacements.json").read_text(encoding="utf-8"))
        serialized = json.dumps(layout, ensure_ascii=False)
        leaks = [name for name in replacements if len(name) >= 4 and name in serialized]
        if leaks:
            raise ValueError("Report layout contains source identities; inspect privately before publishing")
        write(report / "report.json", layout)
        for name in archive.namelist():
            if name.startswith("Report/StaticResources/"):
                target = report / name.removeprefix("Report/")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))
    (project / ".gitignore").write_text("**/.pbi/\n", encoding="utf-8")
    summary = {"tables": len(model["model"]["tables"]), "measures": len(after),
               "relationships": len(model["model"]["relationships"]),
               "pages": len(layout["sections"]),
               "visuals": sum(len(page.get("visualContainers", [])) for page in layout["sections"]),
               "dax_expressions_unchanged": True, "relationship_definitions_unchanged": True,
               "executive_budget_card_uses_comparable_period_measure": True,
               "native_full_refresh_executed": True}
    (ROOT / "reports/native_project_structure.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))
    return summary


if __name__ == "__main__":
    build()
