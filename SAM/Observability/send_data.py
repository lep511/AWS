import requests
import json
import random
from datetime import datetime

url = input("Enter the URL of the API Gateway: ")
count = input("Enter the number of events to send [10]: ")
if not count or type(count) != int:
    count = 10

for n in range(count):
    now = datetime.now()

    payload = json.dumps({
        "id": str(random.randint(1000, 10000)),
        "event": random.choice(["add_to_cart", "purchase", "buy", "remove_from_cart", "view_product"]),
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "user_id": str(random.randint(1000, 10000)),
        "product_id": str(random.randint(1000, 10000)),
        "quantity": random.randint(1, 10),
        "total_price": random.randint(50, 1000),
        "payment_method": random.choice(["credit_card", "debit_card", "paypal", "cash"]),
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    print(response.text)
