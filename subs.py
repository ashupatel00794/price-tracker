import os, sqlite3
import requests

TOK = os.getenv("TG_TOKEN", "")


def api(method, **data):
    return requests.post(f"https://api.telegram.org/bot{TOK}/{method}", data=data, timeout=20).json()


def main():
    if not TOK:
        return
    db = sqlite3.connect("fk.db")
    db.execute("CREATE TABLE IF NOT EXISTS subs(chat TEXT PRIMARY KEY)")
    db.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
    row = db.execute("SELECT v FROM meta WHERE k='tg_offset'").fetchone()
    off = int(row[0]) if row else 0
    res = api("getUpdates", offset=off, timeout=0).get("result", [])
    for u in res:
        off = max(off, u["update_id"] + 1)
        m = u.get("message") or {}
        chat = m.get("chat", {})
        if chat.get("type") != "private":
            continue
        cid = str(chat["id"])
        text = (m.get("text") or "").strip().lower()
        if text.startswith("/stop"):
            db.execute("DELETE FROM subs WHERE chat=?", (cid,))
            api("sendMessage", chat_id=cid, text="Alerts band kar diye. Dobara chalu karne ke liye /start bhejo.")
        else:
            db.execute("INSERT OR IGNORE INTO subs(chat) VALUES(?)", (cid,))
            api("sendMessage", chat_id=cid, text="Aap add ho gaye. Ab Amazon, Flipkart aur Vijay Sales ke price change alerts yahan aayenge. Band karne ke liye /stop bhejo.")
        print("SUBS handled", cid, text[:20])
    db.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('tg_offset',?)", (str(off),))
    db.commit()
    print("SUBS total", db.execute("SELECT COUNT(*) FROM subs").fetchone()[0])


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("SUBS failed:", e)
