import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 0. TẠO DỊCH VỤ WEB SERVER GIÚP RENDER DÙNG GÓI FREE 24/7 ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Telegram Gemini is running 24/7!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Web server dang chay tren port {port}")
    server.serve_forever()

# --- 1. CẤU HÌNH TOKEN VÀ API KEY ---
TELEGRAM_BOT_TOKEN = "8961970849:AAEupko-iMJZFyoeS5NsgbhkDUpyfMW2LVU"  # Thay Token Telegram của bạn
GEMINI_API_KEY = "AQ.Ab8RN6Kd6ui3C58prwktSsRGcQLykr210MXi_pcjJJfXad9i4w"  # Thay API Key mới (AIzaSy...) vào đây

client = genai.Client(api_key="AQ.Ab8RN6Kd6ui3C58prwktSsRGcQLykr210MXi_pcjJJfXad9i4w")

# --- 2. HÀM XỬ LÝ LỆNH /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Tôi là Bot AI Gemini. Bạn muốn hỏi tôi điều gì?")

# --- 3. HÀM XỬ LÝ TIN NHẮN (STREAMING) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.models.generate_content_stream(
            model='gemini-2.5-flash',
            contents=user_text,
        )
        
        sent_message = None
        full_text = ""
        last_update_len = 0

        for chunk in response:
            if chunk.text:
                full_text += chunk.text
                if len(full_text) - last_update_len > 30:
                    if not sent_message:
                        sent_message = await update.message.reply_text(full_text)
                    else:
                        await sent_message.edit_text(full_text)
                    last_update_len = len(full_text)

        if sent_message and full_text != sent_message.text:
            await sent_message.edit_text(full_text)
        elif not sent_message and full_text:
            await update.message.reply_text(full_text)

    except Exception as e:
        print(f"Lỗi Gemini: {e}")
        await update.message.reply_text(f"⚠️ Đã có lỗi xảy ra: {e}")

# --- 4. KHỞI CHẠY BOT ---
if __name__ == '__main__':
    # Khởi chạy Web server trên luồng phụ trước
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    # Khởi chạy Telegram Bot
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot AI Gemini đang chạy...")
    app.run_polling()
