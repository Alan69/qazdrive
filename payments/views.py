from django.shortcuts import render, redirect
import requests
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
from django.http import HttpResponse
import json
from userconf.models import User
from subs_request.models import SubRequest
import datetime
from django.contrib import messages

def post_order(request, product, sum):
    url = 'https://qazdrivekaspi.kz/api/orders'
    today_date = datetime.datetime.now().date
    start_date = datetime.datetime.now() + datetime.timedelta(30)
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
        
    else:
        print('conditions not met')
    
    # if request.user.tarif_expire_date == today_date:
    if request.user.pddtest_pass == None:
    # if parsed['data']['id'] == None:
        currunt_user.payment_id = parsed['data']['id']
        currunt_user.tarif_name = product
        currunt_user.tarif_expire_date = start_date
        currunt_user.save()
        return render(request, 'payments/post_order.html', { "response": response.json()})
    else:
        messages.success(request, 'У вас есть активный тариф')
        return redirect('index')

# отправка заявки для партнеров
def send_subs_req(request, subsname):
    SubRequest.objects.create(user=request.user, subscription_name=subsname)
    messages.success(request, 'Ваша заявка принята')
    return redirect('index')

#для проверки оплаты
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