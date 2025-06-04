# AutoDJ - AI-Powered Playlist Generator for Disco Lines Style

AutoDJ is an intelligent music discovery system that creates curated playlists inspired by DJ Disco Lines' signature tech house and disco-funk sound. The system uses AI to discover similar artists, analyze tracks, and generate Pioneer XDJ-RX3 compatible playlists.

## 🎵 What is Disco Lines Style?

DJ Disco Lines is known for:
- **Tech House** with disco/funk influences
- **BPM Range**: 120-128 (perfect for club mixing)
- **Labels**: Sony Music Entertainment, Big Beat Records, Insomniac Records, Good Good Records
- **Similar Artists**: SIDEPIECE, John Summit, Mau P, Dom Dolla, Fred Again
- **Signature Tracks**: "Baby Girl", "TECHNO + TEQUILA", "Give It To Me Good", "MDMA"

## 🚀 Features

### 🔍 **Intelligent Discovery**
- **Perplexity AI Integration**: Discovers artists similar to Disco Lines
- **Beatport Integration**: Searches labels, charts, and artist catalogs
- **Multi-source Discovery**: Reddit discussions, festival lineups, label releases

### 🧠 **AI-Powered Analysis**
- **OpenAI Track Analysis**: Evaluates style compatibility with Disco Lines
- **BPM & Key Matching**: Ensures tracks fit the 120-128 BPM sweet spot
- **Style Scoring**: Rates tracks on disco-funk tech house compatibility

### 🎵 **Full Audio Automation** ⭐ **NEW**
- **Complete Pipeline**: Discover → Download → Process → USB Export
- **Social Media Integration**: TikTok and SoundCloud audio extraction using yt-dlp
- **Beatport Automation**: Automated track purchasing (use at your own risk)
- **Audio Processing**: FFmpeg integration for format conversion and quality optimization
- **Metadata Tagging**: Automatic ID3 tag embedding with track information
- **Multi-source Downloads**: Free/legal sources + social media + commercial automation

### 🎧 **Pioneer XDJ-RX3 Ready**
- **Rekordbox XML Export**: Generate playlists compatible with Pioneer equipment
- **USB Structure**: Creates proper folder structure for XDJ-RX3
- **Audio Files Included**: Complete tracks ready for immediate DJ use
- **Metadata Rich**: Includes BPM, key, genre, and cue point information

### 📊 **Smart Curation**
- **Duplicate Removal**: Intelligent deduplication across sources
- **Quality Ranking**: Prioritizes high-compatibility tracks
- **Database Storage**: Tracks discoveries for future playlist building
- **Cache Management**: Efficient audio file caching and USB export management

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- API Keys (OpenAI, Perplexity, optional Beatport)

### Setup

1. **Clone and Setup Environment**
```bash
git clone <repository-url>
cd AutoDJ
python3.11 -m venv autodj_env
source autodj_env/bin/activate  # On Windows: autodj_env\Scripts\activate
pip install -r requirements.txt
```

2. **Configure API Keys**
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required API keys:
- `OPENAI_API_KEY`: For track analysis and style matching
- `PERPLEXITY_API_KEY`: For artist discovery and research
- `BEATPORT_API_KEY`: Optional (will use web scraping if not provided)

3. **Initialize Database**
```bash
python main.py setup
```

## 🎯 Usage

### Quick Start - Discover 25 Tracks
```bash
python main.py discover --export
```

### Custom Playlist
```bash
python main.py discover --count 30 --playlist-name "Miami Vibes 2024" --export
```

### Available Commands

#### 🔍 **Discovery**
```bash
# Discover tracks similar to Disco Lines
python main.py discover [OPTIONS]

Options:
  -c, --count INTEGER        Number of tracks to discover (default: 25)
  -n, --playlist-name TEXT   Custom playlist name
  -e, --export              Export playlist for Pioneer XDJ-RX3
```

#### 📊 **Statistics**
```bash
# View database statistics
python main.py stats
```

#### 📋 **List Tracks**
```bash
# List discovered tracks from database
python main.py list-tracks [OPTIONS]

Options:
  -s, --style-score FLOAT   Minimum style match score (default: 0.7)
```

#### 🎵 **Full Audio Automation** ⭐ **NEW**
```bash
# Complete pipeline: Discover → Download → Process → USB Export
python main.py download [OPTIONS]

Options:
  -c, --count INTEGER           Number of tracks to download (default: 25)
  -n, --playlist-name TEXT      Custom playlist name
  --social-media/--no-social-media  Include social media sources (default: True)
  --headless/--no-headless      Run browser in headless mode (default: True)

# Examples:
python main.py download --count 10                    # All sources including social media
python main.py download --no-social-media             # Traditional sources only
```

#### 📱 **Social Media Downloads** ⭐ **NEW**
```bash
# Download tracks exclusively from social media platforms
python main.py social-download [OPTIONS]

Options:
  -c, --count INTEGER           Number of tracks to download (default: 10)
  -n, --playlist-name TEXT      Custom playlist name
  -p, --platforms TEXT          Platforms to search (soundcloud, tiktok)

# Examples:
python main.py social-download --count 15 --platforms soundcloud
python main.py social-download --platforms tiktok --platforms soundcloud
```

#### 🔗 **Direct URL Downloads**
```bash
# Download audio from a specific TikTok or SoundCloud URL
python main.py download-url [URL] [OPTIONS]

Options:
  -a, --artist TEXT             Artist name (required)
  -t, --title TEXT              Track title (required)

# Examples:
python main.py download-url "https://soundcloud.com/artist/track" -a "Artist" -t "Track Title"
python main.py download-url "https://tiktok.com/@user/video/123" -a "Artist" -t "Track Title"
```

#### 📊 **Audio Status & Management**
```bash
# Check audio automation status and dependencies
python main.py audio-status

# Clear all cached audio files and USB exports
python main.py clear-cache
```

#### ⚙️ **Setup**
```bash
# Check API key configuration
python main.py setup
```

## 📁 Project Structure

```
AutoDJ/
├── main.py                 # CLI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── config/
│   └── settings.py        # Configuration and Disco Lines reference data
├── src/
│   ├── database.py        # SQLite database management
│   ├── discovery/
│   │   └── perplexity_client.py    # Artist discovery via Perplexity
│   ├── intelligence/
│   │   └── openai_processor.py     # Track analysis via OpenAI
│   ├── beatport/
│   │   └── api_client.py           # Beatport integration
│   └── export/
│       └── rekordbox_xml.py        # Pioneer XDJ-RX3 export
└── data/                  # Generated data and exports
    ├── tracks.db          # SQLite database
    ├── cache/             # Audio cache directory
    └── usb_export/        # Pioneer USB structure
```

## 🎛️ Pioneer XDJ-RX3 Integration

AutoDJ generates complete USB-ready exports:

### Generated Files
- **`rekordbox.xml`**: Main playlist file for Pioneer equipment
- **`playlist_name.m3u`**: Standard M3U playlist backup
- **`track_list.txt`**: Human-readable track list with download links

### USB Structure
```
USB_Drive/
├── PIONEER/
│   └── rekordbox/
│       ├── rekordbox.xml
│       └── rekordbox.edb
├── Music/
│   └── [Your downloaded MP3 files]
└── Playlists/
    └── [Generated playlists]
```

### Usage Instructions
1. Run AutoDJ discovery with `--export` flag
2. Download tracks manually from provided Beatport links
3. Place MP3 files in the `Music` folder
4. Copy entire USB structure to USB drive
5. Insert into Pioneer XDJ-RX3 and enjoy!

## 🔧 Configuration

### Disco Lines Style Parameters
Located in `config/settings.py`:

```python
DISCO_LINES_STYLE = {
    'genres': ['tech house', 'house', 'disco house', 'funky house'],
    'bpm_range': (120, 128),
    'energy_level': 'high',
    'similar_artists': ['SIDEPIECE', 'John Summit', 'Mau P', ...],
    'labels': ['Sony Music Entertainment', 'Big Beat Records', ...],
    'reference_tracks': ['Baby Girl', 'TECHNO + TEQUILA', ...]
}
```

### Customization
- Modify `DISCO_LINES_STYLE` to target different artists or styles
- Adjust BPM ranges for different mixing preferences
- Add new labels or similar artists as the scene evolves

## 🤖 AI Components

### Perplexity Discovery
- Searches for artists similar to Disco Lines
- Analyzes Reddit discussions and music forums
- Discovers festival lineups and label rosters
- Finds collaboration networks

### OpenAI Analysis
- Evaluates track compatibility with Disco Lines style
- Extracts track information from unstructured text
- Generates engaging playlist descriptions
- Classifies artist styles and genres

### Beatport Integration
- Searches official track catalogs
- Retrieves metadata (BPM, key, genre, label)
- Accesses current charts and trending tracks
- Provides purchase links for legal downloads

## 📊 Database Schema

### Tracks Table
- Track metadata (title, artist, BPM, key, genre)
- Style compatibility scores
- Beatport integration data
- Discovery source tracking

### Artists Table
- Artist information and style classification
- Label associations and social links
- Similarity scores to Disco Lines

### Playlists Table
- Generated playlist metadata
- Track associations and statistics
- Export history and formats

## 🔍 Discovery Algorithm

1. **Multi-Source Search**
   - Perplexity: Artist discovery and trend analysis
   - Beatport: Official catalog and chart data
   - Label Focus: Releases from Disco Lines' associated labels

2. **Style Analysis**
   - BPM compatibility (120-128 preferred)
   - Genre matching (tech house, disco house)
   - Label association scoring
   - Artist similarity evaluation

3. **Quality Ranking**
   - Style match score (0.0-1.0)
   - Popularity and chart performance
   - Release recency weighting
   - Duplicate detection and removal

4. **Curation**
   - Top-ranked tracks selection
   - BPM flow optimization
   - Key compatibility consideration
   - Final playlist balancing

## 🚨 Limitations & Notes

### API Dependencies
- Requires active OpenAI and Perplexity API keys
- Beatport API access is optional but recommended
- Rate limiting applies to all external services

### Legal Considerations
- AutoDJ discovers and catalogs tracks but does not download audio
- Users must purchase tracks legally from Beatport or other sources
- Generated playlists are for personal DJ use

### Technical Limitations
- Web scraping may break if Beatport changes their HTML structure
- AI analysis quality depends on available track metadata
- Pioneer compatibility tested with XDJ-RX3 (should work with other models)

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Format code
black src/ main.py
```

### Adding New Features
- **New Discovery Sources**: Add modules in `src/discovery/`
- **Additional AI Providers**: Extend `src/intelligence/`
- **Export Formats**: Add exporters in `src/export/`
- **Style Profiles**: Modify `config/settings.py`

## 📝 License

This project is for educational and personal use. Respect music licensing and purchase tracks legally.

## 🎧 Example Output

```
🎵 Discovered Tracks
┏━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━┳━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━┓
┃ # ┃ Artist             ┃ Title                   ┃ BPM ┃ Key ┃ Label         ┃ Score┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━╇━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━┩
│ 1 │ SIDEPIECE          │ Give It To Me Good      │ 124 │ Am  │ Big Beat      │ 0.95 │
│ 2 │ John Summit        │ La Danza               │ 126 │ Fm  │ Insomniac     │ 0.92 │
│ 3 │ Mau P              │ Drugs From Amsterdam   │ 125 │ Gm  │ Insomniac     │ 0.89 │
│ 4 │ Dom Dolla          │ San Frandisco          │ 123 │ Am  │ Sweat It Out  │ 0.87 │
│ 5 │ Fred Again         │ Rumble                 │ 127 │ Cm  │ Atlantic      │ 0.85 │
└───┴────────────────────┴─────────────────────────┴─────┴─────┴───────────────┴──────┘

✅ Playlist created successfully!
📁 USB Export Path: data/usb_export
📄 Track List: data/usb_export/Disco Lines Style - 25 Tracks_track_list.txt

📋 Next Steps
1. Download tracks manually from provided URLs
2. Place MP3 files in the Music folder  
3. Copy entire USB folder to USB drive
4. Insert USB into Pioneer XDJ-RX3
5. Navigate to playlists on the device
```

---

**Ready to discover your next favorite tech house tracks? Start with `python main.py discover --export` and let AutoDJ curate the perfect Disco Lines-inspired playlist for your next set! 🎧**
