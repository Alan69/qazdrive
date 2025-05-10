from django.http import HttpResponse
from .models import Question, Category, Result, QuestionTranslation, QuestionOption
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.conf import settings
import random

@login_required
def category(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        language = request.POST.get('language')
        
        # Set the language in the session
        request.session['quiz_language'] = language
        
        # Set the language for the current request
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
        
        category = Category.objects.get(pk=category_id)
        request.user.category = category
        request.user.save()
        return redirect('quiz')
    
    categories = Category.objects.all()
    return render(request, 'quiz/category.html', {'categories': categories})

@login_required
def quiz(request):
    if not request.user.category:
        return redirect('category')
    
    # Get language from session or default to Russian
    language = request.session.get('quiz_language', 'russian')
    translation.activate(language)
    request.LANGUAGE_CODE = translation.get_language()
    
    if request.method == 'POST':
        # Get the question IDs from the form
        question_ids = [int(qid.split('_')[1]) for qid in request.POST.keys() if qid.startswith('question_')]
        questions = Question.objects.filter(id__in=question_ids)
        
        score = 0
        wrong = 0
        correct = 0
        total = len(questions)
        
        for q in questions:
            # Get the translation for the current language
            translation_obj = QuestionTranslation.objects.get(question=q, language=language)
            # Get the selected option
            selected_option_id = request.POST.get(f'question_{q.id}')
            
            if selected_option_id:
                selected_option = QuestionOption.objects.get(id=selected_option_id)
                if selected_option.is_correct:
                    score += 1
                    correct += 1
                else:
                    wrong += 1
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
        Result.objects.create(user=request.user, score=score)
        return render(request, 'quiz/result.html', context)
    else:
        # Get all questions and select 40 random ones
        all_questions = list(Question.objects.all())
        selected_questions = random.sample(all_questions, min(180, len(all_questions)))
        
        # Prepare questions with their translations and options
        questions_data = []
        for q in selected_questions:
            translation_obj = QuestionTranslation.objects.get(question=q, language=language)
            options = list(QuestionOption.objects.filter(translation=translation_obj))
            # Shuffle options to randomize their order
            random.shuffle(options)
            
            questions_data.append({
                'id': q.id,
                'question_number': q.question_number,
                'question_text': translation_obj.question_text,
                'image_path': q.image_path,
                'options': options
            })
        
        # Shuffle the questions
        random.shuffle(questions_data)
        
        context = {
            'questions': questions_data,
            'category': request.user.category
        }
        return render(request, 'quiz/quiz.html', context)
