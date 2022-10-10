import logging
from pathlib import Path

from cronbackup.CronBackup import CronBackup

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config_file_path = Path('./config.yaml')
    cron_backup = CronBackup(config_file_path)
    cron_backup.run()
