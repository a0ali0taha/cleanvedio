# Import libraries
from pytube import Playlist, YouTube

# Get user input for playlist URL
playlist_url = input("Enter the YouTube playlist URL: ")

# Create a playlist object
playlist = Playlist(playlist_url)

# Function to download a single video
def download_video(video):
  try:
    # Select highest resolution progressive stream
    stream = video.streams.filter(progressive=True).order_by('resolution').desc().first()
    # Download the video to current directory
    stream.download()
    print(f"Downloaded: {video.title}")
  except Exception as e:
    print(f"Error downloading {video.title}: {e}")

# Download all videos in the playlist
for video in playlist.videos:
  download_video(video)

print("Playlist download complete!")
