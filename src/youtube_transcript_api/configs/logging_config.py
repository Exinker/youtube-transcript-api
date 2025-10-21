from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingLevel(Enum):

    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class LoggingConfig(BaseSettings):

    level: LoggingLevel = Field(LoggingLevel.INFO, alias='LOGGING_LEVEL')
    file_bytes: int = Field(1024*1024, alias='LOGGING_FILE_BYTES')
    file_backups: int = Field(3, alias='LOGGING_FILE_COUNTS')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


LOGGING_CONFIG = LoggingConfig()
