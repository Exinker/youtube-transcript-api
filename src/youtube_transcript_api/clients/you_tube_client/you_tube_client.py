import logging
import re

import aiohttp

from youtube_transcript_api.clients.you_tube_client.exceptions import (
    YouTubeBlockError,
    YouTubeRequestError,
    YouTubeClientError,
)


LOGGER = logging.getLogger('youtube-transcript-api')


class YouTubeClient:

    URL = 'https://www.youtube.com/watch?v={video_id}'

    def __init__(
        self,
        session: aiohttp.ClientSession,
    ):
        self.session = session

    async def fetch_api_key(
        self,
        video_id: str,
    ) -> str:

        try:
            async with self.session.get(
                url=self.URL.format(video_id=video_id),
            ) as response:
                if response.status != 200:
                    if response.status == 429:
                        raise YouTubeBlockError
                    raise YouTubeRequestError
                
                html = await response.text()
        except aiohttp.ClientResponseError as error:
            raise YouTubeClientError from error
        except YouTubeClientError as error:
            raise
        except Exception as error:
            raise YouTubeClientError from error

        try:
            api_key = self.extract_api_key(html)
        except Exception as error:
            print()
            raise YouTubeClientError from error
        else:
            return api_key

    def extract_api_key(
        self,
        __html: str,
    ) -> str:

        match = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', __html)
        if match:
            api_key = match.group(1)
            return api_key

        raise YouTubeClientError
