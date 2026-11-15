import re, time, requests
from bs4 import BeautifulSoup

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
     "Accept-Language": "en-IN,en;q=0.9"}
def prices(html):
    soup = BeautifulSoup(html, "html.parser")
    out = {}
    for c in soup.select("div.product-card[data-child-sku]"):
        p = c.select_one(".discountedPrice")
        if p:
            out[c["data-child-sku"]] = re.sub(r"[^\d]", "", p.get_text(" ", strip=True))
    return out, soup
r1 = requests.get("https://www.vijaysales.com/c/laptops", headers=H, timeout=25)
print("VJH", {k: v for k, v in r1.headers.items() if k.lower() in ("age", "cache-control", "cf-cache-status", "x-cache", "last-modified", "date", "etag", "server", "via", "x-served-by", "expires")})
p1, soup = prices(r1.text)
r2 = requests.get(f"https://www.vijaysales.com/c/laptops?nocache={int(time.time())}", headers=H, timeout=25)
p2, _ = prices(r2.text)
print("VJ same-vs-bust: n1", len(p1), "n2", len(p2), "diff", sum(1 for k in p1 if k in p2 and p1[k] != p2[k]))
c = soup.select_one("div.product-card[data-child-sku]")
print("VJ card attrs", {k: str(v)[:60] for k, v in c.attrs.items()})
print("VJ price attrs", [(e.name, {k: str(v)[:40] for k, v in e.attrs.items() if k != 'class'}, e.get("class")) for e in c.select('[class*="rice"]')][:8])
print("VJ sample prices", list(p1.items())[:6])
print("VJ scripts w/ api", sorted(set(re.findall(r'https?://[^"\'\s]*(?:api|price|product)[^"\'\s]{0,60}', r1.text)))[:12])
