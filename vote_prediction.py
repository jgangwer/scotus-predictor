"""
vote_prediction.py

Step 5: Per-justice vote prediction. Makes 9 separate API calls, one per
justice. Each call gets:
  - Case overview and issue analysis output (from Step 3)
  - All case summaries (doctrinal landscape)
  - SCDB voting pattern data (statistical context)
  - Justice-specific instructions

Outputs: vote_prediction_{justice}.txt for each justice, plus
         vote_predictions_combined.txt with all 9 concatenated.

Usage:
    python3 vote_prediction.py data/tariff-case
"""

import anthropic
import sys
import os
import time
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"), override=True)

MODEL = "claude-sonnet-4-5-20250929"
MAX_RETRIES = 3
RETRY_DELAY = 5

OPINIONS_DIR = "data/opinions"
SCDB_PATH = "data/scdb_voting_data.txt"

JUSTICES = [
    "Roberts", "Thomas", "Alito", "Sotomayor", "Kagan",
    "Gorsuch", "Kavanaugh", "Barrett", "Jackson"
]


def read_file(path):
    with open(path, "r") as f:
        return f.read()


def load_all_summaries(opinions_dir):
    """Load all _summary.txt files from the opinions directory."""
    summaries = []
    for fname in sorted(os.listdir(opinions_dir)):
        if not fname.endswith("_summary.txt"):
            continue
        fpath = os.path.join(opinions_dir, fname)
        text = read_file(fpath)
        case_name = fname.replace("_summary.txt", "").replace("_", " ")
        summaries.append(f"[CASE SUMMARY: {case_name}]\n{text}")
    return summaries


def predict_justice_vote(client, justice, case_info, issue_analysis, summaries_text, scdb_text):
    """Make one API call to predict a single justice's vote.

    Uses prompt caching: the large shared context blocks (opinion summaries
    and SCDB voting data) are marked with cache_control so Anthropic caches
    them after the first call. Calls 2-9 reuse the cache at ~90% discount.
    The actual prompt content is identical to the non-cached version.
    """

    system_prompt = f"""You are a Supreme Court analyst predicting how Justice {justice} will vote in the case described below. You have deep expertise in {justice}'s judicial philosophy, writing patterns, doctrinal commitments, and voting history.

CALIBRATION RULES:
1. EMPHASIZE TEXTUAL HOOKS. The most important arguments are often the simplest textual ones. Identify the specific statutory or constitutional language {justice} is most likely to anchor reasoning in.
2. USE THE VOTING DATA. The SCDB statistics show {justice}'s actual voting patterns across hundreds of cases. If your qualitative analysis contradicts the statistical pattern, explain why this case is different.
3. CONSIDER COALITION DYNAMICS. The alignment data shows who {justice} typically joins. Use this to assess whether your predicted vote fits natural coalition patterns.
4. BE SPECIFIC ABOUT REASONING. Don't just say "{justice} is conservative/liberal." Identify the specific doctrinal framework {justice} would apply and how it leads to the predicted vote.
5. FLAG UNCERTAINTY HONESTLY. If the case presents cross-cutting considerations for {justice}, say so. A MEDIUM confidence prediction with clear reasoning is better than a fake HIGH confidence one."""

    # User message as content blocks. The summaries and SCDB blocks are
    # marked for caching — they're identical across all 9 justice calls,
    # so calls 2-9 get the cached version at ~90% discount.
    user_content = [
        {
            "type": "text",
            "text": (f"[CASE OVERVIEW]\n{case_info}\n\n"
                     f"[ISSUE ANALYSIS — Key doctrinal questions identified in prior step]\n"
                     f"{issue_analysis}"),
        },
        {
            "type": "text",
            "text": f"[CASE SUMMARIES — Prior opinions cited in the briefs]\n{summaries_text}",
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": f"[SCDB VOTING PATTERN DATA — Statistical voting history]\n{scdb_text}",
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": (f"TASK: Predict how Justice {justice} will vote in this case.\n\n"
                     f"Provide:\n"
                     f"1. VOTE: How {justice} votes (affirm/reverse/affirm in part, etc.) "
                     f"and which side of the case they land on.\n"
                     f"2. CONFIDENCE: HIGH / MEDIUM / LOW — be honest.\n"
                     f"3. DOCTRINAL REASONING: What specific legal framework or doctrine "
                     f"drives {justice}'s vote? What textual hooks matter most to {justice}? "
                     f"Which precedents from the case summaries are most influential for "
                     f"{justice}?\n"
                     f"4. KEY SIGNALS: What from the oral argument transcript (if referenced "
                     f"in the issue analysis), prior opinions, or voting patterns most "
                     f"strongly predicts this vote?\n"
                     f"5. COALITION: Who does {justice} most likely join or write with? Is "
                     f"this a case where {justice} might write separately (concurrence or "
                     f"dissent)?\n"
                     f"6. WILDCARD FACTORS: Any recusal risk, unusual cross-ideological "
                     f"alignment, or reason this prediction could be wrong.\n"),
        },
    ]

    delay = RETRY_DELAY
    for attempt in range(MAX_RETRIES):
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}],
            )
            usage = message.usage
            cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
            cache_create = getattr(usage, "cache_creation_input_tokens", 0) or 0
            if cache_read > 0 or cache_create > 0:
                print(f"    Cache: {cache_read:,} read, {cache_create:,} created")
            return message.content[0].text, usage.input_tokens, usage.output_tokens

        except anthropic.RateLimitError:
            if attempt < MAX_RETRIES - 1:
                print(f"    Rate limited, waiting {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                raise
        except anthropic.APIError as e:
            if attempt < MAX_RETRIES - 1:
                print(f"    API error ({e}), retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                raise


def main():
    # --- Get case folder from command line ---
    if len(sys.argv) < 2:
        print("Usage: python3 vote_prediction.py <case_folder>")
        print("Example: python3 vote_prediction.py data/tariff-case")
        sys.exit(1)

    case_dir = sys.argv[1].rstrip("/")

    if not os.path.isdir(case_dir):
        print(f"ERROR: {case_dir} is not a directory")
        sys.exit(1)

    # --- Read required inputs ---
    case_info_path = os.path.join(case_dir, "case_info.txt")
    issue_analysis_path = os.path.join(case_dir, "issue_analysis_output.txt")

    if not os.path.exists(case_info_path):
        print(f"ERROR: No case_info.txt found in {case_dir}")
        sys.exit(1)

    if not os.path.exists(issue_analysis_path):
        print(f"ERROR: No issue_analysis_output.txt found in {case_dir}")
        print("Run issue_analysis.py first.")
        sys.exit(1)

    case_info = read_file(case_info_path)
    issue_analysis = read_file(issue_analysis_path)
    print(f"Case info: {len(case_info):,} characters")
    print(f"Issue analysis: {len(issue_analysis):,} characters")

    # --- Load case summaries ---
    if not os.path.isdir(OPINIONS_DIR):
        print(f"ERROR: No opinions directory at {OPINIONS_DIR}")
        sys.exit(1)

    print(f"\nLoading case summaries from {OPINIONS_DIR}...")
    summaries = load_all_summaries(OPINIONS_DIR)
    print(f"  Loaded {len(summaries)} case summaries")

    # Budget: ~600K chars for summaries to stay under 200K token limit
    MAX_SUMMARY_CHARS = 600000
    summaries_text = ""
    for s in summaries:
        if len(summaries_text) + len(s) > MAX_SUMMARY_CHARS:
            remaining = len(summaries) - summaries.index(s)
            print(f"  Hit summary budget at {len(summaries_text):,} chars, skipping {remaining} summaries")
            break
        summaries_text += s + "\n\n"
    print(f"  Total summaries: {len(summaries_text):,} characters")

    # --- Load SCDB voting data ---
    if not os.path.exists(SCDB_PATH):
        print(f"WARNING: No SCDB data at {SCDB_PATH} — proceeding without voting stats")
        scdb_text = "[No SCDB voting data available]"
    else:
        scdb_text = read_file(SCDB_PATH)
        print(f"  SCDB data: {len(scdb_text):,} characters")

    # --- Estimate total prompt size ---
    shared_chars = len(case_info) + len(issue_analysis) + len(summaries_text) + len(scdb_text)
    est_tokens_per_call = shared_chars // 4  # rough estimate
    print(f"\n  Estimated ~{est_tokens_per_call:,} input tokens per justice call")
    print(f"  Estimated ~{est_tokens_per_call * 9:,} total input tokens for all 9 calls")
    est_cost = (est_tokens_per_call * 9 * 3) / 1_000_000
    print(f"  Estimated input cost: ~${est_cost:.2f}")

    # --- Create output directory ---
    votes_dir = os.path.join(case_dir, "votes")
    os.makedirs(votes_dir, exist_ok=True)

    # --- Run predictions ---
    client = anthropic.Anthropic()
    total_in = 0
    total_out = 0
    all_predictions = []
    succeeded = 0
    failed = 0

    print(f"\n{'=' * 60}")
    print(f"PREDICTING VOTES FOR {len(JUSTICES)} JUSTICES")
    print(f"{'=' * 60}\n")

    for i, justice in enumerate(JUSTICES):
        print(f"[{i + 1}/9] Justice {justice}...")

        try:
            prediction, in_tokens, out_tokens = predict_justice_vote(
                client, justice, case_info, issue_analysis, summaries_text, scdb_text
            )
            total_in += in_tokens
            total_out += out_tokens

            # Save individual prediction
            vote_path = os.path.join(votes_dir, f"vote_{justice.lower()}.txt")
            with open(vote_path, "w") as f:
                f.write(prediction)

            print(f"  Saved ({in_tokens:,} in, {out_tokens:,} out)")
            all_predictions.append(f"{'=' * 60}\nJUSTICE {justice.upper()}\n{'=' * 60}\n\n{prediction}")
            succeeded += 1

        except Exception as e:
            print(f"  FAILED: {e}")
            all_predictions.append(f"{'=' * 60}\nJUSTICE {justice.upper()}\n{'=' * 60}\n\n[PREDICTION FAILED: {e}]")
            failed += 1

        # Delay between calls
        if i < len(JUSTICES) - 1:
            time.sleep(1)

    # --- Save combined predictions ---
    combined = "\n\n".join(all_predictions)
    combined_path = os.path.join(case_dir, "vote_predictions_combined.txt")
    with open(combined_path, "w") as f:
        f.write(combined)

    # Cost estimate (Sonnet: $3/M in, $15/M out)
    est_cost = (total_in * 3 / 1_000_000) + (total_out * 15 / 1_000_000)

    print(f"\n{'=' * 60}")
    print(f"DONE")
    print(f"  Succeeded: {succeeded}")
    print(f"  Failed: {failed}")
    print(f"  Total tokens: {total_in:,} in, {total_out:,} out")
    print(f"  Estimated cost: ${est_cost:.2f}")
    print(f"  Individual predictions: {votes_dir}/")
    print(f"  Combined predictions: {combined_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
