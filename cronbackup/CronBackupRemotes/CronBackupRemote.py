# abstract class Remote
from abc import ABC
from pathlib import Path


class CronBackupRemote(ABC):
    def __init__(self, config: dict, *args, **kwargs):
        pass

    def upload(
            self,
            source_path: Path,
            destination_path: Path,
            *args,
            **kwargs
    ):
        pass

    def get_remote_items(
            self,
            destination_path: Path,
            *args,
            **kwargs
    ):
        pass

    def delete_remote_item(
            self,
            destination_path: Path,
            *args,
            **kwargs
    ):
        pass
