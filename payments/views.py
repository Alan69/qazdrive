from django.shortcuts import render
import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from django.http import HttpResponse
import json
from userconf.models import User

def post_order(request, product, sum):
    url = 'https://qazdrivekaspi.kz/api/orders'

    with requests.Session() as session:
        session.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'
        session.get(url)
    
    customer = request.user.first_name + " " + request.user.last_name
    customer_id = request.user.id

    data={
    "full_name": customer,
    "tariff": product,
    "sum": sum,
    "user_id": customer_id,
    "course": "ПДД"
    }
    
    response = requests.post(url, json=data)
    
    if (response.status_code != 204
            and 'content-type' in response.headers
            and 'application/json' in response.headers['content-type']):
        parsed = response.json()

        currunt_user = User.objects.filter(id = request.user.id).first()
        currunt_user.payment_id = parsed['data']['id']
        currunt_user.save()
    else:
        print('conditions not met')
    return render(request, 'payments/post_order.html', { "response": response.json()} )


def check_order(request):
    kaspi_id = request.user.payment_id
    url = f'https://qazdrivekaspi.kz/api/orders/{kaspi_id}'
    response = requests.get(url)
    is_payed = False
    if (response.status_code != 204
            and 'content-type' in response.headers
            and 'application/json' in response.headers['content-type']):
        parsed = response.json()

        if parsed['data']['txn_id'] == None:
            is_payed = False
        else:
            is_payed = True
    else:
        print('conditions not met')
    
    if is_payed == True:
        return HttpResponse("Оплачено")
    else:
        return HttpResponse("Не оплачено")