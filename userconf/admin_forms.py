from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class CustomAdminAuthenticationForm(AuthenticationForm):
    """
    Custom admin login form that shows a more user-friendly label
    """
    username = forms.CharField(
        label=_("Номер телефона или Email"),
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'placeholder': 'Введите номер телефона или email'
        })
    )
    
    error_messages = {
        'invalid_login': _(
            "Пожалуйста, введите корректные данные. "
            "Номер телефона и пароль могут быть чувствительны к регистру."
        ),
        'inactive': _("Этот аккаунт неактивен."),
    }

