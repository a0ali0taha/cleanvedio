import asyncio
import os
from telegram_sender import send_video_to_telegram_in_asyncio
from services.youtube_downloader import download_video, download_playlist
from services.detach import detach_audio
from services.audio_split import split_video
from services.spleeter import create_vocals
from services.audio_merge import combine_audio_segments
from services.attach import attach_audio
from services.mylogger import logger
from video import Video
import threading
from services.get_first_image import get_thumbnail
# add logger to the code?
def start(url,is_playlist = True, output_path='videos',is_send_to_telegram=False):
    i=1
    if is_playlist:
        video_paths=download_playlist(url, output_path)
        for title, file_path in video_paths.items():
              
                # Do something with the title and file_path
                print(f"Video Title: {title}, File Path: {file_path}")
                processing_input_folder=f"{output_path}\\{i}"
                video= Video(processing_input_folder=processing_input_folder,input_video_path=file_path,send_to_telegram=is_send_to_telegram)
                handle(video)#vtitile,newv\1,newv\vtitle.mp4
                i=i+1
        
    else:
        video_title, video_path = download_video(url, output_path)
        processing_input_folder=f"{output_path}\\{i}"
        video= Video(processing_input_folder=processing_input_folder,input_video_path=video_path,send_to_telegram=is_send_to_telegram)
        handle(video)
        

def iniat_dirs(video):
    os.makedirs(video.processing_input_folder)
    
    detached_audio_path= f'{video.processing_input_folder}\\det.mp3'#newv\1\vtitle.mp3
    video.detached_mp3= detached_audio_path
    
    video_file_name=os.path.basename(video.input_video_path)
    output_video_path=f"final\\{video_file_name}"
    video.output_video_path=output_video_path
    
def handle(video):
    #video_name=vtitile,   output_path=newv\1,    video_path=newv\vtitle.mp4,'F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\newv\\Watch The Secret Life Of Pets For English Learners 1.mp4'

    iniat_dirs(video)
    detach_audio(video)
    split_video(video)#newv\1\seg_1.mp3
    create_vocals(video)
    combine_audio_segments(video)
    attach_audio(video)
    if video.send_to_telegram:
        get_thumbnail(video)
        logger.info(f"start  sending to telegram: {video.caption}")
        threading.Thread(target=send_video_to_telegram_in_asyncio, args=([video])).start()


# handle('الحرب العالمية الأولى باختصار','newv\\1','newv\\الحرب العالمية الأولى باختصار.mp4',True)