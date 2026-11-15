import re, requests
from urllib.parse import urljoin

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
     "Accept-Language": "en-IN,en;q=0.9"}
base = "https://www.vijaysales.com/c/laptops"
html = requests.get(base, headers=H, timeout=25).text
srcs = re.findall(r'<script[^>]+src="([^"]+)"', html)
print("VJS scripts", len(srcs))
srcs = [urljoin(base, s) for s in srcs]
srcs += [urljoin(base, s) for s in re.findall(r'(?:href|src)="([^"]+\.js[^"]*)"', html) if urljoin(base, s) not in srcs]
seen = 0
for u in dict.fromkeys(srcs):
    if "vijaysales" not in u and "adobe" not in u:
        continue
    try:
        js = requests.get(u, headers=H, timeout=25).text
    except Exception as e:
        continue
    hits = [m.start() for m in re.finditer(r"vsapimiddleware|adobeioruntime|/api/v1/web", js)]
    pri = [m.start() for m in re.finditer(r"getPrice|price_by_sku|fetchPrice|priceApi|/price|special_price|selling_price", js)]
    print(f"VJS {u[-70:]} len={len(js)} api_hits={len(hits)} price_hits={len(pri)}")
    for i in (hits[:3] + pri[:2]):
        print("VJS   ctx:", js[max(0, i - 120):i + 220].replace("\n", " "))
    seen += 1
    if seen > 25:
        break
print("VJS inline api", re.findall(r'adobeioruntime[^"\'\s<]{0,120}', html)[:6])
