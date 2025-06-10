import asyncio
import socket
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

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

# Portlarni tekshiruvchi funksiya (1-1024)
async def scan_ports(ip):
    ports = range(1, 256)
    tasks = [check_port(ip, port) for port in ports]
    results = await asyncio.gather(*tasks)
    open_ports = [port for port, is_open in results if is_open]
    return open_ports

# /start komandasi uchun xabar
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men TCP port skaner botiman.\n"
        "Iltimos, tekshirmoqchi bo‘lgan IP manzil yoki domen nomini yuboring.\n\n"
        "Masalan: 8.8.8.8 yoki example.com\n\n"
        "Eslatma: Port skanerlash faqat ruxsat olingan tarmoqlarda amalga oshirilishi kerak!"
    )

# Foydalanuvchi yuborgan manzilni qabul qilib, portlarni tekshiradi
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.text.strip()

    # IP yoki domenni IP ga o'zgartirish
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        await update.message.reply_text("Noto‘g‘ri IP manzil yoki domen nomi. Iltimos, yana urinib ko‘ring.")
        return

    await update.message.reply_text(f"{target} ({ip}) uchun portlarni tekshirish boshlandi. Iltimos kuting...")

    open_ports = await scan_ports(ip)

    if open_ports:
        ports_str = ', '.join(str(p) for p in open_ports)
        await update.message.reply_text(f"Ochiq portlar: {ports_str}")
    else:
        await update.message.reply_text("1-255 diapazonidagi hech qanday port ochiq emas.")

# Asosiy funksiya, botni ishga tushiradi
def main():
    TOKEN = "8115968693:AAHj-zIyaHnpmeLlK8vYWtDWaoMjqO3Lg-Y"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
