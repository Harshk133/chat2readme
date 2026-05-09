
# from curl_cffi import requests  # <-- NOT the standard requests library

# def fetch_chatgpt_share(share_url: str) -> dict:
#     # Normalize URL
#     if "/share/" in share_url and "/backend-api/" not in share_url:
#         share_id = share_url.rstrip("/").split("/share/")[-1]
#         api_url = f"https://chatgpt.com/backend-api/share/{share_id}"
#     else:
#         api_url = share_url

#     share_page_url = api_url.replace("/backend-api/share/", "/share/")

#     session = requests.Session(impersonate="chrome124")  # Full Chrome TLS fingerprint

#     # Step 1: Visit the share page first (picks up cookies)
#     session.get(share_page_url, timeout=20)

#     # Step 2: Hit the backend API
#     response = session.get(
#         api_url,
#         headers={
#             "Accept": "application/json",
#             "Referer": share_page_url,
#         },
#         timeout=20,
#     )

#     response.raise_for_status()
#     return response.json()


import httpx
import os

SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")

def fetch_chatgpt_share(share_url: str) -> dict:

    # Normalize URL
    if "/share/" in share_url and "/backend-api/" not in share_url:
        share_id = share_url.rstrip("/").split("/share/")[-1]
        api_url = f"https://chatgpt.com/backend-api/share/{share_id}"
    else:
        api_url = share_url

    share_page_url = api_url.replace("/backend-api/share/", "/share/")

    # Route through ScraperAPI
    proxy_url = f"http://scraperapi:{SCRAPER_API_KEY}@proxy-server.scraperapi.com:8001"

    with httpx.Client(
        proxies={"http://": proxy_url, "https://": proxy_url},
        verify=False,   # ScraperAPI uses its own SSL
        timeout=30,
        follow_redirects=True
    ) as client:
        # Step 1: visit share page for cookies
        client.get(share_page_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html"
        })

        # Step 2: hit the API
        response = client.get(api_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": share_page_url,
        })

        response.raise_for_status()
        return response.json()