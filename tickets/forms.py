from django import forms
from .models import Ticket, TicketMessage, TicketSubject


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['subject', 'custom_subject', 'description', 'priority']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'custom_subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Или введите свою тему'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Опишите вашу проблему подробно'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = TicketSubject.objects.filter(is_active=True)
        self.fields['subject'].required = False
        self.fields['priority'].initial = 'medium'


class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Введите сообщение'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

