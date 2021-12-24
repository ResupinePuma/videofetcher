import logging
import os
import sys
import threading
import time

from bot.video_bot import updater
from . import get_chat_id, bot_cfg

# Decorator to restrict access if user is not the same as in config
def restrict_access(func):
    def _restrict_access(updater, bot=None, update=None):
        chat_id = updater.message.chat_id
        if str(chat_id) != bot_cfg("TELEGRAM_USER_ID"):
            # Inform owner of bot
            msg = "Access denied for user %s" % chat_id
            #bot.send_message(bot_cfg("TELEGRAM_USER_ID"), text=msg)

            logging.info(msg)
            return
        else:
            return func(updater, bot=None, update=None)

    return _restrict_access

# This needs to be run on a new thread because calling 'updater.stop()' inside a
# handler (shutdown_cmd) causes a deadlock because it waits for itself to finish
def shutdown():
    updater.stop()
    updater.is_idle = False


def start_cmd(updater, bot=None, update=None):
    logging.info("PodTubeBot is running!")


@restrict_access
def shutdown_cmd(bot, update, chat_data):
    logging.info("Shutting down...")

    # See comments on the 'shutdown' function
    threading.Thread(target=shutdown).start()

@restrict_access
def restart_cmd(updater, bot=None, update=None):
    logging.info("Bot is restarting...")

    time.sleep(0.2)
    os.execl(sys.executable, sys.executable, *sys.argv)
