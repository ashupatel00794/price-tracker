import os
import time

COOLDOWN_H = float(os.getenv("ALERT_COOLDOWN_H", "24"))


def _init(db):
    db.execute("CREATE TABLE IF NOT EXISTS alerted(key TEXT PRIMARY KEY, ts REAL)")


def recent(db, key):
    """True if this item was already alerted within the cooldown window."""
    _init(db)
    row = db.execute("SELECT ts FROM alerted WHERE key=?", (key,)).fetchone()
    return bool(row and time.time() - row[0] < COOLDOWN_H * 3600)


def mark(db, key):
    _init(db)
    db.execute("INSERT OR REPLACE INTO alerted(key, ts) VALUES(?, ?)", (key, time.time()))


def chats():
    """All Telegram chat ids: TG_CHAT secret (comma separated) + people who pressed Start."""
    import sqlite3
    ids = [c.strip() for c in os.getenv("TG_CHAT", "").split(",") if c.strip()]
    try:
        db = sqlite3.connect("fk.db")
        db.execute("CREATE TABLE IF NOT EXISTS subs(chat TEXT PRIMARY KEY)")
        ids += [r[0] for r in db.execute("SELECT chat FROM subs")]
    except Exception:
        pass
    return list(dict.fromkeys(ids))


def offer_new(db, key, pct, thr):
    """True only when an item newly crosses the offer threshold (or its offer grows by 5+ points)."""
    db.execute("CREATE TABLE IF NOT EXISTS offers(key TEXT PRIMARY KEY, pct REAL)")
    row = db.execute("SELECT pct FROM offers WHERE key=?", (key,)).fetchone()
    if pct < thr:
        if row:
            db.execute("DELETE FROM offers WHERE key=?", (key,))
        return False
    return row is None or pct >= row[0] + 5


def offer_mark(db, key, pct):
    db.execute("INSERT OR REPLACE INTO offers(key, pct) VALUES(?, ?)", (key, pct))
