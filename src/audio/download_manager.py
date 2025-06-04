"""
Audio Download Manager - Handles automated track downloading from various sources
"""
import os
import requests
import time
from typing import List, Dict, Optional
from urllib.parse import urlparse
import hashlib
from pathlib import Path
from config.settings import AUDIO_CACHE_DIR, TARGET_BITRATE, TARGET_SAMPLE_RATE
from src.audio.social_media_downloader import SocialMediaDownloader

class AudioDownloadManager:
    def __init__(self, cache_dir: str = AUDIO_CACHE_DIR):
        self.cache_dir = cache_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AutoDJ/1.0 (Music Discovery Bot)'
        })
        
        # Initialize social media downloader
        self.social_downloader = SocialMediaDownloader(cache_dir)
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
    
    def download_track(self, track: Dict, source_url: str = None) -> Optional[str]:
        """Download a track from various sources"""
        
        if not source_url:
            # Try to find download URL from track metadata
            source_url = self._find_download_url(track)
        
        if not source_url:
            print(f"No download URL found for {track.get('artist')} - {track.get('title')}")
            return None
        
        # Generate filename
        filename = self._generate_filename(track)
        filepath = os.path.join(self.cache_dir, filename)
        
        # Check if already downloaded
        if os.path.exists(filepath):
            print(f"✅ Already cached: {filename}")
            return filepath
        
        try:
            print(f"⬇️  Downloading: {track.get('artist')} - {track.get('title')}")
            
            response = self.session.get(source_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r   Progress: {progress:.1f}%", end='', flush=True)
            
            print(f"\n✅ Downloaded: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ Download failed for {filename}: {e}")
            # Clean up partial download
            if os.path.exists(filepath):
                os.remove(filepath)
            return None
    
    def download_playlist(self, tracks: List[Dict], include_social_media: bool = True) -> Dict[str, str]:
        """Download all tracks in a playlist with fallback to social media"""
        
        results = {}
        successful = 0
        
        print(f"🎵 Starting download of {len(tracks)} tracks...")
        
        for i, track in enumerate(tracks, 1):
            track_name = f"{track.get('artist')} - {track.get('title')}"
            print(f"\n[{i}/{len(tracks)}] Processing: {track_name}")
            
            # Try traditional download first
            filepath = self.download_track(track)
            
            # If traditional download failed and social media is enabled, try social platforms
            if not filepath and include_social_media:
                print(f"   Traditional download failed, trying social media...")
                filepath = self.social_downloader.search_and_download_track(track)
            
            if filepath:
                results[track_name] = filepath
                successful += 1
            else:
                results[track_name] = None
            
            # Rate limiting
            time.sleep(1)
        
        print(f"\n🎉 Download complete: {successful}/{len(tracks)} tracks successful")
        return results
    
    def download_from_social_media_only(self, tracks: List[Dict], platforms: List[str] = None) -> Dict[str, str]:
        """Download tracks exclusively from social media platforms"""
        
        if not self.social_downloader.has_ytdlp:
            print("❌ yt-dlp not available for social media downloads")
            return {}
        
        return self.social_downloader.batch_download(tracks, platforms)
    
    def download_from_url(self, url: str, artist: str, title: str) -> Optional[str]:
        """Download audio from a direct TikTok or SoundCloud URL"""
        
        return self.social_downloader.download_from_direct_url(url, artist, title)
    
    def search_social_media(self, track: Dict, platforms: List[str] = None) -> Optional[str]:
        """Search and download from social media platforms only"""
        
        return self.social_downloader.search_and_download_track(track, platforms)
    
    def _find_download_url(self, track: Dict) -> Optional[str]:
        """Find download URL from track metadata"""
        
        # Check for direct download URLs in track data
        if track.get('download_url'):
            return track['download_url']
        
        # Check for Bandcamp URLs
        if track.get('bandcamp_url'):
            return self._get_bandcamp_download_url(track['bandcamp_url'])
        
        # Check for SoundCloud URLs
        if track.get('soundcloud_url'):
            return self._get_soundcloud_download_url(track['soundcloud_url'])
        
        # Check for free/legal sources
        if track.get('free_download_url'):
            return track['free_download_url']
        
        return None
    
    def _get_bandcamp_download_url(self, bandcamp_url: str) -> Optional[str]:
        """Extract download URL from Bandcamp (for purchased tracks)"""
        # This would require Bandcamp API integration
        # For now, return None - will implement in Phase 2
        return None
    
    def _get_soundcloud_download_url(self, soundcloud_url: str) -> Optional[str]:
        """Extract download URL from SoundCloud (for downloadable tracks)"""
        # This would require SoundCloud API integration
        # For now, return None - will implement in Phase 2
        return None
    
    def _generate_filename(self, track: Dict) -> str:
        """Generate safe filename for track"""
        
        artist = self._sanitize_filename(track.get('artist', 'Unknown'))
        title = self._sanitize_filename(track.get('title', 'Unknown'))
        
        # Create filename with format: Artist - Title.mp3
        filename = f"{artist} - {title}.mp3"
        
        # Ensure unique filename if duplicate
        base_path = os.path.join(self.cache_dir, filename)
        counter = 1
        
        while os.path.exists(base_path):
            name, ext = os.path.splitext(filename)
            filename = f"{name} ({counter}){ext}"
            base_path = os.path.join(self.cache_dir, filename)
            counter += 1
        
        return filename
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility"""
        
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove extra spaces and limit length
        filename = ' '.join(filename.split())
        return filename[:50].strip()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        
        if not os.path.exists(self.cache_dir):
            return {'total_files': 0, 'total_size': 0, 'cache_dir': self.cache_dir}
        
        total_files = 0
        total_size = 0
        
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                if file.endswith(('.mp3', '.wav', '.flac', '.m4a')):
                    filepath = os.path.join(root, file)
                    total_files += 1
                    total_size += os.path.getsize(filepath)
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': self.cache_dir
        }
    
    def clear_cache(self) -> bool:
        """Clear download cache"""
        
        try:
            import shutil
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
