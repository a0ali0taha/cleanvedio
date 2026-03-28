import os
import json
import requests
import subprocess
import time
import threading
from typing import List, Dict, Optional, Callable
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JDownloaderIntegration:
    """
    JDownloader Integration Class
    Provides multiple methods to integrate with JDownloader for video downloading
    """
    
    def __init__(self, jdownloader_path: str = None, api_url: str = "http://localhost:3128"):
        """
        Initialize JDownloader integration
        
        Args:
            jdownloader_path: Path to JDownloader executable (optional)
            api_url: JDownloader API URL (default: http://localhost:3128)
        """
        self.jdownloader_path = jdownloader_path
        self.api_url = api_url
        self.session = requests.Session()
        
    def add_links_to_jdownloader(self, urls: List[str], output_folder: str = None) -> bool:
        """
        Add video URLs to JDownloader's linkgrabber
        
        Args:
            urls: List of video URLs to add
            output_folder: Optional output folder path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Method 1: Using JDownloader's built-in link adding
            if self.jdownloader_path and os.path.exists(self.jdownloader_path):
                return self._add_links_via_cli(urls, output_folder)
            
            # Method 2: Using JDownloader's web interface
            return self._add_links_via_web(urls, output_folder)
            
        except Exception as e:
            logger.error(f"Error adding links to JDownloader: {e}")
            return False
    
    def _add_links_via_cli(self, urls: List[str], output_folder: str = None) -> bool:
        """
        Add links using JDownloader CLI
        """
        try:
            for url in urls:
                cmd = [self.jdownloader_path, "--add-links", url]
                if output_folder:
                    cmd.extend(["--output-directory", output_folder])
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(f"Failed to add link {url}: {result.stderr}")
                    
            return True
            
        except Exception as e:
            logger.error(f"Error using JDownloader CLI: {e}")
            return False
    
    def _add_links_via_web(self, urls: List[str], output_folder: str = None) -> bool:
        """
        Add links using JDownloader's web interface
        """
        try:
            # JDownloader web interface typically runs on port 3128
            web_url = f"{self.api_url}/linkgrabber/add"
            
            for url in urls:
                data = {
                    "urls": url,
                    "autostart": False,
                    "packageName": "Videos"
                }
                
                if output_folder:
                    data["downloadFolder"] = output_folder
                
                response = self.session.post(web_url, json=data)
                if response.status_code != 200:
                    logger.warning(f"Failed to add link {url}: {response.text}")
                    
            return True
            
        except Exception as e:
            logger.error(f"Error using JDownloader web interface: {e}")
            return False
    
    def create_download_package(self, urls: List[str], package_name: str = "Videos", 
                               output_folder: str = None) -> bool:
        """
        Create a download package in JDownloader
        
        Args:
            urls: List of video URLs
            package_name: Name for the download package
            output_folder: Output folder path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a DLC (Download Link Container) file
            dlc_data = {
                "package_name": package_name,
                "urls": urls,
                "output_folder": output_folder or "./downloads"
            }
            
            dlc_file = f"{package_name}.dlc"
            with open(dlc_file, 'w') as f:
                json.dump(dlc_data, f, indent=2)
            
            # Add DLC file to JDownloader
            if self.jdownloader_path:
                subprocess.run([self.jdownloader_path, "--add-links", dlc_file])
            
            # Clean up DLC file
            os.remove(dlc_file)
            return True
            
        except Exception as e:
            logger.error(f"Error creating download package: {e}")
            return False
    
    def get_download_status(self) -> Dict:
        """
        Get current download status from JDownloader
        
        Returns:
            Dict: Download status information
        """
        try:
            status_url = f"{self.api_url}/downloads/status"
            response = self.session.get(status_url)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get status: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting download status: {e}")
            return {"error": str(e)}
    
    def start_downloads(self) -> bool:
        """
        Start all pending downloads in JDownloader
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            start_url = f"{self.api_url}/downloads/start"
            response = self.session.post(start_url)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error starting downloads: {e}")
            return False
    
    def pause_downloads(self) -> bool:
        """
        Pause all downloads in JDownloader
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            pause_url = f"{self.api_url}/downloads/pause"
            response = self.session.post(pause_url)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error pausing downloads: {e}")
            return False
    
    def clear_finished_downloads(self) -> bool:
        """
        Clear finished downloads from JDownloader
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            clear_url = f"{self.api_url}/downloads/clear"
            response = self.session.post(clear_url)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error clearing downloads: {e}")
            return False
    
    def monitor_downloads(self, callback: Callable = None, interval: int = 5) -> None:
        """
        Monitor download progress
        
        Args:
            callback: Optional callback function to handle status updates
            interval: Check interval in seconds
        """
        def monitor():
            while True:
                try:
                    status = self.get_download_status()
                    if callback:
                        callback(status)
                    else:
                        logger.info(f"Download status: {status}")
                    
                    time.sleep(interval)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error monitoring downloads: {e}")
                    time.sleep(interval)
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        return monitor_thread

# Convenience functions for easy integration
def add_videos_to_jdownloader(urls: List[str], output_folder: str = None) -> bool:
    """
    Convenience function to add video URLs to JDownloader
    
    Args:
        urls: List of video URLs
        output_folder: Optional output folder
        
    Returns:
        bool: True if successful, False otherwise
    """
    jd = JDownloaderIntegration()
    return jd.add_links_to_jdownloader(urls, output_folder)

def create_video_package(urls: List[str], package_name: str = "Videos", 
                        output_folder: str = None) -> bool:
    """
    Convenience function to create a video download package
    
    Args:
        urls: List of video URLs
        package_name: Package name
        output_folder: Output folder
        
    Returns:
        bool: True if successful, False otherwise
    """
    jd = JDownloaderIntegration()
    return jd.create_download_package(urls, package_name, output_folder)

def get_jdownloader_status() -> Dict:
    """
    Convenience function to get JDownloader status
    
    Returns:
        Dict: Status information
    """
    jd = JDownloaderIntegration()
    return jd.get_download_status()

# Integration with existing YouTube downloader
class JDownloaderYouTubeIntegration:
    """
    Integration class that combines YouTube URL extraction with JDownloader
    """
    
    def __init__(self, jdownloader_path: str = None):
        self.jd = JDownloaderIntegration(jdownloader_path)
    
    def download_youtube_videos(self, youtube_urls: List[str], 
                               output_folder: str = "./videos",
                               package_name: str = "YouTube Videos") -> bool:
        """
        Download YouTube videos using JDownloader
        
        Args:
            youtube_urls: List of YouTube URLs
            output_folder: Output folder for downloads
            package_name: Name for the download package
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add YouTube URLs directly to JDownloader
            # JDownloader can handle YouTube URLs natively
            success = self.jd.add_links_to_jdownloader(youtube_urls, output_folder)
            
            if success:
                logger.info(f"Added {len(youtube_urls)} YouTube URLs to JDownloader")
                logger.info(f"Output folder: {output_folder}")
                logger.info("Please start downloads in JDownloader application")
                return True
            else:
                logger.error("Failed to add YouTube URLs to JDownloader")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading YouTube videos: {e}")
            return False
    
    def download_youtube_playlist(self, playlist_url: str,
                                 output_folder: str = "./videos",
                                 package_name: str = "YouTube Playlist") -> bool:
        """
        Download YouTube playlist using JDownloader
        
        Args:
            playlist_url: YouTube playlist URL
            output_folder: Output folder for downloads
            package_name: Name for the download package
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # JDownloader can handle YouTube playlist URLs directly
            success = self.jd.add_links_to_jdownloader([playlist_url], output_folder)
            
            if success:
                logger.info(f"Added YouTube playlist to JDownloader: {playlist_url}")
                logger.info(f"Output folder: {output_folder}")
                logger.info("Please start downloads in JDownloader application")
                return True
            else:
                logger.error("Failed to add YouTube playlist to JDownloader")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading YouTube playlist: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    # Example 1: Basic usage
    urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=9bZkp7q19f0"
    ]
    
    # Add videos to JDownloader
    success = add_videos_to_jdownloader(urls, "./downloads")
    print(f"Added videos to JDownloader: {success}")
    
    # Example 2: Using the integration class
    jd_integration = JDownloaderYouTubeIntegration()
    success = jd_integration.download_youtube_videos(urls, "./videos", "Test Videos")
    print(f"YouTube videos added: {success}")
    
    # Example 3: Monitor downloads
    def status_callback(status):
        print(f"Download status: {status}")
    
    jd = JDownloaderIntegration()
    monitor_thread = jd.monitor_downloads(status_callback, interval=10)
    
    # Keep the script running to monitor downloads
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Monitoring stopped") 