import json
import os
import shutil
import time
from pathlib import Path

import inquirer
from yaspin import yaspin, Spinner

from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.table import Table
from rich import box

from fetcher import fetch_chatgpt_share
from markdowns import to_markdown
from links_extractor import extract_urls_from_json


console = Console()


# ---------------------------------------------------------
# Theme Colors
# ---------------------------------------------------------

ORANGE = "#FF8C00"
ORANGE_BORDER = "#E65100"
BLACK = "#000000"
ACCENT = "#FFA726"


# ---------------------------------------------------------
# Custom Spinner (your requested one)
# ---------------------------------------------------------

CUSTOM_SPINNER = Spinner(
    ["⬅", "➡", "⬆", "⬇", "↙", "↘", "↗", "↖", "↕"],
    200
)


# ---------------------------------------------------------
# Banner Utilities
# ---------------------------------------------------------

def get_terminal_width():

    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def get_banner_width(text):

    lines = text.splitlines()

    if not lines:
        return 0

    return max(len(line) for line in lines)


def make_small_banner():

    small = Text()

    small.append(
        "CHAT2README",
        style=f"bold {ORANGE}"
    )

    return small


def create_outlined_text(text):

    lines = text.splitlines()

    outlined = Text()

    for line in lines:

        outlined.append(
            line,
            style=f"bold {BLACK}"
        )

        outlined.append("\n")

    outlined.append(
        f"\x1b[{len(lines)}A"
    )

    for line in lines:

        outlined.append(
            line,
            style=f"bold {ORANGE}"
        )

        outlined.append("\n")

    return outlined


def render_banner():

    banner_path = Path("banner.txt")

    if not banner_path.exists():

        console.print(
            "[bold red]banner.txt not found[/]"
        )

        return

    banner_text = banner_path.read_text(
        encoding="utf-8"
    )

    terminal_width = get_terminal_width()

    banner_width = get_banner_width(
        banner_text
    )

    if banner_width >= terminal_width:

        console.print(
            Panel(
                Align.center(
                    make_small_banner()
                ),
                border_style=ORANGE_BORDER,
                padding=(1, 2),
                width=terminal_width
            )
        )

    else:

        outlined_banner = create_outlined_text(
            banner_text
        )

        console.print(
            Panel(
                Align.center(outlined_banner),
                border_style=ORANGE_BORDER,
                padding=(1, 2),
                width=terminal_width
            )
        )

    console.print(
        Align.center(
            Text(
                "Chat2Readme CLI — Convert chatgpt chats into readme",
                style=f"bold {ACCENT}"
            )
        )
    )

    console.print()


# ---------------------------------------------------------
# Core Logic
# ---------------------------------------------------------

def validate_share_url(url):

    return url.startswith("http") and "/share/" in url


def get_share_id(url):

    return url.rstrip("/").split("/")[-1]


def append_links_section(markdown, links):

    if not links:

        return markdown

    lines = [

        "",
        "---",
        "",
        "## References",
        "",
    ]

    for url, info in links.items():

        title = info.get("title") or url
        snippet = info.get("snippet")

        lines.append(
            f"- [{title}]({url})"
        )

        if snippet:

            lines.append(
                f"  - {snippet}"
            )

    lines.append("")

    return markdown + "\n".join(lines)


def process_chat(url):

    data = fetch_chatgpt_share(url)

    share_id = get_share_id(url)

    os.makedirs(
        "json",
        exist_ok=True
    )

    os.makedirs(
        "readmes",
        exist_ok=True
    )

    json_path = Path(
        "json"
    ) / f"chat_raw_{share_id}.json"

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

    markdown = to_markdown(data)

    try:

        links = extract_urls_from_json(
            data
        )

    except Exception:

        links = {}

    markdown = append_links_section(
        markdown,
        links
    )

    readme_path = Path(
        "readmes"
    ) / f"README_{share_id}.md"

    readme_path.write_text(
        markdown,
        encoding="utf-8"
    )

    return {

        "json": str(json_path),
        "readme": str(readme_path),
        "links": len(links)

    }


# ---------------------------------------------------------
# UI Components
# ---------------------------------------------------------

def show_result(result):

    table = Table(

        title="Generated Files",

        box=box.ROUNDED,

        border_style=ORANGE_BORDER

    )

    table.add_column(
        "Type",
        style=ORANGE
    )

    table.add_column(
        "Path"
    )

    table.add_row(
        "JSON",
        result["json"]
    )

    table.add_row(
        "README",
        result["readme"]
    )

    table.add_row(
        "Links",
        str(result["links"])
    )

    console.print(table)


# ---------------------------------------------------------
# Input Prompts
# ---------------------------------------------------------

def ask_action():

    questions = [

        inquirer.List(

            "action",

            message="Choose action",

            choices=[

                "Generate README",

                "Exit"

            ]

        )

    ]

    answer = inquirer.prompt(
        questions
    )

    return answer["action"]


def ask_url():

    questions = [

        inquirer.Text(

            "url",

            message="Paste ChatGPT share link"

        )

    ]

    answer = inquirer.prompt(
        questions
    )

    return answer["url"]


# ---------------------------------------------------------
# Main Loop
# ---------------------------------------------------------

def main():

    while True:

        console.clear()

        render_banner()

        action = ask_action()

        if action == "Exit":

            console.print(
                "\n🙏 Thank you for using Chat2Readme CLI!"
            )

            break

        url = ask_url()

        if not validate_share_url(url):

            console.print(
                Panel(
                    "Please provide a valid ChatGPT share link.",
                    border_style="red"
                )
            )

            time.sleep(2)

            continue

        with yaspin(

            CUSTOM_SPINNER,

            text="processing..."

        ):

            result = process_chat(url)

            time.sleep(0.5)

        console.clear()

        render_banner()

        show_result(result)

        console.input(
            "\nPress Enter to continue..."
        )


if __name__ == "__main__":

    main()