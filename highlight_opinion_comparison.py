#!/usr/bin/env python3
"""
Compare the actual Supreme Court opinion PDF against predicted drafts (majority + dissent)
and produce a new PDF with highlights:
  GREEN  = argument/reasoning/case predicted accurately
  YELLOW = predicted but slightly off
  RED    = not predicted or prediction wrong

Uses Claude to rate each segment. Requires ANTHROPIC_API_KEY and PyMuPDF (fitz).

For a high-level narrative comparison (structure, reasoning, citations, etc.), run
  python3 compare_opinions.py <case_folder>
which writes opinion_comparison.txt. This script adds passage-level highlights to the PDF.
"""

import anthropic
import fitz
import os
import re
import sys
from pathlib import Path

# Highlight colors (RGB 0-1 for PyMuPDF)
GREEN = (0.0, 0.85, 0.4)
YELLOW = (1.0, 0.95, 0.4)
RED = (1.0, 0.4, 0.4)

CHUNK_CHARS = 3200   # target chars per batch for Claude (leave room for drafts + response)
MAX_BLOCKS_PER_CHUNK = 25


def read_pdf_blocks(pdf_path):
    """Extract (page_index, rect, text) for each text block in reading order."""
    doc = fitz.open(pdf_path)
    blocks = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        # get_text("blocks") -> (x0, y0, x1, y1, text, block_no)
        raw = page.get_text("blocks")
        for b in raw:
            if len(b) >= 5:
                x0, y0, x1, y1 = b[0], b[1], b[2], b[3]
                text = b[4] if isinstance(b[4], str) else ""
                text = (text or "").strip()
                if not text:
                    continue
                rect = fitz.Rect(x0, y0, x1, y1)
                blocks.append((page_num, rect, text))
    doc.close()
    return blocks


def chunk_blocks(blocks):
    """Group blocks into chunks of ~CHUNK_CHARS for API calls."""
    chunks = []
    current = []
    current_len = 0
    for item in blocks:
        page_num, rect, text = item
        current.append(item)
        current_len += len(text) + 1
        if current_len >= CHUNK_CHARS or len(current) >= MAX_BLOCKS_PER_CHUNK:
            chunks.append(current)
            current = []
            current_len = 0
    if current:
        chunks.append(current)
    return chunks


def rate_chunk_with_claude(client, chunk_blocks_list, draft_majority, draft_dissent, model="claude-sonnet-4-5-20250929"):
    """Send one chunk (list of (page_num, rect, text)) to Claude; return list of GREEN|YELLOW|RED same length."""
    passages = []
    for _, _, text in chunk_blocks_list:
        passages.append(text)
    numbered = "\n\n".join(f"[Passage {i+1}]\n{p}" for i, p in enumerate(passages))
    n = len(passages)

    draft_section = ""
    if draft_majority:
        draft_section += f"[PREDICTED MAJORITY OPINION]\n{draft_majority[:60000]}\n\n"
    if draft_dissent:
        draft_section += f"[PREDICTED DISSENT]\n{draft_dissent[:60000]}\n\n"

    user_content = f"""You are comparing excerpts from the ACTUAL Supreme Court opinion to the PREDICTED drafts above.

{draft_section}

[ACTUAL OPINION EXCERPTS TO RATE]
{numbered}

For each passage (1 to {n}), decide how well the predicted drafts anticipated this part of the actual opinion.
- If the passage is from the Court's majority opinion, compare to the PREDICTED MAJORITY.
- If the passage is from a dissent or concurrence, compare to the PREDICTED DISSENT.

Output exactly {n} lines. Each line must be:
<number> <rating> <one short reason>

Rating:
- GREEN: This argument, reasoning, or case was predicted accurately (same idea, same thrust).
- YELLOW: Predicted but slightly off (right general idea, different framing, or partial match).
- RED: Not predicted at all, or the prediction got this wrong or contradicted it.

Example:
1 GREEN Same textual focus on "regulate" not including taxation.
2 YELLOW Major questions doctrine predicted but real opinion is narrower.
3 RED Jurisdictional dismissal was not in the draft.

Output your {n} lines now (no other text):"""

    try:
        msg = client.messages.create(
            model=model,
            max_tokens=2048,
            system="You are a legal expert comparing predicted Supreme Court drafts to the actual opinion. Output only the requested numbered lines with GREEN, YELLOW, or RED and a brief reason.",
            messages=[{"role": "user", "content": user_content}],
        )
        text = msg.content[0].text
    except Exception as e:
        print(f"Claude API error: {e}", file=sys.stderr)
        return ["YELLOW"] * n  # fallback

    # Parse response: accept "1 GREEN ...", "1. GREEN ...", "1) GREEN", "Passage 1: GREEN", etc.
    ratings = [None] * n
    for line in text.strip().split("\n"):
        line = line.strip()
        # Match number (with optional . or )) then GREEN|YELLOW|RED
        m = re.search(r"(\d+)\s*[.:)]?\s*(GREEN|YELLOW|RED)\b", line, re.I)
        if m:
            i = int(m.group(1))
            if 1 <= i <= n:
                ratings[i - 1] = m.group(2).upper()
    filled = sum(1 for r in ratings if r is not None)
    if filled < n:
        print(f"  (Parsed {filled}/{n} ratings from Claude; filling rest as YELLOW)", file=sys.stderr)
    for i in range(n):
        if ratings[i] is None:
            ratings[i] = "YELLOW"
    return ratings


def apply_highlights_pdf(pdf_path, out_path, block_ratings):
    """
    Use Square (rectangle) annotations with fill — PDF Highlight type ignores fill color.
    block_ratings: list of (page_num, rect, rating) where rating is GREEN|YELLOW|RED.
    """
    doc = fitz.open(pdf_path)
    for page_num, rect, rating in block_ratings:
        if page_num >= len(doc):
            continue
        page = doc[page_num]
        color = GREEN if rating == "GREEN" else (YELLOW if rating == "YELLOW" else RED)
        annot = page.add_rect_annot(rect)
        annot.set_colors(fill=color)
        annot.set_border(width=0)
        annot.set_opacity(0.5)
    doc.save(out_path, garbage=4, deflate=True)
    doc.close()


def write_html_output(entries, out_path, title="Opinion comparison"):
    """
    entries: list of (page_num, rect, text, rating). Writes HTML with span background colors.
    """
    import html
    css = {
        "GREEN": "background-color: rgba(0, 217, 102, 0.45);",
        "YELLOW": "background-color: rgba(255, 242, 102, 0.55);",
        "RED": "background-color: rgba(255, 102, 102, 0.45);",
    }
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>", html.escape(title), "</title>",
        "<style>body{font-family:Georgia,serif;max-width:800px;margin:2em auto;padding:0 1em;}",
        "span.green{" + css["GREEN"] + "} span.yellow{" + css["YELLOW"] + "} span.red{" + css["RED"] + "}",
        ".page-break{margin-top:2em;padding-top:1em;border-top:1px solid #ccc;}",
        ".legend{margin-bottom:1.5em;padding:0.5em;background:#f5f5f5;}",
        "span{display:block;margin:0.3em 0;}",
        "</style></head><body>",
        "<div class='legend'><b>Legend:</b> ",
        "<span class='green' style='display:inline'>Green</span> = predicted accurately · ",
        "<span class='yellow' style='display:inline'>Yellow</span> = predicted but slightly off · ",
        "<span class='red' style='display:inline'>Red</span> = not predicted or wrong</div>",
    ]
    cur_page = None
    for page_num, _rect, text, rating in entries:
        if page_num != cur_page:
            if cur_page is not None:
                parts.append("</div>")
            parts.append(f"<div class='page-break' data-page='{page_num + 1}'>")
            cur_page = page_num
        cls = rating.lower()
        escaped = html.escape(text).replace("\n", "<br>\n")
        parts.append(f"<span class='{cls}'>{escaped}</span>")
    if cur_page is not None:
        parts.append("</div>")
    parts.append("</body></html>")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(parts))


def main():
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    ap = argparse.ArgumentParser(
        description="Compare actual opinion PDF to predicted drafts and output a highlighted PDF."
    )
    ap.add_argument("pdf", help="Path to the actual opinion PDF")
    ap.add_argument("case_folder", nargs="?", default=None,
        help="Folder with majority_draft.txt and dissent_draft.txt (default: data/tariff-case)")
    ap.add_argument("-o", "--output", default=None,
        help="Output path: PDF or HTML base (default: <pdf_basename>_compared)")
    ap.add_argument("--format", choices=("both", "pdf", "html"), default="both",
        help="Output format: both (PDF + HTML), pdf only, or html only (default: both)")
    ap.add_argument("--dry-run", action="store_true",
        help="Only extract blocks and print counts; do not call Claude or write output")
    args = ap.parse_args()

    pdf_path = os.path.abspath(args.pdf)
    case_dir = os.path.abspath(args.case_folder) if args.case_folder else os.path.abspath(os.path.join(os.getcwd(), "data", "tariff-case"))

    if not os.path.isfile(pdf_path):
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    majority_path = os.path.join(case_dir, "majority_draft.txt")
    dissent_path = os.path.join(case_dir, "dissent_draft.txt")
    draft_majority = None
    draft_dissent = None
    if os.path.isfile(majority_path):
        with open(majority_path, "r") as f:
            draft_majority = f.read()
        print(f"Loaded majority draft: {len(draft_majority):,} chars")
    if os.path.isfile(dissent_path):
        with open(dissent_path, "r") as f:
            draft_dissent = f.read()
        print(f"Loaded dissent draft: {len(draft_dissent):,} chars")
    if not draft_majority and not draft_dissent:
        print("ERROR: No majority_draft.txt or dissent_draft.txt found in", case_dir)
        sys.exit(1)

    print("Extracting text blocks from PDF...")
    blocks = read_pdf_blocks(pdf_path)
    print(f"Found {len(blocks)} blocks")

    chunks = chunk_blocks(blocks)
    print(f"Split into {len(chunks)} chunks for API")
    if args.dry_run:
        print("Dry run: skipping Claude and PDF output.")
        return

    client = anthropic.Anthropic()
    # Keep (page_num, rect, text, rating) for HTML; PDF uses (page_num, rect, rating)
    all_entries = []
    for i, chunk in enumerate(chunks):
        print(f"Rating chunk {i+1}/{len(chunks)} ({len(chunk)} blocks)...")
        ratings = rate_chunk_with_claude(client, chunk, draft_majority, draft_dissent)
        for (page_num, rect, text), rating in zip(chunk, ratings):
            all_entries.append((page_num, rect, text, rating))

    out_dir = os.path.dirname(pdf_path) or "."
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    if args.output:
        out_base = os.path.abspath(args.output)
        if not out_base.endswith(".pdf") and not out_base.endswith(".html"):
            pdf_path_out = out_base + ".pdf"
            html_path_out = out_base + ".html"
        else:
            pdf_path_out = out_base.replace(".html", ".pdf")
            html_path_out = out_base.replace(".pdf", ".html")
    else:
        pdf_path_out = os.path.join(out_dir, f"{base}_compared.pdf")
        html_path_out = os.path.join(out_dir, f"{base}_compared.html")

    block_ratings = [(e[0], e[1], e[3]) for e in all_entries]
    if args.format in ("both", "pdf"):
        print(f"Writing PDF to {pdf_path_out}...")
        apply_highlights_pdf(pdf_path, pdf_path_out, block_ratings)
    if args.format in ("both", "html"):
        print(f"Writing HTML to {html_path_out}...")
        write_html_output(all_entries, html_path_out, title=f"Comparison: {base}")
    print("Done.")
    print("Legend: GREEN = predicted accurately | YELLOW = predicted but slightly off | RED = not predicted or wrong")


if __name__ == "__main__":
    main()
