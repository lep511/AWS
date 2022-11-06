import json
import base64

print('#### Loading function ########')

def lambda_handler(event, context):
    print(json.dumps(event, indent=2))
    for record in event['records']:
        payload = base64.b64decode(record['data'])

        # Print stream as source only data here
        kinesisMetadata = record['kinesisRecordMetadata']
        print(kinesisMetadata['sequenceNumber'])
        # print(kinesisMetadata['subsequenceNumber'])
        # print(kinesisMetadata['partitionKey'])
        # print(kinesisMetadata['shardId'])
        # print(kinesisMetadata['approximateArrivalTimestamp'])

        # Do custom processing on the payload here
        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(payload)
        }
        output.append(output_record)

    print('Successfully processed {} records.'.format(len(event['records'])))

    return {'records': output}
