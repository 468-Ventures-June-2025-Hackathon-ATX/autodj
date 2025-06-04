"""
Social Media Audio Downloader - Extract full audio tracks from TikTok and SoundCloud
"""
import os
import subprocess
import json
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import re
from config.settings import AUDIO_CACHE_DIR, TARGET_BITRATE, TARGET_SAMPLE_RATE

class SocialMediaDownloader:
    def __init__(self, cache_dir: str = AUDIO_CACHE_DIR):
        self.cache_dir = cache_dir
        self.social_cache_dir = os.path.join(cache_dir, "social_media")
        
        # Create cache directories
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.social_cache_dir, exist_ok=True)
        
        # Check if yt-dlp is available
        self.has_ytdlp = self._check_ytdlp()
        
        if not self.has_ytdlp:
            print("⚠️  yt-dlp not found. Install with: pip install yt-dlp")
    
    def _check_ytdlp(self) -> bool:
        """Check if yt-dlp is available"""
        try:
            subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def search_and_download_track(self, track: Dict, platforms: List[str] = None) -> Optional[str]:
        """Search for and download a track from social media platforms"""
        
        if not self.has_ytdlp:
            print("❌ yt-dlp not available for social media downloads")
            return None
        
        if platforms is None:
            platforms = ['soundcloud', 'tiktok']
        
        artist = track.get('artist', '')
        title = track.get('title', '')
        
        if not artist or not title:
            print("❌ Missing artist or title information")
            return None
        
        print(f"🔍 Searching for: {artist} - {title}")
        
        # Try each platform
        for platform in platforms:
            try:
                print(f"   Trying {platform.upper()}...")
                
                if platform == 'soundcloud':
                    filepath = self._download_from_soundcloud(artist, title, track)
                elif platform == 'tiktok':
                    filepath = self._download_from_tiktok(artist, title, track)
                else:
                    continue
                
                if filepath and os.path.exists(filepath):
                    print(f"✅ Successfully downloaded from {platform.upper()}")
                    return filepath
                    
            except Exception as e:
                print(f"❌ {platform.upper()} download failed: {e}")
                continue
        
        print(f"❌ Could not find {artist} - {title} on any platform")
        return None
    
    def _download_from_soundcloud(self, artist: str, title: str, track: Dict) -> Optional[str]:
        """Download track from SoundCloud"""
        
        # Generate search query
        search_query = f"{artist} {title}".strip()
        
        # Check if we already have a SoundCloud URL
        soundcloud_url = track.get('soundcloud_url')
        
        if not soundcloud_url:
            # Search for the track on SoundCloud
            soundcloud_url = self._search_soundcloud(search_query)
        
        if not soundcloud_url:
            return None
        
        return self._download_from_url(soundcloud_url, artist, title, 'soundcloud')
    
    def _download_from_tiktok(self, artist: str, title: str, track: Dict) -> Optional[str]:
        """Download track from TikTok"""
        
        # Generate search query
        search_query = f"{artist} {title}".strip()
        
        # Check if we already have a TikTok URL
        tiktok_url = track.get('tiktok_url')
        
        if not tiktok_url:
            # Search for the track on TikTok
            tiktok_url = self._search_tiktok(search_query)
        
        if not tiktok_url:
            return None
        
        return self._download_from_url(tiktok_url, artist, title, 'tiktok')
    
    def _search_soundcloud(self, query: str) -> Optional[str]:
        """Search for a track on SoundCloud"""
        
        try:
            # Use yt-dlp to search SoundCloud with a simpler approach
            search_url = f"ytsearch1:{query} site:soundcloud.com"
            
            cmd = [
                'yt-dlp',
                '--get-url',
                '--no-playlist',
                '--quiet',
                '--no-warnings',
                search_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0 and result.stdout.strip():
                url = result.stdout.strip()
                # Check if it's actually a SoundCloud URL
                if 'soundcloud.com' in url:
                    return url
            
            return None
            
        except Exception as e:
            print(f"SoundCloud search error: {e}")
            return None
    
    def _search_tiktok(self, query: str) -> Optional[str]:
        """Search for a track on TikTok"""
        
        try:
            # Use yt-dlp to search TikTok
            search_url = f"ytsearch1:site:tiktok.com {query}"
            
            cmd = [
                'yt-dlp',
                '--get-url',
                '--no-playlist',
                '--quiet',
                search_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            return None
            
        except Exception as e:
            print(f"TikTok search error: {e}")
            return None
    
    def _download_from_url(self, url: str, artist: str, title: str, platform: str) -> Optional[str]:
        """Download audio from a specific URL"""
        
        # Generate filename
        safe_artist = self._sanitize_filename(artist)
        safe_title = self._sanitize_filename(title)
        filename = f"{safe_artist} - {safe_title} [{platform}].%(ext)s"
        filepath_template = os.path.join(self.social_cache_dir, filename)
        
        # Check if already downloaded
        for ext in ['mp3', 'wav', 'm4a', 'webm']:
            existing_file = filepath_template.replace('%(ext)s', ext)
            if os.path.exists(existing_file):
                print(f"✅ Already cached: {os.path.basename(existing_file)}")
                return existing_file
        
        try:
            print(f"⬇️  Downloading from {platform.upper()}: {url}")
            
            # yt-dlp command for audio extraction
            cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '0',  # Best quality
                '--output', filepath_template,
                '--no-playlist',
                '--quiet',
                '--no-warnings',
                url
            ]
            
            # Add platform-specific options
            if platform == 'tiktok':
                cmd.extend([
                    '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                ])
            elif platform == 'soundcloud':
                cmd.extend([
                    '--cookies-from-browser', 'chrome'  # Use browser cookies if available
                ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                # Find the downloaded file
                downloaded_file = filepath_template.replace('%(ext)s', 'mp3')
                
                if os.path.exists(downloaded_file):
                    print(f"✅ Downloaded: {os.path.basename(downloaded_file)}")
                    return downloaded_file
                else:
                    # Check for other extensions
                    for ext in ['wav', 'm4a', 'webm']:
                        alt_file = filepath_template.replace('%(ext)s', ext)
                        if os.path.exists(alt_file):
                            print(f"✅ Downloaded: {os.path.basename(alt_file)}")
                            return alt_file
            
            print(f"❌ Download failed: {result.stderr}")
            return None
            
        except subprocess.TimeoutExpired:
            print("❌ Download timeout")
            return None
        except Exception as e:
            print(f"❌ Download error: {e}")
            return None
    
    def download_from_direct_url(self, url: str, artist: str, title: str) -> Optional[str]:
        """Download audio from a direct URL (TikTok or SoundCloud link)"""
        
        if not self.has_ytdlp:
            return None
        
        # Determine platform from URL
        platform = 'unknown'
        if 'tiktok.com' in url:
            platform = 'tiktok'
        elif 'soundcloud.com' in url:
            platform = 'soundcloud'
        
        return self._download_from_url(url, artist, title, platform)
    
    def get_track_info(self, url: str) -> Optional[Dict]:
        """Get track information from a URL without downloading"""
        
        if not self.has_ytdlp:
            return None
        
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-playlist',
                '--quiet',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                
                return {
                    'title': info.get('title', ''),
                    'uploader': info.get('uploader', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', ''),
                    'upload_date': info.get('upload_date', ''),
                    'url': url,
                    'platform': 'tiktok' if 'tiktok.com' in url else 'soundcloud' if 'soundcloud.com' in url else 'unknown'
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting track info: {e}")
            return None
    
    def batch_download(self, tracks: List[Dict], platforms: List[str] = None) -> Dict[str, str]:
        """Download multiple tracks from social media"""
        
        if not self.has_ytdlp:
            print("❌ yt-dlp not available for social media downloads")
            return {}
        
        results = {}
        successful = 0
        
        print(f"🎵 Starting social media download of {len(tracks)} tracks...")
        
        for i, track in enumerate(tracks, 1):
            track_name = f"{track.get('artist')} - {track.get('title')}"
            print(f"\n[{i}/{len(tracks)}] Processing: {track_name}")
            
            filepath = self.search_and_download_track(track, platforms)
            
            if filepath:
                results[track_name] = filepath
                successful += 1
            else:
                results[track_name] = None
            
            # Rate limiting to avoid being blocked
            time.sleep(2)
        
        print(f"\n🎉 Social media download complete: {successful}/{len(tracks)} tracks successful")
        return results
    
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
        """Get social media cache statistics"""
        
        if not os.path.exists(self.social_cache_dir):
            return {'total_files': 0, 'total_size': 0, 'cache_dir': self.social_cache_dir}
        
        total_files = 0
        total_size = 0
        
        for root, dirs, files in os.walk(self.social_cache_dir):
            for file in files:
                if file.endswith(('.mp3', '.wav', '.flac', '.m4a', '.webm')):
                    filepath = os.path.join(root, file)
                    total_files += 1
                    total_size += os.path.getsize(filepath)
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': self.social_cache_dir
        }
    
    def clear_cache(self) -> bool:
        """Clear social media download cache"""
        
        try:
            import shutil
            if os.path.exists(self.social_cache_dir):
                shutil.rmtree(self.social_cache_dir)
                os.makedirs(self.social_cache_dir, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error clearing social media cache: {e}")
            return False
