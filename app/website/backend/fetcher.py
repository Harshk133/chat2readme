import httpx

def fetch_chatgpt_share(share_url: str) -> dict:

    # Normalize URL
    if "/share/" in share_url and "/backend-api/" not in share_url:
        share_id = share_url.rstrip("/").split("/share/")[-1]
        api_url = f"https://chatgpt.com/backend-api/share/{share_id}"
    else:
        api_url = share_url

    share_page_url = api_url.replace("/backend-api/share/", "/share/")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": share_page_url,
        "Origin": "https://chatgpt.com",
    }

    with httpx.Client(follow_redirects=True, timeout=20) as client:
        # Step 1: Visit share page to pick up cookies
        resp1 = client.get(share_page_url, headers={
            **headers,
            "Accept": "text/html,application/xhtml+xml"
        })

        # Step 2: Carry cookies into API call
        cookies = resp1.cookies
        response = client.get(api_url, headers=headers, cookies=cookies)

        response.raise_for_status()
        return response.json()