import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# BotFather'dan olingan @NATSecurityShop_bot tokeni
BOT_TOKEN = "9065226331:AAFLbs-1HgtFS05diSxF9FcxisuwZjzB2eE"

# Mini App joylashgan HTTPS manzili (GitHub Pages)
WEBAPP_URL = "https://dariko-hr-marketing.github.io/NATSecurity-shop/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛡️ NAT Security Do'kon & Smeta",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="📞 Buxoro Qo'ng'iroq (+998 91 410-99-69)",
                    url="tel:+998914109969"
                )
            ]
        ]
    )
    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>!\n\n"
        "<b>NAT Security</b> professional xavfsizlik va SKUD tizimlari rasmiy botiga xush kelibsiz.\n\n"
        "Quyidagi xizmatlarimizdan foydalanishingiz mumkin:\n"
        "• 📹 <b>Videokuzatuv kameralari</b> (IP, ColorVu, PTZ 360°)\n"
        "• 🚪 <b>SKUD tizimlari</b> (Face ID, biometrik qulflar, turniketlar)\n"
        "• 🧮 <b>Onlayn Smeta Kalkulyatori</b> (Obyektingiz narxini hisoblash)\n"
        "• 📐 <b>Bepul muhandis ko'rigi</b> (Buxoro shahar va viloyatida)\n\n"
        "Do'kon va kalkulyatorni ochish uchun pastdagi tugmani bosing:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.message(F.web_app_data)
async def web_app_order_handler(message: types.Message):
    raw_data = message.web_app_data.data
    try:
        data = json.loads(raw_data)
        orders = data.get("orders", [])
        total_sum = data.get("total_sum", 0)
        user = data.get("user", {})

        items_text = ""
        for i, item in enumerate(orders, 1):
            items_text += f"{i}. <b>{item['name']}</b> — {item['qty']} dona ({item['price']:,} so'm)\n"

        response_text = (
            "✅ <b>Buyurtmangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
            f"👤 <b>Mijoz:</b> {user.get('first_name', '')} {user.get('last_name', '')} (@{user.get('username', 'nomaʼlum')})\n"
            f"📦 <b>Tanlangan tovarlar va xizmatlar:</b>\n{items_text}\n"
            f"💰 <b>Jami summa:</b> <b>{total_sum:,} so'm</b>\n\n"
            "📍 <b>Hudud:</b> Buxoro shahar va viloyati bo'ylab yetkazish va montaj\n"
            "📞 Mutaxassisimiz tez orada siz bilan bog'lanadi.\n"
            "Savollar uchun: <b>+998 91 410-99-69</b>"
        )
        await message.answer(response_text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"Buyurtma qabul qilindi: {raw_data}")

async def main():
    print("NAT Security Bot (@NATSecurityShop_bot) ishga tushirildi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
