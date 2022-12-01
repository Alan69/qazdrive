from django.http import HttpResponse
from .models import Question, Category, Result
from django.shortcuts import render
import requests
from django.core.paginator import Paginator

def category(request):
    category = Category.objects.all()
    context = {
        'category': category,
    }

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