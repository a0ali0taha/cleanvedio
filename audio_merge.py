from pydub import AudioSegment
import os
def combine_audio_segments(segment_files):
    combined_audio = AudioSegment.empty()

    for segment_file in segment_files:
        segment = AudioSegment.from_file(segment_file)
        combined_audio += segment

    return combined_audio

# if __name__ == "__main__":
#     # directory_path = 'output_folder\\segment_1\vocals.mp3'
#     directory_path = 'output_folder'

#     # List all files in the directory
#     folder_list = os.listdir(directory_path)
#     segment_files=[]
#     for vocal_folder in folder_list:
#     # Perform operations on each MP3 file
#         segment_files.append(directory_path+'\\'+vocal_folder+'\\vocals.mp3')
#     combined_audio = combine_audio_segments(segment_files)
#     output_file = "output_folder\\combined_audio.mp3"
#     combined_audio.export(output_file, format="mp3")