import os
import threading
import time
from flask import Flask
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from yt_dlp import YoutubeDL

TOKEN = "8692270797:AAElm0YZIbcN8YD7rnvjLH566ZV2moTEQm4"
bot = telebot.TeleBot(TOKEN)

# إنشاء سيرفر ويب وهمي لتبقى الاستضافة المجانية نشطة
app = Flask("")


@app.route("/")
def home():
  return "Bot is running!"


def run_web():
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


@bot.message_handler(commands=["start"])
def send_welcome(message):
  bot.reply_to(
      message,
      "أهلاً بك يا موسى! 🎵\nأرسل رابط فيديو يوتيوب للتحميل المباشر، أو اكتب"
      " اسم الأغنية وسأعطيك قائمة لاختيارها.",
  )


@bot.message_handler(func=lambda message: True)
def handle_media(message):
  query = message.text.strip()
  chat_id = message.chat.id

  # إذا كان الرابط مباشر من يوتيوب
  if "http://channels" in query or "youtube.com" in query or "youtu.be" in query:
    bot.send_chat_action(chat_id, "upload_video")
    processing_msg = bot.send_message(chat_id, "جارٍ تحميل الفيديو من الرابط...")

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "noplaylist": True,
        "max_filesize": 50 * 1024 * 1024,
    }

    try:
      os.makedirs("downloads", exist_ok=True)
      with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        file_path = ydl.prepare_filename(info)
        title = info.get("title", "فيديو")

      with open(file_path, "rb") as f:
        bot.send_video(chat_id, f, caption=f"تم التحميل:\n{title}")

      os.remove(file_path)
      bot.delete_message(chat_id, processing_msg.message_id)
    except Exception as e:
      bot.edit_message_text(f"حدث خطأ: {e}", chat_id, processing_msg.message_id)

  else:
    # إذا كان بحثاً بالاسم، نعرض قائمة نتائج بحث (أزرار شفافة)
    processing_msg = bot.send_message(chat_id, "🔍 جارٍ البحث عن النتائج...")

    search_opts = {
        "default_search": "ytsearch5",  # جلب أفضل 5 نتائج مطابقة للبحث
        "noplaylist": True,
    }

    try:
      with YoutubeDL(search_opts) as ydl:
        info = ydl.extract_info(query, download=False)

      if "entries" not in info or not info["entries"]:
        bot.edit_message_text(
            "عذراً، لم أجد نتائج مطابقة لبحثك.", chat_id, processing_msg.message_id
        )
        return

      # إنشاء قائمة أزرار للنتائج
      markup = InlineKeyboardMarkup()
      for idx, entry in enumerate(info["entries"]):
        title = entry.get("title", "بدون عنوان")
        url = entry.get("url", "")
        # اختصار العنوان إذا كان طويلاً جداً
        if len(title) > 40:
          title = title[:40] + "..."

        # تخزين الرابط في الـ callback_data
        markup.add(
            InlineKeyboardButton(
                f"{idx+1}. {title}", callback_data=f"dl|{url}"
            )
        )

      bot.edit_message_text(
          "ختر الأغنية أو الفيديو المطلوب من القائمة أدناه:",
          chat_id,
          processing_msg.message_id,
          reply_markup=markup,
      )

    except Exception as e:
      bot.edit_message_text(
          f"حدث خطأ أثناء البحث: {e}", chat_id, processing_msg.message_id
      )


# التعامل مع الضغط على الأزرار لتحميل الاختيار
@bot.callback_query_handler(func=lambda call: call.data.startswith("dl|"))
def callback_download(call):
  chat_id = call.message.chat.id
  url = call.data.split("|")[1]

  bot.answer_callback_query(call.id, "جاري بدء التحميل...")
  bot.edit_message_text("📥 جارٍ سحب الفيديو وتحميله...", chat_id, call.message.message_id)

  ydl_opts = {
      "format": "best[ext=mp4]/best",
      "outtmpl": "downloads/%(id)s.%(ext)s",
      "noplaylist": True,
      "max_filesize": 50 * 1024 * 1024,
  }

  try:
    os.makedirs("downloads", exist_ok=True)
    with YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      file_path = ydl.prepare_filename(info)
      title = info.get("title", "فيديو")

    with open(file_path, "rb") as f:
      bot.send_video(chat_id, f, caption=f"تم التحميل:\n{title}")

    os.remove(file_path)
    bot.delete_message(chat_id, call.message.message_id)
  except Exception as e:
    bot.send_message(chat_id, f"حدث خطأ أثناء تحميل الملف: {e}")


if __name__ == "__main__":
  t = threading.Thread(target=run_web)
  t.start()

  while True:
    try:
      bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
      print(f"خطأ: {e}")
      time.sleep(5)

