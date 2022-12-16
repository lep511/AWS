import boto3
import json
import pandas as pd
import random
from collections import defaultdict
from faker import Faker
from faker.providers import bank, credit_card, date_time, profile,currency, user_agent
import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ingest_bucket=os.environ.get('ingest_bucket')

def lambda_handler(event, context):


    fake = Faker()
    fake.add_provider(bank)
    fake.add_provider(credit_card)
    fake.add_provider(profile)
    fake.add_provider(date_time)
    fake.add_provider(currency)
    fake.add_provider(user_agent)
    
    
    fake_data = defaultdict(list)
    for _ in range(1000):
        fake_data["first_name"].append( fake.first_name() )
        fake_data["last_name"].append( fake.last_name() )
        fake_data["transaction_date"].append(fake.date_this_month())
        fake_data["card_number"].append( fake.credit_card_number() )
        fake_data["card_expire"].append( fake.credit_card_expire() )
        fake_data["card_type"].append( fake.credit_card_provider() )
        fake_data["card_sec_code"].append( fake.credit_card_security_code() )
        fake_data["transaction_amount"].append(fake.pricetag() )
        fake_data["user_agent"].append(fake.user_agent())
    
    
    df_fake_data = pd.DataFrame(fake_data)
    df_fake_data["transaction_amount"] = df_fake_data["transaction_amount"].str.replace("[$,]","")

    
    print(df_fake_data.head())
    
    df_fake_data.to_csv("/tmp/dataexport.csv")
        
    filename = '/tmp/dataexport.csv'
    
    s3 = boto3.client('s3')
        
    try:
        response = s3.upload_file(
            filename,
             Bucket=ingest_bucket,
            Key='dataexport.csv'
            )
        logger.info('File Uploaded Successfully')
    except Exception as e:
        logging.error(e)
        logger.info('File Not Uploaded')