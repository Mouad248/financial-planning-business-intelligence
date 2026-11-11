"""Package the complete native report sources and anonymous refresh inputs."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def package() -> Path:
    names = {"README.md", ".gitignore", "tests/test_native_recovery.py"}
    for folder in ("powerbi/native", "powerbi/queries", "powerbi/snapshot-queries", "sql",
                   "data/model", "data/budget", "data/targets", "docs/licenses"):
        names.update(path.relative_to(ROOT).as_posix() for path in (ROOT / folder).rglob("*")
                     if path.is_file() and ".pbi" not in path.parts)
    for name in ("open_native_report.py", "prepare_dax_checks.py", "verify_native_model.ps1",
                 "validate_supporting_data.py", "repair_budget_metadata.py", "package_native_release.py"):
        names.add("scripts/" + name)
    names.update(("docs/verification.json", "docs/DAX_AND_POWER_QUERY.md",
                  "docs/UNDERSTAND_THE_PROJECT.md", "powerbi/REFRESH_ANONYMOUS_REPORT.md",
                  "reports/archived_dax_measures.csv", "reports/native_dax_verification.json",
                  "reports/native_project_structure.json", "reports/native_sales_performance.png",
                  "reports/supporting_data_validation.json"))
    if (ROOT / "reports/native_release_smoke.json").is_file():
        names.add("reports/native_release_smoke.json")
    files = {name: (ROOT / name).read_bytes() for name in sorted(names)}
    for name, body in files.items():
        if name.endswith((".json", ".bim", ".pbip", ".pbir", ".pbism", ".pq", ".py", ".ps1", ".md", ".txt", ".sql", ".csv")):
            text = body.decode("utf-8-sig").lower()
            if re.search(r"[a-z]:\\+users\\+[^\\/\"\r\n]+", text) or re.search(r"\bdesktop-[a-z0-9]{6,}\b", text):
                raise ValueError(f"Personal machine marker in release input: {name}")
    manifest = {name: hashlib.sha256(body).hexdigest() for name, body in files.items()}
    target = ROOT / "dist/enterprise-sales-powerbi-portfolio.zip"
    target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, body in files.items():
            archive.writestr(name, body)
        archive.writestr("RELEASE_MANIFEST.json", json.dumps(manifest, indent=2))
    print(f"Created {target.name}: {len(files)} files, {target.stat().st_size} bytes")
    return target


if __name__ == "__main__":
    package()
