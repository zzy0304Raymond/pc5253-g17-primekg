"""Preserve the reviewed PPTX while inserting text-only bookends and notes.

Called by build_final_deck.mjs. Quantitative slides and all their dependencies
are retained byte for byte; only the cover, selected notes and slide order change.
"""
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"p": P, "a": A}
for prefix, uri in (("p", P), ("a", A), ("r", R)):
    ET.register_namespace(prefix, uri)


def xml(root):
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def body_notes(data):
    root = ET.fromstring(data)
    for shape in root.findall(".//p:sp", NS):
        ph = shape.find(".//p:ph", NS)
        if ph is not None and ph.get("type") == "body":
            return root, shape.find("p:txBody", NS)
    raise ValueError("Expected a speaker-notes body placeholder")


def put_notes(data, text):
    root, body = body_notes(data)
    for paragraph in list(body.findall("a:p", NS)):
        body.remove(paragraph)
    for line in text.splitlines():
        paragraph = ET.SubElement(body, f"{{{A}}}p")
        run = ET.SubElement(paragraph, f"{{{A}}}r")
        ET.SubElement(run, f"{{{A}}}t").text = line
    return xml(root)


def read_notes(data):
    _, body = body_notes(data)
    return "\n".join("".join(e.text or "" for e in p.findall(".//a:t", NS))
                     for p in body.findall("a:p", NS))


def replace_shapes(original, authored):
    # Keep the source slide's namespace context and layout relationship.
    pattern = rb"<p:spTree\b[^>]*>.*?</p:spTree>"
    tree = re.search(pattern, authored, flags=re.S)
    if not tree:
        raise ValueError("Authored slide has no shape tree")
    result, count = re.subn(pattern, lambda _: tree.group(), original, count=1, flags=re.S)
    if count != 1:
        raise ValueError("Source slide has no shape tree")
    return result


def main():
    bookends, candidate = map(Path, sys.argv[1:])
    source = ROOT / "slides/G17_working_draft_with_D.pptx"
    with ZipFile(source) as z:
        parts = {name: z.read(name) for name in z.namelist()}
    with ZipFile(bookends) as z:
        cover, thanks = (z.read(f"ppt/slides/slide{i}.xml") for i in (1, 2))
    source_cover = parts["ppt/slides/slide1.xml"]
    parts["ppt/slides/slide1.xml"] = replace_shapes(source_cover, cover)
    parts["ppt/slides/slide18.xml"] = replace_shapes(source_cover, thanks)

    def note_part(slide):
        rels = ET.fromstring(parts[f"ppt/slides/_rels/slide{slide}.xml.rels"])
        target = next(r.get("Target") for r in rels if r.get("Type").endswith("/notesSlide"))
        return posixpath.normpath(posixpath.join("ppt/slides", target))

    notes1 = note_part(1)
    a_notes = (ROOT / "slides/A_speaker_notes.md").read_text(encoding="utf-8")
    b_notes = (ROOT / "slides/B_speaker_notes.md").read_text(encoding="utf-8")
    replacements = {
        1: "Today we ask how losing relations changes both the connectivity of a knowledge graph and its ability to answer queries. We compare random failures, targeted attacks, retrieval theory and restoration on one shared PrimeKG benchmark.",
        3: a_notes.split("## Slide 3", 1)[1].split("\n\n", 1)[1].split("\n## Slide 4", 1)[0].strip()
           + "\n\nSource: slides/A_speaker_notes.md; data/processed/primekg_5000_bfs_v1.",
        4: a_notes.split("## Slide 4", 1)[1].split("\n\n", 1)[1].split("\n## Q&A", 1)[0].strip()
           + "\n\nSource: slides/A_speaker_notes.md; results/ws1. The GF reference agrees with D's solver.",
        5: b_notes.split("## Script", 1)[1].split("## Sources", 1)[0].strip()
           + "\n\nSource: B's ws2 attack and hub-composition tables; D's ws4 attack overlay. Random curves use ten seeds; targeted rankings are fixed.",
        17: "At the same five-percent node loss, both targeted attacks reduce the largest component and retrieval more than random removal. The effect is much larger for retrieval: degree attack adds about seven percentage points of structural loss, but about fifty-six points of retrieval loss. Beyond ten-percent damage, the two attacks differ by at most two of the two hundred queries, so we do not rank them."
            + "\n\nSource: results/ws4/primekg_5000_bfs_v1__equal_damage.csv and __equal_damage_summary.csv.",
    }
    for slide, text in replacements.items():
        name = note_part(slide)
        parts[name] = put_notes(parts[name], text)

    # A new notes part points to the new physical slide18, presented as page15.
    thanks_note = "Thank you for listening. We welcome your questions."
    parts["ppt/notesSlides/notesSlide18.xml"] = put_notes(parts[notes1], thanks_note)
    slide_rels = ET.fromstring(parts["ppt/slides/_rels/slide1.xml.rels"])
    for rel in slide_rels:
        if rel.get("Type").endswith("/notesSlide"):
            rel.set("Target", "../notesSlides/notesSlide18.xml")
    parts["ppt/slides/_rels/slide18.xml.rels"] = xml(slide_rels)
    original_notes_rels = posixpath.join(posixpath.dirname(notes1), "_rels", posixpath.basename(notes1) + ".rels")
    notes_rels = ET.fromstring(parts[original_notes_rels])
    for rel in notes_rels:
        if rel.get("Type").endswith("/slide"):
            rel.set("Target", "../slides/slide18.xml")
    parts["ppt/notesSlides/_rels/notesSlide18.xml.rels"] = xml(notes_rels)

    presentation_rels = ET.fromstring(parts["ppt/_rels/presentation.xml.rels"])
    new_rid = "rIdThankYou"
    if any(r.get("Id") == new_rid for r in presentation_rels):
        raise ValueError("Thank-you relationship already exists in the source")
    ET.SubElement(presentation_rels, f"{{{PKG}}}Relationship", {
        "Id": new_rid, "Type": R + "/slide", "Target": "slides/slide18.xml"})
    parts["ppt/_rels/presentation.xml.rels"] = xml(presentation_rels)
    presentation = ET.fromstring(parts["ppt/presentation.xml"])
    ids = presentation.find("p:sldIdLst", NS)
    if len(ids) != 17:
        raise ValueError("Expected the reviewed fourteen-page deck plus three backups")
    new_id = max(int(s.get("id")) for s in ids) + 1
    ids.insert(14, ET.Element(f"{{{P}}}sldId", {"id": str(new_id), f"{{{R}}}id": new_rid}))
    parts["ppt/presentation.xml"] = xml(presentation)
    content_types = ET.fromstring(parts["[Content_Types].xml"])
    for name, suffix in (("slides/slide18.xml", "slide"), ("notesSlides/notesSlide18.xml", "notesSlide")):
        ET.SubElement(content_types, f"{{{CT}}}Override", {
            "PartName": "/ppt/" + name,
            "ContentType": "application/vnd.openxmlformats-officedocument.presentationml." + suffix + "+xml"})
    ET.register_namespace("", CT)
    parts["[Content_Types].xml"] = xml(content_types)
    if "docProps/app.xml" in parts:
        app = ET.fromstring(parts["docProps/app.xml"])
        for element in app.iter():
            if element.tag.endswith("}Slides"):
                element.text = "18"
        parts["docProps/app.xml"] = xml(app)
    candidate.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(candidate, "w", compression=ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)

    # Export the actual embedded notes in the presentation's visible order.
    order = list(range(1, 15)) + [18, 15, 16, 17]
    lines = ["# G17 final presentation: speaker notes", "",
             "Pages 1–15 are the main presentation. Pages 16–18 are optional Q&A backups.", ""]
    for page, physical in enumerate(order, 1):
        slide = ET.fromstring(parts[f"ppt/slides/slide{physical}.xml"])
        title = slide.find(".//a:t", NS).text
        lines.extend([f"## Slide {page}: {title}", "", read_notes(parts[note_part(physical)]), ""])
    (ROOT / "slides/G17_final_speaker_notes.md").write_text(
        "\n".join(line.rstrip() for line in lines), encoding="utf-8", newline="\n")
    print(json.dumps({"pages": len(order), "main_pages": 15, "backup_pages": 3}))


if __name__ == "__main__":
    main()
