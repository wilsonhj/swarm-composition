#!/usr/bin/env python3
"""Check maintained guide links, citation keys and reviewed diagram-export pins.

No network or model service. These integrity checks do not fact-check prose or
prove that a figure represents the intended computation.
"""
import hashlib
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[3]
GUIDE = ROOT / "docs/guide"


def check_diagrams(guide):
    errors = []
    source = (guide / "architecture.md").read_text()
    diagrams = re.findall(r"```mermaid\s*\n(.*?)\n```", source, re.S)
    records = json.loads((guide / "diagrams/sources.json").read_text())["diagrams"]
    if len(diagrams) != len(records):
        return ["Diagram count differs from reviewed exports"]
    for diagram, record in zip(diagrams, records):
        name = record["name"]
        if hashlib.sha256(diagram.encode()).hexdigest() != record["source_sha256"]:
            errors.append(f"Stale diagram export: {name}; review source and rerender")
        svg = (guide / "diagrams" / (name + ".svg")).read_bytes()
        if hashlib.sha256(svg).hexdigest() != record["svg_sha256"]:
            errors.append(f"Changed diagram export: {name}; review and rerender")
        tags = {node.tag.rsplit("}", 1)[-1] for node in ET.fromstring(svg).iter()}
        if not {"title", "desc"}.issubset(tags):
            errors.append(f"Missing accessible title or description: {name}")
        if "script" in tags:
            errors.append(f"Unexpected script in SVG export: {name}")
    return errors


def check_document(path, keys):
    errors, source = [], path.read_text()
    for label, target in re.findall(r"!?\[([^\]]+)\]\(([^)]+)\)", source):
        target = target.strip("<>")
        if "://" in target or target.startswith(("#", "mailto:")):
            continue
        filename, _, anchor = target.partition("#")
        resolved = path.parent / filename
        if not resolved.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing link {target}")
        elif anchor.startswith("L") and anchor[1:].isdigit():
            lines, number = resolved.read_text().splitlines(), int(anchor[1:])
            if not 1 <= number <= len(lines):
                errors.append(f"{path.name}: out-of-range code anchor {target}")
            else:
                display = label.strip("`")
                name = "" if display.endswith(".py") else display.rsplit(".", 1)[-1]
                if re.fullmatch(r"[A-Za-z_]\w*", name) and not re.search(
                        r"(?:def|class)\s+" + re.escape(name) + r"\b", lines[number - 1]):
                    errors.append(f"{path.name}: moved definition anchor {target} ({name})")
    cited = set(re.findall(r"\b[a-z]+(?:19|20)\d\d[a-z0-9]+\b", source))
    for key in sorted(cited - keys):
        errors.append(f"{path.name}: unknown citation key {key}")
    if len(re.findall(r"^```", source, re.M)) % 2:
        errors.append(f"{path.name}: unbalanced code fences")
    return errors


def main():
    bib = (ROOT / "docs/research/references.bib").read_text()
    entries = re.findall(r"^@\w+\s*\{\s*([^,\s]+),", bib, re.M)
    keys = set(entries)
    errors = [] if len(keys) == len(entries) else ["Duplicate bibliography keys"]
    documents = sorted(GUIDE.glob("*.md")) + [
        ROOT / "README.md", ROOT / "docs/research/README.md",
        ROOT / "docs/research/methods-evidence.md", ROOT / "docs/research/claim-audit.md"]
    for path in documents:
        errors.extend(check_document(path, keys))
    errors.extend(check_diagrams(GUIDE))
    for error in errors:
        print("FAIL:", error, file=sys.stderr)
    print(f"Checked {len(documents)} maintained documents, {len(keys)} unique bibliography keys and diagram exports")
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, KeyError, ValueError, ET.ParseError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
