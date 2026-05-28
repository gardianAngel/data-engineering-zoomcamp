import base64
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import time

from google.cloud import storage
from google.api_core.exceptions import NotFound, Forbidden

# Change this to your bucket name
BUCKET_NAME = "unyime-kestra"

# If you authenticated through the GCP SDK you can comment out these two lines
# -CREDENTIALS_FILE = "gcs.json"
# -client = storage.Client.from_service_account_json(CREDENTIALS_FILE)
# If commented initialize client with the following
# client = storage.Client(project='zoomcamp-mod3-datawarehouse')

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-"
MONTHS = [f"{i:02d}" for i in range(1, 7)]
DOWNLOAD_DIR = "."
CHUNK_SIZE = 8 * 1024 * 1024


def load_credentials_from_env_file():
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        return

    repo_root = Path(__file__).resolve().parents[2]
    env_encoded_path = repo_root / ".env_encoded"
    if not env_encoded_path.exists():
        return

    encoded = None
    for line in env_encoded_path.read_text().splitlines():
        if line.startswith("SECRET_GOOGLE_APPLICATION_CREDENTIALS="):
            _, value = line.split("=", 1)
            encoded = value.strip()
            break

    if not encoded:
        return

    try:
        decoded = base64.b64decode(encoded)
    except Exception as exc:
        print(f"Could not decode SECRET_GOOGLE_APPLICATION_CREDENTIALS: {exc}")
        return

    credential_path = repo_root / ".gcp_service_account.json"
    credential_path.write_bytes(decoded)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credential_path)
    print(f"Loaded Google credentials from {env_encoded_path}")


def get_gcs_client():
    load_credentials_from_env_file()
    try:
        return storage.Client()
    except Exception as exc:
        print(f"Could not create Google Cloud Storage client: {exc}")
        sys.exit(1)


client = get_gcs_client()

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_file(month):
    url = f"{BASE_URL}{month}.parquet"
    file_path = os.path.join(DOWNLOAD_DIR, f"yellow_tripdata_2024-{month}.parquet")

    try:
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, file_path)
        print(f"Downloaded: {file_path}")
        return file_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None


def create_bucket(bucket_name):
    try:
        bucket = client.get_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' exists and is accessible. Proceeding...")
        return bucket
    except NotFound:
        bucket = client.create_bucket(bucket_name)
        print(f"Created bucket '{bucket_name}'")
        return bucket
    except Forbidden:
        print(
            f"A bucket with the name '{bucket_name}' exists, but it is not accessible. Bucket name is taken. Please try a different bucket name."
        )
        sys.exit(1)


def verify_gcs_upload(blob_name):
    return storage.Blob(bucket=bucket, name=blob_name).exists(client)


def upload_to_gcs(file_path, max_retries=3):
    blob_name = os.path.basename(file_path)
    blob = bucket.blob(blob_name)
    blob.chunk_size = CHUNK_SIZE

    for attempt in range(max_retries):
        try:
            print(f"Uploading {file_path} to {BUCKET_NAME} (Attempt {attempt + 1})...")
            blob.upload_from_filename(file_path)
            print(f"Uploaded: gs://{BUCKET_NAME}/{blob_name}")

            if verify_gcs_upload(blob_name):
                print(f"Verification successful for {blob_name}")
                return
            else:
                print(f"Verification failed for {blob_name}, retrying...")
        except Exception as e:
            print(f"Failed to upload {file_path} to GCS: {e}")

        time.sleep(5)

    print(f"Giving up on {file_path} after {max_retries} attempts.")


def main(months=MONTHS):
    global bucket
    bucket = create_bucket(BUCKET_NAME)

    with ThreadPoolExecutor(max_workers=4) as executor:
        file_paths = list(executor.map(download_file, months))

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(upload_to_gcs, filter(None, file_paths))

    print("All files processed and verified.")


if __name__ == "__main__":
    main()
