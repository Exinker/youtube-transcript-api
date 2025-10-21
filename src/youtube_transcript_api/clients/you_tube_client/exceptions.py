
class YouTubeClientError(Exception):
    pass


class YouTubeParsingError(YouTubeClientError):
    pass


class YouTubeRequestError(YouTubeClientError):
    pass


class YouTubeBlockError(YouTubeClientError):
    pass
