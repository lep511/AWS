import boto3
import json

"""
Lists detectorIds of all the existing Amazon GuardDuty detector resources.
==========================================================================
"""

def list_detectors():
    # Create GuardDuty client
    client = boto3.client('guardduty')
    # List detectors
    response = client.list_detectors()
    return response

def main():
    response = list_detectors()
    print(json.dumps(response, indent=4))

if __name__ == '__main__':
    main()