import logging
from bot.engines.abstract import Video, AbstractEngine
from utils import exceptions, sys_config, format_size
import re, requests, hashlib, os, random
from urllib.parse import quote

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
        tiktok = re.findall(r"\/\/.*vm.tiktok\.com\/",url)
        if len(tiktok) > 0:
            return True
        else:
            return False

    def proceed(self, url, notifier, session=requests.Session()) -> Video:
        self.notifier = notifier
        self.session = session
        video = Video(url=url)
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

            video_links, video_id = None, None
            for i in range(3):
                self.notifier.make_progress_bar(i*10)
                response = requests.post(f"{sys_config('SPLASH_URL')}/render.json", json={
                    "url" : url,
                    "http2" : 1,
                    "wait" : 3,
                    "headers" : [("user-agent", sys_config("USER_AGENT").replace('"',''))],
                    "response_body" : 1
                }, timeout=int(sys_config("PROCESSING_TIMEOUT")))

                self.notifier.make_progress_bar(20)
                logging.info("Got splash TT response: {}".format(response.text))

                if "url" in response.json():
                    tt_url = response.json()['url']
                    matches_id = re.search(r"\/video|v\/([0-9]*)",tt_url,re.IGNORECASE)
                    if matches_id:
                        video.name = response.json().get('title')
                        video_id = matches_id.group(1)
                        break

            if not video_id:
                raise exceptions.DownloadError("Can't download from url. Check if this url is correct")
                
            
            tt_url = f"https://godownloader.com/ru/tiktok-downloader?id={video_id}&link={quote(url)}"
            response = requests.post(f"{sys_config('SPLASH_URL')}/render.html", json={
                "url" : tt_url,
                "http2" : 1,
                "wait" : 4,
                "js_source" : 'document.getElementsByClassName("chakra-textarea").item(0).remove();document.getElementsByClassName("css-1cexexp").item(0).remove()',
                "headers" : [("user-agent", sys_config("USER_AGENT").replace('"',''))],
                "response_body" : 1
            }, timeout=int(sys_config("PROCESSING_TIMEOUT")))
            self.notifier.make_progress_bar(30)

            matches = re.search(r'<a download=\"\" href=\"(.*)\" rel.*<\/a>', response.text, re.IGNORECASE)
            if matches:                
                video_links = re.findall(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", matches.group(1))            
                video_links = [l.replace('"',"") for l in video_links if "dl.godownloader.com" in l or "tiktokcdn.com" in l]                
                self.notifier.make_progress_bar(40)
            else:
                raise exceptions.DownloadError("Can't download from url. Try again later")
            
            if not video_links:
                raise exceptions.DownloadError("Can't download video from this url")
            self.notifier.update_status("⏬ Downloading video")

            for i,video_url in enumerate(video_links):
                response = self.session.get(video_url, timeout=10)
                self.notifier.make_progress_bar(50+i*10)        
                if response.status_code < 400 and response.content:
                    path = self.get_downloaded_file_abspath(name_hash)
                    with open(path, "wb") as f:
                        f.write(response.content)
                    video.path = path
                    video.size = os.path.getsize(path)
                    break
            
            self.notifier.make_progress_bar(100)
        except Exception as ex:
            logging.exception(ex)
            video.exception = ex
        
        return video

def proceed(url, notifier, session) -> Video:
    return TiktokEngine().proceed(url, notifier, session)



