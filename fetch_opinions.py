"""
fetch_opinions.py

Extracts case citations from brief PDFs, looks them up on CourtListener,
and downloads the full opinion text for every cited case.

Usage:
    python fetch_opinions.py data/tariff-case/

This will:
1. Read all PDFs in the specified folder
2. Extract text and send to CourtListener's citation lookup API
3. Download full opinion text for every matched citation
4. Save to data/opinions/{case_name}.txt
"""

import os
import sys
import json
import time
import re
import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, ".env"), override=True)

COURTLISTENER_TOKEN = os.getenv("COURTLISTENER_API_TOKEN")
if not COURTLISTENER_TOKEN:
    print("ERROR: Set COURTLISTENER_API_TOKEN in your .env file")
    print("Get your token at: https://www.courtlistener.com/profile/")
    sys.exit(1)

# Sanity check: confirm token loaded
print(f"Token loaded: {COURTLISTENER_TOKEN[:8]}...")

HEADERS = {
    "Authorization": f"Token {COURTLISTENER_TOKEN}",
}

CITATION_LOOKUP_URL = "https://www.courtlistener.com/api/rest/v4/citation-lookup/"
CLUSTER_URL = "https://www.courtlistener.com/api/rest/v4/clusters/{cluster_id}/"
OPINION_URL = "https://www.courtlistener.com/api/rest/v4/opinions/{opinion_id}/"

# Rate limiting: CourtListener allows 5,000 queries per hour for authenticated users
REQUEST_DELAY = 30.0  # seconds between API calls

# Retry settings for rate limit (429) errors
MAX_RETRIES = 3
RETRY_BACKOFF = 10  # seconds, doubles each retry

OUTPUT_DIR = Path("data/opinions")


def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def chunk_text(text, max_chars=20000):
    """Split text into chunks that fit the citation lookup API limit (64K chars).
    We use 60K to leave some margin."""
    chunks = []
    while len(text) > max_chars:
        # Try to split at a paragraph break
        split_point = text.rfind("\n\n", 0, max_chars)
        if split_point == -1:
            split_point = text.rfind("\n", 0, max_chars)
        if split_point == -1:
            split_point = max_chars
        chunks.append(text[:split_point])
        text = text[split_point:]
    if text.strip():
        chunks.append(text)
    return chunks


def api_request(method, url, retries=MAX_RETRIES, **kwargs):
    """Make an API request with retry logic for rate limiting."""
    kwargs.setdefault("headers", HEADERS)
    kwargs.setdefault("timeout", 60)

    for attempt in range(retries + 1):
        try:
            if method == "GET":
                response = requests.get(url, **kwargs)
            else:
                response = requests.post(url, **kwargs)

            if response.status_code == 429:
                wait = RETRY_BACKOFF * (2 ** attempt)
                print(f"    Rate limited (429). Waiting {wait}s before retry {attempt + 1}/{retries}...")
                time.sleep(wait)
                continue

            if response.status_code == 403 and attempt < retries:
                wait = RETRY_BACKOFF * (2 ** attempt)
                print(f"    Forbidden (403). Possibly throttled. Waiting {wait}s before retry {attempt + 1}/{retries}...")
                time.sleep(wait)
                continue

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            if attempt < retries:
                wait = RETRY_BACKOFF * (2 ** attempt)
                print(f"    Request failed: {e}. Waiting {wait}s before retry {attempt + 1}/{retries}...")
                time.sleep(wait)
            else:
                raise

    return None


def lookup_citations(text):
    """Send text to CourtListener citation lookup API.
    Returns list of citation matches."""
    all_citations = []
    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks):
        if len(chunks) > 1:
            print(f"    Processing chunk {i+1}/{len(chunks)}...")

        try:
            response = api_request(
                "POST",
                CITATION_LOOKUP_URL,
                data={"text": chunk},
            )
            if response:
                citations = response.json()
                all_citations.extend(citations)
        except requests.exceptions.RequestException as e:
            print(f"    WARNING: Citation lookup failed for chunk {i+1}: {e}")

        time.sleep(REQUEST_DELAY)

    return all_citations


def extract_cluster_ids(citations):
    """Extract unique cluster IDs and case names from citation lookup results.
    Keeps all courts — not just SCOTUS."""
    clusters = {}  # cluster_id -> case info

    for cite in citations:
        if cite.get("status") != 200:
            continue

        for cluster in cite.get("clusters", []):
            cluster_id = cluster.get("id")
            if not cluster_id:
                continue

            if cluster_id not in clusters:
                case_name = cluster.get("case_name", "Unknown")
                date_filed = cluster.get("date_filed", "")
                court = cluster.get("court", "")
                citation_string = cite.get("normalized_citations", [cite.get("citation", "")])
                if isinstance(citation_string, list):
                    citation_string = citation_string[0] if citation_string else ""

                clusters[cluster_id] = {
                    "case_name": case_name,
                    "date_filed": date_filed,
                    "citation": citation_string,
                    "court": str(court),
                }

    return clusters


def fetch_cluster_opinions(cluster_id):
    """Fetch all opinions (majority, concurrence, dissent) for a cluster."""
    url = CLUSTER_URL.format(cluster_id=cluster_id)

    try:
        response = api_request("GET", url, timeout=30)
        if not response:
            return [], None
        cluster_data = response.json()

        # The cluster contains URLs to individual opinions
        opinion_urls = cluster_data.get("sub_opinions", [])
        return opinion_urls, cluster_data

    except requests.exceptions.RequestException as e:
        print(f"    WARNING: Failed to fetch cluster {cluster_id}: {e}")
        return [], None


def fetch_opinion_text(opinion_url):
    """Fetch the full text of a single opinion."""
    try:
        response = api_request("GET", opinion_url, timeout=30)
        if not response:
            return None
        data = response.json()

        # Opinion text can be in several fields, in order of preference
        text = (
            data.get("plain_text") or
            data.get("html_with_citations") or
            data.get("html") or
            data.get("html_columbia") or
            data.get("html_lawbox") or
            data.get("html_anon_2020") or
            ""
        )

        # Strip HTML tags if we got HTML
        if text and "<" in text:
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\s+', ' ', text).strip()

        opinion_type = data.get("type", "unknown")
        author_str = data.get("author_str", "")
        author_url = data.get("author", "")

        return {
            "text": text,
            "type": opinion_type,
            "author_str": author_str,
            "author_url": author_url,
        }

    except requests.exceptions.RequestException as e:
        print(f"    WARNING: Failed to fetch opinion: {e}")
        return None


def sanitize_filename(name):
    """Make a string safe for use as a filename."""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.replace(' ', '_')
    name = name[:100]  # Truncate long names
    return name


def save_opinion(case_info, opinions, output_dir):
    """Save all opinions for a case to a single text file."""
    case_name = case_info["case_name"]
    filename = sanitize_filename(case_name) + ".txt"
    filepath = output_dir / filename

    # Skip if already downloaded
    if filepath.exists():
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Case: {case_name}\n")
        f.write(f"Citation: {case_info['citation']}\n")
        f.write(f"Court: {case_info.get('court', '')}\n")
        f.write(f"Date: {case_info['date_filed']}\n")
        f.write(f"{'='*80}\n\n")

        # Opinion type mapping
        type_names = {
            "010combined": "Combined Opinion",
            "015unamimous": "Unanimous Opinion",
            "020lead": "Lead Opinion",
            "025plurality": "Plurality Opinion",
            "030concurrence": "Concurrence",
            "035concurrenceinpart": "Concurrence in Part",
            "040dissent": "Dissent",
            "050addendum": "Addendum",
            "060remittitur": "Remittitur",
            "070rehearing": "Rehearing",
            "080onthemerits": "On the Merits",
            "090onmotiontostrike": "On Motion to Strike",
        }

        for opinion in opinions:
            if not opinion or not opinion.get("text"):
                continue

            op_type = type_names.get(opinion["type"], opinion["type"])
            author = opinion.get("author_str", "Unknown")

            f.write(f"--- {op_type} ---\n")
            if author:
                f.write(f"Author: {author}\n")
            f.write(f"\n{opinion['text']}\n\n")
            f.write(f"{'='*80}\n\n")

    return True


def process_briefs(briefs_dir):
    """Main pipeline: extract citations from briefs, download opinions."""
    briefs_dir = Path(briefs_dir)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Find all PDFs
    pdfs = list(briefs_dir.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {briefs_dir}")
        return

    print(f"Found {len(pdfs)} PDFs in {briefs_dir}\n")

    # Step 2: Extract citations from all briefs
    all_clusters = {}

    for pdf_path in pdfs:
        print(f"Processing: {pdf_path.name}")

        # Extract text
        text = extract_text_from_pdf(pdf_path)
        print(f"  Extracted {len(text):,} characters")

        # Look up citations
        citations = lookup_citations(text)
        print(f"  Found {len(citations)} citations")

        # Extract cluster IDs (all courts)
        clusters = extract_cluster_ids(citations)
        print(f"  Matched {len(clusters)} opinions")

        # Merge into master list
        for cid, info in clusters.items():
            if cid not in all_clusters:
                all_clusters[cid] = info

    print(f"\n{'='*60}")
    print(f"Total unique opinions cited: {len(all_clusters)}")
    print(f"{'='*60}\n")

    # Save the citation index for reference
    index_path = OUTPUT_DIR / "_citation_index.json"
    with open(index_path, "w") as f:
        json.dump(
            {str(k): v for k, v in all_clusters.items()},
            f, indent=2
        )
    print(f"Citation index saved to {index_path}\n")

    # Step 3: Download full opinions
    downloaded = 0
    skipped = 0
    failed = 0

    for i, (cluster_id, case_info) in enumerate(all_clusters.items()):
        case_name = case_info["case_name"]
        print(f"[{i+1}/{len(all_clusters)}] {case_name} ({case_info['citation']})")

        # Check if already downloaded
        filename = sanitize_filename(case_name) + ".txt"
        if (OUTPUT_DIR / filename).exists():
            print(f"  Already downloaded, skipping")
            skipped += 1
            continue

        # Fetch the cluster to get opinion URLs
        opinion_urls, cluster_data = fetch_cluster_opinions(cluster_id)
        time.sleep(REQUEST_DELAY)

        if not opinion_urls:
            print(f"  No opinions found in cluster")
            failed += 1
            continue

        # Fetch each opinion's text
        opinions = []
        for op_url in opinion_urls:
            opinion = fetch_opinion_text(op_url)
            if opinion:
                opinions.append(opinion)
            time.sleep(REQUEST_DELAY)

        # Save
        if opinions:
            saved = save_opinion(case_info, opinions, OUTPUT_DIR)
            if saved:
                total_chars = sum(len(o.get("text", "")) for o in opinions)
                print(f"  Saved {len(opinions)} opinion(s), {total_chars:,} chars total")
                downloaded += 1
            else:
                skipped += 1
        else:
            print(f"  No opinion text available")
            failed += 1

    print(f"\n{'='*60}")
    print(f"DONE")
    print(f"  Downloaded: {downloaded}")
    print(f"  Skipped (already had): {skipped}")
    print(f"  Failed: {failed}")
    print(f"  Opinions saved to: {OUTPUT_DIR}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_opinions.py <path_to_briefs_folder>")
        print("Example: python fetch_opinions.py data/tariff-case/")
        sys.exit(1)

    process_briefs(sys.argv[1])