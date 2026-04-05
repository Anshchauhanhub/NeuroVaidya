import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from scrapers import (
    Tata1mgScraper, PharmEasyScraper
)
import concurrent.futures
import time

app = Flask(__name__)
CORS(app)

# Simple in-memory cache
# Format: { "query": { "timestamp": float, "results": list } }
_CACHE = {}
_CACHE_EXPIRY_SECONDS = 3600  # 1 hour

SCRAPERS = [
    Tata1mgScraper(),
    PharmEasyScraper(),
]

def run_scraper(scraper, query, limit):
    try:
        results = scraper.search(query, max_results=limit)
        return [r.to_dict() for r in results]
    except Exception as e:
        print(f"Error in {scraper.SITE_NAME}: {e}")
        return []

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "medicine_scraper"}), 200

@app.route("/debug", methods=["GET"])
def debug_info():
    """Environment diagnostics for Render/Linux."""
    import os
    import shutil
    chrome_path = "/usr/bin/google-chrome"
    return jsonify({
        "os": os.name,
        "platform": __import__("platform").system(),
        "chrome_exists": os.path.exists(chrome_path),
        "chrome_in_path": shutil.which("google-chrome") is not None,
        "working_dir": os.getcwd(),
        "files": os.listdir(".")
    }), 200

@app.route("/api/search", methods=["GET"])
def search_medicines():
    query = request.args.get("q", "").strip().lower()
    limit = int(request.args.get("limit", 5))

    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    # Cache Check
    now = time.time()
    if query in _CACHE:
        entry = _CACHE[query]
        if now - entry["timestamp"] < _CACHE_EXPIRY_SECONDS:
            print(f"DEBUG: Returning cached results for '{query}'")
            return jsonify({
                "query": query,
                "count": len(entry["results"]),
                "results": entry["results"],
                "cached": True
            })

    all_results = []
    
    # Smart Execution: use parallel scraping locally (Fast), sequential on Render (Memory-Safe)
    IS_RENDER = os.environ.get("RENDER") == "true"
    
    if IS_RENDER:
        # Run scrapers one by one to save memory on Render
        for scraper in SCRAPERS:
            try:
                print(f"DEBUG: Running {scraper.SITE_NAME} scraper (Sequential Mode)...")
                data = run_scraper(scraper, query, limit)
                all_results.extend(data)
            except Exception as exc:
                print(f"{scraper.SITE_NAME} generated an exception: {exc}")
    else:
        # Run scrapers in parallel for maximum speed on local machine
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(SCRAPERS)) as executor:
            print(f"DEBUG: Running scrapers in Parallel Mode for speed...")
            futures = {executor.submit(run_scraper, scraper, query, limit): scraper for scraper in SCRAPERS}
            for future in concurrent.futures.as_completed(futures):
                scraper = futures[future]
                try:
                    data = future.result()
                    all_results.extend(data)
                except Exception as exc:
                    print(f"{scraper.SITE_NAME} generated an exception: {exc}")

    # Store in Cache only if we found results (don't cache empty results or errors)
    if all_results:
        _CACHE[query] = {
            "timestamp": now,
            "results": all_results
        }
    else:
        print(f"DEBUG: No results found for '{query}', not caching.")

    return jsonify({
        "query": query,
        "count": len(all_results),
        "results": all_results,
        "cached": False
    })

def warmup_scrapers():
    """Warms up the Chrome driver on startup to save time on the first request."""
    if os.environ.get("RENDER") == "true":
        print("DEBUG: Pre-warming scraper environment...")
        try:
            s = Tata1mgScraper()
            s._init_selenium()
            s._quit_selenium()
            print("DEBUG: Scraper environment warmed up successfully.")
        except Exception as e:
            print(f"DEBUG: Scraper warmup failed (this is expected in some build environments): {e}")

if __name__ == "__main__":
    warmup_scrapers()
    app.run(port=5000, debug=True)
