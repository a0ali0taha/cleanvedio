# telegram_sender.py

from telegram import Bot
from telegram.error import TelegramError
from telegram.helpers import escape_markdown

async def send_to_telegram(video_title, video_file_path):

    bot = Bot(token=bot_token)

    try:
        await bot.send_video(chat_id=chat_id, video=open(video_file_path, 'rb'), caption=escape_markdown(video_title))
    except TelegramError as e:
        print(f"Error sending video to Telegram: {e}")