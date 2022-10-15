from cronbackup.CronBackupAlerts.CronBackupAlert import CronBackupAlert
import requests


class Webhook(CronBackupAlert):
    def __init__(self, config: dict, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.config = config
        assert set(self.config.keys()) == {"url"}, "Invalid config keys for Webhook"
        self.url = self.config["url"]

    def send_alert(self, service: str, message: str, *args, **kwargs):
        requests.post(self.url, json={"text": message, "service": service})
