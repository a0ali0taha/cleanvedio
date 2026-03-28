import subprocess
import os
import gc
import shutil

from services.mylogger import logger

def separate_vocals_with_spleeter(input_audio_path, output_folder):
    # Add memory management flags to spleeter
    spleeter_command = [
        "spleeter",
        "separate",
        "-i",
        input_audio_path,
        "-p",
        "spleeter:2stems",
        "-o",
        output_folder,
        "-c",
        'mp3',
        "--verbose"  # Add verbose output for debugging
    ]

    try:
        # Force garbage collection before running spleeter
        gc.collect()
        
        subprocess.run(spleeter_command, check=True, capture_output=True, text=True)
        logger.info("Vocals separated successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Error while calling Spleeter: %s", e)
        logger.debug("Spleeter stdout: %s", e.stdout)
        logger.debug("Spleeter stderr: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return False
        
def create_vocals(video):
    vocals_folder = os.path.join(video.processing_input_folder, 'vocals')
    
    # Ensure vocals folder exists
    if not os.path.exists(vocals_folder):
        os.makedirs(vocals_folder)
    
    vocal_files = []

    for mp3_file in video.audio_segments_paths: 
        vocal_folder_seg = vocals_folder
        seg_name = os.path.basename(mp3_file).replace(".mp3", "")
        output_file = os.path.join(vocal_folder_seg, seg_name, 'vocals.mp3')
        
        logger.info("Processing: %s", mp3_file)
        logger.debug("Expected output: %s", output_file)

        if not os.path.exists(output_file):
            logger.info("Running spleeter for: %s", mp3_file)
            success = separate_vocals_with_spleeter(mp3_file, vocal_folder_seg)
            if not success:
                logger.warning("Failed to process %s, will use fallback", mp3_file)

        # Check if file was actually created
        if os.path.exists(output_file):
            vocal_files.append(output_file)
            logger.info("Added vocals file: %s", output_file)
        else:
            logger.warning("Expected vocals file not found: %s", output_file)
            if os.path.exists(vocal_folder_seg):
                logger.debug("Contents of %s: %s", vocal_folder_seg, os.listdir(vocal_folder_seg))
    
    # If Spleeter failed completely, use fallback approach
    if len(vocal_files) == 0:
        logger.warning("No vocals files created by Spleeter, using original audio segments as fallback")
        vocal_files = []
        for mp3_file in video.audio_segments_paths:
            # Create a copy of the original audio as "vocals"
            vocal_folder_seg = vocals_folder
            seg_name = os.path.basename(mp3_file).replace(".mp3", "")
            output_file = os.path.join(vocal_folder_seg, seg_name, 'vocals.mp3')
            
            # Ensure the subdirectory exists
            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Copy the original file as vocals
            shutil.copy2(mp3_file, output_file)
            vocal_files.append(output_file)
            logger.info("Created fallback vocals file: %s", output_file)

    video.vocals_paths = vocal_files
    logger.info("Total vocals files found/created: %s", len(vocal_files))

# Replace 'path_to_directory' with the actual path to the directory you want to explore
# Replace 'path_to_directory' with the actual path to the directory you want to explore
# directory_path = 'input_segments'

# # List all files in the directory
# file_list = os.listdir(directory_path)

# # Filter only the MP3 files
# mp3_files = [file for file in file_list if file.endswith('.mp3')]

# # Now you can work with the selected MP3 files
# for mp3_file in mp3_files:
#     # Perform operations on each MP3 file
#     print(mp3_file)
#     # Replace 'input_audio_file.mp3' with the path to your input audio file
#     # Replace 'output_folder' with the desired output folder path
#     separate_vocals_with_spleeter(directory_path+'\\'+mp3_file, 'output_folder')
# separate_vocals_with_spleeter('output\\det.mp3','nnn')
if __name__ == "__main__":
    separate_vocals_with_spleeter('C:\\Users\\User\\Downloads\\1\\seg_1.mp3', 'nnn')
