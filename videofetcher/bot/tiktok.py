import os, re
from urllib.parse import parse_qsl, urlparse
import requests


class TikTokDownloader:
    HEADERS = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'DNT': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Dest': 'video',
        'Referer': 'https://www.tiktok.com/',
        'Accept-Language': 'en-US,en;q=0.9,bs;q=0.8,sr;q=0.7,hr;q=0.6',
        'sec-gpc': '1',
        'Range': 'bytes=0-',
    }

    def __init__(self, url: str, web_id: str):
        self.__url = url
        self.__cookies = {
            'tt_webid': web_id,
            'tt_webid_v2': web_id
        }

    def get_video_url(self) -> str:
        session = requests.Session()
        session.cookies.update(self.__cookies)
        session.headers = TikTokDownloader.HEADERS
        for i in range(3):
            response = session.get(self.__url)
            matches = re.findall(r'"playAddr":"([a-zA-Z0-9:.\/\\.:&-=?%_]*)"', response.content.decode("utf-8"))
            if len(matches) > 1:
                continue
            return matches[0].replace(r'\u0026', '&').replace(r'\u002F', '/')
        return None
