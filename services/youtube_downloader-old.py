# from pytube import Playlist, YouTube
# import os

# def download_video(url, output_path='./videos', progress_callback=None):
#     try:
#         yt = YouTube(url)
#         video_title = yt.title
#         video_stream = yt.streams.get_highest_resolution()
#         video_file_path = video_stream.download(output_path)
#         return video_title, video_file_path
#     except Exception as e:
#         print(f"Error downloading video: {e}")
#         return None, None

# def download_playlist(url, output_path='./videos', send_to_telegram=False, progress_callback=None):
#     playlist = Playlist(url)

#     if not os.path.exists(output_path):
#         os.makedirs(output_path)
#     video_paths = {}
#     for video in playlist.videos:
#         try:
#             video_title = video.title
#             # video_stream = video.streams.filter(res='480p').first() or video.streams.get_highest_resolution()
#             video_stream =  video.streams.get_highest_resolution()
#             video_file_path = video_stream.download(output_path)
#             video_paths[video_title] = video_file_path
#             if send_to_telegram:
#                 # Send to Telegram here if needed
#                 pass
#         except Exception as e:
#             print(f"Error downloading {video.title}: {e}")
#     return video_paths 

# if __name__ == "__main__":
#     download_video("https://www.youtube.com/watch?v=8xXEwqOevBI",output_path='../absher')
# import pytube

# def download_playlist(playlist_url):
#     """Downloads a YouTube playlist.

#     Args:
#         playlist_url: The URL of the YouTube playlist.
#     """

#     # Create a Playlist object from the URL
#     playlist = pytube.Playlist(playlist_url)

#     # Iterate through the videos in the playlist
#     for video in playlist.videos:
#         print(f"Downloading video: {video.title}")
#         video_stream = video.streams.first()
#         video_stream.download()
#         print(f"Downloaded: {video.title}")

# if __name__ == "__main__":
#     playlist_url = "https://www.youtube.com/playlist?list=PLmNPLKPi9xyNOKXinwEncuuHnMjg34IKr"
#     download_playlist(playlist_url)
