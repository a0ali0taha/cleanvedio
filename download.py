from pytube import YouTube

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

# Replace 'https://www.youtube.com/watch?v=YOUR_VIDEO_ID' with the YouTube URL of the video you want to download
# Replace 'output_folder' with the desired path to save the downloaded video
download_youtube_video('https://www.youtube.com/watch?v=txdwffCNTuc', 'download_folder')