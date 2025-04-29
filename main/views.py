from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from quiz.models import Result

# Create your views here.
@login_required(login_url='login')
def index(request):
    result = Result.objects.filter(user=request.user)
    context = {
        'result': result
    }
    return render(request, 'main/index.html', context=context)