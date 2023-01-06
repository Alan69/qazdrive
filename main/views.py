from django.shortcuts import render
from quiz.models import Result

# Create your views here.
def index(request):
    # result = Result.objects.filter(user = request.user)
    context = {
        # 'result':result
    }
    return render(request, 'main/index.html')
    
def partner(request):
    return render(request, 'main/partner.html')