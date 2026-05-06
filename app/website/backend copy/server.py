from flask import Flask, request, jsonify
from flask_cors import CORS

from main import append_links_section
from fetcher import fetch_chatgpt_share
from markdowns import to_markdown
from links_extractor import extract_urls_from_json

app = Flask(__name__)
CORS(app)

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
    app.run(debug=True, port=5000)