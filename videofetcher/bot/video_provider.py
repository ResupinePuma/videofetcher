import logging
import os,re, random
import yt_dlp as yt
from bot.tiktok import TikTokDownloader

from bot.extraction_params import create_extraction_params
from bot.exceptions import FileIsTooLargeException
from bot.telegram_notifier import TelegramNotifier
from telegram import ParseMode

yt.utils.std_headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"

class Video:
    def __init__(self, video_info):
        self.info = video_info


class VideoProvider:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.video_info = None

    def __type_detect(self, link):
        tiktok = re.findall(r"^(http|https):\/\/.*\.tiktok\.com\/",link)

        logging.error(tiktok)
        if len(tiktok) > 0:
            logging.error(1)
            tt = TikTokDownloader(link, str(random.randint(111111111111, 99999999999999)))            
            return "tiktok", tt.get_video_url()
        logging.error(2)
        return "any", link


    def process(self, video_link, update_message_id, text=""):
        notifier = TelegramNotifier(self.bot, self.chat_id, update_message_id)
        yt_downloader = yt.YoutubeDL({"socket_timeout": 10})
        src_link = video_link
        type = "any"
        try:
            type, video_link = self.__type_detect(video_link)
        except:
            return False

        self.video_info = yt_downloader.extract_info(video_link, download=False)
        if (not text):
            text = self.video_info.get('title', "")
            if type == "tiktok":
                text = src_link
        notifier.progress_update("‍🤖 processing video")
        
        try:
            for yt_video in self.yt_videos():
                logging.info("Processing Video -> {}".format(yt_video.info.get("id")))
                request_handler = create_extraction_params(notifier, yt_video.info.get("id"))
                for data in request_handler.process_video(yt_video.info):
                    filename = data["filename"]
                    video_file = open(filename, "rb")

                    notifier.progress_update(
                        "Almost there. Uploading {} 🔈".format(
                            os.path.basename(filename)
                        )
                    )

                    text = f"<a href='{src_link}'>{text}</a>"
                    self.bot.send_chat_action(self.chat_id, "upload_video")
                    self.bot.send_video(
                        self.chat_id,
                        video_file,
                        caption=text,
                        parse_mode=ParseMode.HTML,
                        timeout=120,
                    )
        except FileIsTooLargeException as e:
            file_too_large_error = "[File Is Too Large] {}".format(str(e))
            logging.error(file_too_large_error)
            self.bot.send_message(self.chat_id, file_too_large_error, disable_web_page_preview=True)
            return False
        except:
            return False

        notifier.progress_update("Done! ✅")
        return True

    def yt_videos(self):
        if not self.is_yt_playlist():
            yield Video(self.video_info)
        else:
            for entry in self.get_playlist_videos():
                yield Video(entry)

    def is_yt_playlist(self):
        if "playlist" in self.get_type():
            return True
        return False

    def get_playlist_videos(self):
        return self.video_info["entries"]

    def get_type(self):
        return self.video_info["extractor"]

