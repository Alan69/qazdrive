from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required

# Create your views here.
def loginPage(request):
    return render(request, "login/login.html")

def registerPage(request):
    return render(request, "login/register.html")

def logoutPage(request):
    logout(request)
    return redirect('login')