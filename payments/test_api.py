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

post_order()

def get_orders():
    all_orders = {}
    disable_warnings(InsecureRequestWarning)
    url = 'http://qazdrivekaspi.kz/api/orders/48'
    response = requests.get(url, verify=False)
    data = response.json()
    orders = data
    all_orders = orders
    
    return print(all_orders)
    # for i in range(0, len(all_orders)):
  
    #     if i == (len(all_orders)-1):
    #         print("The last element of list using loop : "
    #             + str(all_orders[i]))

# get_orders()