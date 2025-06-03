"""
Perplexity API client for discovering artists and tracks similar to Disco Lines
"""
import requests
import time
import json
from typing import List, Dict, Optional
from config.settings import PERPLEXITY_API_KEY, API_RATE_LIMIT, DISCO_LINES_STYLE

class PerplexityClient:
    def __init__(self, api_key: str = PERPLEXITY_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def search_similar_artists(self, limit: int = 20) -> List[Dict]:
        """Search for artists similar to Disco Lines"""
        
        # Build search query based on Disco Lines' style
        similar_artists = ", ".join(DISCO_LINES_STYLE['similar_artists'][:5])
        labels = ", ".join(DISCO_LINES_STYLE['labels'][:3])
        
        query = f"""
        Find electronic music artists similar to Disco Lines who make tech house and disco house music.
        Focus on artists who:
        - Make music similar to {similar_artists}
        - Release on labels like {labels}
        - Play BPM range 120-128
        - Have a disco/funk influence in their tech house sound
        - Are active in 2023-2024
        
        For each artist, provide:
        - Artist name
        - Musical style/genre
        - Key tracks or releases
        - Record labels they work with
        - Social media presence (if known)
        
        Limit to {limit} artists and focus on currently active artists.
        """
        
        return self._make_request(query, "similar_artists")
    
    def search_disco_lines_collaborators(self) -> List[Dict]:
        """Search for artists who have collaborated with or remixed Disco Lines"""
        
        reference_tracks = ", ".join(DISCO_LINES_STYLE['reference_tracks'][:5])
        
        query = f"""
        Find artists who have collaborated with, remixed, or are frequently played alongside Disco Lines.
        Look for:
        - Artists who have remixed tracks like {reference_tracks}
        - DJs who include Disco Lines in their sets
        - Artists on the same festival lineups as Disco Lines
        - Collaborators on tracks with Disco Lines
        - Artists with similar Beatport chart positions
        
        For each artist, provide their name, collaboration details, and musical style.
        """
        
        return self._make_request(query, "collaborators")
    
    def search_label_artists(self, label: str) -> List[Dict]:
        """Search for artists on specific labels that Disco Lines works with"""
        
        query = f"""
        Find current tech house and house music artists signed to {label} record label.
        Focus on artists who:
        - Release tech house, disco house, or funky house music
        - Are active in 2023-2024
        - Have tracks in the 120-128 BPM range
        - Have a similar sound to Disco Lines, SIDEPIECE, or John Summit
        
        For each artist, provide:
        - Artist name
        - Recent releases on {label}
        - Musical style
        - Notable tracks
        """
        
        return self._make_request(query, f"label_{label}")
    
    def search_festival_lineups(self) -> List[Dict]:
        """Search for artists from festival lineups where Disco Lines has played"""
        
        query = f"""
        Find electronic music festival lineups from 2023-2024 that featured tech house artists similar to Disco Lines.
        Look for festivals like:
        - EDC (Electric Daisy Carnival)
        - Ultra Music Festival
        - Tomorrowland
        - Coachella
        - Miami Music Week events
        
        Focus on tech house and house music artists from these lineups who:
        - Play similar BPM ranges (120-128)
        - Have a disco/funk influence
        - Are popular in the current scene
        
        Provide artist names and which festivals they played.
        """
        
        return self._make_request(query, "festival_lineups")
    
    def search_reddit_recommendations(self) -> List[Dict]:
        """Search Reddit for Disco Lines recommendations and similar artists"""
        
        query = f"""
        Search Reddit discussions about Disco Lines and find artist recommendations.
        Look in subreddits like:
        - r/TechHouse
        - r/House
        - r/EDM
        - r/electronicmusic
        
        Find posts asking for:
        - Artists similar to Disco Lines
        - Tech house recommendations
        - Disco house artists
        - Festival tech house sets
        
        Extract artist names mentioned as similar to Disco Lines or recommended alongside Disco Lines tracks.
        """
        
        return self._make_request(query, "reddit_recommendations")
    
    def _make_request(self, query: str, search_type: str) -> List[Dict]:
        """Make a request to Perplexity API"""
        
        if not self.api_key:
            print("Warning: No Perplexity API key provided")
            return []
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a music discovery expert specializing in electronic music, particularly tech house and disco house. Provide accurate, current information about artists, tracks, and the electronic music scene."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.3,
            "top_p": 0.9,
            "return_citations": True,
            "search_domain_filter": ["reddit.com", "beatport.com", "soundcloud.com", "mixmag.net", "djmag.com"]
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                citations = result.get('citations', [])
                
                # Parse the response to extract structured data
                parsed_data = self._parse_response(content, search_type)
                
                # Add citations to the data
                for item in parsed_data:
                    item['citations'] = citations
                    item['search_type'] = search_type
                
                return parsed_data
            
            else:
                print(f"Perplexity API error: {response.status_code} - {response.text}")
                return []
        
        except Exception as e:
            print(f"Error making Perplexity request: {e}")
            return []
        
        finally:
            # Rate limiting
            time.sleep(API_RATE_LIMIT)
    
    def _parse_response(self, content: str, search_type: str) -> List[Dict]:
        """Parse Perplexity response into structured data"""
        
        artists = []
        lines = content.split('\n')
        current_artist = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_artist:
                    artists.append(current_artist)
                    current_artist = {}
                continue
            
            # Look for artist names (usually start with numbers or bullets)
            if any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '•', '-', '*']):
                if current_artist:
                    artists.append(current_artist)
                
                # Extract artist name
                artist_name = line
                for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '•', '-', '*']:
                    artist_name = artist_name.replace(prefix, '').strip()
                
                # Remove common prefixes
                artist_name = artist_name.split(':')[0].strip()
                artist_name = artist_name.split('-')[0].strip()
                
                current_artist = {
                    'name': artist_name,
                    'style': '',
                    'tracks': [],
                    'labels': [],
                    'social_links': {},
                    'discovered_from': f'perplexity_{search_type}'
                }
            
            # Look for style/genre information
            elif any(keyword in line.lower() for keyword in ['style:', 'genre:', 'sound:', 'music:']):
                if current_artist:
                    current_artist['style'] = line.split(':')[-1].strip()
            
            # Look for track information
            elif any(keyword in line.lower() for keyword in ['track:', 'release:', 'song:', 'hit:']):
                if current_artist:
                    track_info = line.split(':')[-1].strip()
                    current_artist['tracks'].append(track_info)
            
            # Look for label information
            elif any(keyword in line.lower() for keyword in ['label:', 'record:', 'released on']):
                if current_artist:
                    label_info = line.split(':')[-1].strip()
                    current_artist['labels'].append(label_info)
        
        # Add the last artist if exists
        if current_artist:
            artists.append(current_artist)
        
        # Filter out empty or invalid entries
        valid_artists = []
        for artist in artists:
            if artist.get('name') and len(artist['name']) > 2:
                # Calculate similarity score based on style keywords
                similarity_score = self._calculate_similarity_score(artist)
                artist['similarity_to_disco_lines'] = similarity_score
                valid_artists.append(artist)
        
        return valid_artists
    
    def _calculate_similarity_score(self, artist: Dict) -> float:
        """Calculate similarity score to Disco Lines based on style and other factors"""
        
        score = 0.5  # Base score
        
        style_text = (artist.get('style', '') + ' ' + ' '.join(artist.get('tracks', []))).lower()
        
        # Check for genre matches
        for genre in DISCO_LINES_STYLE['genres']:
            if genre.lower() in style_text:
                score += 0.2
        
        # Check for similar artist mentions
        for similar_artist in DISCO_LINES_STYLE['similar_artists']:
            if similar_artist.lower() in style_text:
                score += 0.15
        
        # Check for label matches
        for label in DISCO_LINES_STYLE['labels']:
            if any(label.lower() in l.lower() for l in artist.get('labels', [])):
                score += 0.1
        
        # Check for key terms
        key_terms = ['disco', 'funk', 'groove', 'tech house', 'house', 'club', 'dance']
        for term in key_terms:
            if term in style_text:
                score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
