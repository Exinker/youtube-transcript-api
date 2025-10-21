import asyncio
from collections.abc import Mapping, Sequence
from typing import Any, NewType, Self
import xml.etree.ElementTree as ET

import aiohttp
from pydantic import BaseModel

Second = NewType('Second', float)


class Snippet(BaseModel):

    start: Second
    text: str


class Transcript(BaseModel):

    video_id: str
    url: str
    language: str
    language_code: str
    snippets: Sequence[Snippet]

    @classmethod
    async def create(
        cls,
        session: aiohttp.ClientSession,
        video_id: str,
        caption_track: Mapping[str, Any],
    ) -> Self:
        
        url = caption_track['baseUrl'].replace('&fmt=srv3', '')
        language = caption_track.get('name', {}).get('runs', [])[0].get('text', '')
        language_code = caption_track.get('languageCode')

        async with session.get(
            url=url,
        ) as response:
            html = await response.text()

        snippets = await asyncio.to_thread(
            cls.extract_snippets,
            html=html,
        )

        return cls(
            video_id=video_id,
            url=url,
            language=language,
            language_code=language_code,
            snippets=snippets,
        )

    def translate(
        self,
        language_code: str,
    ) -> Self:
        raise NotImplementedError

    @staticmethod
    def extract_snippets(
        html: str,
    ) -> Sequence[Snippet]:
        root = ET.fromstring(html)

        snippets = []
        for item in root.findall('text'):
            snippet = Snippet(
                start=item.get('start'),
                text=item.text,
            )
            snippets.append(snippet)
        return tuple(snippets)
