#!/usr/bin/env python3
"""
AutoDJ Demo - Test the basic functionality without API keys
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import TrackDatabase
from beatport.api_client import BeatportClient
from export.rekordbox_xml import RekordboxXMLGenerator

def demo_basic_functionality():
    """Demo basic functionality without API dependencies"""
    
    print("🎧 AutoDJ Demo - Testing Basic Functionality")
    print("=" * 50)
    
    # Test database initialization
    print("\n1. Testing Database...")
    db = TrackDatabase()
    print("✅ Database initialized successfully")
    
    # Add comprehensive sample tracks (50+ tracks)
    sample_tracks = [
        # Disco Lines originals
        {
            'title': 'Baby Girl',
            'artist': 'Disco Lines',
            'bpm': 124,
            'key': 'A minor',
            'genre': 'Tech House',
            'label': 'Sony Music Entertainment',
            'style_match_score': 1.0,
            'popularity_score': 0.95,
            'discovered_from': 'demo'
        },
        {
            'title': 'TECHNO + TEQUILA',
            'artist': 'Disco Lines',
            'bpm': 125,
            'key': 'F major',
            'genre': 'Tech House',
            'label': 'DistroKid',
            'style_match_score': 1.0,
            'popularity_score': 0.92,
            'discovered_from': 'demo'
        },
        {
            'title': 'MDMA',
            'artist': 'Disco Lines',
            'bpm': 123,
            'key': 'C major',
            'genre': 'Tech House',
            'label': 'Good Good Records',
            'style_match_score': 1.0,
            'popularity_score': 0.89,
            'discovered_from': 'demo'
        },
        {
            'title': 'Disco Boy',
            'artist': 'Disco Lines',
            'bpm': 126,
            'key': 'G major',
            'genre': 'Tech House',
            'label': 'DistroKid',
            'style_match_score': 1.0,
            'popularity_score': 0.87,
            'discovered_from': 'demo'
        },
        {
            'title': 'Is This Love',
            'artist': 'Disco Lines',
            'bpm': 122,
            'key': 'D minor',
            'genre': 'Tech House',
            'label': 'DistroKid',
            'style_match_score': 1.0,
            'popularity_score': 0.85,
            'discovered_from': 'demo'
        },
        
        # SIDEPIECE tracks
        {
            'title': 'Give It To Me Good',
            'artist': 'SIDEPIECE',
            'bpm': 125,
            'key': 'F major',
            'genre': 'Tech House',
            'label': 'Big Beat Records',
            'style_match_score': 0.98,
            'popularity_score': 0.94,
            'discovered_from': 'demo'
        },
        {
            'title': 'On My Mind',
            'artist': 'SIDEPIECE',
            'bpm': 124,
            'key': 'A minor',
            'genre': 'Tech House',
            'label': 'Big Beat Records',
            'style_match_score': 0.96,
            'popularity_score': 0.91,
            'discovered_from': 'demo'
        },
        {
            'title': 'Temptation',
            'artist': 'SIDEPIECE',
            'bpm': 126,
            'key': 'G minor',
            'genre': 'Tech House',
            'label': 'Big Beat Records',
            'style_match_score': 0.95,
            'popularity_score': 0.88,
            'discovered_from': 'demo'
        },
        
        # John Summit tracks
        {
            'title': 'La Danza',
            'artist': 'John Summit',
            'bpm': 126,
            'key': 'G minor',
            'genre': 'Tech House',
            'label': 'Insomniac Records',
            'style_match_score': 0.94,
            'popularity_score': 0.93,
            'discovered_from': 'demo'
        },
        {
            'title': 'Deep End',
            'artist': 'John Summit',
            'bpm': 125,
            'key': 'F major',
            'genre': 'Tech House',
            'label': 'Insomniac Records',
            'style_match_score': 0.92,
            'popularity_score': 0.90,
            'discovered_from': 'demo'
        },
        {
            'title': 'Human',
            'artist': 'John Summit',
            'bpm': 124,
            'key': 'A minor',
            'genre': 'Tech House',
            'label': 'Insomniac Records',
            'style_match_score': 0.91,
            'popularity_score': 0.89,
            'discovered_from': 'demo'
        },
        {
            'title': 'Beauty Sleep',
            'artist': 'John Summit',
            'bpm': 127,
            'key': 'C major',
            'genre': 'Tech House',
            'label': 'Insomniac Records',
            'style_match_score': 0.90,
            'popularity_score': 0.86,
            'discovered_from': 'demo'
        },
        
        # Mau P tracks
        {
            'title': 'Drugs From Amsterdam',
            'artist': 'Mau P',
            'bpm': 125,
            'key': 'G minor',
            'genre': 'Tech House',
            'label': 'Insomniac Records',
            'style_match_score': 0.93,
            'popularity_score': 0.92,
            'discovered_from': 'demo'
        },
        {
            'title': 'Your Mind',
            'artist': 'Mau P',
            'bpm': 124,
            'key': 'F major',
            'genre': 'Tech House',
            'label': 'Insomniac Records',
            'style_match_score': 0.91,
            'popularity_score': 0.88,
            'discovered_from': 'demo'
        },
        {
            'title': 'Beats For The Underground',
            'artist': 'Mau P',
            'bpm': 126,
            'key': 'A minor',
            'genre': 'Tech House',
            'label': 'Insomniac Records',
            'style_match_score': 0.89,
            'popularity_score': 0.85,
            'discovered_from': 'demo'
        },
        
        # Dom Dolla tracks
        {
            'title': 'San Frandisco',
            'artist': 'Dom Dolla',
            'bpm': 123,
            'key': 'A minor',
            'genre': 'Tech House',
            'label': 'Sweat It Out',
            'style_match_score': 0.92,
            'popularity_score': 0.91,
            'discovered_from': 'demo'
        },
        {
            'title': 'Take It',
            'artist': 'Dom Dolla',
            'bpm': 125,
            'key': 'F major',
            'genre': 'Tech House',
            'label': 'Sweat It Out',
            'style_match_score': 0.90,
            'popularity_score': 0.87,
            'discovered_from': 'demo'
        },
        {
            'title': 'Pump The Brakes',
            'artist': 'Dom Dolla',
            'bpm': 124,
            'key': 'G major',
            'genre': 'Tech House',
            'label': 'Sweat It Out',
            'style_match_score': 0.88,
            'popularity_score': 0.84,
            'discovered_from': 'demo'
        },
        
        # Fred Again tracks
        {
            'title': 'Rumble',
            'artist': 'Fred Again',
            'bpm': 127,
            'key': 'C major',
            'genre': 'UK Garage',
            'label': 'Atlantic Records',
            'style_match_score': 0.85,
            'popularity_score': 0.93,
            'discovered_from': 'demo'
        },
        {
            'title': 'Turn On The Lights',
            'artist': 'Fred Again',
            'bpm': 126,
            'key': 'D minor',
            'genre': 'UK Garage',
            'label': 'Atlantic Records',
            'style_match_score': 0.83,
            'popularity_score': 0.90,
            'discovered_from': 'demo'
        },
        
        # GUDFELLA tracks
        {
            'title': 'Sunny',
            'artist': 'GUDFELLA',
            'bpm': 124,
            'key': 'F major',
            'genre': 'Tech House',
            'label': 'Good Good Records',
            'style_match_score': 0.89,
            'popularity_score': 0.82,
            'discovered_from': 'demo'
        },
        {
            'title': 'Feel Good',
            'artist': 'GUDFELLA',
            'bpm': 125,
            'key': 'A minor',
            'genre': 'Tech House',
            'label': 'Good Good Records',
            'style_match_score': 0.87,
            'popularity_score': 0.80,
            'discovered_from': 'demo'
        },
        
        # INJI tracks
        {
            'title': 'GASLIGHT',
            'artist': 'INJI',
            'bpm': 123,
            'key': 'G minor',
            'genre': 'Tech House',
            'label': 'DistroKid',
            'style_match_score': 0.86,
            'popularity_score': 0.81,
            'discovered_from': 'demo'
        },
        
        # Additional tech house artists
        {
            'title': 'Losing It',
            'artist': 'Fisher',
            'bpm': 128,
            'key': 'F major',
            'genre': 'Tech House',
            'label': 'Catch & Release',
            'style_match_score': 0.88,
            'popularity_score': 0.95,
            'discovered_from': 'demo'
        },
        {
            'title': 'You Little Beauty',
            'artist': 'Fisher',
            'bpm': 127,
            'key': 'A minor',
            'genre': 'Tech House',
            'label': 'Catch & Release',
            'style_match_score': 0.86,
            'popularity_score': 0.92,
            'discovered_from': 'demo'
        },
        {
            'title': 'Stop It',
            'artist': 'Fisher',
            'bpm': 126,
            'key': 'G major',
            'genre': 'Tech House',
            'label': 'Catch & Release',
            'style_match_score': 0.85,
            'popularity_score': 0.89,
            'discovered_from': 'demo'
        },
        {
            'title': 'Freaks',
            'artist': 'Timmy Trumpet & Savage',
            'bpm': 125,
            'key': 'C major',
            'genre': 'Tech House',
            'label': 'Spinnin Records',
            'style_match_score': 0.82,
            'popularity_score': 0.88,
            'discovered_from': 'demo'
        },
        {
            'title': 'Satisfaction',
            'artist': 'Benny Benassi',
            'bpm': 124,
            'key': 'D minor',
            'genre': 'Electro House',
            'label': 'Ultra Records',
            'style_match_score': 0.80,
            'popularity_score': 0.85,
            'discovered_from': 'demo'
        },
        {
            'title': 'Gecko',
            'artist': 'Oliver Heldens',
            'bpm': 126,
            'key': 'F major',
            'genre': 'Deep House',
            'label': 'Heldeep Records',
            'style_match_score': 0.84,
            'popularity_score': 0.87,
            'discovered_from': 'demo'
        },
        {
            'title': 'Koala',
            'artist': 'Oliver Heldens',
            'bpm': 125,
            'key': 'A minor',
            'genre': 'Deep House',
            'label': 'Heldeep Records',
            'style_match_score': 0.83,
            'popularity_score': 0.84,
            'discovered_from': 'demo'
        },
        {
            'title': 'Mammoth',
            'artist': 'Dimitri Vegas & Like Mike',
            'bpm': 127,
            'key': 'G minor',
            'genre': 'Big Room House',
            'label': 'Smash The House',
            'style_match_score': 0.78,
            'popularity_score': 0.90,
            'discovered_from': 'demo'
        },
        {
            'title': 'Tremor',
            'artist': 'Dimitri Vegas & Like Mike',
            'bpm': 128,
            'key': 'C major',
            'genre': 'Big Room House',
            'label': 'Smash The House',
            'style_match_score': 0.76,
            'popularity_score': 0.88,
            'discovered_from': 'demo'
        },
        {
            'title': 'Clarity',
            'artist': 'Zedd',
            'bpm': 123,
            'key': 'F major',
            'genre': 'Progressive House',
            'label': 'Interscope Records',
            'style_match_score': 0.75,
            'popularity_score': 0.92,
            'discovered_from': 'demo'
        },
        {
            'title': 'Stay',
            'artist': 'Zedd',
            'bpm': 124,
            'key': 'A minor',
            'genre': 'Progressive House',
            'label': 'Interscope Records',
            'style_match_score': 0.74,
            'popularity_score': 0.89,
            'discovered_from': 'demo'
        },
        
        # More tech house gems
        {
            'title': 'Pjanoo',
            'artist': 'Eric Prydz',
            'bpm': 126,
            'key': 'D minor',
            'genre': 'Progressive House',
            'label': 'Pryda Recordings',
            'style_match_score': 0.81,
            'popularity_score': 0.91,
            'discovered_from': 'demo'
        },
        {
            'title': 'Call On Me',
            'artist': 'Eric Prydz',
            'bpm': 125,
            'key': 'G major',
            'genre': 'Progressive House',
            'label': 'Pryda Recordings',
            'style_match_score': 0.79,
            'popularity_score': 0.88,
            'discovered_from': 'demo'
        },
        {
            'title': 'One More Time',
            'artist': 'Daft Punk',
            'bpm': 123,
            'key': 'F major',
            'genre': 'French House',
            'label': 'Virgin Records',
            'style_match_score': 0.87,
            'popularity_score': 0.96,
            'discovered_from': 'demo'
        },
        {
            'title': 'Around The World',
            'artist': 'Daft Punk',
            'bpm': 121,
            'key': 'A minor',
            'genre': 'French House',
            'label': 'Virgin Records',
            'style_match_score': 0.85,
            'popularity_score': 0.94,
            'discovered_from': 'demo'
        },
        {
            'title': 'Get Lucky',
            'artist': 'Daft Punk',
            'bpm': 116,
            'key': 'C major',
            'genre': 'Disco House',
            'label': 'Columbia Records',
            'style_match_score': 0.90,
            'popularity_score': 0.97,
            'discovered_from': 'demo'
        },
        {
            'title': 'Instant Crush',
            'artist': 'Daft Punk',
            'bpm': 118,
            'key': 'G minor',
            'genre': 'Disco House',
            'label': 'Columbia Records',
            'style_match_score': 0.88,
            'popularity_score': 0.93,
            'discovered_from': 'demo'
        },
        
        # Modern disco house
        {
            'title': 'Firestone',
            'artist': 'Kygo',
            'bpm': 122,
            'key': 'D minor',
            'genre': 'Tropical House',
            'label': 'Ultra Records',
            'style_match_score': 0.72,
            'popularity_score': 0.91,
            'discovered_from': 'demo'
        },
        {
            'title': 'Stole The Show',
            'artist': 'Kygo',
            'bpm': 120,
            'key': 'F major',
            'genre': 'Tropical House',
            'label': 'Ultra Records',
            'style_match_score': 0.70,
            'popularity_score': 0.88,
            'discovered_from': 'demo'
        },
        {
            'title': 'Lean On',
            'artist': 'Major Lazer',
            'bpm': 98,
            'key': 'A minor',
            'genre': 'Moombahton',
            'label': 'Mad Decent',
            'style_match_score': 0.65,
            'popularity_score': 0.95,
            'discovered_from': 'demo'
        },
        {
            'title': 'Cold Water',
            'artist': 'Major Lazer',
            'bpm': 100,
            'key': 'G major',
            'genre': 'Tropical House',
            'label': 'Mad Decent',
            'style_match_score': 0.63,
            'popularity_score': 0.92,
            'discovered_from': 'demo'
        },
        
        # Underground tech house
        {
            'title': 'Cola',
            'artist': 'CamelPhat',
            'bpm': 124,
            'key': 'F major',
            'genre': 'Tech House',
            'label': 'Defected Records',
            'style_match_score': 0.89,
            'popularity_score': 0.86,
            'discovered_from': 'demo'
        },
        {
            'title': 'Panic Room',
            'artist': 'CamelPhat',
            'bpm': 125,
            'key': 'A minor',
            'genre': 'Tech House',
            'label': 'Defected Records',
            'style_match_score': 0.87,
            'popularity_score': 0.83,
            'discovered_from': 'demo'
        },
        {
            'title': 'Be Someone',
            'artist': 'CamelPhat',
            'bpm': 126,
            'key': 'G minor',
            'genre': 'Tech House',
            'label': 'Defected Records',
            'style_match_score': 0.85,
            'popularity_score': 0.81,
            'discovered_from': 'demo'
        },
        {
            'title': 'Hypercolour',
            'artist': 'CamelPhat',
            'bpm': 127,
            'key': 'C major',
            'genre': 'Tech House',
            'label': 'Defected Records',
            'style_match_score': 0.84,
            'popularity_score': 0.79,
            'discovered_from': 'demo'
        },
        
        # Glitterbox style
        {
            'title': 'Body Funk',
            'artist': 'Purple Disco Machine',
            'bpm': 122,
            'key': 'D minor',
            'genre': 'Disco House',
            'label': 'Glitterbox Recordings',
            'style_match_score': 0.91,
            'popularity_score': 0.87,
            'discovered_from': 'demo'
        },
        {
            'title': 'Hypnotized',
            'artist': 'Purple Disco Machine',
            'bpm': 123,
            'key': 'F major',
            'genre': 'Disco House',
            'label': 'Glitterbox Recordings',
            'style_match_score': 0.90,
            'popularity_score': 0.85,
            'discovered_from': 'demo'
        },
        {
            'title': 'Fireworks',
            'artist': 'Purple Disco Machine',
            'bpm': 124,
            'key': 'A minor',
            'genre': 'Disco House',
            'label': 'Glitterbox Recordings',
            'style_match_score': 0.88,
            'popularity_score': 0.82,
            'discovered_from': 'demo'
        },
        
        # Classic house influences
        {
            'title': 'Your Love',
            'artist': 'Frankie Knuckles',
            'bpm': 120,
            'key': 'G major',
            'genre': 'Classic House',
            'label': 'Trax Records',
            'style_match_score': 0.83,
            'popularity_score': 0.78,
            'discovered_from': 'demo'
        },
        {
            'title': 'Can U Party',
            'artist': 'Royal House',
            'bpm': 121,
            'key': 'C major',
            'genre': 'Classic House',
            'label': 'Idlers Records',
            'style_match_score': 0.81,
            'popularity_score': 0.75,
            'discovered_from': 'demo'
        },
        
        # Modern underground
        {
            'title': 'Rave',
            'artist': 'ARTBAT',
            'bpm': 125,
            'key': 'D minor',
            'genre': 'Melodic Techno',
            'label': 'Diynamic',
            'style_match_score': 0.77,
            'popularity_score': 0.84,
            'discovered_from': 'demo'
        },
        {
            'title': 'Best Of Me',
            'artist': 'ARTBAT',
            'bpm': 126,
            'key': 'F major',
            'genre': 'Melodic Techno',
            'label': 'Diynamic',
            'style_match_score': 0.75,
            'popularity_score': 0.82,
            'discovered_from': 'demo'
        },
        
        # Festival bangers
        {
            'title': 'Levels',
            'artist': 'Avicii',
            'bpm': 126,
            'key': 'A minor',
            'genre': 'Progressive House',
            'label': 'LE7ELS',
            'style_match_score': 0.78,
            'popularity_score': 0.96,
            'discovered_from': 'demo'
        },
        {
            'title': 'Wake Me Up',
            'artist': 'Avicii',
            'bpm': 124,
            'key': 'G major',
            'genre': 'Progressive House',
            'label': 'PRMD Music',
            'style_match_score': 0.76,
            'popularity_score': 0.94,
            'discovered_from': 'demo'
        }
    ]
    
    print("\n2. Adding Sample Tracks...")
    track_ids = []
    for track in sample_tracks:
        track_id = db.add_track(track)
        track_ids.append(track_id)
        print(f"   ✅ Added: {track['artist']} - {track['title']}")
    
    # Test Beatport client (without API)
    print("\n3. Testing Beatport Client...")
    beatport = BeatportClient()
    print("✅ Beatport client initialized")
    
    # Test style matching
    for track in sample_tracks:
        score = beatport.calculate_style_match_score(track)
        print(f"   Style score for {track['title']}: {score:.2f}")
    
    # Test XML export
    print("\n4. Testing Rekordbox XML Export...")
    exporter = RekordboxXMLGenerator()
    
    playlist_name = "AutoDJ Demo Playlist"
    export_summary = exporter.export_for_pioneer(sample_tracks, playlist_name)
    
    print(f"✅ Exported playlist: {playlist_name}")
    print(f"   📁 USB Path: {export_summary['usb_path']}")
    print(f"   📄 XML Path: {export_summary['xml_path']}")
    print(f"   📋 Track Count: {export_summary['track_count']}")
    
    # Validate XML
    validation = exporter.validate_xml()
    if validation['valid']:
        print("✅ XML validation passed")
    else:
        print("❌ XML validation failed:")
        for error in validation['errors']:
            print(f"   - {error}")
    
    # Test database stats
    print("\n5. Testing Database Stats...")
    stats = db.get_stats()
    print(f"   📊 Total Tracks: {stats['total_tracks']}")
    print(f"   📊 High Quality Tracks: {stats['high_quality_tracks']}")
    
    # Test playlist creation
    print("\n6. Testing Playlist Creation...")
    playlist_id = db.create_playlist(playlist_name, track_ids, "Demo playlist for testing AutoDJ functionality")
    print(f"✅ Created playlist with ID: {playlist_id}")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")
    print("\nNext steps:")
    print("1. Add your API keys to .env file")
    print("2. Run: python main.py discover --export")
    print("3. Check the generated files in data/usb_export/")

if __name__ == "__main__":
    demo_basic_functionality()
