from moviepy.editor import *


def get_last_file_in_dir(directory):
    # Get a list of all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    if not files:
        return None  # Return None if the directory is empty

    # Sort the list of files based on their modification time (last modified file comes last)
    sorted_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(directory, x)))

    # Get the last file from the sorted list
    last_file = sorted_files[-1]

    # Return the absolute path of the last file
    return last_file

def attach_audio(video_path, audio_path, output_video_path):
    # Load the video clip
    video_clip = VideoFileClip(video_path)

    # Load the audio clip
    audio_clip = AudioFileClip(audio_path)

    # Set the audio of the video clip to the loaded audio clip
    video_clip = video_clip.set_audio(audio_clip)

    # Save the video with the attached audio
    video_clip.write_videofile(output_video_path, codec="libx264",bitrate="600k")

    # Close the video and audio clips
    video_clip.close()
    audio_clip.close()


dir= 'download_folder'

downloaded_file_name = get_last_file_in_dir(dir)
downloaded_file_dir = dir+'\\'+downloaded_file_name
detached_audio = 'output_folder\\combined_audio.mp3'
attach_audio(downloaded_file_dir, detached_audio, 'final\\'+downloaded_file_name)