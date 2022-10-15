from datetime import datetime
import logging
from pathlib import Path
from typing import Union
import tarfile
import yaml
from croniter import croniter
import importlib

remotes_mapping_dict = {"s3": "cronbackup.CronBackupRemotes.S3Remote"}

alerts_mapping_dict = {"webhook": "cronbackup.CronBackupAlerts.Webhook"}


class CronBackup:
    def __init__(
        self,
        config_path: Path,
        remotes_mapping: Union[dict, None] = None,
        alerts_mapping: Union[dict, None] = None,
    ):
        logging.info(f"Initializing CronBackup with config_path: {config_path}")
        self.config_path = config_path

        logging.info("Reading config file")
        self.config = self.read_config()

        self.config_remotes = self.config["remotes"]
        self.config_items = self.config["items"]
        self.config_alerts = self.config["alerts"]

        self.remotes = {}

        if remotes_mapping is None:
            self.remotes_mapping = remotes_mapping_dict
            logging.info("Using default remotes_mapping")
        else:
            self.remotes_mapping = remotes_mapping
            logging.info("Using custom remotes_mapping")

        if alerts_mapping is None:
            self.alerts_mapping = alerts_mapping_dict
            logging.info("Using default alerts_mapping")
        else:
            self.alerts_mapping = alerts_mapping
            logging.info("Using custom alerts_mapping")

        logging.debug(
            "Initialized {} remotes and {} items".format(
                len(self.config_remotes), len(self.config_items)
            )
        )

    def read_config(self):
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
        return config

    @staticmethod
    def get_target_backup_file_name(item_name: str):
        return (
            item_name + "_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".tar.gz"
        )

    @staticmethod
    def pack_files(input_path: Path, output_path: Path):
        logging.info(f"Packing files from {input_path} to {output_path}")
        with tarfile.open(output_path, "w:gz") as tar:
            for file in input_path.rglob("**"):
                logging.debug(f"Adding {file} to {output_path}")
                tar.add(file, arcname=file.relative_to(input_path))

    def get_jobs(self):
        for item in self.config_items:
            if croniter.match(item["cron"], datetime.now()):
                yield item

    def send_alerts(self, service: str, message: str):
        for alert in self.config_alerts:
            logging.info("Importing alert module {}".format(alert["type"]))
            alert_class = importlib.import_module(self.alerts_mapping[alert["type"]])
            module_name = alert_class.__name__.split(".")[-1]
            alert_class_obj = getattr(alert_class, module_name)

            logging.info("Initializing alert {}".format(alert["type"]))
            current_alert = alert_class_obj(alert["config"])

            logging.info("Sending alert to {}".format(alert))
            current_alert.send_alert(service=service, message=message)

    def run(self):
        try:
            logging.info("Starting CronBackup")
            # list all jobs to be done
            jobs = list(self.get_jobs())
            logging.info(f"Found {len(jobs)} jobs to be done")
            for job in jobs:
                logging.info("Starting a job {}".format(job["name"]))
                # tar gz all files
                source_files_path = Path(job["source"])
                target_backup_file_path = Path(
                    job["local_path"]
                ) / self.get_target_backup_file_name(job["name"])

                if not target_backup_file_path.parent.exists():
                    target_backup_file_path.parent.mkdir(parents=True)
                CronBackup.pack_files(source_files_path, target_backup_file_path)
                logging.info("Finished packing files")

                # delete old backups
                local_files = list(
                    target_backup_file_path.parent.glob(
                        target_backup_file_path.name.split("_")[0] + "*"
                    )
                )
                local_files.sort()

                if len(local_files) > job["keep_local"]:
                    for file in local_files[: -job["keep_local"]]:
                        logging.info(f"Deleting {file}")
                        file.unlink()

                # upload to remote
                if target_backup_file_path.exists():
                    for remote in job["remotes"]:
                        logging.info("Importing remote module {}".format(remote))
                        remote_class = importlib.import_module(
                            self.remotes_mapping[self.config_remotes[remote]["type"]]
                        )
                        module_name = remote_class.__name__.split(".")[-1]
                        remote_class_obj = getattr(remote_class, module_name)

                        logging.info("Initializing remote {}".format(remote))
                        current_remote = remote_class_obj(
                            self.config_remotes[remote], name=remote
                        )

                        logging.info("Uploading to remote {}".format(remote))
                        current_remote.upload(
                            source_path=target_backup_file_path,
                            destination_path=job["name"]
                            + "/"
                            + target_backup_file_path.name,
                        )

                        # delete old backups on remote
                        current_remote_files = current_remote.get_remote_items(
                            destination_path=job["name"]
                        )
                        current_remote_files.sort()
                        if len(current_remote_files) > job["keep_remote"]:
                            for file in current_remote_files[: -job["keep_remote"]]:
                                # print(file.keys())
                                logging.info(f"Deleting {file} from remote {remote}")
                                current_remote.delete_remote_item(file)
                    logging.info("Finished uploading and deleting old backups")
                else:
                    logging.error("Backup file not found")
                    self.send_alerts(
                        service="CronBackup",
                        message="Backup file {} not found".format(
                            target_backup_file_path
                        ),
                    )
        except Exception as e:
            self.send_alerts(service="CronBackup", message=str(e))
            logging.exception(e)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    config_file_path = Path("../../config.yaml")
    cron_backup = CronBackup(config_file_path)
    cron_backup.run()
