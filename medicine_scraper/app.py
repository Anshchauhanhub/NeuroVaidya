from flask import Flask, request, jsonify
from flask_cors import CORS
from scrapers import (
    Tata1mgScraper, PharmEasyScraper
)
import concurrent.futures

app = Flask(__name__)
CORS(app)

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
    query = request.args.get("q", "")
    limit = int(request.args.get("limit", 5))

    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    all_results = []
    
    # Run scrapers concurrently using a thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(SCRAPERS)) as executor:
        futures = {executor.submit(run_scraper, scraper, query, limit): scraper for scraper in SCRAPERS}
        for future in concurrent.futures.as_completed(futures):
            scraper = futures[future]
            try:
                data = future.result()
                all_results.extend(data)
            except Exception as exc:
                print(f"{scraper.SITE_NAME} generated an exception: {exc}")

    return jsonify({
        "query": query,
        "count": len(all_results),
        "results": all_results
    })

if __name__ == "__main__":
    app.run(port=5000, debug=True)
