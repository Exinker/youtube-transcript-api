from collections.abc import Mapping, Sequence
from typing import Any, NewType

import aiohttp

Second = NewType('Second', float)


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

    async def extract_caption_tracks(
        self,
        video_id: str,
    ) -> Sequence[Mapping[str, Any]]:

        data = await self._fetch_data(
            video_id=video_id,
        )

        caption_tracks = data.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks')
        if caption_tracks is None:
            raise ValueError

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
