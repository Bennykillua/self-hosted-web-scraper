# How to Build a Self-Hosted Web Scraper from Scratch

A Python web scraper built from scratch with Requests, BeautifulSoup, and Playwright, then tested against protected sites and a documented rate limit to show where a self-hosted scraper stops working. Includes the same targets retrieved through Zenrows for comparison.

## Features

- Static page scraper using Requests and BeautifulSoup with rotating user agents, full browser header sets, and exponential backoff retries
- Randomized delays between requests to avoid frequency-based blocks
- Structured extraction into dataclasses, written out to CSV
- Playwright headless browser rendering for pages that populate their content with JavaScript
- Diagnostic tests against three protected sites, showing Cloudflare challenge, DataDome, and edge-cache responses
- A rate-limit test against GitHub's documented 60 requests per hour for unauthenticated clients
- The same protected targets retrieved through Zenrows Fetch with `mode=auto`

## Prerequisites

- Python 3.10 or above (tested on 3.12)
- A Zenrows API key for `zenrows_fetch.py` only, available on the [free tier](https://app.zenrows.com/register)
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

Only `zenrows_fetch.py` reads this. `scraper.py` runs without any credentials.

Get a key from the [Zenrows dashboard](https://app.zenrows.com/register). The free tier includes 5,000 credits per month.

## Project structure

```
.
├── scraper.py
├── zenrows_fetch.py
├── products.csv
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

- `scraper.py` is the full build: static scraping, Playwright rendering, protected site tests, and the rate-limit test
- `zenrows_fetch.py` retrieves the same protected targets through Zenrows Fetch
- `products.csv` is sample output from the static scraper

## How it works

The project moves through four stages, each one testing the scraper against a harder target.

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
Rate-limited endpoint
  ↓
59 requests succeed, the 60th returns 403
  ↓
Zenrows Fetch (mode=auto) → full content on the protected targets
```

The parsing logic stays the same throughout. Only the fetch layer changes between stages, which isolates what each approach can and cannot reach.

## Running the project

### The scraper and all its tests

```bash
python3 scraper.py
```

### The Zenrows comparison

```bash
python3 zenrows_fetch.py
```

## Output

`scraper.py` writes `products.csv` to the project root with the name, price, and URL of every product scraped across three pages, then prints the results of the rendered, protected site, and rate-limit tests to the terminal. Expect 403s, empty shells, and a rate-limit cutoff.

`zenrows_fetch.py` prints the response size and page title for each protected target.

Responses from live sites vary by IP, session, time, and each site's configuration, so your output will not match the article exactly.

## Technologies

- Python
- Requests
- BeautifulSoup
- Playwright
- Zenrows

## Related article

This repository accompanies the Zenrows article: [How to Build a Self-Hosted Web Scraper from Scratch](
https://www.zenrows.com/blog/how-to-build-a-self-hosted-web-scraper-from-scratch)