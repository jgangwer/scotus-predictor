"""
summarize_opinions.py

Generates general-purpose summaries of Supreme Court opinions for use
across any future case analysis. Summaries capture the holding, reasoning,
vote breakdown, and each justice's position.

Summaries are saved alongside the originals: if the opinion is
  data/opinions/loper-bright.txt
the summary will be
  data/opinions/loper-bright_summary.txt

Already-summarized opinions are skipped automatically.

Usage:
    python3 summarize_opinions.py
    python3 summarize_opinions.py --force   # re-summarize everything
"""

import anthropic
import os
import sys
import time
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"), override=True)

OPINIONS_DIR = "data/opinions"
MODEL = "claude-sonnet-4-5-20250929"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds, doubles each retry


def read_file(path):
    with open(path, "r") as f:
        return f.read()


def get_opinion_files(opinions_dir):
    """Get all opinion .txt files, excluding summaries and index files."""
    files = []
    for fname in sorted(os.listdir(opinions_dir)):
        if not fname.endswith(".txt"):
            continue
        if fname.startswith("_"):
            continue
        if fname.endswith("_summary.txt"):
            continue
        files.append(fname)
    return files


def summary_exists(opinions_dir, opinion_filename):
    """Check if a summary already exists for this opinion."""
    summary_name = opinion_filename.replace(".txt", "_summary.txt")
    return os.path.exists(os.path.join(opinions_dir, summary_name))


def summarize_opinion(client, opinion_text, opinion_filename):
    """Send one opinion to Claude and get a general-purpose summary."""

    # Truncate if the opinion is extremely long (some compiled opinions
    # with multiple concurrences/dissents can exceed context limits)
    max_chars = 350000  # leaves room for prompt + response
    if len(opinion_text) > max_chars:
        opinion_text = opinion_text[:max_chars] + "\n\n[... remainder truncated ...]"

    user_prompt = f"""[SUPREME COURT OPINION]
File: {opinion_filename}

{opinion_text}

TASK: Write a general-purpose summary of this opinion (approximately 1 page). This summary will be used as reference material for analyzing future Supreme Court cases, so it should capture the opinion's lasting analytical value rather than being tied to any specific pending case.

Include:

1. CASE AND HOLDING: Case name, citation if visible, and what the Court held in 2-3 sentences.

2. VOTE BREAKDOWN: The exact vote split. Who was in the majority. Who dissented. Who concurred separately.

3. MAJORITY REASONING: The key doctrinal frameworks, legal tests, and analytical moves the majority used to reach its conclusion. What principles did they rely on? What precedents did they apply or distinguish?

4. SEPARATE WRITINGS: For each concurrence and dissent, summarize the author's reasoning in 2-3 sentences. Focus on where and why they diverged from the majority — what principle or framework did they apply differently?

5. DOCTRINAL SIGNIFICANCE: What broader legal principles does this case establish or reinforce? What future questions does it leave open?

Be specific about which justice said what. Use their names. This summary needs to be useful for understanding how individual justices think, not just what the Court decided as a whole."""

    delay = RETRY_DELAY
    for attempt in range(MAX_RETRIES):
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=2000,
                system="You are a Supreme Court analyst writing concise, analytically rich case summaries. Focus on doctrinal reasoning and individual justice positions, not procedural history. Be specific and precise.",
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return message.content[0].text, message.usage.input_tokens, message.usage.output_tokens

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
    force = "--force" in sys.argv

    if not os.path.isdir(OPINIONS_DIR):
        print(f"ERROR: No opinions directory found at {OPINIONS_DIR}")
        print("Run fetch_opinions.py first.")
        sys.exit(1)

    opinion_files = get_opinion_files(OPINIONS_DIR)
    if not opinion_files:
        print(f"ERROR: No opinion .txt files found in {OPINIONS_DIR}")
        sys.exit(1)

    # Count what needs to be done
    to_summarize = []
    already_done = 0
    for fname in opinion_files:
        if not force and summary_exists(OPINIONS_DIR, fname):
            already_done += 1
        else:
            to_summarize.append(fname)

    print(f"Found {len(opinion_files)} opinions in {OPINIONS_DIR}")
    print(f"  Already summarized: {already_done}")
    print(f"  To summarize: {len(to_summarize)}")

    if not to_summarize:
        print("\nNothing to do. Use --force to re-summarize everything.")
        return

    print(f"\nStarting summarization...\n")

    client = anthropic.Anthropic()
    total_input_tokens = 0
    total_output_tokens = 0
    succeeded = 0
    failed = 0

    for i, fname in enumerate(to_summarize):
        print(f"[{i + 1}/{len(to_summarize)}] {fname}")

        fpath = os.path.join(OPINIONS_DIR, fname)
        opinion_text = read_file(fpath)
        print(f"    {len(opinion_text):,} characters")

        try:
            summary, in_tokens, out_tokens = summarize_opinion(
                client, opinion_text, fname
            )
            total_input_tokens += in_tokens
            total_output_tokens += out_tokens

            # Save summary
            summary_name = fname.replace(".txt", "_summary.txt")
            summary_path = os.path.join(OPINIONS_DIR, summary_name)
            with open(summary_path, "w") as f:
                f.write(summary)

            print(f"    Saved {summary_name} ({in_tokens} in, {out_tokens} out)")
            succeeded += 1

        except Exception as e:
            print(f"    FAILED: {e}")
            failed += 1

        # Small delay between calls to be polite to the API
        if i < len(to_summarize) - 1:
            time.sleep(0.5)

    # Cost estimate (Sonnet pricing: $3/M input, $15/M output)
    est_cost = (total_input_tokens * 3 / 1_000_000) + (total_output_tokens * 15 / 1_000_000)

    print(f"\n{'=' * 60}")
    print(f"DONE")
    print(f"  Summarized: {succeeded}")
    print(f"  Failed: {failed}")
    print(f"  Total tokens: {total_input_tokens:,} in, {total_output_tokens:,} out")
    print(f"  Estimated cost: ${est_cost:.2f}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()