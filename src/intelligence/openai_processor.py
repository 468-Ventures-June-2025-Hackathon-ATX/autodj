"""
OpenAI client for processing track information and style matching
"""
import openai
import time
import json
from typing import List, Dict, Optional
from config.settings import OPENAI_API_KEY, API_RATE_LIMIT, DISCO_LINES_STYLE

class OpenAIProcessor:
    def __init__(self, api_key: str = OPENAI_API_KEY):
        self.api_key = api_key
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None
    
    def analyze_track_style_match(self, track_info: Dict) -> Dict:
        """Analyze how well a track matches Disco Lines' style"""
        
        if not self.client:
            print("Warning: OpenAI API key not configured, using default analysis")
            return self._default_analysis()
        
        prompt = f"""
        Analyze this track and determine how well it matches the style of DJ Disco Lines.
        
        Track Information:
        - Artist: {track_info.get('artist', 'Unknown')}
        - Title: {track_info.get('title', 'Unknown')}
        - BPM: {track_info.get('bpm', 'Unknown')}
        - Key: {track_info.get('key', 'Unknown')}
        - Genre: {track_info.get('genre', 'Unknown')}
        - Label: {track_info.get('label', 'Unknown')}
        
        Disco Lines Style Reference:
        - Genres: {', '.join(DISCO_LINES_STYLE['genres'])}
        - BPM Range: {DISCO_LINES_STYLE['bpm_range'][0]}-{DISCO_LINES_STYLE['bpm_range'][1]}
        - Energy Level: {DISCO_LINES_STYLE['energy_level']}
        - Similar Artists: {', '.join(DISCO_LINES_STYLE['similar_artists'][:5])}
        - Reference Tracks: {', '.join(DISCO_LINES_STYLE['reference_tracks'][:5])}
        
        Provide a JSON response with:
        {{
            "style_match_score": 0.0-1.0,
            "bpm_compatibility": 0.0-1.0,
            "genre_match": 0.0-1.0,
            "energy_match": 0.0-1.0,
            "overall_score": 0.0-1.0,
            "reasoning": "explanation of the scoring",
            "recommendations": "suggestions for playlist placement or mixing"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert DJ and music analyst specializing in electronic music, particularly tech house and disco house. Provide accurate, detailed analysis of track compatibility."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                analysis = json.loads(content)
                return analysis
            except json.JSONDecodeError:
                # Fallback: extract scores from text
                return self._extract_scores_from_text(content)
        
        except Exception as e:
            print(f"Error analyzing track style: {e}")
            return self._default_analysis()
        
        finally:
            time.sleep(API_RATE_LIMIT)
    
    def extract_tracks_from_text(self, text: str, source: str = "unknown") -> List[Dict]:
        """Extract track information from unstructured text"""
        
        prompt = f"""
        Extract track information from this text. Look for artist names, track titles, and any additional metadata.
        
        Text to analyze:
        {text[:2000]}  # Limit text length
        
        Extract tracks in this JSON format:
        [
            {{
                "artist": "Artist Name",
                "title": "Track Title",
                "bpm": null or number,
                "key": null or "key",
                "genre": null or "genre",
                "label": null or "label",
                "release_date": null or "YYYY-MM-DD",
                "confidence": 0.0-1.0
            }}
        ]
        
        Rules:
        - Only extract clear artist - title combinations
        - Ignore incomplete or unclear references
        - Set confidence based on how clear the extraction is
        - Focus on electronic music tracks
        - Prefer tracks that might be tech house, house, or disco house
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting music track information from text. Be precise and only extract clear, unambiguous track references."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            
            try:
                tracks = json.loads(content)
                # Add source information
                for track in tracks:
                    track['discovered_from'] = source
                return tracks
            except json.JSONDecodeError:
                return self._extract_tracks_fallback(text, source)
        
        except Exception as e:
            print(f"Error extracting tracks: {e}")
            return []
        
        finally:
            time.sleep(API_RATE_LIMIT)
    
    def classify_artist_style(self, artist_info: Dict) -> Dict:
        """Classify an artist's style and similarity to Disco Lines"""
        
        prompt = f"""
        Analyze this artist and classify their musical style, particularly in relation to Disco Lines.
        
        Artist Information:
        - Name: {artist_info.get('name', 'Unknown')}
        - Style: {artist_info.get('style', 'Unknown')}
        - Tracks: {', '.join(artist_info.get('tracks', [])[:5])}
        - Labels: {', '.join(artist_info.get('labels', [])[:3])}
        
        Disco Lines Reference Style:
        - Tech house with disco/funk influences
        - BPM: 120-128
        - Labels: {', '.join(DISCO_LINES_STYLE['labels'][:3])}
        - Similar to: {', '.join(DISCO_LINES_STYLE['similar_artists'][:3])}
        
        Provide analysis in JSON format:
        {{
            "primary_genre": "main genre",
            "sub_genres": ["list", "of", "sub-genres"],
            "bpm_range": [min, max],
            "similarity_to_disco_lines": 0.0-1.0,
            "style_keywords": ["keyword1", "keyword2"],
            "recommended_for_playlist": true/false,
            "reasoning": "explanation of classification"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a music genre expert specializing in electronic music classification and artist analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            try:
                classification = json.loads(content)
                return classification
            except json.JSONDecodeError:
                return self._default_artist_classification()
        
        except Exception as e:
            print(f"Error classifying artist: {e}")
            return self._default_artist_classification()
        
        finally:
            time.sleep(API_RATE_LIMIT)
    
    def generate_playlist_description(self, tracks: List[Dict], playlist_name: str) -> str:
        """Generate a description for a playlist based on its tracks"""
        
        if not self.client:
            return f"A curated collection of {len(tracks)} tech house and disco house tracks inspired by Disco Lines' signature sound."
        
        # Summarize track information
        artists = [track.get('artist', '') for track in tracks[:10]]
        genres = list(set([track.get('genre', '') for track in tracks if track.get('genre')]))
        avg_bpm = sum([track.get('bpm', 0) for track in tracks if track.get('bpm')]) / len([t for t in tracks if t.get('bpm')])
        
        prompt = f"""
        Create an engaging description for this DJ playlist inspired by Disco Lines' style.
        
        Playlist: {playlist_name}
        Number of tracks: {len(tracks)}
        Featured artists: {', '.join(artists[:8])}
        Genres: {', '.join(genres[:5])}
        Average BPM: {avg_bpm:.0f}
        
        Create a description that:
        - Captures the energy and vibe of the playlist
        - Mentions the Disco Lines influence
        - Highlights key artists or tracks
        - Describes the musical journey
        - Is suitable for DJ use and music discovery
        - Is 2-3 sentences long
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a creative music writer who specializes in electronic music and DJ culture. Write engaging, authentic descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error generating playlist description: {e}")
            return f"A curated collection of {len(tracks)} tech house and disco house tracks inspired by Disco Lines' signature sound."
        
        finally:
            time.sleep(API_RATE_LIMIT)
    
    def _extract_scores_from_text(self, text: str) -> Dict:
        """Fallback method to extract scores from text response"""
        
        import re
        
        scores = {
            "style_match_score": 0.5,
            "bpm_compatibility": 0.5,
            "genre_match": 0.5,
            "energy_match": 0.5,
            "overall_score": 0.5,
            "reasoning": text[:200],
            "recommendations": "Manual review recommended"
        }
        
        # Try to extract numerical scores
        score_patterns = [
            r"style_match_score[\"']?\s*:\s*([0-9.]+)",
            r"overall_score[\"']?\s*:\s*([0-9.]+)",
            r"score[\"']?\s*:\s*([0-9.]+)"
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                scores["overall_score"] = min(score, 1.0)
                break
        
        return scores
    
    def _extract_tracks_fallback(self, text: str, source: str) -> List[Dict]:
        """Fallback method to extract tracks using simple pattern matching"""
        
        import re
        
        tracks = []
        
        # Common patterns for track mentions
        patterns = [
            r"([A-Za-z\s&]+)\s*[-–—]\s*([A-Za-z\s&()]+)",  # Artist - Title
            r"([A-Za-z\s&]+)\s*:\s*([A-Za-z\s&()]+)",      # Artist : Title
            r"\"([^\"]+)\"\s*by\s*([A-Za-z\s&]+)",         # "Title" by Artist
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 2:
                    artist, title = match
                    if len(artist.strip()) > 2 and len(title.strip()) > 2:
                        tracks.append({
                            "artist": artist.strip(),
                            "title": title.strip(),
                            "bpm": None,
                            "key": None,
                            "genre": None,
                            "label": None,
                            "release_date": None,
                            "confidence": 0.6,
                            "discovered_from": source
                        })
        
        return tracks[:10]  # Limit to 10 tracks
    
    def _default_analysis(self) -> Dict:
        """Default analysis when API fails"""
        return {
            "style_match_score": 0.5,
            "bpm_compatibility": 0.5,
            "genre_match": 0.5,
            "energy_match": 0.5,
            "overall_score": 0.5,
            "reasoning": "Analysis unavailable - manual review required",
            "recommendations": "Review track manually for style compatibility"
        }
    
    def _default_artist_classification(self) -> Dict:
        """Default artist classification when API fails"""
        return {
            "primary_genre": "electronic",
            "sub_genres": ["house"],
            "bpm_range": [120, 130],
            "similarity_to_disco_lines": 0.5,
            "style_keywords": ["electronic", "house"],
            "recommended_for_playlist": True,
            "reasoning": "Classification unavailable - manual review required"
        }
