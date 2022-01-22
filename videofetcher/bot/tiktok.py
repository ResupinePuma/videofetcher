import os, re
from urllib.parse import parse_qsl, urlparse
import requests
from bot.telegram_notifier import TelegramNotifier 

from bot.exceptions import TiktokUrlException
from aiohttp import CookieJar

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

    def __init__(self, url: str, web_id: str, session=requests.Session()):
        self.__url = url
        self.session = session
        self.__cookies = {
            'tt_webid': web_id,
            'tt_webid_v2': web_id
        }

    def filter(self, response):
        if response.status <= 200:
            return response

    def get_video_url(self, notifier : TelegramNotifier) -> str:
        if len(re.findall(r'(.*tiktok\.com\/@.*\/live)', self.__url)) > 0:
            raise TiktokUrlException("Can't download tiktok live stream. Try another url")
        for i in range(4):
            notifier.set_progress_bar(i*25)
            response = self.session.get(self.__url, headers=TikTokDownloader.HEADERS, timeout=20)
            if not response:
                self.session.cookies=CookieJar()
                self.session.proxy_list = self.session.get_proxy_list()
                continue
            matches = re.findall(r'"playAddr":"([a-zA-Z0-9:.\/\\.:&-=?%_]*)"', response.text)
            if len(matches) > 1 or len(matches) == 0:
                self.session.cookies=CookieJar()
                self.session.proxy_list = self.session.get_proxy_list()
                continue
            return matches[0].replace(r'\u0026', '&').replace(r'\u002F', '/')
        raise TiktokUrlException()
    
