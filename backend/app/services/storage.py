from google.cloud import storage as gcs
from app.config import settings


def get_gcs_client() -> gcs.Client:
    client = gcs.Client(
        project="dailycinema",
    )
    client._http._auth_request.session.verify = False
    client._connection.API_BASE_URL = settings.gcs_endpoint
    return client


def ensure_bucket(client: gcs.Client, bucket_name: str) -> gcs.Bucket:
    bucket = client.bucket(bucket_name)
    if not bucket.exists():
        bucket = client.create_bucket(bucket_name)
    return bucket
