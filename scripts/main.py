#!/usr/bin/env python3
"""
main.py — The Daily Lens pipeline orchestrator.

Runs the complete daily digest pipeline:
  1. Fetch RSS feeds from all sources
  2. Cluster articles into topics
  3. Generate balanced narratives via Claude API
  4. Render the HTML dashboard
  5. Write index.html for GitHub Pages

Usage:
    python main.py                  # Full pipeline
    python main.py --skip-api       # Skip Claude API (use fallback narratives)
    python main.py --output ./docs  # Custom output directory
"""

import argparse
import json
import os
import sys
from pathlib import Path

from fetch_feeds import fetch_all_articles
from cluster_topics import cluster_articles, prepare_topics_for_digest
from generate_narratives import generate_all_narratives
from render_html import render_page


def run_pipeline(skip_api: bool = False, output_dir: str = ".") -> bool:
    """
    Run the complete Daily Lens pipeline.

    Args:
        skip_api: If True, skip Claude API calls and use fallback narratives.
        output_dir: Directory to write index.html to.

    Returns:
        True if successful, False otherwise.
    """
    print("=" * 60)
    print("  The Daily Lens — Daily Digest Pipeline")
    print("=" * 60)

    # ── Step 1: Fetch RSS feeds ──
    print("\n[1/4] Fetching RSS feeds...")
    articles = fetch_all_articles(max_age_hours=48)

    if not articles:
        print("\n⚠ No articles fetched. Check RSS feeds and network.")
        print("  Trying with extended time window (72h)...")
        articles = fetch_all_articles(max_age_hours=72)

    if not articles:
        print("\n✗ No articles available. Aborting.")
        return False

    print(f"\n  Total: {len(articles)} articles")
    for bias in ("left", "center", "right"):
        n = sum(1 for a in articles if a["bias"] == bias)
        print(f"    {bias}: {n}")

    # ── Step 2: Cluster into topics ──
    print("\n[2/4] Clustering articles into topics...")
    topics = cluster_articles(articles)

    if not topics:
        print("\n✗ No topics found. Not enough article overlap.")
        return False

    print(f"\n  Found {len(topics)} topic clusters")
    for t in topics[:8]:
        print(
            f"    [{t['bias_coverage']}/3] "
            f"{t['label']} ({t['article_count']} articles)"
        )

    digest = prepare_topics_for_digest(topics, max_topics=5)
    print(f"\n  Selected top {len(digest)} topics for digest")

    # ── Step 3: Generate narratives ──
    print("\n[3/4] Generating narratives...")

    if skip_api or not os.environ.get("ANTHROPIC_API_KEY"):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("  ⚠ ANTHROPIC_API_KEY not set")
        print("  Using fallback narratives (no API calls)")
        for topic in digest:
            topic["generated_title"] = topic["topic_label"]
            topic["generated_narrative"] = _build_fallback(topic)
    else:
        digest = generate_all_narratives(digest)

    # ── Step 4: Render HTML ──
    print("\n[4/4] Rendering HTML dashboard...")
    html_content = render_page(digest)

    output_path = Path(output_dir) / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")

    print(f"\n  ✓ Written to {output_path}")
    print(f"  ✓ File size: {len(html_content):,} bytes")

    # Also save the digest data as JSON for debugging
    debug_path = Path(output_dir) / "digest_data.json"
    debug_data = []
    for topic in digest:
        debug_data.append(
            {
                "title": topic.get("generated_title"),
                "narrative": topic.get("generated_narrative"),
                "left": _article_summary(topic.get("left")),
                "center": _article_summary(topic.get("center")),
                "right": _article_summary(topic.get("right")),
                "article_count": topic.get("article_count"),
                "bias_coverage": topic.get("bias_coverage"),
            }
        )
    debug_path.write_text(
        json.dumps(debug_data, indent=2, default=str), encoding="utf-8"
    )

    print(f"\n{'=' * 60}")
    print("  Pipeline complete!")
    print(f"{'=' * 60}\n")
    return True


def _build_fallback(topic: dict) -> str:
    """Build a basic narrative without the API."""
    parts = []
    for bias in ("left", "center", "right"):
        article = topic.get(bias)
        if article:
            parts.append(f"{article['source']} reports: \"{article['title']}\"")
    return " ".join(parts) if parts else topic["topic_label"]


def _article_summary(article: dict | None) -> dict | None:
    """Extract key fields from an article for debug output."""
    if not article:
        return None
    return {
        "source": article.get("source"),
        "title": article.get("title"),
        "link": article.get("link"),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The Daily Lens pipeline")
    parser.add_argument(
        "--skip-api",
        action="store_true",
        help="Skip Claude API calls, use fallback narratives",
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory for index.html (default: current dir)",
    )
    args = parser.parse_args()

    success = run_pipeline(
        skip_api=args.skip_api,
        output_dir=args.output,
    )
    sys.exit(0 if success else 1)
