from main import handle
import os
def start(dir,send_to_telegram):
    i=1
    folder_list = os.listdir(dir)
    for file in folder_list:
    # Perform operations on each MP3 file
        filename = os.path.basename(file)
        name, ext = os.path.splitext(filename)
        output_path=f"{dir}\\{i}"
        video_path=f'{dir}\\{file}'
        handle(output_path,video_path,send_to_telegram)
        i=i+1

# start('newv',True)