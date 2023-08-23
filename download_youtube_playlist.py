
import cv2

<<<< UPDATED
import os
import tkinter as tk
from tkinter import messagebox, BooleanVar
from pytube import Playlist, YouTube
from telegram_sender import send_to_telegram


def download_video(url, output_path='./videos'):
    try:
        yt = YouTube(url)
        video_title = yt.title
        video_file_path = yt.streams.get_highest_resolution().download(output_path)
        return video_title, video_file_path
    except Exception as e:
        messagebox.showerror("Error", f"Error downloading video: {e}")
        return None, None

def download_playlist(url, output_path='./videos', send_to_telegram=False):
    playlist = Playlist(url)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for video in playlist.videos:
        try:
            video_title = video.title
            video.streams.get_highest_resolution().download(output_path)
            if send_to_telegram:
                video_file_path = os.path.join(output_path, f"{video.title}.mp4")
                asyncio.run(send_to_telegram(video_title, video_file_path)_
        except Exception as e:
            messagebox.showerror("Error", f"Error downloading {video.title}: {e}")


def download_button_clicked():
    playlist_url = entry_url.get()
    output_path = entry_output.get()
    send_to_telegram_flag = checkbox_telegram_var.get()

    if not playlist_url:
        messagebox.showwarning("Warning", "Please enter a valid YouTube URL.")
        return

    if checkbox_var.get():
        download_playlist(playlist_url, output_path, send_to_telegram_flag)
        messagebox.showinfo("Success", "Playlist downloaded successfully.")
    else:
        video_title, video_file_path = download_video(playlist_url, output_path)
        if video_title and video_file_path and send_to_telegram_flag:
            send_to_telegram(video_title, video_file_path)
            messagebox.showinfo("Success", "Video downloaded and sent to Telegram successfully.")
        elif video_title and video_file_path:
            messagebox.showinfo("Success", "Video downloaded successfully.")

# Create the GUI window
window = tk.Tk()
window.title("YouTube Downloader & Telegram Sender")

# Create and place widgets
label_url = tk.Label(window, text="Enter YouTube URL:")
label_url.pack(pady=5)

entry_url = tk.Entry(window, width=50)
entry_url.pack(pady=5)

label_output = tk.Label(window, text="Enter Output Folder Path (optional):")
label_output.pack(pady=5)

entry_output = tk.Entry(window, width=50)
entry_output.pack(pady=5)

checkbox_var = BooleanVar()
checkbox_var.set(True)
checkbox = tk.Checkbutton(window, text="Download Playlist", variable=checkbox_var)
checkbox.pack(pady=5)

checkbox_telegram_var = BooleanVar()
checkbox_telegram_var.set(True)
checkbox_telegram = tk.Checkbutton(window, text="Send to Telegram", variable=checkbox_telegram_var)
checkbox_telegram.pack(pady=5)

checkbox_blur_var = BooleanVar()
checkbox_blur_var.set(False)
checkbox_blur = tk.Checkbutton(window, text="Blur Faces in Video", variable=checkbox_blur_var)
checkbox_blur.pack(pady=5)

btn_download = tk.Button(window, text="Download", command=download_button_clicked)
btn_download.pack(pady=10)

# Start the GUI event loop
window.mainloop()