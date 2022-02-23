from abc import ABC, abstractmethod
import typing
from bot.notify_provider import TelegramNotifier
from utils import sys_config
import uuid
import dataclasses
import requests, os


@dataclasses.dataclass
class Video():
    name: str = ""
    url: str = None
    path: str = None
    exception: Exception = None
    size: int = 0
    video_info : typing.Any = None


class AbstractEngine(ABC):
    def __init__(self) -> None:
        self.type = None
        super().__init__()

    @abstractmethod
    def consist_type(self, url) -> bool:
        return False

    def name_to_hash(self, name):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, name)) + "." + sys_config("PREFERRED_VIDEO_FORMAT")

    def get_downloaded_file_abspath(self, filename):
        return os.path.abspath(os.path.join(sys_config("VIDEO_FILE_FOLDER"), filename))

    @abstractmethod
    def proceed(self, url, notifier: TelegramNotifier, session=requests.Session) -> Video:
        self.notifier = notifier
        self.session = session
        return Video()
        
