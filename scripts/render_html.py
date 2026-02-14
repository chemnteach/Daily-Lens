"""
render_html.py — Generate the static HTML dashboard from processed topics.

Takes the digest topics (with generated narratives) and renders them
into a complete, self-contained HTML page using a Jinja2-style
string template approach (no external dependencies).
"""

import html
from datetime import datetime, timezone, timedelta


def escape(text: str) -> str:
    """HTML-escape user content."""
    return html.escape(str(text)) if text else ""


def render_perspective(article: dict | None, bias: str) -> str:
    """Render a single perspective column."""
    labels = {"left": "Skews Left", "center": "Center", "right": "Skews Right"}

    if not article:
        return f"""
      <div class="perspective {bias}">
        <div class="perspective-label">{labels[bias]}</div>
        <div class="perspective-source" style="color:var(--text-dim)">
          No coverage found
        </div>
        <div class="perspective-headline">
          No matching article from this category today.
        </div>
      </div>"""

    return f"""
      <div class="perspective {bias}">
        <div class="perspective-label">{labels[bias]}</div>
        <div class="perspective-source">{escape(article['source'])}</div>
        <div class="perspective-headline">{escape(article['title'])}</div>
        <a class="perspective-link" href="{escape(article['link'])}"
           target="_blank" rel="noopener">Read at {escape(article['source'])}</a>
      </div>"""


def render_topic_card(topic: dict, index: int) -> str:
    """Render a single topic card."""
    title = escape(topic.get("generated_title", topic["topic_label"]))
    narrative = escape(topic.get("generated_narrative", ""))
    num = index + 1

    perspectives = ""
    for bias in ("left", "center", "right"):
        perspectives += render_perspective(topic.get(bias), bias)

    return f"""
  <div class="topic-card">
    <div class="topic-header">
      <div class="topic-number">Topic {num:02d} of 05</div>
      <div class="topic-title">{title}</div>
      <div class="topic-narrative">{narrative}</div>
    </div>
    <div class="perspectives">
      {perspectives}
    </div>
  </div>"""


def render_page(digest_topics: list[dict]) -> str:
    """
    Render the complete HTML page.

    Args:
        digest_topics: List of topic dicts with generated narratives.

    Returns:
        Complete HTML string.
    """
    # Format date for Mountain Time (UTC-7)
    mt_offset = timezone(timedelta(hours=-7))
    now = datetime.now(mt_offset)
    date_display = now.strftime("%A, %B %d, %Y")

    # Render all topic cards
    cards_html = ""
    for i, topic in enumerate(digest_topics[:5]):
        cards_html += render_topic_card(topic, i)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Daily Lens — Balanced News Digest</title>
<meta name="description" content="A daily balanced news digest showing how today's top stories are covered across the political spectrum.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Source+Sans+3:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0f1115;
    --surface: #1a1d24;
    --surface-hover: #22262f;
    --border: #2a2e38;
    --text: #e8e9ed;
    --text-muted: #8b8f9a;
    --text-dim: #5c6070;
    --accent: #6c9bff;
    --left: #5b8def;
    --left-bg: rgba(91,141,239,0.08);
    --left-border: rgba(91,141,239,0.2);
    --center: #a0a8b8;
    --center-bg: rgba(160,168,184,0.08);
    --center-border: rgba(160,168,184,0.2);
    --right: #ef6b5b;
    --right-bg: rgba(239,107,91,0.08);
    --right-border: rgba(239,107,91,0.2);
    --card-radius: 12px;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Source Sans 3', sans-serif;
    line-height: 1.6;
    min-height: 100vh;
  }}
  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    opacity: 0.03;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 999;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 0 24px; }}
  header {{ padding: 48px 0 20px; border-bottom: 1px solid var(--border); margin-bottom: 32px; }}
  .header-top {{ display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 20px; }}
  .masthead {{ font-family: 'DM Serif Display', serif; font-size: 2.4rem; letter-spacing: -0.02em; color: var(--text); line-height: 1.1; }}
  .masthead span {{ color: var(--accent); }}
  .date-badge {{ font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--text-muted); background: var(--surface); padding: 6px 14px; border-radius: 6px; border: 1px solid var(--border); white-space: nowrap; }}
  .about-bar {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--card-radius); padding: 20px 28px; margin-bottom: 32px; display: flex; gap: 28px; align-items: flex-start; }}
  .about-bar .about-icon {{ font-size: 1.6rem; flex-shrink: 0; margin-top: 2px; }}
  .about-bar .about-content {{ flex: 1; }}
  .about-bar h2 {{ font-family: 'DM Serif Display', serif; font-size: 1.1rem; margin-bottom: 6px; color: var(--text); }}
  .about-bar p {{ font-size: 0.9rem; color: var(--text-muted); line-height: 1.6; }}
  .legend {{ display: flex; gap: 20px; margin-top: 12px; flex-wrap: wrap; }}
  .legend-item {{ display: flex; align-items: center; gap: 8px; font-size: 0.82rem; color: var(--text-muted); }}
  .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
  .legend-dot.left {{ background: var(--left); }}
  .legend-dot.center {{ background: var(--center); }}
  .legend-dot.right {{ background: var(--right); }}
  .topic-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--card-radius); margin-bottom: 24px; overflow: hidden; transition: border-color 0.2s; }}
  .topic-card:hover {{ border-color: #3a3f4d; }}
  .topic-header {{ padding: 24px 28px 16px; }}
  .topic-number {{ font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--text-dim); margin-bottom: 8px; }}
  .topic-title {{ font-family: 'DM Serif Display', serif; font-size: 1.45rem; line-height: 1.3; color: var(--text); margin-bottom: 12px; }}
  .topic-narrative {{ font-size: 0.95rem; color: var(--text-muted); line-height: 1.7; max-width: 90ch; }}
  .perspectives {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; border-top: 1px solid var(--border); }}
  .perspective {{ padding: 18px 24px; border-right: 1px solid var(--border); transition: background 0.2s; }}
  .perspective:last-child {{ border-right: none; }}
  .perspective.left {{ background: var(--left-bg); }}
  .perspective.left:hover {{ background: rgba(91,141,239,0.12); }}
  .perspective.center {{ background: var(--center-bg); }}
  .perspective.center:hover {{ background: rgba(160,168,184,0.12); }}
  .perspective.right {{ background: var(--right-bg); }}
  .perspective.right:hover {{ background: rgba(239,107,91,0.12); }}
  .perspective-label {{ font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 8px; font-weight: 500; }}
  .perspective.left .perspective-label {{ color: var(--left); }}
  .perspective.center .perspective-label {{ color: var(--center); }}
  .perspective.right .perspective-label {{ color: var(--right); }}
  .perspective-source {{ font-size: 0.78rem; font-weight: 600; color: var(--text); margin-bottom: 4px; }}
  .perspective-headline {{ font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 8px; }}
  .perspective-link {{ font-size: 0.78rem; color: var(--accent); text-decoration: none; font-weight: 500; display: inline-flex; align-items: center; gap: 4px; transition: opacity 0.2s; }}
  .perspective-link:hover {{ opacity: 0.7; }}
  .perspective-link::after {{ content: '→'; }}
  footer {{ padding: 32px 0 48px; margin-top: 16px; border-top: 1px solid var(--border); text-align: center; }}
  .footer-text {{ font-size: 0.8rem; color: var(--text-dim); line-height: 1.8; }}
  .footer-text a {{ color: var(--text-muted); text-decoration: none; }}
  .footer-text a:hover {{ text-decoration: underline; }}
  @media (max-width: 768px) {{
    .masthead {{ font-size: 1.8rem; }}
    .header-top {{ flex-direction: column; align-items: flex-start; gap: 12px; }}
    .about-bar {{ flex-direction: column; gap: 12px; }}
    .perspectives {{ grid-template-columns: 1fr; }}
    .perspective {{ border-right: none; border-bottom: 1px solid var(--border); }}
    .perspective:last-child {{ border-bottom: none; }}
    .topic-header {{ padding: 20px 20px 14px; }}
    .perspective {{ padding: 16px 20px; }}
  }}
  @keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(16px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  .topic-card {{ animation: fadeUp 0.5s ease both; }}
  .topic-card:nth-child(1) {{ animation-delay: 0.05s; }}
  .topic-card:nth-child(2) {{ animation-delay: 0.12s; }}
  .topic-card:nth-child(3) {{ animation-delay: 0.19s; }}
  .topic-card:nth-child(4) {{ animation-delay: 0.26s; }}
  .topic-card:nth-child(5) {{ animation-delay: 0.33s; }}
  .about-bar {{ animation: fadeUp 0.4s ease both; }}
  header {{ animation: fadeUp 0.3s ease both; }}
</style>
</head>
<body>
<div class="container">

  <header>
    <div class="header-top">
      <div class="masthead">The Daily <span>Lens</span></div>
      <div class="date-badge">{date_display}</div>
    </div>
  </header>

  <div class="about-bar">
    <div class="about-icon">&#9673;</div>
    <div class="about-content">
      <h2>What is The Daily Lens?</h2>
      <p>
        Every morning, this page curates the top 5 news stories of the day and
        shows you how each is being covered across the political spectrum &mdash;
        from left-leaning to center to right-leaning sources. All sources score
        40+ on the <a href="https://adfontesmedia.com" style="color:var(--accent)">
        Ad Fontes Media Bias Chart</a> for news value and reliability, and none
        are behind paywalls. The goal isn&rsquo;t to tell you what to think &mdash;
        it&rsquo;s to show you the full picture so you can decide for yourself.
      </p>
      <div class="legend">
        <div class="legend-item"><div class="legend-dot left"></div> Skews Left</div>
        <div class="legend-item"><div class="legend-dot center"></div> Center / Balanced</div>
        <div class="legend-item"><div class="legend-dot right"></div> Skews Right</div>
      </div>
    </div>
  </div>

  {cards_html}

  <footer>
    <div class="footer-text">
      The Daily Lens &mdash; A balanced news digest, published every morning at 6:00 AM MT.<br>
      Sources rated 40+ for reliability on the
      <a href="https://adfontesmedia.com">Ad Fontes Media Bias Chart</a>.
      No paywalls. No algorithms. Just perspective.<br>
      Built with Python, Claude API &amp; GitHub Actions. Served via GitHub Pages.<br>
      <br>
      This digest is generated for informational purposes. Source bias ratings are approximate.<br>
      &copy; 2026 The Daily Lens
    </div>
  </footer>

</div>
</body>
</html>"""


if __name__ == "__main__":
    # Test with dummy data
    sample_topics = [
        {
            "topic_label": "Test Topic",
            "generated_title": "This Is a Test Headline",
            "generated_narrative": "This is a test narrative for the topic.",
            "left": {
                "source": "NPR",
                "title": "Left take on the story",
                "link": "https://npr.org",
            },
            "center": {
                "source": "Reuters",
                "title": "Center take on the story",
                "link": "https://reuters.com",
            },
            "right": {
                "source": "Fox News",
                "title": "Right take on the story",
                "link": "https://foxnews.com",
            },
        }
    ]

    page = render_page(sample_topics)
    with open("test_output.html", "w") as f:
        f.write(page)
    print(f"Rendered test page: {len(page)} bytes")
