import logging

from config import bot_cfg





# Return chat ID for an update object
def get_chat_id(update=None):
    if update.message:
        return update.message.chat_id
    elif update.callback_query:
        return update.callback_query.from_user["id"]


# Handle all telegram and telegram.ext related errors
def handle_telegram_error(update, error):
    error_str = "Update '%s' caused error '%s'" % (update, error)
    logging.error(error_str)
