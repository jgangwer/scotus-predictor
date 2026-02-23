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
    print("Usage: python3 compare_prediction.py <case_folder>")
    print("Example: python3 compare_prediction.py data/loper-bright")
    print("")
    print("Requires opinion.pdf (the real opinion) in the case folder.")
    sys.exit(1)

case_dir = sys.argv[1].rstrip("/")

if not os.path.isdir(case_dir):
    print(f"ERROR: {case_dir} is not a directory")
    sys.exit(1)

# --- Find the real opinion PDF ---
opinion_pdf = os.path.join(case_dir, "opinion.pdf")
if not os.path.exists(opinion_pdf):
    print(f"ERROR: No opinion.pdf found in {case_dir}")
    print("This script compares predictions against the actual opinion.")
    print("Download the real opinion and save it as opinion.pdf in the case folder.")
    sys.exit(1)

# --- Find prediction outputs ---
issue_analysis_path = os.path.join(case_dir, "issue_analysis_output.txt")
scenario_path = os.path.join(case_dir, "scenario_output.txt")
majority_path = os.path.join(case_dir, "majority_draft.txt")
dissent_path = os.path.join(case_dir, "dissent_draft.txt")

prediction_text = ""
for label, path in [
    ("ISSUE ANALYSIS", issue_analysis_path),
    ("SCENARIO CONSTRUCTION", scenario_path),
    ("MAJORITY DRAFT", majority_path),
    ("DISSENT DRAFT", dissent_path),
]:
    if os.path.exists(path):
        content = read_file(path)
        prediction_text += f"\n\n[{label}]\n{content}"
        print(f"Found {label}: {len(content):,} characters")
    else:
        print(f"Skipping {label} (not found)")

if not prediction_text.strip():
    print("ERROR: No prediction outputs found. Run the pipeline first.")
    sys.exit(1)

# --- Read the real opinion ---
print(f"\nReading actual opinion...")
opinion = read_pdf(opinion_pdf)
print(f"Opinion: {len(opinion):,} characters")

# --- Build prompt ---
case_info = read_file(os.path.join(case_dir, "case_info.txt")) if os.path.exists(os.path.join(case_dir, "case_info.txt")) else "See documents below."

user_prompt = f"""
I built a Supreme Court prediction system. Before the decision was issued, the 
system produced the following predictions:

{prediction_text[:60000]}

Now I have the actual opinion:

[ACTUAL OPINION TEXT]
{opinion[:80000]}

TASK: Compare the predictions against the actual opinion. Grade each of the following 
on a scale of 1-10, with explanation:

1. OUTCOME PREDICTION: Did it get the result and vote count right?
2. COALITION MAPPING: Did it correctly predict who voted which way?
3. DOCTRINAL REASONING: Did it identify the same legal frameworks the majority actually relied on?
4. KEY ARGUMENTS: Did it anticipate the main arguments in the majority opinion?
5. DISSENT ANALYSIS: Did it correctly anticipate the dissent's reasoning?
6. OPINION VOICE (if drafts available): Does the draft opinion sound like the actual author?
7. MISSED ISSUES: What did the actual opinion focus on that the prediction missed entirely?
8. FALSE POSITIVES: What did the prediction emphasize that turned out to be unimportant?

End with an overall assessment: How useful would this prediction have been to an 
attorney preparing for this decision? What are the biggest areas for improvement?
"""

print(f"\nTotal prompt size: ~{len(user_prompt):,} characters")
print("Sending to Claude for grading...\n")

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    system="You are a Supreme Court scholar conducting a rigorous post-mortem comparison of a predictive analysis against an actual Supreme Court opinion. Be specific, cite particular passages from both documents, and be honest about both strengths and weaknesses.",
    messages=[
        {"role": "user", "content": user_prompt}
    ]
)

result = message.content[0].text

output_path = os.path.join(case_dir, "comparison_output.txt")
with open(output_path, "w") as f:
    f.write(result)

print(result)
print(f"\n--- Saved to {output_path} ---")
print(f"Tokens used: {message.usage.input_tokens} in, {message.usage.output_tokens} out")