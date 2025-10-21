import json
import logging
from datetime import datetime, timezone

from youtube_transcript_api.configs import LOGGING_CONFIG


class JsonRecordFormatter(logging.Formatter):

    RECORD_KEYS = {
        'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName',
        'levelname', 'levelno', 'lineno', 'module', 'msecs', 'msg', 'name',
        'pathname', 'relativeCreated', 'process', 'processName', 'stack_info',
        'taskName', 'thread', 'threadName',
    }

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:

        data = dict(
            timestamp=datetime.fromtimestamp(
                timestamp=record.created,
                tz=timezone.utc,
            ).isoformat(),
            level=record.levelname,
            msg=record.msg,
        )

        extra = dict()
        for key, value in record.__dict__.items():
            if key not in self.RECORD_KEYS:
                extra[key] = value

        return json.dumps(dict(
            **data,
            **extra,
        ), ensure_ascii=False)


logger_config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'formatter': {
            '()': JsonRecordFormatter,
        },
    },

    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'level': LOGGING_CONFIG.level.value,
            'filters': [],
            'formatter': 'formatter',
        },
    },

    'loggers': {
        'youtube-transcript-api': {
            'level': logging.DEBUG,
            'handlers': ['stream_handler', ],
            'propagate': True,
        },
    },

}
