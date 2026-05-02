class NotionMarkdownFormatter:
    """
    Notion Markdown Formatter

    Combines:
    - Markdown formatting helpers
    - Markdown → Notion conversion logic

    Designed to work without requiring changes to main.py.
    """

    def __init__(self):
        pass

    # -----------------------------------------------------
    # Core Converter (used by main.py)
    # -----------------------------------------------------

    def convert(self, markdown: str) -> str:
        """
        Convert standard markdown into
        Notion-compatible markdown.
        """

        if not markdown:
            return ""

        lines = markdown.split("\n")
        converted = []

        inside_toggle = False

        for line in lines:

            stripped = line.strip()

            # -----------------------------
            # Convert TIP → Callout
            # Example:
            # TIP: Use caching
            # -----------------------------

            if stripped.startswith("TIP:"):

                text = stripped[4:].strip()

                converted.append(
                    self.format_callout(text)
                )

                continue

            # -----------------------------
            # Convert TOGGLE
            # Example:
            # TOGGLE: Advanced Details
            # -----------------------------

            if stripped.startswith("TOGGLE:"):

                title = stripped.replace(
                    "TOGGLE:",
                    ""
                ).strip()

                converted.append("<details>")
                converted.append(
                    f"<summary>{title}</summary>"
                )
                converted.append("")

                inside_toggle = True

                continue

            # -----------------------------
            # Close toggle automatically
            # -----------------------------

            if inside_toggle and stripped == "ENDTOGGLE":

                converted.append("")
                converted.append("</details>")

                inside_toggle = False

                continue

            # -----------------------------
            # Default behavior
            # -----------------------------

            converted.append(line)

        # Safety close if toggle left open

        if inside_toggle:

            converted.append("")
            converted.append("</details>")

        return "\n".join(converted)

    # -----------------------------------------------------
    # Formatting Helpers
    # -----------------------------------------------------

    def format_heading(self, text, level=1):

        return f"{'#' * level} {text}"

    def format_code_block(self, code, language=""):

        return f"```{language}\n{code}\n```"

    def format_checklist(self, items):

        return "\n".join(
            f"- [ ] {item}"
            for item in items
        )

    def format_divider(self):

        return "---"

    def format_callout(self, text):

        return f"> 💡 {text}"

    def format_table(self, headers, rows):

        if not headers:
            return ""

        header_line = " | ".join(headers)

        separator = " | ".join(
            ["---"] * len(headers)
        )

        row_lines = [
            " | ".join(row)
            for row in rows
        ]

        return "\n".join([
            header_line,
            separator,
            *row_lines
        ])