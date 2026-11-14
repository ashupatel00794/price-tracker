import os, re, sqlite3, time, random
import requests
from bs4 import BeautifulSoup

DOMAIN = os.getenv("AMAZON_DOMAIN", "www.amazon.in")
DROP_PCT = float(os.getenv("DROP_PCT", "15"))
TG_TOKEN = os.getenv("TG_TOKEN", "")
TG_CHAT = os.getenv("TG_CHAT", "")
CATEGORIES = {
    "Phones": "smartphone",
    "Laptops": "laptop",
    "Music": "headphones earbuds",
    "Monitors": "monitor",
    "PC Gaming": "gaming keyboard mouse headset",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
db = sqlite3.connect("prices.db")
db.execute("CREATE TABLE IF NOT EXISTS deals(asin TEXT PRIMARY KEY, title TEXT, price REAL, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")

def num(el):
    return float(re.sub(r"[^\d.]", "", el.get_text().replace(",", ""))) if el else None

def parse(html):
    out = []
    for d in BeautifulSoup(html, "html.parser").select('div[data-component-type="s-search-result"]'):
        asin = d.get("data-asin")
        t = d.select_one("h2")
        p = num(d.select_one("span.a-price:not(.a-text-price) span.a-offscreen"))
        mrp = num(d.select_one("span.a-price.a-text-price span.a-offscreen"))
        if asin and t and p:
            out.append((asin, t.get_text(strip=True)[:70], p, mrp))
    return out

def fetch(query):
    r = requests.get(f"https://{DOMAIN}/s", params={"k": query}, headers=HEADERS, timeout=20)
    if r.status_code != 200 or "captcha" in r.text.lower():
        raise RuntimeError(f"Blocked/failed (status {r.status_code})")
    return parse(r.text)

def notify(lines):
    msg = "Price drop alerts:\n\n" + "\n\n".join(lines[:10])
    print(msg)
    if TG_TOKEN and TG_CHAT:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                      data={"chat_id": TG_CHAT, "text": msg[:4000], "disable_web_page_preview": True}, timeout=15)

def main():
    alerts = []
    counts = []
    for cat, q in CATEGORIES.items():
        try:
            items = fetch(q)
        except Exception as e:
            print("Error:", cat, e); counts.append(f"{cat}: BLOCKED/ERROR"); continue
        print(cat, "items:", len(items)); counts.append(f"{cat}: {len(items)} items")
        for asin, title, price, mrp in items:
            row = db.execute("SELECT price FROM deals WHERE asin=?", (asin,)).fetchone()
            if row and row[0] > 0 and (row[0] - price) / row[0] * 100 >= DROP_PCT:
                off = f", MRP {mrp:.0f}" if mrp else ""
                alerts.append(f"[{cat}] {title}\nAb {price:.0f} (pehle {row[0]:.0f}{off})\nhttps://{DOMAIN}/dp/{asin}")
            db.execute("INSERT OR REPLACE INTO deals(asin,title,price) VALUES(?,?,?)", (asin, title, price))
        db.commit()
        time.sleep(random.uniform(4, 9))
    if alerts:
        notify(alerts)
    if TG_TOKEN and TG_CHAT:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                      data={"chat_id": TG_CHAT, "text": "Deals check done:\n" + "\n".join(counts)}, timeout=15)

if __name__ == "__main__":
    main()
