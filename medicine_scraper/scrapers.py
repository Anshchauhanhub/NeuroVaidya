import re
import urllib.parse
from typing import List
from scraper_base import BaseScraper, MedicineResult, logger

class Tata1mgScraper(BaseScraper):
    SITE_NAME = "Tata 1mg"
    SEARCH_URL = "https://www.1mg.com/search/all?name={query}"

    def search(self, query: str, max_results: int = 10) -> List[MedicineResult]:
        results = []
        url = self.SEARCH_URL.format(query=urllib.parse.quote(query))
        logger.info(f"[{self.SITE_NAME}] Searching: {url}")

        try:
            html = self._selenium_get(url, wait_seconds=2)
            soup = self._get_soup(html)

            cards = soup.select("a.noAnchorColor.width-100")
            if not cards:
                cards = soup.select("a[href*='/otc/'], a[href*='/drugs/']")

            logger.info(f"[{self.SITE_NAME}] Found {len(cards)} product cards")

            for i, card in enumerate(cards[:max_results]):
                try:
                    logger.debug(f"[{self.SITE_NAME}] Card {i} HTML snippet: {str(card)[:200]}...")
                    result = self._parse_card(card)
                    if result:
                        results.append(result)
                    else:
                        logger.warning(f"[{self.SITE_NAME}] Card {i} parsed to None (likely missing name)")
                except Exception as e:
                    logger.error(f"[{self.SITE_NAME}] Error parsing card {i}: {e}")
                    continue

        except Exception as e:
            logger.error(f"[{self.SITE_NAME}] Scraping failed: {e}")
        finally:
            self._quit_selenium()

        return results

    def _parse_card(self, card) -> MedicineResult:
        href = card.get("href", "")
        source_url = href if href.startswith("http") else f"https://www.1mg.com{href}"

        image_url = ""
        img_name = ""
        img = card.select_one("img")
        if img:
            image_url = self._get_valid_image(img)
            img_name = img.get("alt", "") or img.get("title", "") or ""

        name = ""
        header = card.select_one("div[class*='VerticalProductTile__header']")
        if header:
            name = header.get_text(strip=True)
        if not name:
            name = img_name

        description = ""
        pack_div = card.select_one("div.xSmallRegular.textSecondary")
        if pack_div:
            description = pack_div.get_text(strip=True)

        price = ""
        price_span = card.select_one("span.l5Medium")
        if price_span:
            price_text = price_span.get_text(strip=True)
            hidden = price_span.select_one("span.visuallyHidden")
            if hidden:
                hidden_text = hidden.get_text(strip=True)
                price_text = price_text.replace(hidden_text, "").strip()
            price = price_text

        if not price:
            for span in card.select("span"):
                text = span.get_text(strip=True)
                match = re.search(r"₹[\d,.]+", text)
                if match:
                    price = match.group(0)
                    break

        mrp = ""
        strike = card.select_one("strike")
        if strike:
            hidden = strike.select_one("span.visuallyHidden")
            mrp_text = strike.get_text(strip=True)
            if hidden:
                mrp_text = mrp_text.replace(hidden.get_text(strip=True), "").strip()
            match = re.search(r"₹?[\d,.]+", mrp_text)
            if match:
                mrp = "₹" + match.group(0).lstrip("₹")

        discount = ""
        disc_span = card.select_one("span.successColor")
        if disc_span:
            hidden = disc_span.select_one("span.visuallyHidden")
            disc_text = disc_span.get_text(strip=True)
            if hidden:
                disc_text = disc_text.replace(hidden.get_text(strip=True), "").strip()
            if disc_text:
                discount = disc_text

        rating = ""
        rating_els = card.select("span[class*='textSecondary']")
        for el in rating_els:
            txt = el.get_text(strip=True)
            if re.match(r"^\d\.\d", txt):
                rating = txt
                break
        
        if not name:
            return None

        return MedicineResult(
            name=name, price=price, mrp=mrp, discount=discount, description=description,
            manufacturer="", rating=rating, composition="", image_url=image_url,
            source_url=source_url, source_site=self.SITE_NAME,
        )


class PharmEasyScraper(BaseScraper):
    SITE_NAME = "PharmEasy"
    SEARCH_URL = "https://pharmeasy.in/search/all?name={query}"

    def search(self, query: str, max_results: int = 10) -> List[MedicineResult]:
        results = []
        url = self.SEARCH_URL.format(query=urllib.parse.quote(query))
        logger.info(f"[{self.SITE_NAME}] Searching: {url}")

        try:
            html = self._selenium_get(url, wait_seconds=2)
            soup = self._get_soup(html)
            
            cards = soup.select("a[class*='ProductCard_medicineUnitWrapper']")
            if not cards:
                cards = soup.select("div[class*='ProductCard_medicineUnitContainer']")
                
            logger.info(f"[{self.SITE_NAME}] Found {len(cards)} product cards")

            for card in cards[:max_results]:
                try:
                    name_el = card.select_one("div[class*='name'] h1, h1[class*='name'], h2[class*='name']") or card.select_one("h1, h2, h3")
                    if not name_el: continue
                    name = name_el.get_text(strip=True)
                    
                    price_el = card.select_one("div[class*='ourPrice']") or card.select_one("div[class*='price'], span[class*='price']")
                    price = price_el.get_text(strip=True) if price_el else ""
                    
                    mrp_el = card.select_one("div[class*='originalMrp'], span[class*='striked']") or card.select_one("strike, del, div[class*='mrp']")
                    mrp = mrp_el.get_text(strip=True) if mrp_el else ""
                    
                    discount_el = card.select_one("span[class*='DiscountPercent']")
                    discount = discount_el.get_text(strip=True) if discount_el else ""
                    
                    brand_el = card.select_one("div[class*='brandName']")
                    manufacturer = brand_el.get_text(strip=True).replace("By ", "") if brand_el else ""
                    
                    img_el = card.select_one("img")
                    img = self._get_valid_image(img_el)
                    
                    href = card.get("href")
                    if not href:
                        link_el = card.find_parent("a") or card.select_one("a")
                        href = link_el.get("href") if link_el else ""
                    source = href if href.startswith("http") else f"https://pharmeasy.in{href}"

                    results.append(MedicineResult(
                        name=name, price=price, mrp=mrp, discount=discount, description="",
                        manufacturer=manufacturer, rating="", composition="", image_url=img,
                        source_url=source, source_site=self.SITE_NAME
                    ))
                except Exception as e:
                    logger.warning(f"[{self.SITE_NAME}] Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.error(f"[{self.SITE_NAME}] Error: {e}")
        finally:
            self._quit_selenium()
            
        return results
