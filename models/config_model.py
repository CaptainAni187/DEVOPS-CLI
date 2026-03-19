from dataclasses import dataclass
from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class Config:
    project_name: str
    log_path: str
    backup_dir: str
    monitor_interval: int
    log_level: LogLevel = LogLevel.INFO

    def __post_init__(self):
        if isinstance(self.log_level, str):
            self.log_level = LogLevel(self.log_level.upper())