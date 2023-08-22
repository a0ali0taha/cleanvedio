import os
import sys
import detach
import audio_split
import spleeter_code
import audio_merge
import attach

def process_mp4_files(directory):
    files = os.listdir(directory)
    mp4_files = [f for f in files if f.endswith('.mp4')]

    for mp4_file in mp4_files:
        video_path = os.path.join(directory, mp4_file)
        audio_path = os.path.join(directory, f'{mp4_file}_audio.mp3')
        detach.detach_audio(video_path, audio_path)

        segments = audio_split.split(audio_path)
        separated_files = []
        for i, segment in enumerate(segments):
            output_file = os.path.join(directory, f'{mp4_file}_segment_{i+1}.mp3')
            spleeter_code.separator.separate_to_file(segment, output_file)
            separated_files.append(output_file)

        merged_audio_path = os.path.join(directory, f'{mp4_file}_merged.mp3')
        audio_merge.merge(separated_files, merged_audio_path)

        final_video_path = os.path.join(directory, f'{mp4_file}_final.mp4')
        attach.attach_audio(video_path, merged_audio_path, final_video_path)

if __name__ == "__main__":
    directory = sys.argv[1]
    proce

