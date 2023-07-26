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

def detach_audio(video_path, output_audio_path):
    # Load the video clip
    video_clip = VideoFileClip(video_path)

    # Get the audio part of the video
    audio_clip = video_clip.audio

    # Save the audio to a file
    audio_clip.write_audiofile(output_audio_path,codec="mp3")

    # Close the video and audio clips
    video_clip.close()
    audio_clip.close()

# Replace 'input_video.mp4' with the path to your input video file
# Replace 'output_audio.wav' with the desired path and filename for the output audio

# dir= 'download_folder'
# downloaded_file_name = get_last_file_in_dir(dir)
# downloaded_file_dir = dir+'\\'+downloaded_file_name
# detached_audio = 'output\\det.mp3'
# detach_audio(downloaded_file_dir, detached_audio)