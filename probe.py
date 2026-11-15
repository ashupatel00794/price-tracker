import requests, json
H = {"User-Agent": "Mozilla/5.0 Chrome/124.0"}
K="bb8ef7667d38c04e8a81c80f4a43a998"; S="ss-unbxd-aapac-prod-vijaysales-magento33881704883825"
for q in ["laptop","ssd","monitor"]:
    r = requests.get(f"https://search.unbxd.io/{K}/{S}/search", params={"q":q,"rows":5}, headers=H, timeout=25)
    print("VJS", q, r.status_code, len(r.text))
    try:
        d = r.json()
        print("VJS total", d["response"]["numberOfProducts"])
        for p in d["response"]["products"][:3]:
            print("VJS keys", list(p.keys())[:40])
            print("VJS", {k:p[k] for k in p if any(w in k.lower() for w in ["price","name","title","sku","url"])})
            break
    except Exception as e:
        print("VJS err", e, r.text[:300])
