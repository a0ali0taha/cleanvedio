from moviepy.editor import VideoFileClip

def cut_last_minutes(video_path, output_path):
    """
    Cuts the last 8 minutes from a video file
    
    Args:
        video_path (str): Path to input video file
        output_path (str): Path to save the trimmed video
    """
    try:
        # Load the video
        video = VideoFileClip(video_path)
        
        # Get video duration in seconds
        duration = video.duration
        
        # Calculate where to cut (8 minutes = 480 seconds from end)
        cut_point = max(0, duration - 480)
        
        # Cut the video from start to cut_point
        trimmed = video.subclip(0, cut_point)
        
        # Write the trimmed video
        trimmed.write_videofile(output_path)
        
        # Close the video to free up resources
        video.close()
        trimmed.close()
        
        return True
        
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return False
if __name__ == "__main__":
    video_path = "F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\final\\1000074607.mp4"
    output_path = "F:\\Ahmed\\lab\\scripts\\NoMusic\\cleanvedio\\final\\1000074607_cut.mp4"
    cut_last_minutes(video_path, output_path)   

