import os
import time
import requests
import fitz
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("COURTLISTENER_API_TOKEN")
print(f"Token: {token[:8]}...")

# Quick test with known citation
response = requests.post(
    "https://www.courtlistener.com/api/rest/v4/citation-lookup/",
    headers={"Authorization": f"Token {token}"},
    data={"text": "Obergefell v. Hodges (576 US 644)"},
    timeout=60,
)
print(f"Quick test status: {response.status_code}")

# Extract text from one brief
doc = fitz.open("data/tariff-case/VOS Brief.pdf")
text = ""
for page in doc:
    text += page.get_text()
doc.close()
print(f"Full text: {len(text):,} chars")

# Test increasing chunk sizes
for size in [5000, 20000, 40000, 60000]:
    chunk = text[:size]
    response = requests.post(
        "https://www.courtlistener.com/api/rest/v4/citation-lookup/",
        headers={"Authorization": f"Token {token}"},
        data={"text": chunk},
        timeout=60,
    )
    print(f"{size//1000}K chunk status: {response.status_code}")
    time.sleep(2)