from django import forms
from .models import StudentGroup, Student, StudentDocument, LessonRecord
from schools.models import DrivingCategory, SchoolCabinet
from staff.models import Teacher, DrivingInstructor, ProductionMaster


class StudentGroupForm(forms.ModelForm):
    class Meta:
        model = StudentGroup
        fields = [
            'name', 'category', 'teacher', 'driving_instructor', 'production_master',
            'cabinet', 'start_date', 'end_date', 'max_students', 'status', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 1-2А'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'driving_instructor': forms.Select(attrs={'class': 'form-select'}),
            'production_master': forms.Select(attrs={'class': 'form-select'}),
            'cabinet': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['category'].queryset = school.categories.all()
            self.fields['teacher'].queryset = Teacher.objects.filter(school=school, status='active')
            self.fields['driving_instructor'].queryset = DrivingInstructor.objects.filter(school=school, status='active')
            self.fields['production_master'].queryset = ProductionMaster.objects.filter(school=school, status='active')
            self.fields['cabinet'].queryset = SchoolCabinet.objects.filter(school=school, approval_status='approved')


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'group', 'last_name', 'first_name', 'middle_name', 'iin', 'birth_date',
            'phone', 'email', 'address', 'photo',
            'enrollment_date', 'contract_number',
            'medical_certificate_number', 'medical_certificate_date', 'medical_certificate_valid_until',
            'status', 'notes'
        ]
        widgets = {
            'group': forms.Select(attrs={'class': 'form-select'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'iin': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '12'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX XX XX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'enrollment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contract_number': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_certificate_number': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_certificate_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'medical_certificate_valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['group'].queryset = StudentGroup.objects.filter(
                school=school,
                status__in=['enrolling', 'training']
            ).order_by('name')


class StudentDocumentForm(forms.ModelForm):
    class Meta:
        model = StudentDocument
        fields = ['document_type', 'title', 'file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class LessonRecordForm(forms.ModelForm):
    class Meta:
        model = LessonRecord
        fields = [
            'lesson_type', 'date', 'start_time', 'end_time', 'duration_minutes',
            'instructor_teacher', 'instructor_driving', 'instructor_production',
            'vehicle', 'status', 'notes', 'grade'
        ]
        widgets = {
            'lesson_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'instructor_teacher': forms.Select(attrs={'class': 'form-select'}),
            'instructor_driving': forms.Select(attrs={'class': 'form-select'}),
            'instructor_production': forms.Select(attrs={'class': 'form-select'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'grade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
        }
    
    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school:
            self.fields['instructor_teacher'].queryset = Teacher.objects.filter(school=school, status='active')
            self.fields['instructor_driving'].queryset = DrivingInstructor.objects.filter(school=school, status='active')
            self.fields['instructor_production'].queryset = ProductionMaster.objects.filter(school=school, status='active')
            self.fields['vehicle'].queryset = school.vehicles.filter(status='active')

