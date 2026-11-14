import os, re, requests

URL = "https://www.vijaysales.com/search/laptop"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
html = requests.get(URL, headers=H, timeout=25).text
out = [f"VijaySales {len(html)//1000}KB, ldjson {html.count('ld+json')}"]
n = 0
for m in re.finditer("₹", html):
    win = html[max(0, m.start() - 700):m.start() + 40]
    hrefs = re.findall(r'href="([^"]+)"', win)
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", win))[-150:]
    out.append(f"[{n}] {hrefs[-1] if hrefs else None} | {text}")
    n += 1
    if n >= 4:
        break
msg = "\n".join(out)[:3800]
print(msg)
tok, chat = os.getenv("TG_TOKEN"), os.getenv("TG_CHAT")
if tok and chat:
    requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", data={"chat_id": chat, "text": msg}, timeout=15)
