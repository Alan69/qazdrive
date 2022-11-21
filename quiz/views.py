from django.http import HttpResponse
from .models import Question, Category, Result
from django.shortcuts import render

def category(request):
    category = Category.objects.all()
    context = {
        'category': category,
    }
    return render(request, 'quiz/category.html', context)

def quiz(request, id):
    # category = Category.objects.get(id = id)
    # question = Question.objects.filter(category = category)
    # context = {
    #     'question': question,
    # }

    # return render(request, 'quiz/quiz.html', context)

    if request.method == 'POST':
        category = Category.objects.get(id = id)
        questions = Question.objects.filter(category = category)
        score=0
        wrong=0
        correct=0
        total=0
        for q in questions:

            total+=1
            answer = request.POST.get(q.question_text) # Gets user's choice, i.e the key of answer
            items = vars(q) # Holds the value for choice
            # print(items[answer])
            # Compares actual answer with user's choice
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
        return render(request,'quiz/result.html',context)
    else:
        category = Category.objects.get(id = id)
        questions=Question.objects.filter(category = category)
        context = {
        'questions':questions
        }
        return render(request,'quiz/quiz.html', context)


def result(request):
    results = Result.objects.all()
    context = {
        'results': results,
    }
    return render(request, 'quiz, result.html', context)