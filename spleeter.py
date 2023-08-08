import subprocess
import os
def separate_vocals_with_spleeter(input_audio_path, output_folder):
    spleeter_command = [
        "spleeter",
        "separate",
        "-i",
        input_audio_path,
        "-p",
        "spleeter:2stems",
        "-o",
        output_folder,
        "-c",
        'mp3'
    ]

    try:
        subprocess.run(spleeter_command, check=True)
        print("Vocals separated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error while calling Spleeter: {e}")


# Replace 'path_to_directory' with the actual path to the directory you want to explore
# Replace 'path_to_directory' with the actual path to the directory you want to explore
# directory_path = 'input_segments'

# # List all files in the directory
# file_list = os.listdir(directory_path)

# # Filter only the MP3 files
# mp3_files = [file for file in file_list if file.endswith('.mp3')]

# # Now you can work with the selected MP3 files
# for mp3_file in mp3_files:
#     # Perform operations on each MP3 file
#     print(mp3_file)
#     # Replace 'input_audio_file.mp3' with the path to your input audio file
#     # Replace 'output_folder' with the desired output folder path
#     separate_vocals_with_spleeter(directory_path+'\\'+mp3_file, 'output_folder')
# separate_vocals_with_spleeter('output\\det.mp3','nnn')