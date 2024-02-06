import datetime
import psycopg2
import json
import boto3
import logging
import sys
import time
import os
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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


def send_email(vinnum, name, city, postalcode):

    SENDER = os.environ['email_identity']
    RECIPIENT = os.environ['email_identity']
    AWS_REGION = os.environ['AWS_REGION']
    SUBJECT = "Notification of Vehicle Arrivals"
    BODY_TEXT = ("Vehicle with specified vin number test01 has reached the specified address below \r\n"
                 " frisco, texas"
                 )

    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
    <p>Dear Customer,</p>
    <p></p>
        <p>Vehicle with vin number <b> %s </b>  has reached the address below.<br>
        <u> %s <br> %s, %s </u></p>
        <p></p>
        <p>Thank you, <br>
        VCS Team</p>
        <p></p>
        <p>Note: Please do not reply to this automated email message. Contact <a href=''>support</a> for any assistance neede.</p>
    </body>
    </html>
                """ % (vinnum, name, city, postalcode)

    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def lambda_handler(event, context):

    logger.info('RECEIVED:', event)

    geo_event = event['detail']
    idata_time = geo_event['SampleTime']
    idata_geofenceid = geo_event['GeofenceId']
    idata_vehicleid = geo_event['DeviceId']
    idata_eventtype = geo_event['EventType']
    idata_long = geo_event['Position'][0]
    idata_lat = geo_event['Position'][1]
    idata_eventid = event['id']

    # ********** Insert the event in the database
    logger.info('ACTION: Save the geofence event into database')
    try:
        cur = conn.cursor()
        iq_01 = """INSERT INTO geofenceevents
                        (time, geofenceid, vehicleid, eventtype, latitude, longitude, position, eventid)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, point(%s,%s), %s);"""
        cur.execute(iq_01, (idata_time, idata_geofenceid, idata_vehicleid,
                            idata_eventtype, idata_lat, idata_long, idata_long, idata_lat, idata_eventid,))
        conn.commit()
    except Exception as e:
        logger.error("Geofence event insert error {}".format(e))
        conn.rollback()

    try:
        iq_02 = """ INSERT INTO vehiclestatus(vehicleid) VALUES (%s);"""
        cur.execute(iq_02, (idata_vehicleid,))
        conn.commit()
    except Exception as e:
        logger.error("Vehicle insert error {}".format(e))
        conn.rollback()

    logger.info('ACTION: Get the dealer for corresponding geofence')
    sq_01 = """ select dealerid from dealergeofences g where geofenceid = %s """
    cur.execute(sq_01, (idata_geofenceid,))
    dealer_records = cur.fetchall()

    if len(dealer_records) > 0:
        logger.info('ACTION: Update the vehicle status')
        dealer_id = dealer_records[0][0]
        raise_exception = False
        in_transit = False
        if idata_eventtype == 'ENTER':
            sq_04 = """ select vin, dealername, dealercity, dealerpostalcode from vehicle_details where vehicleid = %s"""
            cur.execute(sq_04, (idata_vehicleid,))
            sqr_04 = cur.fetchone()
            if sqr_04:
                send_email(sqr_04[0], sqr_04[1], sqr_04[2], sqr_04[3])

            sq_02 = """ select dealerid from dealervehicles where vehicleid = %s"""
            cur.execute(sq_02, (idata_vehicleid,))
            sqr_02 = cur.fetchone()
            if sqr_02:

                allot_dealer = sqr_02[0]

                if allot_dealer != dealer_id:
                    raise_exception = True
                    try:
                        iq_03 = """ INSERT INTO dealerexceptions(
                                vehicleid, dealerid, time)
                                VALUES (%s, %s, %s); """
                        cur.execute(iq_03, (idata_vehicleid,
                                    dealer_id, idata_time,))
                        conn.commit()
                    except Exception as e:
                        logger.error(
                            "Vehicle update status error {}".format(e))
                        conn.rollback()

            try:
                uq_01 = """ update vehiclestatus set atdealer = %s, intransit = %s , haveexception = %s where vehicleid = %s """
                cur.execute(uq_01, (dealer_id, in_transit,
                                    raise_exception, idata_vehicleid))
                conn.commit()
            except Exception as e:
                logger.error("Vehicle update status error {}".format(e))
                conn.rollback()

        elif idata_eventtype == 'EXIT':
            uq_02 = """ update vehiclestatus set atdealer = %s where vehicleid = %s """
            cur.execute(uq_02, (None,  idata_vehicleid))
            conn.commit()

            # ********** Insert the event in the database

    response_status = 200
    return_message = ''
    return {
        'statusCode': response_status,
        'body': return_message
    }
