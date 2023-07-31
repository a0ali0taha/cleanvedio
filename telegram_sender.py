# telegram_sender.py

from telegram import Bot
from telegram.error import TelegramError
from telegram.helpers import escape_markdown
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
async def send_to_telegram(video_title, video_file_path):

    
    bot = Bot(token=bot_token)
    # app = ApplicationBuilder().token(bot_token).write_timeout(
    #     None).get_updates_write_timeout(None).build()

    # app.run_polling(write_timeout=None)

    try:
        await bot.send_video(chat_id=chat_id, video=open(video_file_path, 'rb'), caption=escape_markdown(video_title),supports_streaming=True)
    except TelegramError as e:
        print(f"Error sending video to Telegram: {e}")

# asyncio.run(send_to_telegram('test', 'newv/الحرب العالمية الأولى باختصار.mp4'))
