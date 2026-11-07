#!/usr/bin/env python3
"""Export the canonical Mermaid fences in architecture.md; never reads run data.

Install @mermaid-js/mermaid-cli@11.12.0 in a separate temporary/tool environment.
Example: python3 docs/guide/tools/render_diagrams.py --mmdc /path/to/mmdc
"""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import tempfile


GUIDE = pathlib.Path(__file__).resolve().parents[1]
NAMES = ("01-study-dataflow", "02-v2-topologies", "03-provenance-boundary", "04-sae-proposal")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mmdc", default="mmdc", help="Mermaid CLI executable")
    parser.add_argument("--browser", help="Optional Chromium executable path")
    parser.add_argument("--out-dir", type=pathlib.Path, default=GUIDE / "diagrams")
    parser.add_argument("--format", choices=("svg", "png"), default="svg")
    args = parser.parse_args()
    source = (GUIDE / "architecture.md").read_text()
    diagrams = re.findall(r"```mermaid\s*\n(.*?)\n```", source, re.S)
    if len(diagrams) != len(NAMES):
        parser.error(f"Expected {len(NAMES)} named diagrams, found {len(diagrams)}")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="swarm-mermaid-") as temporary:
        root = pathlib.Path(temporary)
        config = root / "mermaid.json"
        config.write_text(json.dumps({
            "theme": "base", "securityLevel": "strict", "deterministicIds": True,
            "deterministicIDSeed": "swarm-code-guide",
            "themeVariables": {"fontFamily": "Arial, sans-serif", "fontSize": "16px",
                               "primaryColor": "#EAF2FF", "primaryBorderColor": "#345A90",
                               "primaryTextColor": "#172B4D", "lineColor": "#52647C"},
            "flowchart": {"htmlLabels": False, "curve": "basis", "nodeSpacing": 35, "rankSpacing": 45}
        }))
        browser_config = root / "browser.json"
        browser_settings = {"args": ["--no-sandbox", "--disable-setuid-sandbox"]}
        if args.browser:
            browser_settings["executablePath"] = args.browser
        browser_config.write_text(json.dumps(browser_settings))
        for name, diagram in zip(NAMES, diagrams):
            path = root / (name + ".mmd")
            path.write_text(diagram + "\n")
            output = args.out_dir / (name + "." + args.format)
            subprocess.run([args.mmdc, "-i", str(path), "-o", str(output), "-c", str(config),
                            "-p", str(browser_config), "-b", "white", "-w", "1600", "-q"], check=True)
            print(output)
    if args.format == "svg":
        records = [{"name": name,
                    "source_sha256": hashlib.sha256(diagram.encode()).hexdigest(),
                    "svg_sha256": hashlib.sha256((args.out_dir / (name + ".svg")).read_bytes()).hexdigest()}
                   for name, diagram in zip(NAMES, diagrams)]
        (args.out_dir / "sources.json").write_text(json.dumps({
            "schema_version": 1, "canonical_source": "docs/guide/architecture.md",
            "scope": "Reviewed source/export integrity pins; not proof of scientific claims or rendering semantics",
            "diagrams": records}, indent=2) + "\n")


if __name__ == "__main__":
    main()
