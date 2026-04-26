def extract_messages(data: dict) -> list:
    messages = []
    mapping = data.get("mapping", {})

    def walk(node_id):
        node = mapping.get(node_id, {})
        msg = node.get("message")
        if msg and msg.get("content"):
            parts = msg["content"].get("parts", [])
            text = " ".join(p for p in parts if isinstance(p, str)).strip()
            if text:
                messages.append({
                    "role": msg["author"]["role"],
                    "content": text,
                })
        for child_id in node.get("children", []):
            walk(child_id)

    root_id = next(
        (nid for nid, n in mapping.items() if n.get("parent") is None), None
    )
    if root_id:
        walk(root_id)

    return messages