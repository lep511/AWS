# UnarchiveFindings.py
#
# This script unarchives findings in GuardDuty.
#
# Usage:
# python3 UnarchiveFindings.py


import boto3
import json
import os

def unarchive_findings():
    # Create GuardDuty client
    client = boto3.client('guardduty')
    # List detectors
    response = client.list_detectors()
    # Get detectorId
    detectorId = response['DetectorIds'][0]
    # List findings
    response = client.list_findings(
        DetectorId=detectorId,
        FindingCriteria={
            'Criterion': {
                'service.archived': {
                    'Eq': [
                        True,
                    ]
                }
            }
        }
    )
    # Get findingIds
    findingIds = response['FindingIds']
    # Unarchive findings
    response = client.unarchive_findings(
        DetectorId=detectorId,
        FindingIds=findingIds
    )
    return response

def main():
    response = unarchive_findings()
    print(json.dumps(response, indent=4))

if __name__ == '__main__':
    main()