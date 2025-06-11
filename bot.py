import asyncio
import socket
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# Bosqichlar
CHOOSING_RANGE = 1

# Asinxron port tekshiruvi funksiyasi
async def check_port(ip, port, timeout=1):
    try:
        conn = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return port, True
    except:
        return port, False

# Portlarni tekshiruvchi funksiya (dynamic diapazon)
async def scan_ports(ip, max_port):
    ports = range(1, max_port + 1)
    tasks = [check_port(ip, port) for port in ports]
    results = await asyncio.gather(*tasks)
    open_ports = [port for port, is_open in results if is_open]
    return open_ports

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['1–256', '1–512', '1–1024']]
    await update.message.reply_text(
        "Salom! Men TCP port skaner botiman.\n"
        "Iltimos, port diapazonini tanlang:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSING_RANGE

# Diapazon tanlangach, IP so‘rash
async def choose_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '1–256':
        context.user_data['max_port'] = 256
    elif text == '1–512':
        context.user_data['max_port'] = 512
    else:
        context.user_data['max_port'] = 1024

    await update.message.reply_text(
        "Endi IP manzil yoki domen nomini yuboring.\n\nMasalan: 8.8.8.8 yoki example.com",
        reply_markup=ReplyKeyboardRemove()
    )
    return MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)

# IP qabul qilish va tekshirish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.text.strip()

    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        await update.message.reply_text("❌ Noto‘g‘ri IP manzil yoki domen nomi. Iltimos, yana urinib ko‘ring.")
        return ConversationHandler.END

    max_port = context.user_data.get('max_port', 1024)
    await update.message.reply_text(f"🔍 {target} ({ip}) uchun 1–{max_port} portlar tekshirilmoqda. Iltimos kuting...")

    open_ports = await scan_ports(ip, max_port)

    if open_ports:
        ports_str = ', '.join(str(p) for p in open_ports)
        await update.message.reply_text(f"✅ Ochiq portlar: {ports_str}")
    else:
        await update.message.reply_text("❗ Belgilangan diapazondagi hech qanday port ochiq emas.")

    return ConversationHandler.END

# Bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Jarayon bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Asosiy funksiya
def main():
    TOKEN = "8115968693:AAHj-zIyaHnpmeLlK8vYWtDWaoMjqO3Lg-Y"
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_RANGE: [
                MessageHandler(filters.Regex("^(1–256|1–512|1–1024)$"), choose_range)
            ],
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message): [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
