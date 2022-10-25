import os
from pathlib import Path


class PostgresDumper:
    def __init__(self, user: str, password: str, host: str, port: int = 5432):
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def dump(self, database: str, target_file_path: Path):
        os.environ["PGPASSWORD"] = self.password
        os.system(
            f"pg_dump -U {self.user} -h {self.host} -p {self.port} {database} > {target_file_path}"
        )


if __name__ == "__main__":
    dumper = PostgresDumper(user="", password="", host="", port=5432)
    dumper.dump("postres", Path("./test.sql"))
