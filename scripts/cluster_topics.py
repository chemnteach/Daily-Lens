"""
cluster_topics.py — Group articles into topics using text similarity.

Uses TF-IDF vectorization and agglomerative clustering to identify
common topics across left/center/right sources. Prioritizes topics
that have coverage from multiple bias categories.
"""

import re
from collections import Counter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity


# Common news stopwords that don't help distinguish topics
NEWS_STOPWORDS = {
    "says", "said", "new", "news", "report", "reports", "today",
    "just", "like", "update", "updates", "latest", "breaking",
    "live", "watch", "video", "opinion", "editorial", "analysis",
}


def preprocess_text(text: str) -> str:
    """Lowercase, remove punctuation, filter stopwords."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    words = text.split()
    words = [w for w in words if w not in NEWS_STOPWORDS and len(w) > 2]
    return " ".join(words)


def cluster_articles(
    articles: list[dict],
    n_topics: int = 8,
    distance_threshold: float = 0.65,
) -> list[dict]:
    """
    Cluster articles into topics.

    Args:
        articles: List of article dicts from fetch_feeds.
        n_topics: Target number of clusters (used as fallback).
        distance_threshold: Agglomerative clustering distance cutoff.

    Returns:
        List of topic dicts, sorted by cross-spectrum coverage, each with:
            topic_id, label, articles, bias_coverage
    """
    if not articles:
        return []

    # Build text corpus from title + summary
    texts = [
        preprocess_text(f"{a['title']} {a.get('summary', '')}")
        for a in articles
    ]

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(
        max_features=3000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.8,
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
    except ValueError:
        # Not enough documents for min_df=2, relax constraint
        vectorizer = TfidfVectorizer(
            max_features=3000,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.9,
        )
        tfidf_matrix = vectorizer.fit_transform(texts)

    # Agglomerative clustering with cosine distance
    # Convert to dense for distance computation
    distance_matrix = 1 - cosine_similarity(tfidf_matrix)
    np.fill_diagonal(distance_matrix, 0)

    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric="precomputed",
        linkage="average",
    )
    labels = clustering.fit_predict(distance_matrix)

    # Group articles by cluster
    clusters = {}
    for idx, label in enumerate(labels):
        label = int(label)
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(articles[idx])

    # Build topic objects with metadata
    topics = []
    for cluster_id, cluster_articles in clusters.items():
        bias_sources = {
            "left": [],
            "center": [],
            "right": [],
        }
        for article in cluster_articles:
            bias_sources[article["bias"]].append(article)

        # Count how many bias categories are represented
        bias_coverage = sum(
            1 for b in bias_sources.values() if len(b) > 0
        )

        # Generate a label from the most common significant terms
        all_titles = " ".join(a["title"] for a in cluster_articles)
        label = _extract_topic_label(all_titles)

        topics.append(
            {
                "topic_id": cluster_id,
                "label": label,
                "articles": cluster_articles,
                "bias_sources": bias_sources,
                "bias_coverage": bias_coverage,
                "article_count": len(cluster_articles),
            }
        )

    # Sort: prefer topics with coverage across all 3 bias categories,
    # then by article count
    topics.sort(
        key=lambda t: (t["bias_coverage"], t["article_count"]),
        reverse=True,
    )

    return topics


def _extract_topic_label(titles_text: str) -> str:
    """Extract a rough topic label from combined titles."""
    cleaned = preprocess_text(titles_text)
    words = cleaned.split()

    # Count word frequency, prefer 2-grams
    word_freq = Counter(words)

    # Remove very common words
    for w in list(word_freq.keys()):
        if len(w) < 4 or word_freq[w] < 2:
            del word_freq[w]

    if word_freq:
        top_words = [w for w, _ in word_freq.most_common(4)]
        return " ".join(top_words).title()

    return "Trending Story"


def select_best_article(articles: list[dict]) -> dict | None:
    """Pick the best article from a list — prefer those with summaries."""
    if not articles:
        return None

    # Prefer articles with longer summaries (more content)
    scored = sorted(
        articles,
        key=lambda a: len(a.get("summary", "")),
        reverse=True,
    )
    return scored[0]


def prepare_topics_for_digest(
    topics: list[dict], max_topics: int = 5
) -> list[dict]:
    """
    Select top topics and pick the best article per bias for each.

    Returns list of dicts ready for narrative generation:
        topic_label, left_article, center_article, right_article
    """
    digest_topics = []

    for topic in topics[:max_topics]:
        best = {}
        for bias in ("left", "center", "right"):
            best[bias] = select_best_article(
                topic["bias_sources"].get(bias, [])
            )

        digest_topics.append(
            {
                "topic_label": topic["label"],
                "article_count": topic["article_count"],
                "bias_coverage": topic["bias_coverage"],
                "left": best["left"],
                "center": best["center"],
                "right": best["right"],
                "all_articles": topic["articles"],
            }
        )

    return digest_topics


if __name__ == "__main__":
    import json

    # Test with saved articles
    try:
        with open("raw_articles.json") as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("Run fetch_feeds.py first to generate raw_articles.json")
        exit(1)

    print(f"Clustering {len(articles)} articles...\n")
    topics = cluster_articles(articles)

    print(f"Found {len(topics)} topic clusters:\n")
    for t in topics[:10]:
        print(
            f"  [{t['bias_coverage']}/3 spectrum] "
            f"{t['label']} ({t['article_count']} articles)"
        )

    digest = prepare_topics_for_digest(topics)
    print(f"\nTop {len(digest)} digest topics selected.")
