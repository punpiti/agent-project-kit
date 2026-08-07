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

LEGACY_FONT_XML = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W}">
  <w:body>
    <w:p>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="TH SarabunPSK" w:hAnsi="THSarabunPSK"
                    w:eastAsia="TH Sarabun ๙" w:cs="TH Sarabun IT๙"/>
        </w:rPr>
        <w:t>ข้อความทดสอบ</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>
""".encode()

legacy_repaired, _, _ = MODULE.repair_document(LEGACY_FONT_XML)
legacy_root = etree.fromstring(legacy_repaired)
legacy_fonts = legacy_root.find(".//w:rFonts", namespaces=NS)
assert legacy_fonts is not None
for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
    assert legacy_fonts.get(MODULE.QN(attribute)) == "TH Sarabun New"

GENERIC_FONT_XML = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:fonts xmlns:w="{W}">
  <w:font w:name="th-sarabun-psk"><w:altName w:val="TH Sarabun 9"/></w:font>
</w:fonts>
""".encode()
generic_repaired, generic_count = MODULE.repair_font_names(GENERIC_FONT_XML)
generic_root = etree.fromstring(generic_repaired)
assert generic_count == 2
assert generic_root.find(".//w:font", namespaces=NS).get(MODULE.QN("name")) == "TH Sarabun New"
assert generic_root.find(".//w:altName", namespaces=NS).get(MODULE.QN("val")) == "TH Sarabun New"

print("thai DOCX language metadata regression: PASS")
