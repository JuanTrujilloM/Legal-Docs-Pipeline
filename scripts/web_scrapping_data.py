import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import time
from urllib.parse import urlparse, parse_qs
import urllib3

# Desactivate warnings about insecure requests (since we're using verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define base URL and sitemap URL
BASE_URL = "https://www.suin-juriscol.gov.co"
SITEMAP_URL = f"{BASE_URL}/sitemapleyes.xml"

# Define the directory to save the downloaded HTML files
BASE_DIR = Path(__file__).resolve().parents[1]
SAVE_DIR = BASE_DIR / "data" / "Laws"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# Define headers to mimic a browser to evit potential blocking by the server
headers = {
    "User-Agent": "Mozilla/5.0"
}

print("Downloading sitemap...")

# Fetch the sitemap and extract URLs
response = requests.get(SITEMAP_URL, headers=headers, verify=False)
response.raise_for_status()

# Parse the sitemap XML and extract document URLs
soup = BeautifulSoup(response.text, "xml")
urls = [loc.text.strip() for loc in soup.find_all("loc")]

print(f"Found {len(urls)} documents.")
print("Downloading only the first 5...\n")

# Download the first 5 documents and save them as HTML files
for url in urls[:50]:

    print(f"Processing: {url}")

    try:
        # Make a GET request to the document URL with a timeout and without SSL verification
        page = requests.get(url, headers=headers, timeout=15, verify=False)
        page.raise_for_status()
        
    except Exception as e:
        print("Error opening the page:", e)
        continue

    # Extract the document ID from the URL query parameters to use as the file name
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    doc_id = query_params.get("id", ["sin_id"])[0]

    # Save the page content as an HTML file
    file_name = f"{doc_id}.html"
    file_path = SAVE_DIR / file_name

    # Write the HTML content to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(page.text)

    print(f"Saved as {file_name}\n")

    time.sleep(1)

print("Test finished.")
