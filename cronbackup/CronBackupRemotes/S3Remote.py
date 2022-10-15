import logging
from pathlib import Path

from boto3.s3.transfer import TransferConfig

from cronbackup.CronBackupRemotes import CronBackupRemote
import boto3


class S3Remote(CronBackupRemote):
    def __init__(self, config: dict, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.config = config
        assert set(self.config.keys()) == {
            "endpoint",
            "region",
            "multipart_chunk_size",
            "type",
            "secret_access_key",
            "access_key_id",
            "bucket",
        }, "Invalid config keys for S3Remote"

        assert self.config["type"] == "s3", "Invalid type for S3Remote"

        logging.info("Initializing S3Remote")

        self.name = kwargs.get("name")
        self.access_key_id = self.config["access_key_id"]
        self.secret_access_key = self.config["secret_access_key"]
        self.bucket = self.config["bucket"]
        self.region = self.config["region"]
        self.endpoint = self.config["endpoint"]
        self.multipart_chunk_size = self.config["multipart_chunk_size"]

        logging.info("Initializing S3 client")
        self.s3_session = boto3.Session(
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region,
        )

        logging.info("Initializing S3 resource")
        self.s3_resource = self.s3_session.resource("s3", endpoint_url=self.endpoint)
        self.s3_client = self.s3_session.client("s3", endpoint_url=self.endpoint)

        # if bucket doesn't exist, create it
        if self.bucket not in [
            bucket.name for bucket in self.s3_resource.buckets.all()
        ]:
            logging.info("Bucket {} does not exist, creating it".format(self.bucket))
            self.s3_resource.create_bucket(
                Bucket=self.bucket,
                CreateBucketConfiguration={"LocationConstraint": self.region},
            )
            self.s3_client.put_public_access_block(
                Bucket=self.bucket,
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": True,
                    "IgnorePublicAcls": True,
                    "BlockPublicPolicy": True,
                    "RestrictPublicBuckets": True,
                },
            )

    def upload(self, source_path: Path, destination_path: Path, *args, **kwargs):
        self.s3_client.upload_file(
            Filename=str(source_path),
            Bucket=self.bucket,
            Key=str(destination_path),
            Config=TransferConfig(multipart_chunksize=self.multipart_chunk_size),
        )

    def get_remote_items(self, destination_path: Path, *args, **kwargs):
        if self.bucket in [bucket.name for bucket in self.s3_resource.buckets.all()]:
            return [
                item.key
                for item in self.s3_resource.Bucket(self.bucket).objects.filter(
                    Prefix=str(destination_path)
                )
            ]
        else:
            return []

    def delete_remote_item(self, destination_path: Path, *args, **kwargs):
        self.s3_resource.Object(self.bucket, str(destination_path)).delete()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    config = {
        "name": "mblabs-test",
        "type": "s3",
        "access_key_id": "",
        "secret_access_key": "",
        "bucket": "mblabs-test2",
        "region": "eu-central-1",
        "endpoint": "https://s3.amazonaws.com",
        "multipart_chunk_size": 1024,
    }
    s3_remote = S3Remote(config)
    # s3_remote.upload(
    #     source_path=Path("../../README.md"),
    #     destination_path=Path("README.md")
    # )
