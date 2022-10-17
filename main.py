import logging
from pathlib import Path
import time

from cronbackup.CronBackup import CronBackup

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    config_file_path = Path("./config.yaml")
    if not config_file_path.exists():
        logging.info("Config file not found. Creating empty...")
        config_file_path.write_text("remotes:\nitems:\nalerts:\n")

    last_update_time = config_file_path.stat().st_mtime

    cron_backup = CronBackup(config_file_path)
    while True:
        if config_file_path.stat().st_mtime != last_update_time:
            logging.info("Config file changed. Reloading...")
            cron_backup.reload_config()
            last_update_time = config_file_path.stat().st_mtime
        cron_backup.run()
        time.sleep(60)
