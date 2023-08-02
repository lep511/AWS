import io
from typing import Dict
import time

from aws_lambda_powertools.utilities.streaming.s3_object import S3Object
from aws_lambda_powertools.utilities.streaming.transformations import CsvTransform
from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: Dict[str, str], context: LambdaContext):
    start = time.time()
    max_time = 120
    break_check = True
    s3 = S3Object(bucket=event["bucket"], key=event['key'])

    tsv_stream = s3.transform(CsvTransform(delimiter=","))
    DISTANCE=0
    count=0
    
    for obj in tsv_stream:
        DISTANCE += int(obj['DISTANCE'])
        count += 1
        actual_time = time.time()
        if actual_time - start > max_time:
            print("--- Break ---")
            break_check = False
            break
    
    end = time.time()
    
    print("Promedio distancia:", DISTANCE/count)
    print("Total process:", count)
    print("Total time:", end - start)
    print("Finish normal:", break_check)
