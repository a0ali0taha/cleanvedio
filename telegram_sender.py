import asyncio
from pyrogram import Client
import os
import threading
bot_token = '6554914797:AAE1_FqgZh16eNsFZcJ_BgL51-ccwIHEJJQ'
chat_id = -1001938941284
from moviepy.editor import VideoFileClip
# 29646632
# eae5d7f69ecf16e96c6bd9f14aaa4f97
def send_video_progress(current, total):
    percent = (current / total) * 100
    print(f"Uploading: {percent:.2f}%")
def get_video_duration(file_path):
    try:
        clip = VideoFileClip(file_path)
        return clip.duration
    except Exception as e:
        print("Error:", e)
        return None
async def send_video_to_telegram(video_file_path,caption):
    caption= caption or os.path.basename(video_file_path)
    async with Client("my_account", api_id=29646632, api_hash='eae5d7f69ecf16e96c6bd9f14aaa4f97',bot_token=bot_token) as app:
        thumbnail_path = video_file_path + '.thumbnail.jpg'
        with VideoFileClip(video_file_path) as video:
            thumbnail = video.get_frame(0)  # Get the first frame as the thumbnail
            thumbnail.save_frame(thumbnail_path)
        await app.send_video(chat_id=chat_id,video=video_file_path,caption=caption,progress=send_video_progress,thumb=thumbnail_path,duration=get_video_duration)
        # await app.send_message(chat_id=chat_id,text='test')
def send_video_to_telegram_in_asyncio(video_file_path,caption):
    asyncio.run(send_video_to_telegram(video_file_path,caption))
threading.Thread(target=send_video_to_telegram_in_asyncio, args=('F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\final\\01.mp4','test')).start()
# asyncio.run(send_video_to_telegram('F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\final\\filename.mp4','test'))