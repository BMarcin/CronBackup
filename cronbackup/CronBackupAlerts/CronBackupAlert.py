from abc import ABC


class CronBackupAlert(ABC):
    def __init__(self, config: dict, *args, **kwargs):
        pass

    def send_alert(self, service: str, message: str, *args, **kwargs):
        pass
