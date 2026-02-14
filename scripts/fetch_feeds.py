"""
fetch_feeds.py — Fetch and normalize articles from RSS feeds.

Pulls recent articles from all configured sources, normalizes dates,
strips HTML from summaries, and returns structured article data.
"""

import re
from datetime import datetime, timezone, timedelta

import feedparser

from sources import SOURCES


def clean_html(text: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:500]


def parse_date(entry) -> datetime | None:
    """Extract a timezone-aware datetime from a feed entry."""
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=timezone.utc)
            except (ValueError, TypeError):
                continue
    return None


def fetch_all_articles(max_age_hours: int = 48) -> list[dict]:
    """
    Fetch articles from all RSS sources.

    Args:
        max_age_hours: Only include articles published within this window.

    Returns:
        List of article dicts with keys:
            source, bias, title, link, summary, published
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    articles = []

    for bias, sources in SOURCES.items():
        for source in sources:
            try:
                feed = feedparser.parse(source["rss"])
                count = 0
                for entry in feed.entries[:20]:
                    title = entry.get("title", "").strip()
                    link = entry.get("link", "").strip()
                    if not title or not link:
                        continue

                    pub_date = parse_date(entry)

                    # If we have a date, filter by recency
                    if pub_date and pub_date < cutoff:
                        continue

                    summary = clean_html(entry.get("summary", ""))

                    articles.append(
                        {
                            "source": source["name"],
                            "bias": bias,
                            "title": title,
                            "link": link,
                            "summary": summary,
                            "published": pub_date.isoformat() if pub_date else None,
                        }
                    )
                    count += 1

                print(f"  ✓ {source['name']}: {count} articles")

            except Exception as e:
                print(f"  ✗ {source['name']}: {e}")

    print(f"\nTotal articles fetched: {len(articles)}")
    return articles


if __name__ == "__main__":
    import json

    print("Fetching RSS feeds...\n")
    articles = fetch_all_articles()

    # Summary by bias
    for bias in ("left", "center", "right"):
        n = sum(1 for a in articles if a["bias"] == bias)
        print(f"  {bias.upper()}: {n} articles")

    with open("raw_articles.json", "w") as f:
        json.dump(articles, f, indent=2, default=str)
    print("\nSaved to raw_articles.json")
