import urllib.request
import urllib.parse
import json
import time
import sys

BOT_TOKEN = "9065226331:AAFLbs-1HgtFS05diSxF9FcxisuwZjzB2eE"
WEBAPP_URL = "https://dariko-hr-marketing.github.io/NATSecurity-shop/"
ADMIN_CHAT_ID = 944857221  # Sizning Telegram chat ID'ingiz

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
    print("🛡️ NAT Security Bot (@NATSecurityShop_bot) ishga tushdi!")
    print("Buyurtmalar va xabarlar kuzatilmoqda...")
    print("==================================================")
    
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
                username = from_user.get("username", "")

                # 1. Mini App'dan buyurtma kelganda
                if "web_app_data" in msg:
                    raw_data = msg["web_app_data"].get("data", "{}")
                    try:
                        order_info = json.loads(raw_data)
                        orders = order_info.get("orders", [])
                        total_sum = order_info.get("total_sum", 0)

                        items_text = ""
                        for idx, it in enumerate(orders, 1):
                            items_text += f"{idx}. <b>{it.get('name')}</b> — {it.get('qty')} ta ({it.get('price', 0):,} so'm)\n"

                        # Mijozga yuboriladigan chek
                        client_msg = (
                            "✅ <b>Buyurtmangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
                            f"📋 <b>Tanlangan tovarlar va xizmatlar:</b>\n{items_text}\n"
                            f"💰 <b>Jami summa:</b> <b>{total_sum:,} so'm</b>\n\n"
                            "📍 <b>Xizmat hududi:</b> Buxoro shahar va viloyati\n"
                            "📞 Tez orada mutaxassisimiz siz bilan bog'lanadi: <b>+998 91 410-99-69</b>"
                        )
                        send_telegram_message(chat_id, client_msg)

                        # Adminga yuboriladigan xabarnoma
                        admin_msg = (
                            "🚨 <b>YANGI BUYURTMA KELIB TUSHDI!</b>\n\n"
                            f"👤 <b>Mijoz:</b> {first_name} (@{username or 'nomaʼlum'})\n"
                            f"🆔 <b>Chat ID:</b> <code>{chat_id}</code>\n\n"
                            f"📦 <b>Buyurtma ro'yxati:</b>\n{items_text}\n"
                            f"💵 <b>Umumiy summa:</b> <b>{total_sum:,} so'm</b>"
                        )
                        if ADMIN_CHAT_ID and ADMIN_CHAT_ID != chat_id:
                            send_telegram_message(ADMIN_CHAT_ID, admin_msg)

                        print(f"[Yangi Buyurtma] Mijoz: {first_name}, Summa: {total_sum}")

                    except Exception as err:
                        print("Buyurtmani o'qishda xatolik:", err)
                        send_telegram_message(chat_id, "Buyurtma qabul qilindi. Tez orada bog'lanamiz!")

                # 2. /start buyrug'i bosilganda
                elif msg.get("text") == "/start":
                    keyboard = {
                        "inline_keyboard": [
                            [
                                {"text": "🛡️ Do'kon & Smeta (Mini App)", "web_app": {"url": WEBAPP_URL}}
                            ]
                        ]
                    }
                    welcome_text = (
                        f"Assalomu alaykum, <b>{first_name}</b>!\n\n"
                        "<b>NAT Security</b> professional xavfsizlik va SKUD tizimlari rasmiy do'koniga xush kelibsiz.\n\n"
                        "Quyidagi xizmatlarimizdan foydalanishingiz mumkin:\n"
                        "• 📹 <b>Videokuzatuv kameralari</b> (IP, ColorVu, PTZ 360°)\n"
                        "• 🚪 <b>SKUD</b> (Face ID, aqlli qulflar, turniketlar)\n"
                        "• 🧮 <b>Onlayn Smeta Kalkulyatori</b>\n"
                        "• 📐 <b>Bepul muhandis ko'rigi</b> (Buxoro viloyati)\n\n"
                        "📞 Aloqa: <b>+998 91 410-99-69</b>\n\n"
                        "Do'konni ochish uchun pastdagi tugmani bosing:"
                    )
                    send_telegram_message(chat_id, welcome_text, keyboard)

        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()
