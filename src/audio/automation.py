"""
Audio Automation Orchestrator - Coordinates the full download-to-USB pipeline
"""
import os
import time
from typing import List, Dict, Optional
from pathlib import Path

from src.audio.download_manager import AudioDownloadManager
from src.audio.processor import AudioProcessor
from src.beatport.web_automation import BeatportWebAutomation
from src.export.rekordbox_xml import RekordboxXMLGenerator
from config.settings import USB_EXPORT_DIR, AUDIO_CACHE_DIR

class AudioAutomation:
    def __init__(self):
        self.download_manager = AudioDownloadManager()
        self.audio_processor = AudioProcessor()
        self.xml_generator = RekordboxXMLGenerator()
        self.beatport_automation = None
        
        # Create necessary directories
        os.makedirs(USB_EXPORT_DIR, exist_ok=True)
        os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
    
    def setup_beatport_automation(self, email: str, password: str, headless: bool = True) -> bool:
        """Setup Beatport web automation with user credentials"""
        
        try:
            self.beatport_automation = BeatportWebAutomation(headless=headless)
            
            if self.beatport_automation.setup_driver():
                return self.beatport_automation.login(email, password)
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to setup Beatport automation: {e}")
            return False
    
    def process_full_pipeline(self, tracks: List[Dict], playlist_name: str, 
                            beatport_credentials: Dict = None) -> Dict:
        """Run the complete automation pipeline"""
        
        print("🚀 Starting Full Audio Automation Pipeline")
        print("=" * 60)
        
        pipeline_results = {
            'playlist_name': playlist_name,
            'total_tracks': len(tracks),
            'downloaded_tracks': {},
            'processed_tracks': {},
            'usb_export': None,
            'success_count': 0,
            'errors': []
        }
        
        try:
            # Phase 1: Download tracks
            print("\n📥 Phase 1: Downloading Tracks")
            print("-" * 40)
            
            downloaded_tracks = self._download_phase(tracks, beatport_credentials)
            pipeline_results['downloaded_tracks'] = downloaded_tracks
            
            # Phase 2: Process audio files
            print("\n🔧 Phase 2: Processing Audio Files")
            print("-" * 40)
            
            processed_tracks = self._processing_phase(downloaded_tracks, tracks)
            pipeline_results['processed_tracks'] = processed_tracks
            
            # Phase 3: Create USB export
            print("\n💾 Phase 3: Creating USB Export")
            print("-" * 40)
            
            usb_export = self._usb_export_phase(processed_tracks, tracks, playlist_name)
            pipeline_results['usb_export'] = usb_export
            
            # Calculate success metrics
            successful_tracks = [k for k, v in processed_tracks.items() if v is not None]
            pipeline_results['success_count'] = len(successful_tracks)
            
            print("\n🎉 Pipeline Complete!")
            print("=" * 60)
            print(f"✅ Successfully processed: {pipeline_results['success_count']}/{pipeline_results['total_tracks']} tracks")
            
            if pipeline_results['usb_export']:
                print(f"📁 USB Export: {pipeline_results['usb_export']['usb_path']}")
                print(f"📄 Rekordbox XML: {pipeline_results['usb_export']['xml_path']}")
            
            return pipeline_results
            
        except Exception as e:
            error_msg = f"Pipeline failed: {e}"
            print(f"❌ {error_msg}")
            pipeline_results['errors'].append(error_msg)
            return pipeline_results
        
        finally:
            # Cleanup
            if self.beatport_automation:
                self.beatport_automation.close()
    
    def _download_phase(self, tracks: List[Dict], beatport_credentials: Dict = None) -> Dict[str, str]:
        """Phase 1: Download all tracks"""
        
        downloaded_tracks = {}
        
        # Try different download sources
        
        # 1. Try free/legal sources first
        print("🆓 Attempting free/legal downloads...")
        free_downloads = self.download_manager.download_playlist(tracks)
        downloaded_tracks.update(free_downloads)
        
        # 2. Try Beatport automation if credentials provided
        if beatport_credentials and any(v is None for v in downloaded_tracks.values()):
            print("🛒 Attempting Beatport purchases...")
            
            if self.setup_beatport_automation(
                beatport_credentials.get('email', ''),
                beatport_credentials.get('password', ''),
                beatport_credentials.get('headless', True)
            ):
                # Only try to purchase tracks that weren't downloaded for free
                tracks_to_purchase = [
                    track for track in tracks 
                    if downloaded_tracks.get(f"{track.get('artist')} - {track.get('title')}") is None
                ]
                
                if tracks_to_purchase:
                    beatport_downloads = self.beatport_automation.purchase_playlist(tracks_to_purchase)
                    
                    # Update results
                    for track_name, download_path in beatport_downloads.items():
                        if download_path:
                            downloaded_tracks[track_name] = download_path
            else:
                print("❌ Failed to setup Beatport automation")
        
        return downloaded_tracks
    
    def _processing_phase(self, downloaded_tracks: Dict[str, str], track_metadata: List[Dict]) -> Dict[str, str]:
        """Phase 2: Process all downloaded audio files"""
        
        # Filter out failed downloads
        valid_downloads = {k: v for k, v in downloaded_tracks.items() if v is not None}
        
        if not valid_downloads:
            print("❌ No tracks to process")
            return {}
        
        # Process tracks
        processed_tracks = self.audio_processor.process_playlist(valid_downloads, track_metadata)
        
        return processed_tracks
    
    def _usb_export_phase(self, processed_tracks: Dict[str, str], track_metadata: List[Dict], 
                         playlist_name: str) -> Optional[Dict]:
        """Phase 3: Create USB export with audio files"""
        
        # Filter successful tracks
        successful_tracks = {k: v for k, v in processed_tracks.items() if v is not None}
        
        if not successful_tracks:
            print("❌ No processed tracks to export")
            return None
        
        try:
            # Create USB folder structure
            usb_music_dir = os.path.join(USB_EXPORT_DIR, "Music")
            os.makedirs(usb_music_dir, exist_ok=True)
            
            # Copy processed tracks to USB Music folder
            final_track_paths = {}
            
            for track_name, processed_path in successful_tracks.items():
                if processed_path and os.path.exists(processed_path):
                    # Copy to USB Music directory
                    filename = os.path.basename(processed_path)
                    usb_track_path = os.path.join(usb_music_dir, filename)
                    
                    import shutil
                    shutil.copy2(processed_path, usb_track_path)
                    
                    final_track_paths[track_name] = usb_track_path
                    print(f"📁 Copied to USB: {filename}")
            
            # Update track metadata with USB paths
            updated_tracks = []
            for track in track_metadata:
                track_name = f"{track.get('artist')} - {track.get('title')}"
                if track_name in final_track_paths:
                    track_copy = track.copy()
                    track_copy['file_path'] = final_track_paths[track_name]
                    updated_tracks.append(track_copy)
            
            # Generate Rekordbox XML with audio file references
            export_summary = self.xml_generator.export_for_pioneer(updated_tracks, playlist_name)
            
            # Validate the export
            validation = self.xml_generator.validate_xml()
            
            if validation['valid']:
                print("✅ USB export validation passed")
                return {
                    **export_summary,
                    'audio_files': len(final_track_paths),
                    'validation': validation
                }
            else:
                print("❌ USB export validation failed")
                for error in validation['errors']:
                    print(f"   - {error}")
                return None
                
        except Exception as e:
            print(f"❌ USB export failed: {e}")
            return None
    
    def get_pipeline_status(self) -> Dict:
        """Get current pipeline status and statistics"""
        
        # Cache stats
        cache_stats = self.download_manager.get_cache_stats()
        
        # USB export stats
        usb_stats = {'total_files': 0, 'total_size': 0}
        if os.path.exists(USB_EXPORT_DIR):
            for root, dirs, files in os.walk(USB_EXPORT_DIR):
                for file in files:
                    if file.lower().endswith(('.mp3', '.wav', '.flac', '.m4a')):
                        filepath = os.path.join(root, file)
                        usb_stats['total_files'] += 1
                        usb_stats['total_size'] += os.path.getsize(filepath)
        
        usb_stats['total_size_mb'] = round(usb_stats['total_size'] / (1024 * 1024), 2)
        
        return {
            'cache_stats': cache_stats,
            'usb_stats': usb_stats,
            'beatport_connected': self.beatport_automation is not None and self.beatport_automation.logged_in,
            'ffmpeg_available': self.audio_processor.has_ffmpeg
        }
    
    def clear_all_cache(self) -> bool:
        """Clear all cached files"""
        
        try:
            # Clear download cache
            cache_cleared = self.download_manager.clear_cache()
            
            # Clear USB export
            import shutil
            if os.path.exists(USB_EXPORT_DIR):
                shutil.rmtree(USB_EXPORT_DIR)
                os.makedirs(USB_EXPORT_DIR, exist_ok=True)
            
            return cache_cleared
            
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
    
    def test_dependencies(self) -> Dict[str, bool]:
        """Test all required dependencies"""
        
        results = {
            'ffmpeg': False,
            'chrome_driver': False,
            'mutagen': False,
            'selenium': False
        }
        
        # Test FFmpeg
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            results['ffmpeg'] = True
        except:
            pass
        
        # Test Chrome Driver
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            
            driver = webdriver.Chrome(options=options)
            driver.quit()
            results['chrome_driver'] = True
        except:
            pass
        
        # Test Mutagen
        try:
            import mutagen
            results['mutagen'] = True
        except:
            pass
        
        # Test Selenium
        try:
            import selenium
            results['selenium'] = True
        except:
            pass
        
        return results
