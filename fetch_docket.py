#!/usr/bin/env python3
"""
fetch_docket.py — Case Discovery & Tracking

Discovers all current-term SCOTUS cases via the Oyez API,
creates case directories with case_info.txt files, and maintains
a docket_status.json tracking file.

Usage:
    python3 fetch_docket.py              # fetch OT2025 cases (default)
    python3 fetch_docket.py --term 2024  # fetch a specific term
"""

import json
import os
import re
import sys
import textwrap
import time
from pathlib import Path

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
CASES_DIR = os.path.join(DATA_DIR, "cases")
STATUS_FILE = os.path.join(DATA_DIR, "docket_status.json")

OYEZ_BASE = "https://api.oyez.org"
REQUEST_DELAY = 1.0  # seconds between Oyez API requests


def load_status():
    """Load or initialize the docket status tracking file."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {"term": None, "cases": {}}


def save_status(status):
    """Save the docket status tracking file."""
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def fetch_term_cases(term):
    """Fetch all cases for a given SCOTUS term from Oyez API."""
    url = f"{OYEZ_BASE}/cases?per_page=0&filter=term:{term}"
    print(f"Fetching OT{term} cases from Oyez API...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    cases = resp.json()
    print(f"  Found {len(cases)} cases")
    return cases


def fetch_case_detail(case_href):
    """Fetch detailed case info from Oyez API."""
    time.sleep(REQUEST_DELAY)
    resp = requests.get(case_href, timeout=30)
    resp.raise_for_status()
    return resp.json()


def extract_docket_number(case_data):
    """Extract the primary docket number from Oyez case data."""
    docket = case_data.get("docket_number", "")
    if not docket:
        return None
    docket = docket.strip()
    docket = re.sub(r"^No\.\s*", "", docket)
    # Take only the first docket number if consolidated
    docket = docket.split(",")[0].strip()
    return docket


def extract_question_presented(case_data):
    """Extract the question presented from Oyez case data."""
    question = case_data.get("question", "")
    if isinstance(question, dict):
        question = question.get("text", "")
    if not question:
        return "Not available from Oyez."
    # Clean HTML tags
    question = re.sub(r"<[^>]+>", "", question)
    question = question.strip()
    return question


def extract_timeline(case_data):
    """Extract timeline events from Oyez case data."""
    timeline = {}
    events = case_data.get("timeline", [])
    if isinstance(events, list):
        for event in events:
            event_type = event.get("event", "")
            dates = event.get("dates", [])
            if dates:
                ts = dates[0] if isinstance(dates[0], (int, float)) else None
                if ts:
                    from datetime import datetime
                    date_str = datetime.fromtimestamp(ts).strftime("%B %d, %Y")
                    if "grant" in event_type.lower():
                        timeline["granted"] = date_str
                    elif "argue" in event_type.lower():
                        timeline["argued"] = date_str
                    elif "decid" in event_type.lower():
                        timeline["decided"] = date_str
    return timeline


def extract_facts(case_data):
    """Extract the facts/background from Oyez case data."""
    facts = case_data.get("facts_of_the_case", "")
    if isinstance(facts, dict):
        facts = facts.get("text", "")
    if not facts:
        return ""
    # Clean HTML tags
    facts = re.sub(r"<[^>]+>", "", facts)
    facts = facts.strip()
    return facts


def generate_case_info(case_data, detail_data):
    """Generate a case_info.txt matching the format used by pipeline scripts."""
    name = case_data.get("name", "Unknown Case")
    name = name.replace("&amp;", "&").replace("&#039;", "'")

    docket = extract_docket_number(case_data)
    question = extract_question_presented(detail_data)
    facts = extract_facts(detail_data)
    timeline = extract_timeline(detail_data)

    lines = []
    lines.append(f"{name} (No. {docket})")
    lines.append("")

    lines.append("QUESTIONS PRESENTED:")
    wrapped = textwrap.fill(question, width=76, initial_indent="", subsequent_indent="   ")
    lines.append(wrapped)
    lines.append("")

    if facts:
        lines.append("BACKGROUND:")
        wrapped = textwrap.fill(facts, width=76)
        lines.append(wrapped)
        lines.append("")

    if timeline.get("argued"):
        lines.append(f"Argued: {timeline['argued']}")
    elif timeline.get("granted"):
        lines.append(f"Certiorari granted: {timeline['granted']}")
        lines.append("Argued: Not yet argued")
    if timeline.get("decided"):
        lines.append(f"Decided: {timeline['decided']}")
    else:
        lines.append("Decision expected: Pending")
    lines.append("")

    # Key legal issues placeholder — the pipeline's issue_analysis.py
    # generates these from the actual briefs
    lines.append("KEY LEGAL ISSUES:")
    lines.append("- To be determined by issue analysis pipeline step")

    return "\n".join(lines)


def process_case(case_data, status, force=False):
    """Process a single case: create directory, write case_info.txt, update status."""
    docket = extract_docket_number(case_data)
    if not docket:
        print(f"  Skipping case with no docket number: {case_data.get('name', '?')}")
        return False

    name = case_data.get("name", "Unknown")
    name = name.replace("&amp;", "&").replace("&#039;", "'")

    # Check if already tracked — just update timeline on re-run
    if docket in status["cases"] and not force:
        existing = status["cases"][docket]
        if case_data.get("href"):
            try:
                detail = fetch_case_detail(case_data["href"])
                timeline = extract_timeline(detail)
                existing["timeline"] = timeline
                existing["name"] = name
                if timeline.get("decided"):
                    existing["decided"] = True
            except Exception as e:
                print(f"  Warning: Could not update {docket}: {e}")
        return False

    # Create case directory with briefs/ and transcript/ subdirs
    safe_docket = docket.replace("/", "-")
    case_dir = os.path.join(CASES_DIR, safe_docket)
    os.makedirs(case_dir, exist_ok=True)
    os.makedirs(os.path.join(case_dir, "briefs"), exist_ok=True)
    os.makedirs(os.path.join(case_dir, "transcript"), exist_ok=True)

    # Fetch detailed case info from Oyez
    detail_data = {}
    if case_data.get("href"):
        try:
            detail_data = fetch_case_detail(case_data["href"])
        except Exception as e:
            print(f"  Warning: Could not fetch detail for {docket}: {e}")

    # Generate and write case_info.txt
    case_info = generate_case_info(case_data, detail_data)
    info_path = os.path.join(case_dir, "case_info.txt")
    with open(info_path, "w") as f:
        f.write(case_info)

    timeline = extract_timeline(detail_data)
    argued = bool(timeline.get("argued"))
    decided = bool(timeline.get("decided"))

    # Update status tracking
    status["cases"][docket] = {
        "name": name,
        "docket": docket,
        "directory": safe_docket,
        "state": "discovered",
        "timeline": timeline,
        "argued": argued,
        "decided": decided,
        "briefs_downloaded": False,
        "transcript_downloaded": False,
        "pipeline_ready": False,
        "pipeline_complete": False,
    }

    print(f"  + {docket}: {name}")
    if argued:
        print(f"    Argued: {timeline.get('argued')}")
    if decided:
        print(f"    Decided: {timeline.get('decided')}")

    return True


def main():
    term = "2025"
    force = False
    for arg in sys.argv[1:]:
        if arg == "--force":
            force = True
        elif arg == "--term":
            idx = sys.argv.index("--term")
            if idx + 1 < len(sys.argv):
                term = sys.argv[idx + 1]
        elif arg.isdigit() and len(arg) == 4:
            term = arg

    status = load_status()
    status["term"] = f"OT{term}"

    try:
        cases = fetch_term_cases(term)
    except requests.RequestException as e:
        print(f"Error fetching cases from Oyez API: {e}")
        sys.exit(1)

    if not cases:
        print("No cases found for the specified term.")
        sys.exit(0)

    new_count = 0
    total = len(cases)
    print(f"\nProcessing {total} cases...")

    for i, case in enumerate(cases):
        was_new = process_case(case, status, force=force)
        if was_new:
            new_count += 1

    save_status(status)

    # Summary
    total_tracked = len(status["cases"])
    argued_count = sum(1 for c in status["cases"].values() if c.get("argued"))
    decided_count = sum(1 for c in status["cases"].values() if c.get("decided"))
    ready_count = sum(1 for c in status["cases"].values() if c.get("pipeline_ready"))
    complete_count = sum(1 for c in status["cases"].values() if c.get("pipeline_complete"))

    print(f"\n{'='*60}")
    print(f"DOCKET SUMMARY — {status['term']}")
    print(f"{'='*60}")
    print(f"  Total cases tracked:    {total_tracked}")
    print(f"  New cases added:        {new_count}")
    print(f"  Cases argued:           {argued_count}")
    print(f"  Cases decided:          {decided_count}")
    print(f"  Pipeline ready:         {ready_count}")
    print(f"  Pipeline complete:      {complete_count}")
    print(f"\nStatus saved to: {STATUS_FILE}")
    print(f"Case directories in: {CASES_DIR}/")


if __name__ == "__main__":
    main()
