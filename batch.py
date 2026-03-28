from main import handle
import os
from video import Video


def start_dir(dir):
    i = 1
    folder_list = os.listdir(dir)
    for file in folder_list:
        filename = os.path.basename(file)
        name, ext = os.path.splitext(filename)
        processing_input_folder = os.path.join(dir, str(i))
        video_path = os.path.join(dir, file)
        video = Video(
            processing_input_folder=processing_input_folder,
            input_video_path=video_path,
        )
        handle(video)
        i = i + 1


def start_file(video_path):
    base_path, ext = os.path.splitext(video_path)
    processing_input_folder = base_path
    video = Video(
        processing_input_folder=processing_input_folder,
        input_video_path=video_path,
    )
    handle(video)


if __name__ == "__main__":
    # No default run on import; call start_dir(...) or start_file(...) from a script.
    pass
