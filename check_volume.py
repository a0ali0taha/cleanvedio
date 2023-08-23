from pydub import AudioSegment
import math

def check_volume_level(sound):
    rms = sound.rms
    dbfs = 20 * math.log10(rms)
    return dbfs

def increase_volume(sound, output_file, increase_factor):
    louder_sound = sound + increase_factor
    louder_sound.export(output_file, format="mp3")

input_file = "C:\\Users\\User\\Downloads\\bug\\1\\samev\\segment_1.mp3"  # Replace with your MP3 file
output_file = "C:\\Users\\User\\Downloads\\bug\\1\\samev\\segment_2s.mp3"  # Replace with desired output file path
threshold_dbfs = 75  # Adjust the threshold as needed

sound = AudioSegment.from_file(input_file)
volume_level = check_volume_level(sound)
if volume_level < threshold_dbfs:
    print("Audio volume is too low. Increasing the volume...")
    increase_factor = threshold_dbfs - volume_level
    increase_volume(sound, output_file, increase_factor)
else:
    print("Audio volume is sufficient.")