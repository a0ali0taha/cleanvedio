from pydub import AudioSegment

def split_mp3_by_duration(input_file, output_dir, segment_duration):
    audio = AudioSegment.from_mp3(input_file)
    segment_length = segment_duration * 1000  # Convert to milliseconds
    
    for i in range(0, len(audio), segment_length):
        segment = audio[i:i+segment_length]
        output_path = f"{output_dir}/segment_{i//segment_length + 1}.mp3"
        
        # Match export settings to input audio
        segment = segment.set_channels(audio.channels)
        segment = segment.set_frame_rate(audio.frame_rate)
        segment= segment+20
        segment.export(output_path, format="mp3", parameters=["-q:a", "0"])

if __name__ == "__main__":
    input_file = "input.mp3"  # Replace with your input MP3 file
    output_dir = "output_segments"  # Replace with the desired output directory
    segment_duration = 550  # Duration of each segment in seconds
    
    split_mp3_by_duration("C:\\Users\\User\\Downloads\\bug\\1\\det.mp3", "C:\\Users\\User\\Downloads\\bug\\1\\samev2", segment_duration)
