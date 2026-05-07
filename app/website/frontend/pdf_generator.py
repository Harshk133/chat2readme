# pdf_generator.py

import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, ListFlowable, ListItem
)


# ---------------------------------------------------------
# Markdown → ReportLab elements converter
# ---------------------------------------------------------

def _escape_xml(text: str) -> str:
    """Escape characters that break ReportLab's XML parser."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _inline_styles(text: str) -> str:
    """Convert inline markdown (bold, italic, code) to ReportLab tags."""
    # Bold+italic
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<b><i>\1</i></b>", text)
    # Bold
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    # Italic
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    # Inline code
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    return text


def _build_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "ChatTitle",
            parent=base["Title"],
            fontSize=20,
            leading=26,
            spaceAfter=10,
            textColor=colors.HexColor("#1a1a2e"),
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontSize=14,
            leading=18,
            spaceBefore=12,
            spaceAfter=4,
            textColor=colors.HexColor("#16213e"),
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontSize=12,
            leading=16,
            spaceBefore=8,
            spaceAfter=3,
            textColor=colors.HexColor("#0f3460"),
        ),
        "user_label": ParagraphStyle(
            "UserLabel",
            parent=base["Normal"],
            fontSize=11,
            leading=15,
            spaceBefore=12,
            spaceAfter=3,
            textColor=colors.HexColor("#2563eb"),
            fontName="Helvetica-Bold",
        ),
        "assistant_label": ParagraphStyle(
            "AssistantLabel",
            parent=base["Normal"],
            fontSize=11,
            leading=15,
            spaceBefore=12,
            spaceAfter=3,
            textColor=colors.HexColor("#16a34a"),
            fontName="Helvetica-Bold",
        ),
        "system_label": ParagraphStyle(
            "SystemLabel",
            parent=base["Normal"],
            fontSize=11,
            leading=15,
            spaceBefore=12,
            spaceAfter=3,
            textColor=colors.HexColor("#9333ea"),
            fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            spaceAfter=4,
            textColor=colors.HexColor("#374151"),
        ),
        "code_block": ParagraphStyle(
            "CodeBlock",
            parent=base["Code"],
            fontSize=8.5,
            leading=12,
            spaceBefore=4,
            spaceAfter=4,
            backColor=colors.HexColor("#f3f4f6"),
            borderPadding=(4, 6, 4, 6),
            fontName="Courier",
            textColor=colors.HexColor("#1f2937"),
            leftIndent=8,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            leftIndent=16,
            textColor=colors.HexColor("#374151"),
        ),
        "ref_header": ParagraphStyle(
            "RefHeader",
            parent=base["Heading2"],
            fontSize=13,
            spaceBefore=14,
            spaceAfter=6,
            textColor=colors.HexColor("#1a1a2e"),
        ),
        "ref_link": ParagraphStyle(
            "RefLink",
            parent=base["Normal"],
            fontSize=9,
            leading=13,
            leftIndent=8,
            textColor=colors.HexColor("#2563eb"),
        ),
        "ref_snippet": ParagraphStyle(
            "RefSnippet",
            parent=base["Normal"],
            fontSize=8.5,
            leading=12,
            leftIndent=20,
            textColor=colors.HexColor("#6b7280"),
        ),
    }

    return styles


# ---------------------------------------------------------
# Markdown block parser
# ---------------------------------------------------------

def _markdown_to_elements(text: str, styles: dict) -> list:
    """
    Convert a markdown string into a list of ReportLab flowables.
    Handles: headings, code blocks, bullet lists, horizontal rules, paragraphs.
    """
    elements = []
    lines = text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # --- Fenced code block ---
        if line.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(_escape_xml(lines[i]))
                i += 1
            code_text = "<br/>".join(code_lines) if code_lines else " "
            elements.append(Paragraph(code_text, styles["code_block"]))
            i += 1
            continue

        # --- Horizontal rule ---
        if re.match(r"^---+$", line.strip()):
            elements.append(Spacer(1, 4))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#d1d5db")))
            elements.append(Spacer(1, 4))
            i += 1
            continue

        # --- Headings ---
        h1_match = re.match(r"^# (.+)", line)
        h2_match = re.match(r"^## (.+)", line)
        h3_match = re.match(r"^### (.+)", line)

        if h1_match:
            content = _inline_styles(_escape_xml(h1_match.group(1)))
            elements.append(Paragraph(content, styles["title"]))
            i += 1
            continue

        if h2_match:
            content = _inline_styles(_escape_xml(h2_match.group(1)))
            elements.append(Paragraph(content, styles["h2"]))
            i += 1
            continue

        if h3_match:
            raw = h3_match.group(1)
            # Role labels — keep their emoji, apply role style
            if "🧑 User" in raw:
                elements.append(Paragraph("🧑 User", styles["user_label"]))
            elif "🤖 Assistant" in raw:
                elements.append(Paragraph("🤖 Assistant", styles["assistant_label"]))
            elif "⚙️ System" in raw:
                elements.append(Paragraph("⚙️ System", styles["system_label"]))
            else:
                content = _inline_styles(_escape_xml(raw))
                elements.append(Paragraph(content, styles["h3"]))
            i += 1
            continue

        # --- Bullet list item ---
        bullet_match = re.match(r"^(\s*)[-*+] (.+)", line)
        if bullet_match:
            content = _inline_styles(_escape_xml(bullet_match.group(2)))
            indent = len(bullet_match.group(1))
            style = ParagraphStyle(
                "BulletIndent",
                parent=styles["bullet"],
                leftIndent=16 + indent * 8,
            )
            elements.append(Paragraph(f"• {content}", style))
            i += 1
            continue

        # --- Numbered list item ---
        num_match = re.match(r"^\d+\. (.+)", line)
        if num_match:
            content = _inline_styles(_escape_xml(num_match.group(1)))
            elements.append(Paragraph(f"{content}", styles["bullet"]))
            i += 1
            continue

        # --- Blank line ---
        if line.strip() == "":
            elements.append(Spacer(1, 5))
            i += 1
            continue

        # --- Regular paragraph ---
        content = _inline_styles(_escape_xml(line))
        elements.append(Paragraph(content, styles["body"]))
        i += 1

    return elements


# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------

def to_pdf(markdown: str, output_path: str, links: dict = None) -> str:
    """
    Convert a markdown string (as produced by to_markdown()) into a PDF.

    Args:
        markdown:     Full markdown text of the conversation.
        output_path:  Destination .pdf file path.
        links:        Optional dict of {url: {"title": ..., "snippet": ...}}
                      If provided, a References section is appended.

    Returns:
        output_path on success.
    """

    styles = _build_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="ChatGPT Conversation",
        author="ChatGPT Share Exporter",
    )

    story = _markdown_to_elements(markdown, styles)

    # --- References section ---
    if links:
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#9ca3af")))
        story.append(Paragraph("References", styles["ref_header"]))

        for url, info in links.items():
            title = info.get("title") or url
            snippet = info.get("snippet")

            safe_url = _escape_xml(url)
            safe_title = _escape_xml(title)

            story.append(
                Paragraph(
                    f'<link href="{safe_url}" color="#2563eb">{safe_title}</link>',
                    styles["ref_link"],
                )
            )
            if snippet:
                story.append(Paragraph(_escape_xml(snippet), styles["ref_snippet"]))

    doc.build(story)
    print(f"Saved → {output_path}")
    return output_path