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


def lambda_handler(event: dict, context):
    """Handler that will find the weather station that has the highest average temperature by month.

    Returns a dictionary with "year-month" as the key and dictionary (weather station info) as value.

    """
    input_bucket_name = os.environ["INPUT_BUCKET_NAME"]

    high_by_month: Dict[str, Dict] = {}

    for item in event["Items"]:
        csv_data = get_file_from_s3(input_bucket_name, item["Key"])
        dict_data = get_csv_dict_from_string(csv_data)

        for row in dict_data:
            avg_temp = float(row["TEMP"])

            date = datetime.fromisoformat(row["DATE"])
            month_str = date.strftime("%Y-%m")

            monthly_high_record = high_by_month.get(month_str) or {}

            if not monthly_high_record:
                row["TEMP"] = avg_temp
                high_by_month[month_str] = row
                continue

            if avg_temp > float(monthly_high_record["TEMP"]):
                high_by_month[month_str] = row

    return high_by_month


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