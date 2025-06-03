"""
Rekordbox XML playlist generator for Pioneer XDJ-RX3 compatibility
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from datetime import datetime
from typing import List, Dict
from config.settings import REKORDBOX_XML_PATH, USB_EXPORT_PATH

class RekordboxXMLGenerator:
    def __init__(self):
        self.xml_path = REKORDBOX_XML_PATH
        self.usb_path = USB_EXPORT_PATH
    
    def generate_playlist_xml(self, tracks: List[Dict], playlist_name: str, description: str = "") -> str:
        """Generate Rekordbox XML for a playlist"""
        
        # Create root element
        root = ET.Element("DJ_PLAYLISTS")
        root.set("Version", "1.0.0")
        
        # Add product info
        product = ET.SubElement(root, "PRODUCT")
        product.set("Name", "rekordbox")
        product.set("Version", "6.0.0")
        product.set("Company", "Pioneer DJ")
        
        # Add collection
        collection = ET.SubElement(root, "COLLECTION")
        collection.set("Entries", str(len(tracks)))
        
        # Add tracks to collection
        for i, track in enumerate(tracks):
            track_elem = self._create_track_element(track, i + 1)
            collection.append(track_elem)
        
        # Add playlists section
        playlists = ET.SubElement(root, "PLAYLISTS")
        
        # Add root node
        root_node = ET.SubElement(playlists, "NODE")
        root_node.set("Type", "0")
        root_node.set("Name", "ROOT")
        root_node.set("Count", "1")
        
        # Add playlist node
        playlist_node = ET.SubElement(root_node, "NODE")
        playlist_node.set("Type", "1")
        playlist_node.set("Name", playlist_name)
        playlist_node.set("KeyType", "0")
        playlist_node.set("Entries", str(len(tracks)))
        
        # Add tracks to playlist
        for i, track in enumerate(tracks):
            track_ref = ET.SubElement(playlist_node, "TRACK")
            track_ref.set("Key", str(i + 1))
        
        # Format XML
        xml_string = self._prettify_xml(root)
        
        # Save to file
        os.makedirs(os.path.dirname(self.xml_path), exist_ok=True)
        with open(self.xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        
        return xml_string
    
    def _create_track_element(self, track: Dict, track_id: int) -> ET.Element:
        """Create a track element for Rekordbox XML"""
        
        track_elem = ET.Element("TRACK")
        track_elem.set("TrackID", str(track_id))
        track_elem.set("Name", track.get('title', ''))
        track_elem.set("Artist", track.get('artist', ''))
        track_elem.set("Composer", track.get('artist', ''))
        track_elem.set("Album", track.get('label', ''))
        track_elem.set("Grouping", track.get('genre', ''))
        track_elem.set("Genre", track.get('genre', ''))
        track_elem.set("Kind", "MP3 File")
        track_elem.set("Size", "0")  # Will be updated when actual files are added
        track_elem.set("TotalTime", "300")  # Default 5 minutes, update with actual duration
        track_elem.set("DiscNumber", "0")
        track_elem.set("TrackNumber", "0")
        track_elem.set("Year", "2024")
        track_elem.set("AverageBpm", str(track.get('bpm', 120)))
        track_elem.set("DateAdded", datetime.now().strftime("%Y-%m-%d"))
        track_elem.set("BitRate", "320")
        track_elem.set("SampleRate", "44100")
        track_elem.set("Comments", f"Discovered via AutoDJ - {track.get('discovered_from', 'unknown')}")
        track_elem.set("PlayCount", "0")
        track_elem.set("Rating", "0")
        track_elem.set("Location", f"file://localhost/{self._get_track_file_path(track)}")
        track_elem.set("Remixer", "")
        track_elem.set("Tonality", track.get('key', ''))
        track_elem.set("Label", track.get('label', ''))
        track_elem.set("Mix", "")
        
        # Add tempo information
        if track.get('bpm'):
            tempo = ET.SubElement(track_elem, "TEMPO")
            tempo.set("Inizio", "0.000")
            tempo.set("Bpm", str(track.get('bpm')))
            tempo.set("Metro", "4/4")
            tempo.set("Battito", "1")
        
        # Add position mark (for cue points)
        position_mark = ET.SubElement(track_elem, "POSITION_MARK")
        position_mark.set("Name", "")
        position_mark.set("Type", "0")
        position_mark.set("Start", "0.000")
        position_mark.set("Num", "-1")
        
        return track_elem
    
    def _get_track_file_path(self, track: Dict) -> str:
        """Generate file path for track"""
        
        # Sanitize filename
        artist = self._sanitize_filename(track.get('artist', 'Unknown'))
        title = self._sanitize_filename(track.get('title', 'Unknown'))
        
        filename = f"{artist} - {title}.mp3"
        return os.path.join(self.usb_path, "Music", filename).replace("\\", "/")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility"""
        
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        return filename[:50].strip()
    
    def _prettify_xml(self, elem: ET.Element) -> str:
        """Return a pretty-printed XML string"""
        
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def create_usb_structure(self, tracks: List[Dict], playlist_name: str) -> Dict:
        """Create USB folder structure for Pioneer XDJ-RX3"""
        
        usb_structure = {
            'base_path': self.usb_path,
            'folders': {
                'PIONEER': os.path.join(self.usb_path, 'PIONEER'),
                'rekordbox': os.path.join(self.usb_path, 'PIONEER', 'rekordbox'),
                'music': os.path.join(self.usb_path, 'Music'),
                'playlists': os.path.join(self.usb_path, 'Playlists')
            },
            'files': {
                'xml': os.path.join(self.usb_path, 'PIONEER', 'rekordbox', 'rekordbox.xml'),
                'edb': os.path.join(self.usb_path, 'PIONEER', 'rekordbox', 'rekordbox.edb'),
                'anlz': os.path.join(self.usb_path, 'PIONEER', 'rekordbox', 'share.anlz')
            }
        }
        
        # Create directories
        for folder_path in usb_structure['folders'].values():
            os.makedirs(folder_path, exist_ok=True)
        
        # Generate XML file
        xml_content = self.generate_playlist_xml(tracks, playlist_name)
        
        # Copy XML to USB structure
        with open(usb_structure['files']['xml'], 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Create track list file for manual download
        self._create_track_list_file(tracks, playlist_name)
        
        return usb_structure
    
    def _create_track_list_file(self, tracks: List[Dict], playlist_name: str):
        """Create a text file with track list for manual download"""
        
        track_list_path = os.path.join(self.usb_path, f"{playlist_name}_track_list.txt")
        
        with open(track_list_path, 'w', encoding='utf-8') as f:
            f.write(f"AutoDJ Playlist: {playlist_name}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Tracks: {len(tracks)}\n")
            f.write("=" * 50 + "\n\n")
            
            for i, track in enumerate(tracks, 1):
                f.write(f"{i:2d}. {track.get('artist', 'Unknown')} - {track.get('title', 'Unknown')}\n")
                
                if track.get('bpm'):
                    f.write(f"    BPM: {track.get('bpm')}")
                if track.get('key'):
                    f.write(f" | Key: {track.get('key')}")
                if track.get('label'):
                    f.write(f" | Label: {track.get('label')}")
                f.write("\n")
                
                if track.get('beatport_url'):
                    f.write(f"    Beatport: {track.get('beatport_url')}\n")
                
                f.write("\n")
            
            f.write("\n" + "=" * 50 + "\n")
            f.write("Instructions:\n")
            f.write("1. Download tracks from Beatport or other sources\n")
            f.write("2. Name files as: 'Artist - Title.mp3'\n")
            f.write("3. Place in the 'Music' folder\n")
            f.write("4. Import rekordbox.xml into Rekordbox software\n")
            f.write("5. Sync to USB for Pioneer XDJ-RX3\n")
    
    def generate_m3u_playlist(self, tracks: List[Dict], playlist_name: str) -> str:
        """Generate M3U playlist file as alternative format"""
        
        m3u_path = os.path.join(self.usb_path, f"{playlist_name}.m3u")
        
        with open(m3u_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            f.write(f"#PLAYLIST:{playlist_name}\n")
            
            for track in tracks:
                # Extended info line
                duration = 300  # Default 5 minutes
                artist = track.get('artist', 'Unknown')
                title = track.get('title', 'Unknown')
                
                f.write(f"#EXTINF:{duration},{artist} - {title}\n")
                
                # File path
                file_path = self._get_track_file_path(track)
                f.write(f"{file_path}\n")
        
        return m3u_path
    
    def validate_xml(self, xml_path: str = None) -> Dict:
        """Validate generated XML for Rekordbox compatibility"""
        
        if not xml_path:
            xml_path = self.xml_path
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'track_count': 0,
            'playlist_count': 0
        }
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Check root element
            if root.tag != "DJ_PLAYLISTS":
                validation_result['errors'].append("Root element should be DJ_PLAYLISTS")
                validation_result['valid'] = False
            
            # Check collection
            collection = root.find("COLLECTION")
            if collection is not None:
                tracks = collection.findall("TRACK")
                validation_result['track_count'] = len(tracks)
                
                # Validate track elements
                for track in tracks:
                    if not track.get("TrackID"):
                        validation_result['warnings'].append("Track missing TrackID")
                    if not track.get("Name"):
                        validation_result['warnings'].append("Track missing Name")
                    if not track.get("Artist"):
                        validation_result['warnings'].append("Track missing Artist")
            
            # Check playlists
            playlists = root.find("PLAYLISTS")
            if playlists is not None:
                playlist_nodes = playlists.findall(".//NODE[@Type='1']")
                validation_result['playlist_count'] = len(playlist_nodes)
        
        except ET.ParseError as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"XML Parse Error: {e}")
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Validation Error: {e}")
        
        return validation_result
    
    def export_for_pioneer(self, tracks: List[Dict], playlist_name: str, description: str = "") -> Dict:
        """Complete export process for Pioneer XDJ-RX3"""
        
        # Create USB structure
        usb_structure = self.create_usb_structure(tracks, playlist_name)
        
        # Generate M3U as backup
        m3u_path = self.generate_m3u_playlist(tracks, playlist_name)
        
        # Validate XML
        validation = self.validate_xml()
        
        # Create summary
        export_summary = {
            'playlist_name': playlist_name,
            'track_count': len(tracks),
            'usb_path': self.usb_path,
            'xml_path': usb_structure['files']['xml'],
            'm3u_path': m3u_path,
            'validation': validation,
            'instructions': [
                "1. Download tracks manually from provided URLs",
                "2. Place MP3 files in the Music folder",
                "3. Copy entire USB folder to USB drive",
                "4. Insert USB into Pioneer XDJ-RX3",
                "5. Navigate to playlists on the device"
            ]
        }
        
        return export_summary
