#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import random
from datetime import datetime
import json
import boto3
import base64
from random import randrange
from datetime import timedelta
from mtcp import ManagedTempCredentialsProvider

mtcp = ManagedTempCredentialsProvider()
mtcp.register_default()


batch_no = 0
batch_max = 1000000
batch_size = 500
count = 0
stream_name = 'stock-stream'
records = []
order_types = ['buy', 'sell']
categories = ['amount', 'price', 'limited', 'stop']
statuses = ['pending', 'open', 'complete', 'canceled', 'rejected']

def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)
def print_time_stamp(count,batch_no):
    curDTObj = datetime.now()
    timeStr = curDTObj.strftime("%Y/%m/%d %H:%M:%S")
    print(f"{timeStr} - Batch Number: {batch_no} Count: {count}" )

stocks_df = pd.read_csv('data/stocks.csv')
stocks_lst = stocks_df.values.tolist()
random.seed()
firehose_client = boto3.client('firehose')

print_time_stamp(count,batch_no) 

while True:
    count += 1
    ticker = stocks_lst[random.randint(0,len(stocks_lst)-1)][0] 
    order_class = 'stocks'
    order_type = order_types[random.randint(0,1)]
    category = categories[random.randint(0,3)]
    amount = random.randint(1,500)
    executed = amount
    price = round(random.uniform(10.12, 480.47), 2)
    status = statuses[random.randint(0,4)]
    investor_id = random.randint(1,10000000)
    
    d1 = datetime.strptime('1/1/2010 12:00 AM', '%m/%d/%Y %I:%M %p')
    d2 = datetime.now()
    rdate = random_date(d1, d2)
    
    order_date = rdate.strftime("%Y-%m-%d")
    order_time = rdate.strftime("%H:%M:%S")
 
    row = {
        "ticker" : ticker,
        "order_class" : order_class,
        "order_type" : order_type,
        "category" : category,
        "amount" : amount,
        "executed" : executed,
        "price" : price,
        "status" : status,
        "investor_id" : investor_id,
        "order_date" : order_date,
        "order_time" : order_time
    }

    record = {
        'Data' : json.dumps(row)
    }
    records.append(record) 
    json.dumps(records)
    
    if count % batch_size == 0:
        print_time_stamp(count,batch_no)
        response = firehose_client.put_record_batch(
            DeliveryStreamName = stream_name,
            Records = records
        )
        batch_no = batch_no + 1
        records.clear()

    if (count >= batch_max):   
        print('The end!')
        break
