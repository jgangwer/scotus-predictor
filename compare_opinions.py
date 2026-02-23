import anthropic
import fitz
import sys
import os
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

# --- Get case folder from command line ---
if len(sys.argv) < 2:
    print("Usage: python3 compare_opinions.py <case_folder>")
    print("Example: python3 compare_opinions.py data/tariff-case")
    print("")
    print("Requires opinion.pdf and draft opinion files in the case folder.")
    sys.exit(1)

case_dir = sys.argv[1].rstrip("/")

if not os.path.isdir(case_dir):
    print(f"ERROR: {case_dir} is not a directory")
    sys.exit(1)

# --- Find the real opinion PDF ---
opinion_pdf = os.path.join(case_dir, "opinion.pdf")
if not os.path.exists(opinion_pdf):
    print(f"ERROR: No opinion.pdf found in {case_dir}")
    sys.exit(1)

print("Reading files...")
real_opinion = read_pdf(opinion_pdf)

# --- Find draft opinions ---
draft_majority_path = os.path.join(case_dir, "majority_draft.txt")
draft_dissent_path = os.path.join(case_dir, "dissent_draft.txt")

draft_majority = None
draft_dissent = None

if os.path.exists(draft_majority_path):
    draft_majority = read_file(draft_majority_path)
    print(f"Found majority draft: {len(draft_majority):,} characters")
else:
    print("WARNING: No majority_draft.txt found")

if os.path.exists(draft_dissent_path):
    draft_dissent = read_file(draft_dissent_path)
    print(f"Found dissent draft: {len(draft_dissent):,} characters")
else:
    print("WARNING: No dissent_draft.txt found")

if not draft_majority and not draft_dissent:
    print("ERROR: No draft opinions found")
    sys.exit(1)

client = anthropic.Anthropic()

user_prompt = f"""
I built a system that drafts predicted Supreme Court opinions before decisions are released.
Now I have the real opinion. Grade the drafts against reality.
"""

if draft_majority:
    user_prompt += f"""
[DRAFT MAJORITY OPINION]
{draft_majority}
"""

if draft_dissent:
    user_prompt += f"""
[DRAFT DISSENT]
{draft_dissent}
"""

user_prompt += f"""
[ACTUAL OPINION]
{real_opinion[:80000]}

TASK: Grade each draft on these dimensions (1-10 scale with explanation):

FOR THE MAJORITY DRAFT (if provided):
1. STRUCTURE: Did it match the real opinion's organization and flow?
2. LEGAL REASONING: Did it identify the same arguments and doctrinal moves?
3. KEY PASSAGES: Did it anticipate the opinion's most important analytical moments?
4. VOICE: Does it sound like the actual author? Capture their rhetorical style?
5. CITATIONS: Did it cite the same key cases?
6. WHAT IT MISSED: Important elements of the real opinion absent from the draft.
7. WHAT IT GOT WRONG: Things in the draft that contradict the real opinion.

FOR THE DISSENT DRAFT (if provided):
Same 7 dimensions for the dissent.

End with: If an attorney read these drafts before the real decision dropped, how 
prepared would they have been? What would have surprised them? What's the single 
biggest improvement to make the drafts more useful?
"""

print("Sending to Claude for grading...\n")

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    system="You are a Supreme Court scholar comparing predicted draft opinions against actual Supreme Court opinions. Be rigorous, specific, and cite particular passages from both drafts and the real opinion.",
    messages=[
        {"role": "user", "content": user_prompt}
    ]
)

result = message.content[0].text

output_path = os.path.join(case_dir, "opinion_comparison.txt")
with open(output_path, "w") as f:
    f.write(result)

print(result)
print(f"\n--- Saved to {output_path} ---")
print(f"Tokens used: {message.usage.input_tokens} in, {message.usage.output_tokens} out")