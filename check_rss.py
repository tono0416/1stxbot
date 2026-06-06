import feedparser
import requests
import os

# ここに Nitter/Xcancel 系の RSS URL を入れる
RSS_URL = "https://nitter.net/amarareitem/rss"

# 検知したいキーワード
KEYWORD = "らくらくベビー"

feed = feedparser.parse(RSS_URL)

# 最新から 5 件までチェック
for entry in feed.entries[:5]:
    title = entry.get("title", "")
    summary = entry.get("summary", "")
    link = entry.get("link", "")

    text = f"{title} {summary}"

    if KEYWORD in text:
        webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
        requests.post(
            webhook_url,
            json={"content": f"条件一致: {title}\nURL: {link}"}
        )
        break
