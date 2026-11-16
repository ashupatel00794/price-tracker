import re, requests
from bs4 import BeautifulSoup
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36","Accept-Language":"en-IN,en;q=0.9"}
# Amazon
h = requests.get("https://www.amazon.in/gp/bestsellers/electronics/1389432031", headers=H, timeout=25).text
li = BeautifulSoup(h,"html.parser").select_one("li.zg-no-numbers")
print("AMZ", re.sub(r"\s+"," ",li.get_text(" ",strip=True))[:300] if li else "none")
print("AMZ html", re.sub(r"\s+"," ",str(li))[:1800] if li else "")
# Flipkart
h = requests.get("https://www.flipkart.com/search?q=laptop", headers=H, timeout=25).text
s = BeautifulSoup(h,"html.parser")
a = s.select_one('a[href*="/p/itm"]')
n=a
for _ in range(6):
    if n.parent: n=n.parent
    t=n.get_text(" ",strip=True)
    if "₹" in t: break
print("FK", t[:500])
print("FK rating cands", re.findall(r"\b[1-5]\.\d\b\s*\(?[\d,]+\)?", t)[:3])
# Vijay
K="bb8ef7667d38c04e8a81c80f4a43a998"; S="ss-unbxd-aapac-prod-vijaysales-magento33881704883825"
p = requests.get(f"https://search.unbxd.io/{K}/{S}/search", params={"q":"laptop","rows":1}, headers=H, timeout=25).json()["response"]["products"][0]
print("VJS", {k:str(v)[:60] for k,v in p.items() if any(w in k.lower() for w in ["rating","review","mrp","discount","title","name","offer"]) and not k.startswith("cityId")})
