import argparse
import logging
import os
import json
import imghdr
import boto3
import sys
import requests

"""
Calls DetectAnomalies using the supplied project, model version, and image.
:param lookoutvision_client: A Lookout for Vision Boto3 client.
:param project: The project that contains the model that you want to use.
:param model_version: The version of the model that you want to use.
:param photo: The photo that you want to analyze.
:return: The DetectAnomalyResult object that contains the analysis results.
"""
def get_region():
    try:
        response = requests.get("http://169.254.169.254/latest/meta-data/placement/region", timeout=1)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
region = get_region()

lookoutvision_client = boto3.client('lookoutvision', region_name=region)
project_name='l4v-cpu'
model_version='1'

# assign directory
directory = sys.argv[1]
print(directory)
# iterate over files in that directory
for filename in os.listdir(directory):
    photo = os.path.join(directory, filename)
    print(photo)

    image_type = imghdr.what(photo)
    if image_type == "jpeg":
        content_type = "image/jpeg"
    elif image_type == "png":
        content_type = "image/png"
    else:
        print("Invalid image type for %s", photo)
        raise ValueError(
            f"Invalid file format. Supply a jpeg or png format file: {photo}")


    # Get images bytes for call to detect_anomalies
    with open(photo, "rb") as image:
        response = lookoutvision_client.detect_anomalies(
            ProjectName=project_name,
            ContentType=content_type,
            Body=image.read(),
            ModelVersion=model_version)

    #write response to a file

    print(response['DetectAnomalyResult'])