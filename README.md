# 📰 The Daily Lens

**A daily balanced news digest that shows you how today's top stories are covered across the political spectrum.**

Every morning at 6:00 AM MT, this pipeline automatically:
1. Fetches headlines from 15 curated news sources across left, center, and right
2. Clusters articles into common topics using NLP
3. Generates balanced narrative summaries using Claude AI
4. Publishes a static dashboard to GitHub Pages

All sources score **40+ on the [Ad Fontes Media Bias Chart](https://adfontesmedia.com)** for news value and reliability. None are behind paywalls.

## 🏗️ Architecture

```
RSS Feeds (15 sources)
        │
        ▼
  [fetch_feeds.py]     ← feedparser, 48h window
        │
        ▼
  [cluster_topics.py]  ← TF-IDF + agglomerative clustering
        │
        ▼
  [generate_narratives.py]  ← Claude Haiku API
        │
        ▼
  [render_html.py]     ← Static HTML generation
        │
        ▼
  docs/index.html      ← GitHub Pages serves this
```

**Stack:** Python 3.12 · GitHub Actions (cron) · Claude API (Haiku) · GitHub Pages

**Cost:** Essentially free. GitHub Actions free tier covers it, Claude Haiku costs ~$0.01/day for 5 API calls.

## 🚀 Setup

### 1. Fork or clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/daily-lens.git
cd daily-lens
```

### 2. Add your Anthropic API key

Go to your repo on GitHub:
- **Settings → Secrets and variables → Actions → New repository secret**
- Name: `ANTHROPIC_API_KEY`
- Value: Your API key from [console.anthropic.com](https://console.anthropic.com)

### 3. Enable GitHub Pages

Go to your repo on GitHub:
- **Settings → Pages**
- Source: **GitHub Actions**

### 4. Run it manually (first test)

- Go to **Actions → Daily Lens — Generate & Deploy**
- Click **Run workflow**
- Wait ~2 minutes
- Visit `https://YOUR_USERNAME.github.io/daily-lens/`

### 5. That's it!

The workflow runs automatically every day at 6:00 AM Mountain Time. Your friends can bookmark the URL.

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline locally
cd scripts
python main.py --output ../docs

# Or skip the API for testing
python main.py --skip-api --output ../docs

# Open the result
open ../docs/index.html
```

## 📊 News Sources

| Skews Left | Center / Balanced | Skews Right |
|---|---|---|
| NPR | Reuters | Fox News |
| PBS NewsHour | AP News | The Dispatch |
| The Guardian | The Hill | RealClearPolitics |
| BBC News | USA Today | National Review |
| ProPublica | ABC News | New York Post |

Sources can be added/removed/recategorized in `scripts/sources.py`.

## 🛠️ Customization

- **Change publish time:** Edit the cron schedule in `.github/workflows/daily-digest.yml`
- **Add/remove sources:** Edit `scripts/sources.py`
- **Change the look:** Edit the CSS in `scripts/render_html.py`
- **Adjust clustering:** Tweak `distance_threshold` in `scripts/cluster_topics.py`
- **Change the AI model:** Edit the model name in `scripts/generate_narratives.py`

## 📝 How It Works

**Topic Clustering:** Articles are vectorized using TF-IDF (title + summary text) and grouped using agglomerative clustering with cosine distance. Topics are ranked by how many bias categories (left/center/right) have coverage — stories that appear across the spectrum rank highest.

**Narrative Generation:** For each of the top 5 topics, the headlines and summaries from all three perspectives are sent to Claude Haiku with instructions to write a neutral, factual summary. The prompt explicitly asks for no editorializing.

**Fallback Mode:** If the API key isn't set or calls fail, the pipeline still runs using headline-based fallback narratives.

## 📄 License

MIT — Do whatever you want with it.
