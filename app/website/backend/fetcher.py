
from curl_cffi import requests  # <-- NOT the standard requests library
import urllib.request

def fetch_chatgpt_share(share_url: str) -> dict:


    # Normalize URL
    if "/share/" in share_url and "/backend-api/" not in share_url:
        share_id = share_url.rstrip("/").split("/share/")[-1]
        api_url = f"https://chatgpt.com/backend-api/share/{share_id}"
    else:
        api_url = share_url

    share_page_url = api_url.replace("/backend-api/share/", "/share/")

    session = requests.Session(impersonate="chrome124")  # Full Chrome TLS fingerprint

    # Step 1: Visit the share page first (picks up cookies)
    session.get(share_page_url, timeout=20)

    # Step 2: Hit the backend API
    response = session.get(
        api_url,
        headers={
            "Accept": "application/json",
            "Referer": share_page_url,
        },
        timeout=20,
    )

    response.raise_for_status()
    return response.json()