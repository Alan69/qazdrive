import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

def post_order():
    # disable_warnings(InsecureRequestWarning)
    url = 'http://qazdrivekaspi.kz/api/orders'
    data={
"full_name": "Аслан",
"tariff": "Оптимальный",
"sum": 1,
"user_id": 10,
"course": "QazDrive"
}

    response = requests.post(url, json=data)

    if (response.status_code != 204
            and 'content-type' in response.headers
            and 'application/json' in response.headers['content-type']):
        parsed = response.json()
        # print('parsed response: 👉️', parsed)
    else:
        print('conditions not met')

    return print(f"Status Code: {response.text}")

# post_order()

def get_orders():
    all_orders = {}
    url = 'http://qazdrivekaspi.kz/api/orders'
    response = requests.get(url)
    data = response.json()
    orders = data[data]
    all_orders = orders

    if (response.status_code != 204
            and 'content-type' in response.headers
            and 'application/json' in response.headers['content-type']):
        parsed = response.json()
    else:
        print('conditions not met')

    return print(all_orders)

# get_orders()

def check_order():
    # kaspi_id = request.user.payment_id
    url = 'http://qazdrivekaspi.kz/api/orders/48'
    response = requests.get(url)

    if (response.status_code != 204
            and 'content-type' in response.headers
            and 'application/json' in response.headers['content-type']):
        parsed = response.json()
    else:
        print("sosi")

    if parsed['data']['txn_id'] == None:
        print("Не оплочено")
    else:
        print("оплочено")

    
# check_order()