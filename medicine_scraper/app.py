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
    
    # Run scrapers one by one to save memory on Render
    # This prevents multiple Chrome processes from running at the same time
    for scraper in SCRAPERS:
        try:
            print(f"DEBUG: Running {scraper.SITE_NAME} scraper...")
            data = run_scraper(scraper, query, limit)
            all_results.extend(data)
        except Exception as exc:
            print(f"{scraper.SITE_NAME} generated an exception: {exc}")

    # Store in Cache
    _CACHE[query] = {
        "timestamp": now,
        "results": all_results
    }

    return jsonify({
        "query": query,
        "count": len(all_results),
        "results": all_results,
        "cached": False
    })

if __name__ == "__main__":
    app.run(port=5000, debug=True)
