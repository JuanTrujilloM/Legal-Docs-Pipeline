# Legal-Docs-Pipeline

## Documentation

Pipeline to download legal documents from the SUIN sitemap and convert them to clean TXT.

## Requirements
- Python 3.9+
- Dependencies: see requirements.txt

Quick install:
```bash
pip install -r requirements.txt
```

## Usage

### 1) Download HTMLs (web scraping)
```bash
python3 Scripts/ProcessHTMLs/webScrappingData.py --output data/Laws
```

Options:
- --sitemap: sitemap URL (default: https://www.suin-juriscol.gov.co/sitemapleyes.xml)
- --sleep: delay between requests (default: 0.5)
- --max-retries: retry attempts (default: 6)
- --backoff: backoff factor (default: 1.5)
- --failed-log: file to log failures

Example:
```bash
python3 Scripts/ProcessHTMLs/webScrappingData.py \
	--sitemap https://www.suin-juriscol.gov.co/sitemapleyes.xml \
	--output data/Laws \
	--sleep 0.5 \
	--max-retries 6 \
	--backoff 1.5 \
	--failed-log data/failed_downloads.txt
```

### 2) Preprocess HTMLs to TXT
```bash
python3 Scripts/ProcessHTMLs/preprocessHTMLs.py --input data/Laws --output dataCleaned/Laws
```

## Output structure
- HTMLs: data/Laws/*.html
- Clean TXT: dataCleaned/Laws/*.txt

## Notes
- If you re-run the scraper, already-downloaded files are skipped automatically.
- The preprocessing removes UI tags and normalizes text.
