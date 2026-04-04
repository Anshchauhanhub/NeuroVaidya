import time
from dataclasses import dataclass, asdict
from typing import List, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging

logging.basicConfig(level=logging.INFO)
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
        """Initializes a headless Chrome WebDriver."""
        if self.driver is not None:
            return

        try:
            import undetected_chromedriver as uc
            options = uc.ChromeOptions()
            options.headless = True
            
            # Additional arguments for stability
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            self.driver = uc.Chrome(options=options)
            self.driver.set_page_load_timeout(20)
            return
        except ImportError:
            logger.warning("undetected-chromedriver not found, falling back to standard selenium")
        except Exception as e:
            logger.warning(f"uc.Chrome failed: {e}, falling back to standard selenium")

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Suppress webdriver manager logs
        import os
        os.environ["WDM_LOG"] = "0"
        
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.driver.set_page_load_timeout(20)
        except Exception as e:
            logger.error(f"Failed to initialize Selenium for {self.SITE_NAME}: {e}")
            self.driver = None

    def _quit_selenium(self):
        """Quits the WebDriver if it exists."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
            
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

    def search(self, query: str, max_results: int = 10) -> List[MedicineResult]:
        """Must be implemented by subclasses."""
        raise NotImplementedError
