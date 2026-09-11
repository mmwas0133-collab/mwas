import os
import telebot
import yt_dlp

# توكن البوت الخاص بك
TOKEN = "8692270797:AAElm0YZIbcN8YD7rnvjLH566ZV2moTEQm4"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message,
      "أهلاً بك! أرسل لي رابط فيديو من اليوتيوب وسأقوم بتحميله لك فوراً.",
  )


@bot.message_handler(func=lambda message: True)
def download_youtube_video(message):
  url = message.text.strip()
  if "youtube.com" not in url and "youtu.be" not in url:
    bot.reply_to(message, "يرجى إرسال رابط يوتيوب صحيح.")
    return

  bot.reply_to(message, "جاري معالجة الفيديو وتحميله، دقيقة واحدة...")

  # إعدادات yt-dlp المتطورة لتخطي الحظر بدون كوكيز
  ydl_opts = {
      # اختيار أفضل جودة متوفرة وتدمج الصوت مع الصورة
      "format": "bestvideo+bestaudio/best",
      "outtmpl": "downloaded_video.mp4",
      "noplaylist": True,
      # ترويسات متصفح حقيقي لتخطي فلاتر الحماية
      "http_headers": {
          "User-Agent": (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
          ),
          "Accept": (
              "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
          ),
          "Accept-Language": "en-US,en;q=0.9",
      },
      # تمرير وسائط عملاء أندرويد وويب لخداع سيرفرات يوتيوب
      "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      filename = ydl.prepare_filename(info)

    # إرسال الفيديو للمستخدم على التليجرام
    with open(filename, "rb") as video_file:
      bot.send_video(message.chat.id, video_file)

    # حذف الملف من السيرفر بعد الإرسال لتوفير المساحة
    if os.path.exists(filename):
      os.remove(filename)

  except Exception as e:
    bot.reply_to(
        message, f"حدث خطأ أثناء تحميل الفيديو: تأكد من أن الرابط متاح وعام. ({e})"
    )


if __name__ == "__main__":
  print("Bot is running...")
  bot.infinity_polling()
