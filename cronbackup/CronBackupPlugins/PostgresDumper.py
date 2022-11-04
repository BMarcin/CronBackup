import logging
import os
import subprocess
from pathlib import Path

from cronbackup.CronBackupPlugins import CronBackupPlugin


class PostgresDumper(CronBackupPlugin):
    def __init__(
        self, user: str, password: str, host: str, port: int = 5432, *args, **kwargs
    ):
        super().__init__()

        self.user = user
        self.password = password
        self.host = host
        self.port = port

        self._target_file_path = None

    def run(self, database: str, target_file_path: Path, *args, **kwargs):
        logging.info(f"Dumping database {database} to {target_file_path}")
        os.environ["PGPASSWORD"] = self.password
        if not target_file_path.parent.exists():
            target_file_path.parent.mkdir(parents=True, exist_ok=True)

        # execute pg_dump and get the output
        pg_dump = subprocess.Popen(
            [
                "/bin/bash",
                "-c",
                "pg_dump",
                "-U",
                self.user,
                "-h",
                self.host,
                "-p",
                str(self.port),
                database,
                "-f",
                str(target_file_path),
            ],
            stdout=subprocess.PIPE,
        )
        output, error = pg_dump.communicate()
        if error:
            logging.error(f"Error while dumping database {database}: {error}")
            raise Exception(f"Error while dumping database {database}: {error}")
        else:
            logging.info(f"Database {database} dumped successfully")
        self._target_file_path = target_file_path

    def cleanup(self):
        logging.info(f"Removing {self._target_file_path}")
        self._target_file_path.unlink()


if __name__ == "__main__":
    dumper = PostgresDumper(user="", password="", host="", port=5432)
    dumper.run("postgres", Path("./test.sql"))
