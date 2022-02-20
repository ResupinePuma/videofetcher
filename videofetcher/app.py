#!/usr/bin/python3
"""
python3 app.py
"""
from telegram.ext import CommandHandler, Updater
from utils import init_logger, config_provider, logging_provider
from bot.message_handler import GenericMessageHandler

if __name__ == "__main__":
    config_provider.init_config()
    init_logger()

    updater = Updater(token=config_provider.tg_config("TELEGRAM_BOT_TOKEN"), use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_error_handler(logging_provider.handle_telegram_error)
    GenericMessageHandler(dispatcher)

    updater.start_polling()
    updater.idle()
    
    # Add command handlers to dispatcher
    #dispatcher.add_handler(CommandHandler("start", start_cmd))
    #dispatcher.add_handler(CommandHandler("restart", restart_cmd, pass_chat_data=True))
    # dispatcher.add_handler(
    #     CommandHandler("shutdown", shutdown_cmd, pass_chat_data=True)
    # )

    # Register message handler

