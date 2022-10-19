import boto3
import json

table_name = 'SuperMissionTable'

dynamodb = boto3.resource('dynamodb')
dynamo = boto3.client('dynamodb')
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    response = table.scan()
    if response['Items'] == []:
        print("No hay nada")
        put_elements()
    return {
        'statusCode': 200,
        'body': json.dumps(response['Items'])
    }

    
def put_elements():
    # Put elements to table
    dynamo.put_item(
        TableName=table_name,
        Item={
            'SuperHero': {'S': 'Superman'},
            'SuperMission': {'S': 'Save the world'},
            'SuperPower': {'S': 'Super strength'},
            'SuperWeapon': {'S': 'Laser eyes'},
            'SuperWeakness': {'S': 'Kryptonite'},
            'Villain1': {'S': 'Lex Luthor'},
            'Villain2': {'S': 'Brainiac'},
            'Villain3': {'S': 'Darkseid'},
            'Villain4': {'S': 'Bizarro'},
        }
    )
    dynamo.put_item(
        TableName=table_name,
        Item={
            'SuperHero': {'S': 'Batman'},
            'SuperMission': {'S': 'Save Gotham City'},
            'SuperPower': {'S': 'Super intelligence'},
            'SuperWeapon': {'S': 'Utility belt'},
            'Villain1': {'S': 'Joker'},
            'Villain2': {'S': 'Two-Face'},
            'Villain3': {'S': 'Penguin'},
    
        }
    )
    dynamo.put_item(
        TableName=table_name,
        Item={
            'SuperHero': {'S': 'Spiderman'},
            'SuperMission': {'S': 'Catch the bad guys'},
            'SuperPower': {'S': 'Super agility'},
            'SuperWeapon': {'S': 'Spider web'},
            'Villain1': {'S': 'Green Goblin'},
            'Villain2': {'S': 'Venom'},
        }
    )
    dynamo.put_item(
        TableName=table_name,
        Item={
            'SuperHero': {'S': 'Ironman'},
            'SuperMission': {'S': 'Save the world'},
            'SuperPower': {'S': 'Super intelligence'},
            'SuperWeapon': {'S': 'Mark 50'},
            'Villain1': {'S': 'Mandarin'},
            'Villain2': {'S': 'Whiplash'},
            'Villain3': {'S': 'Ultron'},
        }
    )
    dynamo.put_item(
        TableName=table_name,
        Item={
            'SuperHero': {'S': 'Captain America'},
            'SuperMission': {'S': 'Save the world'},
            'SuperPower': {'S': 'Super strength'},
            'SuperWeapon': {'S': 'Shield'},
            'Villain1': {'S': 'Red Skull'},
            'Villain2': {'S': 'Hydra'},
        }
    )
    return