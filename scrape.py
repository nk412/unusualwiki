#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests",
#   "beautifulsoup4",
# ]
# ///
"""Scrape Wikipedia's list of unusual articles and merge into wiki.json.

Merge policy: union by URL. Existing entries win on collision, preserving any
hand-edited descriptions. Entries that were in wiki.json but are no longer on
Wikipedia's list are kept.
"""

import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://en.wikipedia.org/wiki/Wikipedia:Unusual_articles"
WIKI_ROOT = "https://en.wikipedia.org"
OUTPUT = Path(__file__).parent / "wiki.json"
WHITESPACE = re.compile(r"\s+")


def scrape() -> list[dict]:
    r = requests.get(SOURCE_URL, headers={"User-Agent": "unusualwiki-scraper/1.0"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    seen: set[str] = set()
    out: list[dict] = []
    for table in soup.find_all("table", class_="wikitable"):
        for row in table.find_all("tr"):
            # Find the td that contains a <b><a>...</a></b> — the title cell.
            # Some rows lead with a <th> (country flag), so don't assume cells[0].
            title_cell = None
            for td in row.find_all("td"):
                bold = td.find("b")
                if bold and bold.find("a"):
                    title_cell = td
                    break
            if title_cell is None:
                continue

            # Description sits in the next <td> sibling. Rows without one
            # (e.g. title-only stubs) are skipped.
            desc_cell = title_cell.find_next_sibling("td")
            if desc_cell is None:
                continue

            link = title_cell.find("b").find("a")
            href = link.get("href", "")
            if not href.startswith("/wiki/"):
                continue

            title = WHITESPACE.sub(" ", link.get_text()).strip()
            desc = WHITESPACE.sub(" ", desc_cell.get_text()).strip()
            url = WIKI_ROOT + href

            if not title or not desc or url in seen:
                continue
            seen.add(url)
            out.append({"desc": desc, "title": title, "url": url})
    return out


def merge(fresh: list[dict], existing: list[dict]) -> list[dict]:
    by_url: dict[str, dict] = {a["url"]: a for a in fresh}
    for a in existing:
        by_url[a["url"]] = a  # existing wins on collision
    # Sort by title for stable diffs.
    return sorted(by_url.values(), key=lambda a: a["title"].lower())


def main() -> int:
    existing: list[dict] = []
    if OUTPUT.exists():
        existing = json.loads(OUTPUT.read_text())["articles"]

    fresh = scrape()
    if not fresh:
        print("ERROR: scraper returned 0 articles — aborting without writing.", file=sys.stderr)
        return 1

    existing_urls = {a["url"] for a in existing}
    fresh_urls = {a["url"] for a in fresh}
    added = fresh_urls - existing_urls
    only_existing = existing_urls - fresh_urls

    merged = merge(fresh, existing)

    print(f"fresh from wikipedia: {len(fresh)}")
    print(f"existing on disk:     {len(existing)}")
    print(f"newly added:          {len(added)}")
    print(f"only in existing:     {len(only_existing)} (kept)")
    print(f"merged total:         {len(merged)}")

    OUTPUT.write_text(
        json.dumps({"articles": merged}, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
