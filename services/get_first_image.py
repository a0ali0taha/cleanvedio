import subprocess

def get_thumbnail(video):
    video_input_path = video.input_video_path
    thumbnail_path = video_input_path + '.thumbnail.jpg'
    subprocess.call(['ffmpeg', '-i', video_input_path, '-ss', '00:00:20.000', '-vframes', '1', thumbnail_path])
    video.video_thumbnail_path=thumbnail_path