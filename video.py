import os
class Video:
    def __init__(self,processing_input_folder,url="",input_video_path="",send_to_telegram = False):
        self._url = url
        self._input_video_path = input_video_path
        self._output_video_path = ""
        self._processing_input_folder = processing_input_folder
        self._detached_mp3 = ""
        self._audio_segments_paths = []
        self._vocals_paths = []
        self._output_audio_path = ""
        self._send_to_telegram = send_to_telegram 
        self._video_thumbnail_path = ""
        self._video_duration = ""
        self._caption = os.path.basename(input_video_path).replace('.mp4','')

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def input_video_path(self):
        return self._input_video_path

    @input_video_path.setter
    def input_video_path(self, value):
        self._input_video_path = value

    @property
    def output_video_path(self):
        return self._output_video_path

    @output_video_path.setter
    def output_video_path(self, value):
        self._output_video_path = value

    @property
    def processing_input_folder(self):
        return self._processing_input_folder

    @processing_input_folder.setter
    def processing_input_folder(self, value):
        self._processing_input_folder = value

    @property
    def detached_mp3(self):
        return self._detached_mp3

    @detached_mp3.setter
    def detached_mp3(self, value):
        self._detached_mp3 = value

    @property
    def audio_segments_paths(self):
        return self._audio_segments_paths

    @audio_segments_paths.setter
    def audio_segments_paths(self, value):
        self._audio_segments_paths = value

    @property
    def vocals_paths(self):
        return self._vocals_paths

    @vocals_paths.setter
    def vocals_paths(self, value):
        self._vocals_paths = value

    @property
    def output_audio_path(self):
        return self._output_audio_path

    @output_audio_path.setter
    def output_audio_path(self, value):
        self._output_audio_path = value

    @property
    def send_to_telegram(self):
        return self._send_to_telegram

    @send_to_telegram.setter
    def send_to_telegram(self, value):
        self._send_to_telegram = value

    @property
    def video_thumbnail_path(self):
        return self._video_thumbnail_path

    @video_thumbnail_path.setter
    def video_thumbnail_path(self, value):
        self._video_thumbnail_path = value

    @property
    def video_duration(self):
        return self._video_duration

    @video_duration.setter
    def video_duration(self, value):
        self._video_duration = value

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, value):
        self._caption = value


# Example usage:
# my_video = Video()
# my_video.url = "https://example.com/video.mp4"
# my_video.input_video_path = "input.mp4"
# my_video.output_video_path = "output.mp4"
# my_video.processing_input_folder = "processing_output"
# my_video.detached_mp3 = "audio.mp3"
# my_video.audio_segments_paths = ["segment1.wav", "segment2.wav"]
# my_video.vocals_paths = ["vocals1.wav", "vocals2.wav"]
# my_video.output_audio_path = "output_audio.wav"
# my_video.send_to_telegram = True
# my_video.video_thumbnail_path = "thumbnail.jpg"
# my_video.video_duration = "2:30"
# my_video.caption = "Check out this amazing video!"
