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


async def fetch_transcipt(
    video_id: str,
) -> Transcript:

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
                'Fetching YouTube api key failed',
                extra=dict(
                    video_id=video_id,
                    error=str(error),
                )
            )
            raise
        else:
            LOGGER.info(
                'YouTube api key fetched successfully',
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
                'Fetching caption tracks failed',
                extra=dict(
                    video_id=video_id,
                    error=str(error),
                ),
            )
            raise
        else:
            LOGGER.info(
                'Caption tracks fetched successfully',
                extra=dict(
                    video_id=video_id,
                )
            )
            if LOGGER.isEnabledFor(logging.DEBUG):
                filedir = CAHCE_DIR / video_id
                filedir.mkdir(parents=True, exist_ok=True)

                with open(filedir / 'caption_tracks.json', 'w') as file:
                    json.dump(caption_tracks, file, indent=2)

        try:
            transcript = await Transcript.create(
                session=session,
                video_id=video_id,
                caption_track=caption_tracks[0],
            )
        except YouTubeClientError as error:
            LOGGER.error(
                'Fetching transcript failed',
                extra=dict(
                    video_id=video_id,
                    error=str(error),
                ),
            )
            raise
        except Exception as error:
            LOGGER.error(
                'Unknown error',
                extra=dict(
                    video_id=video_id,
                    error=str(error),
                ),
            )
            raise
        else:
            LOGGER.info(
                'Transcript fetched successfully',
                extra=dict(
                    video_id=video_id,
                ),
            )

        return transcript


async def main() -> None:

    with open('data.json', 'r') as file:
        data = json.load(file)

    for datum in data:
        video_id = datum['video_id']

        transcript = await fetch_transcipt(
            video_id=video_id,
        )

        filedir = CAHCE_DIR / video_id / 'transcript'
        filedir.mkdir(parents=True, exist_ok=True)
        with open(filedir / 'result.json', 'w') as file:
            json.dump(transcript.model_dump(), file, indent=2, ensure_ascii=False)
        with open(filedir / 'result.txt', 'w') as file:
            text = '\n'.join([
                '{created_at} - {text}'.format(
                    created_at=snippet.created_at,
                    text=snippet.text,
                )
                for snippet in transcript.snippets
            ])
            file.write(text)


if __name__ == '__main__':
    asyncio.run(main())
