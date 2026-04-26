
# import json
# import sys
# from fetcher import fetch_chatgpt_share
# from markdowns import to_markdown
# from links_extractor import extract_urls_from_json
# import shutil
# import os


# if __name__ == "__main__":
#     url = sys.argv[1] if len(sys.argv) > 1 else \
#         "https://chatgpt.com/share/69ecfbba-0344-8323-9451-3ca4d223069b"

#     print(f"Fetching: {url}")
#     data = fetch_chatgpt_share(url)

#     os.makedirs("json", exist_ok=True)
#     os.makedirs("readmes", exist_ok=True)

#     with open(f"chat_raw{url[26:]}.json", "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

#     shutil.move(f"chat_raw{url[26:]}.json", f'json/chat_raw{url[26:]}.json')

#     print("✅ Saved → chat_raw.json")

#     md = to_markdown(data)
#     with open(f"README{url[26:]}.md", "w", encoding="utf-8") as f:
#         f.write(md)

#     shutil.move(f"README{url[26:]}.md", f'readmes/README{url[26:]}.md')
#     print("✅ Saved → README.md")



import json
import sys
import shutil
import os

from fetcher import fetch_chatgpt_share
from markdowns import to_markdown
from links_extractor import extract_urls_from_json


# ---------------------------------------------------------
# Helper: Extract Share ID Safely
# ---------------------------------------------------------

def get_share_id(url: str) -> str:
    """
    Extract share ID from URL.

    Example:
        https://chatgpt.com/share/abc123

    Returns:
        abc123
    """

    return url.rstrip("/").split("/")[-1]


# ---------------------------------------------------------
# Helper: Append Links to Markdown
# ---------------------------------------------------------

def append_links_section(markdown: str, links: dict) -> str:
    """
    Append references section only if links exist.
    """

    if not links:
        print("No links detected — skipping references section")
        return markdown

    print(f"Links detected: {len(links)}")

    lines = []

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## References")
    lines.append("")

    for url, info in links.items():

        title = info.get("title") or url
        snippet = info.get("snippet")

        lines.append(f"- [{title}]({url})")

        if snippet:
            lines.append(f"  - {snippet}")

    lines.append("")

    return markdown + "\n".join(lines)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    url = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "https://chatgpt.com/share/69ecfbba-0344-8323-9451-3ca4d223069b"
    )

    print(f"Fetching: {url}")

    data = fetch_chatgpt_share(url)

    share_id = get_share_id(url)

    # -----------------------------------------------------
    # Ensure folders exist
    # -----------------------------------------------------

    os.makedirs("json", exist_ok=True)
    os.makedirs("readmes", exist_ok=True)

    # -----------------------------------------------------
    # Save raw JSON
    # -----------------------------------------------------

    json_path = f"json/chat_raw_{share_id}.json"

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved → {json_path}")

    # -----------------------------------------------------
    # Generate Markdown from chat
    # -----------------------------------------------------

    markdown = to_markdown(data)

    # -----------------------------------------------------
    # Extract links safely
    # -----------------------------------------------------

    try:

        links = extract_urls_from_json(data)

    except Exception as e:

        print("Link extraction skipped:", e)
        links = {}

    # -----------------------------------------------------
    # Append links to markdown if present
    # -----------------------------------------------------

    markdown = append_links_section(
        markdown,
        links
    )

    # -----------------------------------------------------
    # Save README
    # -----------------------------------------------------

    readme_path = f"readmes/README_{share_id}.md"

    with open(
        readme_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(markdown)

    print(f"Saved → {readme_path}")