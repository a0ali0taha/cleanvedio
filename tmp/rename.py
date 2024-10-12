# import os
# import re

# source_dir = "F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\final\\bokhary" # replace with your source directory path
# dest_dir = "F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\final\\bokhary\\test" # replace with your destination directory path

# if not os.path.exists(dest_dir):
#     os.makedirs(dest_dir)

# for file in os.listdir(source_dir):
#     if file.endswith('.mp4'):
#         match = re.search(r'Episode (\d+)', file)
#         if match:
#             episode_number = match.group(1)
#             new_name = f'Episode {episode_number}.mp4'
#             source_file_path = os.path.join(source_dir, file)
#             dest_file_path = os.path.join(dest_dir, new_name)
#             os.rename(source_file_path, dest_file_path)
import os

folder_path =  "f:\\with_music\\ayat" # replace with your source directory path


# List all files in the folder
files = os.listdir(folder_path)

# Loop through each file and rename it
for file in files:
    if os.path.isfile(os.path.join(folder_path, file)):
        episode_number = file.replace("(1080p_25fps_H264-128kbit_AAC)",'')  # Assuming the episode number is separated by a space
        new_name = f"{episode_number}"  # Prepend the episode number with leading zeros if necessary
        os.rename(os.path.join(folder_path, file), os.path.join(folder_path, new_name))
