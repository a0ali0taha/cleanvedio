from pytube import YouTube
from moviepy.editor import *
import os

def download_youtube_video(video_url, output_path):
    try:
        # Create a YouTube object for the specified video URL
        yt = YouTube(video_url)

        # Get the highest resolution stream available
        video_stream = yt.streams.get_highest_resolution()

        # Download the video to the specified output path
        video_stream.download(output_path)

        print("Video download complete.")
    except Exception as e:
        print(f"Error while downloading the video: {e}")


def detach_audio(video_path, output_audio_path):
    # Load the video clip
    video_clip = VideoFileClip(video_path)

    # Get the audio part of the video
    audio_clip = video_clip.audio

    # Save the audio to a file
    audio_clip.write_audiofile(output_audio_path)

    # Close the video and audio clips
    video_clip.close()
    audio_clip.close()

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

import subprocess

def separate_vocals_with_spleeter(input_audio_path, output_folder):
    spleeter_command = [
        "spleeter",
        "separate",
        "-i",
        input_audio_path,
        "-p",
        "spleeter:2stems",
        "-o",
        output_folder
    ]

    try:
        subprocess.run(spleeter_command, check=True)
        print("Vocals separated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error while calling Spleeter: {e}")


def attach_audio(video_path, audio_path, output_video_path):
    # Load the video clip
    video_clip = VideoFileClip(video_path)

    # Load the audio clip
    audio_clip = AudioFileClip(audio_path)

    # Set the audio of the video clip to the loaded audio clip
    video_clip = video_clip.set_audio(audio_clip)

    # Save the video with the attached audio
    video_clip.write_videofile(output_video_path, codec="libx264")

    # Close the video and audio clips
    video_clip.close()
    audio_clip.close()



import datetime
import glob

def process_all_videos_in_dir(directory):
    # Get a list of all mp4 files in the directory
    mp4_files = glob.glob(os.path.join(directory, "*.mp4"))

    # Process each mp4 file
    for mp4_file in mp4_files:
        # Detach audio
        detached_audio = 'output\\det.wav'
        detach_audio(mp4_file, detached_audio)

        # Separate vocals with spleeter
        separate_vocals_with_spleeter(detached_audio, 'output')

        # Attach audio
        attach_audio(mp4_file, 'output\\det\\vocals.wav', 'final\\' + os.path.basename(mp4_file))

# Get the current date and time
current_time = datetime.datetime.now()
time_format = "%Y-%m-%d %H:%M:%S"  # Year-Month-Day Hour:Minute:Second
formatted_time = current_time.strftime(time_format)

# Print the current time
print("Current time:", formatted_time)


# Replace 'https://www.youtube.com/watch?v=YOUR_VIDEO_ID' with the YouTube URL of the video you want to download
# Replace 'output_folder' with the desired path to save the downloaded video
dir= 'download_folder'
download_youtube_video('https://www.youtube.com/watch?v=WcKgqocYukI', dir)

# Process all videos in the directory
process_all_videos_in_dir(dir)

current_time = datetime.datetime.now()
time_format = "%Y-%m-%d %H:%M:%S"  # Year-Month-Day Hour:Minute:Second
formatted_time = current_time.strftime(time_format)

# Print the current time
print("Current time:", formatted_time)