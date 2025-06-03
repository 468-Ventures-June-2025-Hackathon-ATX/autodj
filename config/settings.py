"""
Configuration settings for AutoDJ
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
BEATPORT_API_KEY = os.getenv('BEATPORT_API_KEY')

# Reddit API
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'AutoDJ:v1.0 (by /u/autodj_bot)')

# Disco Lines Reference Data
DISCO_LINES_STYLE = {
    'genres': ['tech house', 'house', 'disco house', 'funky house'],
    'bpm_range': (120, 128),
    'key_preferences': ['A minor', 'F major', 'C major', 'G major', 'D minor'],
    'energy_level': 'high',
    'labels': [
        'Sony Music Entertainment',
        'Big Beat Records', 
        'Insomniac Records',
        'Good Good Records',
        'DistroKid',
        'UMe Direct 2',
        'Fantastic Trax',
        'TH3RD BRAIN',
        'Boom Records LLC'
    ],
    'similar_artists': [
        'SIDEPIECE',
        'John Summit',
        'Mau P',
        'Dom Dolla',
        'Fred Again',
        'Justin Jay',
        'GUDFELLA',
        'INJI'
    ],
    'reference_tracks': [
        'Baby Girl',
        'TECHNO + TEQUILA',
        'Give It To Me Good',
        'MDMA',
        'Disco Boy',
        'Is This Love',
        'Another Chance'
    ]
}

# Database
DATABASE_PATH = 'data/tracks.db'

# Audio Processing
AUDIO_CACHE_DIR = 'data/cache'
SUPPORTED_FORMATS = ['.mp3', '.wav', '.flac', '.m4a']
TARGET_BITRATE = 320  # kbps
TARGET_SAMPLE_RATE = 44100  # Hz

# Export Settings
REKORDBOX_XML_PATH = 'data/rekordbox_export.xml'
USB_EXPORT_PATH = 'data/usb_export'

# Search Settings
MAX_TRACKS_PER_SEARCH = 50
MIN_TRACK_POPULARITY = 0.3  # 0-1 scale
TRACK_RECENCY_WEIGHT = 0.7  # Prefer newer tracks

# Rate Limiting
API_RATE_LIMIT = 1.0  # seconds between API calls
REDDIT_RATE_LIMIT = 2.0  # seconds between Reddit requests
