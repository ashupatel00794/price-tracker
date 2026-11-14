import re, requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
     "Accept-Language": "en-IN,en;q=0.9", "Accept": "text/html,application/xhtml+xml"}
for p in ["/gp/bestsellers/electronics/92071051031", "/gp/bestsellers/electronics/1389401031"]:
    t = requests.get("https://www.amazon.in" + p, headers=H, timeout=25).text
    seen = []
    for h, n, name in re.findall(r'href="(/gp/bestsellers/[a-z-]+(?:/\d+)*/(\d+)[^"]*)"[^>]*>\s*([^<]{2,45})<', t):
        if n not in seen:
            seen.append(n)
            print("AMZS", p[-12:], n, name.strip())
