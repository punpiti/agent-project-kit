#!/usr/bin/env python3
"""Regression checks for Thai/Latin Word run metadata."""

import importlib.util
from pathlib import Path

from lxml import etree


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "repair_thai_wordbreak_docx.py"
SPEC = importlib.util.spec_from_file_location("thai_docx_repair", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

W = MODULE.W
NS = {"w": W}
XML = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W}">
  <w:body>
    <w:p>
      <w:r><w:t>๖.๓ มก. สามารถนำโปรแกรมคอมพิวเตอร์ แบบจำลอง และ Nowcasting ไปใช้ในการวิจัย</w:t></w:r>
    </w:p>
  </w:body>
</w:document>
""".encode()

repaired, repaired_runs, split_runs = MODULE.repair_document(XML)
root = etree.fromstring(repaired)

assert repaired_runs == 1
assert split_runs == 1
assert "".join(root.xpath(".//w:t/text()", namespaces=NS)) == (
    "๖.๓ มก. สามารถนำโปรแกรมคอมพิวเตอร์ แบบจำลอง และ Nowcasting ไปใช้ในการวิจัย"
)

thai_runs = root.xpath(
    './/w:r[contains(string(w:t), "สามารถ") or contains(string(w:t), "วิจัย")]',
    namespaces=NS,
)
latin_runs = root.xpath('.//w:r[contains(string(w:t), "Nowcasting")]', namespaces=NS)
assert thai_runs
assert latin_runs

for run in thai_runs:
    language = run.find("w:rPr/w:lang", namespaces=NS)
    assert language is not None
    assert language.get(MODULE.QN("val")) == "th-TH"
    assert language.get(MODULE.QN("eastAsia")) == "th-TH"
    assert language.get(MODULE.QN("bidi")) == "th-TH"

for run in latin_runs:
    language = run.find("w:rPr/w:lang", namespaces=NS)
    assert language is not None
    assert language.get(MODULE.QN("val")) == "en-US"
    assert language.get(MODULE.QN("eastAsia")) == "en-US"
    assert language.get(MODULE.QN("bidi")) == "en-US"
    assert run.find("w:rPr/w:cs", namespaces=NS) is None

print("thai DOCX language metadata regression: PASS")
