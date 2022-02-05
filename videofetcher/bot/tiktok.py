import os, re
from urllib.parse import parse_qsl, urlparse
import requests
from bot.telegram_notifier import TelegramNotifier 

from bot.exceptions import TiktokUrlException
from config.bot_config import SPLASH_URL


class TikTokDownloader:
    def __init__(self, url: str, web_id: str):
        self.__url = url
        
    def get_video_url(self, notifier : TelegramNotifier) -> str:
        if len(re.findall(r'(.*tiktok\.com\/@.*\/live)', self.__url)) > 0:
            raise TiktokUrlException("Can't download tiktok live stream. Try another url")
        for i in range(4):
            notifier.set_progress_bar(i*25)
            response = requests.post(f"{SPLASH_URL}/render.html", json={
                "url" : self.__url,
                "http2" : 1,
                "headers" : [("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36")]
            }, timeout=30)
            matches = re.findall(r'"playAddr":"([a-zA-Z0-9:.\/\\.:&-=?%_]*)"', response.text)
            return matches[0].replace(r'\u0026', '&').replace(r'\u002F', '/')
        raise TiktokUrlException()