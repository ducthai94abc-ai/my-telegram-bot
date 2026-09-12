from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Hàm xử lý khi người dùng gửi lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chào bạn! Tôi là bot Telegram do bạn vừa tạo.")

# Hàm phản hồi lại đúng tin nhắn người dùng gửi (Echo)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Bạn vừa nói: {update.message.text}")

if __name__ == '__main__':
    # Khởi tạo ứng dụng với Token
    app = ApplicationBuilder().token("8961970849:AAEupko-iMJZFyoeS5NsgbhkDUpyfMW2LVU").build()

    # Thêm bộ xử lý lệnh /start
    app.add_handler(CommandHandler("start", start))
    
    # Thêm bộ xử lý tin nhắn văn bản thông thường
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot đang chạy...")
    app.run_polling()