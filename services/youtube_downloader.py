import os
import yt_dlp
def download_video(url, output_path='./videos', progress_callback=None):
    try:
        # yt = YouTube(url)
        # video_title = yt.title
        # video_stream = yt.streams.get_highest_resolution()
        # video_file_path = video_stream.download(output_path)


        ydl_opts = {
        'format': 'best',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }],
    }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            if video_title:
                print(f"Downloading: {video_title}")
            ydl.download([url])
            video_file_path=ydl.prepare_filename(info_dict)
        return video_title, video_file_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None, None

def download_playlist(url, output_path='./videos', send_to_telegram=False, progress_callback=None):
    ydl_opts = {
        'format': 'best',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }],
    }
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    video_paths = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        if 'entries' in info_dict:
            # Playlist
            print(f"Downloading playlist: {info_dict['title']}")
            for i, entry in enumerate(info_dict['entries']):
                video_title = entry['title']
                video_file_path = ydl.prepare_filename(entry)
                video_paths[video_title] = video_file_path
                print(f"Downloading video {i+1}/{len(info_dict['entries'])}: {entry['title']}")
        else:
            # Single video
            print(f"Downloading video: {info_dict['title']}")
    return video_paths 

if __name__ == "__main__":
    download_video("https://www.youtube.com/watch?v=ZMaGXWVuWvY&pp=ygUV2LPZiNix2Kkg2KfZhNmD2YjYq9ix",output_path='../absher1')