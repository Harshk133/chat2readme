
from flask import Flask, request, jsonify
from flask_cors import CORS

from main import append_links_section
from fetcher import fetch_chatgpt_share
from markdowns import to_markdown
from links_extractor import extract_urls_from_json
import os

app = Flask(__name__)   # ← Only ONE app

CORS(
    app,
    origins=[
        "https://chat2readme-o3fv.vercel.app",
        "http://localhost:3000"
    ],
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"]
)

@app.route("/")
def home():
    return jsonify({"message": "Backend Working"})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})
@app.route("/convert", methods=["POST", "OPTIONS"])
def convert():
    if request.method == "OPTIONS":
        return jsonify({"message": "OPTIONS works"}), 200

    try:
        body = request.json

        if not body or not body.get("url"):
            return jsonify({"error": "Missing URL"}), 400

        url = body.get("url")

        print(f"Received URL: {url}") 
        # TEMP DEBUG - remove after fixing
        api_key = os.environ.get("SCRAPER_API_KEY")
        print(f"SCRAPER_API_KEY present: {bool(api_key)}")
        print(f"SCRAPER_API_KEY value: {api_key[:5] if api_key else 'NOT SET'}")

        data = fetch_chatgpt_share(url)
        markdown = to_markdown(data)
        links = {}

        try:
            links = extract_urls_from_json(data)
        except Exception as e:
            print(f"Link extraction failed: {e}")

        if body.get("include_links", True):
            markdown = append_links_section(markdown, links)

        return jsonify({
            "markdown": markdown,
            "links": len(links)
        })

    except Exception as e:
        print(f"Convert error: {e}")                        
        return jsonify({"error": str(e)}), 500              

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
