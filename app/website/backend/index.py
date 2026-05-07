from flask import Flask, request, jsonify
from flask_cors import CORS

from main import append_links_section
from fetcher import fetch_chatgpt_share
from markdowns import to_markdown
from links_extractor import extract_urls_from_json

app = Flask(__name__)
# CORS CONFIG
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "https://chat2readme-o3fv.vercel.app"
            ]
        }
    }
)

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Backend Working"
    })

@app.route("/convert", methods=["POST"])
def convert():
    body = request.json
    url = body.get("url")

    data = fetch_chatgpt_share(url)

    markdown = to_markdown(data)

    links = {}

    try:
        links = extract_urls_from_json(data)
    except:
        pass

    if body.get("include_links", True):
        markdown = append_links_section(markdown, links)

    return jsonify({
        "markdown": markdown,
        "links": len(links)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)