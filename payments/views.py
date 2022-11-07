from django.shortcuts import render
import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from django.http import HttpResponse
import json

# Create your views here.
def get_orders(request):
    all_orders = {}
    disable_warnings(InsecureRequestWarning)
    url = 'http://kaspi.ustudy.center/temp/orders/'
    response = requests.get(url, verify=False)
    data = response.json()
    orders = data['orders']
    all_orders = orders 

    return render (request, 'payments/get_orders.html', { "all_orders": all_orders} )

def post_order(request):
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
    
    print(f"Status Code: {response.status_code}, Response: {response.json()}")

    return render(request, 'payments/post_order.html', { "response": response.json()} )