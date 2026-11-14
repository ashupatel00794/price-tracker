import json, os, re, sqlite3, time, random
import requests
from bs4 import BeautifulSoup

CHECK_EVERY_MIN = int(os.getenv("CHECK_EVERY_MIN", "60"))
TG_TOKEN = os.getenv("TG_TOKEN", "")
TG_CHAT = os.getenv("TG_CHAT", "")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
db = sqlite3.connect("prices.db")
db.execute("CREATE TABLE IF NOT EXISTS prices(url TEXT, price REAL, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")

def get_price(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200 or "captcha" in r.text.lower():
        raise RuntimeError(f"Blocked/failed (status {r.status_code})")
    soup = BeautifulSoup(r.text, "html.parser")
    el = soup.select_one("span.a-price span.a-offscreen") or soup.select_one("#priceblock_ourprice")
    if not el:
        raise RuntimeError("Price not found")
    return float(re.sub(r"[^\d.]", "", el.get_text().replace(",", "")))

def notify(msg):
    print(msg)
    if TG_TOKEN and TG_CHAT:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                      data={"chat_id": TG_CHAT, "text": msg}, timeout=15)

def check_all():
    for item in json.load(open("items.json")):
        url, target = item["url"], item["target"]
        try:
            p = get_price(url)
        except Exception as e:
            print("Error:", url, e); continue
        last = db.execute("SELECT price FROM prices WHERE url=? ORDER BY ts DESC LIMIT 1", (url,)).fetchone()
        db.execute("INSERT INTO prices(url, price) VALUES(?,?)", (url, p)); db.commit()
        if p <= target and (not last or last[0] != p):
            notify(f"Price drop! {item.get('name', url)}\nAb: {p}  (target {target})\n{url}")
        time.sleep(random.uniform(3, 8))

if __name__ == "__main__":
    if os.getenv("ONCE"):
        check_all(); raise SystemExit
    while True:
        check_all()
        time.sleep(CHECK_EVERY_MIN * 60)
