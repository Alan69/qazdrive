from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from userconf.models import User

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(required=True)
    class Meta:
        model=User
        fields=['phone_number', 'first_name', 'last_name', 'city']
        widgets = {
        'phone_number': forms.TextInput(attrs={'class':'form-control'}),
        'first_name': forms.TextInput(attrs={'class':'form-control'}),
        'last_name': forms.TextInput(attrs={'class':'form-control'}),
        'city': forms.Select(attrs={'class':'form-control'}),
        
    }