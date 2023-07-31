import asyncio
import os
from telegram_sender import send_to_telegram
from youtube_downloader import download_video, download_playlist
from detach import detach_audio
from audio_split import split
from spleeter import separate_vocals_with_spleeter
from audio_merge import combine_audio_segments
from attach import attach_audio
import os
def start(dir):
    i=1
    folder_list = os.listdir(dir)
    for file in folder_list:
    # Perform operations on each MP3 file
        filename = os.path.basename(file)
        name, ext = os.path.splitext(filename)
        output_path=f"output1\\{i}"
        handle(name,output_path,f'{dir}\\{file}',False)
        i=i+1
    

        
def handle(video_title,output_path,video_path,is_send_to_telegram=False):
    detached_audio_path= video_path.replace('mp4','mp3')
    detach_audio(video_path,detached_audio_path)
    segments_files=split(detached_audio_path)
    vocals_folder=f'{output_path}\\vocals'
    vocal_files = []
    for mp3_file in segments_files: 
        vocal_folder_seg=f'{vocals_folder}\\{mp3_file}'
        separate_vocals_with_spleeter(mp3_file,vocal_folder_seg)
        vocal_files.append(f'{vocal_folder_seg}\\{video_title}\\vocals.mp3')

    combined_audio = combine_audio_segments(vocal_files)
    combined_audio_file = f"{output_path}\\combined_audio.mp3"
    combined_audio.export(combined_audio_file, format="mp3")
    final_video_path=f"final\\{video_title}.mp4"
    attach_audio(video_path, combined_audio_file, final_video_path)
    if is_send_to_telegram:
        asyncio.run(send_to_telegram(video_title, final_video_path))


start('newv')