import httpx

share_url = "https://chatgpt.com/share/6a183847-532c-8322-adae-452f99dc46e2"
api_url_1 = "https://chatgpt.com/backend-api/share/6a183847-532c-8322-adae-452f99dc46e2"
api_url_2 = "https://chatgpt.com/backend-anon/share/6a183847-532c-8322-adae-452f99dc46e2"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": share_url,
    "Origin": "https://chatgpt.com",
}

with httpx.Client(follow_redirects=True, timeout=20) as client:
    resp1 = client.get(share_url, headers={**headers, "Accept": "text/html,application/xhtml+xml"})
    cookies = resp1.cookies
    print("Cookies:", cookies)
    
    resp2 = client.get(api_url_1, headers=headers, cookies=cookies)
    print("API 1 status:", resp2.status_code)
    try:
        print(resp2.json())
    except:
        pass
    
    resp3 = client.get(api_url_2, headers=headers, cookies=cookies)
    print("API 2 status:", resp3.status_code)
    try:
        print(resp3.json())
    except:
        pass
