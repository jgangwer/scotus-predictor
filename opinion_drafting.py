import anthropic
import fitz
import sys
import os
import json
from dotenv import load_dotenv

load_dotenv()

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
    """Find PDFs supporting both flat and structured layouts."""
    briefs_dir = os.path.join(case_dir, "briefs")
    transcript_dir = os.path.join(case_dir, "transcript")
    
    briefs = []
    transcripts = []
    
    if os.path.isdir(briefs_dir):
        briefs = sorted([os.path.join(briefs_dir, f) for f in os.listdir(briefs_dir) if f.lower().endswith(".pdf")])
        if os.path.isdir(transcript_dir):
            transcripts = sorted([os.path.join(transcript_dir, f) for f in os.listdir(transcript_dir) if f.lower().endswith(".pdf")])
    else:
        briefs = sorted([os.path.join(case_dir, f) for f in os.listdir(case_dir) if f.lower().endswith(".pdf")])
    
    return briefs, transcripts

# --- Get case folder from command line ---
if len(sys.argv) < 2:
    print("Usage: python3 opinion_drafting.py <case_folder>")
    print("Example: python3 opinion_drafting.py data/loper-bright")
    print("         python3 opinion_drafting.py data/tariff-case")
    sys.exit(1)

case_dir = sys.argv[1].rstrip("/")

if not os.path.isdir(case_dir):
    print(f"ERROR: {case_dir} is not a directory")
    sys.exit(1)

# --- Read required inputs ---
case_info_path = os.path.join(case_dir, "case_info.txt")
scenario_path = os.path.join(case_dir, "scenario_output.txt")

if not os.path.exists(case_info_path):
    print(f"ERROR: No case_info.txt found in {case_dir}")
    sys.exit(1)

if not os.path.exists(scenario_path):
    print(f"ERROR: No scenario_output.txt found in {case_dir}")
    print("Run scenario_construction.py first.")
    sys.exit(1)

case_info = read_file(case_info_path)
scenario = read_file(scenario_path)
system_prompt = read_file("prompts/opinion_drafting_system.txt")

# --- Read PDFs for source material ---
brief_paths, transcript_paths = find_pdfs(case_dir)
all_pdf_text = ""
MAX_PDF_CHARS = 60000
chars_remaining = MAX_PDF_CHARS

for pdf_path in brief_paths + transcript_paths:
    pdf_name = os.path.basename(pdf_path)
    text = read_pdf(pdf_path)
    chunk = text[:chars_remaining]
    all_pdf_text += f"\n\n[SOURCE: {pdf_name}]\n{chunk}"
    chars_remaining -= len(chunk)
    if chars_remaining <= 0:
        break

print(f"Read {len(brief_paths)} briefs + {len(transcript_paths)} transcripts ({len(all_pdf_text):,} chars)")

# --- Read prior opinions if available ---
opinions_dir = "data/opinions"
opinions_text = ""
if os.path.isdir(opinions_dir):
    opinion_files = [f for f in os.listdir(opinions_dir) if f.endswith(".txt") and not f.startswith("_")]
    if opinion_files:
        MAX_OPINION_CHARS = 30000
        chars_remaining = MAX_OPINION_CHARS
        for op_file in sorted(opinion_files)[:20]:
            op_path = os.path.join(opinions_dir, op_file)
            op_text = read_file(op_path)
            chunk = op_text[:chars_remaining]
            opinions_text += f"\n\n[PRIOR OPINION: {op_file}]\n{chunk}"
            chars_remaining -= len(chunk)
            if chars_remaining <= 0:
                break
        print(f"Included {len(opinions_text):,} chars of prior opinions")

client = anthropic.Anthropic()

# --- Step 1: Ask Claude to identify who writes what in the top scenario ---
print("\nIdentifying opinion assignments from scenario...")

extract_message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=500,
    messages=[
        {"role": "user", "content": f"""From this scenario analysis, identify the opinions to draft for the MOST LIKELY scenario only.

{scenario}

Respond in exactly this JSON format, nothing else:
{{
    "opinions": [
        {{"justice": "Chief Justice Roberts", "role": "majority opinion", "filename": "majority_draft.txt"}},
        {{"justice": "Justice Kagan", "role": "dissenting opinion", "filename": "dissent_draft.txt"}}
    ]
}}

Include the majority opinion and the primary dissent. If there's an important concurrence, include that too. Use the justice's full title (e.g., "Chief Justice Roberts" or "Justice Thomas"). For filename, use majority_draft.txt, dissent_draft.txt, concurrence_draft.txt."""}
    ]
)

raw_response = extract_message.content[0].text.strip()

# Parse JSON - handle markdown code blocks if Claude wraps it
if raw_response.startswith("```"):
    raw_response = raw_response.split("\n", 1)[1].rsplit("```", 1)[0]

try:
    assignments = json.loads(raw_response)
    opinions_to_draft = assignments["opinions"]
except (json.JSONDecodeError, KeyError) as e:
    print(f"WARNING: Couldn't parse opinion assignments: {e}")
    print(f"Raw response: {raw_response}")
    print("Falling back to default: majority + dissent")
    opinions_to_draft = [
        {"justice": "the majority opinion author", "role": "majority opinion", "filename": "majority_draft.txt"},
        {"justice": "the primary dissent author", "role": "dissenting opinion", "filename": "dissent_draft.txt"},
    ]

print(f"Will draft {len(opinions_to_draft)} opinions:")
for op in opinions_to_draft:
    print(f"  - {op['role']} by {op['justice']}")

# --- Step 2: Draft each opinion ---
for opinion in opinions_to_draft:
    print(f"\n{'='*60}")
    print(f"Drafting {opinion['role']} by {opinion['justice']}...")
    print(f"{'='*60}")

    user_prompt = f"""
[CASE]
{case_info}

[SCENARIO AND COALITION]
{scenario[:15000]}

[CASE MATERIALS]
{all_pdf_text}
"""

    if opinions_text:
        user_prompt += f"""
[RELEVANT PRIOR OPINIONS]
{opinions_text}
"""

    user_prompt += f"""
TASK: Draft the {opinion['role']} by {opinion['justice']}. 

This should read like a real Supreme Court opinion — proper structure, legal 
reasoning grounded in authority, and the authentic voice of this justice. 
Include the syllabus-style opening, section structure, and citation format 
characteristic of actual opinions.

Do not fabricate case citations. If you need to cite a case you're unsure about, 
write [additional authority needed].
"""

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    result = message.content[0].text
    output_path = os.path.join(case_dir, opinion["filename"])

    with open(output_path, "w") as f:
        f.write(result)

    print(result[:2000])
    print(f"\n... [full text saved to {output_path}]")
    print(f"Tokens: {message.usage.input_tokens} in, {message.usage.output_tokens} out")

print(f"\n{'='*60}")
print(f"All opinions saved to {case_dir}/")
print(f"{'='*60}")