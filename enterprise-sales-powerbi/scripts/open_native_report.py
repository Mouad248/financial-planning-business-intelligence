"""Open a machine-specific private copy of the native Power BI project."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def prepare_copy() -> Path:
    source = ROOT / "powerbi/native"
    destination = ROOT / ".private/native-open"
    destination.mkdir(parents=True, exist_ok=True)
    for path in source.rglob("*"):
        if path.is_file() and ".pbi" not in path.parts:
            target = destination / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    model_path = destination / "EnterpriseSales.SemanticModel/model.bim"
    model = json.loads(model_path.read_text(encoding="utf-8"))
    parameter = next(item for item in model["model"]["expressions"] if item["name"] == "ProjectRoot")
    parameter["expression"] = '"' + str(ROOT).replace('"', '""') + '" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
    model_path.write_text(json.dumps(model, indent=2, ensure_ascii=False), encoding="utf-8")
    return destination / "EnterpriseSales.pbip"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    report = prepare_copy()
    if args.prepare_only:
        print("Prepared the private machine-specific Power BI project.")
    elif os.name == "nt":
        os.startfile(report)
        print("Opened the native project. Use Refresh in Power BI to load the included full data snapshot.")
    else:
        raise SystemExit("Power BI Desktop requires Windows; the project files remain available for inspection.")
