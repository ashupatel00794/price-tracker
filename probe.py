import re, requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
     "Accept-Language": "en-IN,en;q=0.9", "Accept": "text/html,application/xhtml+xml"}
def subs(path):
    t = requests.get("https://www.amazon.in" + path, headers=H, timeout=25).text
    out = []
    for h, n, name in re.findall(r'href="(/gp/bestsellers/[a-z-]+(?:/\d+)*/(\d+)[^"]*)"[^>]*>\s*([^<]{2,45})<', t):
        if n not in [x[0] for x in out]:
            out.append((n, name.strip()))
    return t, out
for p in ["/gp/bestsellers/electronics", "/gp/bestsellers/shoes", "/gp/bestsellers/electronics/1389401031", "/gp/bestsellers/computers/1375424031"]:
    t, o = subs(p)
    cards = t.count('class="zg-no-numbers"')
    prices = len(re.findall(r"p13n-sc-price[^>]*>₹", t))
    print(f"AMZP {p}: size={len(t)//1000}KB cards={cards} prices={prices}")
    for n, name in o[:22]:
        print(f"AMZS {p[-18:]} {n} {name}")
