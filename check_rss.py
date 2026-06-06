import feedparser
import requests
import os
import json

# ここに Nitter/Xcancel 系の RSS URL を入れる
RSS_URL = "https://nitter.net/amarareitem/rss"
# 検知したいキーワード
KEYWORD = "らくらくベビー"

STATE_FILE = "last_checked.json"

# 前回のリンクを読み出す
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        last_links = json.load(f)
else:
    last_links = []

feed = feedparser.parse(RSS_URL)

for entry in feed.entries[:5]:
    link = entry.get("link", "")
    if link in last_links:
        continue

    title = entry.get("title", "")
    summary = entry.get("summary", "")
    text = f"{title} {summary}"

    if KEYWORD in text:
        webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
        requests.post(
            webhook_url,
            json={"content": f"条件一致: {title}\nURL: {link}"}
        )

        # 今回のリンクを保存
        last_links.append(link)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(last_links, f, ensure_ascii=False, indent=2)
        break
