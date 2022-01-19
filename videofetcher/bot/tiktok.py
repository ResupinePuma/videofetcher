import os, re
from urllib.parse import parse_qsl, urlparse
import requests

from bot.exceptions import TiktokUrlException
from bot.session import PSession



class TikTokDownloader:
    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "DNT": "1",
        # "Host": "vm.tiktok.com",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
    }

    def __init__(self, url: str, web_id: str):
        self.__url = url
        self.__cookies = {
            'tt_webid': web_id,
            'tt_webid_v2': web_id
        }

    def filter(self, response):
        if response.status <= 200:
            return response

    def get_video_url(self) -> str:
        session = PSession()
        if len(re.findall(r'(.*tiktok\.com\/@.*\/live)', self.__url)) > 0:
            raise TiktokUrlException("Can't download tiktok live stream. Try another url")
        for _ in range(3):
            response = session.get(self.__url, filter=self.filter, headers=TikTokDownloader.HEADERS, timeout=5)
            matches = re.findall(r'"playAddr":"([a-zA-Z0-9:.\/\\.:&-=?%_]*)"', response.text)
            if len(matches) > 1 or len(matches) == 0:
                continue
            return matches[0].replace(r'\u0026', '&').replace(r'\u002F', '/')
        raise TiktokUrlException()
    
