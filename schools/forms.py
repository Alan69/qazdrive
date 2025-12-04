from django import forms
from .models import School, SchoolCabinet, Vehicle, CatalogCard, DrivingCategory


class SchoolForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=DrivingCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Категории для обучения'
    )
    
    class Meta:
        model = School
        fields = [
            'name', 'short_name', 'bin_iin',
            'director_full_name', 'director_iin',
            'address', 'phone', 'email',
            'license_number', 'license_issue_date', 'license_expiry_date',
            'categories', 'allow_electronic_certificates',
            'cashback_certificate_percent', 'cashback_aitest_percent',
            'logo'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bin_iin': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '12'}),
            'director_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'director_iin': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '12'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'license_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cashback_certificate_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cashback_aitest_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'allow_electronic_certificates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class SchoolCabinetForm(forms.ModelForm):
    class Meta:
        model = SchoolCabinet
        fields = ['address']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите адрес кабинета'}),
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'brand', 'model', 'plate_number', 'category',
            'transmission', 'status', 'description', 'year', 'photo'
        ]
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'BMW, Toyota, etc.'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '525, Camry, etc.'}),
            'plate_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123ABC01'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'transmission': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2020'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CatalogCardForm(forms.ModelForm):
    class Meta:
        model = CatalogCard
        fields = [
            'name', 'category', 'description', 'address',
            'phone', 'price_from', 'price_to', 'image', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'price_from': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'price_to': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

