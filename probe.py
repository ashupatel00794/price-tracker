import os, re, requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
t = requests.get("https://www.vijaysales.com/c/laptops", headers=H, timeout=25).text
links = list(dict.fromkeys(re.findall(r'(/p/[^"#?\\]+)', t)))
out = [f"laptops links {len(links)}, price keys {t.count(chr(34) + 'price' + chr(34))}"]
for u in links[1:3]:
    i = t.find(u)
    out.append("--- " + t[max(0, i - 250):i + 450].replace("\n", " "))
msg = "\n".join(out)[:3800]
print(msg)
tok, chat = os.getenv("TG_TOKEN"), os.getenv("TG_CHAT")
if tok and chat:
    requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", data={"chat_id": chat, "text": msg}, timeout=15)
