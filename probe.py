import re, requests

DESK = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
        "Accept-Language": "en-IN,en;q=0.9", "Accept": "text/html,application/xhtml+xml"}
MOB = {"User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36",
       "Accept-Language": "en-IN,en;q=0.9", "Accept": "text/html,application/xhtml+xml"}
TESTS = [
    ("search desktop", "https://www.amazon.in/s?k=laptop", DESK),
    ("search mobile", "https://www.amazon.in/s?k=laptop", MOB),
    ("bestsellers", "https://www.amazon.in/gp/bestsellers/computers", DESK),
    ("deals", "https://www.amazon.in/deals", DESK),
    ("goldbox", "https://www.amazon.in/gp/goldbox", DESK),
    ("home", "https://www.amazon.in/", DESK),
]
for name, url, h in TESTS:
    try:
        r = requests.get(url, headers=h, timeout=25)
        t = r.text
        low = t.lower()
        print(f"AMZ {name}: HTTP {r.status_code} size={len(t)//1000}KB asin={t.count('data-asin=')} rs={t.count('₹')} captcha={'captcha' in low} robot={'robot' in low}")
    except Exception as e:
        print(f"AMZ {name}: ERR {str(e)[:80]}")
