from datetime import datetime
import os
import json
import requests
import boto3

def get_region():
    token_url = "http://169.254.169.254/latest/api/token"
    metadata_url = "http://169.254.169.254/latest/meta-data/placement/region"

    try:
        # Fetch the token
        token_response = requests.put(token_url, headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"})
        token_response.raise_for_status()
        token = token_response.text

        # Fetch the region using the obtained token
        region_response = requests.get(metadata_url, headers={"X-aws-ec2-metadata-token": token}, timeout=1)
        region_response.raise_for_status()
        return region_response.text
    except requests.RequestException as e:
        print(f"An error occurred while fetching the region. Defaulting to us-east-1: {e}")
        return "us-east-1"

def get_bucket_with_prefix(prefix):
    s3 = boto3.client('s3', region_name=region)
    buckets = s3.list_buckets()
    for bucket in buckets['Buckets']:
        if bucket['Name'].startswith(prefix):
            return bucket['Name']
    return None

now = datetime.now()
dttm = now.strftime("%Y-%m-%dT%H:%M:%S.%f")
region = get_region() or "us-east-1"
bucket_prefix = 'lookoutvision'
bucket = get_bucket_with_prefix(bucket_prefix)
datasets = ["train", "test"]
directory = 'lab-codes'  # replace with the name of the local folder where the data is.

for ds in datasets:
    print(ds)
    folders = os.listdir(f"./{ds}")

    with open(f"{ds}.manifest", "w") as f:
        for folder in folders:
            print(folder)
            label = 0 if folder == "anomaly" else 1
            files = os.listdir(f"./{ds}/{folder}")

            for file in files:
                manifest = {
                    "source-ref": f"s3://{bucket}/{ds}/{folder}/{file}",
                    "auto-label": label,
                    "auto-label-metadata": {
                        "confidence": 1,
                        "job-name": "labeling-job/auto-label",
                        "class-name": folder,
                        "human-annotated": "yes",
                        "creation-date": dttm,
                        "type": "groundtruth/image-classification"
                    }
                }
                f.write(json.dumps(manifest) + "\n")