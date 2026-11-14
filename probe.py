import os, re, requests

SITES = {
    "Vijay Sales": "https://www.vijaysales.com/search/laptop",
    "Croma": "https://www.croma.com/searchB?q=laptop%3Arelevance&text=laptop",
    "Reliance Digital": "https://www.reliancedigital.in/search?q=laptop",
    "Myntra": "https://www.myntra.com/sports-shoes",
    "Tata CLiQ": "https://www.tatacliq.com/search/?searchCategory=all&text=laptop",
}
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
out = ["Site test:"]
for name, url in SITES.items():
    try:
        r = requests.get(url, headers=H, timeout=25)
        t = r.text
        rs = len(re.findall(r"₹|Rs\.?\s?\d|&#8377;", t))
        out.append(f"{name}: HTTP {r.status_code}, {len(t)//1000}KB, price-marks {rs}")
    except Exception as e:
        out.append(f"{name}: ERROR {str(e)[:60]}")
msg = "\n".join(out)
print(msg)
tok, chat = os.getenv("TG_TOKEN"), os.getenv("TG_CHAT")
if tok and chat:
    requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", data={"chat_id": chat, "text": msg}, timeout=15)
