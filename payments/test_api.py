import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

def post_order():
    disable_warnings(InsecureRequestWarning)
    url = 'https://kaspi.ustudy.center/temp/orders/'
    data={
    "customer": "Гасир2",
    "product": "Экзамен Тест",
    "sum": "2",
    "description": "тест Гасир"
    }

    response = requests.post(url, json=data,  verify=False)

    if (response.status_code != 204
            and 'content-type' in response.headers
            and 'application/json' in response.headers['content-type']):
        parsed = response.json()
        print('parsed response: 👉️', parsed)
    else:
        print('conditions not met')

    return print(f"Status Code: {response.text}")

post_order()