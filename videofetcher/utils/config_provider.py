import configparser
import os

__default_config = {
    'TELEGRAM' : {
        'TELEGRAM_BOT_TOKEN' : '0000000000:11111111111111111111111111111111111',
        'TELEGRAM_USER_ID' : '111111111',
    },
    'SYSTEM' : {
        'LOG_LEVEL' : 'INFO',
        'STATS_OUTPUT' : "NONE",
        'VIDEO_FILE_FOLDER' : '/tmp',
        'PROCESSING_TIMEOUT' : '30',  #seconds
        'SPLASH_URL' : 'http://splash:8050',
        'MAX_FILE_SIZE' : '50',
        'PREFERRED_VIDEO_FORMAT' : "mp4",
        "USER_AGENT" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    },
    'ELASTICSEARCH' : {
        "INDEX" : "messages",
        "HOST" : "127.0.0.1:9200"
    },
    'JSON' : {
        "PATH" : "./messages.ndjson",
    }
}

def init_config():
    config = configparser.ConfigParser()
    config.update(__default_config)
    if not os.path.exists("config.ini"):
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

def __config(key : str, group : str):
    c = configparser.ConfigParser()
    c.read("config.ini")
    return c.get(group, key) or None


def tg_config(key : str = "NONE"):
    return __config(key, "TELEGRAM")

def sys_config(key : str = "NONE"):
    return __config(key, "SYSTEM")

def es_config(key : str = "NONE"):
    return __config(key, "ELASTICSEARCH")

def json_config(key : str = "NONE"):
    return __config(key, "JSON")
