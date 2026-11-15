import os, re, sqlite3, time, random
import requests
import dedupe
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
    seen = {}
    for pg in (1, 2, 3):
        r = requests.get("https://www.flipkart.com/search", params={"q": q, "page": pg}, headers=HEADERS, timeout=25)
        if r.status_code != 200:
            if pg == 1:
                raise RuntimeError(f"status {r.status_code}")
            break
        got = parse(r.text)
        if not got:
            break
        for it in got:
            seen.setdefault(it[0], it)
        time.sleep(random.uniform(2, 4))
    return list(seen.values())

def tg(text):
    print(text)
    if TG_TOKEN and TG_CHAT:
        for chat in [c.strip() for c in TG_CHAT.split(",") if c.strip()]:
            r = requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                              data={"chat_id": chat, "text": text[:4000], "disable_web_page_preview": True}, timeout=15)
            print("TG", r.status_code, r.text[:80])

def run_once():
    alerts, counts = [], []
    for cat, q in CATEGORIES.items():
        try:
            items = fetch(q)
        except Exception as e:
            counts.append(f"{cat}: ERROR {e}"); continue
        counts.append(f"{cat}: {len(items)} items")
        for pid, title, price, link in items:
            row = db.execute("SELECT price FROM fk WHERE pid=?", (pid,)).fetchone()
            if row and row[0] > 0 and abs(row[0] - price) / row[0] * 100 >= DROP_PCT and not dedupe.recent(db, "fk:" + pid):
                pct = (row[0] - price) / row[0] * 100
                tag = "🔻 sasta" if pct > 0 else "🔺 mehnga"
                alerts.append(f"{tag} {abs(pct):.1f}% | {cat}\n{title}\nAb ₹{price:,.0f} (pehle ₹{row[0]:,.0f})\nhttps://www.flipkart.com{link}")
                dedupe.mark(db, "fk:" + pid)
            db.execute("INSERT OR REPLACE INTO fk(pid,title,price) VALUES(?,?,?)", (pid, title, price))
        db.commit()
        time.sleep(random.uniform(4, 9))
    for i in range(0, min(len(alerts), 240), 8):
        tg("Flipkart price changes:\n\n" + "\n\n".join(alerts[i:i + 8]))
    if os.getenv("STATUS", "1") == "1":
        tg("Flipkart check done:\n" + "\n".join(counts))

if __name__ == "__main__":
    run_once()
