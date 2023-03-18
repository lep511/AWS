#======================================================================================================================
# Backend Scanning Engine for Protecting Workloads Workshop WAF Lab
#======================================================================================================================
from __future__ import print_function

import waf_scans

import json
import os
os.chdir("/tmp")
import logging
import boto3
#import itertools, collections
import asyncio
import copy
#import aiodns
#import cchardet
import aiohttp
from asyncio import AbstractEventLoop
from botocore.exceptions import ClientError
from collections import defaultdict, Counter
from boto3.dynamodb.conditions import Key, Attr


logger = logging.getLogger()
logger.setLevel(logging.INFO)

#======================================================================================================================
# Variables
#======================================================================================================================

WSWOriginBucket = os.environ['WSW_BUCKET']
ALBEndpoint = os.environ['ALB_ENDPOINT']
predefined_tests= waf_scans.predefined_tests()

#======================================================================================================================
# Helpers
#======================================================================================================================

# parse HTTP request results
def parse_result(http_result):
    _http_result = http_result
    if  403 == _http_result:
        return ('403 Forbidden' , 0)
    elif 200 == _http_result:
        return ('200 OK' , 1)
    elif 404 == _http_result:
        return ('404 Not Found' , 2)
    elif 500 == _http_result:
        return ('500 Server Error' , 3)
    elif 400 == _http_result:
        return ('400 Bad Request' , 4)
    else:
        return (_http_result , 9)



def put_json_s3(filedata, key):
	s3 = boto3.client('s3')
	response = s3.put_object( 
		Bucket=WSWOriginBucket,
		Body=filedata,
		Key=key,
		Metadata={'Cache-Control': 'no-store, must-revalidate', 'Pragma': 'no-cache', 'Content-Type': 'application/json'}
	)


# Create waf tests to execute
def build_tests(uuid, target):
    t = str(target)
    for u in predefined_tests:
        url_string = 'http://' + t + str(u['exec_string']['uri'])
        u['exec_string']['url'] = url_string

        logger.debug("log -- Tests: %s " % predefined_tests)
        logger.info(f'log -- Scanning target: uid: { uuid } - endpoint: { target }')
        
    return predefined_tests


async def fetch(uid, ttype, tname, url, method, headers, data, jsondata):
    conn = aiohttp.TCPConnector(limit=300, ttl_dns_cache=1500)
    try:
        async with aiohttp.ClientSession(connector=conn) as session:
            if len(jsondata) == 0:
                async with session.request(method, url, headers=headers, data=data, ssl=False, timeout=1) as resp:
                    response = uid, ttype, tname, resp.status
                    return response
            else:
                async with session.request(method, url, headers=headers, json=jsondata, ssl=False, timeout=1) as resp:
                    response = uid, ttype, tname, resp.status
                    return response

    except (ClientError, aiohttp.client_exceptions.ClientConnectorError, asyncio.TimeoutError, AttributeError)as e:
        logger.error(e)
        logger.info("log -- Unable to access uid %s endpoint: %s " % (uid, url))  
        return False


# Execute tests on the target
async def run_tests(loop: AbstractEventLoop):
    result_data = {}
    tasks = []

    try:
        uid = "scans"
        logger.debug("log -- UUID: %s " % uid)
        tests = build_tests(uuid=1, target=ALBEndpoint)
        result_data[uid] = {}

        for single_test in tests:
            logger.debug("log -- Single Test: %s " % single_test)
            tname = str(single_test['Name'])
            ttype = single_test['Type']
            reqdata = single_test['exec_string']
            url = reqdata['url']
            headers = reqdata['headers']
            method = reqdata['method']
            data = reqdata['data']
            jsondata = reqdata['json']    

            tasks.append(loop.create_task(fetch(uid, ttype, tname, url, method, headers, data, jsondata)))

        
    except Exception as e:
        logger.error(e)
        pass

    for task in tasks:
        results = await task
        try:
            if results:
                logger.debug("log -- Test Id: {0} - Request: {1}".format([single_test['Id']], single_test['exec_string']))
                logger.debug("log -- Result: %s " % str(results))

                uid = results[0]
                ttype = results[1]
                tname = results[2]
                status = results[3]

                result_string, ret_code = parse_result(status)

                if ret_code == 1 and 'Canary' not in ttype:
                    testres = {'UUID':uid, tname:'200'}
                    result_data[uid].update(testres)
                elif ret_code == 1 and 'Canary' in ttype:
                    testres = {'UUID':uid, tname:'OK200'}
                    result_data[uid].update(testres)
                elif ret_code == 0 and 'Canary' in ttype:
                    testres = {'UUID':uid, tname:'FAIL403'}
                    result_data[uid].update(testres)
                elif ret_code == 0:
                    testres = {'UUID':uid, tname:'403'}
                    result_data[uid].update(testres)
                elif ret_code == 2:
                    testres = {'UUID':uid,tname:'404'}
                    result_data[uid].update(testres)
                elif ret_code == 3:
                    testres = {'UUID':uid, tname:'500'}
                    result_data[uid].update(testres)
                elif ret_code == 4:
                    testres = {'UUID':uid, tname:'400'}
                    result_data[uid].update(testres)
                else:
                    testres = {'UUID':uid, tname:'OTHER'}
                    result_data[uid].update(testres)
            
        except Exception as e:
            logger.error(e)
            pass

    # Build dictionary template to store results
    result_data_global = {}
    result_data_personal = copy.deepcopy(result_data)
    for t in predefined_tests:
        logger.debug("log -- Building results for tests: %s " % t["Name"])
        result_data_global[t["Name"]] = {
                "OK200": 0, "FAIL403": 0, "200": 0, "403": 0, "404": 0, "500": 0, "400": 0, "OTHER": 0
                }

    result_data_global_s3 = []
    result_data_s3 = []
    result_data_personal_s3 = []
    
    # Aggregate test rewsults by UUID into dictionary and upload to S3
    for d in result_data.values():
        result_data_s3.append(d)  
        for k, v in d.items():
            if k != 'UUID':
                result_data_global[k][v] = result_data_global.setdefault(k, {}).get(v, 0) + 1

    for d in list(result_data_personal.values()):
        complete = ['403', '400','OK200']
        incomplete = ['404', '500', '200', 'OTHER', 'FAIL403']
        uuid = d["UUID"]
        for k, v in d.items():
            if v in complete:
                result_data_personal[uuid].update({k: 100})
            elif v in incomplete:
                result_data_personal[uuid].update({k: 99})

    result_data_global_s3.append(result_data_global)
    result_data_personal_s3.append(result_data_personal)

    # Write test results to S3 as JSON object
    logger.debug("log -- Uploading result totals to s3: %s " % str(result_data_s3))
    put_json_s3(json.dumps(result_data_s3), 'dataDetail.json')
    put_json_s3(json.dumps(result_data_global_s3), 'dataSummary.json')
    put_json_s3(json.dumps(result_data_personal_s3), 'dataPersonal.json')

    return result_data_s3, result_data_global_s3, result_data_personal_s3
    
#======================================================================================================================
# Lambda entry point
#======================================================================================================================

 
def lambda_handler(event, context):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(run_tests(loop))

    return result


def main():
    lambda_handler("test", "test")

if __name__ == "__main__":
  main()