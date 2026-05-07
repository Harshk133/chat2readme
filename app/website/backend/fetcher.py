
from curl_cffi import requests  # <-- NOT the standard requests library
import urllib.request

def fetch_chatgpt_share(share_url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as response:
        return response.read().decode("utf-8")


    # # Normalize URL
    # if "/share/" in share_url and "/backend-api/" not in share_url:
    #     share_id = share_url.rstrip("/").split("/share/")[-1]
    #     api_url = f"https://chatgpt.com/backend-api/share/{share_id}"
    # else:
    #     api_url = share_url

    # share_page_url = api_url.replace("/backend-api/share/", "/share/")

    # session = requests.Session(impersonate="chrome124")  # Full Chrome TLS fingerprint

    # # Step 1: Visit the share page first (picks up cookies)
    # session.get(share_page_url, timeout=20)

    # # Step 2: Hit the backend API
    # response = session.get(
    #     api_url,
    #     headers={
    #         "Accept": "application/json",
    #         "Referer": share_page_url,
    #     },
    #     timeout=20,
    # )

    # response.raise_for_status()
    # return response.json()