import logging

# Handle all telegram and telegram.ext related errors
def handle_telegram_error(update, error):
    error_str = "Update '%s' caused error '%s'" % (update, error)
    logging.error(error_str)