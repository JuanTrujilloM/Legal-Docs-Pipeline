import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path
import time
from urllib.parse import urlparse, parse_qs
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

# Retry/backoff configuration to handle flaky server responses
CONNECT_TIMEOUT = 15
READ_TIMEOUT = 60
MAX_RETRIES = 6
BACKOFF_FACTOR = 1.5
SLEEP_BETWEEN_REQUESTS = 0.5
FAILED_LOG = BASE_DIR / "data" / "failed_downloads.txt"

session = requests.Session()
retry = Retry(
    total=MAX_RETRIES,
    connect=MAX_RETRIES,
    read=MAX_RETRIES,
    status=MAX_RETRIES,
    backoff_factor=BACKOFF_FACTOR,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    raise_on_status=False,
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)
session.mount("http://", adapter)

print("Downloading sitemap...")

# Fetch the sitemap and extract URLs
response = session.get(SITEMAP_URL, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), verify=False)
response.raise_for_status()

# Parse the sitemap XML and extract document URLs
soup = BeautifulSoup(response.text, "xml")
urls = [loc.text.strip() for loc in soup.find_all("loc")]

print(f"Found {len(urls)} documents.")
print("Downloading all documents...\n")

# Download all documents and save them as HTML files
for index, url in enumerate(urls, start=1):

    print(f"Processing: {url}")

    # Extract the document ID from the URL query parameters to use as the file name
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    doc_id = query_params.get("id", ["sin_id"])[0]

    # Save the page content as an HTML file
    file_name = f"{doc_id}.html"
    file_path = SAVE_DIR / file_name

    # Skip already downloaded files to allow resume
    if file_path.exists():
        print(f"[{index}/{len(urls)}] Skipping existing: {file_name}")
        continue

    try:
        # Make a GET request to the document URL with a timeout and without SSL verification
        page = session.get(
            url,
            headers=headers,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            verify=False,
        )
        if page.status_code >= 400:
            raise requests.HTTPError(f"HTTP {page.status_code}")

    except Exception as e:
        print("Error opening the page:", e)
        with open(FAILED_LOG, "a", encoding="utf-8") as log_file:
            log_file.write(f"{url}\t{e}\n")
        continue

    # Write the HTML content to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(page.text)

    print(f"[{index}/{len(urls)}] Saved as {file_name}\n")

    time.sleep(SLEEP_BETWEEN_REQUESTS)

print("Test finished.")
