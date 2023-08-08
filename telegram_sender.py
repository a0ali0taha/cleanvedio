import asyncio
from pyrogram import Client
import os
bot_token = '6554914797:AAE1_FqgZh16eNsFZcJ_BgL51-ccwIHEJJQ'
chat_id = -1001938941284

# 29646632
# eae5d7f69ecf16e96c6bd9f14aaa4f97
def send_video_progress(current, total):
    percent = (current / total) * 100
    print(f"Uploading: {percent:.2f}%")

async def send_video_to_telegram(video_file_path,caption):
    caption= caption or os.path.basename(video_file_path)
    async with Client("my_account", api_id=29646632, api_hash='eae5d7f69ecf16e96c6bd9f14aaa4f97',bot_token=bot_token) as app:
        await app.send_video(chat_id=chat_id,video=video_file_path,caption=caption,progress=send_video_progress)
        # await app.send_message(chat_id=chat_id,text='test')


# asyncio.run(send_video_to_telegram('F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\final\\01.mp4','test'))