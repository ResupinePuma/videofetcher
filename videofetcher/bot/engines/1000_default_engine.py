import logging, os, hashlib, requests
from bot.engines.abstract import Video, AbstractEngine
from utils import exceptions, sys_config, format_size 
import yt_dlp as ytd
from base64 import b64decode, b64encode


class Ydl_Extractor():
    def __init__(self, notifier) -> None:
        self.video_info = None
        self.notifier = notifier
        self.filename = None

    def get_extract_params(self, name):
        self.filename = name
        return {
            "outtmpl": os.path.join(sys_config("VIDEO_FILE_FOLDER"), self.filename),
            "format": "best[height<=960][ext=mp4],best[ext=unknown_video],bestvideo[height<=480][ext=mp4]+worstaudio[ext=m4a],best[height<=960][ext=mp4],best[ext=unknown_video],worst[ext=mp4]",
            "socket_timeout": 10,
            "retries": 10,
            #"verbose" : True,
            "prefer_ffmpeg": True,
            "keepvideo": True,
        }

    def video_id(self):
        return self.video_info["id"]

    def video_timestamp(self):
        return self.video_info["timestamp"]

    def video_title(self):
        return self.video_info["title"]

    def video_url(self):
        return self.video_info["webpage_url"]

    def process_video(self, video : Video, extraction_param, downloaded_filename):
        self.video_info = video.video_info

        allowed_file_size = int(sys_config("MAX_FILE_SIZE"))
        filesize = int(video.video_info.get('filesize_approx', 0))
        if filesize >> 20 > allowed_file_size:
            raise exceptions.FileIsTooLargeException("File size > {}Mb".format(allowed_file_size))
       
        ydl = ytd.YoutubeDL(extraction_param)
        try:
            ydl.download([self.video_url()])
        except:
            raise exceptions.DownloadError("Can't download video from this url")
        #downloaded_filename = self.get_downloaded_file_abspath(self.filename)
        file_size = os.path.getsize(downloaded_filename)
        video.size = file_size
        video.path = downloaded_filename
        formatted_file_size = format_size(file_size)
        logging.info("Video saved as: {}".format(downloaded_filename))

        allowed_file_size = int(sys_config("MAX_FILE_SIZE"))
        if file_size >> 20 > allowed_file_size:
            raise exceptions.FileIsTooLargeException("File size > {}".format(formatted_file_size))
        else:
            yield video

class DefaultEngine(AbstractEngine):
    def __init__(self) -> None:
        super().__init__()
    
    def consist_type(self, url) -> bool:
        return True

    def get_videos(self):
        if not self.is_playlist():
            yield Video(video_info=self.video_info)
        else:
            for entry in self.get_playlist_videos():
                yield Video(video_info=entry)

    def is_playlist(self):
        if "playlist" in self.get_type():
            return True
        return False

    def get_playlist_videos(self):
        return self.video_info["entries"]

    def get_type(self):
        return self.video_info["extractor"]

    def proceed(self, url, notifier, session=None) -> Video:
        self.notifier = notifier
        self.session = notifier

        video = Video(url=url)

        ytd.utils.std_headers['User-Agent'] = sys_config("USER_AGENT")
        downloader = ytd.YoutubeDL({"socket_timeout": 10})

        name_hash = self.name_to_hash(video.url)
        if os.path.exists(self.get_downloaded_file_abspath(name_hash)):
            path = self.get_downloaded_file_abspath(name_hash)
            file_size = os.path.getsize(path)
            video.name = downloader.extract_info(url, download=False).get("title", url)
            video.size = file_size
            video.path = path
            logging.info("Return saved video: {}".format(path))
            return video

        try:
            self.notifier.update_status("‍♻️ processing video")
            logging.info("Processing video")
            self.video_info = downloader.extract_info(url, download=False)
            logging.info("Got video info")

            self.notifier.make_progress_bar(0)

            for yt_video in self.get_videos():
                video.name = yt_video.video_info.get("title")
                video.video_info = yt_video.video_info
                ydl_extractor = Ydl_Extractor(self.notifier)

                self.notifier.make_progress_bar(30)
                path = self.get_downloaded_file_abspath(name_hash)
                for media in ydl_extractor.process_video(video, ydl_extractor.get_extract_params(name_hash), path):
                    video = media                    
                    break
            self.notifier.make_progress_bar(100)
        except Exception as ex:
            video.exception = ex
        
        return video

def proceed(url, notifier, session=None) -> Video:
    return DefaultEngine().proceed(url, notifier, session=None)