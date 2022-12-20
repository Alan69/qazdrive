from django.http import HttpResponse
from .models import Question, Category, Result
from django.shortcuts import render
import requests
from django.core.paginator import Paginator

def category(request):
    #check if user payed tests
    kaspi_id = request.user.payment_id
    url = f'https://qazdrivekaspi.kz/api/orders/{kaspi_id}'
    with requests.Session() as session:
        session.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'
        response=session.get(url)
    # response = requests.get(url)
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
        #register in ppdtest.kz
        if request.user.pddtest_pass == None or request.user.pddtest_pass == "":
            ppdtest_api_register_url = "https://api.pddtest.kz/system/external_register_user"

            with requests.Session() as session:
                session.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'
                session.get(ppdtest_api_register_url)
            
            customer_first_name = request.user.first_name
            customer_last_name = request.user.last_name
            customer_city = request.user.city
            customer_email = request.user.email

            data={
                "firstName": customer_first_name,
                "lastName": customer_last_name,
                "city": customer_city,
                "email": customer_email,
                "premium": {
                    "tests": True,
                    "autodrom_id": 15 
                }
            }
            auth_token='KZ910R_smYr91Vbs5IO2kOLS9_FsmmEJlBVoqh3F_sqplb2k396438VN'
            hed = {'Authorization': 'Bearer ' + auth_token}
            response2 = requests.post(ppdtest_api_register_url, json=data, headers=hed)
            print(response2.json())
            if (response2.status_code != 204
                and 'content-type' in response2.headers
                and 'application/json' in response2.headers['content-type']):
                parsed = response2.json()
                # request.user.pddtest_pass = parsed['data']['password']
                
                for i in response2.json():
                    try:
                        ls = i['data']['password']
                        request.user.pddtest_pass = ls
                    except:
                        print("Fuck you!!!")
                        print(i)

        context = {
        "response": parsed
        }

        request.user.is_have_tarif = True
        return render(request, 'quiz/category.html', context)
    else:
        return HttpResponse("Не оплачено")

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
        category = Category.objects.get(id = id)
        questions=Question.objects.filter(category = category)
        context = {
        'questions':questions
        }
        return render(request,'quiz/quiz.html', context)