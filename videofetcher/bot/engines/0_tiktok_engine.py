import logging
from bot.engines.abstract import Video, AbstractEngine
from utils import exceptions, sys_config, format_size
import re, requests, hashlib, os, random

PHRASES = [
    "📞 Asking Xi's permission to download",
    "🤙 Contacting with agent in TT headquaters",
    "✂️ Cutting TT webpage",
    "📛 Breaking through chinese firewall",
    "🔎 Searching video"
]

class TiktokEngine(AbstractEngine):
    def __init__(self) -> None:
        super().__init__()

    def consist_type(self, url) -> bool:
        tiktok = re.findall(r"\/\/.*\.tiktok\.com\/",url)
        if len(tiktok) > 0:
            return True
        else:
            return False

    def proceed(self, url, notifier, session=requests.Session()) -> Video:
        self.notifier = notifier
        self.session = session
        video = Video(url=url, name=url)
        if not self.consist_type(url):
            return video

        name_hash = self.name_to_hash(video.url)
        if os.path.exists(self.get_downloaded_file_abspath(name_hash)):
            path = self.get_downloaded_file_abspath(name_hash)
            file_size = os.path.getsize(path)
            video.size = file_size
            video.path = path
            logging.info("Return saved video: {}".format(path))
            return video

        try:
            if len(re.findall(r'(.*tiktok\.com\/@.*\/live)', url)) > 0:
                raise exceptions.DownloadError("Can't download tiktok live stream. Try another url")

            self.notifier.update_status(random.choice(PHRASES))

            video_url = None
            for i in range(3):
                self.notifier.make_progress_bar(i*25)
                response = requests.post(f"{sys_config('SPLASH_URL')}/render.html", json={
                    "url" : url,
                    "http2" : 1,
                    "wait" : 1,
                    "headers" : [("user-agent", sys_config("USER_AGENT").replace('"',''))]
                }, timeout=int(sys_config("PROCESSING_TIMEOUT")))
                matches = re.findall(r'"playAddr":"([a-zA-Z0-9:.\/\\.:&-=?%_]*)"', response.text)
                if len(matches) > 1 or len(matches) == 0:
                    continue
                video_url = matches[0].replace(r'\u0026', '&').replace(r'\u002F', '/')
                break
            
            if not video_url:
                raise exceptions.DownloadError("Can't download video from this url")

            self.notifier.update_status("⏬ Downloading video")

            response = self.session.get(video_url, timeout=10)
            
            if response.status_code < 400 and response.content:
                path = self.get_downloaded_file_abspath(name_hash)
                with open(path, "wb") as f:
                    f.write(response.content)
                video.path = path
                video.size = os.path.getsize(path)
                video.name = url
            
            self.notifier.make_progress_bar(100)
        except Exception as ex:
            logging.exception(ex)
            video.exception = ex
        
        return video

def proceed(url, notifier, session) -> Video:
    return TiktokEngine().proceed(url, notifier, session)
