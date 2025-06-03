"""
AutoDJ - Main CLI application for discovering and creating Disco Lines style playlists
"""
import click
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import TrackDatabase
from discovery.perplexity_client import PerplexityClient
from intelligence.openai_processor import OpenAIProcessor
from beatport.api_client import BeatportClient
from export.rekordbox_xml import RekordboxXMLGenerator
from config.settings import DISCO_LINES_STYLE

console = Console()

class AutoDJ:
    def __init__(self):
        self.db = TrackDatabase()
        self.perplexity = PerplexityClient()
        self.openai = OpenAIProcessor()
        self.beatport = BeatportClient()
        self.exporter = RekordboxXMLGenerator()
    
    def discover_tracks(self, target_count: int = 25) -> list:
        """Main discovery workflow"""
        
        discovered_tracks = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Step 1: Discover similar artists
            task1 = progress.add_task("🔍 Discovering artists similar to Disco Lines...", total=None)
            artists = self.perplexity.search_similar_artists(limit=15)
            progress.update(task1, description=f"✅ Found {len(artists)} similar artists")
            
            # Step 2: Search label releases
            task2 = progress.add_task("🏷️  Searching label releases...", total=None)
            label_tracks = []
            for label in DISCO_LINES_STYLE['labels'][:3]:  # Top 3 labels
                tracks = self.beatport.search_label_releases(label, limit=10)
                label_tracks.extend(tracks)
            progress.update(task2, description=f"✅ Found {len(label_tracks)} label tracks")
            
            # Step 3: Get tech house charts
            task3 = progress.add_task("📈 Getting tech house charts...", total=None)
            chart_tracks = self.beatport.get_genre_charts("tech-house", limit=15)
            progress.update(task3, description=f"✅ Found {len(chart_tracks)} chart tracks")
            
            # Step 4: Search for similar artist tracks
            task4 = progress.add_task("🎵 Searching artist tracks...", total=None)
            artist_tracks = []
            for artist in DISCO_LINES_STYLE['similar_artists'][:5]:
                tracks = self.beatport.search_artist_tracks(artist, limit=8)
                artist_tracks.extend(tracks)
            progress.update(task4, description=f"✅ Found {len(artist_tracks)} artist tracks")
            
            # Combine all tracks
            all_tracks = label_tracks + chart_tracks + artist_tracks
            
            # Step 5: Analyze and score tracks
            task5 = progress.add_task("🧠 Analyzing track compatibility...", total=len(all_tracks))
            
            for i, track in enumerate(all_tracks):
                # Calculate style match score
                style_score = self.beatport.calculate_style_match_score(track)
                track['style_match_score'] = style_score
                
                # Enrich with additional metadata if needed
                if not track.get('bpm') or not track.get('key'):
                    track = self.beatport.enrich_track_metadata(track)
                
                # Add to database
                track_id = self.db.add_track(track)
                track['db_id'] = track_id
                
                discovered_tracks.append(track)
                progress.update(task5, advance=1)
            
            progress.update(task5, description=f"✅ Analyzed {len(discovered_tracks)} tracks")
        
        # Filter and rank tracks
        filtered_tracks = self._filter_and_rank_tracks(discovered_tracks, target_count)
        
        return filtered_tracks
    
    def _filter_and_rank_tracks(self, tracks: list, target_count: int) -> list:
        """Filter and rank tracks based on Disco Lines style compatibility"""
        
        # Remove duplicates
        unique_tracks = {}
        for track in tracks:
            key = f"{track.get('artist', '').lower()}_{track.get('title', '').lower()}"
            if key not in unique_tracks or track.get('style_match_score', 0) > unique_tracks[key].get('style_match_score', 0):
                unique_tracks[key] = track
        
        tracks = list(unique_tracks.values())
        
        # Filter by BPM range
        bpm_filtered = []
        for track in tracks:
            bpm = track.get('bpm', 0)
            if bpm and DISCO_LINES_STYLE['bpm_range'][0] <= bpm <= DISCO_LINES_STYLE['bpm_range'][1]:
                bpm_filtered.append(track)
            elif bpm and 115 <= bpm <= 135:  # Broader range
                track['style_match_score'] = track.get('style_match_score', 0) * 0.8  # Reduce score
                bpm_filtered.append(track)
        
        # Sort by style match score and popularity
        bpm_filtered.sort(key=lambda x: (
            x.get('style_match_score', 0),
            x.get('popularity_score', 0)
        ), reverse=True)
        
        return bpm_filtered[:target_count]
    
    def create_playlist(self, tracks: list, name: str = None) -> dict:
        """Create a playlist from discovered tracks"""
        
        if not name:
            name = f"Disco Lines Style - {len(tracks)} Tracks"
        
        # Generate description
        description = self.openai.generate_playlist_description(tracks, name)
        
        # Create playlist in database
        track_ids = [track.get('db_id') for track in tracks if track.get('db_id')]
        playlist_id = self.db.create_playlist(name, track_ids, description)
        
        # Export for Pioneer
        export_summary = self.exporter.export_for_pioneer(tracks, name, description)
        
        return {
            'playlist_id': playlist_id,
            'name': name,
            'description': description,
            'tracks': tracks,
            'export_summary': export_summary
        }
    
    def display_tracks(self, tracks: list):
        """Display tracks in a formatted table"""
        
        table = Table(title="🎵 Discovered Tracks")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Artist", style="green", width=20)
        table.add_column("Title", style="yellow", width=25)
        table.add_column("BPM", style="blue", width=5)
        table.add_column("Key", style="magenta", width=5)
        table.add_column("Label", style="white", width=15)
        table.add_column("Score", style="red", width=6)
        
        for i, track in enumerate(tracks, 1):
            score = track.get('style_match_score', 0)
            score_color = "green" if score > 0.7 else "yellow" if score > 0.5 else "red"
            
            table.add_row(
                str(i),
                track.get('artist', 'Unknown')[:18],
                track.get('title', 'Unknown')[:23],
                str(track.get('bpm', '?')),
                track.get('key', '?'),
                track.get('label', 'Unknown')[:13],
                f"[{score_color}]{score:.2f}[/{score_color}]"
            )
        
        console.print(table)
    
    def display_stats(self):
        """Display database statistics"""
        
        stats = self.db.get_stats()
        
        stats_table = Table(title="📊 AutoDJ Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Total Tracks", str(stats['total_tracks']))
        stats_table.add_row("Total Artists", str(stats['total_artists']))
        stats_table.add_row("Total Playlists", str(stats['total_playlists']))
        stats_table.add_row("High Quality Tracks", str(stats['high_quality_tracks']))
        stats_table.add_row("Recent Discoveries", str(stats['recent_discoveries']))
        
        console.print(stats_table)

@click.group()
def cli():
    """🎧 AutoDJ - AI-powered playlist generator for Disco Lines style music"""
    pass

@cli.command()
@click.option('--count', '-c', default=25, help='Number of tracks to discover')
@click.option('--playlist-name', '-n', help='Custom playlist name')
@click.option('--export', '-e', is_flag=True, help='Export playlist for Pioneer XDJ-RX3')
def discover(count, playlist_name, export):
    """🔍 Discover tracks similar to Disco Lines style"""
    
    console.print(Panel.fit(
        "[bold green]AutoDJ - Disco Lines Style Discovery[/bold green]\n"
        f"Target: {count} tracks\n"
        "Style: Tech House with Disco/Funk influences",
        title="🎧 Starting Discovery"
    ))
    
    autodj = AutoDJ()
    
    try:
        # Discover tracks
        tracks = autodj.discover_tracks(count)
        
        if not tracks:
            console.print("[red]❌ No tracks discovered. Check your API keys and try again.[/red]")
            return
        
        # Display results
        console.print(f"\n[green]✅ Discovered {len(tracks)} tracks![/green]")
        autodj.display_tracks(tracks)
        
        # Create playlist if requested
        if export or playlist_name:
            name = playlist_name or f"Disco Lines Style - {len(tracks)} Tracks"
            
            console.print(f"\n[yellow]📝 Creating playlist: {name}[/yellow]")
            playlist = autodj.create_playlist(tracks, name)
            
            console.print(f"\n[green]✅ Playlist created successfully![/green]")
            console.print(f"📁 USB Export Path: {playlist['export_summary']['usb_path']}")
            console.print(f"📄 Track List: {playlist['export_summary']['usb_path']}/{name}_track_list.txt")
            
            # Display instructions
            console.print(Panel(
                "\n".join(playlist['export_summary']['instructions']),
                title="📋 Next Steps",
                border_style="blue"
            ))
    
    except Exception as e:
        console.print(f"[red]❌ Error during discovery: {e}[/red]")
        console.print("[yellow]💡 Make sure you have set up your API keys in .env file[/yellow]")

@cli.command()
def stats():
    """📊 Show database statistics"""
    
    autodj = AutoDJ()
    autodj.display_stats()

@cli.command()
@click.option('--style-score', '-s', default=0.7, help='Minimum style match score')
def list_tracks(style_score):
    """📋 List discovered tracks from database"""
    
    autodj = AutoDJ()
    tracks = autodj.db.get_tracks_by_style(style_score)
    
    if tracks:
        console.print(f"\n[green]Found {len(tracks)} tracks with style score >= {style_score}[/green]")
        autodj.display_tracks(tracks)
    else:
        console.print(f"[yellow]No tracks found with style score >= {style_score}[/yellow]")

@cli.command()
def setup():
    """⚙️  Setup AutoDJ with API keys"""
    
    console.print(Panel.fit(
        "[bold blue]AutoDJ Setup[/bold blue]\n"
        "Configure your API keys for full functionality",
        title="⚙️ Setup"
    ))
    
    env_file = ".env"
    
    if os.path.exists(env_file):
        console.print(f"[yellow]Found existing {env_file} file[/yellow]")
    else:
        console.print(f"[blue]Creating {env_file} file...[/blue]")
    
    # Check for API keys
    required_keys = [
        ("OPENAI_API_KEY", "OpenAI API key for track analysis"),
        ("PERPLEXITY_API_KEY", "Perplexity API key for artist discovery"),
        ("BEATPORT_API_KEY", "Beatport API key (optional - will use web scraping)")
    ]
    
    setup_table = Table(title="🔑 API Key Status")
    setup_table.add_column("Service", style="cyan")
    setup_table.add_column("Status", style="green")
    setup_table.add_column("Required", style="yellow")
    
    for key, description in required_keys:
        value = os.getenv(key)
        status = "✅ Configured" if value else "❌ Missing"
        required = "Yes" if key != "BEATPORT_API_KEY" else "Optional"
        setup_table.add_row(key, status, required)
    
    console.print(setup_table)
    
    console.print(f"\n[blue]📝 Edit {env_file} file to add your API keys[/blue]")
    console.print(f"[blue]📖 See {env_file}.example for the required format[/blue]")

if __name__ == '__main__':
    cli()
