from django.http import HttpResponse
from .models import Question, Category, Result
from django.shortcuts import render
import requests
from django.core.paginator import Paginator
from userconf.models import User
import datetime
import json

def category(request):
    #check if user payed tests
    kaspi_id = request.user.payment_id
    url = f'https://qazdrivekaspi.kz/api/orders/{kaspi_id}'
    # with requests.Session() as session:
    #     session.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    #     session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'
    #     response=session.get(url)
    # response = requests.get(url)
    is_payed = False
    # if (response.status_code != 204
    #         and 'content-type' in response.headers
    #         and 'application/json' in response.headers['content-type']):
    #     parsed = response.json()

    #     if parsed['data']['txn_id'] == None:
    #         is_payed = False
    #     else:
    #         is_payed = True
    # else:
    #     print('conditions not met')

    if kaspi_id == None or kaspi_id == 0 or kaspi_id == " ":
        is_payed = False
    else:
        is_payed = True
    start_date = datetime.datetime.now() + datetime.timedelta(30)
    if is_payed == True:
        #register in ppdtest.kz

        ppdtest_api_register_url = "https://api.pddtest.kz/system/external_register_user"
        customer_first_name = request.user.first_name
        customer_last_name = request.user.last_name
        customer_city = request.user.city
        customer_email = request.user.email
        
        autodrom_id_list = {
            'Алматы': 16,
            'Астана': 15,
            'Актау': 17,
            'Актобе': 18,
            'Атырау': 19,
            'Костанай': 20,
            'Кызылорда': 21,
            'Павлодар': 22,
            'Петропавл': 23,
            'Талдыкорган': 24,
            'Тараз': 25,
            'Орал': 26,
            'Шымкент': 27
        }

        for i, v in autodrom_id_list.items():
            if request.user.city == i:
                autodrom_id = v
            else:
                autodrom_id = 15
                
        if request.user.tarif_name == "pdd" or request.user.tarif_name == "paketone" or request.user.tarif_name == "pakettwo" or request.user.tarif_name == "paketthree":
            data={
                    "firstName": customer_first_name,
                    "lastName": customer_last_name,
                    "email": customer_email,
                    "city": customer_city,
                        "premium": {
                            "tests": True,
                            "expires_at": str(start_date)
                        },
                        "autodrom": {
                            "active": False,
                            }
                }
        elif request.user.tarif_name == "avtodrom":
            data={
                    "firstName": customer_first_name,
                    "lastName": customer_last_name,
                    "email": customer_email,
                    "city": customer_city,
                        "premium": {
                            "tests": False,
                        },
                        "autodrom": {
                            "active": True,
                            "expires_at": str(start_date),
                            "autodrom_id": autodrom_id
                            }
                }
        elif request.user.tarif_name == "pddandavtodrom":
            data={
                    "firstName": customer_first_name,
                    "lastName": customer_last_name,
                    "email": customer_email,
                    "city": customer_city,
                        "premium": {
                            "tests": True,
                            "expires_at": str(start_date),
                        },
                        "autodrom": {
                            "active": True,
                            "expires_at": str(start_date),
                            "autodrom_id": autodrom_id
                            }
                }

        if request.user.pddtest_pass == None:
            auth_token='KZ910R_smYr91Vbs5IO2kOLS9_FsmmEJlBVoqh3F_sqplb2k396438VN'
            hed = {'Authorization': 'Bearer ' + auth_token}
            response2 = requests.post(ppdtest_api_register_url, json=data, headers=hed)
            # print(response2.json())
            parsed2 = response2.json()
            currunt_user = User.objects.filter(id = request.user.id).first()
            currunt_user.pddtest_pass = parsed2['data']['password']
            currunt_user.save()

        # login_to_pdd(request.user.email, request.user.pddtest_pass)
        request.user.is_have_tarif = True
        return render(request, 'quiz/category.html')
    else:
        return HttpResponse("Не оплачено")

def login_to_pdd(username, password):
    url = "https://api.pddtest.kz/auth/authorize"
    url_main_page = "https://pddtest.kz/main"
    with requests.Session() as session:
        payload = {'username': username, 'password': password}
        res = session.post(url, json=payload)
        session.headers.update({'Authorization': 'Bearer ' + json.loads(res.content)['access_token'][0]})
        # s.get(url_main_page)
        # print(res.content)
        # return r

def quiz(request, id):
    if request.method == 'POST':
        category = Category.objects.get(id = id)
        questions = Question.objects.filter(category = id)
        score=0
        wrong=0
        correct=0
        total=0
        for q in questions:
            total+=1
            # print('selected: '+str(request.POST.get(q.question_text)))
            # print('correct: '+str(q.correctly))
            # print()
            answer = request.POST.get(q.question_text)
            if q.correctly == answer:
                score+=10
                correct+=1
            else:
                wrong+=1
        percent = score/(total*10) *100
        context = {
            'score':score,
            'time': request.POST.get('timer'),
            'correct':correct,
            'wrong':wrong,
            'percent':percent,
            'total':total
        }
        Result.objects.create(category=category.cat_name, user=request.user, score=score)
        return render(request,'quiz/result.html',context)
    else:
        # category = Category.objects.get(id = id)
        # questions=Question.objects.filter(category = category)
        context = {
        # 'questions':questions
        }
        return render(request,'quiz/quiz.html', context)