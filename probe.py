import requests
H = {"User-Agent": "Mozilla/5.0 Chrome/124.0"}
K="bb8ef7667d38c04e8a81c80f4a43a998"; S="ss-unbxd-aapac-prod-vijaysales-magento33881704883825"
r = requests.get(f"https://search.unbxd.io/{K}/{S}/search", params={"q":"ssd","rows":2}, headers=H, timeout=25).json()
p = r["response"]["products"][0]
print("VJS", {k:(str(v)[:80]) for k,v in p.items() if not k.startswith("cityId_") and not k.startswith("categoryPath")})
