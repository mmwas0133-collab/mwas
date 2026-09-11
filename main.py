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

  # إعدادات yt-dlp المحدثة لعملاء iOS و TV لتخطي الحظر
  ydl_opts = {
      "format": "bestvideo+bestaudio/best",
      "outtmpl": "downloaded_video.mp4",
      "noplaylist": True,
      "http_headers": {
          "User-Agent": (
              "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
              "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
          ),
      },
      # تحويل العميل إلى ios و tv لتخطي حظر الـ 403 نهائياً
      "extractor_args": {"youtube": {"player_client": ["ios", "tv"]}},
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      filename = ydl.prepare_filename(info)

    # إرسال الفيديو للمستخدم على التليجرام
    with open(filename, "rb") as video_file:
      bot.send_video(message.chat.id, video_file)

    # حذف الملف من السيرفر بعد الإرسال
    if os.path.exists(filename):
      os.remove(filename)

  except Exception as e:
    bot.reply_to(
        message, f"حدث خطأ أثناء تحميل الفيديو: تأكد من أن الرابط متاح وعام. ({e})"
    )


if __name__ == "__main__":
  print("Bot is running...")
  bot.infinity_polling()
