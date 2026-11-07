#!/usr/bin/env python3
"""Render the citation keys used in markdown files into a reference list.

Usage:
  python3 report/tools/render_refs.py report/draft.md [more.md ...] \
      --bib docs/research/references.bib --out report/references.md [--check]

Only entries present in the bib are rendered. Missing fields are never invented
(a missing year renders as "n.d."). Bracketed key-like tokens that are not in
the bib are errors (exit 1). With --check, nothing is written; exit 1 if the
output file differs from what would be generated.
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

KEYLIKE = re.compile(r"^[A-Za-z][A-Za-z0-9_:-]*\d{4}[A-Za-z0-9_:-]*$")
BRACKET = re.compile(r"\[([^\[\]\n]+)\](?!\()")
BACKTICK = re.compile(r"`([^`\n]+)`")

ACCENTS = {"`": "\u0300", "'": "\u0301", "^": "\u0302", "~": "\u0303",
           '"': "\u0308", "=": "\u0304", ".": "\u0307", "u": "\u0306",
           "v": "\u030c", "c": "\u0327", "H": "\u030b"}
SPECIAL = {"ss": "ß", "o": "ø", "O": "Ø", "ae": "æ", "AE": "Æ", "l": "ł",
           "L": "Ł", "i": "ı", "aa": "å", "AA": "Å", "oe": "œ", "OE": "Œ"}


# ---------------------------------------------------------------- bib parsing
def _match_brace(s, i):
    """s[i] == '{'; return index of the matching '}'."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return j
    raise ValueError("unbalanced braces in bib")


def parse_bib(text):
    entries = {}
    for m in re.finditer(r"^@(\w+)\s*\{\s*([^,\s]+)\s*,", text, re.M):
        etype, key = m.group(1).lower(), m.group(2)
        brace = text.index("{", m.start())
        end = _match_brace(text, brace)
        body = text[m.end():end]
        entries[key] = {"_type": etype, **parse_fields(body)}
    return entries


def parse_fields(body):
    fields, i, n = {}, 0, len(body)
    while i < n:
        m = re.compile(r"\s*,?\s*([A-Za-z_]+)\s*=\s*").match(body, i)
        if not m:
            break
        name, i = m.group(1).lower(), m.end()
        if i < n and body[i] == "{":
            j = _match_brace(body, i)
            val, i = body[i + 1:j], j + 1
        elif i < n and body[i] == '"':
            j = body.index('"', i + 1)
            val, i = body[i + 1:j], j + 1
        else:
            m2 = re.compile(r"[^,\s]+").match(body, i)
            val, i = m2.group(0), m2.end()
        fields[name] = val
    return fields


# ------------------------------------------------------------------- cleaning
def clean(s):
    """LaTeX-ish bib text -> plain text. {{...}} / {X} protection is dropped."""
    def accent(m):
        base = m.group(2) if m.group(2) else ""
        return unicodedata.normalize("NFC", base + ACCENTS[m.group(1)])
    # {\"u}, \"u, {\'e}, \c{c}, \v{s}
    s = re.sub(r"\\([`'^~\"=.])\s*\{?\\?([A-Za-z]?)\}?", accent, s)
    s = re.sub(r"\\([uvcH])\s*\{([A-Za-z])\}", accent, s)
    s = re.sub(r"\\(ss|oe|OE|ae|AE|aa|AA|[oOlLi])(?![A-Za-z])\s*", lambda m: SPECIAL[m.group(1)], s)
    s = s.replace("``", "\u201c").replace("''", "\u201d")
    s = s.replace("---", "\u2014").replace("--", "\u2013")
    s = re.sub(r"\\([#%&_$])", r"\1", s)
    s = s.replace("~", "\u00a0") if False else s
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def split_authors(raw):
    parts, depth, cur, i = [], 0, "", 0
    while i < len(raw):
        c = raw[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if depth == 0 and re.match(r"\s+and\s+", raw[i:]):
            parts.append(cur)
            cur = ""
            i += re.match(r"\s+and\s+", raw[i:]).end()
            continue
        cur += c
        i += 1
    if cur.strip():
        parts.append(cur)
    return [p.strip() for p in parts]


def initials(first):
    out = []
    for tok in first.split():
        sub = tok.split("-")
        out.append("-".join(t[0] + "." for t in sub if t))
    return " ".join(out)


def format_author(a):
    """Return (display, sortkey)."""
    a = a.strip()
    if a.startswith("{") and _match_brace(a, 0) == len(a) - 1:
        name = clean(a)  # corporate author, as-is
        return name, name
    if "," in a:
        last, first = [x.strip() for x in a.split(",", 1)]
    else:
        toks = a.split()
        last, first = toks[-1], " ".join(toks[:-1])
    last_c, first_c = clean(last), clean(first)
    disp = f"{last_c}, {initials(first_c)}" if first_c else last_c
    return disp, last_c


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))


def fmt_authors(names):
    if len(names) <= 6:
        if len(names) <= 2:
            return " & ".join(names)
        return ", ".join(names[:-1]) + ", & " + names[-1]
    return ", ".join(names[:6]) + ", et al."


# ------------------------------------------------------------------ rendering
def render_entry(key, e, missing):
    for f in ("author", "year", "title"):
        if not e.get(f):
            missing.setdefault(key, []).append(f)
    raw = split_authors(e["author"]) if e.get("author") else []
    etal = bool(raw) and raw[-1].strip().lower() == "others"  # BibTeX "and others"
    authors = [format_author(a) for a in raw if a.strip().lower() != "others"]
    year = clean(e["year"]) if e.get("year") else "n.d."
    title = clean(e["title"]) if e.get("title") else ""
    names = fmt_authors([d for d, _ in authors]) if authors else ""
    if etal and not names.endswith("et al."):
        names = (", ".join(d for d, _ in authors[:6]) + ", et al.") if len(authors) > 1 else names + " et al."
    pieces = []
    head = f"{names} ({year})." if names else f"({year})."
    pieces.append(head)
    if title:
        pieces.append(title if title.endswith(("?", "!", ".")) else title + ".")
    src = []
    if e.get("eprint"):
        src.append(f"arXiv:{clean(e['eprint'])}")
    for f in ("booktitle", "journal", "howpublished", "institution", "publisher"):
        if e.get(f):
            src.append(clean(e[f]))
    if e.get("pages"):
        src.append("pp. " + clean(e["pages"]))
    if src:
        pieces.append(" / ".join(src) + ".")
    if e.get("url"):
        pieces.append(clean(e["url"]).replace(" ", ""))
    sortkey = (strip_accents(authors[0][1]).casefold() if authors else "\uffff", year, key)
    return sortkey, f"- <a id=\"{key}\"></a>**[{key}]** " + " ".join(pieces)


# ------------------------------------------------------------ key collection
def collect_keys(text, bib_keys, source):
    found, unknown = set(), {}
    def consider(tok):
        if tok in bib_keys:
            found.add(tok)
        elif KEYLIKE.match(tok):
            unknown.setdefault(tok, set()).add(source)
    for m in BRACKET.finditer(text):
        items = [x.strip().strip("`") for x in m.group(1).split(",")]
        if items and all(KEYLIKE.match(x) or x in bib_keys for x in items):
            for x in items:
                consider(x)
        elif m.group(1).startswith("TODO") or "Keys used" in m.group(1):
            pass  # handled by the Keys used scan below
    for line in text.splitlines():
        if "Keys used:" in line:
            tail = line.split("Keys used:", 1)[1]
            for tok in re.findall(r"[A-Za-z][A-Za-z0-9_:-]*", tail):
                if tok in bib_keys or KEYLIKE.match(tok):
                    consider(tok)
    return found, unknown


def build(paths, bib_path, out_arg_str):
    bib = parse_bib(Path(bib_path).read_text(encoding="utf-8"))
    keys, unknown = set(), {}
    for p in paths:
        f, u = collect_keys(Path(p).read_text(encoding="utf-8"), set(bib), p)
        keys |= f
        for k, v in u.items():
            unknown.setdefault(k, set()).update(v)
    missing = {}
    rows = sorted(render_entry(k, bib[k], missing) for k in keys)
    header = (
        "<!-- GENERATED FILE: do not edit by hand. Rendered only from docs/research/references.bib.\n"
        f"     Regenerate: {out_arg_str}\n"
        "     Check freshness: add --check -->\n\n"
        "# References\n\n"
    )
    body = "\n".join(r for _, r in rows) + "\n"
    return header + body, len(rows), unknown, missing


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("markdown", nargs="+")
    ap.add_argument("--bib", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    cmd = ("python3 report/tools/render_refs.py " + " ".join(a.markdown)
           + f" --bib {a.bib} --out {a.out}")
    text, n, unknown, missing = build(a.markdown, a.bib, cmd)
    rc = 0
    for k, srcs in sorted(unknown.items()):
        print(f"ERROR: key not in bib: {k} (in {', '.join(sorted(srcs))})", file=sys.stderr)
        rc = 1
    for k, fs in sorted(missing.items()):
        print(f"WARNING: bib entry {k} missing: {', '.join(fs)}", file=sys.stderr)
    if rc:
        return rc
    out = Path(a.out)
    if a.check:
        if not out.exists() or out.read_text(encoding="utf-8") != text:
            print(f"STALE: {a.out} does not match rendered output", file=sys.stderr)
            return 1
        print(f"OK: {a.out} is up to date ({n} keys)")
        return 0
    out.write_text(text, encoding="utf-8")
    print(f"wrote {a.out}: {n} keys")
    return 0


if __name__ == "__main__":
    sys.exit(main())
