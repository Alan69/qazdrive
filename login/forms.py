from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from userconf.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model=User
        fields=['email', 'first_name', 'last_name', 'city']
        widgets = {
        'email': forms.TextInput(attrs={'class':'form-control' }),
        'first_name': forms.TextInput(attrs={'class':'form-control'}),
        'last_name': forms.TextInput(attrs={'class':'form-control'}),
        'city': forms.Select(attrs={'class':'form-control'}),
        
    }