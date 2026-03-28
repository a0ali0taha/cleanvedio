import os
import re
import unicodedata
import yt_dlp
from typing import List, Dict, Optional, Tuple
import logging

# Fix the import to work when running the file directly
try:
    from .jdownloader_integration import JDownloaderYouTubeIntegration, JDownloaderIntegration
except ImportError:
    # Fallback for when running the file directly
    from jdownloader_integration import JDownloaderYouTubeIntegration, JDownloaderIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _sanitize_video_path(file_path):
    """Normalize Unicode in filename to prevent encoding errors on Windows.
    
    Converts fullwidth punctuation (e.g. ＂ → ") to ASCII equivalents via NFKC,
    then strips characters that are invalid in Windows filenames or can't be
    encoded by the default console codepage.
    """
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    normalized = unicodedata.normalize('NFKC', base_name)
    sanitized = re.sub(r'[<>:"|?*]', '_', normalized)
    if sanitized != base_name:
        new_path = os.path.join(dir_name, sanitized)
        if os.path.exists(file_path) and not os.path.exists(new_path):
            os.rename(file_path, new_path)
        return new_path
    return file_path


class YouTubeDownloaderWithJDownloader:
    """
    Enhanced YouTube downloader with JDownloader integration
    Provides both direct download and JDownloader integration options
    """
    
    def __init__(self, use_jdownloader: bool = False, jdownloader_path: str = None):
        """
        Initialize the downloader
        
        Args:
            use_jdownloader: Whether to use JDownloader for downloads
            jdownloader_path: Path to JDownloader executable
        """
        self.use_jdownloader = use_jdownloader
        self.jd_integration = None
        
        if use_jdownloader:
            self.jd_integration = JDownloaderYouTubeIntegration(jdownloader_path)
    
    def get_ydl_opts(self, output_path=None):
        """Get yt-dlp options"""
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'ignoreerrors': True,
            'no_warnings': False,
            'extract_flat': False,
            'quiet': False,
            'verbose': True,
        }
        
        if output_path:
            ydl_opts['outtmpl'] = os.path.join(output_path, '%(title)s.%(ext)s')
        
        return ydl_opts
    
    def download_video(self, url: str, output_path: str = './videos', 
                      progress_callback=None) -> Tuple[Optional[str], Optional[str]]:
        """
        Download a single video
        
        Args:
            url: YouTube video URL
            output_path: Output directory
            progress_callback: Optional progress callback
            
        Returns:
            Tuple of (video_title, video_file_path) or (None, None) if failed
        """
        if self.use_jdownloader and self.jd_integration:
            return self._download_with_jdownloader([url], output_path)
        else:
            return self._download_with_ytdlp(url, output_path, progress_callback)
    
    def download_playlist(self, url: str, output_path: str = './videos',
                         progress_callback=None) -> Dict[str, str]:
        """
        Download a playlist

        Args:
            url: YouTube playlist URL
            output_path: Output directory
            progress_callback: Optional progress callback

        Returns:
            Dict mapping video titles to file paths
        """
        if self.use_jdownloader and self.jd_integration:
            return self._download_playlist_with_jdownloader(url, output_path)
        else:
            return self._download_playlist_with_ytdlp(url, output_path, progress_callback)
    
    def _download_with_jdownloader(self, urls: List[str], output_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Download using JDownloader"""
        try:
            success = self.jd_integration.download_youtube_videos(urls, output_path)
            if success:
                logger.info(f"Added {len(urls)} videos to JDownloader")
                # Return placeholder values since JDownloader handles the actual download
                return "JDownloader Download", "JDownloader will handle the download"
            else:
                logger.error("Failed to add videos to JDownloader")
                return None, None
        except Exception as e:
            logger.error(f"Error with JDownloader download: {e}")
            return None, None
    
    def _download_with_ytdlp(self, url: str, output_path: str, 
                           progress_callback=None) -> Tuple[Optional[str], Optional[str]]:
        """Download using yt-dlp"""
        try:
            ydl_opts = self.get_ydl_opts(output_path)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_title = info_dict.get('title', None)
                if video_title:
                    logger.info(f"جاري تنزيل: {video_title}")
                ydl.download([url])
                video_file_path = ydl.prepare_filename(info_dict)
                
                if not os.path.exists(video_file_path):
                    # Try different extensions
                    base_path = video_file_path.rsplit('.', 1)[0]
                    for ext in ['.mp4', '.mkv', '.webm']:
                        alt_path = base_path + ext
                        if os.path.exists(alt_path):
                            video_file_path = alt_path
                            break
                
                video_file_path = _sanitize_video_path(video_file_path)
                return video_title, video_file_path
        except Exception as e:
            logger.error(f"خطأ في تنزيل الفيديو: {e}")
            return None, None
    
    def _download_playlist_with_jdownloader(self, url: str, output_path: str) -> Dict[str, str]:
        """Download playlist using JDownloader"""
        try:
            success = self.jd_integration.download_youtube_playlist(url, output_path)
            if success:
                logger.info(f"Added playlist to JDownloader: {url}")
                # Return placeholder since JDownloader handles the download
                return {"JDownloader Playlist": "JDownloader will handle the download"}
            else:
                logger.error("Failed to add playlist to JDownloader")
                return {}
        except Exception as e:
            logger.error(f"Error with JDownloader playlist download: {e}")
            return {}
    
    def _download_playlist_with_ytdlp(self, url: str, output_path: str,
                                    progress_callback=None) -> Dict[str, str]:
        """Download playlist using yt-dlp"""
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        video_paths = {}
        ydl_opts = self.get_ydl_opts(output_path)
        ydl_opts.update({
            'extract_flat': 'in_playlist',
            'ignoreerrors': True,
            'no_warnings': True,
            'playliststart': 1,
            'quiet': False,
            'verbose': True,
        })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                
                if 'entries' in info_dict:
                    # Playlist
                    playlist_title = info_dict.get('title', 'Playlist')
                    logger.info(f"جاري تنزيل قائمة التشغيل: {playlist_title}")
                    
                    for i, entry in enumerate(info_dict['entries'], 1):
                        if entry is None:
                            continue
                        try:
                            video_title = entry.get('title', f'Video {i}')
                            video_file_path = ydl.prepare_filename(entry)
                            # download the video
                            ydl.download([entry['url']])
                            
                            # Check for file with different extensions
                            if not os.path.exists(video_file_path):
                                base_path = video_file_path.rsplit('.', 1)[0]
                                for ext in ['.mp4', '.mkv', '.webm']:
                                    alt_path = base_path + ext
                                    if os.path.exists(alt_path):
                                        video_file_path = alt_path
                                        break
                            
                            video_file_path = _sanitize_video_path(video_file_path)
                            if os.path.exists(video_file_path):
                                video_paths[video_title] = video_file_path
                                logger.info(f"تم تنزيل الفيديو {i}: {video_title}")
                            else:
                                logger.error(f"فشل تنزيل الفيديو {i}: {video_title}")
                                
                        except Exception as e:
                            logger.error(f"خطأ في تنزيل الفيديو {i}: {str(e)}")
                            continue
                else:
                    # Single video
                    video_title = info_dict['title']
                    video_file_path = ydl.prepare_filename(info_dict)
                    video_file_path = _sanitize_video_path(video_file_path)
                    if os.path.exists(video_file_path):
                        video_paths[video_title] = video_file_path
                        logger.info(f"تم تنزيل الفيديو: {video_title}")
                    
        except Exception as e:
            logger.error(f"خطأ في تنزيل قائمة التشغيل: {str(e)}")
        
        return video_paths
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get video information without downloading
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dict with video information or None if failed
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                return {
                    'title': info_dict.get('title'),
                    'duration': info_dict.get('duration'),
                    'uploader': info_dict.get('uploader'),
                    'view_count': info_dict.get('view_count'),
                    'upload_date': info_dict.get('upload_date'),
                    'thumbnail': info_dict.get('thumbnail'),
                    'description': info_dict.get('description'),
                    'formats': [f.get('format_id') for f in info_dict.get('formats', [])]
                }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    def get_playlist_info(self, url: str) -> Optional[Dict]:
        """
        Get playlist information without downloading
        
        Args:
            url: YouTube playlist URL
            
        Returns:
            Dict with playlist information or None if failed
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                return {
                    'title': info_dict.get('title'),
                    'uploader': info_dict.get('uploader'),
                    'video_count': len(info_dict.get('entries', [])),
                    'videos': [
                        {
                            'title': entry.get('title'),
                            'duration': entry.get('duration'),
                            'url': entry.get('url')
                        }
                        for entry in info_dict.get('entries', [])
                        if entry is not None
                    ]
                }
        except Exception as e:
            logger.error(f"Error getting playlist info: {e}")
            return None

# Convenience functions for backward compatibility
def download_video(url: str, output_path: str = './videos', 
                  use_jdownloader: bool = False, progress_callback=None) -> Tuple[Optional[str], Optional[str]]:
    """
    Download a single video with optional JDownloader integration
    
    Args:
        url: YouTube video URL
        output_path: Output directory
        use_jdownloader: Whether to use JDownloader
        progress_callback: Optional progress callback
        
    Returns:
        Tuple of (video_title, video_file_path) or (None, None) if failed
    """
    downloader = YouTubeDownloaderWithJDownloader(use_jdownloader=use_jdownloader)
    logger.info(f"Downloading video: {url}")
    return downloader.download_video(url, output_path, progress_callback)

def download_playlist(url: str, output_path: str = './videos',
                     use_jdownloader: bool = False,
                     progress_callback=None) -> Dict[str, str]:
    """
    Download a playlist with optional JDownloader integration

    Args:
        url: YouTube playlist URL
        output_path: Output directory
        use_jdownloader: Whether to use JDownloader
        progress_callback: Optional progress callback

    Returns:
        Dict mapping video titles to file paths
    """
    downloader = YouTubeDownloaderWithJDownloader(use_jdownloader=use_jdownloader)
    return downloader.download_playlist(url, output_path, progress_callback)

# Example usage
if __name__ == "__main__":
    # Example 1: Download with yt-dlp (default)
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    title, path = download_video(url, "./videos")
    print(f"Downloaded: {title} -> {path}")
    
    # # Example 2: Download with JDownloader
    # title, path = download_video(url, "./videos", use_jdownloader=True)
    # print(f"Added to JDownloader: {title} -> {path}")
    
    # # Example 3: Get video info
    # downloader = YouTubeDownloaderWithJDownloader()
    # info = downloader.get_video_info(url)
    # print(f"Video info: {info}") 