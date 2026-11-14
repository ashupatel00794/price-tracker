import re, requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
t = requests.get("https://www.vijaysales.com/c/laptops", headers=H, timeout=25).text
for sku in ["259536", "261462"]:
    i = t.find(f'data-child-sku="{sku}"')
    j = t.find('class="product-card"', i + 50)
    card = t[i:j if j > 0 else i + 12000]
    k = card.find("product-card__featurelist")
    seg = card[k:]
    seg = re.sub(r"\s+", " ", seg)
    seg = re.sub(r'(<(?:div|span|a|del|s|strong|p)[^>]*?)\s+(?:style|data-[a-z-]+|target|rel)="[^"]*"', r"\1", seg)
    print(f"RAWCARD {sku} len={len(card)}:", seg[:3200])
print("TITLES", len(re.findall(r'class="product-name"', t)), "PRICES", len(re.findall(r'class="[^"]*discountedPrice[^"]*"', t)))
