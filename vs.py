import os, re, sqlite3, time, random
import requests
import dedupe
from bs4 import BeautifulSoup

BASE = "https://www.vijaysales.com"
DROP_PCT = float(os.getenv("DROP_PCT", "15"))
OFFER_PCT = float(os.getenv("OFFER_PCT", "40"))
EXTRA = {}  # sku -> (mrp, discount %)
TG_TOKEN = os.getenv("TG_TOKEN", "")
TG_CHAT = os.getenv("TG_CHAT", "")
K = "bb8ef7667d38c04e8a81c80f4a43a998"
SITE = "ss-unbxd-aapac-prod-vijaysales-magento33881704883825"
API = f"https://search.unbxd.io/{K}/{SITE}/search"
QUERIES = {
    "Smartphone": "smartphone", "iPhone": "iphone", "Laptop": "laptop",
    "Headphones": "headphones", "Earbuds": "earbuds", "Mouse": "mouse",
    "Keyboard": "keyboard", "SSD": "ssd", "Hard Disk": "hard disk",
    "Pen Drive": "pen drive", "Monitor": "monitor", "Desktop": "desktop",
    "RAM": "ram", "Gaming": "gaming", "Cable": "cable",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36"}


def fetch(q, pages=3, rows=100):
    out = {}
    for pg in range(pages):
        r = requests.get(API, params={"q": q, "rows": rows, "start": pg * rows}, headers=HEADERS, timeout=25)
        r.raise_for_status()
        prods = r.json()["response"]["products"]
        for p in prods:
            sku = str(p.get("uniqueId") or p.get("_root_") or "")
            try:
                price = float(p.get("price"))
            except Exception:
                continue
            link = p.get("productUrl") or ""
            title = str(p.get("title") or p.get("modelName") or "")[:70]
            if sku and price > 0 and link and sku not in out:
                out[sku] = (title, price, link)
                try:
                    EXTRA[sku] = (float(p.get("mrp") or 0), int(float(p.get("discountPercentage") or 0)))
                except Exception:
                    EXTRA[sku] = (0, 0)
        if len(prods) < rows:
            break
    return [(k, t, pr, l) for k, (t, pr, l) in out.items()]


def tg(text):
    print(text)
    if TG_TOKEN:
        for chat in dedupe.chats():
            r = requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                              data={"chat_id": chat, "text": text[:4000], "disable_web_page_preview": True}, timeout=15)
            print("TG", r.status_code, r.text[:80])


def run_once():
    db = sqlite3.connect("fk.db")
    db.execute("CREATE TABLE IF NOT EXISTS vs2(sku TEXT PRIMARY KEY, title TEXT, price REAL)")
    alerts, counts, offers = [], [], []
    for cat, slug in QUERIES.items():
        try:
            items = fetch(slug)
        except Exception as e:
            counts.append(f"{cat}: ERROR {str(e)[:60]}")
            continue
        counts.append(f"{cat}: {len(items)} items")
        for sku, title, price, link in items:
            row = db.execute("SELECT price FROM vs2 WHERE sku=?", (sku,)).fetchone()
            if row and row[0] > 0 and abs(row[0] - price) / row[0] * 100 >= DROP_PCT and not dedupe.recent(db, "vs2:" + sku):
                pct = (row[0] - price) / row[0] * 100
                tag = "🔻 sasta" if pct > 0 else "🔺 mehnga"
                alerts.append(f"{tag} {abs(pct):.1f}% | Vijay Sales {cat}\n{title}\nAb ₹{price:,.0f} (pehle ₹{row[0]:,.0f})\n{link}")
                dedupe.mark(db, "vs2:" + sku)
            mrp, off = EXTRA.get(sku, (0, 0))
            if dedupe.offer_new(db, "vs2:" + sku, off, OFFER_PCT):
                offers.append((off, sku, f"🔥 {off}% OFF | Vijay Sales {cat}\n{title}\nPrice ₹{price:,.0f} (MRP ₹{mrp:,.0f})\n{link}"))
            db.execute("INSERT OR REPLACE INTO vs2(sku,title,price) VALUES(?,?,?)", (sku, title, price))
        db.commit()
        time.sleep(1)
    print("VS counts:", counts)
    offers.sort(reverse=True)
    top = offers[:40]
    for off, sku, _ in top:
        dedupe.offer_mark(db, "vs2:" + sku, off)
    db.commit()
    for i in range(0, len(top), 8):
        tg("Vijay Sales best offers:\n\n" + "\n\n".join(t[2] for t in top[i:i + 8]))
    for i in range(0, min(len(alerts), 240), 8):
        tg("Vijay Sales price changes:\n\n" + "\n\n".join(alerts[i:i + 8]))
    if os.getenv("STATUS", "1") == "1":
        tg("Vijay Sales check done:\n" + "\n".join(counts))


if __name__ == "__main__":
    try:
        run_once()
    except Exception as e:
        print("VS failed:", e)
