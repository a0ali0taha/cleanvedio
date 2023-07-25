import tkinter as tk
from tkinter import messagebox
from pytube import YouTube
import os
 
from moviepy.editor import *
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


def start_download_youtube_video():
    video_url = url_entry.get()
    output_directory = 'download_folder'

    if not video_url or not output_directory:
        messagebox.showerror("Error", "Please enter the YouTube URL and output directory.")
        return

    try:
        # here
        # Replace 'https://www.youtube.com/watch?v=YOUR_VIDEO_ID' with the YouTube URL of the video you want to download
        # Replace 'output_folder' with the desired path to save the downloaded video
        dir= 'download_folder'
        download_youtube_video(video_url, dir)

        # Replace 'input_video.mp4' with the path to your input video file
        # Replace 'output_audio.wav' with the desired path and filename for the output audio
        # Example usage:
        exit()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")



# Create the main window
root = tk.Tk()
root.title("YouTube Video Downloader")

# Create and place widgets
url_label = tk.Label(root, text="الرابط:")
url_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=5)

download_button = tk.Button(root, text="حول", command=start_download_youtube_video)
download_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Run the main event loop
root.mainloop()