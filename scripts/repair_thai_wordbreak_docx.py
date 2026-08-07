#!/usr/bin/env python3
"""Repair Thai complex-script metadata in a DOCX without changing its text."""

import argparse
from copy import deepcopy
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
QN = lambda name: f"{{{W}}}{name}"

KNOWN_PROPER_NAMES = (
    "STAiM",
    "PhET",
    "AILit",
    "ChatGPT",
    "CMKL",
    "ETDA",
    "OECD",
    "UNESCO",
    "GenAI",
    "iNaturalist",
    "TPACK",
)

LEGACY_THAI_FONT_KEYS = {
    "thsarabunpsk",
    "thsarabun๙",
    "thsarabunit๙",
    "thsarabun9",
    "thsarabunit9",
}
TARGET_THAI_FONT = "TH Sarabun New"


def font_key(name):
    """Normalize spacing/punctuation/case while preserving Thai or Latin digits."""
    return "".join(character for character in name.casefold() if character.isalnum())


def normalize_legacy_font_names(root):
    """Replace legacy TH Sarabun font attributes anywhere in an XML tree."""
    replacements = 0
    for element in root.iter():
        for attribute, value in list(element.attrib.items()):
            if font_key(value) in LEGACY_THAI_FONT_KEYS:
                element.set(attribute, TARGET_THAI_FONT)
                replacements += 1
    return replacements


def repair_font_names(xml_bytes):
    """Normalize legacy font names without rewriting XML when no match exists."""
    root = etree.fromstring(xml_bytes)
    replacements = normalize_legacy_font_names(root)
    if not replacements:
        return xml_bytes, 0
    return (
        etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True),
        replacements,
    )


def contains_thai(text):
    return any("\u0e00" <= character <= "\u0e7f" for character in text)


def contains_latin(text):
    return any(("A" <= character <= "Z") or ("a" <= character <= "z") for character in text)


def script_segments(text):
    """Split mixed Thai/Latin text without changing any character."""
    segments = []
    current = ""
    current_script = None
    for character in text:
        if "\u0e00" <= character <= "\u0e7f":
            script = "thai"
        elif ("A" <= character <= "Z") or ("a" <= character <= "z") or character.isdigit():
            script = "latin"
        else:
            script = None
        if script is not None and current_script is not None and script != current_script:
            segments.append((current_script, current))
            current = ""
        if script is not None:
            current_script = script
        current += character
    if current:
        segments.append((current_script or "latin", current))
    return segments


def ensure_child(parent, name, before=None):
    child = parent.find(QN(name))
    if child is None:
        child = etree.Element(QN(name))
        if before is not None:
            anchor = parent.find(QN(before))
            if anchor is not None:
                parent.insert(parent.index(anchor), child)
            else:
                parent.append(child)
        else:
            parent.append(child)
    return child


def repair_document(xml_bytes):
    root = etree.fromstring(xml_bytes)
    normalize_legacy_font_names(root)
    repaired_runs = 0
    split_runs = 0
    for run in list(root.xpath(".//w:r", namespaces=NS)):
        text = "".join(run.xpath(".//w:t/text() | .//w:delText/text()", namespaces=NS))
        if not contains_thai(text):
            continue
        properties = run.find(QN("rPr"))
        if properties is None:
            properties = etree.Element(QN("rPr"))
            run.insert(0, properties)

        fonts = ensure_child(properties, "rFonts")
        complex_font = (
            fonts.get(QN("cs"))
            or fonts.get(QN("hAnsi"))
            or fonts.get(QN("ascii"))
            or fonts.get(QN("eastAsia"))
            or "TH Sarabun New"
        )
        fonts.set(QN("cs"), complex_font)
        fonts.set(QN("hint"), "cs")
        ensure_child(properties, "cs")

        language = ensure_child(properties, "lang")
        # Word uses w:val for proofing and line-breaking behavior even when
        # w:eastAsia/w:bidi are present.  A Thai run marked en-US may wrap only
        # at spaces and may be checked with the English dictionary.
        language.set(QN("val"), "th-TH")
        language.set(QN("eastAsia"), "th-TH")
        language.set(QN("bidi"), "th-TH")
        repaired_runs += 1

        # A single run forced to Complex Script makes Word proof English words
        # with the Thai dictionary.  Split simple mixed-language runs exactly
        # as Word does when clean text is pasted back into the document.
        text_nodes = run.xpath("./w:t | ./w:delText", namespaces=NS)
        non_properties = [child for child in run if child.tag != QN("rPr")]
        simple_content = all(child.tag in (QN("t"), QN("delText"), QN("br")) for child in non_properties)
        if contains_latin(text) and len(text_nodes) == 1 and simple_content:
            segments = script_segments(text)
            if len(segments) > 1:
                parent = run.getparent()
                position = parent.index(run)
                source_text_tag = text_nodes[0].tag
                for offset, (script, segment) in enumerate(segments):
                    new_run = deepcopy(run)
                    if offset:
                        for line_break in new_run.findall(QN("br")):
                            new_run.remove(line_break)
                    new_text = new_run.find(source_text_tag)
                    new_text.text = segment
                    space_name = "{http://www.w3.org/XML/1998/namespace}space"
                    if segment.startswith(" ") or segment.endswith(" ") or "  " in segment:
                        new_text.set(space_name, "preserve")
                    elif space_name in new_text.attrib:
                        del new_text.attrib[space_name]
                    new_properties = new_run.find(QN("rPr"))
                    if script == "latin":
                        complex_toggle = new_properties.find(QN("cs"))
                        if complex_toggle is not None:
                            new_properties.remove(complex_toggle)
                        new_fonts = new_properties.find(QN("rFonts"))
                        if new_fonts is not None and new_fonts.get(QN("hint")) == "cs":
                            del new_fonts.attrib[QN("hint")]
                        new_language = ensure_child(new_properties, "lang")
                        new_language.set(QN("val"), "en-US")
                        new_language.set(QN("eastAsia"), "en-US")
                        new_language.set(QN("bidi"), "en-US")
                    else:
                        new_language = ensure_child(new_properties, "lang")
                        new_language.set(QN("val"), "th-TH")
                        new_language.set(QN("eastAsia"), "th-TH")
                        new_language.set(QN("bidi"), "th-TH")
                    parent.insert(position + offset, new_run)
                parent.remove(run)
                split_runs += 1

    # Keep Word from flagging stable project names and acronyms as English
    # misspellings.  Restrict this to Latin-only runs so surrounding Thai text
    # continues to be proofed normally.
    for run in root.xpath(".//w:r", namespaces=NS):
        text = "".join(run.xpath(".//w:t/text() | .//w:delText/text()", namespaces=NS))
        if contains_thai(text) or not any(name in text for name in KNOWN_PROPER_NAMES):
            continue
        properties = run.find(QN("rPr"))
        if properties is None:
            properties = etree.Element(QN("rPr"))
            run.insert(0, properties)
        ensure_child(properties, "noProof")

    return (
        etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True),
        repaired_runs,
        split_runs,
    )


def repair_styles(xml_bytes):
    root = etree.fromstring(xml_bytes)
    normalize_legacy_font_names(root)
    defaults = root.find(".//w:docDefaults/w:rPrDefault/w:rPr", namespaces=NS)
    if defaults is None:
        raise RuntimeError("styles.xml has no default run properties")
    fonts = ensure_child(defaults, "rFonts")
    if fonts.get(QN("cs")) is None:
        fonts.set(QN("cs"), "TH Sarabun New")
    # Do not force Complex Script at document-default level: that makes every
    # inherited Latin run use the Thai proofing language.  Thai runs receive
    # w:cs directly in repair_document().
    if fonts.get(QN("hint")) == "cs":
        del fonts.attrib[QN("hint")]
    complex_toggle = defaults.find(QN("cs"))
    if complex_toggle is not None:
        defaults.remove(complex_toggle)
    language = ensure_child(defaults, "lang")
    language.set(QN("val"), "en-US")
    language.set(QN("eastAsia"), "th-TH")
    language.set(QN("bidi"), "th-TH")
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def repair_settings(xml_bytes, enable_track_changes=False):
    root = etree.fromstring(xml_bytes)
    if enable_track_changes and root.find(QN("trackRevisions")) is None:
        root.insert(0, etree.Element(QN("trackRevisions")))
    language = root.find(QN("themeFontLang"))
    if language is None:
        language = etree.SubElement(root, QN("themeFontLang"))
    language.set(QN("val"), "en-US")
    language.set(QN("eastAsia"), "th-TH")
    language.set(QN("bidi"), "th-TH")
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--enable-track-changes", action="store_true")
    args = parser.parse_args()

    with ZipFile(args.source) as source:
        story_parts = {
            name
            for name in source.namelist()
            if name == "word/document.xml"
            or name == "word/footnotes.xml"
            or name == "word/endnotes.xml"
            or name == "word/comments.xml"
            or (name.startswith("word/header") and name.endswith(".xml"))
            or (name.startswith("word/footer") and name.endswith(".xml"))
        }
        repaired_payloads = {}
        repaired_runs = 0
        split_runs = 0
        normalized_auxiliary_font_references = 0
        for name in story_parts:
            payload, part_repaired_runs, part_split_runs = repair_document(source.read(name))
            repaired_payloads[name] = payload
            repaired_runs += part_repaired_runs
            split_runs += part_split_runs
        for name in source.namelist():
            if (
                name.startswith("word/")
                and name.endswith(".xml")
                and name not in story_parts
                and name not in {"word/styles.xml", "word/settings.xml"}
            ):
                payload, replacements = repair_font_names(source.read(name))
                if replacements:
                    repaired_payloads[name] = payload
                    normalized_auxiliary_font_references += replacements
        styles_xml = repair_styles(source.read("word/styles.xml"))
        settings_xml = repair_settings(
            source.read("word/settings.xml"),
            enable_track_changes=args.enable_track_changes,
        )
        with ZipFile(args.output, "w", ZIP_DEFLATED) as output:
            for item in source.infolist():
                if item.filename in repaired_payloads:
                    payload = repaired_payloads[item.filename]
                elif item.filename == "word/styles.xml":
                    payload = styles_xml
                elif item.filename == "word/settings.xml":
                    payload = settings_xml
                else:
                    payload = source.read(item.filename)
                output.writestr(item, payload)

    print(f"repaired_thai_runs={repaired_runs}")
    print(f"split_mixed_runs={split_runs}")
    print(f"repaired_story_parts={len(story_parts)}")
    print(
        "normalized_auxiliary_legacy_font_references="
        f"{normalized_auxiliary_font_references}"
    )


if __name__ == "__main__":
    main()
