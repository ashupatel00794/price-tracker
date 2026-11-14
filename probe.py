import os, requests

tok, chat = os.getenv("TG_TOKEN"), os.getenv("TG_CHAT")
print("have token", bool(tok), "have chat", bool(chat))
for text in [
    "Amazon test message (delivery check)\n🔻 sasta 5% | Amazon Laptop\nTest item\nAb ₹10,000 (pehle ₹10,500)\nhttps://www.amazon.in/dp/B098NS6PVG",
    "Vijay Sales test message (delivery check)\n🔻 sasta 5% | Vijay Sales Laptop\nTest item\nAb ₹10,000 (pehle ₹10,500)\nhttps://www.vijaysales.com/p/259536/hp-laptop",
]:
    r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                      data={"chat_id": chat, "text": text, "disable_web_page_preview": True}, timeout=15)
    print("TG", r.status_code, r.text[:160])
