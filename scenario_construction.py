import anthropic
import sys
import os
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"), override=True)

def read_file(path):
    with open(path, "r") as f:
        return f.read()

# --- Get case folder from command line ---
if len(sys.argv) < 2:
    print("Usage: python3 scenario_construction.py <case_folder>")
    print("Example: python3 scenario_construction.py data/loper-bright")
    print("         python3 scenario_construction.py data/tariff-case")
    sys.exit(1)

case_dir = sys.argv[1].rstrip("/")

if not os.path.isdir(case_dir):
    print(f"ERROR: {case_dir} is not a directory")
    sys.exit(1)

# --- Read required inputs ---
case_info_path = os.path.join(case_dir, "case_info.txt")
issue_analysis_path = os.path.join(case_dir, "vote_predictions_combined.txt")

if not os.path.exists(case_info_path):
    print(f"ERROR: No case_info.txt found in {case_dir}")
    sys.exit(1)

if not os.path.exists(issue_analysis_path):
    print(f"ERROR: No issue_analysis_output.txt found in {case_dir}")
    print("Run issue_analysis.py first.")
    sys.exit(1)

case_info = read_file(case_info_path)
issue_analysis = read_file(issue_analysis_path)
system_prompt = read_file("prompts/scenario_system.txt")

print(f"Case info: {len(case_info):,} characters")
print(f"Issue analysis: {len(issue_analysis):,} characters")

# --- Build prompt ---
user_prompt = f"""
[CASE]
{case_info}

[ISSUE ANALYSIS AND VOTE PREDICTIONS]
{issue_analysis}

TASK: Construct 2-3 distinct outcome scenarios for this case. For each scenario provide:

1. SCENARIO NAME: A short descriptive label
2. PROBABILITY: Percentage likelihood (all scenarios must sum to ~100%)
3. VOTE SPLIT: Exact coalition (e.g., 6-3, Roberts writing for Thomas, Alito, Gorsuch, Kavanaugh, Barrett)
4. HOLDING: One-paragraph summary of what the Court holds
5. PRIMARY LEGAL REASONING: The doctrinal path — what textual, structural, and historical arguments anchor the opinion
6. WHAT REPLACES THE OLD RULE: The practical framework going forward
7. CONCURRENCES: Who writes separately and why
8. DISSENT: Who dissents, who writes, and the core argument
9. IMPLICATIONS: What this means for pending cases, related legal questions, and the broader legal landscape
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

output_path = os.path.join(case_dir, "scenario_output.txt")
with open(output_path, "w") as f:
    f.write(result)

print(result)
print(f"\n--- Saved to {output_path} ---")
print(f"Tokens used: {message.usage.input_tokens} in, {message.usage.output_tokens} out")