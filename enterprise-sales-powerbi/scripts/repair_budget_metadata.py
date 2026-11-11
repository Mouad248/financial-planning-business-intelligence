"""Repair Office date namespace bindings without changing worksheet contents."""

from __future__ import annotations

import hashlib
import io
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def repair(path: Path) -> dict:
    for prefix, uri in (
        ("cp", "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"),
        ("dc", "http://purl.org/dc/elements/1.1/"),
        ("dcterms", "http://purl.org/dc/terms/"),
        ("xsi", "http://www.w3.org/2001/XMLSchema-instance"),
    ):
        ET.register_namespace(prefix, uri)
    with zipfile.ZipFile(path) as archive:
        metadata = ET.fromstring(archive.read("docProps/core.xml"))
        corrected = ET.tostring(metadata, encoding="utf-8", xml_declaration=True)
        namespaces = dict(event[1] for event in ET.iterparse(io.BytesIO(corrected), events=["start-ns"]))
        for node in metadata.iter():
            type_name = node.get("{http://www.w3.org/2001/XMLSchema-instance}type", "")
            if ":" in type_name and type_name.split(":")[0] not in namespaces:
                raise ValueError("Unbound Office metadata type prefix")
        original_hashes = {name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist() if name != "docProps/core.xml"}
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as output:
            for info in archive.infolist():
                output.writestr(info, corrected if info.filename == "docProps/core.xml" else archive.read(info.filename))
    with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as output:
        assert all(hashlib.sha256(output.read(name)).hexdigest() == digest for name, digest in original_hashes.items())
    temporary = path.with_suffix(".xlsx.fixed")
    temporary.write_bytes(buffer.getvalue())
    temporary.replace(path)
    return {"metadata_namespace_repaired": True, "other_workbook_members_byte_identical": len(original_hashes)}


if __name__ == "__main__":
    workbook = ROOT / "data/budget/Monthly_Budget.xlsx"
    backup = ROOT / ".private/backups/before-native-recovery/data/budget/Monthly_Budget.xlsx"
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        shutil.copy2(workbook, backup)
    print(repair(workbook))
