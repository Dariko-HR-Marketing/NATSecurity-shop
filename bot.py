import urllib.request
import urllib.parse
import json
import time
import os

BOT_TOKEN = "8884858490:AAHl3OQN3rEjX1_hnJEKqTkC0tu9ybY5qOs"
WEBAPP_URL = "https://dariko-hr-marketing.github.io/NATSecurity-shop/"
ADMIN_CHAT_ID = 944857221  # NAT Security Admin

USERS_DB_FILE = os.path.join(os.path.dirname(__file__), "users_db.json")

def load_db():
    if os.path.exists(USERS_DB_FILE):
        try:
            with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"users": {}, "orders": []}
    return {"users": {}, "orders": []}

def save_db(db):
    with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def send_telegram_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Xabar yuborishda xatolik: {e}")
        return None

def handle_updates():
    offset = 0
    print("NAT Security 5-Bosqichli Professional CRM Bot ishga tushdi...")
    db = load_db()

    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=20"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=25) as response:
                result = json.loads(response.read().decode())
                updates = result.get("result", [])

                for update in updates:
                    offset = update["update_id"] + 1

                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        user_info = msg.get("from", {})
                        first_name = user_info.get("first_name", "Mijoz")
                        username = user_info.get("username", "")

                        # Kontakt yuborilganda (1-Bosqich: Asosiy shaxsiy identifikatsiya)
                        if "contact" in msg:
                            contact = msg["contact"]
                            phone = contact.get("phone_number", "")
                            c_name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
                            
                            uid = str(chat_id)
                            if uid not in db["users"]:
                                db["users"][uid] = {
                                    "user_id": chat_id,
                                    "full_name": c_name or first_name,
                                    "username": f"@{username}" if username else "Mavjud emas",
                                    "phone": phone,
                                    "client_type": "Jismoniy shaxs",
                                    "location": "Buxoro",
                                    "address": "Aniqlanmoqda",
                                    "object_type": "Xususiy xonadon / Obyekt",
                                    "interest": "Videokuzatuv & Xavfsizlik",
                                    "crm_status": "Yangi",
                                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                                }
                            else:
                                db["users"][uid]["phone"] = phone
                                db["users"][uid]["full_name"] = c_name or first_name

                            save_db(db)

                            # Adminga CRM xabari
                            admin_notify = (
                                f"👤 <b>YANGI MIJOZ RO'YXATDAN O'TDI! (CRM)</b>\n\n"
                                f"▫️ <b>F.I.O:</b> {db['users'][uid]['full_name']}\n"
                                f"▫️ <b>Telefon:</b> {phone}\n"
                                f"▫️ <b>Telegram:</b> @{username} (ID: {chat_id})\n"
                                f"▫️ <b>CRM Holati:</b> 🟢 Yangi\n"
                                f"▫️ <b>Sana:</b> {db['users'][uid]['created_at']}"
                            )
                            send_telegram_message(ADMIN_CHAT_ID, admin_notify)

                            # Mijozga minnatdorchilik va Mini App tugmasi
                            reply_kb = {
                                "keyboard": [
                                    [{"text": "🛡️ NAT Security Do'koni & Kalkulyator", "web_app": {"url": WEBAPP_URL}}],
                                    [{"text": "📍 Obyekt manzilini yuborish (GPS)", "request_location": True}],
                                    [{"text": "📞 Mutaxassis bilan bog'lanish"}]
                                ],
                                "resize_keyboard": True
                            }
                            send_telegram_message(
                                chat_id,
                                f"✅ Rahmat, <b>{first_name}</b>! Ma'lumotlaringiz NAT Security tizimida muvaffaqiyatli ro'yxatga olindi.\n\n"
                                f"Pastdagi tugma orqali katalogimizdan kameralar, turniketlar va smart qulflarni ko'rishingiz hamda hisob-kitob qilishingiz mumkin:",
                                reply_kb
                            )

                        # Lokatsiya yuborilganda (2-Bosqich: Obyekt geolokatsiyasi)
                        elif "location" in msg:
                            loc = msg["location"]
                            lat, lon = loc["latitude"], loc["longitude"]
                            uid = str(chat_id)
                            if uid in db["users"]:
                                db["users"][uid]["geo"] = {"lat": lat, "lon": lon}
                                db["users"][uid]["crm_status"] = "Ko'rik belgilandi"
                                save_db(db)

                            admin_loc_notify = (
                                f"📍 <b>OBYEKT LOKATSIYASI KELIB TUSHDI!</b>\n\n"
                                f"▫️ <b>Mijoz:</b> {first_name} (@{username})\n"
                                f"▫️ <b>Koordinatalar:</b> {lat}, {lon}\n"
                                f"▫️ <a href='https://maps.google.com/?q={lat},{lon}'>Google Maps xaritasida ochish</a>"
                            )
                            send_telegram_message(ADMIN_CHAT_ID, admin_loc_notify)
                            send_telegram_message(chat_id, "📍 Obyektingiz geolokatsiyasi qabul qilindi. Mutaxassislarimiz borish joyini xaritada belgiladi!")

                        # /start komandasi
                        elif "text" in msg:
                            text = msg["text"]
                            if text == "/start":
                                kb = {
                                    "keyboard": [
                                        [{"text": "📲 Telefon raqamimni yuborish (Ro'yxatdan o'tish)", "request_contact": True}],
                                        [{"text": "🛡️ NAT Security Do'koni (Mini App)", "web_app": {"url": WEBAPP_URL}}],
                                        [{"text": "📍 Obyekt manzilini yuborish", "request_location": True}]
                                    ],
                                    "resize_keyboard": True
                                }
                                welcome_text = (
                                    f"Assalomu alaykum, <b>{first_name}</b>!\n\n"
                                    f"<b>NAT Security</b> — Buxorodagi professional xavfsizlik va videokuzatuv tizimlari markaziga xush kelibsiz!\n\n"
                                    f"🏢 <b>Bizning xizmatlar:</b>\n"
                                    f"• Hikvision, Dahua 4K & ColorVu kameralari\n"
                                    f"• SKUD Face ID va Smart biometrik qulflar\n"
                                    f"• Turniketlar va avtomatik shlagbaumlar\n"
                                    f"• Bepul loyihalash, smeta va 1 yillik kafolat\n\n"
                                    f"<i>Buyurtma va hisob-kitoblar uchun pastdagi tugma orqali telefon raqamingizni yuboring:</i>"
                                )
                                send_telegram_message(chat_id, welcome_text, kb)

                            elif text == "📞 Mutaxassis bilan bog'lanish":
                                send_telegram_message(
                                    chat_id,
                                    "📞 <b>NAT Security Aloqa Markazi:</b>\n\n"
                                    "📱 Telefon: <b>+998 91 410-99-69</b>\n"
                                    "📍 Manzil: Buxoro shahri\n"
                                    "🌐 Sayt: natsecurity.uz\n\n"
                                    "Har kuni 09:00 dan 20:00 gacha xizmatingizdamiz!"
                                )

        except Exception as e:
            time.sleep(3)

if __name__ == "__main__":
    handle_updates()
