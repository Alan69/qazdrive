from django.shortcuts import render
import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from django.http import HttpResponse
import json
from userconf.models import User

# Create your views here.
def get_orders(request):
    all_orders = {}
    disable_warnings(InsecureRequestWarning)
    url = 'http://kaspi.ustudy.center/temp/orders/'
    response = requests.get(url, verify=False)
    data = response.json()
    orders = data['orders']
    all_orders = orders
    context = {
        "all_orders": all_orders,
    }
    return render (request, 'payments/get_orders.html', context)

def post_order(request, product, sum):
    disable_warnings(InsecureRequestWarning)
    url = 'http://qazdrivekaspi.kz/api/orders'
    customer = request.user.first_name + " " + request.user.last_name
    customer_id = request.user.id
    data={
"full_name": customer,
"tariff": product,
"sum": sum,
"user_id": customer_id,
"course": "QazDrive"
}
    response = requests.post(url, json=data, verify=False)

    if (response.status_code != 204
            and 'content-type' in response.headers
            and 'application/json' in response.headers['content-type']):
        parsed = response.json()
        # print('parsed response: 👉️', parsed)
    else:
        print('conditions not met')
    
    # print(f"Status Code: {response.status_code}, Response: {response.json()}")

    return render(request, 'payments/post_order.html', { "response": response.json()} )

def check_order(request):
    kaspi_id = request.user.payment_id
    url = f'http://qazdrivekaspi.kz/api/orders/{kaspi_id}'
    response = requests.get(url)

    if (response.status_code != 204
            and 'content-type' in response.headers
            and 'application/json' in response.headers['content-type']):
        parsed = response.json()
    else:
        print('conditions not met')
    
    if parsed['data']['txn_id'] == None:
        return HttpResponse("Не оплачено")
    else:
        return HttpResponse("Оплачено")