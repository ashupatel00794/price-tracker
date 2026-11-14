import os, re, sqlite3, time, random
import requests
from bs4 import BeautifulSoup

DROP_PCT = float(os.getenv("DROP_PCT", "15"))
TG_TOKEN = os.getenv("TG_TOKEN", "")
TG_CHAT = os.getenv("TG_CHAT", "")
CATEGORIES = {
    "Android Phone": "android smartphone",
    "iPhone": "iphone",
    "Laptop": "laptop",
    "Headphones/Earbuds": "headphones earbuds",
    "Monitor": "monitor",
    "PC Gaming": "gaming keyboard mouse headset",
    "SSD": "ssd",
    "RAM": "ram laptop desktop",
    "Hard Drive": "external hard drive",
    "Cables": "usb cable",
    "iPhone Cable": "iphone lightning cable",
    "Sunglasses": "sunglasses",
    "Shoes": "sports shoes",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
db = sqlite3.connect("fk.db")
db.execute("CREATE TABLE IF NOT EXISTS fk(pid TEXT PRIMARY KEY, title TEXT, price REAL)")
