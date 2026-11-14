        if pid in items:
            continue
        node, prices = a, []
        for _ in range(7):
            prices = re.findall(r"₹\s?([\d,]{3,9})", node.get_text(" ", strip=True))
            if prices or node.parent is None:
                break
            node = node.parent
        if prices:
            items[pid] = (float(prices[0].replace(",", "")), a["href"].split("?")[0])
    return [(pid, titles.get(pid, pid)[:70], p, link) for pid, (p, link) in items.items()]

def fetch(q):
    r = requests.get("https://www.flipkart.com/search", params={"q": q}, headers=HEADERS, timeout=25)
    if r.status_code != 200:
        raise RuntimeError(f"status {r.status_code}")
    return parse(r.text)

def tg(text):
    print(text)
    if TG_TOKEN and TG_CHAT:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                      data={"chat_id": TG_CHAT, "text": text[:4000], "disable_web_page_preview": True}, timeout=15)

def run_once():
    alerts, counts = [], []
    for cat, q in CATEGORIES.items():
        try:
            items = fetch(q)
        except Exception as e:
            counts.append(f"{cat}: ERROR {e}"); continue
        counts.append(f"{cat}: {len(items)} items")
        for pid, title, price, link in items:
            row = db.execute("SELECT price FROM fk WHERE pid=?", (pid,)).fetchone()
            if row and row[0] > 0 and (row[0] - price) / row[0] * 100 >= DROP_PCT:
                pct = (row[0] - price) / row[0] * 100
                alerts.append(f"🔻 {pct:.0f}% sasta | {cat}\n{title}\nAb ₹{price:,.0f} (pehle ₹{row[0]:,.0f})\nhttps://www.flipkart.com{link}")
            db.execute("INSERT OR REPLACE INTO fk(pid,title,price) VALUES(?,?,?)", (pid, title, price))
        db.commit()
        time.sleep(random.uniform(4, 9))
    if alerts:
        tg("Flipkart price drops:\n\n" + "\n\n".join(alerts[:10]))
    if os.getenv("STATUS", "1") == "1":
        tg("Flipkart check done:\n" + "\n".join(counts))

if __name__ == "__main__":
    if os.getenv("LOOP"):
        while True:
            run_once()
            time.sleep(int(os.getenv("EVERY_MIN", "60")) * 60)
    else:
        run_once()
