class FileIsTooLargeException(ValueError):
    pass


class DownloadError(ValueError):
    pass


class TiktokUrlException(Exception):
    def __init__(self, message) -> None:
        super().__init__("Can't download video from this url. Try another tiktok or try again later")


class UrlException(Exception):
    def __init__(self, message) -> None:
        super().__init__("Can't download video from this url. Check if url is correct")
