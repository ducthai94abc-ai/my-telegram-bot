import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 0. TẠO DUMMY WEB SERVER CHO RENDER PASSED PORT CHECK ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Telegram Gemini is running 24/7!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Web server fake dang chay tren port {port}")
    server.serve_forever()

# --- 1. CẤU HÌNH TOKEN VÀ API KEY ---
TELEGRAM_BOT_TOKEN = "8961970849:AAEupko-iMJZFyoeS5NsgbhkDUpyfMW2LVU"  # Thay Token Telegram của bạn vào đây
GEMINI_API_KEY = "AQ.Ab8RN6KDh3Ey6yX1YXGplCcdmSzFpIZkv87UAc94sKRGXMnsKg"  # Key Gemini của bạn

client = genai.Client(api_key="AQ.Ab8RN6KDh3Ey6yX1YXGplCcdmSzFpIZkv87UAc94sKRGXMnsKg")

# --- 2. HÀM XỬ LÝ LỆNH /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Tôi là Bot AI Gemini. Bạn muốn hỏi tôi điều gì?")

# --- 3. HÀM XỬ LÝ TIN NHẮN VỚI GEMINI (STREAMING) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Gọi Gemini AI trả lời
        response = client.models.generate_content_stream(
            model='gemini-3.6-flash',
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
    # Chạy Web Server ở luồng phụ (Thread)
    threading.Thread(target=run_dummy_server, daemon=True).start()

    # Chạy Telegram Bot Polling ở luồng chính
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot AI Gemini đang chạy...")
    app.run_polling()
