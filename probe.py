import re, requests
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36"}
html = requests.get("https://www.vijaysales.com/c/laptops", headers=H, timeout=25).text
for m in re.finditer(r"unbxd|apiKey|siteKey|api_key|site_key|search\.unbxd", html, re.I):
    print("VJS", html[max(0,m.start()-100):m.start()+200].replace("\n"," "))
    break
for k in ["unbxd","apiKey","siteKey","adobeioruntime","api/v1"]:
    for m in list(re.finditer(k, html))[:3]:
        print("VJS", k, "::", html[max(0,m.start()-150):m.start()+250].replace("\n"," "))
