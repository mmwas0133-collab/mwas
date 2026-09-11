import os
import threading
import time
from flask import Flask
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from yt_dlp import YoutubeDL

TOKEN = "8692270797:AAElmOYZiBcNB8YD7rnvjLH566ZV2moTEQm4"
bot = telebot.TeleBot(TOKEN)

app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! دز رابط يوتيوب أو اسم الأغنية وسأقوم بتحميلها لك.")

@bot.message_handler(func=lambda message: True)
def download_youtube(message):
    query = message.text.strip()
    chat_id = message.chat.id
    
    bot.send_chat_action(chat_id, "upload_video")
    processing_msg = bot.send_message(chat_id, "جاري تحويل الفيديو من الرابط...")

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "noplaylist": True,
        "max_filesize": 50 * 1024 * 1024,
        "extractor-args": {"youtube": {"player-client": ["mweb", "ios"]}},
    }

    try:
        os.makedirs("downloads", exist_ok=True)
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            file_path = ydl.prepare_filename(info)
            title = info.get("title", "فيديو")

        with open(file_path, "rb") as f:
            bot.send_video(chat_id, f, caption=f"تم التحميل: \n{title}")

        os.remove(file_path)
        bot.delete_message(chat_id, processing_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"حدث خطأ: {e}", chat_id, processing_msg.message_id)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
