import datetime
import psycopg2
import json
import boto3
import logging
import sys
import time
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)
TRACKER_NAME = "tracker-01"
SECRET_ID = os.environ['SecretARN']

client_sm = boto3.client('secretsmanager')
response = client_sm.get_secret_value(
    SecretId=SECRET_ID
)
db_conn = json.loads(response['SecretString'])

ENDPOINT = db_conn['host']
PORT = db_conn['port']
USER = db_conn['username']
REGION = os.environ['AWS_REGION']
DBNAME = "vcsmaster"
DBPWD = db_conn['password']

# ********* create the connection for the database
try:
    conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER,
                            password=DBPWD)
except psycopg2.Error as e:
    logger.error("Database connection failed due to {}".format(e))
    logger.error(e)
    sys.exit()

logger.info("OUTCOME: Connection to RDS instance succeeded")


def lambda_handler(event, context):

    vehicle_id = event["vehicleid"]
    event_id = event["eventid"]
    event_tstamp = event["timestamp"]
    event_position = event["position"]
    forward_event = False

    # ********* verify the vehicle information from the database and its sold status
    logger.info(
        "ACTION: Checking if the vehicle exists in back end and if so check status to see if its not sold")
    cur = conn.cursor()
    select_query = "SELECT v.*, c.customerid FROM vehicles v LEFT JOIN customervehicles c ON v.vehicleid=c.vehicleid where v.vehicleid = %s"
    cur.execute(select_query, (vehicle_id,))
    vehicle_records = cur.fetchall()
    vehicle_records_count = len(vehicle_records)
    logger.info("OUTCOME: Total rocords that matches the vehicle id: %s",
                vehicle_records_count)

    if vehicle_records_count == 1:
        customer_id = vehicle_records[0][11]

        if(customer_id is None):
            forward_event = True

            # ********* Create vehicle if not exists for updating the vehicle status
            try:
                iq_02 = """ INSERT INTO vehiclestatus(vehicleid) VALUES (%s);"""
                cur.execute(iq_02, (vehicle_id,))
                conn.commit()
            except:
                logger.error("Vehicle insert error")
                conn.rollback()

            # ********* Update the vehicle status and last known position
            logger.info(
                "ACTION: Updating the vehicle's in-transit status and its last known position")
            update_v_01 = "UPDATE vehiclestatus SET intransit=%s, lastposition=point(%s, %s), lastpositiontstamp=%s, longitude=%s, latitude=%s WHERE vehicleid = %s;"
            cur.execute(
                update_v_01, (True, event_position[0], event_position[1], event_tstamp, event_position[0], event_position[1], vehicle_id))
            conn.commit()

            # ********* Insert vehicle telemetry
            try:
                logger.info('ACTION: Save the geofence event into database')
                cur = conn.cursor()
                iq_01 = """ INSERT INTO public.positionevents(
                            time, vehicleid, eventid,  longitude, latitude,position)
                            VALUES
                            (%s, %s, %s, %s, %s, point(%s,%s));"""
                cur.execute(iq_01, (event_tstamp, vehicle_id, event_id,
                                    event_position[0], event_position[1], event_position[0], event_position[1]))
                conn.commit()
            except:
                logger.error("Vehicle insert error")
                conn.rollback()

    else:
        logger.info("OUTCOME: Vehicle does not exists in the backend.")

    if forward_event:


        # ********* Forward the location information to the amazon location service
        curr_datetime = datetime.datetime.utcnow()
        curr_datetime_iso = curr_datetime.isoformat()

        updates = [
            {
                "DeviceId": vehicle_id,
                "SampleTime": curr_datetime_iso,
                "Position": event['position']
            }
        ]

        client_als = boto3.client("location")
        response = client_als.batch_update_device_position(
            TrackerName=TRACKER_NAME, Updates=updates)

        response_status = response['ResponseMetadata']['HTTPStatusCode']

        if response_status == 200:
            return_message = "location event routed to amazon location service."
        else:
            return_message = "error while routing location event to location service"

        logger.info("RESPONSE: Status code %s received and %s",
                    response_status, return_message)

        return {
            'statusCode': response_status,
            'body': return_message
        }
    else:
        logger.error("Event not routed.")
