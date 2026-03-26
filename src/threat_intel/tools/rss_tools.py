import os
import yaml
import feedparser
from newspaper import Article
from crewai.tools import BaseTool
from pathlib import Path    

print("LOADED rss_tools.py")

# ------------------
# CONFIG
# ------------------
BASE_DIR = Path(__file__).resolve().parent.parent 
SEEN_FILE =  BASE_DIR / "seen_links.txt"
RSS_FEEDS_FILE = BASE_DIR / "config" / "rss_sources.yaml"


# ------------------
# HELPERS
# ------------------
def load_seen_links():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_seen_link(link: str):
    with open(SEEN_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")


def load_rss_feeds() -> list:
    with open(RSS_FEEDS_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("rss_feeds", [])


# ------------------
# TOOL
# ------------------
class FetchNewArticles(BaseTool):
    name: str = "fetch_new_articles"
    description: str = (
        "Fetch new articles from pre-configured RSS feeds "
        "and return full article content."
    )

    def _run(self,**kwargs) -> list:
        rss_urls = load_rss_feeds()
        seen_links = load_seen_links()
        articles = []

        for feed_url in rss_urls:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                link = entry.get("link")
                if not link or link in seen_links:
                    continue

                try:
                    article = Article(link)
                    article.download()
                    article.parse()
                except Exception:
                    continue  # skip broken articles safely

                articles.append({
                    "source": feed_url,
                    "title": article.title,
                    "text": article.text,
                    "url": link
                })

                save_seen_link(link)

        return {
            "status": "completed",
            "new_items_found": len(articles),
            "articles": articles
        }