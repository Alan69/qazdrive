from django.shortcuts import render
from django.conf import settings
from userconf.models import User
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.views import PasswordChangeView
from .forms import PasswordChangingForm

# Create your views here.
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
    return HttpResponseRedirect(reverse_lazy('profile'))

class PasswordsChangeView(PasswordChangeView):
    from_class = PasswordChangingForm
    success_url = reverse_lazy('profile')