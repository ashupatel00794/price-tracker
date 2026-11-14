import os, re, requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
t = requests.get("https://www.vijaysales.com/c/laptops", headers=H, timeout=25).text
print("SIZE", len(t))
print("SCRIPTS", [(m.group(1)[:40], len(m.group(2))) for m in re.finditer(r"<script([^>]*)>(.*?)</script>", t, re.S) if len(m.group(2)) > 20000])
for pid in ["261462", "261460"]:
    for n, m in enumerate(re.finditer(pid, t)):
        if n >= 4:
            break
        print(f"PID {pid} #{n} @{m.start()}:", t[max(0, m.start() - 200):m.start() + 400].replace("\n", " "))
for n, m in enumerate(re.finditer(r'"price"', t)):
    if n >= 4:
        break
    print(f"PRICE #{n} @{m.start()}:", t[max(0, m.start() - 250):m.start() + 250].replace("\n", " "))
