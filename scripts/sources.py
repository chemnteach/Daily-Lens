"""
sources.py — Curated news source registry for The Daily Lens.

All sources score 40+ on the Ad Fontes Media Bias Chart for reliability.
All sources are free (no paywall required for headlines/articles).
Each source includes its RSS feed URL and bias category.

Bias categories:
  - left: Skews left on the Ad Fontes chart
  - center: Center or balanced
  - right: Skews right on the Ad Fontes chart
"""

SOURCES = {
    "left": [
        {
            "name": "NPR",
            "rss": "https://feeds.npr.org/1001/rss.xml",
            "homepage": "https://www.npr.org",
        },
        {
            "name": "PBS NewsHour",
            "rss": "https://www.pbs.org/newshour/feeds/rss/headlines",
            "homepage": "https://www.pbs.org/newshour",
        },
        {
            "name": "The Guardian",
            "rss": "https://www.theguardian.com/us-news/rss",
            "homepage": "https://www.theguardian.com/us-news",
        },
        {
            "name": "BBC News",
            "rss": "https://feeds.bbci.co.uk/news/rss.xml",
            "homepage": "https://www.bbc.com/news",
        },
        {
            "name": "ProPublica",
            "rss": "https://feeds.propublica.org/propublica/main",
            "homepage": "https://www.propublica.org",
        },
    ],
    "center": [
        {
            "name": "Reuters",
            "rss": "https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best",
            "homepage": "https://www.reuters.com",
        },
        {
            "name": "AP News",
            "rss": "https://rsshub.app/apnews/topics/apf-topnews",
            "homepage": "https://apnews.com",
        },
        {
            "name": "The Hill",
            "rss": "https://thehill.com/feed/",
            "homepage": "https://thehill.com",
        },
        {
            "name": "USA Today",
            "rss": "https://rssfeeds.usatoday.com/usatoday-NewsTopStories",
            "homepage": "https://www.usatoday.com",
        },
        {
            "name": "ABC News",
            "rss": "https://abcnews.go.com/abcnews/topstories",
            "homepage": "https://abcnews.go.com",
        },
    ],
    "right": [
        {
            "name": "Fox News",
            "rss": "https://moxie.foxnews.com/google-publisher/latest.xml",
            "homepage": "https://www.foxnews.com",
        },
        {
            "name": "The Dispatch",
            "rss": "https://thedispatch.com/feed/",
            "homepage": "https://thedispatch.com",
        },
        {
            "name": "RealClearPolitics",
            "rss": "https://www.realclearpolitics.com/index.xml",
            "homepage": "https://www.realclearpolitics.com",
        },
        {
            "name": "National Review",
            "rss": "https://www.nationalreview.com/feed/",
            "homepage": "https://www.nationalreview.com",
        },
        {
            "name": "New York Post",
            "rss": "https://nypost.com/feed/",
            "homepage": "https://nypost.com",
        },
    ],
}


def get_all_sources():
    """Return a flat list of all sources with bias category attached."""
    all_sources = []
    for bias, sources in SOURCES.items():
        for source in sources:
            all_sources.append({**source, "bias": bias})
    return all_sources


def get_sources_by_bias(bias: str):
    """Return sources for a specific bias category."""
    return SOURCES.get(bias, [])
