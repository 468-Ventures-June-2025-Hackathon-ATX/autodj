"""
Database initialization and management for AutoDJ
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from config.settings import DATABASE_PATH

class TrackDatabase:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tracks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                bpm INTEGER,
                key TEXT,
                genre TEXT,
                label TEXT,
                release_date TEXT,
                beatport_id TEXT,
                beatport_url TEXT,
                popularity_score REAL,
                energy_level TEXT,
                style_match_score REAL,
                discovered_from TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(artist, title)
            )
        ''')
        
        # Artists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                style TEXT,
                labels TEXT,  -- JSON array
                social_links TEXT,  -- JSON object
                similarity_to_disco_lines REAL,
                discovered_from TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Playlists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                track_ids TEXT,  -- JSON array of track IDs
                total_duration INTEGER,  -- in seconds
                avg_bpm REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Search history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                source TEXT NOT NULL,  -- 'perplexity', 'reddit', 'beatport'
                results_count INTEGER,
                search_params TEXT,  -- JSON object
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_track(self, track_data: Dict) -> int:
        """Add a new track to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO tracks 
                (title, artist, bpm, key, genre, label, release_date, 
                 beatport_id, beatport_url, popularity_score, energy_level, 
                 style_match_score, discovered_from)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                track_data.get('title'),
                track_data.get('artist'),
                track_data.get('bpm'),
                track_data.get('key'),
                track_data.get('genre'),
                track_data.get('label'),
                track_data.get('release_date'),
                track_data.get('beatport_id'),
                track_data.get('beatport_url'),
                track_data.get('popularity_score'),
                track_data.get('energy_level'),
                track_data.get('style_match_score'),
                track_data.get('discovered_from')
            ))
            
            track_id = cursor.lastrowid
            conn.commit()
            return track_id
            
        except sqlite3.IntegrityError:
            # Track already exists, get its ID
            cursor.execute(
                'SELECT id FROM tracks WHERE artist = ? AND title = ?',
                (track_data.get('artist'), track_data.get('title'))
            )
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
    
    def add_artist(self, artist_data: Dict) -> int:
        """Add a new artist to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO artists 
                (name, style, labels, social_links, similarity_to_disco_lines, discovered_from)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                artist_data.get('name'),
                artist_data.get('style'),
                json.dumps(artist_data.get('labels', [])),
                json.dumps(artist_data.get('social_links', {})),
                artist_data.get('similarity_to_disco_lines'),
                artist_data.get('discovered_from')
            ))
            
            artist_id = cursor.lastrowid
            conn.commit()
            return artist_id
            
        except sqlite3.IntegrityError:
            cursor.execute('SELECT id FROM artists WHERE name = ?', (artist_data.get('name'),))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
    
    def get_tracks_by_style(self, min_style_score: float = 0.7) -> List[Dict]:
        """Get tracks that match Disco Lines style"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tracks 
            WHERE style_match_score >= ? 
            ORDER BY style_match_score DESC, popularity_score DESC
        ''', (min_style_score,))
        
        columns = [description[0] for description in cursor.description]
        tracks = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return tracks
    
    def get_tracks_by_bpm_range(self, min_bpm: int, max_bpm: int) -> List[Dict]:
        """Get tracks within BPM range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tracks 
            WHERE bpm BETWEEN ? AND ?
            ORDER BY style_match_score DESC, popularity_score DESC
        ''', (min_bpm, max_bpm))
        
        columns = [description[0] for description in cursor.description]
        tracks = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return tracks
    
    def create_playlist(self, name: str, track_ids: List[int], description: str = "") -> int:
        """Create a new playlist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate playlist stats
        if track_ids:
            placeholders = ','.join(['?' for _ in track_ids])
            cursor.execute(f'''
                SELECT AVG(bpm), SUM(300) as total_duration 
                FROM tracks WHERE id IN ({placeholders})
            ''', track_ids)
            
            avg_bpm, total_duration = cursor.fetchone()
        else:
            avg_bpm, total_duration = 0, 0
        
        cursor.execute('''
            INSERT INTO playlists (name, description, track_ids, total_duration, avg_bpm)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, description, json.dumps(track_ids), total_duration or 0, avg_bpm or 0))
        
        playlist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return playlist_id
    
    def log_search(self, query: str, source: str, results_count: int, search_params: Dict = None):
        """Log a search operation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_history (query, source, results_count, search_params)
            VALUES (?, ?, ?, ?)
        ''', (query, source, results_count, json.dumps(search_params or {})))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Track count
        cursor.execute('SELECT COUNT(*) FROM tracks')
        stats['total_tracks'] = cursor.fetchone()[0]
        
        # Artist count
        cursor.execute('SELECT COUNT(*) FROM artists')
        stats['total_artists'] = cursor.fetchone()[0]
        
        # Playlist count
        cursor.execute('SELECT COUNT(*) FROM playlists')
        stats['total_playlists'] = cursor.fetchone()[0]
        
        # High-quality tracks (style score > 0.8)
        cursor.execute('SELECT COUNT(*) FROM tracks WHERE style_match_score > 0.8')
        stats['high_quality_tracks'] = cursor.fetchone()[0]
        
        # Recent tracks (last 30 days)
        cursor.execute('''
            SELECT COUNT(*) FROM tracks 
            WHERE created_at > datetime('now', '-30 days')
        ''')
        stats['recent_discoveries'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
