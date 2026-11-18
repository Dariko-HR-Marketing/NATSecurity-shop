import urllib.request
import urllib.parse
import json
import time
import os

BOT_TOKEN = "8884858490:AAHl3OQN3rEjX1_hnJEKqTkC0tu9ybY5qOs"
WEBAPP_URL = "https://dariko-hr-marketing.github.io/NATSecurity-shop/"
ADMIN_CHAT_ID = 944857221  # Sizning Telegram ID'ingiz

USERS_DB_FILE = os.path.join(os.path.dirname(__file__), "users_db.json")

def load_users():
    if os.path.exists(USERS_DB_FILE):
        try:
            with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def send_telegram_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Xabar yuborishda xatolik ({chat_id}):", e)
        return None

def main():
    print("==================================================")
    print("🛡️ NAT Security Bot (@NATSecurity_bot) ishga tushdi!")
    print("Ro'yxatdan o'tish va buyurtmalar kuzatilmoqda...")
    print("==================================================")
    
    users = load_users()
    offset = 0

    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=20"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=25) as resp:
                updates = json.loads(resp.read().decode('utf-8'))

            for u in updates.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message")
                if not msg:
                    continue

                chat_id = msg.get("chat", {}).get("id")
                from_user = msg.get("from", {})
                first_name = from_user.get("first_name", "Foydalanuvchi")
                last_name = from_user.get("last_name", "")
                username = from_user.get("username", "")
                user_key = str(chat_id)

                # 1. Kontakt yuborilganda (Registratsiya yakunlanishi)
                if "contact" in msg:
                    contact = msg["contact"]
                    phone_number = contact.get("phone_number", "")
                    
                    users[user_key] = {
                        "chat_id": chat_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "username": username,
                        "phone": phone_number,
                        "registered_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_users(users)

                    # Adminga yangi ro'yxatdan o'tgan mijoz haqida xabar
                    admin_alert = (
                        "👤 <b>YANGI MIJOZ RO'YXATDAN O'TDI!</b>\n\n"
                        f"• <b>Ism:</b> {first_name} {last_name}\n"
                        f"• <b>Telefon:</b> <code>{phone_number}</code>\n"
                        f"• <b>Username:</b> @{username or 'yo\'q'}\n"
                        f"• <b>ID:</b> <code>{chat_id}</code>"
                    )
                    if ADMIN_CHAT_ID and ADMIN_CHAT_ID != chat_id:
                        send_telegram_message(ADMIN_CHAT_ID, admin_alert)

                    # Mijozga do'kon tugmasi
                    kb = {
                        "inline_keyboard": [
                            [
                                {"text": "🛡️ Do'kon & Smeta (Mini App)", "web_app": {"url": WEBAPP_URL}}
                            ]
                        ]
                    }
                    send_telegram_message(
                        chat_id,
                        f"✅ <b>Rahmat, {first_name}!</b>\n"
                        "Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n\n"
                        "Quyidagi tugma orqali katalog va kalkulyatordan foydalanishingiz mumkin:",
                        kb
                    )
                    continue

                # 2. Mini App'dan buyurtma kelganda
                if "web_app_data" in msg:
                    raw_data = msg["web_app_data"].get("data", "{}")
                    try:
                        order_info = json.loads(raw_data)
                        orders = order_info.get("orders", [])
                        total_sum = order_info.get("total_sum", 0)

                        items_text = ""
                        for idx, it in enumerate(orders, 1):
                            items_text += f"{idx}. <b>{it.get('name')}</b> — {it.get('qty')} ta ({it.get('price', 0):,} so'm)\n"

                        client_msg = (
                            "✅ <b>Buyurtmangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
                            f"📋 <b>Tanlangan tovarlar va xizmatlar:</b>\n{items_text}\n"
                            f"💰 <b>Jami summa:</b> <b>{total_sum:,} so'm</b>\n\n"
                            "📍 <b>Xizmat hududi:</b> Buxoro shahar va viloyati\n"
                            "📞 Tez orada mutaxassisimiz siz bilan bog'lanadi: <b>+998 91 410-99-69</b>"
                        )
                        send_telegram_message(chat_id, client_msg)

                        admin_msg = (
                            "🚨 <b>YANGI BUYURTMA KELIB TUSHDI!</b>\n\n"
                            f"👤 <b>Mijoz:</b> {first_name} (@{username or 'nomaʼlum'})\n"
                            f"🆔 <b>Chat ID:</b> <code>{chat_id}</code>\n\n"
                            f"📦 <b>Buyurtma ro'yxati:</b>\n{items_text}\n"
                            f"💵 <b>Umumiy summa:</b> <b>{total_sum:,} so'm</b>"
                        )
                        if ADMIN_CHAT_ID and ADMIN_CHAT_ID != chat_id:
                            send_telegram_message(ADMIN_CHAT_ID, admin_msg)

                    except Exception as err:
                        print("Buyurtmani o'qishda xatolik:", err)

                # 3. /start bosilganda
                elif msg.get("text") == "/start":
                    # Agar avval ro'yxatdan o'tmagan bo'lsa - raqamini so'raymiz
                    if user_key not in users:
                        reg_keyboard = {
                            "keyboard": [
                                [
                                    {"text": "📱 Telefon raqamimni ulashish", "request_contact": True}
                                ]
                            ],
                            "resize_keyboard": True,
                            "one_time_keyboard": True
                        }
                        welcome_reg = (
                            f"Assalomu alaykum, <b>{first_name}</b>!\n\n"
                            "<b>NAT Security</b> professional xavfsizlik do'koniga xush kelibsiz.\n"
                            "Xizmatlardan to'liq foydalanish va buyurtmalarni rasmiylashtirish uchun, iltimos, quyidagi tugmani bosib <b>telefon raqamingizni tasdiqlang:</b>"
                        )
                        send_telegram_message(chat_id, welcome_reg, reg_keyboard)
                    else:
                        # Ro'yxatdan o'tgan bo'lsa - darhol do'konni ochish tugmasi
                        inline_kb = {
                            "inline_keyboard": [
                                [
                                    {"text": "🛡️ Do'kon & Smeta (Mini App)", "web_app": {"url": WEBAPP_URL}}
                                ]
                            ]
                        }
                        welcome_back = (
                            f"Qaytganingizdan xursandmiz, <b>{first_name}</b>!\n\n"
                            "Do'kon, SKUD tizimlari va kalkulyatordan foydalanish uchun pastdagi tugmani bosing:"
                        )
                        send_telegram_message(chat_id, welcome_back, inline_kb)

        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()
