import asyncio
import os
from telegram_sender import send_to_telegram
from youtube_downloader import download_video, download_playlist
from detach import detach_audio
from audio_split import split
from spleeter import separate_vocals_with_spleeter
from audio_merge import combine_audio_segments
from attach import attach_audio
def start(url,is_playlist = True, output_path='videos',is_send_to_telegram=False):
    if is_playlist:
        video_paths=download_playlist(url, output_path)
        for title, file_path in video_paths.items():
                # Do something with the title and file_path
                print(f"Video Title: {title}, File Path: {file_path}")
                handle(title,file_path,is_send_to_telegram)
        
    else:
        video_title, video_path = download_video(url, output_path)
        handle(video_title,video_path,is_send_to_telegram)
        

        
def handle(video_name,video_path,is_send_to_telegram=False):
    detached_audio_path= video_path.replace('mp4','mp3')
    detach_audio(video_path,detached_audio_path)
    segments_files=split(detached_audio_path)
    vocal_folder='output_folder'
    for mp3_file in segments_files: 
        separate_vocals_with_spleeter(mp3_file,vocal_folder)
        # directory_path = '{output_folder}\\{vedoioname}_{1}\vocals.mp3'

    directory_path = 'output_folder'

    # List all files in the directory
    folder_list = os.listdir(directory_path)
    segment_files=[]
    for vocal_folder in folder_list:
    # Perform operations on each MP3 file
        segment_files.append(directory_path+'\\'+vocal_folder+'\\vocals.mp3')
    combined_audio = combine_audio_segments(segment_files)
    output_file = "output_folder\\combined_audio.mp3"
    combined_audio.export(output_file, format="mp3")
    final_video_path="final\\{output_path}\\{video_name}"
    attach_audio(video_path, output_file, final_video_path)
    if is_send_to_telegram:
        asyncio.run(send_to_telegram(video_name, final_video_path))