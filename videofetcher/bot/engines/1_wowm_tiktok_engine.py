import logging
from bot.engines.abstract import Video, AbstractEngine
from utils import exceptions, sys_config, format_size
import re, requests, hashlib, os, random
from urllib.parse import quote

PHRASES = [
    "📞 Asking Xi's permission to download",
    "🤙 Contacting with agent in TT headquaters",
    "✂️ Cutting TT webpage",
    "📛 Breaking through chinese firewall",
    "🔎 Searching video"
]

class TiktokEngine(AbstractEngine):
    def __init__(self) -> None:
        super().__init__()

    def consist_type(self, url) -> bool:
        tiktok = re.findall(r"\/\/.*vm.tiktok\.com\/",url)
        if len(tiktok) > 0:
            return True
        else:
            return False

    def proceed(self, url, notifier, session=requests.Session()) -> Video:
        self.notifier = notifier
        self.session = session
        video = Video(url=url)
        if not self.consist_type(url):
            return video

        name_hash = self.name_to_hash(video.url)
        if os.path.exists(self.get_downloaded_file_abspath(name_hash)):
            path = self.get_downloaded_file_abspath(name_hash)
            file_size = os.path.getsize(path)
            video.size = file_size
            video.path = path
            logging.info("Return saved video: {}".format(path))
            return video

        try:
            if len(re.findall(r'(.*tiktok\.com\/@.*\/live)', url)) > 0:
                raise exceptions.DownloadError("Can't download tiktok live stream. Try another url")

            self.notifier.update_status(random.choice(PHRASES))

            video_link, video_id = None, None
            for i in range(3):
                self.notifier.make_progress_bar(i*10)

                tt_url = f"https://snaptik.app/ru"
                response = requests.post(f"{sys_config('SPLASH_URL')}/execute", json={
                    "url" : "https://snaptik.app/ru",
                    "lua_source" : f"""
                    function main(splash, args)
                        splash:on_request(function(request)
                            request.headers['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
                        end)
                        splash:go(args.url)
                        assert(splash:wait(0.5))
                        splash:runjs('document.getElementsByName("url")[0].value="{url}";document.getElementsByTagName("form")[0].submit();')
                        assert(splash:wait(1)) 
                        local title = splash:evaljs('document.getElementsByClassName("snaptik-middle center")[0].children[1].innerText')                       
                        return {{
                            html = splash:html(),
                            title = title
                        }}
                    end
                    """
                })

                self.notifier.make_progress_bar(30)
                html = response.json().get("html")
                if not html: 
                    continue  

                matches_id = re.search(r'<a href="(.*)" onclick',html,re.IGNORECASE)
                if matches_id:
                    video_link = matches_id.group(1).split('"')[0]
                    video.name = response.json().get("title")
                    break

            if not video_link:              
                raise exceptions.DownloadError("Can't download from url. Check if this url is correct")
            
            response = self.session.get(video_link, timeout=10)
            self.notifier.make_progress_bar(80)        
            if response.status_code < 400 and response.content:
                path = self.get_downloaded_file_abspath(name_hash)
                with open(path, "wb") as f:
                    f.write(response.content)
                video.path = path
                video.size = os.path.getsize(path)
            
            self.notifier.make_progress_bar(100)
        except Exception as ex:
            logging.exception(ex)
            video.exception = ex
        
        return video

def proceed(url, notifier, session) -> Video:
    return TiktokEngine().proceed(url, notifier, session)



