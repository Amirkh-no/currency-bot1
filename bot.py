import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8143466135:AAHiS2kJc5qNi_5AlOIYOjMHU3T8ImLoRVQ"

logging.basicConfig(level=logging.INFO)

CURRENCIES = {
    "dollar":   ("دلار آمریکا 🇺🇸",   "https://www.tgju.org/profile/price_dollar_rl"),
    "euro":     ("یورو 🇪🇺",           "https://www.tgju.org/profile/price_eur"),
    "pound":    ("پوند انگلیس 🇬🇧",    "https://www.tgju.org/profile/price_gbp"),
    "dirham":   ("درهم امارات 🇦🇪",    "https://www.tgju.org/profile/price_aed"),
    "lira":     ("لیر ترکیه 🇹🇷",      "https://www.tgju.org/profile/price_try"),
    "yuan":     ("یوان چین 🇨🇳",       "https://www.tgju.org/profile/price_cny"),
    "yen":      ("ین ژاپن 🇯🇵",        "https://www.tgju.org/profile/price_jpy"),
    "ruble":    ("روبل روسیه 🇷🇺",     "https://www.tgju.org/profile/price_rub"),
    "riyal_sa": ("ریال عربستان 🇸🇦",   "https://www.tgju.org/profile/price_sar"),
    "gold":     ("طلا 18 عیار 🥇",     "https://www.tgju.org/profile/geram18"),
    "sekke":    ("سکه امامی 🪙",       "https://www.tgju.org/profile/sekke"),
}

CRYPTO = {
    "usdt":  ("تتر 💵",            "tether"),
    "btc":   ("بیت‌کوین ₿",       "bitcoin"),
    "eth":   ("اتریوم 🔷",        "ethereum"),
    "bnb":   ("بایننس کوین 🟡",   "binancecoin"),
    "sol":   ("سولانا 🟣",        "solana"),
    "xrp":   ("ریپل 🔵",          "ripple"),
    "doge":  ("دوج‌کوین 🐶",      "dogecoin"),
    "ada":   ("کاردانو 🔵",       "cardano"),
    "trx":   ("ترون 🔴",          "tron"),
    "ton":   ("تون کوین 💎",      "the-open-network"),
}

# کلمات کلیدی که کاربر میتونه تایپ کنه
KEYWORDS = {
    "دلار": "dollar", "dollar": "dollar", "usd": "dollar",
    "یورو": "euro", "euro": "euro", "eur": "euro",
    "پوند": "pound", "pound": "pound", "gbp": "pound",
    "درهم": "dirham", "dirهم": "dirham", "aed": "dirham",
    "لیر": "lira", "لیره": "lira", "try": "lira",
    "یوان": "yuan", "cny": "yuan",
    "ین": "yen", "jpy": "yen",
    "روبل": "ruble", "rub": "ruble",
    "ریال عربستان": "riyal_sa", "sar": "riyal_sa",
    "طلا": "gold", "gold": "gold",
    "سکه": "sekke", "سکه امامی": "sekke",
    "تتر": "usdt", "tether": "usdt", "usdt": "usdt",
    "بیتکوین": "btc", "بیت کوین": "btc", "bitcoin": "btc", "btc": "btc",
    "اتریوم": "eth", "ethereum": "eth", "eth": "eth",
    "بایننس": "bnb", "bnb": "bnb",
    "سولانا": "sol", "solana": "sol", "sol": "sol",
    "ریپل": "xrp", "xrp": "xrp",
    "دوج": "doge", "دوجکوین": "doge", "dogecoin": "doge", "doge": "doge",
    "کاردانو": "ada", "ada": "ada",
    "ترون": "trx", "trx": "trx",
    "تون": "ton", "ton": "ton",
}

def get_price(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        price_tag = soup.find("span", {"data-col": "info.last_trade.PDrCotVal"})
        if not price_tag:
            price_tag = soup.find("td", class_="nf")
        if price_tag:
            return price_tag.text.strip().replace(",", "،")
        return "در دسترس نیست"
    except Exception:
        return "خطا در دریافت"

def get_crypto_price(coin_id: str) -> str:
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,irt"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if coin_id in data:
            usd = data[coin_id].get("usd", 0)
            irt = data[coin_id].get("irt", 0)
            return f"${usd:,.2f} | {irt:,.0f} تومان"
        return "در دسترس نیست"
    except Exception:
        return "خطا در دریافت"

def make_main_keyboard():
    buttons = [
        [InlineKeyboardButton("💱 نرخ ارز", callback_data="menu_currency"),
         InlineKeyboardButton("🪙 ارز دیجیتال", callback_data="menu_crypto")],
        [InlineKeyboardButton("📊 همه ارزها", callback_data="all_currency"),
         InlineKeyboardButton("📈 همه کریپتو", callback_data="all_crypto")],
    ]
    return InlineKeyboardMarkup(buttons)

def make_currency_keyboard():
    buttons = []
    row = []
    for key, (name, _) in CURRENCIES.items():
        row.append(InlineKeyboardButton(name, callback_data=f"c_{key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 برگشت", callback_data="back")])
    return InlineKeyboardMarkup(buttons)

def make_crypto_keyboard():
    buttons = []
    row = []
    for key, (name, _) in CRYPTO.items():
        row.append(InlineKeyboardButton(name, callback_data=f"cr_{key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 برگشت", callback_data="back")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "سلام! 👋 به ربات نرخ ارز و کریپتو خوش اومدی 💰\n\n"
        "میتونی اسم ارز رو تایپ کنی، مثلاً:\n"
        "• دلار، یورو، طلا، سکه\n"
        "• تتر، بیتکوین، اتریوم\n\n"
        "یا از دکمه‌های زیر استفاده کن:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=make_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text.strip().lower()

    # چک کن کاربر اسم ارز تایپ کرده
    matched_key = None
    for keyword, key in KEYWORDS.items():
        if keyword in text:
            matched_key = key
            break

    if matched_key:
        # ارز رو پیدا کرد
        if matched_key in CURRENCIES:
            name, url = CURRENCIES[matched_key]
            await update.message.reply_text(f"⏳ در حال دریافت نرخ {name}...")
            price = get_price(url)
            await update.message.reply_text(
                f"💱 *{name}*\n\nقیمت: `{price}` ریال\n\n🔄 منبع: tgju.org",
                parse_mode="Markdown"
            )
        elif matched_key in CRYPTO:
            name, coin_id = CRYPTO[matched_key]
            await update.message.reply_text(f"⏳ در حال دریافت قیمت {name}...")
            price = get_crypto_price(coin_id)
            await update.message.reply_text(
                f"🪙 *{name}*\n\nقیمت: `{price}`\n\n🔄 منبع: CoinGecko",
                parse_mode="Markdown"
            )
    else:
        await update.message.reply_text(
            "از دکمه‌های زیر استفاده کن یا اسم ارز رو بنویس 👇\n"
            "مثال: دلار | تتر | بیتکوین | طلا",
            reply_markup=make_main_keyboard()
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data

    if key == "back":
        await query.edit_message_text("یکی از گزینه‌های زیر رو انتخاب کن:", reply_markup=make_main_keyboard())

    elif key == "menu_currency":
        await query.edit_message_text("💱 کدوم ارز؟", reply_markup=make_currency_keyboard())

    elif key == "menu_crypto":
        await query.edit_message_text("🪙 کدوم ارز دیجیتال؟", reply_markup=make_crypto_keyboard())

    elif key == "all_currency":
        await query.edit_message_text("⏳ در حال دریافت نرخ‌ها...")
        lines = ["💱 *نرخ ارز لحظه‌ای*\n"]
        for k, (name, url) in CURRENCIES.items():
            price = get_price(url)
            lines.append(f"{name}: `{price}` ریال")
        lines.append("\n🔄 منبع: tgju.org")
        await query.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=make_main_keyboard())

    elif key == "all_crypto":
        await query.edit_message_text("⏳ در حال دریافت قیمت‌های کریپتو...")
        lines = ["🪙 *قیمت ارزهای دیجیتال*\n"]
        ids = ",".join([coin_id for _, coin_id in CRYPTO.values()])
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,irt"
            resp = requests.get(url, timeout=15)
            data = resp.json()
            for k, (name, coin_id) in CRYPTO.items():
                if coin_id in data:
                    usd = data[coin_id].get("usd", 0)
                    irt = data[coin_id].get("irt", 0)
                    lines.append(f"{name}: `${usd:,.2f}` | `{irt:,.0f}` تومان")
                else:
                    lines.append(f"{name}: در دسترس نیست")
        except Exception:
            lines.append("خطا در دریافت اطلاعات")
        lines.append("\n🔄 منبع: CoinGecko")
        await query.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=make_main_keyboard())

    elif key.startswith("c_"):
        k = key[2:]
        if k in CURRENCIES:
            name, url = CURRENCIES[k]
            await query.edit_message_text(f"⏳ در حال دریافت نرخ {name}...")
            price = get_price(url)
            await query.edit_message_text(
                f"💱 *{name}*\n\nقیمت: `{price}` ریال\n\n🔄 منبع: tgju.org",
                parse_mode="Markdown", reply_markup=make_currency_keyboard()
            )

    elif key.startswith("cr_"):
        k = key[3:]
        if k in CRYPTO:
            name, coin_id = CRYPTO[k]
            await query.edit_message_text(f"⏳ در حال دریافت قیمت {name}...")
            price = get_crypto_price(coin_id)
            await query.edit_message_text(
                f"🪙 *{name}*\n\nقیمت: `{price}`\n\n🔄 منبع: CoinGecko",
                parse_mode="Markdown", reply_markup=make_crypto_keyboard()
            )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ ربات در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()
