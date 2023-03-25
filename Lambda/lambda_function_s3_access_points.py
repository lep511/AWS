# Poicy required: AmazonS3ObjectLambdaExecutionRolePolicy

import boto3
import json
import os
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from urllib import request
from urllib.parse import urlparse, parse_qs, unquote
from urllib.error import HTTPError
from typing import Optional

logger = logging.getLogger('S3-img-processing')
logger.addHandler(logging.StreamHandler())
logger.setLevel(getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))
FILE_EXT = {
    'JPEG': ['.jpg', '.jpeg'],
    'PNG': ['.png'],
    'TIFF': ['.tif']
}
OPACITY = 64  # 0 = transparent and 255 = full solid


def get_img_encoding(file_ext: str) -> Optional[str]:
    result = None
    for key, value in FILE_EXT.items():
        if file_ext in value:
            result = key
            break
    return result


def add_watermark(img: Image, text: str) -> Image:
    font = ImageFont.truetype("AmazonEmber_Rg.ttf", 82)
    txt = Image.new('RGBA', img.size, (255, 255, 255, 0))
    if img.mode != 'RGBA':
        image = img.convert('RGBA')
    else:
        image = img

    d = ImageDraw.Draw(txt)
    # Positioning Text
    width, height = image.size
    text_width, text_height = d.textsize(text, font)
    x = width / 2 - text_width / 2
    y = height / 2 - text_height / 2
    # Applying Text
    d.text((x, y), text, fill=(255, 255, 255, OPACITY), font=font)
    # Combining Original Image with Text and Saving
    watermarked = Image.alpha_composite(image, txt)
    return watermarked


def handler(event, context) -> dict:
    logger.debug(json.dumps(event))
    object_context = event["getObjectContext"]
    # Get the presigned URL to fetch the requested original object
    # from S3
    s3_url = object_context["inputS3Url"]
    # Extract the route and request token from the input context
    request_route = object_context["outputRoute"]
    request_token = object_context["outputToken"]
    parsed_url = urlparse(event['userRequest']['url'])
    object_key = parsed_url.path
    logger.info(f'Object to retrieve: {object_key}')
    parsed_qs = parse_qs(parsed_url.query)
    for k, v in parsed_qs.items():
        parsed_qs[k][0] = unquote(v[0])

    filename = os.path.splitext(os.path.basename(object_key))
    # Get the original S3 object using the presigned URL
    req = request.Request(s3_url)
    try:
        response = request.urlopen(req)
    except HTTPError as e:
        logger.info(f'Error downloading the object. Error code: {e.code}')
        logger.exception(e.read())
        return {'status_code': e.code}

    if encoding := get_img_encoding(filename[1].lower()):
        logger.info(f'Compatible Image format found! Processing image: {"".join(filename)}')
        img = Image.open(response)
        logger.debug(f'Image format: {img.format}')
        logger.debug(f'Image mode: {img.mode}')
        logger.debug(f'Image Width: {img.width}')
        logger.debug(f'Image Height: {img.height}')

        img_result = add_watermark(img, parsed_qs.get('X-Amz-watermark', ['Watermark'])[0])
        img_bytes = BytesIO()

        if img.mode != 'RGBA':
            # Watermark added an Alpha channel that is not compatible with JPEG. We need to convert to RGB to save
            img_result = img_result.convert('RGB')
            img_result.save(img_bytes, format='JPEG')
        else:
            # Will use the original image format (PNG, GIF, TIFF, etc.)
            img_result.save(img_bytes, encoding)
        img_bytes.seek(0)
        transformed_object = img_bytes.read()

    else:
        logger.info(f'File format not compatible. Bypass file: {"".join(filename)}')
        transformed_object = response.read()

    # Write object back to S3 Object Lambda
    s3 = boto3.client('s3')
    # The WriteGetObjectResponse API sends the transformed data
    if os.getenv('AWS_EXECUTION_ENV'):
        s3.write_get_object_response(
            Body=transformed_object,
            RequestRoute=request_route,
            RequestToken=request_token)
    else:
        # Running in a local environment. Saving the file locally
        with open(f'myImage{filename[1]}', 'wb') as f:
            logger.debug(f'Writing file: myImage{filename[1]} to the local filesystem')
            f.write(transformed_object)

    # Exit the Lambda function: return the status code
    return {'status_code': 200}