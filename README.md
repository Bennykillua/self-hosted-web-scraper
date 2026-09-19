# How to Build a Self-Hosted Web Scraper from Scratch

A Python web scraper built from scratch with Requests, BeautifulSoup, and Playwright, then tested against three protected sites to show where a self-hosted scraper stops working. Includes the same tests run through Zenrows for comparison.

## Features

- Static page scraper using Requests and BeautifulSoup with rotating user agents, full browser header sets, and exponential backoff retries
- Randomized rate limiting to avoid frequency-based blocks
- Structured extraction into dataclasses, written out to CSV
- Playwright headless browser rendering for JavaScript-populated pages
- Diagnostic tests against three protected sites showing Cloudflare, DataDome, and edge-cache rejections
- The same three targets retrieved through Zenrows Fetch with `mode=auto`

## Prerequisites

- Python 3.10 or above (tested on 3.12)
- A Zenrows API key for the final script only, available on the [free tier](https://app.zenrows.com/register)
- Chromium, installed through Playwright during setup

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Bennykillua/self-hosted-web-scraper.git
cd self-hosted-web-scraper
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the environment

```bash
# macOS and Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Install the Chromium browser

```bash
python3 -m playwright install chromium
```

This downloads roughly 280 MB of browser binaries.

## Configuration

Create a `.env` file in the project root:

```
ZENROWS_API_KEY=your_api_key
```

Only `zenrows_fetch.py` reads this. The static and Playwright scripts run without any credentials.

Get a key from the [Zenrows dashboard](https://app.zenrows.com/register). The free tier includes 5,000 credits per month.

## Project structure

```
.
├── scraper.py
├── protected_sites.py
├── zenrows_fetch.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

- `scraper_static_page.py` builds the static scraper and adds Playwright rendering
- `scraper_protected_sites.py` runs both approaches against three protected targets
- `zenrows_fetch.py` runs the same three targets through Zenrows

## How it works

The project moves through three stages, each one testing the scraper against a harder target.

```
Static HTML page
  ↓
Requests + BeautifulSoup → works
  ↓
JavaScript-rendered page
  ↓
Requests returns empty fields → Playwright renders → works
  ↓
Protected pages (Cloudflare, DataDome, Varnish)
  ↓
Requests returns 403 → Playwright times out or returns a shell
  ↓
Zenrows Fetch (mode=auto) → full content
```

The parsing logic stays the same throughout. Only the fetch layer changes between stages, which isolates what each approach can and cannot reach.

## Running the project

### Static

```bash
python3 scraper_static_page.py
```

### Rendered scraping

```bash
python3 scraper_js_render_page.py
```

### Protected site tests

```bash
python3 scraper_protected_sites.py
```

### Zenrows comparison

```bash
python3 zenrows_fetch.py
```

## Output

`scraper_static_page.py` writes `products.csv` to the project root, containing the name, price, and URL of every product scraped across three pages.

`scraper_protected_sites.py` prints the status code, response size, server header, protection headers, cookies, and page title for each target, under both Requests and Playwright. Expect 403s and empty shells.

`zenrows_fetch.py` prints the response size and page title for the same three targets. Expect full pages.

## Technologies

- Python
- Requests
- BeautifulSoup
- Playwright
- Zenrows


## Related article

This repository accompanies the Zenrows article: [How to Build a Self-Hosted Web Scraper from Scratch]()