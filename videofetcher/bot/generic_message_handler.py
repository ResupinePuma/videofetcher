import logging
import re


from telegram.ext import MessageHandler, Filters

from bot.video_provider import VideoProvider

def get_url(text):
    ress = re.findall(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", text)
    if len(ress) > 0:
        return ress[0], " ".join(text.replace(ress[0], "").split(" "))
    else:
        return "", text


class GenericMessageHandler:
    def __init__(self, dispatcher):
        self.video_link_handler = MessageHandler(
            Filters.text & (~Filters.command), self.create_video_provider
        )
        dispatcher.add_handler(self.video_link_handler)

    @staticmethod
    def create_video_provider(update, context):
        bot = context.bot
        cid = update.effective_chat.id
        original_message_id = update.message.message_id
        video_link, description = get_url(update.message.text)  
        if (not video_link):
            print(1)
            return
        logging.info("Received message: {}".format(video_link))
        video_provider = VideoProvider(bot, cid)
        reply_message = bot.send_message(
            cid, "Got {}. 👀 at 📼".format(video_link), disable_web_page_preview=True,
        )
        task_completed, status_msg = video_provider.process(video_link, reply_message.message_id, description)
        if task_completed:
            bot.delete_message(cid, original_message_id)
            bot.delete_message(cid, reply_message.message_id)
            logging.info("Finished processing {}".format(video_link))
        else:
            logging.error(
                "Error processing request for {} and video link: {}. Error: {}".format(
                    cid, video_link, status_msg
                ),
            )
            bot.delete_message(cid, reply_message.message_id)
            bot.send_message(cid,
                             "🆘 Looks like something went wrong. "
                             "\n" + status_msg
                             )
