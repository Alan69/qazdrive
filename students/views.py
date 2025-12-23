from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import StudentGroup, Student, StudentDocument, LessonRecord, ExamResult
from .forms import StudentGroupForm, StudentForm, StudentDocumentForm, LessonRecordForm
from schools.views import get_user_schools, get_current_school, school_required
from schools.models import DrivingCategory
from userconf.models import UserRole, UserSchoolRole


# Groups views
@login_required
@school_required
def groups_list(request):
    """List all student groups"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    status_filter = request.GET.get('status', 'all')
    search = request.GET.get('search', '')
    
    groups = StudentGroup.objects.filter(school=school).annotate(
        student_count=Count('students')
    )
    
    if status_filter and status_filter != 'all':
        groups = groups.filter(status=status_filter)
    
    if search:
        groups = groups.filter(
            Q(name__icontains=search) |
            Q(students__last_name__icontains=search) |
            Q(students__first_name__icontains=search) |
            Q(students__iin__icontains=search)
        ).distinct()
    
    groups = groups.order_by('-created_at')
    
    paginator = Paginator(groups, 20)
    page = request.GET.get('page', 1)
    groups = paginator.get_page(page)
    
    # Count by status
    status_counts = {
        'all': StudentGroup.objects.filter(school=school).count(),
        'enrolling': StudentGroup.objects.filter(school=school, status='enrolling').count(),
        'training': StudentGroup.objects.filter(school=school, status='training').count(),
        'exams': StudentGroup.objects.filter(school=school, status='exams').count(),
        'completed': StudentGroup.objects.filter(school=school, status='completed').count(),
    }
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'groups': groups,
        'status_filter': status_filter,
        'search': search,
        'status_counts': status_counts,
    }
    return render(request, 'students/groups_list.html', context)


@login_required
@school_required
def group_detail(request, group_id):
    """Group detail with students list"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    group = get_object_or_404(StudentGroup, id=group_id, school=school)
    
    students = group.students.all().order_by('last_name', 'first_name')
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'group': group,
        'students': students,
    }
    return render(request, 'students/group_detail.html', context)


@login_required
@school_required
def group_add(request):
    """Add new group"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    if request.method == 'POST':
        form = StudentGroupForm(request.POST, school=school)
        if form.is_valid():
            group = form.save(commit=False)
            group.school = school
            group.save()
            messages.success(request, 'Учебная группа создана')
            return redirect('students:groups')
    else:
        form = StudentGroupForm(school=school)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'categories': DrivingCategory.objects.all(),
    }
    return render(request, 'students/group_form.html', context)


@login_required
@school_required
def group_edit(request, group_id):
    """Edit group"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    group = get_object_or_404(StudentGroup, id=group_id, school=school)
    
    if request.method == 'POST':
        form = StudentGroupForm(request.POST, instance=group, school=school)
        if form.is_valid():
            form.save()
            messages.success(request, 'Группа обновлена')
            return redirect('students:group_detail', group_id=group.id)
    else:
        form = StudentGroupForm(instance=group, school=school)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'group': group,
        'categories': DrivingCategory.objects.all(),
    }
    return render(request, 'students/group_form.html', context)


# Students views
@login_required
@school_required
def students_list(request):
    """List all students across all groups"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    search = request.GET.get('search', '')
    group_filter = request.GET.get('group', '')
    
    students = Student.objects.filter(group__school=school)
    
    if search:
        students = students.filter(
            Q(last_name__icontains=search) |
            Q(first_name__icontains=search) |
            Q(iin__icontains=search) |
            Q(group__name__icontains=search)
        )
    
    if group_filter:
        students = students.filter(group_id=group_filter)
    
    students = students.select_related('group').order_by('-created_at')
    
    paginator = Paginator(students, 20)
    page = request.GET.get('page', 1)
    students = paginator.get_page(page)
    
    groups = StudentGroup.objects.filter(school=school).order_by('name')
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'students': students,
        'search': search,
        'group_filter': group_filter,
        'groups': groups,
    }
    return render(request, 'students/students_list.html', context)


@login_required
@school_required
def student_detail(request, student_id):
    """Student detail page with documents and lessons"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    student = get_object_or_404(Student, id=student_id, group__school=school)
    
    documents = student.documents.all().order_by('-created_at')
    lessons = student.lessons.all().order_by('-date')[:10]
    exam_results = student.exam_results.all().order_by('-exam_date')
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'student': student,
        'documents': documents,
        'lessons': lessons,
        'exam_results': exam_results,
    }
    return render(request, 'students/student_detail.html', context)


@login_required
@school_required
def student_add(request, group_id=None):
    """Add new student"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    
    initial = {}
    if group_id:
        group = get_object_or_404(StudentGroup, id=group_id, school=school)
        initial['group'] = group
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, school=school)
        if form.is_valid():
            student = form.save()
            password, user_created = _ensure_student_user_account(student)
            if user_created and password:
                messages.success(
                    request,
                    f'Курсант добавлен. Аккаунт создан: телефон {student.phone}, пароль {password}'
                )
            else:
                messages.success(request, 'Курсант добавлен')
            return redirect('students:student_detail', student_id=student.id)
    else:
        form = StudentForm(school=school, initial=initial)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
    }
    return render(request, 'students/student_form.html', context)


def _ensure_student_user_account(student):
    """
    Ensures the student has a linked platform user.
    Returns (password, created_flag).
    """
    phone = (student.phone or '').strip()
    if not phone:
        return None, False

    User = get_user_model()
    password = None
    user_created = False

    # Try to find existing user by phone
    user = User.objects.filter(phone_number=phone).first()

    # Decide if we can safely set IIN on user (avoid unique conflicts)
    def can_set_iin(u):
        return bool(student.iin) and not User.objects.exclude(id=u.id if u and u.id else None).filter(iin=student.iin).exists()

    if not user:
        password = User.objects.make_random_password(length=8)
        user_kwargs = {
            'phone_number': phone,
            'password': password,
            'first_name': student.first_name or '',
            'last_name': student.last_name or '',
        }
        if student.middle_name:
            user_kwargs['middle_name'] = student.middle_name
        if student.email:
            user_kwargs['email'] = student.email
        if can_set_iin(User()):
            user_kwargs['iin'] = student.iin

        user = User.objects.create_user(**user_kwargs)
        user_created = True
    else:
        updated_fields = []
        if not user.first_name and student.first_name:
            user.first_name = student.first_name
            updated_fields.append('first_name')
        if not user.last_name and student.last_name:
            user.last_name = student.last_name
            updated_fields.append('last_name')
        if not user.middle_name and student.middle_name:
            user.middle_name = student.middle_name
            updated_fields.append('middle_name')
        if not user.email and student.email:
            user.email = student.email
            updated_fields.append('email')
        if not user.iin and can_set_iin(user):
            user.iin = student.iin
            updated_fields.append('iin')
        if updated_fields:
            user.save(update_fields=updated_fields)

    # Ensure student role
    student_role, _ = UserRole.objects.get_or_create(
        code='student',
        defaults={'name': 'Курсант', 'description': 'Курсант'}
    )
    UserSchoolRole.objects.get_or_create(
        user=user,
        school=student.school,
        role=student_role,
        defaults={'is_active': True}
    )

    # Link student to user if not linked yet
    if not student.user_id:
        student.user = user
        student.save(update_fields=['user'])

    return password, user_created


@login_required
@school_required
def student_edit(request, student_id):
    """Edit student"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    student = get_object_or_404(Student, id=student_id, group__school=school)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student, school=school)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные курсанта обновлены')
            return redirect('students:student_detail', student_id=student.id)
    else:
        form = StudentForm(instance=student, school=school)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'student': student,
    }
    return render(request, 'students/student_form.html', context)


# Document upload
@login_required
@school_required
def student_document_add(request, student_id):
    """Upload document for student"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    student = get_object_or_404(Student, id=student_id, group__school=school)
    
    if request.method == 'POST':
        form = StudentDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.student = student
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, 'Документ загружен')
            return redirect('students:student_detail', student_id=student.id)
    else:
        form = StudentDocumentForm()
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'student': student,
    }
    return render(request, 'students/document_form.html', context)


@login_required
@school_required
@require_POST
def student_document_delete(request, student_id, document_id):
    """Delete student document"""
    school = request.current_school
    student = get_object_or_404(Student, id=student_id, group__school=school)
    document = get_object_or_404(StudentDocument, id=document_id, student=student)
    document.delete()
    messages.success(request, 'Документ удален')
    return redirect('students:student_detail', student_id=student.id)


# Lessons
@login_required
@school_required
def lesson_add(request, student_id):
    """Add lesson record for student"""
    school = request.current_school
    user_schools = get_user_schools(request.user)
    student = get_object_or_404(Student, id=student_id, group__school=school)
    
    if request.method == 'POST':
        form = LessonRecordForm(request.POST, school=school)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.student = student
            lesson.save()
            messages.success(request, 'Запись о занятии добавлена')
            return redirect('students:student_detail', student_id=student.id)
    else:
        form = LessonRecordForm(school=school)
    
    context = {
        'school': school,
        'user_schools': user_schools,
        'form': form,
        'student': student,
    }
    return render(request, 'students/lesson_form.html', context)


# API for search
@login_required
def student_search_api(request):
    """API endpoint for student search (autocomplete)"""
    school = get_current_school(request)
    if not school:
        return JsonResponse({'results': []})
    
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    students = Student.objects.filter(
        group__school=school
    ).filter(
        Q(last_name__icontains=query) |
        Q(first_name__icontains=query) |
        Q(iin__icontains=query)
    )[:10]
    
    results = [
        {
            'id': s.id,
            'text': f"{s.full_name} ({s.iin})",
            'group': s.group.name
        }
        for s in students
    ]
    
    return JsonResponse({'results': results})
