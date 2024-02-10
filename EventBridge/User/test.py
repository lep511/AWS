from event_test import Marshaller
from event_test import Event

event_json = {
  "type": {
    "color": "#808080",
    "order": 0,
    "name": "Blackout",
    "description": "No production deployments during this blackout period",
    "ghostedDate": 0,
    "id": "00000000-0000-1100-0000-000000000011",
    "version": 0,
    "dateCreated": 0
  },
  "startDate": 1413384452,
  "endDate": 1413394452,
  "isOneDay": False,
  "releases": [],
  "description": "Optional description",
  "name": "Example event",
  "id": "4f47d1fe-f25a-4f9e-a91a-c8fb0668e99a",
  "version": 0,
  "dateCreated": 1421692929323
}

#Deserialize event into strongly typed object
aws_event: Event = Marshaller.unmarshall(event_json, Event)

#Execute business logic
print(f"Event version: {aws_event.version}")

print(Marshaller.marshall(aws_event))