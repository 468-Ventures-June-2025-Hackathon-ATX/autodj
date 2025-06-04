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
        ("BEATPORT_API_KEY", "Beatport API key (optional - will use web scraping)"),
        ("BEATPORT_EMAIL", "Beatport account email (for audio automation)"),
        ("BEATPORT_PASSWORD", "Beatport account password (for audio automation)")
    ]
    
    setup_table = Table(title="🔑 Configuration Status")
    setup_table.add_column("Service", style="cyan")
    setup_table.add_column("Status", style="green")
    setup_table.add_column("Required", style="yellow")
    
    for key, description in required_keys:
        value = os.getenv(key)
        status = "✅ Configured" if value else "❌ Missing"
        
        if key in ["OPENAI_API_KEY", "PERPLEXITY_API_KEY"]:
            required = "Yes"
        elif key in ["BEATPORT_EMAIL", "BEATPORT_PASSWORD"]:
            required = "Audio Only"
        else:
            required = "Optional"
            
        setup_table.add_row(key, status, required)
    
    console.print(setup_table)
    
    console.print(f"\n[blue]📝 Edit {env_file} file to add your API keys[/blue]")
    console.print(f"[blue]📖 See {env_file}.example for the required format[/blue]")

@cli.command()
@click.option('--count', '-c', default=25, help='Number of tracks to download')
@click.option('--playlist-name', '-n', help='Custom playlist name')
@click.option('--headless/--no-headless', default=True, help='Run browser in headless mode')
@click.option('--social-media/--no-social-media', default=True, help='Include social media sources (TikTok, SoundCloud)')
def download(count, playlist_name, headless, social_media):
    """🎵 Full automation: Discover, download, and prepare tracks for Pioneer XDJ-RX3"""
    
    from src.audio.automation import AudioAutomation
    from config.settings import BEATPORT_EMAIL, BEATPORT_PASSWORD
    
    console.print(Panel.fit(
        "[bold green]AutoDJ - Full Audio Automation[/bold green]\n"
        f"Target: {count} tracks with audio files\n"
        f"Social Media: {'Enabled' if social_media else 'Disabled'}\n"
        "Pipeline: Discover → Download → Process → USB Export",
        title="🚀 Starting Full Automation"
    ))
    
    # Initialize automation
    automation = AudioAutomation()
    
    # Test dependencies
    console.print("\n🔧 [yellow]Testing dependencies...[/yellow]")
    deps = automation.test_dependencies()
    
    deps_table = Table(title="🛠️ Dependencies")
    deps_table.add_column("Tool", style="cyan")
    deps_table.add_column("Status", style="green")
    
    for tool, available in deps.items():
        status = "✅ Available" if available else "❌ Missing"
        deps_table.add_row(tool, status)
    
    console.print(deps_table)
    
    if not deps['selenium']:
        console.print("[red]❌ Selenium not available. Install with: pip install selenium[/red]")
        return
    
    if not deps['chrome_driver']:
        console.print("[red]❌ ChromeDriver not found. Install ChromeDriver and add to PATH[/red]")
        return
    
    if social_media and 'yt-dlp' not in deps:
        # Check yt-dlp separately
        try:
            import subprocess
            subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
            console.print("[green]✅ yt-dlp available for social media downloads[/green]")
        except:
            console.print("[yellow]⚠️  yt-dlp not found. Install with: pip install yt-dlp[/yellow]")
            console.print("[yellow]   Social media downloads will be disabled[/yellow]")
            social_media = False
    
    # Get Beatport credentials from environment
    beatport_credentials = None
    if BEATPORT_EMAIL and BEATPORT_PASSWORD:
        beatport_credentials = {
            'email': BEATPORT_EMAIL,
            'password': BEATPORT_PASSWORD,
            'headless': headless
        }
        console.print("[green]✅ Beatport credentials loaded from .env file[/green]")
    else:
        console.print("[yellow]⚠️  No Beatport credentials in .env - will only use free sources[/yellow]")
        console.print("[blue]💡 Add BEATPORT_EMAIL and BEATPORT_PASSWORD to .env for full automation[/blue]")
    
    try:
        # First discover tracks (reuse existing logic)
        autodj = AutoDJ()
        console.print("\n🔍 [yellow]Phase 1: Discovering tracks...[/yellow]")
        tracks = autodj.discover_tracks(count)
        
        if not tracks:
            console.print("[red]❌ No tracks discovered[/red]")
            return
        
        console.print(f"✅ Discovered {len(tracks)} tracks")
        
        # Run full automation pipeline
        if not playlist_name:
            playlist_name = f"AutoDJ Full Download - {len(tracks)} Tracks"
        
        console.print(f"\n🚀 [yellow]Starting full automation pipeline...[/yellow]")
        results = automation.process_full_pipeline(tracks, playlist_name, beatport_credentials, social_media)
        
        # Display results
        console.print("\n📊 [bold blue]Automation Results[/bold blue]")
        
        results_table = Table(title="🎯 Pipeline Results")
        results_table.add_column("Phase", style="cyan")
        results_table.add_column("Result", style="green")
        
        results_table.add_row("Tracks Discovered", str(results['total_tracks']))
        results_table.add_row("Tracks Downloaded", str(len([v for v in results['downloaded_tracks'].values() if v])))
        results_table.add_row("Tracks Processed", str(len([v for v in results['processed_tracks'].values() if v])))
        results_table.add_row("Final Success Count", str(results['success_count']))
        
        if results['usb_export']:
            results_table.add_row("USB Export", "✅ Success")
            results_table.add_row("Audio Files", str(results['usb_export']['audio_files']))
        else:
            results_table.add_row("USB Export", "❌ Failed")
        
        console.print(results_table)
        
        # Show errors if any
        if results['errors']:
            console.print("\n⚠️ [yellow]Errors encountered:[/yellow]")
            for error in results['errors']:
                console.print(f"   - {error}")
        
        # Success summary
        if results['success_count'] > 0:
            console.print(f"\n🎉 [bold green]Success![/bold green]")
            console.print(f"✅ {results['success_count']} tracks ready for Pioneer XDJ-RX3")
            
            if results['usb_export']:
                console.print(f"📁 USB Path: [blue]{results['usb_export']['usb_path']}[/blue]")
                console.print(f"📄 Rekordbox XML: [blue]{results['usb_export']['xml_path']}[/blue]")
                
                console.print(Panel(
                    "1. Copy the USB export folder to your USB drive\n"
                    "2. Import the rekordbox.xml file into Rekordbox\n"
                    "3. Sync to your Pioneer XDJ-RX3\n"
                    "4. Enjoy your AI-curated playlist!",
                    title="📋 Next Steps",
                    border_style="green"
                ))
        else:
            console.print("[red]❌ No tracks were successfully processed[/red]")
            console.print("[yellow]💡 Try checking your Beatport credentials or internet connection[/yellow]")
    
    except Exception as e:
        console.print(f"[red]❌ Automation failed: {e}[/red]")

@cli.command()
@click.option('--count', '-c', default=10, help='Number of tracks to download')
@click.option('--playlist-name', '-n', help='Custom playlist name')
@click.option('--platforms', '-p', multiple=True, default=['soundcloud', 'tiktok'], help='Social media platforms to search')
def social_download(count, playlist_name, platforms):
    """📱 Download tracks exclusively from social media (TikTok, SoundCloud)"""
    
    from src.audio.download_manager import AudioDownloadManager
    
    console.print(Panel.fit(
        "[bold blue]AutoDJ - Social Media Download[/bold blue]\n"
        f"Target: {count} tracks from social media\n"
        f"Platforms: {', '.join(platforms)}",
        title="📱 Social Media Download"
    ))
    
    # Check yt-dlp availability
    try:
        import subprocess
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        console.print("[green]✅ yt-dlp available[/green]")
    except:
        console.print("[red]❌ yt-dlp not found. Install with: pip install yt-dlp[/red]")
        return
    
    try:
        # First discover tracks
        autodj = AutoDJ()
        console.print("\n🔍 [yellow]Discovering tracks...[/yellow]")
        tracks = autodj.discover_tracks(count)
        
        if not tracks:
            console.print("[red]❌ No tracks discovered[/red]")
            return
        
        console.print(f"✅ Discovered {len(tracks)} tracks")
        
        # Download from social media only
        download_manager = AudioDownloadManager()
        console.print(f"\n📱 [yellow]Downloading from social media...[/yellow]")
        results = download_manager.download_from_social_media_only(tracks, list(platforms))
        
        # Display results
        successful = len([v for v in results.values() if v])
        console.print(f"\n🎉 [bold green]Social media download complete![/bold green]")
        console.print(f"✅ Successfully downloaded: {successful}/{len(tracks)} tracks")
        
        if successful > 0:
            # Create playlist if requested
            if playlist_name:
                console.print(f"\n📝 [yellow]Creating playlist: {playlist_name}[/yellow]")
                successful_tracks = [track for track in tracks if results.get(f"{track.get('artist')} - {track.get('title')}")]
                playlist = autodj.create_playlist(successful_tracks, playlist_name)
                console.print(f"✅ Playlist created with {len(successful_tracks)} tracks")
            
            # Show cache location
            cache_stats = download_manager.social_downloader.get_cache_stats()
            console.print(f"\n📁 Downloaded files location: [blue]{cache_stats['cache_dir']}[/blue]")
            console.print(f"📊 Total files: {cache_stats['total_files']} ({cache_stats['total_size_mb']} MB)")
        
    except Exception as e:
        console.print(f"[red]❌ Social media download failed: {e}[/red]")

@cli.command()
@click.argument('url')
@click.option('--artist', '-a', help='Artist name')
@click.option('--title', '-t', help='Track title')
def download_url(url, artist, title):
    """🔗 Download audio from a specific TikTok or SoundCloud URL"""
    
    from src.audio.download_manager import AudioDownloadManager
    
    if not artist or not title:
        console.print("[red]❌ Both --artist and --title are required[/red]")
        return
    
    console.print(Panel.fit(
        f"[bold cyan]Downloading from URL[/bold cyan]\n"
        f"URL: {url}\n"
        f"Artist: {artist}\n"
        f"Title: {title}",
        title="🔗 Direct URL Download"
    ))
    
    try:
        download_manager = AudioDownloadManager()
        filepath = download_manager.download_from_url(url, artist, title)
        
        if filepath:
            console.print(f"\n✅ [bold green]Download successful![/bold green]")
            console.print(f"📁 File saved: [blue]{filepath}[/blue]")
        else:
            console.print(f"\n❌ [red]Download failed[/red]")
            console.print("[yellow]💡 Make sure the URL is valid and accessible[/yellow]")
    
    except Exception as e:
        console.print(f"[red]❌ Download error: {e}[/red]")

@cli.command()
def audio_status():
    """📊 Show audio automation status and cache statistics"""
    
    from src.audio.automation import AudioAutomation
    
    automation = AudioAutomation()
    status = automation.get_pipeline_status()
    
    console.print(Panel.fit(
        "[bold blue]Audio Automation Status[/bold blue]",
        title="📊 Status"
    ))
    
    # Dependencies
    deps = automation.test_dependencies()
    deps_table = Table(title="🛠️ Dependencies")
    deps_table.add_column("Tool", style="cyan")
    deps_table.add_column("Status", style="green")
    
    for tool, available in deps.items():
        status_text = "✅ Available" if available else "❌ Missing"
        deps_table.add_row(tool, status_text)
    
    console.print(deps_table)
    
    # Cache statistics
    cache_table = Table(title="💾 Cache Statistics")
    cache_table.add_column("Location", style="cyan")
    cache_table.add_column("Files", style="green")
    cache_table.add_column("Size (MB)", style="yellow")
    
    cache_table.add_row(
        "Download Cache",
        str(status['cache_stats']['total_files']),
        str(status['cache_stats']['total_size_mb'])
    )
    
    cache_table.add_row(
        "USB Export",
        str(status['usb_stats']['total_files']),
        str(status['usb_stats']['total_size_mb'])
    )
    
    console.print(cache_table)
    
    # Connection status
    console.print(f"\n🔗 Beatport Connected: {'✅ Yes' if status['beatport_connected'] else '❌ No'}")
    console.print(f"🎵 FFmpeg Available: {'✅ Yes' if status['ffmpeg_available'] else '❌ No'}")

@cli.command()
@click.confirmation_option(prompt='Are you sure you want to clear all cached files?')
def clear_cache():
    """🗑️  Clear all cached audio files and USB exports"""
    
    from src.audio.automation import AudioAutomation
    
    automation = AudioAutomation()
    
    console.print("[yellow]🗑️  Clearing all cached files...[/yellow]")
    
    if automation.clear_all_cache():
        console.print("[green]✅ Cache cleared successfully[/green]")
    else:
        console.print("[red]❌ Failed to clear cache[/red]")

if __name__ == '__main__':
    cli()
