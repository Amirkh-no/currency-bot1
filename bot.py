import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8143466135:AAHiS2kJc5qNi_5AlOIYOjMHU3T8ImLoRVQ"

logging.basicConfig(level=logging.INFO)

CURRENCIES = {
    "dollar":    ("دلار آمریکا 🇺🇸",     "https://www.tgju.org/profile/price_dollar_rl"),
    "euro":      ("یورو 🇪🇺",             "https://www.tgju.org/profile/price_eur"),
    "pound":     ("پوند انگلیس 🇬🇧",      "https://www.tgju.org/profile/price_gbp"),
    "dirham":    ("درهم امارات 🇦🇪",      "https://www.tgju.org/profile/price_aed"),
    "lira":      ("لیر ترکیه 🇹🇷",        "https://www.tgju.org/profile/price_try"),
    "yuan":      ("یوان چین 🇨🇳",         "https://www.tgju.org/profile/price_cny"),
    "yen":       ("ین ژاپن 🇯🇵",          "https://www.tgju.org/profile/price_jpy"),
    "won":       ("وون کره جنوبی 🇰🇷",    "https://www.tgju.org/profile/price_krw"),
    "ruble":     ("روبل روسیه 🇷🇺",       "https://www.tgju.org/profile/price_rub"),
    "riyal_sa":  ("ریال عربستان 🇸🇦",     "https://www.tgju.org/profile/price_sar"),
    "gold":      ("طلا 18 عیار 🥇",       "https://www.tgju.org/profile/geram18"),
    "sekke":     ("سکه امامی 🪙",         "https://www.tgju.org/profile/sekke"),
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

def make_keyboard():
    buttons = []
    row = []
    for key, (name, _) in CURRENCIES.items():
        row.append(InlineKeyboardButton(name, callback_data=key))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("📊 همه نرخ‌ها", callback_data="all")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "سلام! 👋 به ربات نرخ ارز خوش اومدی 💰\n\n"
        "یکی از گزینه‌های زیر رو انتخاب کن:"
    )
    await update.message.reply_text(text, reply_markup=make_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data

    if key == "all":
        await query.edit_message_text("⏳ در حال دریافت نرخ‌ها...")
        lines = ["📊 *نرخ ارز لحظه‌ای*\n"]
        for k, (name, url) in CURRENCIES.items():
            price = get_price(url)
            lines.append(f"{name}: `{price}` ریال")
        lines.append("\n🔄 منبع: tgju.org")
        await query.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=make_keyboard()
        )
    elif key in CURRENCIES:
        name, url = CURRENCIES[key]
        await query.edit_message_text(f"⏳ در حال دریافت نرخ {name}...")
        price = get_price(url)
        text = f"💱 *{name}*\n\nقیمت: `{price}` ریال\n\n🔄 منبع: tgju.org"
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=make_keyboard()
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "از دکمه‌های زیر استفاده کن 👇",
        reply_markup=make_keyboard()
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ ربات نرخ ارز در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()


