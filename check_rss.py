import feedparser
import requests
import os
import json
import time

RSS_URL = "https://nitter.net/amarareitem/rss"
KEYWORD = "らくらくベビー"
STATE_FILE = "last_checked.json"
MAX_ITERATIONS = 5
SLEEP_SECONDS = 30

# 通知容量スタット使用量（手動テスト用）
total_bytes = 0

# 前回のリンクを読み出す
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        last_links = data.get("last_links", [])
else:
    last_links = []

# 通知済みフラグ（エラー通知を 1 回だけ）
error_notified = False

for iteration in range(1, MAX_ITERATIONS + 1):
    print(f"[{iteration}/{MAX_ITERATIONS}] RSS取得中...")
    
    try:
        feed = feedparser.parse(RSS_URL)
        
        if feed.bozo and not feed.entries:
            print("ERROR: RSS取得失敗")
            if not error_notified:
                webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
                if webhook_url:
                    requests.post(
                        webhook_url,
                        json={"content": f"エラー：RSS取得失敗\nURL: {RSS_URL}"}
                    )
                    error_notified = True
            break
        
        for entry in feed.entries[:5]:
            link = entry.get("link", "")
            if link in last_links:
                continue
            
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            text = f"{title} {summary}"
            
            if KEYWORD in text:
                webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
                if webhook_url:
                    content = f"条件一致: {title}\nURL: {link}"
                    requests.post(webhook_url, json={"content": content})
                    total_bytes += len(content.encode("utf-8"))
                
                last_links.append(link)
                with open(STATE_FILE, "w", encoding="utf-8") as f:
                    json.dump(last_links, f, ensure_ascii=False, indent=2)
                print(f"条件一致: {title}")
                break
        
        print(f"[{iteration}/{MAX_ITERATIONS}] 完了")
        
        if iteration < MAX_ITERATIONS:
            print(f"{SLEEP_SECONDS}秒待機...")
            time.sleep(SLEEP_SECONDS)
    
    except Exception as e:
        print(f"ERROR: {e}")
        if not error_notified:
            webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
            if webhook_url:
                requests.post(
                    webhook_url,
                    json={"content": f"エラーが発生しました\n{str(e)}"}
                )
                error_notified = True
        break
