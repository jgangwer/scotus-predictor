"""
export_to_website.py

Converts pipeline output (scenario_output.txt, vote_predictions_combined.txt,
case_info.txt) into structured JSON for the Next.js website.

Uses Claude API to parse the free-form markdown pipeline output into the
exact JSON schema the website expects. Also updates the index.json manifest.

Usage:
    python3 export_to_website.py data/tariff-case

Outputs:
    scotus-website/src/data/cases/<case-id>.json
    scotus-website/src/data/cases/index.json (updated)
"""

import anthropic
import json
import sys
import os
import re
from datetime import date
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"), override=True)

MODEL = "claude-sonnet-4-5-20250929"
MAX_RETRIES = 3
WEBSITE_DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "scotus-website", "src", "data", "cases"
)


def read_file(path):
    with open(path, "r") as f:
        return f.read()


def slugify(name):
    """Convert case name to URL-friendly slug."""
    # Remove "Inc.", "Corp.", etc. for cleaner slugs
    s = name.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    s = re.sub(r'-+', '-', s)
    s = s.strip('-')
    return s


def parse_case_info(text):
    """Extract structured info from case_info.txt."""
    info = {
        "name": "",
        "docket": "",
        "questions": "",
        "background": "",
        "argued": "",
        "decision_expected": "",
        "key_issues": "",
    }

    lines = text.strip().split("\n")

    # First line is usually the case name with docket
    if lines:
        first_line = lines[0].strip()
        # Extract docket number(s) from parenthetical
        docket_match = re.search(r'\((.*?)\)', first_line)
        if docket_match:
            info["docket"] = docket_match.group(1)
            info["name"] = first_line[:first_line.index("(")].strip()
        else:
            info["name"] = first_line

    # Check for consolidated case on second line
    if len(lines) > 1 and "Consolidated with" in lines[1]:
        consolidated = lines[1].strip()
        docket_match = re.search(r'\((.*?)\)', consolidated)
        if docket_match:
            # Combine docket numbers
            info["docket"] = f"Nos. {info['docket'].replace('No. ', '')} & {docket_match.group(1).replace('No. ', '')}"

    # Parse sections
    current_section = None
    section_lines = []

    for line in lines[2:]:
        stripped = line.strip()
        if stripped.startswith("QUESTIONS PRESENTED"):
            if current_section:
                info[current_section] = "\n".join(section_lines).strip()
            current_section = "questions"
            section_lines = []
        elif stripped.startswith("BACKGROUND"):
            if current_section:
                info[current_section] = "\n".join(section_lines).strip()
            current_section = "background"
            section_lines = []
        elif stripped.startswith("KEY LEGAL ISSUES"):
            if current_section:
                info[current_section] = "\n".join(section_lines).strip()
            current_section = "key_issues"
            section_lines = []
        elif stripped.startswith("Argued:"):
            info["argued"] = stripped.replace("Argued:", "").strip()
        elif stripped.startswith("Decision expected:"):
            info["decision_expected"] = stripped.replace("Decision expected:", "").strip()
        elif current_section:
            section_lines.append(line)

    if current_section:
        info[current_section] = "\n".join(section_lines).strip()

    return info


def build_extraction_prompt(case_info_text, scenario_text, votes_text):
    """Build the prompt that asks Claude to produce structured JSON."""

    return f"""You are a data extraction assistant. Convert the following Supreme Court prediction pipeline outputs into a single JSON object matching the exact schema below.

IMPORTANT RULES:
1. Output ONLY valid JSON — no markdown, no commentary, no code fences
2. Use unicode characters for special typography: \\u2013 for en-dash, \\u201c/\\u201d for smart quotes, \\u00a7 for section symbol
3. Probabilities must be integers summing to 100. If the scenario output only contains 2 scenarios that don't sum to 100, you MUST create a third scenario from the vote predictions (e.g. "Government Prevails" or the minority position) with the remaining probability. Every case must have at least 3 scenarios.
4. Every justice must appear in justiceVotes (all 9: Roberts, Thomas, Alito, Sotomayor, Kagan, Gorsuch, Kavanaugh, Barrett, Jackson)
5. Scenario majorityJustices and dissentJustices must use last names only
6. The "prediction" field for justiceVotes should be a short directional phrase (e.g. "Against tariffs", "For petitioner", "Reverse")
7. "confidence" must be one of: "Very High", "High", "Moderate-High", "Moderate", "Low"
8. Keep all text summaries concise — 1-3 sentences max per field
9. For "reasoning" in justiceVotes, capture the most distinctive signal for that justice
10. "tags" should be 3-5 lowercase hyphenated topic keywords
11. Generate a URL-friendly "id" from the case name (lowercase, hyphenated)
12. The "summary" field is a one-line description for search engines and card displays
13. Extract "lowerCourt" from the background section
14. Set "status" to "Awaiting Decision" if no decision date is mentioned
15. Set "decisionDate" to null if not yet decided
16. Set "lastUpdated" to today's date: {date.today().isoformat()}

JSON SCHEMA:
{{
  "id": "case-name-slug",
  "name": "Full Case Name v. Other Party",
  "docket": "Nos. XX-XXXX & XX-XXX" or "No. XX-XXXX",
  "term": "October Term YYYY",
  "argued": "Month Day, Year",
  "decisionDate": null,
  "status": "Awaiting Decision",
  "questionPresented": "Whether...",
  "summary": "One-line description for SEO and card display",
  "lowerCourt": "Court name (disposition)",
  "lastUpdated": "YYYY-MM-DD",
  "tags": ["tag1", "tag2"],
  "scenarios": [
    {{
      "id": 1,
      "title": "Full Scenario Title",
      "shortLabel": "Short 2-3 Word Label",
      "probability": 55,
      "voteSplit": "6\\u20133",
      "holding": "One paragraph holding summary",
      "author": "LastName",
      "majorityJustices": ["LastName1", "LastName2"],
      "dissentJustices": ["LastName1", "LastName2"],
      "primaryReasoning": [
        {{
          "label": "Framework Name",
          "summary": "1-2 sentence explanation"
        }}
      ],
      "concurrences": [
        {{
          "author": "LastName",
          "joinedBy": ["LastName"] or [],
          "summary": "2-3 sentence explanation"
        }}
      ],
      "dissent": {{
        "author": "LastName",
        "joinedBy": ["LastName1", "LastName2"],
        "coreArguments": [
          "Argument 1 as a sentence",
          "Argument 2 as a sentence"
        ]
      }},
      "newRule": "Paragraph describing new legal framework going forward"
    }}
  ],
  "justiceVotes": [
    {{
      "name": "LastName",
      "prediction": "Directional phrase",
      "confidence": "High",
      "reasoning": "1-2 sentence distinctive reasoning for this justice"
    }}
  ]
}}

--- CASE INFO ---
{case_info_text}

--- SCENARIO OUTPUT ---
{scenario_text}

--- VOTE PREDICTIONS ---
{votes_text}

Now output the JSON object:"""


def extract_json_with_claude(case_info_text, scenario_text, votes_text):
    """Call Claude to convert pipeline text to structured JSON."""
    client = anthropic.Anthropic()

    prompt = build_extraction_prompt(case_info_text, scenario_text, votes_text)

    print(f"  Sending to Claude ({MODEL})...")
    print(f"  Input size: {len(prompt):,} characters")

    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=8192,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.content[0].text.strip()

            # Strip any markdown code fences if present
            if text.startswith("```"):
                text = re.sub(r'^```(?:json)?\n?', '', text)
                text = re.sub(r'\n?```$', '', text)

            # Parse and validate JSON
            data = json.loads(text)

            # Basic validation
            assert "id" in data, "Missing 'id' field"
            assert "scenarios" in data, "Missing 'scenarios' field"
            assert "justiceVotes" in data, "Missing 'justiceVotes' field"
            assert len(data["justiceVotes"]) == 9, f"Expected 9 justices, got {len(data['justiceVotes'])}"

            # Validate probabilities sum to ~100
            total_prob = sum(s["probability"] for s in data["scenarios"])
            assert 98 <= total_prob <= 102, f"Probabilities sum to {total_prob}, expected ~100"

            print(f"  Successfully extracted {len(data['scenarios'])} scenarios, {len(data['justiceVotes'])} justice votes")
            return data

        except json.JSONDecodeError as e:
            print(f"  Attempt {attempt + 1}: JSON parse error: {e}")
            if attempt < MAX_RETRIES - 1:
                print("  Retrying...")
        except AssertionError as e:
            print(f"  Attempt {attempt + 1}: Validation error: {e}")
            if attempt < MAX_RETRIES - 1:
                print("  Retrying...")
        except Exception as e:
            print(f"  Attempt {attempt + 1}: API error: {e}")
            if attempt < MAX_RETRIES - 1:
                import time
                time.sleep(5)
                print("  Retrying...")

    print("  ERROR: Failed after all retries")
    sys.exit(1)


def update_index(case_data):
    """Update the index.json manifest with the new/updated case."""
    index_path = os.path.join(WEBSITE_DATA_DIR, "index.json")

    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            index = json.load(f)
    else:
        index = {
            "term": "October Term 2025",
            "lastUpdated": date.today().isoformat(),
            "cases": [],
        }

    # Update the lastUpdated date
    index["lastUpdated"] = date.today().isoformat()

    # Build case summary entry
    top_scenario = max(case_data["scenarios"], key=lambda s: s["probability"])
    case_entry = {
        "id": case_data["id"],
        "name": case_data["name"],
        "docket": case_data["docket"],
        "status": case_data["status"],
        "summary": case_data["summary"],
        "topPrediction": {
            "probability": top_scenario["probability"],
            "outcome": top_scenario["shortLabel"],
            "voteSplit": top_scenario["voteSplit"],
        },
        "tags": case_data["tags"],
    }

    # Update existing entry or append new one
    existing_idx = next(
        (i for i, c in enumerate(index["cases"]) if c["id"] == case_data["id"]),
        None,
    )
    if existing_idx is not None:
        index["cases"][existing_idx] = case_entry
        print(f"  Updated existing entry in index.json")
    else:
        index["cases"].append(case_entry)
        print(f"  Added new entry to index.json")

    # Update homepage subtitle count
    index["caseCount"] = len(index["cases"])

    with open(index_path, "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return index


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 export_to_website.py <case_folder>")
        print("Example: python3 export_to_website.py data/tariff-case")
        sys.exit(1)

    case_dir = sys.argv[1].rstrip("/")

    if not os.path.isdir(case_dir):
        print(f"ERROR: {case_dir} is not a directory")
        sys.exit(1)

    # Check required files
    required_files = {
        "case_info.txt": "case info",
        "scenario_output.txt": "scenario construction output",
        "vote_predictions_combined.txt": "vote predictions",
    }

    for filename, description in required_files.items():
        path = os.path.join(case_dir, filename)
        if not os.path.exists(path):
            print(f"ERROR: Missing {filename} ({description}) in {case_dir}")
            print(f"Run the pipeline steps first.")
            sys.exit(1)

    print(f"Exporting case from {case_dir}")
    print(f"Website data dir: {WEBSITE_DATA_DIR}")
    print()

    # Read pipeline outputs
    case_info_text = read_file(os.path.join(case_dir, "case_info.txt"))
    scenario_text = read_file(os.path.join(case_dir, "scenario_output.txt"))
    votes_text = read_file(os.path.join(case_dir, "vote_predictions_combined.txt"))

    print(f"Input files:")
    print(f"  case_info.txt:                  {len(case_info_text):>8,} chars")
    print(f"  scenario_output.txt:            {len(scenario_text):>8,} chars")
    print(f"  vote_predictions_combined.txt:  {len(votes_text):>8,} chars")
    print()

    # Extract structured JSON via Claude
    print("Step 1: Extracting structured data...")
    case_data = extract_json_with_claude(case_info_text, scenario_text, votes_text)
    print()

    # Write case JSON
    os.makedirs(WEBSITE_DATA_DIR, exist_ok=True)
    case_path = os.path.join(WEBSITE_DATA_DIR, f"{case_data['id']}.json")
    with open(case_path, "w") as f:
        json.dump(case_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Step 2: Wrote {case_path}")
    print(f"  ({os.path.getsize(case_path):,} bytes)")
    print()

    # Update index
    print("Step 3: Updating index.json...")
    index = update_index(case_data)
    print(f"  Total cases in index: {len(index['cases'])}")
    print()

    # Summary
    print("=" * 60)
    print("EXPORT COMPLETE")
    print("=" * 60)
    print(f"  Case:       {case_data['name']}")
    print(f"  ID:         {case_data['id']}")
    print(f"  Scenarios:  {len(case_data['scenarios'])}")
    print(f"  Status:     {case_data['status']}")
    print(f"  File:       {case_path}")
    print()
    print("Next steps:")
    print(f"  cd scotus-website && npm run build")
    print(f"  cd scotus-website && npm run dev")
    print(f"  Visit: http://localhost:3000/cases/{case_data['id']}")


if __name__ == "__main__":
    main()
