import os, re, sqlite3, time, random
import requests
from bs4 import BeautifulSoup

DROP_PCT = float(os.getenv("DROP_PCT", "15"))
TG_TOKEN = os.getenv("TG_TOKEN", "")
TG_CHAT = os.getenv("TG_CHAT", "")
CATEGORIES = {
    "Android Phone": "android smartphone",
    "iPhone": "iphone",
    "Laptop": "laptop",
    "Headphones/Earbuds": "headphones earbuds",
    "Monitor": "monitor",
    "PC Gaming": "gaming keyboard mouse headset",
    "SSD": "ssd",
    "RAM": "ram laptop desktop",
    "Hard Drive": "external hard drive",
    "Cables": "usb cable",
    "iPhone Cable": "iphone lightning cable",
    "Sunglasses": "sunglasses",
    "Shoes": "sports shoes",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
db = sqlite3.connect("fk.db")
db.execute("CREATE TABLE IF NOT EXISTS fk(pid TEXT PRIMARY KEY, title TEXT, price REAL)")
def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    items, titles = {}, {}
    for a in soup.select('a[href*="/p/itm"]'):
        m = re.search(r"/p/(itm[a-z0-9]+)", a["href"])
        if not m:
            continue
        pid = m.group(1)
        slug = a["href"].split("/p/")[0].strip("/").split("/")[-1].replace("-", " ").title()
        t = a.get("title") or a.get_text(" ", strip=True)
        if not t:
            img = a.find("img")
            t = img.get("alt", "") if img else ""
        if len(t) < 8 or "₹" in t:
            t = slug
        if len(t) > len(titles.get(pid, "")):
            titles[pid] = t
        if pid in items:
            continue
        node, prices = a, []
        for _ in range(7):
            prices = re.findall(r"₹\s?([\d,]{3,9})", node.get_text(" ", strip=True))
            if prices or node.parent is None:
                break
            node = node.parent
        if prices:
            items[pid] = (float(prices[0].replace(",", "")), a["href"].split("?")[0])
    return [(pid, titles.get(pid, pid)[:70], p, link) for pid, (p, link) in items.items()]
def fetch(q):
    r = requests.get("https://www.flipkart.com/search", params={"q": q}, headers=HEADERS, timeout=25)
    if r.status_code != 200:
        raise RuntimeError(f"status {r.status_code}")
    return parse(r.text)
def tg(text):
    print(text)
    if TG_TOKEN and TG_CHAT:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                      data={"chat_id": TG_CHAT, "text": text[:4000], "disable_web_page_preview": True}, timeout=15)

# end of tgdef run_once():
    alerts, counts = [], []
    for cat, q in CATEGORIES.items():
        try:
            items = fetch(q)
        except Exception as e:
            counts.append(f"{cat}: ERROR {e}"); continue
        counts.append(f"{cat}: {len(items)} items")
        for pid, title, price, link in items:
            row = db.execute("SELECT price FROM fk WHERE pid=?", (pid,)).fetchone()
            if row and row[0] > 0 and (row[0] - price) / row[0] * 100 >= DROP_PCT:
                pct = (row[0] - price) / row[0] * 100
                alerts.append(f"🔻 {pct:.0f}% sasta | {cat}\n{title}\nAb ₹{price:,.0f} (pehle ₹{row[0]:,.0f})\nhttps://www.flipkart.com{link}")
            db.execute("INSERT OR REPLACE INTO fk(pid,title,price) VALUES(?,?,?)", (pid, title, price))
        db.commit()
        time.sleep(random.uniform(4, 9))
    if alerts:
        tg("Flipkart price drops:\n\n" + "\n\n".join(alerts[:10]))
    if os.getenv("STATUS", "1") == "1":
        tg("Flipkart check done:\n" + "\n".join(counts))

if __name__ == "__main__":
    run_once()
# end of parse
