import asyncio
from pyrogram import Client
import os
import threading
from video import Video
from moviepy.editor import *
import uuid
bot_token = '6554914797:AAE1_FqgZh16eNsFZcJ_BgL51-ccwIHEJJQ'
chat_id = -1001938941284
chat_id = 'clean_video'
session=1
# my chat_id   
chat_id='Ahmed0taha0'
# 29646632
# eae5d7f69ecf16e96c6bd9f14aaa4f97
def send_video_progress(current, total):
    percent = (current / total) * 100
    print(f"Uploading: {percent:.2f}%")
import subprocess

def get_thumbnail(video_input_path):
    thumbnail_path = video_input_path + '.thumbnail.jpg'
    subprocess.call(['ffmpeg', '-i', video_input_path, '-ss', '00:00:20.000', '-vframes', '1', thumbnail_path])#override file if exist?
    return thumbnail_path

async def send_video_to_telegram(file_path,caption,thumb,duration):
    # session = 2 if session == 1 else 1  
    
    async with Client(f"session", api_id=29646632, api_hash='eae5d7f69ecf16e96c6bd9f14aaa4f97',bot_token=bot_token) as app:
        # thumbnail_path = video_file_path + '.thumbnail.jpg'
        # with VideoFileClip(video_file_path) as video:
        #     thumbnail = video.get_frame(0)  # Get the first frame as the thumbnail
        #     thumbnail.save_frame(thumbnail_path)
        duration=int(round(duration))
        await app.send_video(chat_id=chat_id,video=file_path,caption=caption,progress=send_video_progress,thumb=thumb,duration=duration)
        # await app.send_video(chat_id=chat_id,video=video_file_path,caption=caption,progress=send_video_progress)
        # await app.send_message(chat_id=chat_id,text='test')
def send_video_to_telegram_in_asyncio(video):

    
    asyncio.run(send_video_to_telegram(video))
    
# video= Video(processing_input_folder='',input_video_path='file_path',send_to_telegram=True)

# threading.Thread(target=send_video_to_telegram_in_asyncio, args=([video])).start()
# threading.Thread(target=send_video_to_telegram_in_asyncio, args=(video)).start()
# asyncio.run(send_video_to_telegram('F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\final\\filename.mp4','test'))
from main import handle
import os
from video import Video
import time
def send_video_to_telegram_threaded(file_path, caption, thumb, duration):
    asyncio.run(send_video_to_telegram(file_path, caption, thumb, duration))

def start_dir(dir):
    i=1
    # list all mp4 files in the directory and sorted by name?

    mp4_files = [f for f in os.listdir(dir) if f.endswith('.mp4')]
    mp4_files.sort()

    for file in mp4_files:
        if file.endswith(".mp4"):
            file_path=dir+"\\"+file
            filename = os.path.basename(file)
            name, ext = os.path.splitext(filename) 
            clip = VideoFileClip(file_path)
            thumbnail_path=get_thumbnail(file_path)

            # put below line in thread?
            # threading.Thread(target=send_video_to_telegram_threaded, args=(file_path,name,thumbnail_path,clip.duration), daemon=True).start()
            send_video_to_telegram_threaded(file_path,name,thumbnail_path,clip.duration)
            # sleep for 10 seconds?
            time.sleep(3*60)
            i=i+1


start_dir("F:\\Ahmed\\lab\\scripts\\NoMusic\\download from yt\\final\\nemo" )

os.system("shutdown /s /t {}".format(600))

