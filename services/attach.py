"""
Attach processed audio to the source video.

Historically this used MoviePy ``write_videofile``, which **re-encodes** the entire
video (decode every frame + encode again). For long HD files that is extremely
slow. This module uses **ffmpeg** to **copy** the video stream (``-c:v copy``)
and mux only a new AAC audio track, which is typically I/O-bound and much faster.
"""

import os
import shutil
import subprocess
import uuid


def get_last_file_in_dir(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None
    sorted_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(directory, f)))
    return sorted_files[-1]


def _resolve_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    return None


def _ffmpeg_mux_video_copy_audio_aac(video_path, audio_path, out_path):
    ffmpeg = _resolve_ffmpeg()
    if not ffmpeg:
        raise RuntimeError(
            "ffmpeg was not found on PATH. Install ffmpeg or add it to PATH (see server runtime layout)."
        )
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        video_path,
        "-i",
        audio_path,
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        out_path,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=None, check=False)
    except OSError as e:
        raise RuntimeError(f"failed to run ffmpeg: {e}") from e
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip()
        tail = err[-4000:] if len(err) > 4000 else err
        raise RuntimeError(f"ffmpeg mux failed (exit {r.returncode}): {tail}")


def attach_audio(video):
    video_path = video.input_video_path
    audio_path = video.output_audio_path
    output_video_path = video.output_video_path

    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"video not found: {video_path}")
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"audio not found: {audio_path}")

    output_dir = os.path.dirname(output_video_path)
    os.makedirs(output_dir, exist_ok=True)
    ext = os.path.splitext(output_video_path)[1]
    temp_path = os.path.join(output_dir, f"_tmp_{uuid.uuid4().hex[:8]}{ext}")

    try:
        _ffmpeg_mux_video_copy_audio_aac(video_path, audio_path, temp_path)
        if os.path.exists(output_video_path):
            os.remove(output_video_path)
        os.replace(temp_path, output_video_path)
    except Exception:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise


# dir= 'download_folder'

# downloaded_file_name = get_last_file_in_dir(dir)
# downloaded_file_dir = dir+'\\'+downloaded_file_name
# detached_audio = 'output_folder\\combined_audio.mp3'
# attach_audio(downloaded_file_dir, detached_audio, 'final\\'+downloaded_file_name)
# attach_audio('newv\in.mp4','newv\\1\\combined_audio.mp3','final\\newv\\1\\out.mp4')
if __name__ == "__main__":
    raise SystemExit("Use pipeline / batch: attach_audio expects a video.Video instance.")
