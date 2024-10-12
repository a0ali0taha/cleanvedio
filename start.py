import asyncio
import os
import tkinter as tk
from tkinter import messagebox, BooleanVar
from main import start


def download_button_clicked():
    playlist_url = entry_url.get()
    output_path = entry_output.get() or 'newv'
    send_to_telegram_flag = checkbox_telegram_var.get()
    start(playlist_url,checkbox_var.get(),output_path,send_to_telegram_flag)
    os.system("shutdown /s /t {}".format(600))

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

btn_download = tk.Button(window, text="Download", command=download_button_clicked)
btn_download.pack(pady=10)                     

# Start the GUI event loop
window.mainloop()
