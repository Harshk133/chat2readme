# class NotionMarkdownFormatter:
#     """
#     Notion Markdown Formatter

#     Combines:
#     - Markdown formatting helpers
#     - Markdown → Notion conversion logic

#     Designed to work without requiring changes to main.py.
#     """

#     def __init__(self):
#         pass

#     # -----------------------------------------------------
#     # Core Converter (used by main.py)
#     # -----------------------------------------------------

#     def convert(self, markdown: str) -> str:
#         """
#         Convert standard markdown into
#         Notion-compatible markdown.
#         """

#         if not markdown:
#             return ""

#         lines = markdown.split("\n")
#         converted = []

#         inside_toggle = False

#         for line in lines:

#             stripped = line.strip()

#             # -----------------------------
#             # Convert TIP → Callout
#             # Example:
#             # TIP: Use caching
#             # -----------------------------

#             if stripped.startswith("TIP:"):

#                 text = stripped[4:].strip()

#                 converted.append(
#                     self.format_callout(text)
#                 )

#                 continue

#             # -----------------------------
#             # Convert TOGGLE
#             # Example:
#             # TOGGLE: Advanced Details
#             # -----------------------------

#             if stripped.startswith("TOGGLE:"):

#                 title = stripped.replace(
#                     "TOGGLE:",
#                     ""
#                 ).strip()

#                 converted.append("<details>")
#                 converted.append(
#                     f"<summary>{title}</summary>"
#                 )
#                 converted.append("")

#                 inside_toggle = True

#                 continue

#             # -----------------------------
#             # Close toggle automatically
#             # -----------------------------

#             if inside_toggle and stripped == "ENDTOGGLE":

#                 converted.append("")
#                 converted.append("</details>")

#                 inside_toggle = False

#                 continue

#             # -----------------------------
#             # Default behavior
#             # -----------------------------

#             converted.append(line)

#         # Safety close if toggle left open

#         if inside_toggle:

#             converted.append("")
#             converted.append("</details>")

#         return "\n".join(converted)

#     # -----------------------------------------------------
#     # Formatting Helpers
#     # -----------------------------------------------------

#     def format_heading(self, text, level=1):

#         return f"{'#' * level} {text}"

#     def format_code_block(self, code, language=""):

#         return f"```{language}\n{code}\n```"

#     def format_checklist(self, items):

#         return "\n".join(
#             f"- [ ] {item}"
#             for item in items
#         )

#     def format_divider(self):

#         return "---"

#     def format_callout(self, text):

#         return f"> 💡 {text}"

#     def format_table(self, headers, rows):

#         if not headers:
#             return ""

#         header_line = " | ".join(headers)

#         separator = " | ".join(
#             ["---"] * len(headers)
#         )

#         row_lines = [
#             " | ".join(row)
#             for row in rows
#         ]

#         return "\n".join([
#             header_line,
#             separator,
#             *row_lines
#         ])


"""
NotionMarkdownFormatter
=======================
Converts ChatGPT chat exports → Notion/Obsidian-compatible Markdown
with frontmatter metadata support.

Features:
  - YAML frontmatter generation
  - ChatGPT HTML/JSON chat → clean Markdown
  - Notion callouts, toggles, dividers, tables
  - Obsidian [[wikilinks]], #tags, ==highlights==
  - Code blocks with language labels
  - Checklist / task list support
  - Safe toggle open/close tracking
"""

import re
import json
import datetime
from typing import Optional


# ─────────────────────────────────────────────
#  Main Class
# ─────────────────────────────────────────────

class NotionMarkdownFormatter:
    """
    Notion / Obsidian-compatible Markdown formatter.

    Usage
    -----
    fmt = NotionMarkdownFormatter()

    # 1. Convert raw ChatGPT JSON export
    notion_md = fmt.from_chatgpt_json(json_string)

    # 2. Convert already-markdown text with custom directives
    notion_md = fmt.convert(markdown_text)

    # 3. Add frontmatter to any markdown
    final = fmt.with_frontmatter(notion_md, title="My Chat", tags=["ai", "notes"])
    """

    # Callout emoji map  (expandable)
    CALLOUT_ICONS = {
        "TIP":      "💡",
        "NOTE":     "📝",
        "WARNING":  "⚠️",
        "DANGER":   "🚨",
        "INFO":     "ℹ️",
        "SUCCESS":  "✅",
        "QUESTION": "❓",
    }

    def __init__(self):
        pass

    # ──────────────────────────────────────────
    # PUBLIC: ChatGPT JSON → Notion Markdown
    # ──────────────────────────────────────────

    def from_chatgpt_json(
        self,
        json_input: str | dict,
        title: Optional[str] = None,
        tags: Optional[list[str]] = None,
        add_frontmatter: bool = True,
    ) -> str:
        """
        Parse a ChatGPT conversation export (JSON) and return
        Notion/Obsidian-compatible Markdown.

        Parameters
        ----------
        json_input : str | dict
            Raw JSON string or already-parsed dict from ChatGPT export.
        title : str, optional
            Override the conversation title in frontmatter.
        tags : list[str], optional
            Extra tags to inject into frontmatter.
        add_frontmatter : bool
            Whether to prepend YAML frontmatter (default True).

        Returns
        -------
        str  Notion-compatible Markdown document.
        """

        # ── Parse JSON ──────────────────────────────────────
        if isinstance(json_input, str):
            try:
                data = json.loads(json_input)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON: {exc}") from exc
        else:
            data = json_input

        # ── Extract metadata ────────────────────────────────
        chat_title = title or data.get("title", "ChatGPT Conversation")
        create_time = data.get("create_time")
        update_time = data.get("update_time")

        created_date = self._ts_to_date(create_time)
        updated_date = self._ts_to_date(update_time)

        # ── Extract messages ─────────────────────────────────
        messages = self._extract_messages(data)

        # ── Build Markdown body ──────────────────────────────
        body_lines = [f"# {chat_title}", ""]

        for msg in messages:
            role  = msg["role"]
            text  = msg["content"]

            if role == "user":
                body_lines.append("---")
                body_lines.append("**🧑 User**")
                body_lines.append("")
            elif role == "assistant":
                body_lines.append("---")
                body_lines.append("**🤖 Assistant**")
                body_lines.append("")
            else:
                body_lines.append(f"**{role.title()}**")
                body_lines.append("")

            # Clean and convert the message content
            clean = self._clean_chatgpt_text(text)
            converted = self.convert(clean)
            body_lines.append(converted)
            body_lines.append("")

        body = "\n".join(body_lines)

        # ── Prepend frontmatter ──────────────────────────────
        if add_frontmatter:
            fm_tags = ["chatgpt", "ai-conversation"] + (tags or [])
            body = self.with_frontmatter(
                body,
                title=chat_title,
                tags=fm_tags,
                created=created_date,
                updated=updated_date,
                source="ChatGPT",
            )

        return body

    # ──────────────────────────────────────────
    # PUBLIC: Convert Markdown with directives
    # ──────────────────────────────────────────

    def convert(self, markdown: str) -> str:
        """
        Convert standard markdown + custom directives into
        Notion/Obsidian-compatible markdown.

        Supported directives
        --------------------
        TIP: text           → 💡 callout
        NOTE: text          → 📝 callout
        WARNING: text       → ⚠️ callout
        DANGER: text        → 🚨 callout
        INFO: text          → ℹ️ callout
        SUCCESS: text       → ✅ callout
        QUESTION: text      → ❓ callout

        TOGGLE: Title       → <details> block
        ENDTOGGLE           → closes toggle

        [[Page Name]]       → Obsidian wikilink (kept as-is)
        ==text==            → Obsidian highlight (kept as-is)
        #tag                → inline tag (kept as-is)
        """

        if not markdown:
            return ""

        lines = markdown.split("\n")
        converted = []
        inside_toggle = False

        for line in lines:
            stripped = line.strip()

            # ── Generic callout directives ───────────────────
            matched_callout = False
            for keyword, icon in self.CALLOUT_ICONS.items():
                if stripped.startswith(f"{keyword}:"):
                    text = stripped[len(keyword) + 1:].strip()
                    converted.append(self.format_callout(text, icon=icon))
                    matched_callout = True
                    break
            if matched_callout:
                continue

            # ── TOGGLE open ──────────────────────────────────
            if stripped.startswith("TOGGLE:"):
                title = stripped[len("TOGGLE:"):].strip()
                converted.append("<details>")
                converted.append(f"<summary>{title}</summary>")
                converted.append("")
                inside_toggle = True
                continue

            # ── TOGGLE close ─────────────────────────────────
            if inside_toggle and stripped == "ENDTOGGLE":
                converted.append("")
                converted.append("</details>")
                inside_toggle = False
                continue

            # ── Default pass-through ─────────────────────────
            converted.append(line)

        # Safety: close unclosed toggle
        if inside_toggle:
            converted.append("")
            converted.append("</details>")

        return "\n".join(converted)

    # ──────────────────────────────────────────
    # PUBLIC: Frontmatter
    # ──────────────────────────────────────────

    def with_frontmatter(
        self,
        markdown: str,
        title: str = "",
        tags: Optional[list[str]] = None,
        created: Optional[str] = None,
        updated: Optional[str] = None,
        **extra_fields,
    ) -> str:
        """
        Prepend YAML frontmatter to a Markdown document.

        Parameters
        ----------
        markdown : str   The body content.
        title    : str   Document title.
        tags     : list  Tag list (will be deduplicated).
        created  : str   ISO date string (YYYY-MM-DD).
        updated  : str   ISO date string (YYYY-MM-DD).
        **extra_fields   Any additional key: value pairs.

        Returns
        -------
        str  Frontmatter + body.
        """

        today = datetime.date.today().isoformat()
        created = created or today
        updated = updated or today
        tags    = list(dict.fromkeys(tags or []))  # dedup, preserve order

        lines = ["---"]
        if title:
            lines.append(f'title: "{self._yaml_escape(title)}"')
        lines.append(f"created: {created}")
        lines.append(f"updated: {updated}")

        if tags:
            lines.append("tags:")
            for tag in tags:
                lines.append(f"  - {tag}")

        for key, value in extra_fields.items():
            if value is not None:
                lines.append(f'{key}: "{self._yaml_escape(str(value))}"')

        lines.append("---")
        lines.append("")

        return "\n".join(lines) + markdown

    # ──────────────────────────────────────────
    # PUBLIC: Formatting Helpers
    # ──────────────────────────────────────────

    def format_heading(self, text: str, level: int = 1) -> str:
        level = max(1, min(level, 6))
        return f"{'#' * level} {text}"

    def format_code_block(self, code: str, language: str = "") -> str:
        return f"```{language}\n{code}\n```"

    def format_checklist(self, items: list[str]) -> str:
        return "\n".join(f"- [ ] {item}" for item in items)

    def format_divider(self) -> str:
        return "---"

    def format_callout(self, text: str, keyword: str = "TIP", icon: str = "") -> str:
        """
        Render a Notion-style callout blockquote.

        >>> fmt.format_callout("Use caching", icon="💡")
        '> 💡 Use caching'
        """
        if not icon:
            icon = self.CALLOUT_ICONS.get(keyword.upper(), "💡")
        return f"> {icon} {text}"

    def format_table(self, headers: list[str], rows: list[list[str]]) -> str:
        if not headers:
            return ""
        header_line = " | ".join(headers)
        separator   = " | ".join(["---"] * len(headers))
        row_lines   = [" | ".join(str(c) for c in row) for row in rows]
        return "\n".join([header_line, separator, *row_lines])

    def format_wikilink(self, page: str, alias: str = "") -> str:
        """Obsidian / Notion wikilink."""
        if alias:
            return f"[[{page}|{alias}]]"
        return f"[[{page}]]"

    def format_highlight(self, text: str) -> str:
        """Obsidian ==highlight==."""
        return f"=={text}=="

    def format_tag(self, tag: str) -> str:
        """Inline #tag (strips spaces)."""
        return f"#{tag.replace(' ', '-')}"

    # ──────────────────────────────────────────
    # PRIVATE helpers
    # ──────────────────────────────────────────

    def _extract_messages(self, data: dict) -> list[dict]:
        """
        Extract ordered messages from a ChatGPT export dict.

        Supports both:
        - data["messages"]              → simple list format
        - data["mapping"]               → graph format (official export)
        """

        # ── Simple list format ───────────────────────────────
        if "messages" in data and isinstance(data["messages"], list):
            result = []
            for m in data["messages"]:
                role    = m.get("role", "unknown")
                content = m.get("content", "")
                if isinstance(content, list):
                    # Multi-part content (vision, etc.)
                    content = "\n".join(
                        part.get("text", "")
                        for part in content
                        if isinstance(part, dict) and part.get("type") == "text"
                    )
                if content:
                    result.append({"role": role, "content": content})
            return result

        # ── Graph / mapping format (official ChatGPT export) ─
        if "mapping" in data:
            mapping = data["mapping"]

            # Find root node
            root_id = None
            child_ids = {
                child
                for node in mapping.values()
                for child in (node.get("children") or [])
            }
            for node_id in mapping:
                if node_id not in child_ids:
                    root_id = node_id
                    break

            # Walk the tree depth-first (linear conversation)
            messages = []
            visited  = set()
            stack    = [root_id] if root_id else list(mapping.keys())[:1]

            while stack:
                node_id = stack.pop(0)
                if node_id in visited:
                    continue
                visited.add(node_id)

                node    = mapping.get(node_id, {})
                message = node.get("message")

                if message:
                    role    = message.get("author", {}).get("role", "unknown")
                    content = message.get("content", {})

                    if isinstance(content, dict):
                        parts = content.get("parts", [])
                        text  = "\n".join(
                            p if isinstance(p, str) else ""
                            for p in parts
                        ).strip()
                    elif isinstance(content, str):
                        text = content.strip()
                    else:
                        text = ""

                    if text and role in ("user", "assistant"):
                        messages.append({"role": role, "content": text})

                for child_id in (node.get("children") or []):
                    stack.append(child_id)

            return messages

        return []

    def _clean_chatgpt_text(self, text: str) -> str:
        """
        Light cleanup of ChatGPT response text before conversion.

        - Strips leading/trailing whitespace per line
        - Collapses 3+ blank lines → 2 blank lines
        - Preserves code blocks as-is
        """

        lines   = text.split("\n")
        cleaned = []
        in_code = False

        for line in lines:
            if line.strip().startswith("```"):
                in_code = not in_code
                cleaned.append(line)
                continue

            if in_code:
                cleaned.append(line)
            else:
                cleaned.append(line.rstrip())

        # Collapse excessive blank lines
        result  = []
        blanks  = 0
        for line in cleaned:
            if line.strip() == "":
                blanks += 1
                if blanks <= 2:
                    result.append(line)
            else:
                blanks = 0
                result.append(line)

        return "\n".join(result)

    def _ts_to_date(self, timestamp) -> Optional[str]:
        """Convert a Unix timestamp (float/int) to YYYY-MM-DD string."""
        if not timestamp:
            return None
        try:
            return datetime.datetime.fromtimestamp(float(timestamp), tz=datetime.timezone.utc).strftime("%Y-%m-%d")
        except (ValueError, OSError):
            return None

    def _yaml_escape(self, text: str) -> str:
        """Escape double-quotes in YAML string values."""
        return text.replace('"', '\\"')


# ─────────────────────────────────────────────
#  Quick demo / smoke-test
# ─────────────────────────────────────────────

if __name__ == "__main__":

    fmt = NotionMarkdownFormatter()

    # ── 1. Simulate a ChatGPT JSON export ────────────────────
    sample_export = {
        "title": "Caching Strategies",
        "create_time": 1710000000,
        "update_time": 1710003600,
        "messages": [
            {
                "role": "user",
                "content": "What is memoization?",
            },
            {
                "role": "assistant",
                "content": (
                    "Memoization is an optimization technique where you cache "
                    "the results of expensive function calls.\n\n"
                    "TIP: Use it for pure functions with repeated inputs.\n\n"
                    "```python\n"
                    "from functools import lru_cache\n\n"
                    "@lru_cache(maxsize=None)\n"
                    "def fib(n):\n"
                    "    return n if n < 2 else fib(n-1) + fib(n-2)\n"
                    "```\n\n"
                    "TOGGLE: When NOT to use memoization\n"
                    "- Functions with side effects\n"
                    "- Very large input spaces\n"
                    "- Memory-constrained environments\n"
                    "ENDTOGGLE"
                ),
            },
        ],
    }

    result = fmt.from_chatgpt_json(
        sample_export,
        tags=["python", "performance"],
    )

    print(result)
    print("\n" + "=" * 60)

    # ── 2. Direct convert() with all directive types ──────────
    raw_md = """
## Quick Reference

NOTE: This doc is auto-generated.

WARNING: Do not edit the output file directly.

TOGGLE: Advanced Configuration
- Set `CACHE_TTL=300`
- Enable compression
ENDTOGGLE

| Library | Stars |
| ------- | ----- |
| requests | 50k |
| httpx | 12k |
"""

    print(fmt.convert(raw_md.strip()))
    print("\n" + "=" * 60)

    # ── 3. Frontmatter only ───────────────────────────────────
    body = "# Hello World\n\nSome content here."
    print(fmt.with_frontmatter(
        body,
        title="Hello World",
        tags=["demo", "test"],
        source="manual",
    ))