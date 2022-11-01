from abc import ABC


class CronBackupPlugin(ABC):
    def __init__(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        pass

    def cleanup(self, *args, **kwargs):
        pass
