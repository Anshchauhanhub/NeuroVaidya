import time
import os
import gc
from dataclasses import dataclass, asdict
from typing import List, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging

logging.basicConfig(level=logging.INFO)
# Cache the installer result to avoid checking for updates on every search request
_CHROMEDRIVER_PATH = None
logger = logging.getLogger(__name__)

@dataclass
class MedicineResult:
    name: str
    price: str
    mrp: str
    discount: str
    description: str
    manufacturer: str
    rating: str
    composition: str
    image_url: str
    source_url: str
    source_site: str

    def to_dict(self):
        return asdict(self)

class BaseScraper:
    SITE_NAME = "Base"
    SEARCH_URL = ""

    def __init__(self):
        self.driver = None

    def _init_selenium(self):
        """Initializes a stealthy headless Chrome WebDriver."""
        if self.driver is not None:
            return

        options = Options()
        # Use new headless mode for better compatibility and stealth
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--memory-pressure-off")
        options.add_argument("--disk-cache-size=0")
        
        # Use eager load strategy for much faster page rendering (ignores blocking images/css)
        options.page_load_strategy = 'eager'
        
        # Disable images for faster loading and less memory
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        
        # Anti-detection: disable automation flags
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Custom User-Agent to avoid generic bot signatures
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        options.add_argument(f"user-agent={user_agent}")
        
        # Explicitly set Chrome binary path for Render (Linux)
        if os.name == 'posix':
            chrome_path = "/usr/bin/google-chrome"
            if os.path.exists(chrome_path):
                options.binary_location = chrome_path
        
        global _CHROMEDRIVER_PATH
        try:
            if not _CHROMEDRIVER_PATH:
                # Use pre-installed driver on Render/Linux to save 20s startup time
                if os.name == 'posix' and os.path.exists("/usr/local/bin/chromedriver"):
                    _CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"
                    logger.info(f"[{self.SITE_NAME}] Using pre-installed ChromeDriver")
                else:
                    logger.info(f"[{self.SITE_NAME}] Initializing ChromeDriver (via Manager)...")
                    _CHROMEDRIVER_PATH = ChromeDriverManager().install()
            
            # Using the cached ChromeDriver path for speed
            self.driver = webdriver.Chrome(service=Service(_CHROMEDRIVER_PATH), options=options)
            
            # Stealth: Remove navigator.webdriver property
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })
            
            self.driver.set_page_load_timeout(25)
            logger.info(f"[{self.SITE_NAME}] Stealth Selenium initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Stealth Selenium for {self.SITE_NAME}: {e}")
            self.driver = None


    def _quit_selenium(self):
        """Quits the WebDriver and forces garbage collection."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
        
        # Explicitly collect garbage to free up memory on Render
        gc.collect()
            
    def _get_valid_image(self, img_el) -> str:
        """Extract a real product image from an img element, ignoring placeholders."""
        if not img_el:
            return ""
        
        # Check attributes in order of preference for high-res/lazy-loaded
        for attr in ['srcset', 'data-src', 'data-original', 'src']:
            val = img_el.get(attr)
            if not val:
                continue
                
            urls = []
            if attr == 'srcset':
                # e.g., "url1 1x, url2 2x"
                urls = [part.strip().split(' ')[0] for part in val.split(',')]
            else:
                urls = [val]
                
            for u in urls:
                if not u or not u.startswith('http'):
                    continue
                # Ignore common placeholders
                u_lower = u.lower()
                if '.svg' in u_lower or 'placeholder' in u_lower or 'default' in u_lower or 'logo' in u_lower:
                    continue
                
                # Upgrade image resolution if CDN sizing parameters exist
                import re
                u = re.sub(r'w_\d+,h_\d+', 'w_600,h_600', u)  # Tata 1mg
                u = re.sub(r'dim=\d+x\d+', 'dim=700x700', u)  # PharmEasy
                u = re.sub(r'q=\d+', 'q=100', u)              # Enhance quality parameter
                
                return u
        return ""

    def _selenium_get(self, url: str, wait_seconds: int = 5) -> str:
        """Fetches a URL using Selenium and returns the HTML source."""
        self._init_selenium()
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        
        logger.info(f"[{self.SITE_NAME}] Fetching: {url}")
        self.driver.get(url)
        time.sleep(wait_seconds)  # Wait for JS to render
        return self.driver.page_source



    def _get_soup(self, html: str) -> BeautifulSoup:
        """Parses HTML into a BeautifulSoup object."""
        return BeautifulSoup(html, "lxml")

    def search(self, query: str, max_results: int = 5, wait_seconds: int = 3) -> List[MedicineResult]:
        """Must be implemented by subclasses."""
        raise NotImplementedError
