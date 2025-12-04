from django import forms
from .models import Teacher, DrivingInstructor, ProductionMaster, Employee
from schools.models import DrivingCategory, Vehicle


class TeacherForm(forms.ModelForm):
    teaching_categories = forms.ModelMultipleChoiceField(
        queryset=DrivingCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Категории преподавания'
    )
    
    class Meta:
        model = Teacher
        fields = [
            'last_name', 'first_name', 'middle_name', 'iin',
            'phone', 'email', 'position',
            'qualification_number', 'qualification_issue_date', 'qualification_expiry_date',
            'teaching_categories', 'status', 'notes', 'photo'
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'iin': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '12'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'qualification_number': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'qualification_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DrivingInstructorForm(forms.ModelForm):
    license_categories = forms.ModelMultipleChoiceField(
        queryset=DrivingCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Категории ВУ'
    )
    
    class Meta:
        model = DrivingInstructor
        fields = [
            'last_name', 'first_name', 'middle_name', 'iin',
            'phone', 'email', 'position',
            'license_number', 'license_issue_date', 'license_expiry_date',
            'license_categories', 'assigned_vehicle',
            'status', 'notes', 'photo'
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'iin': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '12'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'license_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_vehicle': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['assigned_vehicle'].queryset = Vehicle.objects.filter(school=school, status='active')


class ProductionMasterForm(forms.ModelForm):
    teaching_categories = forms.ModelMultipleChoiceField(
        queryset=DrivingCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Категории обучения'
    )
    
    class Meta:
        model = ProductionMaster
        fields = [
            'last_name', 'first_name', 'middle_name', 'iin',
            'phone', 'email', 'position',
            'qualification_number', 'qualification_issue_date', 'qualification_expiry_date',
            'teaching_categories', 'status', 'notes', 'photo'
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'iin': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '12'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'qualification_number': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'qualification_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'last_name', 'first_name', 'middle_name', 'iin',
            'email', 'phone', 'position', 'custom_position', 'is_active'
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'iin': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '12'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'custom_position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Если выбрано "Другое"'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

