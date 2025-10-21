import logging
from collections.abc import Mapping, Sequence
from typing import Any

import aiohttp

from youtube_transcript_api.clients.inner_tube_client.exceptions import InnerTubeClientError


LOGGER = logging.getLogger('youtube-transcript-api')


class InnerTubeClient:

    URL = 'https://www.youtube.com/youtubei/v1/player?key={api_key}'
    CONTEXT = {'client': {'clientName': 'ANDROID', 'clientVersion': '20.10.38'}}

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str,
    ) -> None:

        self.session = session
        self.api_key = api_key

    @property
    def url(self) -> str:
        return self.URL.format(
            api_key=self.api_key,
        )

    async def fetch_caption_tracks(
        self,
        video_id: str,
    ) -> Sequence[Mapping[str, Any]]:

        try:
            data = await self._fetch_data(
                video_id=video_id,
            )
        except Exception as error:
            LOGGER.error(
                'Fetching innertube data is failed',
                extra=dict(
                    video_id=video_id,
                    error=str(error),
                ),
            )
            raise

        caption_tracks = data.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks')
        if caption_tracks is None:
            LOGGER.error(
                'Caption track list is empty',
                extra=dict(
                    video_id=video_id,
                ),
            )
            raise InnerTubeClientError

        return caption_tracks

    async def _fetch_data(
        self,
        video_id: str,
    ) -> Mapping[str, Any]:

        async with self.session.post(
            url=self.url,
            json={
                'context': self.CONTEXT,
                'videoId': video_id,
            },
        ) as response:
            data = await response.json()

        return data
