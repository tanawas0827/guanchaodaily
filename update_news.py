
import feedparser
from datetime import datetime, timezone, timedelta
from html import escape
from pathlib import Path
import re

# 公开 RSS 新闻源
SOURCES = [
    ("科技与 AI", "Hacker News", "https://hnrss.org/frontpage"),
    ("国际新闻", "BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("商业与经济", "BBC Business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("科技动态", "BBC Technology", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
]

START = "<!-- GUANCHAO_NEWS_START -->"
END = "<!-- GUANCHAO_NEWS_END -->"

def get_news():
    articles = []
    seen = set()

    for category, source, url in SOURCES:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()

            if not title or not link or link in seen:
                continue

            seen.add(link)
            articles.append({
                "category": category,
                "source": source,
                "title": title,
                "link": link,
            })

    return articles

def build_section(articles):
    now = datetime.now(timezone(timedelta(hours=8)))
    date_text = now.strftime("%Y年%m月%d日 %H:%M")

    cards = []

    for article in articles:
        cards.append(f"""
        <article class="gc-news-card">
          <div class="gc-news-meta">
            {escape(article['category'])} · {escape(article['source'])}
          </div>
          <h3>
            <a href="{escape(article['link'], quote=True)}"
               target="_blank" rel="noopener noreferrer">
              {escape(article['title'])}
            </a>
          </h3>
        </article>
        """)

    return f"""
    <section id="guanchao-latest" class="gc-news-section">
      <style>
        .gc-news-section {{
          max-width: 960px;
          margin: 48px auto;
          padding: 24px;
          font-family: system-ui, sans-serif;
          color: #222;
        }}
        .gc-news-section h2 {{
          font-size: 28px;
          margin-bottom: 8px;
        }}
        .gc-news-date {{
          color: #777;
          margin-bottom: 24px;
        }}
        .gc-news-card {{
          padding: 20px 0;
          border-bottom: 1px solid #ddd;
        }}
        .gc-news-meta {{
          color: #777;
          font-size: 13px;
          margin-bottom: 8px;
        }}
        .gc-news-card h3 {{
          font-size: 19px;
          line-height: 1.5;
          margin: 0;
        }}
        .gc-news-card a {{
          color: inherit;
          text-decoration: none;
        }}
        .gc-news-card a:hover {{
          text-decoration: underline;
        }}
      </style>
      <h2>📰 观潮 · 最新资讯</h2>
      <p class="gc-news-date">更新时间：{date_text}（北京时间）</p>
      {''.join(cards)}
    </section>
    """

def main():
    articles = get_news()

    if not articles:
        raise RuntimeError("所有 RSS 新闻源均未返回文章，保留旧页面")

    path = Path("index.html")
    html = path.read_text(encoding="utf-8")
    section = START + build_section(articles) + END

    if START in html and END in html:
        html = re.sub(
            re.escape(START) + r".*?" + re.escape(END),
            lambda _: section,
            html,
            flags=re.S,
        )
    elif "</body>" in html.lower():
        html = re.sub(
            r"</body\s*>",
            lambda m: section + "\n" + m.group(0),
            html,
            count=1,
            flags=re.I,
        )
    else:
        html += "\n" + section

    path.write_text(html, encoding="utf-8")
    print(f"成功更新 {len(articles)} 条新闻")

if __name__ == "__main__":
    main()
