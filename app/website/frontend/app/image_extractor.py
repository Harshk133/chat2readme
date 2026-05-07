"""
chatgpt_images_to_readme.py

Extract all AI-generated images from a ChatGPT shared conversation JSON
and write them into a README.md with inline image display.

Usage:
    python chatgpt_images_to_readme.py <input.json> [output.md]

How ChatGPT stores images in the JSON:
    content.parts[].content_type == "image_asset_pointer"
    content.parts[].asset_pointer == "sediment://file_XXXX?shared_conversation_id=YYY"

Public image URL pattern (works without login for shared conversations):
    https://files.oaiusercontent.com/{file_id}?se=shared&sp=r&spr=https
    &sv=2021-08-06&sr=b&shared_conversation_id={conv_id}
"""

import json
import re
import sys
from pathlib import Path


# ------------------------------------------------------------------
# Step 1: Extract all image_asset_pointer entries from the JSON
# ------------------------------------------------------------------

def extract_images(data: dict) -> list:
    """
    Recursively walk the JSON and collect every image_asset_pointer.

    Returns a list of dicts:
      - file_id       : "file_0000000021a87208903a6e5f919c85f8"
      - conv_id       : shared_conversation_id from the asset pointer
      - gen_id        : DALL-E generation ID
      - prompt        : image generation prompt (may be empty)
      - title         : async_task_title from the parent message metadata
      - width/height  : pixel dimensions
      - size_bytes    : file size
      - orientation   : "landscape" / "portrait" / "square"
      - is_error      : True if the image generation failed (skip these)
    """
    images = []
    # Map response_message_id -> title from async_task_title
    titles = {}
    # Map response_message_id -> is_error
    errors = set()

    # ---- First pass: collect titles and error flags ----
    def find_meta(obj, depth=0):
        if depth > 12 or not isinstance(obj, (dict, list)):
            return
        if isinstance(obj, dict):
            meta = obj.get("metadata", {})
            if meta:
                resp_id = meta.get("response_message_id", "")
                t = meta.get("async_task_title") or meta.get("image_gen_title", "")
                if t and resp_id:
                    titles[resp_id] = t
                if meta.get("is_error") and resp_id:
                    errors.add(resp_id)
            for v in obj.values():
                find_meta(v, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                find_meta(item, depth + 1)

    find_meta(data)

    # ---- Second pass: collect image pointers ----
    def walk(obj, depth=0):
        if depth > 12 or not isinstance(obj, (dict, list)):
            return
        if isinstance(obj, dict):
            if obj.get("content_type") == "image_asset_pointer":
                asset = obj.get("asset_pointer", "")

                # Parse file_id from "sediment://file_XXX?shared_conversation_id=YYY"
                m_file = re.search(r"sediment://(file_[a-f0-9]+)", asset)
                m_conv = re.search(r"shared_conversation_id=([a-f0-9\-]+)", asset)

                file_id = m_file.group(1) if m_file else None
                conv_id = m_conv.group(1) if m_conv else data.get("conversation_id", "")

                if not file_id:
                    return

                dalle = obj.get("metadata", {}).get("dalle", {})
                gen   = obj.get("metadata", {}).get("generation", {})

                images.append({
                    "file_id":     file_id,
                    "conv_id":     conv_id,
                    "gen_id":      dalle.get("gen_id") or gen.get("gen_id", ""),
                    "prompt":      dalle.get("prompt", "").strip(),
                    "title":       titles.get(file_id, ""),
                    "width":       obj.get("width", 0),
                    "height":      obj.get("height", 0),
                    "size_bytes":  obj.get("size_bytes", 0),
                    "orientation": gen.get("orientation", ""),
                    "is_error":    file_id in errors,
                })
                return  # don't recurse inside image pointer

            for v in obj.values():
                walk(v, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                walk(item, depth + 1)

    walk(data)

    # Remove duplicates (same file_id can appear in both mapping + linear_conversation)
    seen = set()
    unique = []
    for img in images:
        if img["file_id"] not in seen:
            seen.add(img["file_id"])
            unique.append(img)

    return unique


# ------------------------------------------------------------------
# Step 2: Build the public image URL
# ------------------------------------------------------------------

def build_image_url(file_id: str, conv_id: str) -> str:
    """
    Construct the publicly accessible image URL for a shared conversation.
    This URL works without login as long as the conversation is public.
    """
    base = "https://files.oaiusercontent.com"
    params = (
        f"se=shared"
        f"&sp=r"
        f"&spr=https"
        f"&sv=2021-08-06"
        f"&sr=b"
        f"&shared_conversation_id={conv_id}"
    )
    return f"{base}/{file_id}?{params}"


# ------------------------------------------------------------------
# Step 3: Build the README
# ------------------------------------------------------------------

def build_readme(images: list, chat_title: str = "") -> str:
    heading = chat_title.strip() or "ChatGPT Generated Images"

    # Filter out error images
    valid   = [img for img in images if not img["is_error"]]
    errored = [img for img in images if img["is_error"]]

    lines = [
        f"# {heading}",
        "",
        f"> Images generated by ChatGPT in this conversation.",
        f"> Total images: **{len(valid)}**",
        "",
        "---",
        "",
    ]

    if not valid:
        lines.append("*No successfully generated images found in this conversation.*")
        if errored:
            lines += ["", f"*({len(errored)} image(s) failed to generate.)*"]
        return "\n".join(lines)

    for i, img in enumerate(valid, 1):
        url   = build_image_url(img["file_id"], img["conv_id"])
        title = img["title"] or img["prompt"] or f"Image {i}"
        w, h  = img["width"], img["height"]
        size_kb = round(img["size_bytes"] / 1024)

        lines += [
            f"## {i}. {title}",
            "",
            f"![{title}]({url})",
            "",
        ]

        # Metadata table
        lines += [
            "| Field | Value |",
            "|-------|-------|",
            f"| File ID | `{img['file_id']}` |",
            f"| Dimensions | {w} × {h} px |",
            f"| Orientation | {img['orientation'] or 'N/A'} |",
            f"| File size | {size_kb} KB |",
        ]
        if img["prompt"]:
            lines.append(f"| Prompt | {img['prompt']} |")
        if img["gen_id"]:
            lines.append(f"| Generation ID | `{img['gen_id']}` |")

        lines += ["", f"[Direct link]({url})", "", "---", ""]

    if errored:
        lines += [
            "## Failed Generations",
            "",
            f"*{len(errored)} image(s) were blocked or failed:*",
            "",
        ]
        for img in errored:
            lines.append(f"- `{img['file_id']}` — generation failed")
        lines.append("")

    lines += [
        "---",
        "",
        "*Auto-generated by `chatgpt_images_to_readme.py`*",
        "",
    ]

    return "\n".join(lines)


# ------------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python chatgpt_images_to_readme.py <input.json> [output.md]")
        sys.exit(1)

    input_path  = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.with_suffix(".md")

    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    print(f"Reading:   {input_path}")
    data = json.loads(input_path.read_text(encoding="utf-8"))

    chat_title = data.get("title", "")
    images     = extract_images(data)

    print(f"Found:     {len(images)} image(s)")
    for img in images:
        status = "ERROR" if img["is_error"] else "OK   "
        print(f"  [{status}] {img['file_id']}  {img['width']}x{img['height']}  {img['title'] or img['prompt'] or '(no title)'}")

    readme = build_readme(images, chat_title)
    output_path.write_text(readme, encoding="utf-8")
    print(f"Written:   {output_path}")


if __name__ == "__main__":
    main()