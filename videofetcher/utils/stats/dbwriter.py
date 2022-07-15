from abc import ABC, abstractmethod
from cgi import test
from datetime import datetime
import logging
from sqlite3 import Timestamp
import time
from telegram import user
from telegram.message import Message
import re, enum, elasticsearch, json
from utils.config_provider import es_config, json_config

class Outputs(enum.Enum):
    NONE = -1
    STDOUT = 0
    ELASTICSEARCH = 1
    JSON = 2

class AbstractDB:
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def write_msg(self, msg : Message) -> None:
        pass

class BashOutput(AbstractDB):
    def __init__(self) -> None:
        super().__init__()

    def write_msg(self, msg: Message) -> None:
        text = msg.text
        user = msg.from_user
        chat_id = msg.chat_id
        timestamp = int(time.time())
        ress = re.findall(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", text)
        if len(ress) > 0:
            link = ress[0]
            title = " ".join(text.replace(ress[0], "").split(" "))
        else:
            link = None
            title = None
        
        logging.info(f"text: {text}\nuser: {user}\nchat_id: {chat_id}\ntimestamp: {timestamp}\nlink: {link}\ntitle: {title}\n")

class NDJsonOutput(AbstractDB):
    def __init__(self) -> None:
        self.path = json_config("PATH")

    def write_msg(self, msg: Message) -> None:
        body = {
            "text" : msg.text,
            "userinfo" : msg.from_user.to_dict(),
            "chat_id" : msg.chat_id,
            "timestamp" : str(datetime.utcnow())
        }
        ress = re.findall(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", msg.text)
        if len(ress) > 0:
            body.update({"video" : {
                "link" : ress[0],
                "title" : " ".join(msg.text.replace(ress[0], "").split(" "))
            }})
        with open(self.path, "a") as file:
            text = json.dumps(body)
            file.write(f"{text}\n")

class ElasticOutput(AbstractDB):
    def __init__(self) -> None:
        self.index = es_config("INDEX")
        self.es = elasticsearch.Elasticsearch(es_config("HOST"))

    def write_msg(self, msg: Message) -> None:
        body = {
            "text" : msg.text,
            "userinfo" : msg.from_user.to_dict(),
            "chat_id" : msg.chat_id,
            "timestamp" : datetime.now()
        }
        ress = re.findall(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", msg.text)
        if len(ress) > 0:
            body.update({"video" : {
                "link" : ress[0],
                "title" : " ".join(msg.text.replace(ress[0], "").split(" "))
            }})
        self.es.index(self.index, body)
