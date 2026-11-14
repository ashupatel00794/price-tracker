import re, requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
     "Accept-Language": "en-IN,en;q=0.9", "Accept": "text/html,application/xhtml+xml"}
t = requests.get("https://www.amazon.in/gp/bestsellers/computers", headers=H, timeout=25).text
i = t.find('data-asin=')
card = t[max(0, i - 300):i + 5000]
card = re.sub(r"\s+", " ", card)
card = re.sub(r'\s(?:style|data-[a-z-]+|aria-[a-z-]+|tabindex|role|id)="[^"]*"', "", card)
print("AMZCARD", card[:2600])
subs = re.findall(r'href="(/gp/bestsellers/[a-z-]+/(\d+)[^"]*)"[^>]*>\s*([^<]{2,40})<', t)
seen = []
for h, n, name in subs:
    if n not in seen:
        seen.append(n)
        print("AMZSUB", n, name.strip(), h[:60])
    if len(seen) >= 25:
        break
