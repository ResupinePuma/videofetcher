from bot.engines.abstract import Video
import requests
from bot.notify_provider import TelegramNotifier
from utils import sys_config
from bot.engines import load_engines, engines
load_engines()


class VideoProvider():
    def __init__(self, notifier: TelegramNotifier) -> None:
        self.notifier = notifier
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": sys_config("USER_AGENT").replace('"', '')})

    def process_video(self, url) -> Video:
        res = Video()
        sorted_engines = {k: engines[k] for k in sorted(engines)}
        for name, eng in sorted_engines.items():
            try:
                res = eng.proceed(url, self.notifier, self.session)
                if res.path:
                    break
            except Exception as ex:
                res.exception = ex
        return res
