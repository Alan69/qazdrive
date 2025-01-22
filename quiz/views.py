from django.http import HttpResponse
from .models import Question, Category, Result
from django.shortcuts import render

def category(request):
    categories = Category.objects.all()
    return render(request, 'quiz/category.html', {'categories': categories})

def quiz(request, category_id):
    category = Category.objects.get(pk=category_id)
    if request.method == 'POST':
        questions = Question.objects.filter(category=category)
        score = 0
        wrong = 0
        correct = 0
        total = 0
        for q in questions:
            total += 1
            answer = request.POST.get(q.question_text)
            if q.correctly == answer:
                score += 10
                correct += 1
            else:
                wrong += 1
        percent = score / (total * 10) * 100
        context = {
            'score': score,
            'time': request.POST.get('timer'),
            'correct': correct,
            'wrong': wrong,
            'percent': percent,
            'total': total
        }
        Result.objects.create(category=category, user=request.user, score=score)
        return render(request, 'quiz/result.html', context)
    else:
        questions = Question.objects.filter(category=category)
        context = {
            'questions': questions,
            'category': category
        }
        return render(request, 'quiz/quiz.html', context)
