import pysrt

def merge_srt_files(file1, file2, output_file):
    # Load the SRT files
    subs1 = pysrt.open(file1)
    subs2 = pysrt.open(file2)

    # Concatenate the subtitle lists
    merged_subs = subs1 + subs2

    # Sort the subtitles based on start time
    merged_subs.sort(key=lambda x: x.start)

    # Save the merged subtitles to a new file
    merged_subs.save(output_file, encoding='utf-8')

if __name__ == "__main__":
    file1 = "C:\\Users\\User\\Downloads\\The.Great.Escape.HDTVRip.400mb.ESubs_track3_eng.srt"
    file2 = "C:\\Users\\User\\Downloads\\SUBDL.com__the.great.escape1034666\\The.Great.Escape.HDTVRip.400mb.ESubs_track3_eng.srt"
    output_file = "merged_subtitle.srt"

    merge_srt_files(file1, file2, output_file)