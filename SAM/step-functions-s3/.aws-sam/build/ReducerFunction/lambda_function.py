# -----------------------------------------------------------
#    Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#    SPDX-License-Identifier: MIT-0
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy of this
#    software and associated documentation files (the "Software"), to deal in the Software
#    without restriction, including without limitation the rights to use, copy, modify,
#    merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
#    permit persons to whom the Software is furnished to do so.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#    PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
#    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------
import json
import os
import csv
import io

from datetime import datetime
from decimal import Decimal
from typing import Dict, List

import boto3


S3_CLIENT = boto3.client("s3")


def lambda_handler(event: dict, context: dict):
    """Reducer function will read all of the mapped results from S3 and write to DDB.

    Args:
        event (dict): The event payload that arrives after the distributed map run has the
        folllowing structure:

            {
            "MapRunArn": "arn-of-the-map-run",
            "ResultWriterDetails": {
                "Bucket": "bucket-name-where-results-are-written",
                "Key": "results/dee8fb57-3653-3f09-88dd-4f39225d2367/manifest.json",
            },
        }
        context (dict): Lambda context
    """
    print(event)
    results_bucket = event["ResultWriterDetails"]["Bucket"]
    manifest = get_file_from_s3(
        results_bucket,
        event["ResultWriterDetails"]["Key"],
    )

    maniftest_json = json.loads(manifest)

    high_by_month: Dict[str, Dict] = {}

    for result in maniftest_json["ResultFiles"].get("SUCCEEDED", []):
        results = get_file_from_s3(results_bucket, result["Key"])

        for json_result in json.loads(results):

            monthly_highs: Dict[str, Dict] = json.loads(json_result["Output"])

            for month_str, row in monthly_highs.items():
                high_temp = float(row["TEMP"])

                monthly_high = high_by_month.get(month_str)

                if not monthly_high:
                    high_by_month[month_str] = row
                    continue

                if high_temp > float(monthly_high["TEMP"]):
                    high_by_month[month_str] = row

    _write_results_to_ddb(high_by_month)


def _write_results_to_ddb(high_by_month: Dict[str, Dict]):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ["RESULTS_DYNAMODB_TABLE_NAME"])

    for month_str, row in high_by_month.items():
        row["pk"] = month_str
        row["TEMP"] = round(Decimal(row["TEMP"]), 1)
        table.put_item(Item=row)


def get_file_from_s3(input_bucket_name: str, key: str) -> str:
    resp = S3_CLIENT.get_object(Bucket=input_bucket_name, Key=key)
    return resp["Body"].read().decode("utf-8")
def get_csv_dict_from_string(csv_string: str) -> dict:
    return csv.DictReader(io.StringIO(csv_string))