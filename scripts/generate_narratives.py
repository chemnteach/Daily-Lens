"""
generate_narratives.py — Use Claude API to generate balanced topic narratives.

For each topic in the digest, sends the headlines and summaries from all
three bias categories to Claude, which produces a concise, neutral narrative.
"""

import os
import json

import anthropic


def build_prompt(topic: dict) -> str:
    """Build a prompt for Claude to generate a balanced narrative."""
    articles_text = ""

    for bias in ("left", "center", "right"):
        article = topic.get(bias)
        if article:
            articles_text += f"\n[{bias.upper()} - {article['source']}]\n"
            articles_text += f"Headline: {article['title']}\n"
            if article.get("summary"):
                articles_text += f"Summary: {article['summary'][:300]}\n"
            articles_text += f"URL: {article['link']}\n"

    # Include extra articles for context
    for article in topic.get("all_articles", [])[:6]:
        if article not in [topic.get("left"), topic.get("center"), topic.get("right")]:
            articles_text += (
                f"\n[Additional - {article['source']} ({article['bias']})]"
                f"\nHeadline: {article['title']}\n"
            )

    prompt = f"""You are a balanced news digest writer. Given the following news articles
about the same topic from across the political spectrum, write:

1. A clear, descriptive TITLE for the topic (10 words max, newspaper headline style)
2. A NARRATIVE summary (3-5 sentences, ~80 words) that:
   - States the key facts neutrally
   - Notes where different sources emphasize different angles (if applicable)
   - Avoids editorializing or taking sides
   - Is written in present tense where appropriate
   - Gives readers the essential context to understand the story

Articles:
{articles_text}

Respond in this exact JSON format:
{{
  "title": "Your Topic Title Here",
  "narrative": "Your balanced narrative summary here."
}}

Return ONLY the JSON, no other text."""

    return prompt


def generate_narrative(topic: dict, client: anthropic.Anthropic) -> dict:
    """
    Call Claude API to generate a title and narrative for a topic.

    Returns dict with 'title' and 'narrative' keys.
    """
    prompt = build_prompt(topic)

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text.strip()

        # Strip markdown code fences if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

        result = json.loads(response_text)
        return {
            "title": result.get("title", topic["topic_label"]),
            "narrative": result.get("narrative", ""),
        }

    except json.JSONDecodeError:
        # If Claude doesn't return valid JSON, extract what we can
        print(f"  ⚠ JSON parse failed for topic: {topic['topic_label']}")
        return {
            "title": topic["topic_label"],
            "narrative": response_text[:300] if response_text else "",
        }
    except Exception as e:
        print(f"  ✗ API error for topic '{topic['topic_label']}': {e}")
        return {
            "title": topic["topic_label"],
            "narrative": f"Coverage from multiple sources on: {topic['topic_label']}.",
        }


def generate_all_narratives(digest_topics: list[dict]) -> list[dict]:
    """
    Generate narratives for all digest topics.

    Requires ANTHROPIC_API_KEY environment variable.

    Returns the digest_topics list with 'generated_title' and
    'generated_narrative' added to each topic.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠ ANTHROPIC_API_KEY not set — using fallback narratives")
        for topic in digest_topics:
            topic["generated_title"] = topic["topic_label"]
            topic["generated_narrative"] = _fallback_narrative(topic)
        return digest_topics

    client = anthropic.Anthropic(api_key=api_key)

    print("Generating narratives with Claude API...\n")
    for i, topic in enumerate(digest_topics):
        print(f"  Generating {i + 1}/{len(digest_topics)}: {topic['topic_label']}")
        result = generate_narrative(topic, client)
        topic["generated_title"] = result["title"]
        topic["generated_narrative"] = result["narrative"]

    print("\nAll narratives generated.")
    return digest_topics


def _fallback_narrative(topic: dict) -> str:
    """Generate a simple fallback narrative without the API."""
    parts = []
    for bias in ("left", "center", "right"):
        article = topic.get(bias)
        if article:
            parts.append(f"{article['source']} reports: {article['title']}")

    if parts:
        return " | ".join(parts)
    return f"Multiple sources are covering: {topic['topic_label']}."


if __name__ == "__main__":
    # Test with a sample topic
    sample = {
        "topic_label": "Test Topic",
        "left": {
            "source": "NPR",
            "title": "Sample headline from the left",
            "summary": "A summary of the article.",
            "link": "https://example.com",
        },
        "center": {
            "source": "Reuters",
            "title": "Sample headline from center",
            "summary": "A summary of the article.",
            "link": "https://example.com",
        },
        "right": {
            "source": "Fox News",
            "title": "Sample headline from the right",
            "summary": "A summary of the article.",
            "link": "https://example.com",
        },
        "all_articles": [],
    }

    result = generate_all_narratives([sample])
    print(json.dumps(result[0], indent=2, default=str))
