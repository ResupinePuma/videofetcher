class FileIsTooLargeException(ValueError):
    pass


class DownloadError(ValueError):
    pass


class TiktokUrlException(Exception):
    def __init__(self, message="Can't download video from this url. Try another tiktok or try again later") -> None:
        super().__init__(message)


class UrlException(Exception):
    def __init__(self, message="Can't download video from this url. Check if url is correct") -> None:
        super().__init__(message)
