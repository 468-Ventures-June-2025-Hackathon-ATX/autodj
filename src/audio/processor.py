"""
Audio Processor - Handles audio format conversion, metadata tagging, and quality optimization
"""
import os
import subprocess
import json
from typing import Dict, Optional, List
from pathlib import Path
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, TBPM, TKEY
from config.settings import TARGET_BITRATE, TARGET_SAMPLE_RATE

class AudioProcessor:
    def __init__(self):
        self.target_bitrate = TARGET_BITRATE
        self.target_sample_rate = TARGET_SAMPLE_RATE
        
        # Check for required tools
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required audio tools are available"""
        
        try:
            # Check for ffmpeg
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
            self.has_ffmpeg = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Warning: ffmpeg not found. Audio conversion will be limited.")
            self.has_ffmpeg = False
    
    def process_track(self, input_path: str, track_metadata: Dict, output_path: str = None) -> Optional[str]:
        """Process a single track with conversion and metadata"""
        
        if not os.path.exists(input_path):
            print(f"❌ Input file not found: {input_path}")
            return None
        
        if not output_path:
            output_path = self._generate_output_path(input_path, track_metadata)
        
        try:
            # Step 1: Convert audio format if needed
            converted_path = self._convert_audio(input_path, output_path)
            
            if not converted_path:
                print(f"❌ Audio conversion failed for {input_path}")
                return None
            
            # Step 2: Add metadata tags
            self._add_metadata(converted_path, track_metadata)
            
            # Step 3: Validate output
            if self._validate_audio(converted_path):
                print(f"✅ Processed: {os.path.basename(converted_path)}")
                return converted_path
            else:
                print(f"❌ Validation failed for {converted_path}")
                return None
                
        except Exception as e:
            print(f"❌ Processing failed for {input_path}: {e}")
            return None
    
    def process_playlist(self, tracks_with_paths: Dict[str, str], track_metadata: List[Dict]) -> Dict[str, str]:
        """Process all tracks in a playlist"""
        
        results = {}
        successful = 0
        
        print(f"🎵 Processing {len(tracks_with_paths)} audio files...")
        
        # Create metadata lookup
        metadata_lookup = {f"{track.get('artist')} - {track.get('title')}": track 
                          for track in track_metadata}
        
        for track_name, input_path in tracks_with_paths.items():
            if input_path is None:
                results[track_name] = None
                continue
            
            print(f"\n🔧 Processing: {track_name}")
            
            # Get metadata for this track
            metadata = metadata_lookup.get(track_name, {})
            
            # Process the track
            output_path = self.process_track(input_path, metadata)
            
            if output_path:
                results[track_name] = output_path
                successful += 1
            else:
                results[track_name] = None
        
        print(f"\n🎉 Processing complete: {successful}/{len(tracks_with_paths)} tracks successful")
        return results
    
    def _convert_audio(self, input_path: str, output_path: str) -> Optional[str]:
        """Convert audio to target format and quality"""
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # If input is already MP3 with good quality, just copy
        if self._is_good_quality_mp3(input_path):
            import shutil
            shutil.copy2(input_path, output_path)
            return output_path
        
        if not self.has_ffmpeg:
            # Fallback: just copy the file
            import shutil
            shutil.copy2(input_path, output_path)
            return output_path
        
        try:
            # FFmpeg command for high-quality conversion
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-codec:a', 'libmp3lame',
                '-b:a', f'{self.target_bitrate}k',
                '-ar', str(self.target_sample_rate),
                '-channels', '2',
                '-y',  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return output_path
            else:
                print(f"FFmpeg error: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Conversion error: {e}")
            return None
    
    def _is_good_quality_mp3(self, filepath: str) -> bool:
        """Check if MP3 is already good quality"""
        
        try:
            audio = MP3(filepath)
            
            # Check bitrate
            if hasattr(audio.info, 'bitrate') and audio.info.bitrate >= self.target_bitrate * 1000:
                return True
            
            return False
            
        except Exception:
            return False
    
    def _add_metadata(self, filepath: str, metadata: Dict):
        """Add ID3 metadata tags to MP3 file"""
        
        try:
            audio = MP3(filepath, ID3=ID3)
            
            # Add ID3 tag if it doesn't exist
            if audio.tags is None:
                audio.add_tags()
            
            # Clear existing tags
            audio.tags.clear()
            
            # Add metadata
            if metadata.get('title'):
                audio.tags.add(TIT2(encoding=3, text=metadata['title']))
            
            if metadata.get('artist'):
                audio.tags.add(TPE1(encoding=3, text=metadata['artist']))
            
            if metadata.get('label'):
                audio.tags.add(TALB(encoding=3, text=metadata['label']))
            
            if metadata.get('genre'):
                audio.tags.add(TCON(encoding=3, text=metadata['genre']))
            
            if metadata.get('bpm'):
                audio.tags.add(TBPM(encoding=3, text=str(metadata['bpm'])))
            
            if metadata.get('key'):
                audio.tags.add(TKEY(encoding=3, text=metadata['key']))
            
            if metadata.get('release_date'):
                audio.tags.add(TDRC(encoding=3, text=metadata['release_date']))
            
            # Save tags
            audio.save()
            
        except Exception as e:
            print(f"Metadata tagging failed: {e}")
    
    def _validate_audio(self, filepath: str) -> bool:
        """Validate processed audio file"""
        
        try:
            # Check file exists and has size
            if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:
                return False
            
            # Try to load with mutagen
            audio = mutagen.File(filepath)
            if audio is None:
                return False
            
            # Check duration (should be > 30 seconds for real tracks)
            if hasattr(audio.info, 'length') and audio.info.length < 30:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _generate_output_path(self, input_path: str, metadata: Dict) -> str:
        """Generate output path for processed file"""
        
        # Get base directory from input
        base_dir = os.path.dirname(input_path)
        
        # Generate clean filename
        artist = self._sanitize_filename(metadata.get('artist', 'Unknown'))
        title = self._sanitize_filename(metadata.get('title', 'Unknown'))
        
        filename = f"{artist} - {title}.mp3"
        
        return os.path.join(base_dir, filename)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility"""
        
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove extra spaces and limit length
        filename = ' '.join(filename.split())
        return filename[:50].strip()
    
    def get_audio_info(self, filepath: str) -> Dict:
        """Get detailed audio file information"""
        
        try:
            audio = mutagen.File(filepath)
            
            if audio is None:
                return {'error': 'Could not read audio file'}
            
            info = {
                'filepath': filepath,
                'filename': os.path.basename(filepath),
                'filesize': os.path.getsize(filepath),
                'filesize_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2)
            }
            
            # Audio properties
            if hasattr(audio.info, 'length'):
                info['duration'] = round(audio.info.length, 2)
                info['duration_formatted'] = self._format_duration(audio.info.length)
            
            if hasattr(audio.info, 'bitrate'):
                info['bitrate'] = audio.info.bitrate
            
            if hasattr(audio.info, 'sample_rate'):
                info['sample_rate'] = audio.info.sample_rate
            
            if hasattr(audio.info, 'channels'):
                info['channels'] = audio.info.channels
            
            # Metadata tags
            if hasattr(audio, 'tags') and audio.tags:
                info['title'] = str(audio.tags.get('TIT2', [''])[0])
                info['artist'] = str(audio.tags.get('TPE1', [''])[0])
                info['album'] = str(audio.tags.get('TALB', [''])[0])
                info['genre'] = str(audio.tags.get('TCON', [''])[0])
                info['bpm'] = str(audio.tags.get('TBPM', [''])[0])
                info['key'] = str(audio.tags.get('TKEY', [''])[0])
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in MM:SS format"""
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def batch_analyze(self, directory: str) -> List[Dict]:
        """Analyze all audio files in a directory"""
        
        results = []
        
        if not os.path.exists(directory):
            return results
        
        for filename in os.listdir(directory):
            if filename.lower().endswith(('.mp3', '.wav', '.flac', '.m4a')):
                filepath = os.path.join(directory, filename)
                info = self.get_audio_info(filepath)
                results.append(info)
        
        return results
