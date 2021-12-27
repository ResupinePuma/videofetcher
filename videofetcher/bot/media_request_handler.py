import logging
import os, hashlib

import yt_dlp as yt

from bot.exceptions import *
from common.helper import format_size, rename_file
from config.bot_config import PREFERRED_AUDIO_CODEC, AUDIO_OUTPUT_DIR


class MediaRequestHandler:
    def __init__(self, extraction_param, notifier):
        self.extraction_param = extraction_param
        self.notifier = notifier
        self.video_info = None

    def get_downloaded_file_abspath(self):
        filename = hashlib.md5(self.video_id().encode("utf-8")).hexdigest() + "." + PREFERRED_AUDIO_CODEC
        return os.path.abspath(os.path.join(AUDIO_OUTPUT_DIR, filename))

    def video_id(self):
        return self.video_info["id"]

    def video_timestamp(self):
        return self.video_info["timestamp"]

    def video_title(self):
        return self.video_info["title"]

    def video_url(self):
        return self.video_info["webpage_url"]

    def process_video(self, yt_video):
        self.video_info = yt_video
        ydl = yt.YoutubeDL(self.extraction_param)
        try:
            ydl.download([self.video_url()])
        except:
            raise DownloadError("Can't download video from this url")
        downloaded_filename = self.get_downloaded_file_abspath()
        file_size = os.path.getsize(downloaded_filename)
        formatted_file_size = format_size(file_size)
        downloaded_video_message = "🔈 File size: {}".format(formatted_file_size)
        self.notifier.progress_update(downloaded_video_message)
        logging.info(downloaded_video_message)

        filename = self.get_downloaded_file_abspath()
        #rename_file(
        #     self.get_downloaded_file_abspath(),
        #     "{0}".format(hashlib.md5(self.video_id().encode("utf-8")).hexdigest() + "." + PREFERRED_AUDIO_CODEC),
        # )

        # if the extracted audio file is larger than 50M
        allowed_file_size = 50
        if file_size >> 20 > allowed_file_size:
            file_size_warning = "😱 File size {} > allowed {} therefore trying to chunk into smaller files".format(
                formatted_file_size, allowed_file_size
            )
            raise FileIsTooLargeException(file_size_warning)
        else:
            yield {
                "filename": filename,
            }
