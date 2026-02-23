#!/usr/bin/env python3
"""
fetch_sources.py — Source Material Download

For a given case (by docket number or directory), downloads:
  A) Party briefs from supremecourt.gov docket page
  B) Amicus briefs — downloads all, AI-scores cover pages with Haiku, keeps top 5
  C) Oral argument transcript from supremecourt.gov

Usage:
    python3 fetch_sources.py 25-332              # by docket number
    python3 fetch_sources.py data/cases/25-332    # by directory path
    python3 fetch_sources.py --all                # all argued, non-ready cases
    python3 fetch_sources.py --skip-amicus 25-332 # skip amicus scoring, keep first 5
"""

import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"), override=True)

DATA_DIR = os.path.join(SCRIPT_DIR, "data")
CASES_DIR = os.path.join(DATA_DIR, "cases")
STATUS_FILE = os.path.join(DATA_DIR, "docket_status.json")

SCOTUS_BASE = "https://www.supremecourt.gov"
DOCKET_URL_TEMPLATE = f"{SCOTUS_BASE}/docket/docketfiles/html/public/{{docket}}.html"
TRANSCRIPT_INDEX_URL = f"{SCOTUS_BASE}/oral_arguments/argument_transcript/2025"

REQUEST_DELAY = 2.0  # be polite to supremecourt.gov
MAX_AMICUS_BRIEFS = 5

# ── Filing classification patterns ──────────────────────────────────────

# Party briefs we want to download
PARTY_BRIEF_PATTERNS = [
    r"brief\s+(for|of)\s+(the\s+)?petitioner",
    r"brief\s+(for|of)\s+(the\s+)?respondent",
    r"brief\s+(for|of)\s+the\s+united\s+states",
    r"brief\s+on\s+the\s+merits",
    r"reply\s+brief",
    r"reply\s+of\s+(the\s+)?petitioner",
    r"brief\s+in\s+opposition",
    r"opening\s+brief",
    r"response\s+brief",
    r"petitioners?\s*['']\s*brief",
    r"respondents?\s*['']\s*brief",
    r"merits\s+brief",
]

# Amicus briefs
AMICUS_PATTERNS = [
    r"amici?\s+curiae",
    r"amicus",
]

# Procedural stuff to skip
SKIP_PATTERNS = [
    r"^motion",
    r"^waiver",
    r"^order\b",
    r"^letter\b",
    r"^notice\b",
    r"^consent",
    r"extension\s+of\s+time",
    r"^application",
    r"^response\s+to\s+(request|application|motion)",
    r"proof\s+of\s+service",
    r"certificate\s+of\s+(compliance|word\s+count)",
    r"^joint\s+appendix",
    r"^supplemental\s+brief",
    r"blanket\s+consent",
    r"^record\b",
    r"^lodging\b",
]


# ── Utilities ────────────────────────────────────────────────────────────

def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {"term": None, "cases": {}}


def save_status(status):
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def resolve_case_dir(arg):
    """Resolve a docket number or path to (case_dir, docket)."""
    if os.path.isdir(arg):
        docket = os.path.basename(arg.rstrip("/"))
        return arg.rstrip("/"), docket
    docket = arg.strip()
    case_dir = os.path.join(CASES_DIR, docket)
    if os.path.isdir(case_dir):
        return case_dir, docket
    print(f"Error: Cannot find case directory for '{arg}'")
    print(f"  Tried: {case_dir}")
    sys.exit(1)


def download_pdf(url, output_path, label=""):
    """Download a PDF file. Returns True on success."""
    time.sleep(REQUEST_DELAY)
    try:
        resp = requests.get(url.strip(), timeout=60, allow_redirects=True)
        resp.raise_for_status()
        if len(resp.content) < 1000:
            print(f"    Warning: File seems too small ({len(resp.content)} bytes): {label}")
            return False
        with open(output_path, "wb") as f:
            f.write(resp.content)
        size_kb = len(resp.content) / 1024
        print(f"    Downloaded: {label} ({size_kb:.0f} KB)")
        return True
    except requests.RequestException as e:
        print(f"    Error downloading {label}: {e}")
        return False


def classify_filing(description):
    """Classify a docket entry as party_brief, amicus, or skip."""
    desc_lower = description.lower().strip()
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, desc_lower):
            return "skip"
    for pattern in PARTY_BRIEF_PATTERNS:
        if re.search(pattern, desc_lower):
            return "party_brief"
    for pattern in AMICUS_PATTERNS:
        if re.search(pattern, desc_lower):
            return "amicus"
    return "skip"


def clean_brief_name(description):
    """Generate a clean filename from a filing description."""
    desc_lower = description.lower().strip()
    if re.search(r"reply\s+brief|reply\s+of", desc_lower):
        return "reply_brief.pdf"
    elif re.search(r"brief\s+in\s+opposition", desc_lower):
        return "brief_in_opposition.pdf"
    elif re.search(r"petitioner|appellant", desc_lower):
        return "petitioner_brief.pdf"
    elif re.search(r"respondent|appellee", desc_lower):
        return "respondent_brief.pdf"
    elif re.search(r"united\s+states", desc_lower):
        return "us_brief.pdf"
    else:
        name = re.sub(r"[^a-z0-9]+", "_", desc_lower)[:60].strip("_")
        return f"{name}.pdf"


# ── Docket page parsing ─────────────────────────────────────────────────

def fetch_docket_page(docket):
    """Fetch and parse the SCOTUS docket page HTML."""
    url = DOCKET_URL_TEMPLATE.format(docket=docket)
    print(f"  Fetching docket page: {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def extract_filings(soup):
    """Extract all filings with descriptions and PDF links from a docket page."""
    filings = []
    cards = soup.find_all("div", class_="card")

    for card in cards:
        table = card.find("table", class_="ProceedingItem")
        if not table:
            continue

        date_td = table.find("td", class_="ProceedingDate")
        date_str = date_td.get_text(strip=True) if date_td else ""

        tds = table.find_all("td")
        if len(tds) < 2:
            continue

        desc_td = tds[1]
        doc_links_span = desc_td.find("span", class_="documentlinks")

        # Get description text (everything before the document links)
        description = ""
        for child in desc_td.children:
            if child == doc_links_span:
                break
            if hasattr(child, "get_text"):
                description += child.get_text()
            elif isinstance(child, str):
                description += child
        description = re.sub(r"\s+", " ", description).strip().rstrip(".")

        # Get PDF links
        pdf_links = []
        if doc_links_span:
            for a_tag in doc_links_span.find_all("a", class_="documentanchor"):
                href = a_tag.get("href", "").strip()
                link_text = a_tag.get_text(strip=True)
                if href:
                    if not href.startswith("http"):
                        href = f"{SCOTUS_BASE}{href}"
                    pdf_links.append({"url": href, "label": link_text})

        filings.append({
            "date": date_str,
            "description": description,
            "pdf_links": pdf_links,
        })

    return filings


# ── Step A: Party briefs ─────────────────────────────────────────────────

def download_party_briefs(filings, briefs_dir):
    """Download party briefs (petitioner, respondent, reply, etc.)."""
    print("\n  Step A: Downloading party briefs...")
    downloaded = 0
    seen_names = set()

    for filing in filings:
        if classify_filing(filing["description"]) != "party_brief":
            continue

        # Find the "Main Document" link, or fall back to first link
        main_link = None
        for link in filing["pdf_links"]:
            if link["label"] == "Main Document":
                main_link = link
                break
        if not main_link:
            if filing["pdf_links"]:
                main_link = filing["pdf_links"][0]
            else:
                print(f"    Skipping (no PDF): {filing['description'][:80]}")
                continue

        filename = clean_brief_name(filing["description"])

        # Handle duplicate names (e.g., multiple respondent briefs)
        if filename in seen_names:
            base, ext = os.path.splitext(filename)
            counter = 2
            while f"{base}_{counter}{ext}" in seen_names:
                counter += 1
            filename = f"{base}_{counter}{ext}"
        seen_names.add(filename)

        output_path = os.path.join(briefs_dir, filename)
        if os.path.exists(output_path):
            print(f"    Already exists: {filename}")
            downloaded += 1
            continue

        if download_pdf(main_link["url"], output_path, filename):
            downloaded += 1

    print(f"  Party briefs downloaded: {downloaded}")
    return downloaded


# ── Step B: Amicus briefs (AI-scored) ────────────────────────────────────

def extract_cover_pages(pdf_path, max_pages=2):
    """Extract text from the first 2 pages of a PDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for i in range(min(max_pages, len(doc))):
        page = doc.load_page(i)
        text += page.get_text() + "\n"
    doc.close()
    return text[:5000]  # cap to keep Haiku costs minimal


def score_amicus_brief(cover_text, description):
    """Score an amicus brief 1-10 using Claude Haiku."""
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("    Warning: No ANTHROPIC_API_KEY, defaulting to score 5")
        return {"score": 5, "filer": "Unknown", "party_supported": "unknown",
                "reason": "No API key for scoring"}

    client = anthropic.Anthropic()
    prompt = f"""Score this amicus brief 1-10 for analytical value to a Supreme Court case prediction.

Consider:
- Filer identity (Solicitor General = 10, state AG coalition = 8, major legal org = 7, individual professor = 4, trade association = 5)
- Whether it likely raises arguments distinct from party briefs
- Whether the filer has special expertise on the legal question

Filing description: {description}

Cover page text:
{cover_text}

Return ONLY valid JSON (no markdown, no code blocks):
{{"score": N, "filer": "name of filer", "party_supported": "petitioner|respondent|neither", "reason": "one sentence explaining score"}}"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-20250414",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        result_text = response.content[0].text.strip()
        return json.loads(result_text)
    except json.JSONDecodeError:
        match = re.search(r"\{[^}]+\}", result_text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"score": 5, "filer": "Unknown", "party_supported": "unknown",
                "reason": "Could not parse score"}
    except Exception as e:
        print(f"    Warning: Scoring failed: {e}")
        return {"score": 5, "filer": "Unknown", "party_supported": "unknown",
                "reason": str(e)}


def download_amicus_briefs(filings, briefs_dir, skip_scoring=False):
    """Download amicus briefs. If scoring enabled, download all, score, keep top 5."""
    print("\n  Step B: Processing amicus briefs...")

    amicus_filings = []
    for filing in filings:
        if classify_filing(filing["description"]) != "amicus":
            continue
        main_link = None
        for link in filing["pdf_links"]:
            if link["label"] == "Main Document":
                main_link = link
                break
        if not main_link and filing["pdf_links"]:
            main_link = filing["pdf_links"][0]
        if main_link:
            amicus_filings.append({
                "description": filing["description"],
                "url": main_link["url"],
                "date": filing["date"],
            })

    print(f"  Found {len(amicus_filings)} amicus briefs")
    if not amicus_filings:
        return 0

    # Simple mode: just take first 5 without scoring
    if skip_scoring:
        count = 0
        for i, af in enumerate(amicus_filings[:MAX_AMICUS_BRIEFS]):
            filename = f"amicus_{i+1}.pdf"
            output_path = os.path.join(briefs_dir, filename)
            if os.path.exists(output_path):
                print(f"    Already exists: {filename}")
                count += 1
                continue
            if download_pdf(af["url"], output_path, filename):
                count += 1
        return count

    # AI-scored mode: download all to temp dir, score cover pages, keep top 5
    temp_dir = tempfile.mkdtemp(prefix="amicus_")
    scored = []

    for i, af in enumerate(amicus_filings):
        temp_path = os.path.join(temp_dir, f"amicus_{i}.pdf")
        print(f"    Downloading amicus {i+1}/{len(amicus_filings)}: "
              f"{af['description'][:60]}...")
        if not download_pdf(af["url"], temp_path, f"amicus_{i+1}"):
            continue

        try:
            cover_text = extract_cover_pages(temp_path)
        except Exception as e:
            print(f"    Warning: Could not extract cover page: {e}")
            cover_text = af["description"]

        score_result = score_amicus_brief(cover_text, af["description"])
        scored.append({
            "temp_path": temp_path,
            "description": af["description"],
            "score": score_result.get("score", 0),
            "filer": score_result.get("filer", "Unknown"),
            "party_supported": score_result.get("party_supported", "unknown"),
            "reason": score_result.get("reason", ""),
        })

    # Sort by score descending, keep top 5
    scored.sort(key=lambda x: x["score"], reverse=True)
    kept = scored[:MAX_AMICUS_BRIEFS]

    print(f"\n  Amicus brief scores:")
    for i, s in enumerate(scored):
        marker = " *KEPT*" if i < MAX_AMICUS_BRIEFS else ""
        print(f"    {s['score']}/10 - {s['filer']}: {s['reason'][:60]}{marker}")

    # Move kept briefs to the briefs directory
    count = 0
    for s in kept:
        filer_clean = re.sub(r"[^a-zA-Z0-9]+", "_", s["filer"])[:30].strip("_")
        filename = f"amicus_{filer_clean}.pdf"
        output_path = os.path.join(briefs_dir, filename)
        if not os.path.exists(output_path):
            shutil.move(s["temp_path"], output_path)
            print(f"    Kept: {filename} (score: {s['score']}/10)")
        count += 1

    shutil.rmtree(temp_dir, ignore_errors=True)
    return count


# ── Step C: Oral argument transcript ─────────────────────────────────────

def download_transcript(docket, transcript_dir):
    """Download the oral argument transcript from supremecourt.gov."""
    print("\n  Step C: Downloading oral argument transcript...")

    existing = list(Path(transcript_dir).glob("*.pdf"))
    if existing:
        print(f"    Already exists: {existing[0].name}")
        return True

    try:
        time.sleep(REQUEST_DELAY)
        resp = requests.get(TRANSCRIPT_INDEX_URL, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    Error fetching transcript index: {e}")
        return False

    soup = BeautifulSoup(resp.text, "html.parser")
    transcript_url = None

    for a_tag in soup.find_all("a"):
        href = a_tag.get("href", "")
        text = a_tag.get_text(strip=True)
        if docket in text or docket.lower() in href.lower():
            if ".pdf" in href.lower():
                if href.startswith(".."):
                    transcript_url = f"{SCOTUS_BASE}/oral_arguments/{href.lstrip('../')}"
                elif href.startswith("/"):
                    transcript_url = f"{SCOTUS_BASE}{href}"
                elif href.startswith("http"):
                    transcript_url = href
                else:
                    transcript_url = (f"{SCOTUS_BASE}/oral_arguments/"
                                      f"argument_transcripts/2025/{href}")
                break

    if not transcript_url:
        print(f"    Transcript not yet available for {docket}")
        return False

    filename = f"transcript_{docket}.pdf"
    output_path = os.path.join(transcript_dir, filename)
    return download_pdf(transcript_url, output_path, filename)


# ── Main logic ───────────────────────────────────────────────────────────

def process_case(docket, case_dir, skip_amicus=False):
    """Download all source materials for one case."""
    print(f"\n{'='*60}")
    print(f"Processing: {docket}")
    print(f"Directory: {case_dir}")
    print(f"{'='*60}")

    briefs_dir = os.path.join(case_dir, "briefs")
    transcript_dir = os.path.join(case_dir, "transcript")
    os.makedirs(briefs_dir, exist_ok=True)
    os.makedirs(transcript_dir, exist_ok=True)

    try:
        soup = fetch_docket_page(docket)
    except requests.RequestException as e:
        print(f"  Error fetching docket page: {e}")
        return False

    filings = extract_filings(soup)
    print(f"  Found {len(filings)} docket entries")

    counts = {"party_brief": 0, "amicus": 0, "skip": 0}
    for f in filings:
        counts[classify_filing(f["description"])] += 1
    print(f"  Classification: {counts['party_brief']} party briefs, "
          f"{counts['amicus']} amicus, {counts['skip']} skipped")

    party_count = download_party_briefs(filings, briefs_dir)
    amicus_count = download_amicus_briefs(filings, briefs_dir,
                                           skip_scoring=skip_amicus)
    transcript_ok = download_transcript(docket, transcript_dir)

    # Update docket_status.json
    status = load_status()
    if docket in status.get("cases", {}):
        case_status = status["cases"][docket]
        case_status["briefs_downloaded"] = party_count > 0
        case_status["transcript_downloaded"] = transcript_ok
        case_status["pipeline_ready"] = (party_count > 0) and transcript_ok
        if case_status["pipeline_ready"]:
            case_status["state"] = "pipeline_ready"
        elif party_count > 0:
            case_status["state"] = "briefs_downloaded"
        save_status(status)

    print(f"\n  Summary for {docket}:")
    print(f"    Party briefs:  {party_count}")
    print(f"    Amicus briefs: {amicus_count}")
    print(f"    Transcript:    {'Yes' if transcript_ok else 'Not available'}")
    print(f"    Pipeline ready: {'Yes' if party_count > 0 and transcript_ok else 'No'}")

    return party_count > 0 and transcript_ok


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage:")
        print("  python3 fetch_sources.py 25-332              # by docket number")
        print("  python3 fetch_sources.py data/cases/25-332    # by directory path")
        print("  python3 fetch_sources.py --all                # all argued, non-ready cases")
        print("  python3 fetch_sources.py --skip-amicus 25-332 # skip amicus scoring")
        sys.exit(1)

    skip_amicus = "--skip-amicus" in args
    if skip_amicus:
        args.remove("--skip-amicus")

    if "--all" in args:
        status = load_status()
        if not status.get("cases"):
            print("No cases discovered yet. Run fetch_docket.py first.")
            sys.exit(1)

        to_process = []
        for docket, info in status["cases"].items():
            if info.get("argued") and not info.get("pipeline_ready"):
                to_process.append((docket, info.get("directory", docket)))

        if not to_process:
            print("No cases need source downloading.")
            sys.exit(0)

        print(f"Processing {len(to_process)} cases...")
        ready_count = 0
        for docket, directory in sorted(to_process):
            case_dir = os.path.join(CASES_DIR, directory)
            if process_case(docket, case_dir, skip_amicus=skip_amicus):
                ready_count += 1

        print(f"\n{'='*60}")
        print(f"DONE: {ready_count}/{len(to_process)} cases are pipeline-ready")
    else:
        case_dir, docket = resolve_case_dir(args[0])
        process_case(docket, case_dir, skip_amicus=skip_amicus)


if __name__ == "__main__":
    main()
