#!/usr/bin/env python3
"""
Generate Phantom-format ammo for POST /similar/ load test.

Each request posts url + cnt as application/x-www-form-urlencoded.
The model must already be trained before running the test.

Usage:
    python gen-post-ammo.py > post-ammo.txt
"""

import urllib.parse

URLS = [
    "https://en.wikipedia.org/wiki/The_Godfather",
    "https://en.wikipedia.org/wiki/Pulp_Fiction",
    "https://en.wikipedia.org/wiki/Schindler%27s_List",
    "https://en.wikipedia.org/wiki/Forrest_Gump",
    "https://en.wikipedia.org/wiki/The_Matrix",
]

HOST = "158.160.91.139"

for wiki_url in URLS:
    body = urllib.parse.urlencode({"url": wiki_url, "cnt": 3})
    body_bytes = body.encode()
    headers = (
        f"POST /similar/ HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"\r\n"
    )
    full_request = headers.encode() + body_bytes
    print(len(full_request))
    print(full_request.decode(errors="replace"))
    print()
