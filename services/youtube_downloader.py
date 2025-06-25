import os
import yt_dlp

def get_ydl_opts(output_path=None):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # تحسين اختيار الصيغة
        'merge_output_format': 'mp4',
        'ignoreerrors': True,  # تجاهل الأخطاء والاستمرار في التنزيل
        'no_warnings': False,
        'extract_flat': False,
        'quiet': False,
        'verbose': True,
    }
    
    if output_path:
        ydl_opts['outtmpl'] = os.path.join(output_path, '%(title)s.%(ext)s')
    
    return ydl_opts

def download_video(url, output_path='./videos', progress_callback=None):
    try:
        ydl_opts = get_ydl_opts(output_path)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            if video_title:
                print(f"جاري تنزيل: {video_title}")
            ydl.download([url])
            video_file_path = ydl.prepare_filename(info_dict)
            
            if not os.path.exists(video_file_path):
                # محاولة البحث عن الملف بامتداد مختلف
                base_path = video_file_path.rsplit('.', 1)[0]
                for ext in ['.mp4', '.mkv', '.webm']:
                    alt_path = base_path + ext
                    if os.path.exists(alt_path):
                        video_file_path = alt_path
                        break
            
            return video_title, video_file_path
    except Exception as e:
        print(f"خطأ في تنزيل الفيديو: {e}")
        return None, None

def download_playlist(url, output_path='./videos', send_to_telegram=False, progress_callback=None):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    video_paths = {}
    ydl_opts = get_ydl_opts(output_path)
    ydl_opts.update({
        'extract_flat': 'in_playlist',
        'ignoreerrors': True,
        'no_warnings': True,
        'playliststart': 1,
        'quiet': False,
        'verbose': True,
    })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            
            if 'entries' in info_dict:
                # قائمة تشغيل
                playlist_title = info_dict.get('title', 'Playlist')
                print(f"جاري تنزيل قائمة التشغيل: {playlist_title}")
                
                for i, entry in enumerate(info_dict['entries'], 1):
                    if entry is None:
                        continue
                    try:
                        video_title = entry.get('title', f'Video {i}')
                        video_file_path = ydl.prepare_filename(entry)
                        # download the video
                        ydl.download([entry['url']])
                        
                        # التحقق من وجود الملف بامتدادات مختلفة
                        if not os.path.exists(video_file_path):
                            base_path = video_file_path.rsplit('.', 1)[0]
                            for ext in ['.mp4', '.mkv', '.webm']:
                                alt_path = base_path + ext
                                if os.path.exists(alt_path):
                                    video_file_path = alt_path
                                    break
                        
                        if os.path.exists(video_file_path):
                            video_paths[video_title] = video_file_path
                            print(f"تم تنزيل الفيديو {i}: {video_title}")
                        else:
                            print(f"فشل تنزيل الفيديو {i}: {video_title}")
                            
                    except Exception as e:
                        print(f"خطأ في تنزيل الفيديو {i}: {str(e)}")
                        continue
            else:
                # فيديو واحد
                video_title = info_dict['title']
                video_file_path = ydl.prepare_filename(info_dict)
                if os.path.exists(video_file_path):
                    video_paths[video_title] = video_file_path
                    print(f"تم تنزيل الفيديو: {video_title}")
                
    except Exception as e:
        print(f"خطأ في تنزيل قائمة التشغيل: {str(e)}")
    
    return video_paths

if __name__ == "__main__":
    # اختبار التنزيل
    url_test = "https://www.youtube.com/watch?v=ZMaGXWVuWvY"
    download_video(url_test, output_path='../test_output')