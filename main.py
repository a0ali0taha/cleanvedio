import asyncio
import os
from telegram_sender import send_video_to_telegram
from youtube_downloader import download_video, download_playlist
from detach import detach_audio
from audio_split import split
from spleeter import separate_vocals_with_spleeter
from audio_merge import combine_audio_segments
from attach import attach_audio
import re
def start(url,is_playlist = True, output_path='videos',is_send_to_telegram=False):
    i=1
    if is_playlist:
        video_paths=download_playlist(url, output_path)
        for title, file_path in video_paths.items():
                output_path=f"{output_path}\\{i}"
                # Do something with the title and file_path
                print(f"Video Title: {title}, File Path: {file_path}")
                handle(output_path,file_path,is_send_to_telegram)#vtitile,newv\1,newv\vtitle.mp4
                i=i+1
        
    else:
        video_title, video_path = download_video(url, output_path)
        output_path=f"{output_path}\\{i}"
        handle(output_path,video_path,is_send_to_telegram)
        

        
def handle(output_path,video_path,is_send_to_telegram=False):
    #video_name=vtitile,   output_path=newv\1,    video_path=newv\vtitle.mp4,'F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\newv\\Watch The Secret Life Of Pets For English Learners 1.mp4'

    os.makedirs(output_path)
    detached_audio_path= f'{output_path}\\det.mp3'#newv\1\vtitle.mp3
    detach_audio(video_path,detached_audio_path)
    segments_files=split(detached_audio_path,output_path)#newv\1\seg_1.mp3
    vocals_folder=f'{output_path}\\vocals' #newv\1\vocals
    vocal_files = []
    for i,mp3_file in enumerate(segments_files): 
        vocal_folder_seg=f'{vocals_folder}'#newv\1\vocals
        separate_vocals_with_spleeter(mp3_file,vocal_folder_seg)
        vocal_files.append(f'{vocal_folder_seg}\\seg_{i+1}\\vocals.mp3')#newv\1\vocals\seg_1\vocals.mp3, newv\1\vocals\seg_1\vocals.mp3

    combined_audio = combine_audio_segments(vocal_files)
    combined_audio_file = f"{output_path}\\combined_audio.mp3"#'newv\\1\\combined_audio.mp3'
    combined_audio.export(combined_audio_file, format="mp3")
    video_file_name=os.path.basename(video_path)
    final_video_path=f"final\\{video_file_name}"
    attach_audio(video_path, combined_audio_file, final_video_path)
    if is_send_to_telegram:
        asyncio.run(send_video_to_telegram(final_video_path ,video_file_name.replace('.mp4','')))


# handle('الحرب العالمية الأولى باختصار','newv\\1','newv\\الحرب العالمية الأولى باختصار.mp4',True)