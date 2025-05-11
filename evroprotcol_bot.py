import telebot
from telebot import types

TOKEN = '7219842852:AAHdEm-iJoY4x1dxXTmHvLn18uH53mLkfQQ'
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 7120585371  # O'zingizning Telegram ID
user_lang = {}
user_locations = {}
user_contacts = {}

# START
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    uz = types.KeyboardButton("🇺🇿 O'zbekcha")
    ru = types.KeyboardButton("🇷🇺 Русский")
    markup.add(uz, ru)
    bot.send_message(message.chat.id, "Tilni tanlang / Выберите язык:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["🇺🇿 O'zbekcha", "🇷🇺 Русский"])
def set_language(message):
    lang = 'uz' if "O'zbekcha" in message.text else 'ru'
    user_lang[message.chat.id] = lang

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    location_btn = types.KeyboardButton("📍 Lokatsiyani yuborish" if lang == 'uz' else "📍 Отправить локацию", request_location=True)
    phone_btn = types.KeyboardButton("📞 Telefon raqam" if lang == 'uz' else "📞 Номер телефона", request_contact=True)
    order_btn = types.KeyboardButton("📦 Buyurtma berish" if lang == 'uz' else "📦 Заказать")
    markup.add(location_btn, phone_btn, order_btn)

    text = (
        "Xush kelibsiz!\n\nIltimos, lokatsiya va telefon raqamingizni yuboring, so‘ngra 'Buyurtma berish' tugmasini bosing."
        if lang == 'uz' else
        "Добро пожаловать!\n\nПожалуйста, отправьте свою локацию и номер телефона, затем нажмите 'Заказать'."
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

# LOKATSIYA
@bot.message_handler(content_types=['location'])
def handle_location(message):
    lang = user_lang.get(message.chat.id, 'uz')
    lat = message.location.latitude
    lon = message.location.longitude
    maps_url = f"https://maps.google.com/?q={lat},{lon}"
    user_locations[message.chat.id] = maps_url

    bot.send_message(message.chat.id, "📍 Lokatsiyangiz qabul qilindi!" if lang == 'uz' else "📍 Ваша локация получена!")

    if message.chat.id in user_contacts:
        remind_to_order(message.chat.id, lang)

# TELEFON
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    lang = user_lang.get(message.chat.id, 'uz')
    phone = message.contact.phone_number
    user_contacts[message.chat.id] = phone

    bot.send_message(message.chat.id, "📞 Telefon raqamingiz qabul qilindi!" if lang == 'uz' else "📞 Ваш номер получен!")

    if message.chat.id in user_locations:
        remind_to_order(message.chat.id, lang)

def remind_to_order(chat_id, lang):
    bot.send_message(chat_id, "✅ Endi 'Buyurtma berish' tugmasini bosing." if lang == 'uz' else "✅ Теперь нажмите кнопку 'Заказать'.")

# BUYURTMA BERISH
@bot.message_handler(func=lambda m: m.text in ["📦 Buyurtma berish", "📦 Заказать"])
def handle_order(message):
    user = message.from_user
    lang = user_lang.get(message.chat.id, 'uz')
    location = user_locations.get(message.chat.id, "⚠️ Lokatsiya yo‘q")
    phone = user_contacts.get(message.chat.id, "⚠️ Raqam yo‘q")

    text_admin = (
        f"🆕 Buyurtma!\n"
        f"👤 Foydalanuvchi: {user.first_name}\n"
        f"🆔 Telegram ID: {user.id}\n"
        f"☎️ Telefon: {phone}\n"
        f"📍 Lokatsiya: {location}"
    )

    bot.send_message(ADMIN_ID, text_admin)

    bot.send_message(message.chat.id, "✅ Buyurtmangiz qabul qilindi!" if lang == 'uz' else "✅ Ваша заявка принята!")

    send_social_links(message.chat.id, lang)

def send_social_links(chat_id, lang):
    text = "📲 Bizning ijtimoiy tarmoqlar:" if lang == 'uz' else "📲 Наши социальные сети:"
    bot.send_message(chat_id, text)
    bot.send_message(chat_id, "Telegram: https://t.me/eprotocol")
    bot.send_message(chat_id, "Instagram: https://www.instagram.com/evroprotocol.uz")
    bot.send_message(chat_id, "YouTube: https://www.youtube.com/channel/UC4wpKr8-ppjnvowjniQ5vvg")
    bot.send_message(chat_id, "Web: https://eprotocoll.uz/")

# BOTNI ISHLATISH UCHUN
print("Bot ishga tushdi...")
bot.polling(none_stop=True)
