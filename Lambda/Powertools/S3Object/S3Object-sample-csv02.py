import io
from typing import Dict

from aws_lambda_powertools.utilities.streaming.s3_object import S3Object
from aws_lambda_powertools.utilities.streaming.transformations import CsvTransform
from aws_lambda_powertools.utilities.typing import LambdaContext

LAST_ROW_SIZE = 22
CSV_HEADERS = ["isig", "datetime", "glucose"]

def lambda_handler(event: Dict[str, str], context: LambdaContext):
    sample_csv = S3Object(bucket=event["bucket"], key=event['key'])

    # From the end of the file, jump exactly 30 bytes backwards
    sample_csv.seek(-LAST_ROW_SIZE, io.SEEK_END)

    # Transform portion of data into CSV with our headers
    sample_csv.transform(CsvTransform(fieldnames=CSV_HEADERS), in_place=True)

    # We will only read the last portion of the file from S3
    # as we're only interested in the last 'location' from our dataset

    for last_row in sample_csv:
        print(last_row["isig"])
