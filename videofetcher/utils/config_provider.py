import configparser
import os

__default_config = {
    'TELEGRAM' : {
        'TELEGRAM_BOT_TOKEN' : '0000000000:11111111111111111111111111111111111',
        'TELEGRAM_USER_ID' : '111111111',
    },
    'SYSTEM' : {
        'LOG_LEVEL' : 'INFO',
        'VIDEO_FILE_FOLDER' : '/tmp',
        'PROCESSING_TIMEOUT' : '30',  #seconds
        'SPLASH_URL' : 'http://splash:8050',
        'MAX_FILE_SIZE' : '50',
        'PREFERRED_VIDEO_FORMAT' : "mp4",
        "USER_AGENT" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    }
}

def init_config():
    config = configparser.ConfigParser()
    config.update(__default_config)
    if not os.path.exists("config.ini"):
        with open('config.ini', 'w') as configfile:
            configfile.write(config)

def __config(key : str, group : str):
    c = configparser.ConfigParser()
    c.read("config.ini")
    return c.get(group, key) or None


def tg_config(key : str = "NONE"):
    return __config(key, "TELEGRAM")

def sys_config(key : str = "NONE"):
    return __config(key, "SYSTEM")
