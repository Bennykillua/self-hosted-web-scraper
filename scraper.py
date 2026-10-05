import random
import requests

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
]


def build_headers() -> dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

import time

RETRY_STATUS = {429, 500, 502, 503, 504}


def fetch(session: requests.Session, url: str, max_retries: int = 3) -> str | None:
    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=build_headers(), timeout=15)

            if response.status_code == 200:
                return response.text

            if response.status_code not in RETRY_STATUS:
                print(f"{url} returned {response.status_code}, not retrying")
                return None

            time.sleep(2 ** attempt)

        except requests.RequestException as error:
            print(f"{url} failed with {type(error).__name__}")
            time.sleep(2 ** attempt)

    return None

def polite_delay(base: float = 1.5, jitter: float = 1.0) -> None:
    time.sleep(base + random.uniform(0, jitter))

from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict


@dataclass
class Product:
    name: str
    price: str
    url: str


def parse_products(html: str) -> list[Product]:
    soup = BeautifulSoup(html, "lxml")
    products = []

    for card in soup.select("li.product"):
        name = card.select_one(".product-name")
        price = card.select_one(".product-price")
        link = card.select_one("a.woocommerce-LoopProduct-link")

        if not (name and price and link):
            continue

        products.append(Product(
            name=name.get_text(strip=True),
            price=price.get_text(strip=True),
            url=link["href"],
        ))

    return products

import csv

BASE_URL = "https://www.scrapingcourse.com/ecommerce/page/{}/"


def scrape(pages: int = 3) -> list[Product]:
    all_products = []

    with requests.Session() as session:
        for page in range(1, pages + 1):
            html = fetch(session, BASE_URL.format(page))

            if html is None:
                continue

            products = parse_products(html)
            print(f"page {page}: {len(products)} products")
            all_products.extend(products)
            polite_delay()

    return all_products


if __name__ == "__main__":
    products = scrape()

    with open("products.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "price", "url"])
        writer.writeheader()
        writer.writerows(asdict(p) for p in products)

    print(f"saved {len(products)} products")


from playwright.sync_api import sync_playwright


def fetch_rendered(url: str, wait_for: str, timeout: int = 30000) -> str | None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=random.choice(USER_AGENTS))

        try:
            page.goto(url, timeout=timeout)
            page.wait_for_selector(wait_for, timeout=timeout)
            return page.content()
        except Exception as error:
            print(f"{url} failed to render: {type(error).__name__}")
            return None
        finally:
            browser.close()

def parse_rendered(html: str) -> list[Product]:
    soup = BeautifulSoup(html, "lxml")
    products = []

    for card in soup.select(".product-item"):
        name = card.select_one("[data-testid=product-name]")
        price = card.select_one("[data-testid=product-price]")
        link = card.select_one("a.product-link")

        if not (name and price and link):
            continue

        products.append(Product(
            name=name.get_text(strip=True),
            price=price.get_text(strip=True),
            url=link["href"],
        ))

    return products


if __name__ == "__main__":
    url = "https://www.scrapingcourse.com/javascript-rendering"

    with requests.Session() as session:
        html = fetch(session, url)

    if html is None:
        raise RuntimeError(f"Could not fetch {url}")

    soup = BeautifulSoup(html, "lxml")

    for card in soup.select(".product-item")[:3]:
        name = card.select_one("[data-testid=product-name]")
        price = card.select_one("[data-testid=product-price]")
        link = card.select_one("a.product-link")
        print(repr(name.get_text(strip=True)), repr(price.get_text(strip=True)), repr(link["href"]))

TARGETS = [
    "https://dexscreener.com/solana",
    "https://www.sofascore.com/football",
    "https://www.g2.com/categories/crm",
]

if __name__ == "__main__":
    with requests.Session() as session:
        for url in TARGETS:
            r = session.get(url, headers=build_headers(), timeout=15)
            print(f"\n{url}")
            print("status:", r.status_code, "| bytes:", len(r.content))
            print("server:", r.headers.get("server"))
            print("cf-mitigated:", r.headers.get("cf-mitigated"))
            print("x-datadome:", r.headers.get("x-datadome"))
            print("cookies:", list(r.cookies.keys()))
            print("title:", BeautifulSoup(r.text, "lxml").title)

print("\nRate-limiting example")

RATE_LIMIT_URL = "https://api.github.com/users/Python"

if __name__ == "__main__":
    with requests.Session() as session:
        for i in range(1, 71):
            r = session.get(RATE_LIMIT_URL, headers=build_headers(), timeout=15)
            remaining = r.headers.get("x-ratelimit-remaining")

            if i == 1 or i % 10 == 0 or r.status_code != 200:
                print(f"request {i}: {r.status_code} | remaining: {remaining}")

            if r.status_code != 200:
                print("limit:", r.headers.get("x-ratelimit-limit"))
                print("reset:", r.headers.get("x-ratelimit-reset"))
                break


print("\nTesting rendered fetch with Playwright")

if __name__ == "__main__":
    for url in ["https://dexscreener.com/solana", "https://www.g2.com/categories/crm"]:
        html = fetch_rendered(url, wait_for="body")
        if html:
            soup = BeautifulSoup(html, "lxml")
            print(f"\n{url}")
            print("bytes:", len(html))
            print("title:", soup.title)