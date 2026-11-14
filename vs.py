import os, re, sqlite3, time, random
import requests
from bs4 import BeautifulSoup

BASE = "https://www.vijaysales.com"
DROP_PCT = float(os.getenv("DROP_PCT", "15"))
TG_TOKEN = os.getenv("TG_TOKEN", "")
TG_CHAT = os.getenv("TG_CHAT", "")
CATEGORIES = {
    "Smartphone": "smartphones",
    "iPhone": "iphones",
    "Laptop": "laptops",
    "Headphones": "headphones",
    "Mouse": "mouse",
    "Keyboard": "keyboards",
    "SSD": "ssd",
    "Hard Disk": "hard-disks",
    "Pen Drive": "pen-drives",
    "Monitor": "monitors",
    "Desktop": "desktops",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    items = {}
    for card in soup.select("div.product-card[data-child-sku]"):
        sku = card["data-child-sku"]
        a = card.select_one("a.product-card__link")
        name = card.select_one(".product-name")
        price = card.select_one(".discountedPrice")
        if not (a and name and price):
            continue
        digits = re.sub(r"[^\d]", "", price.get_text(" ", strip=True))
        if not digits or sku in items:
            continue
        items[sku] = (name.get_text(" ", strip=True)[:70], float(digits), a["href"].split("?")[0])
    return [(sku, t, p, link) for sku, (t, p, link) in items.items()]


def tg(text):
    print(text)
    if TG_TOKEN and TG_CHAT:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                      data={"chat_id": TG_CHAT, "text": text[:4000], "disable_web_page_preview": True}, timeout=15)


def run_once():
    db = sqlite3.connect("fk.db")
    db.execute("CREATE TABLE IF NOT EXISTS vs(sku TEXT PRIMARY KEY, title TEXT, price REAL)")
    alerts, counts = [], []
    for cat, slug in CATEGORIES.items():
        try:
            r = requests.get(f"{BASE}/c/{slug}", headers=HEADERS, timeout=25)
            if r.status_code != 200:
                raise RuntimeError(f"status {r.status_code}")
            items = parse(r.text)
        except Exception as e:
            counts.append(f"{cat}: ERROR {str(e)[:60]}")
            continue
        counts.append(f"{cat}: {len(items)} items")
        for sku, title, price, link in items:
            row = db.execute("SELECT price FROM vs WHERE sku=?", (sku,)).fetchone()
            if row and row[0] > 0 and abs(row[0] - price) / row[0] * 100 >= DROP_PCT:
                pct = (row[0] - price) / row[0] * 100
                tag = "🔻 sasta" if pct > 0 else "🔺 mehnga"
                alerts.append(f"{tag} {abs(pct):.0f}% | Vijay Sales {cat}\n{title}\nAb ₹{price:,.0f} (pehle ₹{row[0]:,.0f})\n{BASE}{link}")
            db.execute("INSERT OR REPLACE INTO vs(sku,title,price) VALUES(?,?,?)", (sku, title, price))
        db.commit()
        time.sleep(random.uniform(3, 6))
    print("VS counts:", counts)
    for i in range(0, min(len(alerts), 40), 8):
        tg("Vijay Sales price changes:\n\n" + "\n\n".join(alerts[i:i + 8]))
    if os.getenv("STATUS", "1") == "1":
        tg("Vijay Sales check done:\n" + "\n".join(counts))


if __name__ == "__main__":
    try:
        run_once()
    except Exception as e:
        print("VS failed:", e)
