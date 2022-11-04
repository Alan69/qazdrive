from django.shortcuts import render
from django.conf import settings
from userconf.models import User

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

def profile(request):
    obj = User.objects.all()
    context={
        "obj":obj,
    }
    return render(request, 'main/profile.html', context)