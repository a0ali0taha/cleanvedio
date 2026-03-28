from pydub import AudioSegment
import math
import os  # Add this import at the beginning of your file

def check_volume_level(sound):
    rms = sound.rms
    dbfs = 20 * math.log10(rms)
    return dbfs

def split_audio_by_duration(audio, segment_count, segment_duration_ms=550000):
    return [
        audio[i * segment_duration_ms : (i + 1) * segment_duration_ms]
        for i in range(segment_count)
    ]

# if __name__ == "__main__":
#     input_audio_file = "output\\det.mp3"
#     segments = split_audio_by_duration(input_audio_file)

#     for i, segment in enumerate(segments):
#         output_file = f"segment_{i+1}.mp3"
#         segment.export('input_segments\\'+output_file, format="mp3")
##newv\1\vtitle.mp3,newv\1
def split_video(video):
    input_audio_file=video.detached_mp3
    output_path = video.processing_input_folder
    audio = AudioSegment.from_mp3(input_audio_file)
    volume_level = check_volume_level(audio)
    threshold_dbfs = 75 
    # Reduce segment duration to prevent memory issues with Spleeter
    segment_duration_ms = 180000  # 3 minutes (was 550000 ms)
    audio_len_ms = len(audio)
    segment_count = max(
        1, (audio_len_ms + segment_duration_ms - 1) // segment_duration_ms
    )

    def _seg_index(name):
        stem, _ = os.path.splitext(name)
        if stem.startswith("seg_") and stem[4:].isdigit():
            return int(stem[4:])
        return -1

    existing_audio_files = sorted(
        [f for f in os.listdir(output_path) if f.startswith("seg_")],
        key=_seg_index,
    )
    if len(existing_audio_files) >= segment_count:
        segments_files = [
            os.path.join(output_path, f) for f in existing_audio_files[:segment_count]
        ]
        video.audio_segments_paths = segments_files
        return segments_files
    segments = split_audio_by_duration(audio, segment_count, segment_duration_ms)
    segments_files=[]
    increase_factor = threshold_dbfs - volume_level
    # add_more_volume
    for i, segment in enumerate(segments):
        output_file = os.path.join(output_path, f"seg_{i+1}.mp3")
        #newv\1\seg_1.mp3
        if increase_factor > 0:
            segment = segment + increase_factor
            segment.export( output_file, format="mp3")
        else:
            segment.export( output_file, format="mp3")

        segments_files.append(output_file)
    video.audio_segments_paths=segments_files
    return segments_files
# from ..video import Video
# v=Video()
# v.detached_mp3="C:\\Users\\User\\Downloads\\bug\\1\\det.mp3"
# output_path = "C:\\Users\\User\\Downloads\\bug\\1"
# split_video(v)
# split_audio_by_duration()