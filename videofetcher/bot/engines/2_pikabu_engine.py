import logging
from bot.engines.abstract import Video, AbstractEngine
from utils import exceptions, sys_config, format_size
import re, requests, hashlib, os, random

class PikabuEngine(AbstractEngine):
    def __init__(self) -> None:
        super().__init__()

    def consist_type(self, url) -> bool:
        vid = re.findall(r"\/\/.*pikabu\.ru\/story\/",url)
        if len(vid) > 0:
            return True
        else:
            return False

    def proceed(self, url, notifier, session=requests.Session()) -> Video:
        self.notifier = notifier
        self.session :requests.Session = session
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
            self.notifier.update_status("🔎 Extracting video")

            self.notifier.make_progress_bar(0)
            response = self.session.get(url)

            self.notifier.make_progress_bar(25)


            matches = re.search(r'<div class="player.*data-webm="(.*webm)"', response.text, re.IGNORECASE)
            if matches:
                video_url = matches.group(1)                
            else:
                raise exceptions.DownloadError("Can't find video on this url. Try again later")

            self.notifier.make_progress_bar(50)

            matches = re.search(r'<span class=\"story__title-link\">(.*)<\/span>', response.text, re.IGNORECASE)
            if matches:
                video.name = matches.group(1).split('</span>')[0]                
            else:
                logging.error("Can't get title from page")

            self.notifier.make_progress_bar(75)
            
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
                video.name = video.name or url
            
            self.notifier.make_progress_bar(100)            

        except Exception as ex:
            logging.exception(ex)
            video.exception = ex
        
        return video

def proceed(url, notifier, session) -> Video:
    return PikabuEngine().proceed(url, notifier, session)



