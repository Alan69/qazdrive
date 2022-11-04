from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from userconf.models import User
from .helpers import send_forget_password_mail
from django.contrib import messages
from .models import Profile

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

                profile_obj = Profile.objects.create(user = user)
                profile_obj.save()
                return redirect('login')
        context={
            'form':form,
        }
        return render(request,'login/register.html',context)

def logoutPage(request):
    logout(request)
    return redirect('login')

def ChangePassword(request , token):
    context = {}
    
    
    try:
        profile_obj = Profile.objects.filter(forget_password_token = token).first()
        context = {'user_id' : profile_obj.user.id}
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')
            
            if user_id is  None:
                messages.success(request, 'No user id found.')
                return redirect(f'/change-password/{token}/')
                
            
            if  new_password != confirm_password:
                messages.success(request, 'both should  be equal.')
                return redirect(f'/change-password/{token}/')
                         
            
            user_obj = User.objects.get(id = user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return redirect('login')
            
            
    except Exception as e:
        print(e)
    return render(request , 'login/change-password.html' , context)


import uuid
def ForgetPassword(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            
            if not User.objects.filter(email=email).first():
                messages.success(request, 'Not user found with this email.')
                return redirect('/forget-password/')
            
            user_obj = User.objects.get(email = email)
            token = str(uuid.uuid4())
            profile_obj= Profile.objects.get(user = user_obj)
            profile_obj.forget_password_token = token
            profile_obj.save()
            send_forget_password_mail(user_obj.email, token)
            messages.success(request, 'An email is sent.')
            return redirect('/forget-password/')
    except Exception as e:
        print(e)
    return render(request , 'login/forget-password.html')