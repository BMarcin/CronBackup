import logging
from pathlib import Path

from cronbackup.CronBackup import CronBackup

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    config_file_path = Path("./config.yaml")
    if not config_file_path.exists():
        logging.info("Config file not found. Creating empty...")
        config_file_path.write_text("remotes:\nitems:\nalerts:\n")

    cron_backup = CronBackup(config_file_path)
    cron_backup.run()
