from django import forms
from .models import Certificate
from students.models import Student
from schools.models import DrivingCategory


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = [
            'student', 'category', 'issue_date', 'expiry_date',
            'training_start_date', 'training_end_date',
            'theory_hours', 'practice_hours',
            'theory_exam_passed', 'practice_exam_passed',
            'notes'
        ]
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'training_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'training_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'theory_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'practice_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'theory_exam_passed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'practice_exam_passed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            # Only show students from this school who have completed their training
            self.fields['student'].queryset = Student.objects.filter(
                group__school=school,
                status='completed'
            ).select_related('group')
            self.fields['category'].queryset = school.categories.all()

