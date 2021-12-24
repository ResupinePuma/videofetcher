import os
from urllib.parse import parse_qsl, urlparse, pars
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
        response = requests.get(self.__url, cookies=self.__cookies, headers=TikTokDownloader.HEADERS)
        return response.content.decode("utf-8").split('"playAddr":"')[1].split('"')[0].replace(r'\u0026', '&').replace('\u002F', '/')