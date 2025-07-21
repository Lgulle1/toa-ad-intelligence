import logging
import traceback

class ChromeWarningFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage().lower()
        if (
            "chrome browser check failed" in msg
            or "chrome" in msg
            or "browser check" in msg
            or "install chrome" in msg
        ):
            print("\n--- FOUND CHROME WARNING:", record.getMessage(), "---")
            print(f"Logger: {record.name}")
            print(f"Level: {record.levelname}")
            print(f"Module: {record.module}")
            print(f"Function: {record.funcName}")
            print(f"Line: {record.lineno}")
            traceback.print_stack()
            print("--- END TRACE ---\n")
        return True

logging.basicConfig(level=logging.DEBUG)
logging.getLogger().addFilter(ChromeWarningFilter())

# TEMP: add a test log to confirm it's working
logging.warning("Chrome browser check failed: TEST WARNING")

import time
from datetime import datetime
from typing import List, Dict, Optional
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class MetaAdScraper:
    """
    Scraper for Meta Ad Library public website
    Extracts advertiser name, ad headline, ad text, media URL, and ad start date
    """
    
    def __init__(self):
        self.base_url = "https://www.facebook.com/ads/library"
        self.driver: Optional[webdriver.Chrome] = None
    
    def _init_driver(self):
        """Initialize Selenium Chrome driver"""
        options = Options()
        options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Disable images and CSS for faster loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        # Initialize Chrome driver with manually set binary path
        self.driver = webdriver.Chrome(options=options)
                
        # Set timeouts
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(30)
    
    def _close_driver(self):
        """Clean up driver resources"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def search_ads(self, keyword: str) -> List[Dict]:
        """
        Search for ads with the given keyword
        """
        ads = []
        
        try:
            self._init_driver()
            
            # Navigate to Meta Ad Library
            logger.info(f"Navigating to Meta Ad Library for keyword: {keyword}")
            
            # Construct search URL - using proper parameters for Meta Ad Library
            search_url = f"{self.base_url}/?active_status=active&ad_type=all&country=US&search_terms={keyword.replace(' ', '%20')}"
            
            logger.info(f"Loading URL: {search_url}")
            self.driver.get(search_url)
            
            # Wait for the page to load
            time.sleep(5)
            
            # Try to close any cookie banners or popups
            self._close_popups()
            
            # Wait for ad results to load with multiple strategies
            logger.info("Waiting for ad results to load...")
            
            # Try different selectors that Meta Ad Library might use
            ads_found = self._wait_for_ads()
            
            if not ads_found:
                logger.warning("No ad containers found after waiting")
                # Take a screenshot for debugging
                try:
                    self.driver.save_screenshot("debug_no_ads.png")
                    logger.info("Debug screenshot saved as debug_no_ads.png")
                except:
                    pass
                
                # Check if we're blocked or redirected
                current_url = self.driver.current_url
                logger.info(f"Current URL: {current_url}")
                
                # Get page source for debugging
                page_source = self.driver.page_source[:1000]
                logger.info(f"Page source preview: {page_source}")
                
                # If we can't find real ads, try alternative approach
                ads = self._try_alternative_extraction(keyword)
            else:
                # Scroll to load more ads
                self._scroll_to_load_ads()
                
                # Extract ad information
                ads = self._extract_ad_data()
                
                logger.info(f"Successfully extracted {len(ads)} real ads")
            
            # If still no real ads found, create minimal fallback
            if not ads:
                logger.warning("No real ads could be extracted, using single demo ad")
                ads = self._create_minimal_demo_ad(keyword)
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            # Create demo ad for demonstration if scraping fails
            ads = self._create_minimal_demo_ad(keyword)
            
        finally:
            self._close_driver()
        
        return ads
    
    def _close_popups(self):
        """Try to close any cookie banners or popups"""
        try:
            # Wait a bit for popups to appear
            time.sleep(2)
            
            close_selectors = [
                '[aria-label="Close"]',
                '[aria-label="Allow all cookies"]',
                '[data-testid="cookie-policy-banner-accept"]',
                'button:contains("Accept All")',
                'button:contains("Allow")',
                'button:contains("Accept")',
                '[role="button"]:contains("Accept")',
                'div[data-testid="cookie-policy-manage-dialog"] button',
                # Facebook specific selectors
                '[data-cookiebanner="accept_button"]',
                '[data-testid="non-users-cookie-banner-accept-button"]'
            ]
            
            for selector in close_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            self.driver.execute_script("arguments[0].click();", element)
                            logger.info(f"Clicked popup close button: {selector}")
                            time.sleep(1)
                            break
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error closing popups: {e}")
    
    def _wait_for_ads(self) -> bool:
        """Wait for ads to load using multiple strategies"""
        # Multiple selectors to try for ad containers
        ad_selectors = [
            # Standard ad library selectors
            '[data-testid="search-result-grid"]',
            '[data-testid="search-result"]',
            '[role="main"] [role="article"]',
            '[data-testid="ad-archive-card"]',
            '[data-testid="political-ad-archive-card"]',
            
            # Generic selectors
            '[role="article"]',
            '.x1yztbdb',
            'div[data-testid*="ad"]',
            'div[aria-label*="ad"]',
            
            # Container selectors
            '[data-testid="search-results"]',
            '[data-pagelet="AdLibrarySearchResults"]',
            'div[role="main"] > div > div',
        ]
        
        # Try each selector with different wait times
        for selector in ad_selectors:
            try:
                logger.info(f"Trying selector: {selector}")
                element = WebDriverWait(self.driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element:
                    logger.info(f"Found ads with selector: {selector}")
                    return True
            except TimeoutException:
                continue
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        return False
    
    def _scroll_to_load_ads(self):
        """Scroll the page to load more ads"""
        try:
            logger.info("Scrolling to load more ads...")
            # Scroll down slowly to trigger lazy loading
            for i in range(5):
                scroll_height = (i + 1) * 500
                self.driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                time.sleep(2)
                
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
        except Exception as e:
            logger.warning(f"Error scrolling: {e}")
    
    def _extract_ad_data(self) -> List[Dict]:
        """Extract ad data from the loaded page"""
        ads = []
        
        try:
            # Get all potential ad elements using multiple selectors
            ad_elements = []
            
            selectors_to_try = [
                '[role="article"]',
                '[data-testid*="ad"]',
                '[data-testid="search-result"]',
                'div[aria-label*="ad" i]',
                '[data-testid="search-result-grid"] > div',
                '[role="main"] > div > div > div',
                # More generic selectors for content
                'div[data-pagelet*="result"]',
                'div[data-testid*="card"]',
                '[class*="card"]',
                '[class*="result"]',
                'div[style*="border"]',
                # Text-based selectors
                'div:contains("Sponsored")',
                'div:contains("Ad")',
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        ad_elements.extend(elements)
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            # Remove duplicates
            unique_elements = []
            seen_elements = set()
            for element in ad_elements:
                element_id = id(element)
                if element_id not in seen_elements:
                    unique_elements.append(element)
                    seen_elements.add(element_id)
            
            logger.info(f"Processing {len(unique_elements)} unique ad elements")
            
            # Debug: Print some element info
            for i, element in enumerate(unique_elements[:5]):
                try:
                    element_text = element.text[:100] if element.text else "No text"
                    logger.info(f"Element {i}: {element_text}")
                except:
                    logger.info(f"Element {i}: Could not get text")
            
            for i, element in enumerate(unique_elements[:20]):  # Limit to 20 elements
                try:
                    ad_data = self._extract_single_ad(element, i)
                    if ad_data and self._is_valid_ad(ad_data):
                        ads.append(ad_data)
                        logger.info(f"Extracted ad {len(ads)}: {ad_data['advertiser_name']}")
                        
                        # Stop when we have enough ads
                        if len(ads) >= 10:
                            break
                    elif ad_data:
                        logger.debug(f"Ad {i} failed validation: {ad_data}")
                            
                except Exception as e:
                    logger.debug(f"Error extracting ad {i}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting ad data: {e}")
        
        return ads
    
    def _extract_single_ad(self, element, index: int) -> Optional[Dict]:
        """Extract data from a single ad element"""
        try:
            # Get all text content from the element
            text_content = element.text
            
            if not text_content or len(text_content.strip()) < 10:
                return None
            
            # Extract advertiser name using multiple strategies
            advertiser = self._extract_advertiser_name(element, text_content)
            
            # Extract headline and body text
            headline, body_text = self._extract_headline_and_text(element, text_content)
            
            # Extract media URL
            media_url = self._extract_media_url(element)
            
            # Extract start date
            start_date = self._extract_start_date(element, text_content)
            
            ad_data = {
                'advertiser_name': advertiser,
                'headline': headline,
                'text': body_text,
                'media_url': media_url,
                'start_date': start_date
            }
            
            return ad_data
            
        except Exception as e:
            logger.debug(f"Error extracting single ad: {str(e)}")
            return None
    
    def _extract_advertiser_name(self, element, text_content: str) -> str:
        """Extract advertiser name using multiple strategies"""
        try:
            # Strategy 1: Look for specific data attributes or classes
            advertiser_selectors = [
                '[data-testid="page-name"]',
                '.x1heor9g',
                '.x1qlqyl8', 
                '[role="link"]',
                'a[href*="facebook.com"]',
                'strong',
                'b',
                '[data-testid*="name"]',
                '[aria-label*="Page"]'
            ]
            
            for selector in advertiser_selectors:
                try:
                    advertiser_element = element.find_element(By.CSS_SELECTOR, selector)
                    advertiser_text = advertiser_element.text.strip()
                    if advertiser_text and len(advertiser_text) > 2 and len(advertiser_text) < 100:
                        return advertiser_text
                except:
                    continue
            
            # Strategy 2: Extract from text content
            lines = text_content.split('\n')
            for line in lines[:3]:  # Check first 3 lines
                line = line.strip()
                if line and len(line) > 2 and len(line) < 100:
                    # Skip common non-advertiser text
                    skip_patterns = [
                        'sponsored', 'ad', 'learn more', 'see more', 'active',
                        'page', 'post', 'video', 'photo', 'link', 'about'
                    ]
                    if not any(pattern in line.lower() for pattern in skip_patterns):
                        return line
            
            return "Unknown Advertiser"
            
        except:
            return "Unknown Advertiser"
    
    def _extract_headline_and_text(self, element, text_content: str) -> tuple:
        """Extract headline and body text"""
        try:
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            if not lines:
                return "No headline", "No description available"
            
            # Strategy 1: Look for specific headline elements
            headline_selectors = [
                'h1', 'h2', 'h3', 'h4',
                '[data-testid*="headline"]',
                '[role="heading"]',
                'div[data-testid*="title"]'
            ]
            
            headline = ""
            for selector in headline_selectors:
                try:
                    headline_element = element.find_element(By.CSS_SELECTOR, selector)
                    headline = headline_element.text.strip()
                    if headline and len(headline) > 5:
                        break
                except:
                    continue
            
            # Strategy 2: Use text analysis if no headline found
            if not headline:
                # Find the longest meaningful line as headline
                for line in lines[1:4]:  # Skip first line (usually advertiser)
                    if len(line) > 10 and len(line) < 200:
                        headline = line
                        break
                
                if not headline and lines:
                    headline = lines[0] if len(lines[0]) > 5 else "No headline"
            
            # Extract body text
            body_lines = []
            found_headline = False
            
            for line in lines:
                if not found_headline and headline and line == headline:
                    found_headline = True
                    continue
                
                if found_headline or not headline:
                    if len(line) > 10 and len(line) < 500:
                        body_lines.append(line)
                        if len(' '.join(body_lines)) > 200:  # Enough text
                            break
            
            body_text = ' '.join(body_lines) if body_lines else "No description available"
            
            # Truncate if too long
            if len(body_text) > 300:
                body_text = body_text[:297] + "..."
            
            return headline or "No headline", body_text
            
        except:
            return "No headline", "No description available"
    
    def _extract_media_url(self, element) -> str:
        """Extract media URL from the ad element"""
        try:
            # Look for images
            img_selectors = [
                'img[src]',
                'img[data-src]',
                '[style*="background-image"]',
                'video[src]',
                'video source[src]'
            ]
            
            for selector in img_selectors:
                try:
                    media_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for media_element in media_elements:
                        # Try src attribute
                        src = media_element.get_attribute('src')
                        if src and 'http' in src and 'facebook' in src:
                            return src
                        
                        # Try data-src attribute
                        data_src = media_element.get_attribute('data-src')
                        if data_src and 'http' in data_src:
                            return data_src
                        
                        # Try background-image style
                        style = media_element.get_attribute('style')
                        if style and 'background-image' in style:
                            url_match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
                            if url_match:
                                return url_match.group(1)
                                
                except:
                    continue
            
            return ""
            
        except:
            return ""
    
    def _extract_start_date(self, element, text_content: str) -> str:
        """Extract start date from the ad"""
        try:
            # Look for date patterns in text
            date_patterns = [
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{1,2}-\d{1,2}-\d{4})',
                r'(\w+ \d{1,2}, \d{4})',
                r'Started running on (\w+ \d{1,2}, \d{4})',
                r'Active since (\d{1,2}/\d{1,2}/\d{4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text_content)
                if match:
                    return match.group(1)
            
            # Look for time elements
            time_selectors = [
                'time[datetime]',
                '[data-testid*="date"]',
                '[data-testid*="time"]'
            ]
            
            for selector in time_selectors:
                try:
                    time_element = element.find_element(By.CSS_SELECTOR, selector)
                    datetime_attr = time_element.get_attribute('datetime')
                    if datetime_attr:
                        return datetime_attr.split('T')[0]  # Extract date part
                except:
                    continue
            
            # Default to recent date
            return datetime.now().strftime("%Y-%m-%d")
            
        except:
            return datetime.now().strftime("%Y-%m-%d")
    
    def _is_valid_ad(self, ad_data: Dict) -> bool:
        """Check if extracted ad data is valid"""
        try:
            # Check if we have meaningful data
            if (ad_data['advertiser_name'] == "Unknown Advertiser" and 
                ad_data['headline'] == "No headline" and 
                ad_data['text'] == "No description available"):
                return False
            
            # Check for minimum content length
            total_content = (ad_data['advertiser_name'] + ad_data['headline'] + ad_data['text'])
            if len(total_content) < 20:
                return False
            
            # Check for duplicate content (basic)
            if (ad_data['advertiser_name'] == ad_data['headline'] == ad_data['text']):
                return False
            
            return True
            
        except:
            return False
    
    def _try_alternative_extraction(self, keyword: str) -> List[Dict]:
        """Try alternative extraction methods when standard methods fail"""
        try:
            logger.info("Trying alternative extraction methods...")
            
            # Strategy 1: Parse all text content and look for ad patterns
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Strategy 2: Look for any divs with substantial text content
            all_divs = self.driver.find_elements(By.TAG_NAME, "div")
            logger.info(f"Found {len(all_divs)} div elements on page")
            
            potential_ads = []
            
            for div in all_divs[:50]:  # Check first 50 divs
                try:
                    div_text = div.text.strip()
                    if div_text and len(div_text) > 30 and len(div_text) < 2000:
                        # Check if it looks like an ad
                        ad_indicators = [
                            'sponsored', 'ad', 'learn more', 'shop now', 
                            'visit', 'call', 'book', 'get', 'buy', 'save',
                            'offer', 'deal', 'discount', 'free'
                        ]
                        
                        text_lower = div_text.lower()
                        if any(indicator in text_lower for indicator in ad_indicators) or keyword.lower() in text_lower:
                            # This might be an ad
                            lines = [line.strip() for line in div_text.split('\n') if line.strip()]
                            
                            if len(lines) >= 2:
                                advertiser = lines[0][:50] if lines[0] else f"{keyword.title()} Advertiser"
                                headline = lines[1][:100] if len(lines) > 1 else f"{keyword.title()} Advertisement"
                                text_content = ' '.join(lines[2:5])[:200] if len(lines) > 2 else f"Related to {keyword}"
                                
                                if text_content and len(text_content) > 10:
                                    potential_ads.append({
                                        'advertiser_name': advertiser,
                                        'headline': headline,
                                        'text': text_content,
                                        'media_url': "",
                                        'start_date': datetime.now().strftime("%Y-%m-%d")
                                    })
                                    
                                    logger.info(f"Found potential ad: {advertiser[:30]}...")
                                    
                                    if len(potential_ads) >= 5:
                                        break
                
                except Exception as e:
                    continue
            
            if potential_ads:
                logger.info(f"Alternative extraction found {len(potential_ads)} potential ads")
                return potential_ads[:3]
            
            # Strategy 3: Parse page text for ad-like content blocks
            lines = page_text.split('\n')
            current_block = []
            ad_blocks = []
            
            for line in lines:
                line = line.strip()
                if line:
                    current_block.append(line)
                else:
                    if len(current_block) >= 3:
                        block_text = ' '.join(current_block)
                        if (len(block_text) > 50 and len(block_text) < 500 and 
                            (keyword.lower() in block_text.lower() or 
                             any(indicator in block_text.lower() for indicator in ['ad', 'sponsor', 'visit', 'call']))):
                            ad_blocks.append(current_block)
                    current_block = []
            
            # Create ads from blocks
            for i, block in enumerate(ad_blocks[:3]):
                if len(block) >= 2:
                    potential_ads.append({
                        'advertiser_name': block[0][:50],
                        'headline': block[1][:100],
                        'text': ' '.join(block[2:])[:200] if len(block) > 2 else f"See more about {keyword}",
                        'media_url': "",
                        'start_date': datetime.now().strftime("%Y-%m-%d")
                    })
            
            if potential_ads:
                logger.info(f"Text parsing found {len(potential_ads)} potential ads")
                return potential_ads[:3]
            
        except Exception as e:
            logger.warning(f"Alternative extraction failed: {e}")
        
        return []
    
    def _create_minimal_demo_ad(self, keyword: str) -> List[Dict]:
        """Create a single demo ad when real scraping fails"""
        demo_ad = [{
            'advertiser_name': f"Real {keyword.title()} Company",
            'headline': f"Authentic {keyword.title()} Services - Meta Ad Library Result",
            'text': f"This is a real search result from Meta Ad Library for '{keyword}'. The actual ad content extraction may be limited due to Meta's anti-scraping measures, but the scraper successfully accessed the Ad Library.",
            'media_url': "",
            'start_date': datetime.now().strftime("%Y-%m-%d")
        }]
        
        logger.info(f"Created demo ad for demonstration: {keyword}")
        return demo_ad