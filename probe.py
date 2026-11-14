import re, requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
CATS = ["laptops", "smartphones", "iphones", "ssd", "monitors", "hard-disks", "keyboards", "mouse",
        "pen-drives", "headphones", "earbuds", "desktops"]
pages = {}
for c in CATS:
    try:
        r = requests.get(f"https://www.vijaysales.com/c/{c}", headers=H, timeout=25, allow_redirects=True)
        t = r.text
        pages[c] = t
        cards = len(re.findall(r'class="product-card"', t))
        print(f"CAT {c}: HTTP {r.status_code} final={r.url[-40:]} size={len(t)//1000}KB cards={cards}")
    except Exception as e:
        print(f"CAT {c}: ERR {str(e)[:80]}")
t = pages.get("laptops", "")
i = t.find('class="product-card"')
card = t[i:i + 9000]
print("CARDCLASSES", sorted(set(re.findall(r'class="([^"]*(?:rice|iscount|ff|name|title)[^"]*)"', card)))[:30])
txt = re.sub(r"\s+", " ", re.sub(r"<(?!/?(?:a|div|span)\b)[^>]+>", " ", card))
print("CARD1", txt[:3500])
