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
