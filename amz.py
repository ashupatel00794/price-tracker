import os, re, sqlite3, time, random
import requests
from bs4 import BeautifulSoup

BASE = "https://www.amazon.in"
DROP_PCT = float(os.getenv("DROP_PCT", "15"))
TG_TOKEN = os.getenv("TG_TOKEN", "")
TG_CHAT = os.getenv("TG_CHAT", "")
CATEGORIES = {
    "Smartphone": "/gp/bestsellers/electronics/1389432031",
    "Laptop": "/gp/bestsellers/computers/1375424031",
    "Headphones": "/gp/bestsellers/electronics/1388921031",
    "Monitor": "/gp/bestsellers/computers/1375425031",
    "Keyboard/Mouse": "/gp/bestsellers/computers/1375412031",
    "Storage (SSD/HDD)": "/gp/bestsellers/computers/1375393031",
    "PC Components": "/gp/bestsellers/computers/1375344031",
    "Cables/Accessories": "/gp/bestsellers/computers/1375248031",
    "Shoes": "/gp/bestsellers/shoes/1983396031",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
}


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    items = {}
    for li in soup.select("li.zg-no-numbers"):
        a = li.select_one('a[href*="/dp/"]')
        if not a:
            continue
        m = re.search(r"/dp/([A-Z0-9]{10})", a["href"])
        if not m or m.group(1) in items:
            continue
        title = li.select_one('[class*="line-clamp"]')
        price = li.select_one('[class*="p13n-sc-price"]')
        if not (title and price):
            continue
        num = re.sub(r"[^\d.]", "", price.get_text(" ", strip=True))
        if not num:
            continue
        items[m.group(1)] = (title.get_text(" ", strip=True)[:70], float(num))
    return [(asin, t, p) for asin, (t, p) in items.items()]


def tg(text):
    print(text)
    if TG_TOKEN and TG_CHAT:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                      data={"chat_id": TG_CHAT, "text": text[:4000], "disable_web_page_preview": True}, timeout=15)


def run_once():
    db = sqlite3.connect("fk.db")
    db.execute("CREATE TABLE IF NOT EXISTS amz(asin TEXT PRIMARY KEY, title TEXT, price REAL)")
    alerts, counts = [], []
    for cat, path in CATEGORIES.items():
        try:
            r = requests.get(BASE + path, headers=HEADERS, timeout=25)
            if r.status_code != 200:
                raise RuntimeError(f"status {r.status_code}")
            items = parse(r.text)
        except Exception as e:
            counts.append(f"{cat}: ERROR {str(e)[:60]}")
            continue
        counts.append(f"{cat}: {len(items)} items")
        if items:
            print("AMZ sample", cat, "|", items[0][1][:50], "|", items[0][2])
        for asin, title, price in items:
            row = db.execute("SELECT price FROM amz WHERE asin=?", (asin,)).fetchone()
            if row and row[0] > 0 and abs(row[0] - price) / row[0] * 100 >= DROP_PCT:
                pct = (row[0] - price) / row[0] * 100
                tag = "🔻 sasta" if pct > 0 else "🔺 mehnga"
                alerts.append(f"{tag} {abs(pct):.0f}% | Amazon {cat}\n{title}\nAb ₹{price:,.0f} (pehle ₹{row[0]:,.0f})\n{BASE}/dp/{asin}")
            db.execute("INSERT OR REPLACE INTO amz(asin,title,price) VALUES(?,?,?)", (asin, title, price))
        db.commit()
        time.sleep(random.uniform(4, 8))
    print("AMZ counts:", counts)
    for i in range(0, min(len(alerts), 40), 8):
        tg("Amazon price changes:\n\n" + "\n\n".join(alerts[i:i + 8]))
    if os.getenv("STATUS", "1") == "1":
        tg("Amazon check done:\n" + "\n".join(counts))


if __name__ == "__main__":
    try:
        run_once()
    except Exception as e:
        print("AMZ failed:", e)
