from spleeter.separator import Separator

# Initialize Spleeter with desired output file names
separator = Separator('spleeter:2stems')
separator.separate_to_file('input_segments\\segment_1.mp3', 'output_directory', filename_format='vocals.mp3')
