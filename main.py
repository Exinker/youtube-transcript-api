import asyncio
import json
import logging
from collections.abc import Sequence
from pathlib import Path

import aiohttp

from youtube_transcript_api.clients import (
    InnerTubeClient,
    InnerTubeClientError,
    YouTubeClient,
    YouTubeClientError,
)
from youtube_transcript_api.transcripts import Transcript

CAHCE_DIR = Path.cwd() / '.cache'
CAHCE_DIR.mkdir(parents=True, exist_ok=True)

LOGGER = logging.getLogger('youtube-transcript-api')


async def main(
    video_id: str,
) -> Sequence[Transcript]:

    filedir = CAHCE_DIR / video_id
    filedir.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:

        try:
            you_tube_client = YouTubeClient(
                session=session,
            )
            api_key = await you_tube_client.fetch_api_key(
                video_id=video_id,
            )
        except YouTubeClientError as error:
            LOGGER.error(
                'Fetching api-key is failed',
                extra=dict(
                    video_id=video_id,
                    error=str(error),
                )
            )
            raise
        else:
            LOGGER.info(
                'Youtube api-key is fetched successfully',
                extra=dict(
                    video_id=video_id,
                ),
            )

        try:
            inner_tube_client = InnerTubeClient(
                session=session,
                api_key=api_key,
            )
            caption_tracks = await inner_tube_client.fetch_caption_tracks(
                video_id=video_id,
            )
        except InnerTubeClientError as error:
            LOGGER.error(
                'Fetching caption tracks is failed',
                extra=dict(
                    video_id=video_id,
                    error=str(error),
                ),
            )
            raise
        else:
            LOGGER.info(
                'Caption tracks are fetched successfully',
                extra=dict(
                    video_id=video_id,
                )
            )
            if LOGGER.isEnabledFor(logging.DEBUG):
                with open(filedir / 'caption_tracks.json', 'w') as file:
                    json.dump(caption_tracks, file, indent=2)

        try:
            transcripts = await asyncio.gather(*[
                Transcript.create(
                    session=session,
                    video_id=video_id,
                    caption_track=caption_track,
                )
                for caption_track in caption_tracks
            ])
        except Exception as error:
            raise
        else:
            LOGGER.info(
                'Transcripts are fetched successfully',
                extra=dict(
                    video_id=video_id,
                ),
            )
            if LOGGER.isEnabledFor(logging.DEBUG):
                with open(filedir / 'transcripts.json', 'w') as file:
                    json.dump([
                        transcript.model_dump()
                        for transcript in transcripts
                    ], file, indent=2, ensure_ascii=False)

        return transcripts


if __name__ == '__main__':
    video_id = 'eVcx6qZfU-M'
    transcripts = asyncio.run(main(
        video_id=video_id,
    ))

    filedir = CAHCE_DIR / video_id / 'texts'
    filedir.mkdir(parents=True, exist_ok=True)
    for i, transcript in enumerate(transcripts, start=1):
        text = '\n'.join([
            '{created_at} - {text}'.format(
                created_at=snippet.created_at,
                text=snippet.text,
            )
            for snippet in transcript.snippets
        ])

        with open(filedir / f'{i}.txt', 'w') as file:
            file.write(text)
