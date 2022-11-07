from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from userconf.models import User


class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-controll', 'type':'password', 'name':'old_password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-controll', 'type':'password', 'name':'new_password1'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-controll', 'type':'password', 'name':'new_password2'}))

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

