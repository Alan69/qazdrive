from django.shortcuts import render
from django.conf import settings
from userconf.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

def profile(request):
    obj = User.objects.all()
    context={
        "obj":obj,
    }
    return render(request, 'main/profile.html', context)

def updaterecord(request, id):
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    city = request.POST['city']
    email = request.POST['email']
    user = User.objects.get(id=id)
    user.first_name = first_name
    user.last_name = last_name
    user.city = city
    user.email = email
    user.save()
    return HttpResponseRedirect(reverse('profile'))