from bot.media_request_handler import MediaRequestHandler
from config.bot_config import OUTPUT_FORMAT, AUDIO_OUTPUT_DIR
import speedtest, hashlib, os

s = speedtest.Speedtest()
s.get_best_server()
s.download()

print(s.results.dict()['download'])

def gethashname(name):
    return hashlib.md5(name.encode("utf-8")).hexdigest()

def GetExtractParams(id):
    return {
        "outtmpl": os.path.join(AUDIO_OUTPUT_DIR, gethashname(id)+".mp4"),
        "format": "best[height<=960][ext=mp4],best[ext=unknown_video],bestvideo[height<=480][ext=mp4]+worstaudio[ext=m4a]",
        "socket_timeout": 10,
        "throttled-rate" : s.results.dict()['download'],
        'ratelimit': s.results.dict()['download'],
        "retries": 10,
        "verbose" : True,
        "prefer_ffmpeg": True,
        "keepvideo": True,
    }


def create_extraction_params(notifier, id):
    extraction_param = GetExtractParams(id)
    return MediaRequestHandler(extraction_param, notifier)


def is_yt_video(extractor):
    return extractor == "youtube"
