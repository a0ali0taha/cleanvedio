from main import handle
import os
from video import Video
def start_dir(dir,send_to_telegram):
    i=1
    folder_list = os.listdir(dir)
    for file in folder_list:
    # Perform operations on each MP3 file
        filename = os.path.basename(file)
        name, ext = os.path.splitext(filename)
        processing_input_folder=f"{dir}\\{i}"
        video_path=f'{dir}\\{file}'
        video= Video(processing_input_folder=processing_input_folder,input_video_path=video_path,send_to_telegram=send_to_telegram)
        handle(video)
        i=i+1
def start_file(video_path,send_to_telegram):
    processing_input_folder=video_path.replace('mp4','')
    video= Video(processing_input_folder=processing_input_folder,input_video_path=video_path,send_to_telegram=send_to_telegram)
    handle(video)

# start_dir("F:\\with_music\\younos" ,True)
# F:\with_music\younos

start_file("F:\\luckluck.mp4",True)
os.system("shutdown /s /t {}".format(600))