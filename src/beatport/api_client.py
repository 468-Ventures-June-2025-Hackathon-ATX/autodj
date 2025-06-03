"""
Beatport API client for track discovery and metadata enrichment
"""
import requests
import time
import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from config.settings import BEATPORT_API_KEY, API_RATE_LIMIT, DISCO_LINES_STYLE

class BeatportClient:
    def __init__(self, api_key: str = BEATPORT_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.beatport.com/v4"
        self.web_base_url = "https://www.beatport.com"
        self.headers = {
            "User-Agent": "AutoDJ/1.0 (Music Discovery Bot)",
            "Accept": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def search_tracks(self, query: str, genre: str = None, limit: int = 50) -> List[Dict]:
        """Search for tracks on Beatport"""
        
        # If no API key, fall back to web scraping
        if not self.api_key:
            return self._web_search_tracks(query, limit)
        
        params = {
            "q": query,
            "type": "tracks",
            "per_page": limit
        }
        
        if genre:
            params["genre"] = genre
        
        try:
            response = requests.get(
                f"{self.base_url}/catalog/search",
                headers=self.headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get("tracks", [])
                return [self._format_track_data(track) for track in tracks]
            else:
                print(f"Beatport API error: {response.status_code}")
                return self._web_search_tracks(query, limit)
        
        except Exception as e:
            print(f"Error searching Beatport: {e}")
            return self._web_search_tracks(query, limit)
        
        finally:
            time.sleep(API_RATE_LIMIT)
    
    def search_artist_tracks(self, artist_name: str, limit: int = 20) -> List[Dict]:
        """Search for tracks by a specific artist"""
        
        query = f"artist:{artist_name}"
        return self.search_tracks(query, limit=limit)
    
    def search_label_releases(self, label_name: str, limit: int = 30) -> List[Dict]:
        """Search for recent releases from a specific label"""
        
        query = f"label:{label_name}"
        tracks = self.search_tracks(query, limit=limit)
        
        # Filter for recent releases and tech house genre
        filtered_tracks = []
        for track in tracks:
            # Prefer tracks in Disco Lines' BPM range
            bpm = track.get('bpm', 0)
            if DISCO_LINES_STYLE['bpm_range'][0] <= bpm <= DISCO_LINES_STYLE['bpm_range'][1]:
                track['style_relevance'] = 'high'
            elif 115 <= bpm <= 135:  # Broader range
                track['style_relevance'] = 'medium'
            else:
                track['style_relevance'] = 'low'
            
            filtered_tracks.append(track)
        
        # Sort by style relevance and popularity
        filtered_tracks.sort(key=lambda x: (
            x.get('style_relevance') == 'high',
            x.get('popularity_score', 0)
        ), reverse=True)
        
        return filtered_tracks
    
    def get_similar_tracks(self, track_id: str) -> List[Dict]:
        """Get tracks similar to a given track"""
        
        if not self.api_key:
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/catalog/tracks/{track_id}/similar",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get("tracks", [])
                return [self._format_track_data(track) for track in tracks]
        
        except Exception as e:
            print(f"Error getting similar tracks: {e}")
        
        finally:
            time.sleep(API_RATE_LIMIT)
        
        return []
    
    def get_genre_charts(self, genre: str = "tech-house", limit: int = 20) -> List[Dict]:
        """Get current charts for a specific genre"""
        
        # Web scraping approach for charts
        try:
            url = f"{self.web_base_url}/genre/{genre}/top-100"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tracks = self._parse_chart_page(soup)
                return tracks[:limit]
        
        except Exception as e:
            print(f"Error getting genre charts: {e}")
        
        finally:
            time.sleep(API_RATE_LIMIT)
        
        return []
    
    def enrich_track_metadata(self, track: Dict) -> Dict:
        """Enrich track data with additional Beatport metadata"""
        
        # Search for the track to get full metadata
        search_query = f"{track.get('artist', '')} {track.get('title', '')}"
        search_results = self.search_tracks(search_query, limit=5)
        
        # Find the best match
        best_match = None
        for result in search_results:
            if (self._normalize_string(result.get('artist', '')) == self._normalize_string(track.get('artist', '')) and
                self._normalize_string(result.get('title', '')) == self._normalize_string(track.get('title', ''))):
                best_match = result
                break
        
        if best_match:
            # Merge the data
            enriched_track = track.copy()
            enriched_track.update({
                'bpm': best_match.get('bpm', track.get('bpm')),
                'key': best_match.get('key', track.get('key')),
                'genre': best_match.get('genre', track.get('genre')),
                'label': best_match.get('label', track.get('label')),
                'release_date': best_match.get('release_date', track.get('release_date')),
                'beatport_id': best_match.get('beatport_id'),
                'beatport_url': best_match.get('beatport_url'),
                'popularity_score': best_match.get('popularity_score', 0.5)
            })
            return enriched_track
        
        return track
    
    def _web_search_tracks(self, query: str, limit: int) -> List[Dict]:
        """Fallback web scraping search when API is not available"""
        
        try:
            # Clean query for URL
            clean_query = query.replace(" ", "%20")
            url = f"{self.web_base_url}/search?q={clean_query}"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tracks = self._parse_search_results(soup)
                return tracks[:limit]
        
        except Exception as e:
            print(f"Error in web search: {e}")
        
        return []
    
    def _parse_search_results(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse Beatport search results from HTML"""
        
        tracks = []
        
        # Look for track containers (this may need adjustment based on Beatport's current HTML structure)
        track_elements = soup.find_all(['div', 'li'], class_=lambda x: x and ('track' in x.lower() or 'item' in x.lower()))
        
        for element in track_elements[:20]:  # Limit parsing
            try:
                track_data = self._extract_track_from_element(element)
                if track_data:
                    tracks.append(track_data)
            except Exception as e:
                continue
        
        return tracks
    
    def _parse_chart_page(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse Beatport chart page"""
        
        tracks = []
        
        # Similar to search results but for chart pages
        track_elements = soup.find_all(['div', 'li'], class_=lambda x: x and 'track' in x.lower())
        
        for i, element in enumerate(track_elements[:50]):
            try:
                track_data = self._extract_track_from_element(element)
                if track_data:
                    track_data['chart_position'] = i + 1
                    track_data['popularity_score'] = max(0.1, 1.0 - (i / 100))  # Higher score for higher chart position
                    tracks.append(track_data)
            except Exception as e:
                continue
        
        return tracks
    
    def _extract_track_from_element(self, element) -> Optional[Dict]:
        """Extract track information from HTML element"""
        
        try:
            # This is a simplified extraction - would need to be adjusted based on actual Beatport HTML
            title_elem = element.find(['a', 'span'], class_=lambda x: x and 'title' in x.lower())
            artist_elem = element.find(['a', 'span'], class_=lambda x: x and 'artist' in x.lower())
            
            if not title_elem or not artist_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            artist = artist_elem.get_text(strip=True)
            
            # Try to extract additional metadata
            bpm_elem = element.find(text=lambda x: x and 'bpm' in x.lower())
            key_elem = element.find(['span'], class_=lambda x: x and 'key' in x.lower())
            
            track_data = {
                'title': title,
                'artist': artist,
                'bpm': self._extract_bpm(bpm_elem) if bpm_elem else None,
                'key': key_elem.get_text(strip=True) if key_elem else None,
                'genre': 'Tech House',  # Default assumption
                'label': None,
                'release_date': None,
                'beatport_id': None,
                'beatport_url': None,
                'popularity_score': 0.5,
                'discovered_from': 'beatport_web'
            }
            
            return track_data
        
        except Exception as e:
            return None
    
    def _format_track_data(self, track_data: Dict) -> Dict:
        """Format track data from Beatport API response"""
        
        return {
            'title': track_data.get('name', ''),
            'artist': ', '.join([artist.get('name', '') for artist in track_data.get('artists', [])]),
            'bpm': track_data.get('bpm'),
            'key': track_data.get('key', {}).get('name') if track_data.get('key') else None,
            'genre': track_data.get('genre', {}).get('name') if track_data.get('genre') else None,
            'label': track_data.get('label', {}).get('name') if track_data.get('label') else None,
            'release_date': track_data.get('date', {}).get('released') if track_data.get('date') else None,
            'beatport_id': str(track_data.get('id', '')),
            'beatport_url': f"https://www.beatport.com/track/{track_data.get('slug', '')}/{track_data.get('id', '')}",
            'popularity_score': min(1.0, track_data.get('chart_position', 100) / 100) if track_data.get('chart_position') else 0.5,
            'discovered_from': 'beatport_api'
        }
    
    def _extract_bpm(self, text: str) -> Optional[int]:
        """Extract BPM from text"""
        
        import re
        
        if not text:
            return None
        
        match = re.search(r'(\d+)\s*bpm', text.lower())
        if match:
            return int(match.group(1))
        
        return None
    
    def _normalize_string(self, s: str) -> str:
        """Normalize string for comparison"""
        
        if not s:
            return ""
        
        return s.lower().strip().replace("&", "and")
    
    def calculate_style_match_score(self, track: Dict) -> float:
        """Calculate how well a track matches Disco Lines' style"""
        
        score = 0.0
        
        # BPM scoring
        bpm = track.get('bpm', 0)
        if bpm:
            if DISCO_LINES_STYLE['bpm_range'][0] <= bpm <= DISCO_LINES_STYLE['bpm_range'][1]:
                score += 0.3
            elif 115 <= bpm <= 135:
                score += 0.15
        
        # Genre scoring
        genre = track.get('genre', '').lower()
        for disco_genre in DISCO_LINES_STYLE['genres']:
            if disco_genre.lower() in genre:
                score += 0.25
                break
        
        # Label scoring
        label = track.get('label', '').lower()
        for disco_label in DISCO_LINES_STYLE['labels']:
            if disco_label.lower() in label:
                score += 0.2
                break
        
        # Artist scoring
        artist = track.get('artist', '').lower()
        for similar_artist in DISCO_LINES_STYLE['similar_artists']:
            if similar_artist.lower() in artist:
                score += 0.25
                break
        
        return min(score, 1.0)
