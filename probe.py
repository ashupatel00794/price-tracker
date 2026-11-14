import os, re, requests

BASE = "https://www.vijaysales.com"
CATS = ["laptops", "smartphones", "ssd", "monitors"]
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
out = ["Vijay category test"]
for c in CATS:
    try:
        r = requests.get(f"{BASE}/c/{c}", headers=H, timeout=25)
        t = r.text
        links = re.findall(r'href="(?:https://www\.vijaysales\.com)?(/p/[^"#?]+)', t)
        uniq = list(dict.fromkeys(links))
        out.append(f"{c}: HTTP {r.status_code}, {len(t)//1000}KB, links {len(uniq)}, Rs {t.count('₹')}")
        for u in uniq[:2]:
            i = t.find(u)
            txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t[i:i + 1500]))[:150]
            out.append(f"  {u[:60]} | {txt}")
    except Exception as e:
        out.append(f"{c}: ERROR {str(e)[:60]}")
msg = "\n".join(out)[:3800]
print(msg)
tok, chat = os.getenv("TG_TOKEN"), os.getenv("TG_CHAT")
if tok and chat:
    requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", data={"chat_id": chat, "text": msg}, timeout=15)
