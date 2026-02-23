#!/usr/bin/env python3
"""
generate_opinion_pdfs.py — Convert draft opinion .txt files to formatted PDFs
resembling Supreme Court slip opinions.

Usage:
    python3 generate_opinion_pdfs.py data/tariff-case
    python3 generate_opinion_pdfs.py data/cases/25-332
    python3 generate_opinion_pdfs.py --all   # all cases with draft files
"""

import os
import sys
import re
import json
import textwrap

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable
)
from reportlab.lib import colors

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
DISCLAIMER = "AI-GENERATED PREDICTION \u2014 NOT AN ACTUAL SUPREME COURT OPINION"
PAGE_W, PAGE_H = letter
MARGIN = 1.0 * inch

DRAFT_PATTERNS = [
    ("majority_draft.txt",   "majority"),
    ("dissent_draft.txt",    "dissent"),
    ("concurrence_draft.txt", "concurrence"),
]

# Also pick up named concurrences like concurrence_thomas_draft.txt
def find_draft_files(case_dir):
    """Return list of (txt_path, opinion_type, basename) for all draft files."""
    results = []
    for fname in sorted(os.listdir(case_dir)):
        if not fname.endswith("_draft.txt"):
            continue
        fpath = os.path.join(case_dir, fname)
        if "majority" in fname:
            otype = "majority"
        elif "dissent" in fname:
            otype = "dissent"
        elif "concurrence" in fname:
            otype = "concurrence"
        else:
            otype = "opinion"
        basename = fname.replace("_draft.txt", "") + ".pdf"
        results.append((fpath, otype, basename))
    return results


# ------------------------------------------------------------------
# PDF builder
# ------------------------------------------------------------------
def build_opinion_pdf(txt_path, out_path, opinion_type="majority"):
    """Convert a draft opinion .txt file to a formatted PDF."""
    with open(txt_path, "r", encoding="utf-8") as f:
        raw = f.read()

    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        "CourtHeader",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=6,
        spaceBefore=12,
    ))
    styles.add(ParagraphStyle(
        "CourtSubheader",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "OpinionBody",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=11,
        leading=15,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        firstLineIndent=24,
    ))
    styles.add(ParagraphStyle(
        "OpinionBodyNoIndent",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=11,
        leading=15,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=11,
        alignment=TA_CENTER,
        spaceAfter=8,
        spaceBefore=16,
    ))
    styles.add(ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        alignment=TA_CENTER,
        textColor=colors.Color(0.6, 0.1, 0.1),
    ))

    def on_each_page(canvas, doc):
        """Draw page number and disclaimer footer on every page."""
        canvas.saveState()
        # Page number
        canvas.setFont("Times-Roman", 9)
        canvas.drawCentredString(PAGE_W / 2, 0.6 * inch, str(doc.page))
        # Disclaimer
        canvas.setFont("Helvetica-Bold", 7)
        canvas.setFillColor(colors.Color(0.6, 0.1, 0.1))
        canvas.drawCentredString(PAGE_W / 2, 0.35 * inch, DISCLAIMER)
        # Top line
        canvas.setStrokeColor(colors.Color(0, 0, 0))
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, PAGE_H - 0.8 * inch, PAGE_W - MARGIN, PAGE_H - 0.8 * inch)
        canvas.restoreState()

    doc = SimpleDocTemplate(
        out_path,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=1.0 * inch,
        bottomMargin=0.9 * inch,
    )

    story = []

    # Parse the text into paragraphs
    lines = raw.split("\n")
    i = 0
    header_done = False

    while i < len(lines):
        line = lines[i].rstrip()

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Detect header section (first ~20 lines typically contain court header)
        if not header_done:
            # Lines like "SUPREME COURT OF THE UNITED STATES", docket numbers,
            # party names, "ON WRITS OF CERTIORARI...", date, author line
            if line.startswith("SUPREME COURT"):
                story.append(Paragraph(escape_xml(line), styles["CourtHeader"]))
                i += 1
                continue
            elif line.startswith("_") and len(line.strip("_")) == 0:
                story.append(HRFlowable(width="60%", thickness=1, color=colors.black))
                i += 1
                continue
            elif line.startswith("No") and ("." in line or "-" in line):
                story.append(Paragraph(escape_xml(line), styles["CourtSubheader"]))
                i += 1
                continue
            elif line.startswith("[") and line.endswith("]"):
                # Date line like [June __, 2026]
                story.append(Spacer(1, 12))
                story.append(Paragraph(escape_xml(line), styles["CourtSubheader"]))
                story.append(Spacer(1, 12))
                i += 1
                header_done = True
                continue
            elif line.startswith("ON WRIT") or line.startswith("ON PETITION"):
                story.append(Paragraph(escape_xml(line), styles["CourtSubheader"]))
                i += 1
                continue
            elif any(x in line.upper() for x in ["PETITIONER", "RESPONDENT", "APPELLANT"]):
                story.append(Paragraph(escape_xml(line), styles["CourtSubheader"]))
                i += 1
                continue
            elif line.strip().lower() == "v.":
                story.append(Paragraph(escape_xml(line), styles["CourtSubheader"]))
                i += 1
                continue
            elif "delivered the opinion" in line.lower() or "filed a dissenting" in line.lower() or "filed a concurring" in line.lower() or "concurring in" in line.lower():
                header_done = True
                story.append(Spacer(1, 6))
                story.append(Paragraph(escape_xml(line), styles["OpinionBodyNoIndent"]))
                story.append(Spacer(1, 8))
                i += 1
                continue
            else:
                # Other header lines (party names etc)
                story.append(Paragraph(escape_xml(line), styles["CourtSubheader"]))
                i += 1
                continue

        # Section headings: Roman numerals, single letters, standalone numbers
        stripped = line.strip()
        if re.match(r'^[IVX]+$', stripped) or re.match(r'^[A-Z]$', stripped) or stripped == "* * *":
            story.append(Paragraph(escape_xml(stripped), styles["SectionHeading"]))
            i += 1
            continue

        # Regular paragraph — collect until next blank line
        para_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip():
            para_lines.append(lines[i].rstrip())
            i += 1

        para_text = " ".join(para_lines)
        story.append(Paragraph(escape_xml(para_text), styles["OpinionBody"]))

    doc.build(story, onFirstPage=on_each_page, onLaterPages=on_each_page)
    return out_path


def escape_xml(text):
    """Escape XML special characters for ReportLab Paragraph."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    # Preserve em-dashes and smart quotes
    return text


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_opinion_pdfs.py <case_folder>")
        print("       python3 generate_opinion_pdfs.py --all")
        sys.exit(1)

    if sys.argv[1] == "--all":
        # Find all case directories with draft files
        dirs = []
        for d in ["data/tariff-case", "data/loper-bright"]:
            if os.path.isdir(d):
                dirs.append(d)
        cases_dir = "data/cases"
        if os.path.isdir(cases_dir):
            for sub in os.listdir(cases_dir):
                full = os.path.join(cases_dir, sub)
                if os.path.isdir(full):
                    dirs.append(full)
        case_dirs = dirs
    else:
        case_dirs = [sys.argv[1].rstrip("/")]

    # Determine website output base
    website_opinions_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "scotus-website", "public", "opinions"
    )

    total_pdfs = 0
    for case_dir in case_dirs:
        if not os.path.isdir(case_dir):
            print(f"WARNING: {case_dir} not found, skipping")
            continue

        drafts = find_draft_files(case_dir)
        if not drafts:
            continue

        # Determine slug for website path
        case_info_path = os.path.join(case_dir, "case_info.txt")
        slug = os.path.basename(case_dir)

        # Try to determine slug from index.json or case_info
        index_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "scotus-website", "src", "data", "cases", "index.json"
        )
        if os.path.exists(index_path):
            with open(index_path) as f:
                index_data = json.load(f)
            # Match by docket number in case_info or directory name
            for case in index_data.get("cases", []):
                if slug in case.get("docket", "") or os.path.basename(case_dir) in case.get("docket", ""):
                    slug = case["id"]
                    break

        out_dir = os.path.join(website_opinions_dir, slug)
        os.makedirs(out_dir, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"Case: {case_dir} -> {slug}")
        print(f"{'='*60}")

        for txt_path, otype, pdf_name in drafts:
            out_path = os.path.join(out_dir, pdf_name)
            print(f"  Generating {pdf_name}...", end=" ", flush=True)
            try:
                build_opinion_pdf(txt_path, out_path, otype)
                print(f"OK ({os.path.getsize(out_path) // 1024} KB)")
                total_pdfs += 1
            except Exception as e:
                print(f"FAILED: {e}")

    print(f"\nGenerated {total_pdfs} PDFs in {website_opinions_dir}/")


if __name__ == "__main__":
    main()
