import logging
import os,re, random
import yt_dlp as yt
import timeout_decorator
from bot.tiktok import TikTokDownloader

from bot.extraction_params import create_extraction_params, proxies_session
from bot.exceptions import *
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

    def __type_detect(self, link, notifier):
        tiktok = re.findall(r"\/\/.*\.tiktok\.com\/",link)

        if len(tiktok) > 0:
            tt = TikTokDownloader(link)            
            return "tiktok", tt.get_video_url(notifier)
        return "any", link

    @timeout_decorator.timeout(50, use_signals=False)
    def process(self, video_link, update_message_id, text=""):
        notifier = TelegramNotifier(self.bot, self.chat_id, update_message_id)
        yt_downloader = yt.YoutubeDL({"socket_timeout": 10})
        src_link = video_link
        type = "any"
        
        try:
            type, video_link = self.__type_detect(video_link, notifier)
            try:
                self.video_info = yt_downloader.extract_info(video_link, download=False)
            except:
                raise UrlException()
            notifier.set_progress_bar(100)
            notifier.rm_progress_bar()
                
            if (not text):
                text = self.video_info.get('title', "")
                if type == "tiktok":
                    text = src_link
            notifier.progress_update("‍🤖 processing video")

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
                        timeout=60,
                    )
        except FileIsTooLargeException as e:
            file_too_large_error = "[File Is Too Large] {}".format(str(e))
            # logging.error(file_too_large_error)
            # self.bot.send_message(self.chat_id, file_too_large_error, disable_web_page_preview=True)
            return False, file_too_large_error
        except TiktokUrlException as e:
            return False, str(e)
        except DownloadError as e:
            return False, str(e)
        except UrlException as e:
            return False, str(e)
        except Exception as ex:
            logging.error(ex)
            return False, "We'll have a look and try to fix this issue."

        notifier.progress_update("Done! ✅")
        return True, ""

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

