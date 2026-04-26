
import json
import sys
from fetcher import fetch_chatgpt_share
from markdowns import to_markdown
import shutil
import os


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else \
        "https://chatgpt.com/share/69ecfbba-0344-8323-9451-3ca4d223069b"

    print(f"Fetching: {url}")
    data = fetch_chatgpt_share(url)

    os.makedirs("json", exist_ok=True)
    os.makedirs("readmes", exist_ok=True)

    with open(f"chat_raw{url[26:]}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    shutil.move(f"chat_raw{url[26:]}.json", f'json/chat_raw{url[26:]}.json')
    print("✅ Saved → chat_raw.json")

    md = to_markdown(data)
    with open(f"README{url[26:]}.md", "w", encoding="utf-8") as f:
        f.write(md)

    shutil.move(f"README{url[26:]}.md", f'readmes/README{url[26:]}.md')
    print("✅ Saved → README.md")

