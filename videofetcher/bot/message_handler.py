from asyncio import exceptions
from html import entities
import logging, re

from telegram.ext import MessageHandler, Filters

from bot.video_provider import VideoProvider
from bot.notify_provider import TelegramNotifier
from telegram import MessageEntity, ParseMode
import utils.exceptions as exs
import time


def extract_url(text):
    ress = re.findall(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", text)
    if len(ress) > 0:
        return ress[0], " ".join(text.replace(ress[0], "").split(" "))
    else:
        return "", text


class GenericMessageHandler:
    def __init__(self, dispatcher):
        self.message_handler = MessageHandler(
            Filters.text & (~Filters.command), self.create_video_provider
        )
        dispatcher.add_handler(self.message_handler)

    @staticmethod
    def create_video_provider(update, context):
        bot = context.bot
        chat_id = update.effective_chat.id
        original_message_id = update.message.message_id

        logging.info("Received message: {}".format(update.message.text))
        video_link, description = extract_url(update.message.text)

        if (not video_link):
            logging.info("🔎 No url found in message text!")
            return

        logging.info("Got url: {}".format(video_link))
        reply_message = bot.send_message(
            chat_id, "Got {}. 👀 at 📼".format(video_link), disable_web_page_preview=True,
        )

        notifier = TelegramNotifier(bot, chat_id, reply_message.message_id)

        video_provider = VideoProvider(notifier)

        video = video_provider.process_video(video_link)

        if not video.path or video.exception:
            logging.exception(video.exception)
            notifier.update_status("Something went wrong 🤔")
            if type(video.exception) in [exs.DownloadError, exs.FileIsTooLargeException]:
                notifier.update_status("Something went wrong 🤔\n{}".format(video.exception))
            return

        video_bytes = open(video.path, "rb")

        notifier.update_status(
            "Almost there. Uploading {} 🔈".format(video.name)
        )

        text = f"<a href='{video.url}'>{description if description else video.name}</a>"
        bot.send_chat_action(chat_id, "upload_video")

        entities = [
            MessageEntity('url',0,len(video.url),video.url)
        ]
        
        bot.send_video(
            chat_id,
            video_bytes,
            caption=f"{video.url}\n{video.name}",
            caption_entities=entities,
            timeout=60,

        )

        bot.delete_message(chat_id, original_message_id)
        notifier.update_status("Done! ✅")
        time.sleep(3)
        bot.delete_message(chat_id, reply_message.message_id)