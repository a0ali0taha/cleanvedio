from pydub import AudioSegment
import math
import os  # Add this import at the beginning of your file

def check_volume_level(sound):
    rms = sound.rms
    dbfs = 20 * math.log10(rms)
    return dbfs

def split_audio_by_duration(audio,num_segments, segment_duration_ms=550000):

 
   

    # Split the audio into segments
    audio_segments = [audio[i * segment_duration_ms:(i + 1) * segment_duration_ms] for i in range(num_segments+1)]

    return audio_segments

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
    segment_duration_ms=550000
    num_segments = len(audio) // segment_duration_ms

    existing_audio_files = [f for f in os.listdir(output_path) if f.startswith('seg_')]
    if num_segments <= len(existing_audio_files):
        segments_files = [os.path.join(output_path, f) for f in existing_audio_files]
        video.audio_segments_paths = segments_files
        return segments_files
    segments = split_audio_by_duration(audio,num_segments,segment_duration_ms)
    segments_files=[]
    increase_factor = threshold_dbfs - volume_level
    # add_more_volume
    for i, segment in enumerate(segments):
        output_file = f"{output_path}\\seg_{i+1}.mp3"
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
