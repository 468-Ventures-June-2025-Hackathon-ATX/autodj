"""
Beatport Web Automation - Automated track purchasing using Selenium
WARNING: This violates Beatport's Terms of Service. Use at your own risk.
"""
import time
import os
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests

class BeatportWebAutomation:
    def __init__(self, headless: bool = True, download_dir: str = None):
        self.headless = headless
        self.download_dir = download_dir or os.path.join(os.getcwd(), 'data', 'downloads')
        self.driver = None
        self.logged_in = False
        
        # Create download directory
        os.makedirs(self.download_dir, exist_ok=True)
    
    def setup_driver(self):
        """Setup Chrome WebDriver with download preferences"""
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Download preferences
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Additional options for stability
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # User agent to appear more human
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            print("💡 Make sure ChromeDriver is installed and in PATH")
            return False
    
    def login(self, email: str, password: str) -> bool:
        """Login to Beatport account"""
        
        if not self.driver:
            if not self.setup_driver():
                return False
        
        try:
            print("🔐 Logging into Beatport...")
            
            # Navigate to login page
            self.driver.get("https://www.beatport.com/login")
            
            # Wait for login form
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            password_field = self.driver.find_element(By.NAME, "password")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            # Fill in credentials
            email_field.clear()
            email_field.send_keys(email)
            
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit login
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 15).until(
                lambda driver: "login" not in driver.current_url.lower()
            )
            
            # Check if login was successful
            if "account" in self.driver.current_url or "my-beatport" in self.driver.current_url:
                print("✅ Successfully logged into Beatport")
                self.logged_in = True
                return True
            else:
                print("❌ Login failed - check credentials")
                return False
                
        except TimeoutException:
            print("❌ Login timeout - page took too long to load")
            return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def search_and_purchase_track(self, artist: str, title: str) -> Optional[str]:
        """Search for a track and attempt to purchase it"""
        
        if not self.logged_in:
            print("❌ Not logged in to Beatport")
            return None
        
        try:
            print(f"🔍 Searching for: {artist} - {title}")
            
            # Navigate to search
            search_query = f"{artist} {title}".replace(" ", "+")
            search_url = f"https://www.beatport.com/search?q={search_query}"
            self.driver.get(search_url)
            
            # Wait for search results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "track-grid-item"))
            )
            
            # Find the best matching track
            track_element = self._find_best_match(artist, title)
            
            if not track_element:
                print(f"❌ Track not found: {artist} - {title}")
                return None
            
            # Get track URL
            track_link = track_element.find_element(By.CSS_SELECTOR, "a.buk-track-title")
            track_url = track_link.get_attribute("href")
            
            # Navigate to track page
            self.driver.get(track_url)
            
            # Attempt to purchase
            download_path = self._purchase_track()
            
            if download_path:
                print(f"✅ Successfully purchased: {artist} - {title}")
                return download_path
            else:
                print(f"❌ Purchase failed: {artist} - {title}")
                return None
                
        except Exception as e:
            print(f"❌ Error purchasing track: {e}")
            return None
    
    def _find_best_match(self, artist: str, title: str) -> Optional[object]:
        """Find the best matching track from search results"""
        
        try:
            track_elements = self.driver.find_elements(By.CLASS_NAME, "track-grid-item")
            
            best_match = None
            best_score = 0
            
            for track_element in track_elements:
                try:
                    # Get track info
                    track_title_elem = track_element.find_element(By.CSS_SELECTOR, ".buk-track-title")
                    track_artist_elem = track_element.find_element(By.CSS_SELECTOR, ".buk-track-artists")
                    
                    track_title = track_title_elem.text.lower()
                    track_artist = track_artist_elem.text.lower()
                    
                    # Calculate match score
                    title_score = self._calculate_similarity(title.lower(), track_title)
                    artist_score = self._calculate_similarity(artist.lower(), track_artist)
                    
                    total_score = (title_score + artist_score) / 2
                    
                    if total_score > best_score and total_score > 0.7:  # Minimum 70% match
                        best_score = total_score
                        best_match = track_element
                        
                except Exception:
                    continue
            
            return best_match
            
        except Exception:
            return None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        
        # Simple word-based similarity
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _purchase_track(self) -> Optional[str]:
        """Attempt to purchase the current track"""
        
        try:
            # Look for purchase/download button
            purchase_selectors = [
                "button[data-track-action='purchase']",
                ".buk-track-purchase-button",
                "button:contains('Add to Cart')",
                "button:contains('Buy')",
                ".purchase-button"
            ]
            
            purchase_button = None
            for selector in purchase_selectors:
                try:
                    purchase_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not purchase_button:
                print("❌ Purchase button not found")
                return None
            
            # Check if track is already owned
            if "owned" in purchase_button.get_attribute("class").lower():
                print("✅ Track already owned - attempting download")
                return self._download_owned_track()
            
            # Click purchase button
            purchase_button.click()
            
            # Wait for cart/checkout process
            time.sleep(2)
            
            # Handle cart and checkout
            return self._complete_checkout()
            
        except Exception as e:
            print(f"❌ Purchase error: {e}")
            return None
    
    def _download_owned_track(self) -> Optional[str]:
        """Download a track that's already owned"""
        
        try:
            # Look for download button
            download_selectors = [
                "button[data-track-action='download']",
                ".download-button",
                "a[href*='download']"
            ]
            
            download_button = None
            for selector in download_selectors:
                try:
                    download_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if download_button:
                download_button.click()
                
                # Wait for download to start
                time.sleep(5)
                
                # Check for downloaded file
                return self._check_for_download()
            
            return None
            
        except Exception as e:
            print(f"❌ Download error: {e}")
            return None
    
    def _complete_checkout(self) -> Optional[str]:
        """Complete the checkout process"""
        
        try:
            # This is a simplified version - real implementation would need
            # to handle cart, payment confirmation, etc.
            
            # Look for checkout button
            checkout_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button:contains('Checkout')"))
            )
            
            checkout_button.click()
            
            # Wait for payment processing
            time.sleep(10)
            
            # Check for download
            return self._check_for_download()
            
        except Exception as e:
            print(f"❌ Checkout error: {e}")
            return None
    
    def _check_for_download(self) -> Optional[str]:
        """Check if file was downloaded"""
        
        # Wait for download to complete
        time.sleep(5)
        
        # Check download directory for new files
        try:
            files = os.listdir(self.download_dir)
            audio_files = [f for f in files if f.lower().endswith(('.mp3', '.wav', '.flac', '.m4a'))]
            
            if audio_files:
                # Return the most recent file
                latest_file = max(audio_files, key=lambda f: os.path.getctime(os.path.join(self.download_dir, f)))
                return os.path.join(self.download_dir, latest_file)
            
            return None
            
        except Exception:
            return None
    
    def purchase_playlist(self, tracks: List[Dict]) -> Dict[str, str]:
        """Purchase multiple tracks"""
        
        results = {}
        successful = 0
        
        print(f"🛒 Starting purchase of {len(tracks)} tracks...")
        
        for i, track in enumerate(tracks, 1):
            artist = track.get('artist', '')
            title = track.get('title', '')
            
            print(f"\n[{i}/{len(tracks)}] Purchasing: {artist} - {title}")
            
            download_path = self.search_and_purchase_track(artist, title)
            
            if download_path:
                results[f"{artist} - {title}"] = download_path
                successful += 1
            else:
                results[f"{artist} - {title}"] = None
            
            # Rate limiting to avoid detection
            time.sleep(3)
        
        print(f"\n🎉 Purchase complete: {successful}/{len(tracks)} tracks successful")
        return results
    
    def close(self):
        """Close the browser"""
        
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logged_in = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
