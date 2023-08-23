import asyncio
from pyrogram import Client
import os
import threading
from video import Video
bot_token = '6554914797:AAE1_FqgZh16eNsFZcJ_BgL51-ccwIHEJJQ'
chat_id = -1001938941284
chat_id = 'clean_video'

# 29646632
# eae5d7f69ecf16e96c6bd9f14aaa4f97
def send_video_progress(current, total):
    percent = (current / total) * 100
    print(f"Uploading: {percent:.2f}%")

async def send_video_to_telegram(video):
   
    async with Client("my_account", api_id=29646632, api_hash='eae5d7f69ecf16e96c6bd9f14aaa4f97',bot_token=bot_token) as app:
        # thumbnail_path = video_file_path + '.thumbnail.jpg'
        # with VideoFileClip(video_file_path) as video:
        #     thumbnail = video.get_frame(0)  # Get the first frame as the thumbnail
        #     thumbnail.save_frame(thumbnail_path)
        await app.send_video(chat_id=chat_id,video=video.output_video_path,caption=video.caption,progress=send_video_progress,thumb=video.video_thumbnail_path,duration=video.video_duration)
        # await app.send_video(chat_id=chat_id,video=video_file_path,caption=caption,progress=send_video_progress)
        # await app.send_message(chat_id=chat_id,text='test')
def send_video_to_telegram_in_asyncio(video):
    
    asyncio.run(send_video_to_telegram(video))
# video= Video(processing_input_folder='',input_video_path='file_path',send_to_telegram=True)

# threading.Thread(target=send_video_to_telegram_in_asyncio, args=([video])).start()
# threading.Thread(target=send_video_to_telegram_in_asyncio, args=(video)).start()
# asyncio.run(send_video_to_telegram('F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\final\\filename.mp4','test'))
# asyncio.run(send_video_to_telegram('F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\final\\01.mp4','test'))