from extractor import extract_messages

def to_markdown(data: dict) -> str:
    title = data.get("title", "ChatGPT Conversation")
    messages = extract_messages(data)

    role_labels = {
        "user": "### 🧑 User",
        "assistant": "### 🤖 Assistant",
        "system": "### ⚙️ System",
    }

    lines = [f"# {title}\n"]
    for msg in messages:
        label = role_labels.get(msg["role"], f"### {msg['role'].capitalize()}")
        lines.append(label)
        lines.append(msg["content"])
        lines.append("")

    return "\n".join(lines)