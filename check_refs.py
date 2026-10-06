#!/usr/bin/env python3
"""
check_refs.py — human-supervised reference verification pipeline.

Modes:
  python3 check_refs.py verify manuscript.txt            -> verification_table.md
  python3 check_refs.py bibtex manuscript.txt            -> references.bib (+ stubs for non-DOI)

What it does (verify mode):
  1. Slices the References section out of the manuscript (plain text, APA).
  2. Splits it into entries (blank-line separated).
  3. Extracts the DOI from each entry, if present.
  4. Resolves each DOI against the Crossref API and compares:
       - title (normalized fuzzy match)
       - first author family name
       - year (exact, or +/-1 to tolerate online-first vs print)
       - volume and pages, when both sides have them
  5. Writes a PASS / WARN / FAIL table plus a manual checklist of
     non-DOI entries. FAIL = wrong paper or major mismatch. WARN = minor
     metadata drift worth a human look. Nothing is auto-"fixed":
     every WARN/FAIL is for you to resolve against the publisher record.

Requires: Python 3.8+, internet access. Stdlib only (urllib, difflib).
Be polite to Crossref: the script sleeps 1s between requests and sends a
mailto in the User-Agent (edit CONTACT below to your email).
"""

import json
import re
import sys
import time
import unicodedata
import urllib.request
import urllib.error
from difflib import SequenceMatcher

CONTACT = "your-email@example.edu"  # edit: Crossref politeness policy
CROSSREF = "https://api.crossref.org/works/"
DOI_RE = re.compile(r"https?://doi\.org/(10\.\S+?)(?=[\s\)\]]|$)", re.I)


# ---------------------------------------------------------------- parsing

def load_entries(path):
    text = open(path, encoding="utf-8").read()
    idx = max(text.rfind("\nReferences\n"), text.rfind("# References"))
    if idx == -1:
        sys.exit("Could not find a 'References' heading in the file.")
    block = text[idx:].split("\n", 1)[1]
    entries, cur = [], []
    for line in block.split("\n"):
        if line.strip().startswith("#"):
            break
        if not line.strip():
            if cur:
                entries.append(" ".join(s.strip() for s in cur))
                cur = []
        else:
            cur.append(line)
    if cur:
        entries.append(" ".join(s.strip() for s in cur))
    return [e for e in entries if len(e) > 30]


def parse_entry(entry):
    m = DOI_RE.search(entry)
    doi = m.group(1).rstrip(".") if m else None
    first_author = re.match(r"([^,]+),", entry)
    year = re.search(r"\((\d{4})[a-z]?\)", entry)
    vol = re.search(r"(?:,\s|\s)(\d+)\s*\(", entry)
    pages = re.search(r"(\d+)\s*[–-]\s*(\d+)", entry.split("https://")[0])
    return {
        "raw": entry,
        "doi": doi,
        "author": first_author.group(1).strip() if first_author else "",
        "year": int(year.group(1)) if year else None,
        "volume": vol.group(1) if vol else None,
        "pages": (pages.group(1), pages.group(2)) if pages else None,
    }


# ---------------------------------------------------------------- crossref

def fetch_crossref(doi):
    req = urllib.request.Request(
        CROSSREF + urllib.parse.quote(doi),
        headers={"User-Agent": f"ref-checker/1.0 (mailto:{CONTACT})"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["message"]
    except urllib.error.HTTPError as e:
        return {"_error": f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}


def fetch_bibtex(doi):
    req = urllib.request.Request(
        "https://doi.org/" + urllib.parse.quote(doi),
        headers={
            "Accept": "application/x-bibtex",
            "User-Agent": f"ref-checker/1.0 (mailto:{CONTACT})",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8")
    except Exception as e:  # noqa: BLE001
        return f"% FAILED to fetch BibTeX for {doi}: {e}\n"


# ---------------------------------------------------------------- compare

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def title_sim(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def compare(local, remote):
    """Return (status, notes). status in PASS / WARN / FAIL."""
    if "_error" in remote:
        return "FAIL", [f"DOI did not resolve on Crossref ({remote['_error']}) — check by hand (may be DataCite/other registrar)"]
    notes = []
    r_title = (remote.get("title") or [""])[0]
    sim = title_sim(guess_local_title(local["raw"]), r_title)
    if sim < 0.55:
        return "FAIL", [f"Title mismatch (similarity {sim:.2f}): Crossref says: \"{r_title[:90]}\" — DOI likely points to a DIFFERENT paper"]
    if sim < 0.80:
        notes.append(f"Title similarity only {sim:.2f} — eyeball it")

    r_auth = ((remote.get("author") or [{}])[0].get("family") or "")
    if r_auth and norm(r_auth) not in norm(local["raw"]):
        notes.append(f"First author on record is '{r_auth}' — not found in entry")

    r_year = None
    for k in ("published-print", "published-online", "issued"):
        if remote.get(k, {}).get("date-parts"):
            r_year = remote[k]["date-parts"][0][0]
            if k == "published-print":
                break
    if local["year"] and r_year and abs(local["year"] - r_year) > 1:
        notes.append(f"Year: entry says {local['year']}, record says {r_year}")
    elif local["year"] and r_year and local["year"] != r_year:
        notes.append(f"Year off by one ({local['year']} vs {r_year}) — likely online-first vs print; confirm the citable year")

    if local["volume"] and remote.get("volume") and local["volume"] != remote["volume"]:
        notes.append(f"Volume: entry {local['volume']}, record {remote['volume']}")
    if local["pages"] and remote.get("page"):
        if local["pages"][0] not in remote["page"]:
            notes.append(f"Pages: entry {local['pages'][0]}–{local['pages'][1]}, record {remote['page']}")

    if any("DIFFERENT" in n for n in notes):
        return "FAIL", notes
    return ("WARN", notes) if notes else ("PASS", [])


def guess_local_title(entry):
    # text between the (year). and the next period-ish boundary
    m = re.search(r"\(\d{4}[a-z]?\)\.\s*(.+?)(?:\.\s|\?\s|\!\s)", entry)
    return m.group(1) if m else entry[:120]


# ---------------------------------------------------------------- modes

def mode_verify(path):
    entries = [parse_entry(e) for e in load_entries(path)]
    with_doi = [e for e in entries if e["doi"]]
    no_doi = [e for e in entries if not e["doi"]]
    rows, fails, warns = [], 0, 0
    print(f"{len(entries)} entries: {len(with_doi)} with DOI, {len(no_doi)} manual.\n")
    for i, e in enumerate(with_doi, 1):
        remote = fetch_crossref(e["doi"])
        status, notes = compare(e, remote)
        fails += status == "FAIL"
        warns += status == "WARN"
        rows.append((status, e, notes))
        print(f"[{i}/{len(with_doi)}] {status:4s}  {e['author']} ({e['year']})  {e['doi']}")
        for n in notes:
            print(f"          - {n}")
        time.sleep(1)

    with open("verification_table.md", "w", encoding="utf-8") as f:
        f.write("# Mechanical DOI verification\n\n")
        f.write(f"Result: {len(with_doi)-fails-warns} PASS · {warns} WARN · {fails} FAIL\n\n")
        f.write("| Status | Entry | Notes |\n|---|---|---|\n")
        for status, e, notes in rows:
            f.write(f"| {status} | {e['author']} ({e['year']}) `{e['doi']}` | {'; '.join(notes) or '—'} |\n")
        f.write("\n# Manual checklist (no DOI) — confirm each against the original source\n\n")
        for e in no_doi:
            f.write(f"- [ ] {e['raw'][:160]}\n")
    print("\nWrote verification_table.md")
    print("REMINDER: PASS means metadata matched; the human end-to-end check is still the final gate.")


def mode_bibtex(path):
    entries = [parse_entry(e) for e in load_entries(path)]
    with open("references.bib", "w", encoding="utf-8") as f:
        f.write("% Auto-built from publisher records via DOI content negotiation.\n")
        f.write("% Stub entries below require manual completion from the original source.\n\n")
        for e in entries:
            if e["doi"]:
                f.write(fetch_bibtex(e["doi"]).strip() + "\n\n")
                time.sleep(1)
            else:
                key = f"{norm(e['author']).replace(' ', '')}{e['year'] or 'XXXX'}"
                f.write(f"% TODO manual entry — verify against publisher:\n")
                f.write(f"% {e['raw'][:200]}\n@misc{{{key}, note = {{FILL FROM SOURCE}} }}\n\n")
    print("Wrote references.bib")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("verify", "bibtex"):
        sys.exit(__doc__)
    (mode_verify if sys.argv[1] == "verify" else mode_bibtex)(sys.argv[2])
