import json
import urllib.request
import numpy as np
import timeit
import platform

list_api_elemnt = ["trivia", "math", "date", "year"]

def lambda_handler(event, context):
    print("Machine: " + platform.machine())
    start_time = timeit.default_timer()
    ndat = first_n_prime_numbres(100)
    stop_time = timeit.default_timer()
    elapsed_time = stop_time - start_time
    print("Elapsed time: " + str(elapsed_time))	
    
    body = json.loads(event['body'])
    if body['type'] not in list_api_elemnt:
        return {
        'headers': {
            'Content-Type': 'application/json',
        },           
            'statusCode': 400,
            'body': json.dumps('Type must be trivia, math, date or year')
        }
    res = urllib.request.urlopen('http://numbersapi.com/'+ str(body['number']) + '/' + body['type'])
    responsebody = res.read().decode('utf-8')

    response = {
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'application/json',
        },
        'statusCode': 200,
        'body': json.dumps(responsebody)
    }
    return response

def first_n_prime_numbres(n):    
    s = np.arange(3, n, 2)
    for m in range(3, int(n ** 0.5)+1, 2):         
        if s[(m-3)//2]: 
            s[(m*m-3)//2::m]=0
    return np.r_[2, s[s>0]]