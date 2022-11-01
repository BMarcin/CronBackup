import logging
import os
from pathlib import Path

from cronbackup.CronBackupPlugins import CronBackupPlugin


class PostgresDumper(CronBackupPlugin):
    def __init__(self, user: str, password: str, host: str, port: int = 5432, *args, **kwargs):
        super().__init__()

        self.user = user
        self.password = password
        self.host = host
        self.port = port

        self._target_file_path = None

    def run(self, database: str, target_file_path: Path, *args, **kwargs):
        logging.info(f"Dumping database {database} to {target_file_path}")
        os.environ["PGPASSWORD"] = self.password
        os.system(
            f"pg_dump -U {self.user} -h {self.host} -p {self.port} {database} > {target_file_path}"
        )
        self._target_file_path = target_file_path

    def cleanup(self):
        logging.info(f"Removing {self._target_file_path}")
        os.remove(self._target_file_path)


if __name__ == "__main__":
    dumper = PostgresDumper(user="", password="", host="", port=5432)
    dumper.run("postgres", Path("./test.sql"))
