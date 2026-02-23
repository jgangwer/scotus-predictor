"""
issue_analysis.py (revised)

Step 3: Identifies the specific doctrinal questions, frameworks, and legal
tests that will determine the outcome. Does NOT predict votes — that's
vote_prediction.py's job.

Inputs: case_info.txt, briefs (PDFs), oral argument transcript (PDF)
Output: issue_analysis_output.txt

Usage:
    python3 issue_analysis.py data/tariff-case
"""

import anthropic
import fitz  # pymupdf
import sys
import os
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"), override=True)


def read_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def read_file(path):
    with open(path, "r") as f:
        return f.read()


def find_pdfs(case_dir):
    """Find PDFs in the case folder, supporting both flat and structured layouts."""
    briefs_dir = os.path.join(case_dir, "briefs")
    transcript_dir = os.path.join(case_dir, "transcript")

    briefs = []
    transcripts = []

    if os.path.isdir(briefs_dir):
        briefs = sorted([os.path.join(briefs_dir, f) for f in os.listdir(briefs_dir) if f.lower().endswith(".pdf")])
        if os.path.isdir(transcript_dir):
            transcripts = sorted([os.path.join(transcript_dir, f) for f in os.listdir(transcript_dir) if f.lower().endswith(".pdf")])
        print(f"Structured layout: {len(briefs)} briefs, {len(transcripts)} transcripts")
    else:
        briefs = sorted([os.path.join(case_dir, f) for f in os.listdir(case_dir) if f.lower().endswith(".pdf")])
        print(f"Flat layout: {len(briefs)} PDFs (all treated as briefs)")

    return briefs, transcripts


# --- Get case folder from command line ---
if len(sys.argv) < 2:
    print("Usage: python3 issue_analysis.py <case_folder>")
    print("Example: python3 issue_analysis.py data/tariff-case")
    sys.exit(1)

case_dir = sys.argv[1].rstrip("/")

if not os.path.isdir(case_dir):
    print(f"ERROR: {case_dir} is not a directory")
    sys.exit(1)

# --- Read case_info.txt (required) ---
case_info_path = os.path.join(case_dir, "case_info.txt")
if not os.path.exists(case_info_path):
    print(f"ERROR: No case_info.txt found in {case_dir}")
    print("Create one with the case name, questions presented, and key context.")
    sys.exit(1)

case_info = read_file(case_info_path)
print(f"Case info: {len(case_info):,} characters")

# --- Find and read PDFs ---
brief_paths, transcript_paths = find_pdfs(case_dir)

if not brief_paths and not transcript_paths:
    print(f"ERROR: No PDFs found in {case_dir}")
    sys.exit(1)

# Read briefs
brief_text = ""
MAX_BRIEF_CHARS = 130000
chars_remaining = MAX_BRIEF_CHARS

for pdf_path in brief_paths:
    pdf_name = os.path.basename(pdf_path)
    text = read_pdf(pdf_path)
    print(f"  Brief: {pdf_name} — {len(text):,} chars")
    chunk = text[:chars_remaining]
    brief_text += f"\n\n[BRIEF: {pdf_name}]\n{chunk}"
    chars_remaining -= len(chunk)
    if chars_remaining <= 0:
        print(f"  (hit brief character budget, truncating remaining)")
        break

# Read transcripts separately
transcript_text = ""
MAX_TRANSCRIPT_CHARS = 50000

for pdf_path in transcript_paths:
    pdf_name = os.path.basename(pdf_path)
    text = read_pdf(pdf_path)
    print(f"  Transcript: {pdf_name} — {len(text):,} chars")
    transcript_text += f"\n\n[ORAL ARGUMENT TRANSCRIPT: {pdf_name}]\n{text[:MAX_TRANSCRIPT_CHARS]}"

# --- Load system prompt ---
system_prompt = read_file("prompts/issue_analysis_system.txt")

# --- Build user prompt ---
user_prompt = f"""
[CASE OVERVIEW]
{case_info}

[BRIEFS AND FILINGS]
{brief_text}
"""

if transcript_text:
    user_prompt += f"""
[ORAL ARGUMENT]
{transcript_text}
"""

user_prompt += """
TASK: Identify and analyze the specific legal questions and doctrinal frameworks 
that will determine the outcome of this case. For each question:

1. State the legal question precisely
2. Explain the competing legal theories
3. Identify the key textual hooks — the specific statutory or constitutional 
   language the Court is most likely to anchor its reasoning in
4. Identify the relevant precedents and doctrinal frameworks each side will invoke
5. Note any procedural or institutional factors — possible recusals, likelihood 
   of a per curiam opinion, unusual coalition dynamics, or narrow vs. broad 
   resolution paths

Do NOT predict individual justice votes here. Focus on mapping the doctrinal 
landscape — what are the questions, what are the possible answers, and what 
legal reasoning supports each path. The vote predictions happen in a separate 
step that uses this analysis.
"""

print(f"\nTotal prompt size: ~{len(user_prompt):,} characters")
print("Sending to Claude...\n")

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    system=system_prompt,
    messages=[
        {"role": "user", "content": user_prompt}
    ]
)

result = message.content[0].text

output_path = os.path.join(case_dir, "issue_analysis_output.txt")
with open(output_path, "w") as f:
    f.write(result)

print(result)
print(f"\n--- Saved to {output_path} ---")
print(f"Tokens used: {message.usage.input_tokens:,} in, {message.usage.output_tokens:,} out")