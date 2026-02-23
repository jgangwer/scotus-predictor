"""
prep_scdb.py — SCDB Data Preparation for SCOTUS Predictor

Produces a compact, token-efficient summary of voting patterns optimized
for Claude API consumption (not human reading).

SCDB variable codes (scdb.la.psu.edu/online-codebook):
  majority: 1=dissent side, 2=majority side
  vote: 1=majority/plurality, 2=dissent, 3=regular concurrence,
        4=special concurrence (concurrence in judgment), 5=judgment of Court
  opinion: 1=no opinion, 2=wrote opinion, 3=co-authored
  direction: 1=conservative, 2=liberal, 3=unspecifiable
  firstAgreement/secondAgreement: justice ID of opinion they joined
  majOpinWriter: justice ID of majority opinion author (case-centered data)

Output format per justice per case:
  Name:VT  where V=vote type, T=modifier
  Vote types: M=majority, D=dissent, C=concurrence, CJ=conc-in-judgment, J=judgment
  Modifiers: *=authored majority, +=wrote opinion, >Name=joined Name's opinion

Example: Roberts:M* Kagan:M Kavanaugh:C+ Thomas:D+ Gorsuch:D>Thomas

Output: data/scdb_voting_data.txt
"""

import pandas as pd
import os

# --- Config ---
JUSTICE_CSV = "data/SCDB_2025_01_justiceCentered_Citation.csv"
CASE_CSV = "data/SCDB_2025_01_caseCentered_Citation.csv"
OUTPUT_PATH = "data/scdb_voting_data.txt"

CURRENT_JUSTICES = [
    "JGRoberts", "CThomas", "SAAlito", "SSotomayor",
    "EKagan", "NMGorsuch", "BMKavanaugh", "ACBarrett", "KBJackson"
]

DISPLAY = {
    "JGRoberts": "Roberts", "CThomas": "Thomas", "SAAlito": "Alito",
    "SSotomayor": "Sotomayor", "EKagan": "Kagan", "NMGorsuch": "Gorsuch",
    "BMKavanaugh": "Kavanaugh", "ACBarrett": "Barrett", "KBJackson": "Jackson",
}

# SCDB numeric justice IDs for current justices (for firstAgreement/secondAgreement)
JUSTICE_IDS = {
    108: "Thomas", 111: "Roberts", 112: "Alito", 113: "Sotomayor",
    114: "Kagan", 115: "Gorsuch", 116: "Kavanaugh", 117: "Barrett", 118: "Jackson",
}

RELEVANT_ISSUE_AREAS = [8, 9, 10]

ISSUE_SHORT = {
    1: "CrimPro", 2: "CivRts", 3: "1stAm", 4: "DueProc", 5: "Privacy",
    6: "Attorneys", 7: "Unions", 8: "EconAct", 9: "JudPwr", 10: "Federalism",
    11: "Interstate", 12: "FedTax", 13: "Misc", 14: "Private",
}

DIR_SHORT = {1: "con", 2: "lib", 3: "unk"}


def load_data():
    print(f"Loading {JUSTICE_CSV}...")
    jdf = pd.read_csv(JUSTICE_CSV, encoding="latin-1", low_memory=False)
    print(f"  {len(jdf):,} justice-level rows")

    print(f"Loading {CASE_CSV}...")
    cdf = pd.read_csv(CASE_CSV, encoding="latin-1", low_memory=False)
    print(f"  {len(cdf):,} case-level rows")

    return jdf, cdf


def build_justice_id_map(jdf):
    """Map all SCDB numeric justice IDs -> justiceName strings."""
    id_map = {}
    for _, row in jdf[["justice", "justiceName"]].drop_duplicates().iterrows():
        if pd.notna(row["justice"]):
            id_map[int(row["justice"])] = row["justiceName"]
    return id_map


def get_agreement_name(justice_id):
    """Convert a firstAgreement/secondAgreement justice ID to a display name."""
    if pd.isna(justice_id):
        return None
    jid = int(justice_id)
    return JUSTICE_IDS.get(jid, None)


def format_justice_vote(row, is_maj_author, all_justice_id_map):
    """
    Format one justice's vote as a compact token.
    Returns: "Name:CODE" e.g. "Roberts:M*" or "Gorsuch:D>Thomas"
    """
    name = DISPLAY.get(row["justiceName"], row["justiceName"])
    vote = int(row["vote"]) if pd.notna(row["vote"]) else 0
    wrote = int(row["opinion"]) if pd.notna(row["opinion"]) else 0
    wrote = wrote in [2, 3]

    # Base vote code
    if vote == 1:
        base = "M"
    elif vote == 2:
        base = "D"
    elif vote == 3:
        base = "C"
    elif vote == 4:
        base = "CJ"
    elif vote == 5:
        base = "J"
    else:
        base = "?"

    # Modifier
    if is_maj_author:
        modifier = "*"
    elif wrote:
        modifier = "+"
    else:
        # Check who they joined via firstAgreement/secondAgreement
        joined = get_agreement_name(row.get("firstAgreement"))
        if joined and joined != name:
            modifier = f">{joined}"
        else:
            joined2 = get_agreement_name(row.get("secondAgreement"))
            if joined2 and joined2 != name:
                modifier = f">{joined2}"
            else:
                modifier = ""

    return f"{name}:{base}{modifier}"


def find_current_natural_court_cases(jdf):
    case_justices = jdf.groupby("caseId")["justiceName"].apply(set)
    current_set = set(CURRENT_JUSTICES)
    qualifying = case_justices[case_justices.apply(lambda s: current_set.issubset(s))]
    return set(qualifying.index)


def find_relevant_issue_area_cases(cdf, min_term=1991):
    mask = (cdf["issueArea"].isin(RELEVANT_ISSUE_AREAS)) & (cdf["term"] >= min_term)
    return set(cdf[mask]["caseId"])


def format_case_line(case_row, case_votes, maj_author_name, all_justice_id_map):
    """Format a single case as one compact line."""
    term = int(case_row["term"])
    name = case_row["caseName"]
    issue = int(case_row["issueArea"]) if pd.notna(case_row["issueArea"]) else 0
    issue_str = ISSUE_SHORT.get(issue, f"A{issue}")
    maj = int(case_row["majVotes"]) if pd.notna(case_row["majVotes"]) else "?"
    mins = int(case_row["minVotes"]) if pd.notna(case_row["minVotes"]) else "?"
    direction = DIR_SHORT.get(
        int(case_row["decisionDirection"]) if pd.notna(case_row["decisionDirection"]) else 0, "?"
    )

    header = f"[{term}] {name} {maj}-{mins} {direction} [{issue_str}]"

    vote_tokens = []
    for _, vrow in case_votes.sort_values("justiceName").iterrows():
        is_author = (vrow["justiceName"] == maj_author_name)
        token = format_justice_vote(vrow, is_author, all_justice_id_map)
        vote_tokens.append(token)

    return f"{header} {' '.join(vote_tokens)}"


def build_output(jdf, cdf, natural_court_cases, issue_area_cases, all_justice_id_map):
    lines = []

    lines.append("SCOTUS VOTING DATA FOR PREDICTION PIPELINE")
    lines.append("=" * 60)
    lines.append("Format: Name:VT where V=vote T=modifier")
    lines.append("Votes: M=majority D=dissent C=concurrence CJ=conc-in-judgment J=judgment")
    lines.append("Modifiers: *=authored majority +=wrote opinion >Name=joined Name's opinion")
    lines.append("Direction: con=conservative lib=liberal unk=unspecifiable")
    lines.append("")

    # === SECTION 1: Current natural court ===
    nc_case_ids = sorted(natural_court_cases)
    nc_jdf = jdf[jdf["caseId"].isin(natural_court_cases) & jdf["justiceName"].isin(CURRENT_JUSTICES)]
    nc_cdf = cdf[cdf["caseId"].isin(natural_court_cases)]

    lines.append(f"SEC1: CURRENT NATURAL COURT ({len(nc_case_ids)} cases)")
    lines.append("-" * 60)

    for case_id in nc_case_ids:
        case_row = nc_cdf[nc_cdf["caseId"] == case_id].iloc[0]
        maj_writer_id = case_row["majOpinWriter"]
        maj_author_name = all_justice_id_map.get(int(maj_writer_id), None) if pd.notna(maj_writer_id) else None
        case_votes = nc_jdf[nc_jdf["caseId"] == case_id]
        line = format_case_line(case_row, case_votes, maj_author_name, all_justice_id_map)
        lines.append(line)

    # === SECTION 2: Relevant issue areas (not in natural court) ===
    ia_only = issue_area_cases - natural_court_cases
    ia_case_ids = sorted(ia_only)
    ia_jdf = jdf[jdf["caseId"].isin(ia_only) & jdf["justiceName"].isin(CURRENT_JUSTICES)]
    ia_cdf = cdf[cdf["caseId"].isin(ia_only)]

    sec2_lines = []
    for case_id in ia_case_ids:
        case_rows = ia_cdf[ia_cdf["caseId"] == case_id]
        if len(case_rows) == 0:
            continue
        case_row = case_rows.iloc[0]
        case_votes = ia_jdf[ia_jdf["caseId"] == case_id]
        if len(case_votes) < 3:
            continue
        maj_writer_id = case_row["majOpinWriter"]
        maj_author_name = all_justice_id_map.get(int(maj_writer_id), None) if pd.notna(maj_writer_id) else None
        line = format_case_line(case_row, case_votes, maj_author_name, all_justice_id_map)
        sec2_lines.append(line)

    lines.append("")
    lines.append(f"SEC2: RELEVANT ISSUE AREAS SINCE 1991 ({len(sec2_lines)} cases, 3+ current justices)")
    lines.append("Issues: EconAct, JudPwr, Federalism")
    lines.append("-" * 60)
    lines.extend(sec2_lines)

    # === SECTION 3: Pairwise agreement ===
    lines.append("")
    lines.append("SEC3: PAIRWISE AGREEMENT (current natural court)")
    lines.append("-" * 60)

    agreement = {}
    for j1 in CURRENT_JUSTICES:
        for j2 in CURRENT_JUSTICES:
            if j1 >= j2:
                continue
            agree = total = 0
            for case_id in nc_case_ids:
                v1 = nc_jdf[(nc_jdf["caseId"] == case_id) & (nc_jdf["justiceName"] == j1)]
                v2 = nc_jdf[(nc_jdf["caseId"] == case_id) & (nc_jdf["justiceName"] == j2)]
                if len(v1) == 0 or len(v2) == 0:
                    continue
                m1 = v1.iloc[0]["majority"]
                m2 = v2.iloc[0]["majority"]
                if pd.notna(m1) and pd.notna(m2):
                    total += 1
                    if m1 == m2:
                        agree += 1
            if total > 0:
                agreement[(j1, j2)] = (agree / total * 100, agree, total)

    for (j1, j2), (pct, agree, total) in sorted(agreement.items(), key=lambda x: -x[1][0]):
        n1 = DISPLAY[j1]
        n2 = DISPLAY[j2]
        lines.append(f"{n1}-{n2} {pct:.0f}% ({agree}/{total})")

    # === SECTION 4: Per-justice stats ===
    lines.append("")
    lines.append("SEC4: PER-JUSTICE STATS (current natural court)")
    lines.append("-" * 60)

    for jname_scdb in CURRENT_JUSTICES:
        jname = DISPLAY[jname_scdb]
        jv = nc_jdf[nc_jdf["justiceName"] == jname_scdb]
        total = len(jv)
        if total == 0:
            continue
        in_maj = len(jv[jv["majority"] == 2])
        in_dis = len(jv[jv["majority"] == 1])
        wrote = len(jv[jv["opinion"].isin([2, 3])])
        con = len(jv[jv["direction"] == 1])
        lib = len(jv[jv["direction"] == 2])
        dir_total = con + lib
        lines.append(
            f"{jname}: {total}cases maj:{in_maj}({in_maj*100//total}%) "
            f"dis:{in_dis}({in_dis*100//total}%) wrote:{wrote} "
            f"con:{con}({con*100//dir_total if dir_total else 0}%) "
            f"lib:{lib}({lib*100//dir_total if dir_total else 0}%)"
        )

    return "\n".join(lines)


def main():
    if not os.path.exists(JUSTICE_CSV):
        print(f"ERROR: {JUSTICE_CSV} not found.")
        return
    if not os.path.exists(CASE_CSV):
        print(f"ERROR: {CASE_CSV} not found.")
        return

    jdf, cdf = load_data()

    print("\nBuilding justice ID map...")
    all_justice_id_map = build_justice_id_map(jdf)
    print(f"  Mapped {len(all_justice_id_map)} justice IDs")

    print("Finding current natural court cases...")
    nc_cases = find_current_natural_court_cases(jdf)
    print(f"  Found {len(nc_cases)} cases")

    print("Finding relevant issue area cases since 1991...")
    ia_cases = find_relevant_issue_area_cases(cdf, min_term=1991)
    print(f"  Found {len(ia_cases)} cases")

    print("\nFormatting output...")
    output = build_output(jdf, cdf, nc_cases, ia_cases, all_justice_id_map)

    with open(OUTPUT_PATH, "w") as f:
        f.write(output)

    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    char_count = len(output)
    line_count = output.count("\n")

    print(f"\nSaved to {OUTPUT_PATH}")
    print(f"  {line_count:,} lines, {char_count:,} chars ({size_kb:.0f} KB)")
    print(f"  Fits in Claude prompt: {'YES' if char_count < 200000 else 'TRIM NEEDED'}")


if __name__ == "__main__":
    main()