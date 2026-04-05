import requests
from bs4 import BeautifulSoup

def test_requests_scraper(site_name, url):
    print(f"--- Testing {site_name} with requests ---")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Check for data presence
            text = soup.get_text()
            if "dolo" in text.lower():
                print("Success: Data found in HTML")
                # Look for cards
                cards = soup.select("a.noAnchorColor.width-100") or soup.select("a[class*='ProductCard']")
                print(f"Found {len(cards)} cards with simple BS4")
            else:
                print("Fail: Keyword not found, likely bot protection or JS required")
        else:
            print(f"Fail: Status {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_requests_scraper("Tata1mg", "https://www.1mg.com/search/all?name=dolo")
    test_requests_scraper("PharmEasy", "https://pharmeasy.in/search/all?name=dolo")
