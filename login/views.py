from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

# Create your views here.
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
       if request.method=="POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        user=authenticate(request,email=email,password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
       context={}
       return render(request,'login/login.html',context)

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('login') 
    else: 
        form = CustomUserCreationForm()
        if request.method=='POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid() :
                user=form.save()
                return redirect('login')
        context={
            'form':form,
        }
        return render(request,'login/register.html',context)

def logoutPage(request):
    logout(request)
    return redirect('login')