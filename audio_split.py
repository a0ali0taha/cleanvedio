from pydub import AudioSegment

def split_audio_by_duration(audio_file, segment_duration_ms=550000):
    audio = AudioSegment.from_file(audio_file)

    # Calculate the number of segments needed
    num_segments = len(audio) // segment_duration_ms

    # Split the audio into segments
    audio_segments = [audio[i * segment_duration_ms:(i + 1) * segment_duration_ms] for i in range(num_segments+1)]

    return audio_segments

# if __name__ == "__main__":
#     input_audio_file = "output\\det.mp3"
#     segments = split_audio_by_duration(input_audio_file)

#     for i, segment in enumerate(segments):
#         output_file = f"segment_{i+1}.mp3"
#         segment.export('input_segments\\'+output_file, format="mp3")
#newv\vtitle.mp3
def split(input_audio_file):
    segments = split_audio_by_duration(input_audio_file)
    segments_files=[]
    for i, segment in enumerate(segments):
        output_file = f"{input_audio_file}_{i+1}"
        segment.export( output_file, format="mp3")
        segments_files.append(output_file)
    return segments_files